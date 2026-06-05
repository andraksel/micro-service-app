# Урок 03. API, контракты и HTTP status codes

## Цель урока

Научиться проверять backend API вручную, понимать request/response contract и правильно интерпретировать HTTP status codes.

## Компетенции после урока

После урока ты должен уметь:

- читать Swagger UI каждого сервиса;
- составлять валидные и невалидные API-запросы;
- проверять status code, headers, body и schema;
- понимать разницу между `400`, `404`, `409`, `422`, `500`, `502`, `503`, `504`;
- объяснять, почему API contract важен для микросервисов;
- отличать дефект контракта от дефекта бизнес-логики.

## Перед практикой: что нужно понять

API - это договор между клиентом и backend. Клиентом может быть браузер, QA Dashboard, Postman, другой микросервис или автотест. Договор описывает, какой запрос можно отправить и какой ответ система обязана вернуть.

Если UI - это "что видит пользователь", то API - это "как пользовательское действие превращается в технический запрос".

### Из чего состоит API contract

API contract обычно включает:

| Часть контракта | Что это значит | Пример в проекте |
| --- | --- | --- |
| Method | Какое действие выполняется. | `GET`, `POST`, `PATCH`, `DELETE`. |
| Path | Куда отправляется запрос. | `/api/users`, `/api/products/{id}`. |
| Headers | Служебные данные запроса или ответа. | `Content-Type`, `X-Cache`, `X-Request-ID`. |
| Request body | Данные, которые клиент отправляет в backend. | email, имя пользователя, товары заказа. |
| Response body | Данные, которые backend возвращает клиенту. | `id`, `status`, `total_amount`. |
| Status code | Краткий технический итог операции. | `201`, `404`, `409`, `422`. |
| Schema | Форма данных: типы, обязательные поля, ограничения. | `email` должен быть email, `stock` не может быть отрицательным. |

Для QA это важно потому, что многие дефекты не видны в UI. Интерфейс может показать "ошибка", но только API даст точный статус, тело ответа и компонент, который не выполнил контракт.

### Что такое Swagger UI

Swagger UI - это веб-страница с документацией API. В FastAPI она обычно доступна по `/docs`.

В проекте каждый сервис имеет свой Swagger:

```text
user-service         http://localhost:8001/docs
product-service      http://localhost:8002/docs
order-service        http://localhost:8003/docs
payment-service      http://localhost:8004/docs
notification-service http://localhost:8005/docs
```

Swagger нужен не только разработчику. QA использует его, чтобы:

- увидеть список endpoint-ов;
- понять обязательные поля;
- проверить типы данных;
- понять, какие status codes ожидаются;
- собрать позитивные и негативные API-проверки;
- заметить расхождение между документацией и фактическим поведением.

### Gateway URL и прямой URL сервиса

В проекте один и тот же смысловой запрос можно отправить двумя путями.

Через gateway:

```text
http://localhost:8080/api/users
```

Напрямую в сервис:

```text
http://localhost:8001/users
```

Gateway-URL ближе к реальному пользовательскому сценарию, потому что браузер ходит через nginx. Прямой URL полезен для локализации.

Пример диагностики:

```text
Через /api/users ошибка 404, напрямую /users работает
  -> вероятно, проблема в nginx route.

Через /api/users ошибка 422, напрямую /users тоже 422
  -> вероятно, проблема в payload или backend validation.
```

### Что значат основные status codes

Status code - это не просто "красный или зеленый ответ". Это язык, на котором backend объясняет итог операции.

| Код | Смысл | Как читать в этом проекте |
| --- | --- | --- |
| `200` | Запрос успешно выполнен. | Данные получены или обновлены. |
| `201` | Ресурс создан. | Создан пользователь, товар или заказ. |
| `204` | Успешно, но тела ответа нет. | Удаление или soft delete выполнены. |
| `400` | Бизнес-запрос некорректен. | Пользователь заблокирован, товара не хватает, dependency вернула 4xx. |
| `404` | Ресурс не найден. | Нет пользователя, товара, заказа или уведомления. |
| `409` | Конфликт состояния. | Email уже существует. |
| `422` | Payload не прошел schema validation. | Неверный email, отрицательная цена, пустое обязательное поле. |
| `500` | Внутренняя ошибка сервиса. | Непойманное исключение или дефект backend. |
| `502` | Ошибка upstream/dependency. | Сервис получил плохой ответ от другого сервиса. |
| `503` | Сервис или зависимость не готовы. | `/ready` падает из-за БД, Redis или RabbitMQ. |
| `504` | Timeout dependency. | `payment-service` или другой dependency не ответил вовремя. |

Сильный QA не пишет "сервер вернул ошибку". Он пишет конкретно: "ожидался `409 Conflict` при повторном email, фактически получен `500`, это скрывает бизнес-конфликт и ломает контракт".

### Schema validation vs business validation

Schema validation проверяет форму данных до выполнения бизнес-логики.

Примеры:

- email должен быть похож на email;
- price должен быть числом больше нуля;
- stock не может быть отрицательным;
- обязательное поле не может отсутствовать.

Business validation проверяет смысл операции.

Примеры:

- email уже занят;
- пользователь заблокирован;
- товар архивирован;
- товара недостаточно на складе;
- заказ нельзя отменить повторно.

Это разные типы дефектов. Если сломан schema validation, сервис принимает мусорные данные. Если сломана business validation, сервис принимает технически корректный запрос, но нарушает правила продукта.

### Что должен проговаривать QA

Перед каждым API-запросом проговаривай:

```text
Какой endpoint я проверяю?
Какой contract у этого endpoint?
Какие поля обязательны?
Какой status code ожидается?
Что будет считаться дефектом контракта?
Что будет считаться дефектом бизнес-логики?
Через gateway или напрямую в сервис я проверяю?
```

## Что сделать

Открой Swagger UI:

```text
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
http://localhost:8004/docs
http://localhost:8005/docs
```

Выполни через PowerShell или Postman:

```powershell
$body = @{
  email = "manual-api-user@example.com"
  full_name = "Manual API User"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8080/api/users -Method POST -Body $body -ContentType "application/json"
```

Проверь невалидный email:

```powershell
$body = @{
  email = "bad-email"
  full_name = "Bad Email"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8080/api/users -Method POST -Body $body -ContentType "application/json"
```

Проверь создание продукта:

```powershell
$body = @{
  name = "API Product"
  description = "Created manually"
  price = "15.00"
  currency = "USD"
  stock = 5
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8080/api/products -Method POST -Body $body -ContentType "application/json"
```

## Куда смотреть и почему

Swagger UI показывает публичный контракт сервиса: какие endpoints есть, какие поля обязательны, какие типы данных ожидаются.

Response body показывает фактическое поведение. Если API должен вернуть `201`, но вернул `200`, это может быть contract issue. Если поле пропало или поменяло тип, это contract regression.

Headers важны для технических проверок. В проекте полезны:

```text
X-Request-ID
X-Cache
Content-Type
```

## Status codes

| Код | Как понимать в проекте |
| --- | --- |
| `200` | Успешное чтение или обновление. |
| `201` | Ресурс создан: user, product, order. |
| `204` | Успешная операция без body. |
| `400` | Бизнес-ошибка: inactive user, insufficient stock. |
| `404` | Ресурс не найден. |
| `409` | Конфликт состояния, например duplicate email. |
| `422` | Ошибка валидации схемы запроса. |
| `500` | Необработанная внутренняя ошибка. |
| `502` | Ошибка upstream dependency или contract violation. |
| `503` | Сервис не готов или dependency недоступна. |
| `504` | Timeout dependency. |

## Что проверить вручную

- `POST /api/users` с валидным email.
- `POST /api/users` с плохим email.
- `POST /api/users` с пустым `full_name`.
- `POST /api/users` с дубликатом email.
- `GET /api/users/UNKNOWN_ID`.
- `POST /api/products` с валидным товаром.
- `POST /api/products` с отрицательной ценой.
- `POST /api/products` с `stock = -1`.
- `POST /api/orders` без items.
- `POST /api/orders` с неизвестным user id.

## Что записать

```text
Endpoint:
Method:
Request body:
Expected status:
Actual status:
Expected schema:
Actual schema:
Headers:
Conclusion:
```

## Вопросы на собеседовании

### Вопрос: Что такое API contract?

Основной ответ:  
API contract - это соглашение между клиентом и сервисом: endpoint, method, request schema, response schema, status codes, headers и бизнес-значения. Если контракт неожиданно меняется, клиенты могут сломаться.

Альтернативный ответ:  
Это публичные правила взаимодействия с сервисом.

### Вопрос: Почему `422` - это не то же самое, что `400`?

Основной ответ:  
`422` обычно означает, что запрос синтаксически принят, но не прошел валидацию схемы: неверный тип поля, плохой email, отсутствует обязательное поле. `400` чаще означает бизнес-ошибку или некорректный запрос на уровне логики.

Альтернативный ответ:  
`422` - schema validation, `400` - business/request logic.

### Вопрос: Как проверить, что API не сломал контракт?

Основной ответ:  
Нужно сравнить фактический response со схемой: обязательные поля, типы, enum values, status code, headers. Также нужно проверить негативные сценарии и backward compatibility.

Альтернативный ответ:  
Проверить, что старый клиентский сценарий продолжает работать без изменения запроса.

## Критерий завершения урока

Ты можешь для любого endpoint проекта сказать: method, path, request body, expected response, возможные ошибки и как проверить контракт.
