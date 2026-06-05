# microservices-qa-lab

Локальный учебный проект для тестировщика, который хочет разобраться в реальном микросервисном приложении.

Это небольшой интернет-магазин с пользовательским интерфейсом, QA Dashboard, API Gateway, несколькими backend-сервисами, базами данных, Redis, RabbitMQ, Prometheus и Grafana. Проект можно запускать полностью на своем компьютере через Docker Compose. Платные облачные сервисы не нужны.

На этом проекте можно тренировать:

- ручное тестирование UI и API;
- интеграционное тестирование нескольких сервисов;
- проверку контрактов запросов и ответов;
- работу с RabbitMQ и асинхронными событиями;
- проверку Redis cache;
- диагностику через логи, метрики, Prometheus и Grafana;
- моделирование поломок через fault injection;
- подготовку к собеседованию QA / QA Automation.

## Архитектура

```mermaid
flowchart LR
    Tests["client / pytest"] --> Gateway["Nginx API Gateway :8080"]
    Gateway --> User["user-service"]
    Gateway --> Product["product-service"]
    Gateway --> Order["order-service"]
    Gateway --> Payment["payment-service"]
    Gateway --> Notification["notification-service"]

    User --> UserDb[("user-db PostgreSQL")]
    Product --> ProductDb[("product-db PostgreSQL")]
    Product --> Redis[("Redis cache")]
    Order --> OrderDb[("order-db PostgreSQL")]
    Order --> User
    Order --> Product
    Order --> Payment
    Order --> Rabbit["RabbitMQ orders.exchange"]
    Rabbit --> Notification
    Notification --> NotificationDb[("notification-db PostgreSQL")]
    Prometheus["Prometheus :9090"] --> User
    Prometheus --> Product
    Prometheus --> Order
    Prometheus --> Payment
    Prometheus --> Notification
    Grafana["Grafana :3000"] --> Prometheus
```

Пользователь открывает магазин через `nginx`. `nginx` работает как API Gateway: принимает внешние запросы на `http://localhost:8080` и отправляет их в нужный сервис.

Например:

- создание пользователя идет в `user-service`;
- каталог товаров идет в `product-service`;
- оформление заказа идет в `order-service`;
- платеж проверяется через `payment-service`;
- уведомление о заказе создается через `notification-service` после события в RabbitMQ.

## Сервисы

| Сервис | За что отвечает |
| --- | --- |
| `user-service` | Пользователи, email, имя, статус аккаунта. |
| `product-service` | Каталог товаров, цены, остатки на складе, Redis cache. |
| `order-service` | Создание заказов, проверка пользователя, товаров и платежа. |
| `payment-service` | Тестовая платежная система: success, failure, timeout, random. |
| `notification-service` | Читает события заказов из RabbitMQ и создает уведомления. |
| `nginx` | Единая точка входа в приложение: `http://localhost:8080`. |
| `prometheus` | Собирает метрики сервисов с `/metrics`. |
| `grafana` | Показывает метрики в готовом dashboard. |

## Быстрый запуск

Перейди в папку проекта. Если работаешь с текущей локальной папкой, команда будет такой:

```powershell
cd C:\microservices-qa-lab
```

Если ты клонировал репозиторий из GitHub в другое место, перейди в свою папку проекта.

И запусти все сервисы:

```powershell
docker compose up --build
```

Если хочешь запустить в фоне, используй:

```powershell
docker compose up -d --build
```

После запуска открой:

```text
http://localhost:8080
```

Это главный вход через gateway.

## Пользовательский магазин

Пользовательский интерфейс магазина:

```text
http://localhost:8080/store.html
```

В нем можно:

- посмотреть каталог товаров;
- создать аккаунт покупателя;
- добавить товары в корзину;
- оформить заказ;
- посмотреть историю заказов;
- увидеть статус заказа;
- проверить, что обычный пользователь видит систему как реальный интернет-магазин.

Этот UI работает через те же backend-сервисы, что и тесты: `user-service`, `product-service`, `order-service`, `payment-service` и `notification-service`.

## QA Dashboard

QA Dashboard:

```text
http://localhost:8080
```

Он нужен тестировщику. Через него можно быстро:

- создавать пользователей;
- создавать товары;
- создавать заказы;
- переключать режим платежей;
- проверять Redis cache через `X-Cache`;
- смотреть уведомления;
- открывать Swagger UI сервисов;
- переходить в RabbitMQ, Grafana и Prometheus.

## Полезные web-инструменты

RabbitMQ Management UI:

```text
http://localhost:15672
guest / guest
```

RabbitMQ нужен, чтобы смотреть очереди и события заказов.

Grafana:

```text
http://localhost:3000
admin / admin
```

Grafana нужна, чтобы смотреть dashboard с метриками: количество запросов, ошибки, latency и состояние сервисов.

Prometheus:

```text
http://localhost:9090
```

Prometheus собирает метрики с сервисов и хранит их для Grafana.

## Остановка и полный сброс

Остановить контейнеры:

```powershell
docker compose down
```

Остановить контейнеры и удалить все данные из баз, Redis и RabbitMQ:

```powershell
docker compose down -v
```

Команда `down -v` полезна, когда нужно начать с полностью чистого стенда.

## Проверка, что стенд живой

Быстрая smoke-проверка:

```powershell
py -3 scripts\fault_lab.py smoke
```

Она проверяет gateway, все backend-сервисы, Prometheus и Grafana.

Ожидаемый результат - все строки должны вернуться со статусом `200`.

## Запуск тестов

Установить зависимости для тестов на хосте:

```powershell
pip install -r requirements-dev.txt
```

Запустить все тесты:

```powershell
pytest
```

Запустить тесты по слоям:

```powershell
pytest -m api
pytest -m integration
pytest -m contract
pytest -m async_events
pytest -m cache
pytest -m resilience
```

Запустить тесты внутри Docker Compose:

```powershell
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm test-runner
```

## Учебный план для ручного QA

План обучения без автоматизации:

```text
docs/manual-qa-mastery-plan.md
```

В нем описано, как проходить проект руками: что проверять, какие артефакты готовить, какие вопросы могут быть на собеседовании и как на них отвечать.

Подробные уроки лежат здесь:

```text
docs/training/README.md
```

В папке `docs/training` есть отдельные уроки. В каждом уроке расписано:

- какие компетенции ты получишь;
- что именно делать тестировщику;
- куда смотреть в UI, API, Docker, RabbitMQ, Grafana и логах;
- почему эти проверки важны;
- какие evidence собирать;
- какие вопросы могут быть на собеседовании;
- как отвечать основным и альтернативным способом.

## Fault Injection CLI

В проекте есть CLI-утилита, которая умеет намеренно ломать приложение. Это нужно для тренировки реальных production-ситуаций.

Посмотреть список поломок:

```powershell
py -3 scripts\fault_lab.py list
```

Включить поломку payment timeout:

```powershell
py -3 scripts\fault_lab.py enable payment-timeout
```

Выключить поломку:

```powershell
py -3 scripts\fault_lab.py disable payment-timeout
```

Вернуть систему в рабочее состояние:

```powershell
py -3 scripts\fault_lab.py restore-all
```

Подробный playbook по поломкам:

```text
docs/fault-injection-playbook.md
```

## Основные gateway routes

Все внешние API-запросы идут через `nginx` на `http://localhost:8080`.

| Route | Куда проксируется |
| --- | --- |
| `/api/users` | `user-service /users` |
| `/api/products` | `product-service /products` |
| `/api/orders` | `order-service /orders` |
| `/api/payments` | `payment-service /payments` |
| `/api/payments/test-controls/payment-mode` | `payment-service /test-controls/payment-mode` |
| `/api/notifications` | `notification-service /notifications` |

У каждого сервиса есть:

- `/health` - процесс жив;
- `/ready` - сервис готов принимать рабочие запросы;
- `/metrics` - метрики для Prometheus.

Через gateway это выглядит так:

```text
http://localhost:8080/api/orders/ready
http://localhost:8080/api/orders/metrics
```

## Наблюдаемость

Prometheus каждые 5 секунд собирает метрики с внутренних сервисов:

```text
user-service:8000/metrics
product-service:8000/metrics
order-service:8000/metrics
payment-service:8000/metrics
notification-service:8000/metrics
```

Grafana автоматически получает datasource `Prometheus` и готовый dashboard `Microservices QA Lab Overview`.

Для тестировщика это полезно, потому что можно связать действие пользователя с техническим эффектом:

- создали заказ - выросло количество запросов;
- включили payment timeout - выросла latency;
- остановили сервис - появились ошибки;
- восстановили стенд - метрики вернулись к норме.

## Полезные команды

Посмотреть логи `order-service`:

```powershell
docker compose logs -f order-service
```

Посмотреть логи `notification-service`:

```powershell
docker compose logs -f notification-service
```

Проверить контейнеры:

```powershell
docker compose ps
```

Создать тестовые данные:

```powershell
python scripts/seed-data.py
```

Посмотреть метрики заказов через gateway:

```powershell
curl http://localhost:8080/api/orders/metrics
```

## Что можно тренировать как QA

- Проверка UI магазина от лица пользователя.
- Проверка QA Dashboard как внутреннего инструмента тестировщика.
- API-тестирование пользователей, товаров, заказов, платежей и уведомлений.
- Проверка status codes: `200`, `201`, `400`, `404`, `409`, `422`, `500`.
- Проверка Redis cache через `X-Cache: HIT` и `X-Cache: MISS`.
- Проверка RabbitMQ events, очередей и DLQ.
- Проверка eventual consistency: заказ создан сразу, уведомление приходит позже.
- Проверка идемпотентности уведомлений через уникальный `event_id`.
- Проверка логов с `X-Request-ID`.
- Проверка метрик Prometheus и dashboard в Grafana.
- Проверка отказов через fault injection.
- Подготовка тестовой документации: test plan, checklist, test cases, bug reports, test summary.

## Известные ограничения

- Схемы баз создаются через SQLAlchemy `create_all`; Alembic пока не используется.
- Остаток товара проверяется при создании заказа, но не резервируется и не уменьшается.
- `payment-service` хранит платежи в памяти, потому что это учебная контролируемая зависимость.
- Отказы моделируются детерминированно, но circuit breaker библиотека пока не добавлена.
- Логи доступны через Docker stdout; централизованный сбор логов через Loki или ELK можно добавить позже.

## Возможные следующие улучшения

- Добавить Kafka-вариант асинхронного flow.
- Добавить Pact contract tests.
- Добавить OpenTelemetry tracing.
- Добавить Loki для логов.
- Добавить Sentry для ошибок frontend/backend.
- Добавить GitHub Actions.
- Добавить Docker Compose profiles для разных режимов запуска.
- Добавить больше mutation и fault-injection сценариев.
