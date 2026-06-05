# Урок 04. User-service: аккаунты, валидация и состояние пользователя

## Цель урока

Научиться глубоко тестировать пользовательские данные: создание аккаунта, email uniqueness, статус пользователя и влияние аккаунта на checkout.

## Компетенции после урока

После урока ты должен уметь:

- тестировать поля формы и API-валидацию;
- проверять uniqueness constraint;
- понимать влияние состояния пользователя на бизнес-flow;
- оформлять баги по валидации;
- объяснять, почему тестовые данные должны быть уникальными;
- отличать UI validation от backend validation.

## Что сделать

Через Customer Store:

1. Открой `http://localhost:8080/store.html`.
2. Перейди в `Account`.
3. Создай аккаунт с валидным email.
4. Проверь, что badge стал `active`.
5. Попробуй создать аккаунт с тем же email через QA Dashboard или API.

Через API:

```powershell
$email = "duplicate-user@example.com"
$body = @{ email = $email; full_name = "Duplicate User" } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8080/api/users -Method POST -Body $body -ContentType "application/json"
Invoke-WebRequest -Uri http://localhost:8080/api/users -Method POST -Body $body -ContentType "application/json"
```

Ожидаемый результат:

```text
first request: 201
second request: 409
```

Проверь невалидные значения:

- пустой email;
- `bad-email`;
- пустой `full_name`;
- `full_name` из пробелов;
- слишком длинное имя.

## Куда смотреть и почему

Customer Store показывает, как ошибку видит пользователь.

QA Dashboard показывает raw JSON response и помогает быстрее понять backend result.

Swagger UI показывает ограничения схемы.

Логи user-service помогают понять, дошел ли запрос до backend:

```powershell
docker compose logs --tail=100 user-service
```

## Что важно понять

Backend должен валидировать данные даже если UI уже проверяет поля. UI validation улучшает UX, но не является защитой системы.

Email uniqueness - это бизнес- и data integrity правило. Если оно сломается, в системе появятся неоднозначные пользователи.

Статус пользователя влияет на order flow. Inactive/blocked/deleted user не должен успешно оформлять заказ.

## Практическое задание

1. Создай активного пользователя.
2. Создай продукт.
3. Оформи заказ - он должен пройти.
4. Через API измени статус пользователя на `blocked`:

```powershell
$body = @{ status = "blocked" } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8080/api/users/USER_ID/status -Method PATCH -Body $body -ContentType "application/json"
```

5. Попробуй оформить новый заказ с этим user id.

Ожидаемый результат:

```text
order-service returns business error: user is not active
```

## Артефакт урока

Составь таблицу:

| Поле | Валидное значение | Невалидные значения | Ожидаемый код | Риск |
| --- | --- | --- | --- | --- |
| email | `qa@example.com` | пусто, `bad-email`, duplicate | `201`, `422`, `409` | Дубли, невозможность идентификации. |
| full_name | `QA User` | пусто, пробелы, слишком длинно | `201`, `422` | Плохое качество данных. |
| status | `active` | invalid enum | `200`, `422` | Неверный доступ к checkout. |

## Вопросы на собеседовании

### Вопрос: Почему backend validation обязательна, если есть UI validation?

Основной ответ:  
UI можно обойти через API, Postman, curl или другой клиент. Backend validation защищает систему и данные независимо от клиента.

Альтернативный ответ:  
Frontend validation - удобство пользователя, backend validation - целостность системы.

### Вопрос: Как тестировать уникальность email?

Основной ответ:  
Нужно дважды отправить запрос с одним email. Первый должен создать пользователя, второй должен вернуть `409 Conflict`. Также полезно проверить регистр email, например `Test@Example.com` и `test@example.com`, если система нормализует email.

Альтернативный ответ:  
Проверить duplicate create и убедиться, что в системе не появилось два пользователя с одним email.

### Вопрос: Что делать, если UI показывает общую ошибку, а API возвращает точную?

Основной ответ:  
Нужно завести frontend/UX defect или improvement: пользователь должен видеть понятную ошибку. При этом backend может работать корректно.

Альтернативный ответ:  
Локализую как проблему отображения ошибки на UI, если API contract корректен.

## Критерий завершения урока

Ты можешь протестировать аккаунт на UI и API, объяснить ошибки `409/422`, и показать, как статус пользователя влияет на заказ.
