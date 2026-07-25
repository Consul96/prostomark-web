# ProstoMark Sign Agent (Честный знак)

Выносной агент подписи для модуля «Честный знак». Работает на Windows-машине/сервере
с **CryptoPro CSP**, установленным сертификатом сотрудника Cargo-Trans и `cryptcp.exe`.

## Зачем

Закрытый ключ сертификата **не размещается на VPS**. Backend лишь ставит задачи
подписи (`SignJob`); агент сам опрашивает backend по HTTPS (**исходящее** подключение —
не требует входящих портов в корпоративную сеть), подписывает точные байты и
возвращает CMS-подпись Base64.

## Протокол (backend endpoints)

Базовый префикс: `/api/v1/marking/sign-agent`. Аутентификация — заголовок
`X-Agent-Api-Key: <ключ>` (создаётся при регистрации агента в UI; хранится на сервере
только как HMAC-хеш, показывается один раз).

| Операция | Метод | Путь |
|---|---|---|
| Heartbeat | POST | `/sign-agent/heartbeat` |
| Получить следующую задачу | GET | `/sign-agent/next-job` |
| Вернуть результат | POST | `/sign-agent/result` |
| Вернуть ошибку | POST | `/sign-agent/error` |

Задача (`next-job`) содержит: `job_id`, `sign_type` (`attached`/`detached`),
`payload_base64`, `payload_sha256`, `certificate_thumbprint`, `client_inn`,
`operation`, `expires_at`.

Агент обязан:
1. Проверить SHA-256 полученного payload (`payload_sha256`).
2. Подписать **точные исходные байты** (attached или detached CMS).
3. Вернуть CMS Base64 в `/sign-agent/result` вместе с `payload_sha256`.
4. Не хранить исходный payload дольше выполнения операции.
5. Никогда не возвращать закрытый ключ.
6. Не логировать полный КМ или токен.

## Запуск (PowerShell)

```powershell
$env:AGENT_API_KEY = "<ключ агента>"
$env:BACKEND_URL   = "https://app.prostomark.ru/api/v1/marking"
$env:CERT_THUMBPRINT = "<отпечаток сертификата>"   # опционально; берётся из задачи
$env:CRYPTCP_PATH  = "C:\Program Files\Crypto Pro\CSP\cryptcp.exe"
.\agent.ps1
```

`agent.ps1` в цикле опрашивает `next-job` (интервал `SIGN_AGENT_POLL_SECONDS`),
формирует detached/attached CMS через `cryptcp.exe -sign` и отправляет результат.

## Mock signer (тесты/sandbox)

Для автоматических тестов и sandbox без CryptoPro используется `MockSigner`
(`backend/app/services/marking/auth/sign_service.py`) — детерминированная
не-криптографическая подпись. Продакшн-подпись выполняется только реальным агентом.

## Требования на стороне Windows

- CryptoPro CSP (лицензия);
- сертификат сотрудника с закрытым ключом в хранилище `Мой`;
- `cryptcp.exe` (входит в поставку CryptoPro CSP);
- исходящий HTTPS-доступ к `app.prostomark.ru`.
