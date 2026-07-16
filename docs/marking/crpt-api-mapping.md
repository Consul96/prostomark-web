# Карта интеграций ГИС МТ (модуль «Честный знак»)

Составлено по извлечённому тексту предоставленных документов:

- **True API** — `True API (2).pdf` (методы v3/v4).
- **API СУЗ 3.0** — `API СУЗ 3.0 (1).pdf`.

Правило: endpoint/поле/статус/лимит, не подтверждённые документацией, **не**
реализуются как боевая интеграция. Такие операции помечены `NOT_IMPLEMENTED`
с явной причиной (см. столбец «Статус реализации»).

Легенда статуса реализации:
- ✅ **CONFIRMED** — endpoint и назначение подтверждены документом; клиент/менеджер
  токена реализован.
- 🟡 **PARTIAL** — endpoint подтверждён, но тело запроса/схема требуют сверки перед боем.
- ⛔ **NOT_IMPLEMENTED** — не подтверждено предоставленной документацией.

---

## 1. Базовые URL и окружения

| Система | Окружение | Base URL | Источник |
|---|---|---|---|
| True API | sandbox | `https://markirovka.sandbox.crptech.ru/api/v3/true-api` (и `/api/v4/true-api`) | trueapi.txt:462–464 |
| True API | production | `https://markirovka.crpt.ru/api/v3/true-api` (и `/api/v4/true-api`) | trueapi.txt:468–470 |
| СУЗ | — | `<url стенда>/api/v3/...` (omsId в query) | suz.txt:1290, 1644 |

Настройки: `CRPT_TRUE_API_BASE_URL`, `CRPT_TRUE_API_V4_BASE_URL`, `CRPT_SUZ_BASE_URL`,
`CRPT_ENV`, `CRPT_ALLOW_PRODUCTION`, `CRPT_DRY_RUN`.

---

## 2. Авторизация True API (единый токен UUID/JWT)

| Операция | Система | Endpoint | Метод | Headers | Request | Response | Статус | Источник |
|---|---|---|---|---|---|---|---|---|
| Получить challenge | True API | `/auth/key` | GET | — | — | `{uuid, data}` | ✅ CONFIRMED | trueapi.txt:714–738 |
| Аутентификация (simpleSignIn) | True API | `/auth/simpleSignIn` | POST | `Content-Type: application/json` | `{uuid, data:<CMS Base64 подписи>, inn}` | `{token \| uuidToken, ...}` | ✅ CONFIRMED | trueapi.txt:747–847 |
| Использование токена | True API | все методы | — | `Authorization: Bearer <token>` | — | — | ✅ CONFIRMED | trueapi.txt:1252 и др. |

Реализация: `services/marking/auth/true_api_token_manager.py`.
- challenge UUID **не переиспользуется** (новый на каждую аутентификацию);
- ключ кеша: `true-api:{environment}:{signer_id}:{client_inn}`;
- упреждающее обновление (skew 60 с), Redis-lock, инвалидация при 401 + один повтор.

Ограничения: срок токена UUID не превышает срок действия ключа/сертификата
(trueapi.txt:944–957). Точное время истечения из ответа при наличии — иначе
консервативный TTL 10 ч.

Поддерживаемые товарные группы: любые, где у клиента подключена ТГ в ЛК ГИС МТ
(trueapi.txt:683).

---

## 3. Авторизация СУЗ (clientToken)

| Операция | Система | Endpoint | Метод | Headers | Request | Response | Статус | Источник |
|---|---|---|---|---|---|---|---|---|
| Получить challenge | СУЗ | `/api/v3/auth/key` | GET | — | — | `{uuid, data}` | 🟡 PARTIAL | по аналогии True API; отдельный раздел СУЗ в PDF требует сверки |
| Авторизация → clientToken | СУЗ | `/api/v3/auth/simpleSignIn` (⚠️ путь требует подтверждения) | POST | `Content-Type: application/json` | `{uuid, data:<CMS>, inn, connectionId}` | `{clientToken}` | 🟡 PARTIAL | suz.txt:713–715 (clientToken в заголовке) |
| Использование | СУЗ | методы СУЗ | — | `clientToken: <clientToken>` | — | — | ✅ CONFIRMED | suz.txt:557–563, 1315–1318 |

Реализация: `services/marking/auth/suz_token_manager.py`.
- ключ кеша: `suz:{environment}:{signer_id}:{client_inn}:{oms_connection}`;
- **один активный СУЗ-токен на omsConnection** (Redis-lock сериализует обновление);
- новый токен может инвалидировать предыдущий; при 401 — одна повторная авторизация;
- True API token и СУЗ clientToken **не смешиваются**.

> ⚠️ Точный путь авторизации СУЗ (шаг «→ clientToken») в предоставленной версии PDF
> отдельным разделом не выделен; параметризован через `SuzTokenManager.auth_path`.
> Перед боем — сверить с разделом авторизации API СУЗ 3.0.

Также (suz.txt:714–715): для ТГ «Лекарственные препараты» токен может передаваться
в `Authorization`. Для лёгкой промышленности/обуви используется `clientToken`.

---

## 4. СУЗ — заказ и получение КМ

omsId передаётся в query (`?omsId={omsId}`); значение — из настроек СУЗ клиента
(suz.txt:707–708, 1334).

| # | Операция | Endpoint | Метод | Request (ключевые поля) | Response | Статус | Источник |
|---|---|---|---|---|---|---|---|
| 1 | Ping OMS | `/api/v3/ping?omsId=` (см. схему потока) | GET | omsId | `200 omsId` | 🟡 PARTIAL | suz.txt:762–764 |
| 2 | Создать заказ на эмиссию КМ | `/api/v3/order?omsId={omsId}` | POST | `clientToken` header, тело заказа | `{omsId, orderId, expectedCompletionTime}` | 🟡 PARTIAL | suz.txt:768–769, 1290, 1644 |
| 3 | Статус буфера КМ | `/api/v3/buffer/status` (уточнить) | GET | omsId, orderId, gtin | статус | ⛔ NOT_IMPLEMENTED | suz.txt:772–777 |
| 4 | Получить КМ из заказа | `/api/v3/codes?omsId=&orderId=&gtin=&quantity=&lastBlockId=` | GET | omsId, orderId, gtin, quantity, lastBlockId | `{omsId, codes, blockId}` | 🟡 PARTIAL | suz.txt:777–779, 1084 |
| 5 | Отчёт о нанесении (utilisation) | `/api/v3/utilisation?omsId=` | POST | utilisationReport (подписанный) | `{omsId, reportId}` | 🟡 PARTIAL | suz.txt:782–784 |
| 6 | Отчёт агрегации | `/api/v3/aggregation?omsId=` | POST | aggregationReport | `{omsId, reportId}` | ⛔ NOT_IMPLEMENTED | suz.txt:788–789 |
| 7 | Отчёт о выбытии | `/api/v3/dropout?omsId=` | POST | dropoutReport | `{omsId, reportId}` | ⛔ NOT_IMPLEMENTED | suz.txt:791–793 |

Реализация-интерфейс: `services/marking/suz/client.py` (методы поднимают
`NotImplementedIntegrationError` до сверки тел и снятия предохранителя окружения).

**Частичное получение КМ** (метод 4): `lastBlockId` указывает последний
полученный блок — повторный вызов отдаёт оставшееся (suz.txt:1084). Логика
`ready_quantity`/`received_quantity`/`last_block_id` заложена в `KmOrderItem`.

**Rate limit СУЗ:** не чаще 100 запросов/с на пару «IP + omsId» (suz.txt:1251–1278).

**⚠️ Лимиты количества КМ в заказе / отчёте** документом в извлечённом виде не
зафиксированы численно → в `ProductGroupPolicyRegistry` заданы `None`
(`max_codes_per_order`, `max_km_per_manual_report`) — **уточнить в API СУЗ 3.0**.

**Важно про группы с авто-отчётом (лёгкая промышленность, обувь):** ручной
`/utilisation` (метод 5) **не отправляется** — контроль нанесения ведётся через
True API `/cises/info` (раздел 6).

---

## 5. Национальный каталог (карточки, GTIN, фиды, модерация)

| Операция | Endpoint | Метод | Статус | Причина |
|---|---|---|---|---|
| Резерв/получение GTIN | — | — | ⛔ NOT_IMPLEMENTED | API НК не входит в предоставленные PDF (True API + СУЗ). |
| Отправка фида карточек | — | — | ⛔ NOT_IMPLEMENTED | Требуется отдельная спецификация НК. |
| Статус фида / модерация | — | — | ⛔ NOT_IMPLEMENTED | — |
| Подписание и публикация карточки | — | — | ⛔ NOT_IMPLEMENTED | — |

Интерфейс: `services/marking/national_catalog/client.py`. Base URL параметр
`CRPT_NK_BASE_URL` задан заглушкой. **Не считать GTIN готовым к заказу КМ только
по факту получения номера — требуется статус карточки НК = опубликована.**

---

## 6. Контроль нанесения через True API

| Операция | Endpoint | Метод | Headers | Response (ключевое) | Статус | Источник |
|---|---|---|---|---|---|---|
| Инфо о КИ по списку | `/cises/info` | POST | `Authorization: Bearer` | по каждому КИ: `status`, `statusInn`, владелец, ТГ, дата нанесения | 🟡 PARTIAL | trueapi.txt:1076, 1100, 1369–1374 |
| История КИ | `/cises/history?cis=` | GET | `Authorization: Bearer` | история статусов | 🟡 PARTIAL | trueapi.txt:635–636 |

Реализация-интерфейс: `services/marking/circulation/status_service.py`
(`CisesInfoClient`). Полная пакетная сверка (владелец / статус / товарная группа /
дата нанесения с приведением UTC → timezone клиента) — Phase 4.

Статусы строк контроля нанесения (внутренние): `OK`, `DATE_MISMATCH`,
`NOT_APPLIED`, `NOT_FOUND`, `WRONG_OWNER`, `WRONG_PRODUCT_GROUP`, `INVALID_KM`,
`API_ERROR`.

---

## 7. МЧД

| Операция | Endpoint | Метод | Статус | Источник |
|---|---|---|---|---|
| Статус/список МЧД | `/mchd/...` (True API) | GET | 🟡 PARTIAL | trueapi.txt:2430, 2511 (статусы МЧД присутствуют) |

Пока статус МЧД оценивается детерминированно по сохранённым срокам
(`auth/mchd_service.py`); сетевая проверка списка МЧД через True API — при интеграции
раздела МЧД. Операции блокируются при `mchd_status != active`.

---

## 8. Подпись (Sign Agent)

Не является методом ГИС МТ. CMS-подпись (attached/detached) формируется выносным
агентом (CryptoPro CSP, `cryptcp.exe`) — см. `sign-agent/README.md`. Backend ставит
`SignJob`, агент забирает по HTTPS (исходящее подключение), подписывает **точные
байты** payload и возвращает CMS Base64. Проверка `payload_sha256` перед сохранением.

---

## Сводка «что реально вызывается сейчас»

- ✅ Реализованы менеджеры токенов True API/СУЗ (структура запросов по документации),
  кеш/локи, предохранители окружения, хранилище КМ, реестр товарных групп, протокол
  Sign Agent, CRUD клиентов/заявок, dashboard, история.
- 🟡 Требуют сверки тел/схем перед боем: авторизация СУЗ (путь), создание заказа,
  получение КМ, ручной utilisation, `/cises/info`.
- ⛔ NOT_IMPLEMENTED: Национальный каталог целиком, агрегация, выбытие, буфер-статус.

---

## Проверенное поведение в рантайме (hardening, sandbox)

Проверено на локальном стеке (PostgreSQL 16 + Redis), Docker недоступен на хосте —
использован эквивалентный локальный Postgres/Redis. Все проверки автоматизированы
в `backend/tests/` (40 тестов зелёные).

**Миграции.** Чистый `alembic upgrade head` (initial → marking) создаёт 18 таблиц
`marking_*`; `downgrade -1` дропает только marking, база остаётся; полный цикл
`downgrade base → upgrade head` проходит без ошибок.

**Sandbox connection test** (`POST /clients/{id}/sandbox-connection-test`,
`services/marking/clients/connection_service.py`):
- по каждой системе выполняется **свежий** `/auth/key` challenge → attached-CMS
  подпись через Sign Agent (`SignJob`) → `simpleSignIn` (True API — с ИНН клиента;
  СУЗ — с omsConnection);
- **раздельные кеши токенов** подтверждены рантаймом: ключи
  `true-api:{env}:{signer}:{inn}` и `suz:{env}:{signer}:{inn}:{omsConnection}`
  различаются (`token_caches_separated=true`);
- **честный статус**: `ok` ставится ТОЛЬКО при реально полученном токене. При сетевой
  ошибке → `unavailable`; при отсутствии МЧД/подписанта/omsConnection → `needs_setup`
  (сеть при этом не дёргается). Заполненность полей сама по себе `ok` не даёт;
- продакшн заблокирован: при `CRPT_ENV=production` без `CRPT_ALLOW_PRODUCTION=true`
  тест поднимает `ProductionBlockedError` (409) до любых внешних вызовов;
- юридически значимые операции в connection-тесте не выполняются.

**Sign Agent (протокол, mock signer).** Проверено сквозным прогоном
heartbeat → next-job (claim) → attached/detached подпись → result:
- сырой API-ключ не хранится (только `HMAC-SHA256`); неверный ключ → 401;
- `next-job` не выдаёт просроченные задачи и берёт `SELECT ... FOR UPDATE SKIP LOCKED`;
- несовпадение `payload_sha256` → 409 `MARKING_PAYLOAD_HASH_MISMATCH`, задача не
  переходит в COMPLETED;
- просроченная задача при отправке результата → 409, статус `EXPIRED`;
- дубль того же результата — идемпотентно `{ok, idempotent:true}`; переопределение
  завершённой задачи другим payload → 409;
- деактивированный агент → 401 (недоступен).

**Изоляция арендаторов** доказана тестами: клиент/заявка/агент/SignJob/история одной
компании недоступны другой (404/пусто), заявку нельзя создать на чужого клиента
(подмена UUID → 404). **Роли**: view — все; создание клиента/заявки — manager+;
deactivate/создание агента — только company_admin (+superadmin).

**Найденный и исправленный баг.** Эндпоинт создания Sign Agent
(`POST /sign-agent/agents`) падал с `ValidationError` (валидация ORM против модели с
обязательным `api_key` до его инъекции) — эндпоинт не работал никогда. Исправлено;
покрыто тестом `test_agent_registration_and_key_hashed`.

**Безопасность логирования** подтверждена: HTTP-клиент маскирует заголовки
`Authorization`/`clientToken`/`X-Api-Key`; токены/подписи/полные КМ/ключи/полные
подписанные payload'ы в логи не пишутся.
