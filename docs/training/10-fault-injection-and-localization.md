# Урок 10. Fault injection и локализация дефектов

## Цель урока

Научиться намеренно ломать систему фича-флагами, воспроизводить production-like симптомы, локализовать компонент и возвращать стенд в baseline.

## Компетенции после урока

После урока ты должен уметь:

- использовать `scripts/fault_lab.py`;
- включать и выключать fault flags;
- отличать проблему gateway, сервиса, БД, Redis, RabbitMQ и observability;
- собирать evidence;
- писать runbook локализации;
- объяснять production-grade fix.

## Что сделать

Посмотреть все флаги:

```powershell
py -3 scripts\fault_lab.py list
```

Посмотреть описание:

```powershell
py -3 scripts\fault_lab.py show payment-timeout
```

Включить поломку:

```powershell
py -3 scripts\fault_lab.py enable payment-timeout
```

Проверить симптом:

1. Создай заказ.
2. Посмотри статус.
3. Посмотри latency в Grafana.
4. Посмотри логи order-service.

Выключить:

```powershell
py -3 scripts\fault_lab.py disable payment-timeout
py -3 scripts\fault_lab.py smoke
```

Если система в непонятном состоянии:

```powershell
py -3 scripts\fault_lab.py restore-all
```

## Обязательные сценарии

Пройди минимум эти fault flags:

```text
payment-timeout
payment-service-stop
redis-stop
rabbitmq-stop
notification-service-stop
gateway-stop
prometheus-stop
```

## Как локализовать

1. Что видит пользователь?
2. Какой endpoint отвечает ошибкой?
3. Что показывает `docker compose ps`?
4. Что показывает smoke?
5. Есть ли ошибка в логах gateway?
6. Есть ли ошибка в логах сервиса-оркестратора?
7. Жива ли dependency?
8. Есть ли события в RabbitMQ?
9. Есть ли деградация в Grafana?
10. Какой минимальный restore нужен?

## Таблица локализации

| Симптом | Вероятная зона |
| --- | --- |
| UI не открывается | nginx/gateway/static UI. |
| `/api/users/ready` падает | user-service или user-db. |
| Catalog пустой | product-service/product-db/data. |
| Cache не HIT | Redis/cache invalidation. |
| Checkout медленный | payment timeout/order dependency. |
| Нет notification | RabbitMQ или notification-service. |
| Grafana пустая | Prometheus/Grafana/datasource. |

## Вопросы на собеседовании

### Вопрос: Что такое fault injection?

Основной ответ:  
Это намеренное внесение контролируемых отказов в систему, чтобы проверить поведение при production-like проблемах: падение сервиса, timeout, сетевой разрыв, отказ БД, потеря очереди.

Альтернативный ответ:  
Это способ тренировать resilience и runbook диагностику.

### Вопрос: Как ты локализуешь проблему в микросервисах?

Основной ответ:  
Иду от пользовательского симптома к технической цепочке: UI, gateway response, service readiness, logs, dependency state, RabbitMQ/Redis, metrics. Использую request ID и проверяю каждый сервис по flow.

Альтернативный ответ:  
Не угадываю, а сужаю область по evidence.

### Вопрос: Почему просто restart - не полноценный фикс?

Основной ответ:  
Restart может временно восстановить сервис, но не устраняет root cause. В реальном проекте нужно понять причину: memory leak, deadlock, bad deployment, network issue, DB pool exhaustion, timeout config.

Альтернативный ответ:  
Restart - recovery action, но не root-cause fix.

## Критерий завершения урока

Ты можешь включить fault flag, воспроизвести симптом, доказать причину evidence-ом, восстановить стенд и объяснить production fix.
