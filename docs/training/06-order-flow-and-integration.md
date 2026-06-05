# Урок 06. Order flow и интеграционное тестирование

## Цель урока

Научиться тестировать главный бизнес-flow: пользователь выбирает товары, оформляет заказ, payment-service авторизует платеж, order-service публикует события, notification-service создает уведомления.

## Компетенции после урока

После урока ты должен уметь:

- тестировать end-to-end flow покупки;
- понимать orchestration в order-service;
- локализовать ошибку в цепочке сервисов;
- проверять side effects после API-запроса;
- отличать unit/API проверку от integration проверки;
- объяснять, почему интеграционные дефекты сложнее.

## Перед практикой: что нужно понять

`order-service` - центральный сервис бизнес-flow. Он не просто сохраняет заказ. Он связывает пользователя, товары, оплату и уведомления в один процесс.

В микросервисной системе самый важный навык QA - видеть не один endpoint, а цепочку взаимодействий.

### Что такое order flow

Order flow - это путь заказа через систему.

В этом проекте checkout выглядит так:

```text
Customer Store
  -> POST /api/orders
  -> nginx gateway
  -> order-service
  -> user-service: проверить пользователя
  -> product-service: проверить товары, статус и stock
  -> payment-service: авторизовать платеж
  -> order-db: сохранить заказ
  -> RabbitMQ: опубликовать событие
  -> notification-service: создать уведомление
```

Когда ты тестируешь заказ, ты тестируешь не только `order-service`. Ты проверяешь, что несколько сервисов умеют договориться между собой.

### Что такое orchestration

Orchestration - это когда один компонент управляет последовательностью действий.

В этом проекте оркестратор - `order-service`. Он решает:

- можно ли создать заказ для этого пользователя;
- активны ли товары;
- хватает ли stock;
- какой total amount посчитать;
- что делать с ответом payment-service;
- какой статус присвоить заказу;
- публиковать ли событие в RabbitMQ.

Если `order-service` пропустил заблокированного пользователя, это дефект orchestration. Если `payment-service` вернул `declined`, а заказ стал `paid`, это тоже дефект orchestration.

### Integration test vs API test

Обычная API-проверка может быть узкой:

```text
POST /api/orders вернул 201.
```

Интеграционная проверка шире:

```text
POST /api/orders вернул 201.
Статус заказа paid.
Сумма заказа корректная.
payment-service получил запрос.
Событие ушло в RabbitMQ.
notification-service создал уведомление.
В логах нет ошибок dependency.
```

Именно поэтому один успешный status code не доказывает, что flow работает полностью.

### Sync и async части flow

Синхронная часть - это то, что происходит до ответа клиенту:

- проверка пользователя;
- проверка товаров;
- вызов оплаты;
- сохранение заказа;
- возврат ответа UI.

Асинхронная часть - это то, что может завершиться позже:

- сообщение в RabbitMQ;
- обработка события notification-service;
- появление уведомления.

Если заказ уже `paid`, а уведомления еще нет, это не всегда баг. Нужно понять, уложилось ли поведение в ожидаемую eventual consistency.

### Где обычно прячутся интеграционные дефекты

Типовые проблемы:

- сервисы по-разному понимают contract;
- один сервис вернул поле в неожиданном формате;
- timeout dependency превращается в неправильный status code;
- заказ сохранился, но событие не отправилось;
- событие отправилось, но consumer его не обработал;
- payment decline превращается в `paid`;
- заказ создан с неправильной суммой;
- ошибка dependency показывается пользователю как непонятный `Internal Server Error`.

### Что должен проговаривать QA

Перед проверкой заказа проговаривай:

```text
Какие сервисы участвуют в flow?
Какая часть синхронная, а какая асинхронная?
Какие side effects должны появиться после заказа?
Какой статус заказа ожидается?
Где я проверю payment result?
Где я проверю уведомление?
Какой компонент является suspected component, если flow сломался?
```

## Что сделать

1. Открой QA Dashboard:

```text
http://localhost:8080
```

2. Установи payment mode:

```text
success
```

3. Создай пользователя.

4. Создай продукт со stock `10`.

5. Создай заказ quantity `1`.

6. Проверь ответ:

```json
"status": "paid"
```

7. Нажми `Refresh` в Notifications.

8. Проверь события:

```text
order.created
order.paid
```

9. Повтори тот же flow через Customer Store.

## Что происходит внутри

```text
Customer Store / QA Dashboard
  -> nginx
  -> order-service
  -> user-service
  -> product-service
  -> payment-service
  -> order-db
  -> RabbitMQ
  -> notification-service
  -> notification-db
```

## Что проверять в интеграционном тесте

| Слой | Что проверить |
| --- | --- |
| UI | Кнопка checkout, status, order history. |
| Gateway | `/api/orders` доступен. |
| Order-service | Создан заказ, рассчитана сумма, статус корректен. |
| User-service | Пользователь существует и active. |
| Product-service | Товар существует, active, stock достаточный. |
| Payment-service | Платеж authorized/declined/timeout. |
| RabbitMQ | События опубликованы. |
| Notification-service | Уведомления созданы. |
| Observability | Метрики и логи отражают flow. |

## Негативные сценарии

- user id не существует;
- user заблокирован;
- product id не существует;
- product archived;
- quantity больше stock;
- payment failure;
- payment timeout;
- RabbitMQ недоступен;
- notification-service остановлен.

## Куда смотреть и почему

Order-service logs:

```powershell
docker compose logs --tail=100 order-service
```

RabbitMQ:

```text
http://localhost:15672
```

Notifications API:

```powershell
Invoke-WebRequest -Uri "http://localhost:8080/api/notifications?order_id=ORDER_ID" -UseBasicParsing
```

Grafana:

```text
Microservices QA Lab Overview
```

## Вопросы на собеседовании

### Вопрос: Что такое интеграционное тестирование?

Основной ответ:  
Это проверка взаимодействия компонентов. В этом проекте интеграционный тест заказа проверяет не только endpoint `/api/orders`, но и user-service, product-service, payment-service, RabbitMQ и notification-service.

Альтернативный ответ:  
Это проверка границ между сервисами и корректности общего бизнес-flow.

### Вопрос: Почему один успешный `POST /api/orders` недостаточен?

Основной ответ:  
Потому что нужно проверить side effects: заказ сохранился, статус корректен, payment обработан, события опубликованы, notification создана, метрики и логи не показывают скрытых ошибок.

Альтернативный ответ:  
Ответ API - только часть результата. В микросервисах важны изменения в других сервисах.

### Вопрос: Как локализовать дефект в order flow?

Основной ответ:  
Сначала смотрю response и request ID, потом логи order-service, затем readiness зависимостей, затем логи user/product/payment, состояние RabbitMQ и notifications. Так можно понять, сломался входной запрос, dependency call, payment, публикация события или consumer.

Альтернативный ответ:  
Иду по цепочке вызовов от gateway к downstream-сервисам.

## Критерий завершения урока

Ты можешь оформить заказ через UI, доказать его прохождение через несколько сервисов и объяснить каждый side effect.
