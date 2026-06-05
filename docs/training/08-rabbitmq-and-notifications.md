# Урок 08. RabbitMQ, события и уведомления

## Цель урока

Научиться тестировать асинхронную часть системы: order events, RabbitMQ queue, notification consumer и eventual consistency.

## Компетенции после урока

После урока ты должен уметь:

- объяснять exchange, queue, routing key, consumer, ack;
- проверять RabbitMQ UI;
- понимать eventual consistency;
- тестировать notification-service;
- проверять idempotency через `event_id`;
- локализовать проблемы async flow.

## Что сделать

1. Открой RabbitMQ:

```text
http://localhost:15672
guest / guest
```

2. Найди:

```text
orders.exchange
notification.order-events.queue
```

3. Открой QA Dashboard.

4. Создай заказ с payment `success`.

5. Перейди в RabbitMQ и проверь queue state.

6. В QA Dashboard нажми `Refresh` в Notifications.

7. Проверь события:

```text
order.created
order.paid
```

8. Останови notification-service:

```powershell
py -3 scripts\fault_lab.py enable notification-service-stop
```

9. Создай заказ.

10. Посмотри, что события ожидают consumer.

11. Восстанови:

```powershell
py -3 scripts\fault_lab.py disable notification-service-stop
```

12. Проверь, что notification-service обработал накопленные события.

## Куда смотреть и почему

RabbitMQ UI показывает состояние очередей и consumers.

Notification API показывает фактический результат обработки event:

```powershell
Invoke-WebRequest -Uri "http://localhost:8080/api/notifications?order_id=ORDER_ID" -UseBasicParsing
```

Notification-service logs:

```powershell
docker compose logs --tail=100 notification-service
```

Order-service logs:

```text
order_event_published
```

## Что важно понять

Асинхронная система не обязана дать результат мгновенно. Заказ может быть создан, а notification появится через небольшую задержку.

Это называется eventual consistency: система становится согласованной через время.

Idempotency нужна, чтобы повторная обработка одного события не создала дубликаты.

## Вопросы на собеседовании

### Вопрос: Что такое RabbitMQ queue?

Основной ответ:  
Queue хранит сообщения до тех пор, пока consumer их не обработает. В проекте `notification.order-events.queue` хранит события заказов для notification-service.

Альтернативный ответ:  
Это буфер сообщений между producer и consumer.

### Вопрос: Что такое exchange?

Основной ответ:  
Exchange принимает сообщения и маршрутизирует их в очереди по routing rules. В проекте order-service публикует order events в `orders.exchange`.

Альтернативный ответ:  
Exchange - входная точка публикации сообщений.

### Вопрос: Почему notification может появиться позже заказа?

Основной ответ:  
Потому что notification создается асинхронно. Order-service публикует событие в RabbitMQ, а notification-service обрабатывает его отдельно. Между этими шагами возможна задержка.

Альтернативный ответ:  
Это eventual consistency.

### Вопрос: Как тестировать async behavior?

Основной ответ:  
Нужно использовать polling, проверять queue state, consumer logs и итоговый API результата. Нельзя ожидать, что notification появится в ту же миллисекунду, что и order response.

Альтернативный ответ:  
Проверять событие и результат с разумным ожиданием.

## Критерий завершения урока

Ты можешь создать заказ, найти его события в notification-service, объяснить роль RabbitMQ и показать, что происходит при остановке consumer.
