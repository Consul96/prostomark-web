"""Sandbox connection test: реальная аутентификация клиента в True API и СУЗ.

Выполняет по каждой системе:
  1. свежий challenge /auth/key;
  2. подпись `data` через Sign Agent (attached CMS) — отдельная SignJob;
  3. simpleSignIn с ИНН клиента (True API) / omsConnection (СУЗ);
  4. раздельные кеши токенов (true-api:* и suz:*).

ЧЕСТНЫЙ статус: `ok` ставится ТОЛЬКО если внешняя система реально вернула токен.
Заполненность полей конфигурации сама по себе НЕ даёт `ok`. Сетевые/авторизационные
ошибки → `unavailable`/`cert_unavailable` с безопасным текстом (без токенов/подписей).

Продакшн-предохранитель: перед выполнением вызывается guard.assert_environment_ok().
Тест не выполняет юридически значимых операций — только аутентификацию.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.models.enums import ConnectionStatus, MchdStatus, SignJobType
from app.models.marking import CrptClient, SignerAgent
from app.services.marking import guard
from app.services.marking.auth import token_cache as tc
from app.services.marking.auth.mchd_service import evaluate_mchd_status
from app.services.marking.auth.sign_service import MockSigner, create_sign_job, wait_for_signature
from app.services.marking.auth.suz_token_manager import SuzTokenManager
from app.services.marking.auth.true_api_token_manager import TrueApiTokenManager
from app.services.marking.clients.client_service import record_connection_check
from app.services.marking.errors import ExternalApiError, ExternalAuthError, MarkingError

logger = logging.getLogger('marking.connection')


def _signer_id(client: CrptClient) -> str:
    return str(client.signer_agent_id or client.signer_certificate_thumbprint or 'nosigner')


def _make_sign_callback(db: Session, client: CrptClient, *, operation: str):
    """Возвращает callback(data:str)->CMS Base64 через SignJob + Sign Agent.

    В dry-run/sandbox без активного агента задача подписывается mock-подписантом
    (детерминированная НЕ криптоподпись) — этого достаточно, чтобы прогнать поток
    challenge→sign→signIn; реальный True API/СУЗ такую подпись не примет, и статус
    честно окажется НЕ `ok`.
    """

    def _sign(data: str) -> str:
        payload = data.encode('utf-8')
        job = create_sign_job(
            db,
            company_id=client.company_id,
            payload=payload,
            detached=False,  # attached CMS для авторизации
            client_inn=client.inn,
            operation=operation,
            certificate_thumbprint=client.signer_certificate_thumbprint,
            crpt_client_id=client.id,
            signer_agent_id=client.signer_agent_id,
        )
        db.commit()

        agent = db.get(SignerAgent, client.signer_agent_id) if client.signer_agent_id else None
        use_mock = guard.is_dry_run() or agent is None or not agent.is_active
        if use_mock:
            signature = MockSigner().sign(payload, detached=False, thumbprint=job.certificate_thumbprint)
            job.signature_base64 = signature
            from app.models.enums import SignJobStatus

            job.status = SignJobStatus.COMPLETED.value
            db.commit()
            return signature
        # Реальный агент: ждём подпись (исходящий агент заберёт SignJob).
        return wait_for_signature(db, job)

    return _sign


def run_connection_test(db: Session, client: CrptClient) -> dict:
    guard.assert_environment_ok()  # продакшн без разрешения — контролируемая ошибка

    environment = client.environment or settings.crpt_env
    signer_id = _signer_id(client)
    result: dict = {'environment': environment, 'true_api': {}, 'suz': {}, 'mchd': {}}

    # --- МЧД ---
    mchd = evaluate_mchd_status(client)
    client.mchd_status = mchd
    result['mchd'] = {'status': mchd}
    record_connection_check(db, client, kind='mchd', status=mchd)

    prereq_ok = mchd == MchdStatus.ACTIVE.value and bool(client.signer_agent_id or client.signer_certificate_thumbprint)

    # --- True API ---
    ta_status, ta_detail, ta_key = _test_true_api(db, client, environment, signer_id, prereq_ok)
    client.true_api_status = ta_status
    result['true_api'] = {'status': ta_status, 'detail': ta_detail, 'cache_key': ta_key}
    record_connection_check(db, client, kind='true_api', status=ta_status, detail=ta_detail)

    # --- СУЗ ---
    suz_status, suz_detail, suz_key = _test_suz(db, client, environment, signer_id, prereq_ok)
    client.suz_status = suz_status
    result['suz'] = {'status': suz_status, 'detail': suz_detail, 'cache_key': suz_key}
    record_connection_check(db, client, kind='suz', status=suz_status, detail=suz_detail)

    from datetime import UTC, datetime

    client.last_connection_check_at = datetime.now(UTC)
    db.commit()
    # cache_key возвращаем для наблюдаемости — это НЕ секрет (в нём нет токена).
    result['token_caches_separated'] = ta_key != suz_key
    return result


def _test_true_api(db, client, environment, signer_id, prereq_ok):
    key = tc.true_api_cache_key(environment, signer_id, client.inn)
    if not prereq_ok:
        return ConnectionStatus.NEEDS_SETUP.value, 'Нет активной МЧД или подписанта', key
    try:
        mgr = TrueApiTokenManager(base_url=settings.crpt_true_api_base_url)
        sign = _make_sign_callback(db, client, operation='true_api.auth')
        token = mgr.get_token(
            environment=environment, signer_id=signer_id, client_inn=client.inn, sign=sign, force_refresh=True
        )
        # ok ТОЛЬКО при реально полученном токене
        return (ConnectionStatus.OK.value if token else ConnectionStatus.UNAVAILABLE.value), 'Токен получен', key
    except ExternalAuthError:
        return ConnectionStatus.CERT_UNAVAILABLE.value, 'Подпись/сертификат не приняты True API', key
    except (ExternalApiError, MarkingError) as exc:
        logger.warning('true_api connection test failed: %s', exc.code)
        return ConnectionStatus.UNAVAILABLE.value, 'True API недоступен', key
    except Exception:  # noqa: BLE001
        logger.exception('true_api connection test unexpected error')
        return ConnectionStatus.UNAVAILABLE.value, 'True API недоступен', key


def _test_suz(db, client, environment, signer_id, prereq_ok):
    oms_connection = client.oms_connection or ''
    key = tc.suz_cache_key(environment, signer_id, client.inn, oms_connection)
    if not prereq_ok or not client.oms_id or not oms_connection:
        return ConnectionStatus.NEEDS_SETUP.value, 'Нет omsId/omsConnection/подписанта/МЧД', key
    try:
        mgr = SuzTokenManager(base_url=settings.crpt_suz_base_url)
        sign = _make_sign_callback(db, client, operation='suz.auth')
        token = mgr.get_token(
            environment=environment,
            signer_id=signer_id,
            client_inn=client.inn,
            oms_connection=oms_connection,
            sign=sign,
            force_refresh=True,
        )
        return (ConnectionStatus.OK.value if token else ConnectionStatus.UNAVAILABLE.value), 'clientToken получен', key
    except ExternalAuthError:
        return ConnectionStatus.CERT_UNAVAILABLE.value, 'Подпись/сертификат не приняты СУЗ', key
    except (ExternalApiError, MarkingError) as exc:
        logger.warning('suz connection test failed: %s', exc.code)
        return ConnectionStatus.UNAVAILABLE.value, 'СУЗ недоступен', key
    except Exception:  # noqa: BLE001
        logger.exception('suz connection test unexpected error')
        return ConnectionStatus.UNAVAILABLE.value, 'СУЗ недоступен', key


# Экспортируемый список типов подписи для документации/тестов
SIGN_TYPES = (SignJobType.ATTACHED.value, SignJobType.DETACHED.value)
