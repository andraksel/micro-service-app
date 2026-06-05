# Учебная программа

Эта папка содержит отдельные уроки для обучения ручному QA на проекте `microservices-qa-lab`.

Главная идея: сначала ты проходишь систему как обычный пользователь через `Customer Store`, потом как тестировщик через `QA Dashboard`, затем как инженер качества через API, Docker, RabbitMQ, Redis, Grafana, Prometheus, логи и fault injection.

Каждый урок устроен одинаково: сначала объясняется теория и роль компонента в системе, потом идут ручные действия, точки наблюдения, вопросы для собеседования и критерий завершения.

## Как проходить

1. Подними стенд:

```powershell
cd C:\microservices-qa-lab
docker compose up -d --build
py -3 scripts\fault_lab.py smoke
```

2. Открой пользовательский интерфейс:

```text
http://localhost:8080/store.html
```

3. Открой QA Dashboard:

```text
http://localhost:8080
```

4. Начни с урока `00-system-concepts-glossary.md`. Это не практический чек-лист, а словарь и карта системы. Без него остальные уроки будут восприниматься как набор команд.

5. Проходи остальные уроки строго по порядку.

6. После каждого урока сохраняй артефакты: чек-листы, тест-кейсы, баг-репорты, заметки расследования, скриншоты и выводы.

## Уроки

| Урок | Файл | Главная компетенция |
| --- | --- | --- |
| 00 | `00-system-concepts-glossary.md` | Базовое понимание nginx, gateway, сервисов, баз, Redis, RabbitMQ, Prometheus, Grafana и flow запроса. |
| 01 | `01-environment-and-mental-model.md` | Запуск стенда, понимание сервисов и окружения. |
| 02 | `02-storefront-smoke-and-user-journey.md` | Прохождение приложения как пользователь магазина. |
| 03 | `03-api-contracts-and-status-codes.md` | API, контракты, статусы, схемы запросов и ответов. |
| 04 | `04-user-account-and-validation.md` | Тестирование аккаунтов, валидации и пользовательских данных. |
| 05 | `05-catalog-products-and-redis-cache.md` | Каталог, товары, stock, Redis cache, `HIT/MISS`. |
| 06 | `06-order-flow-and-integration.md` | Интеграционный order flow через несколько сервисов. |
| 07 | `07-payment-failures-and-resilience.md` | Payment failure, timeout, resilience, controlled dependency. |
| 08 | `08-rabbitmq-and-notifications.md` | RabbitMQ, events, queues, notification-service, eventual consistency. |
| 09 | `09-observability-logs-metrics-grafana.md` | Логи, `X-Request-ID`, Prometheus, Grafana, метрики. |
| 10 | `10-fault-injection-and-localization.md` | Fault flags, поломки, локализация, восстановление. |
| 11 | `11-test-documentation-and-interview.md` | Тестовая документация и подготовка к собеседованию. |
| 12 | `12-final-exam.md` | Итоговый экзамен по всему проекту. |

## Правило сильного уровня

Ты не просто нажимаешь кнопки. На каждом шаге ты должен ответить:

- что я проверяю;
- почему это важно;
- какой сервис отвечает за поведение;
- какие данные меняются;
- где я могу увидеть подтверждение;
- какой баг мог бы быть найден;
- как я объясню это на собеседовании.

Если ты можешь уверенно отвечать на эти вопросы без подсказок, компетенция считается закрепленной.
