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
