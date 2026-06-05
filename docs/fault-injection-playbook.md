# Fault Injection Playbook

Этот документ описывает CLI-утилиту `scripts/fault_lab.py` и набор fault flags для ручного моделирования production-like ситуаций: падение сервиса, зависание, сетевой разрыв, отказ БД, отказ кеша, отказ очереди, деградация платежной зависимости и потеря observability.

Утилита предназначена только для локального стенда `microservices-qa-lab`. Не запускай такие команды на реальном production-окружении.

## Быстрый старт

На Windows в этом окружении используй:

```powershell
py -3 scripts\fault_lab.py list
py -3 scripts\fault_lab.py show payment-timeout
py -3 scripts\fault_lab.py enable payment-timeout
py -3 scripts\fault_lab.py disable payment-timeout
py -3 scripts\fault_lab.py restore-all
py -3 scripts\fault_lab.py smoke
```

На Linux/macOS обычно:

```bash
python3 scripts/fault_lab.py list
python3 scripts/fault_lab.py enable payment-timeout
python3 scripts/fault_lab.py restore-all
```

Полный сброс данных:

```powershell
py -3 scripts\fault_lab.py reset-data --yes
```

`restore-all` не удаляет volumes и не чистит БД. Он возвращает контейнеры, сеть и payment mode в рабочее состояние. `reset-data --yes` удаляет volumes и пересоздает стенд с чистыми базами.

## Базовый алгоритм работы тестировщика

1. Поднять стенд:

```powershell
docker compose up -d --build
py -3 scripts\fault_lab.py smoke
```

2. Включить поломку:

```powershell
py -3 scripts\fault_lab.py enable FLAG_NAME
```

3. Воспроизвести пользовательский сценарий через UI или API.

4. Собрать evidence:

```powershell
docker compose ps
docker compose logs --tail=100 order-service
docker compose logs --tail=100 payment-service
docker compose logs --tail=100 notification-service
```

5. Проверить RabbitMQ, если сценарий связан с событиями:

```text
http://localhost:15672
guest / guest
```

6. Проверить Grafana/Prometheus:

```text
http://localhost:3000
http://localhost:9090
```

7. Вернуть стенд:

```powershell
py -3 scripts\fault_lab.py disable FLAG_NAME
py -3 scripts\fault_lab.py smoke
```

Если состояние непонятное:

```powershell
py -3 scripts\fault_lab.py restore-all
py -3 scripts\fault_lab.py smoke
```

## Каталог fault flags

| Flag | Категория | Что моделирует |
| --- | --- | --- |
| `payment-decline` | payment | Бизнес-отказ платежа. |
| `payment-timeout` | payment | Медленная платежная зависимость. |
| `payment-random` | payment | Нестабильное поведение платежной зависимости. |
| `payment-service-stop` | dependency | Падение payment-service. |
| `payment-service-pause` | dependency | Зависание payment-service. |
| `payment-service-disconnect` | network | Сетевой разрыв payment-service. |
| `user-service-stop` | dependency | Падение user-service. |
| `user-service-pause` | dependency | Зависание user-service. |
| `user-db-stop` | database | Падение user-db. |
| `user-db-disconnect` | network | Сетевой разрыв между user-service и user-db. |
| `product-service-stop` | dependency | Падение product-service. |
| `product-db-stop` | database | Падение product-db. |
| `product-db-disconnect` | network | Сетевой разрыв между product-service и product-db. |
| `redis-stop` | cache | Падение Redis. |
| `redis-pause` | cache | Зависание Redis. |
| `redis-cache-flush` | cache | Потеря кеша. |
| `order-service-stop` | core | Падение order-service. |
| `order-service-pause` | core | Зависание order-service. |
| `order-db-stop` | database | Падение order-db. |
| `rabbitmq-stop` | messaging | Падение RabbitMQ. |
| `rabbitmq-pause` | messaging | Зависание RabbitMQ. |
| `rabbitmq-disconnect` | network | Сетевой разрыв RabbitMQ. |
| `rabbitmq-queue-purge` | messaging | Потеря pending-событий уведомлений. |
| `notification-service-stop` | messaging | Остановлен consumer уведомлений. |
| `notification-service-pause` | messaging | Завис consumer уведомлений. |
| `notification-db-stop` | database | Падение notification-db. |
| `gateway-stop` | gateway | Падение публичного API Gateway. |
| `prometheus-stop` | observability | Остановлен сбор метрик. |
| `grafana-stop` | observability | Недоступны dashboards. |
| `observability-stop` | observability | Полная потеря Prometheus + Grafana. |

## Сценарии

### 1. `payment-decline`

Что ломает: payment-service начинает возвращать `declined`. Инфраструктурно все healthy, но новые заказы уходят в `payment_failed`.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable payment-decline
```

Локализовать:

- создать заказ через UI;
- проверить response order-service;
- посмотреть `docker compose logs --tail=100 payment-service`;
- в Grafana посмотреть рост запросов к payment-service без 5xx.

Реальный фикс: это не обязательно баг. Нужно проверить бизнес-правила отказа платежа, корректность статуса заказа, текст ошибки для клиента и отсутствие повторного списания.

### 2. `payment-timeout`

Что ломает: payment-service отвечает дольше, чем `order-service` готов ждать. Заказ должен стать `payment_failed`, latency вырастет.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable payment-timeout
```

Локализовать:

- создать заказ;
- проверить, что запрос стал медленнее;
- посмотреть `payment_timeout` в логах order-service;
- в Grafana проверить p95 latency.

Реальный фикс: настроить timeout, retry policy, circuit breaker, fallback-стратегию и алерт на рост latency.

### 3. `payment-random`

Что ломает: платежная зависимость становится нестабильной: часть заказов оплачивается, часть падает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable payment-random
```

Локализовать:

- создать несколько заказов подряд;
- сравнить статусы `paid` и `payment_failed`;
- проверить логи payment-service и order-service;
- посмотреть распределение статусов в Grafana.

Реальный фикс: убрать недетерминированность из тестового окружения, в production добавить мониторинг success rate и retry/compensation logic.

### 4. `payment-service-stop`

Что ломает: payment-service остановлен.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable payment-service-stop
```

Локализовать:

- `docker compose ps`;
- `/api/payments/ready`;
- создать заказ и проверить поведение order-service;
- логи order-service должны указывать на недоступную dependency.

Реальный фикс: восстановить сервис, проверить deployment, healthcheck, autoscaling, rollback и алерты.

### 5. `payment-service-pause`

Что ломает: контейнер payment-service не падает, а зависает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable payment-service-pause
```

Локализовать:

- `docker compose ps` покажет paused-состояние;
- запросы к payment-service будут висеть;
- order-service должен отработать timeout;
- Grafana покажет рост latency.

Реальный фикс: timeouts обязательны. Нужны liveness probes, restart policy, thread/process dump, анализ deadlock или saturation.

### 6. `payment-service-disconnect`

Что ломает: payment-service жив, но отключен от Docker network.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable payment-service-disconnect
```

Локализовать:

- контейнер может быть `Up`;
- order-service не сможет установить сетевое соединение;
- смотреть `dependency_http_error` / connection errors;
- Prometheus target payment-service может стать `down`.

Реальный фикс: проверить service discovery, network policy, DNS, firewall, mesh/proxy routing.

### 7. `user-service-stop`

Что ломает: user API недоступен, order-service не может валидировать пользователя.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable user-service-stop
```

Локализовать:

- `/api/users/ready` не отвечает;
- создание пользователя невозможно;
- создание заказа с существующим user ID падает на user lookup.

Реальный фикс: восстановить user-service, проверить последние релизы, миграции, readiness и ошибки подключения к БД.

### 8. `user-service-pause`

Что ломает: user-service зависает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable user-service-pause
```

Локализовать:

- user routes зависают;
- order-service ловит timeout при user lookup;
- p95 latency растет.

Реальный фикс: liveness probe, dump процесса, поиск deadlock, ограничение connection pool, rate limiting.

### 9. `user-db-stop`

Что ломает: user-service не может работать с PostgreSQL.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable user-db-stop
```

Локализовать:

- `docker compose ps`;
- `/api/users/ready` должен стать `503`;
- логи user-service должны указывать на database error.

Реальный фикс: восстановить БД, проверить disk, CPU, connection limit, migrations, backup/restore и failover.

### 10. `user-db-disconnect`

Что ломает: БД user-service запущена, но сетевой путь до нее разорван.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable user-db-disconnect
```

Локализовать:

- DB container может быть `Up`;
- readiness user-service падает;
- логи содержат connection refused / network unreachable / DNS-like ошибки.

Реальный фикс: проверить network policy, security groups, DNS, Compose/Kubernetes service, firewall.

### 11. `product-service-stop`

Что ломает: product API недоступен, order-service не может валидировать товары.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable product-service-stop
```

Локализовать:

- `/api/products/ready`;
- создать заказ и увидеть ошибку product dependency;
- проверить логи order-service.

Реальный фикс: восстановить product-service, проверить deployment, миграции, Redis/DB зависимости.

### 12. `product-db-stop`

Что ломает: product-service теряет PostgreSQL.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable product-db-stop
```

Локализовать:

- `/api/products/ready` должен стать `503`;
- создание/получение продукта ломается;
- Redis cache может временно скрыть проблему для уже закешированных reads.

Реальный фикс: восстановить БД, проверить connection pool, disk, locks, migrations.

### 13. `product-db-disconnect`

Что ломает: product-db жив, но недоступен по сети.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable product-db-disconnect
```

Локализовать:

- product-db container `Up`;
- product-service readiness fails;
- Prometheus target product-service может остаться `up`, но `/ready` отдаст ошибку.

Реальный фикс: сетевой runbook: DNS, routes, firewall, Kubernetes service/endpoints, network policy.

### 14. `redis-stop`

Что ломает: Redis недоступен, product-service теряет cache dependency.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable redis-stop
```

Локализовать:

- `/api/products/ready` должен стать `503`;
- запросы продукта могут падать при cache access;
- `docker compose logs product-service`.

Реальный фикс: восстановить Redis, проверить eviction, memory, persistence, connection limit. В реальном проекте решить, должен ли cache быть critical dependency.

### 15. `redis-pause`

Что ломает: Redis зависает, а не падает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable redis-pause
```

Локализовать:

- product requests могут висеть;
- Grafana покажет рост latency;
- readiness может деградировать.

Реальный фикс: timeouts на Redis client, fallback без кеша, circuit breaker, monitoring Redis latency.

### 16. `redis-cache-flush`

Что ломает: очищает cache. Приложение работает, но все следующие product reads идут как `MISS`.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable redis-cache-flush
```

Локализовать:

- дважды запросить один продукт;
- первый запрос после flush должен быть `X-Cache: MISS`;
- второй запрос должен стать `X-Cache: HIT`.

Реальный фикс: это не баг, а cache loss. В production важно, чтобы приложение корректно работало при cold cache и не перегружало БД.

### 17. `order-service-stop`

Что ломает: главный orchestrator заказов недоступен.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable order-service-stop
```

Локализовать:

- `/api/orders/ready` не отвечает;
- UI order flow не работает;
- user/product/payment могут быть healthy.

Реальный фикс: rollback/restart order-service, проверить deployment, env vars, БД, RabbitMQ и downstream dependencies.

### 18. `order-service-pause`

Что ломает: order-service зависает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable order-service-pause
```

Локализовать:

- gateway может долго ждать upstream;
- order routes не отвечают;
- Grafana показывает latency/error rate.

Реальный фикс: liveness probe, restart hung process, profiling, поиск deadlock или thread starvation.

### 19. `order-db-stop`

Что ломает: order-service не может сохранять заказы.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable order-db-stop
```

Локализовать:

- `/api/orders/ready` должен стать `503`;
- create order не должен успешно завершаться;
- логи order-service укажут на database readiness.

Реальный фикс: восстановить БД, проверить locks, migrations, pool exhaustion, failover.

### 20. `rabbitmq-stop`

Что ломает: очередь событий недоступна.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable rabbitmq-stop
```

Локализовать:

- order-service и notification-service readiness должны деградировать;
- orders exchange недоступен;
- notification events не публикуются.

Реальный фикс: восстановить RabbitMQ node, проверить disk alarm, memory alarm, cluster partition, durable queues, DLQ.

### 21. `rabbitmq-pause`

Что ломает: RabbitMQ зависает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable rabbitmq-pause
```

Локализовать:

- RabbitMQ container paused;
- AMQP operations hang;
- notification flow останавливается;
- latency и readiness ухудшаются.

Реальный фикс: liveness/restart, cluster health, queue depth monitoring, connection timeout.

### 22. `rabbitmq-disconnect`

Что ломает: RabbitMQ жив, но изолирован от Docker network.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable rabbitmq-disconnect
```

Локализовать:

- RabbitMQ UI может быть доступен с хоста;
- сервисы не могут подключиться по AMQP;
- readiness order/notification падает.

Реальный фикс: проверить network policy, DNS, firewall, service discovery, cluster routes.

### 23. `rabbitmq-queue-purge`

Что ломает: удаляет pending messages из `notification.order-events.queue`.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable notification-service-stop
# создать заказ
py -3 scripts\fault_lab.py enable rabbitmq-queue-purge
py -3 scripts\fault_lab.py disable notification-service-stop
```

Локализовать:

- заказ создан;
- notification не появляется;
- в RabbitMQ queue пустая;
- в логах notification-service нет обработки события.

Реальный фикс: purged messages нельзя восстановить без outbox/replay. Нужны durable events, outbox pattern, replay mechanism, audit log.

### 24. `notification-service-stop`

Что ломает: consumer уведомлений остановлен.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable notification-service-stop
```

Локализовать:

- создать заказ;
- notification не появляется сразу;
- в RabbitMQ растет очередь;
- после restore consumer должен обработать накопленные сообщения.

Реальный фикс: восстановить consumer, проверить consumer lag, queue depth, dead letters, idempotency.

### 25. `notification-service-pause`

Что ломает: consumer уведомлений зависает.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable notification-service-pause
```

Локализовать:

- контейнер paused;
- queue может иметь ready/unacked messages;
- notification API может зависать.

Реальный фикс: liveness probe, consumer timeout, ack strategy, dead-lettering, restart policy.

### 26. `notification-db-stop`

Что ломает: notification-service не может сохранять обработанные events.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable notification-db-stop
```

Локализовать:

- `/api/notifications/ready` должен стать `503`;
- consumer может не сохранять события;
- логи notification-service покажут database error.

Реальный фикс: восстановить БД, проверить idempotency при повторной обработке, убедиться, что сообщения не потерялись.

### 27. `gateway-stop`

Что ломает: публичная точка входа `http://localhost:8080` недоступна.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable gateway-stop
```

Локализовать:

- UI не открывается;
- `/api/...` routes через gateway недоступны;
- прямые service ports `8001-8005` могут работать.

Реальный фикс: восстановить ingress/gateway, проверить конфиг маршрутизации, upstreams, deployment, certificates, load balancer.

### 28. `prometheus-stop`

Что ломает: сбор метрик прекращается.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable prometheus-stop
```

Локализовать:

- `http://localhost:9090` недоступен;
- Grafana panels показывают ошибки datasource;
- приложение при этом может работать.

Реальный фикс: восстановить monitoring stack, проверить retention storage, config, scrape targets, alerting.

### 29. `grafana-stop`

Что ломает: dashboards недоступны, но Prometheus может продолжать собирать метрики.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable grafana-stop
```

Локализовать:

- `http://localhost:3000` недоступен;
- `http://localhost:9090` продолжает работать;
- метрики не потеряны, потерян UI наблюдения.

Реальный фикс: восстановить Grafana, проверить datasource provisioning, dashboard provisioning, auth, storage.

### 30. `observability-stop`

Что ломает: одновременно выключает Prometheus и Grafana.

Воспроизвести:

```powershell
py -3 scripts\fault_lab.py enable observability-stop
```

Локализовать:

- приложение работает;
- нет dashboard;
- нет новых метрик;
- QA теряет часть evidence для расследования.

Реальный фикс: monitoring stack должен быть высокодоступным. Нужны алерты на сам monitoring, remote write или external storage, резервные dashboards/runbooks.

## Шаблон баг-репорта по fault scenario

```text
Title:
Fault flag:
Environment:
Build / commit:
Preconditions:
Steps to reproduce:
Expected result:
Actual result:
Impact:
Severity:
Priority:
Request ID:
Logs:
Metrics:
RabbitMQ state:
Recovery result:
Suspected component:
Recommendation:
```

## Что считать сильным уровнем

Сценарий считается освоенным, если ты можешь:

- включить fault flag без подсказки;
- воспроизвести симптом через UI/API;
- объяснить, какой компонент сломан;
- подтвердить вывод логами, метриками или состоянием очереди;
- вернуть систему в baseline;
- объяснить production-grade фикс, а не только "перезапустить контейнер".

## Быстрое восстановление

Обычный restore:

```powershell
py -3 scripts\fault_lab.py restore-all
py -3 scripts\fault_lab.py smoke
```

Полный reset с удалением данных:

```powershell
py -3 scripts\fault_lab.py reset-data --yes
py -3 scripts\fault_lab.py smoke
```
