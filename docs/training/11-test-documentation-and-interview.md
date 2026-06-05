# Урок 11. Тестовая документация и собеседование

## Цель урока

Научиться оформлять работу тестировщика профессионально: test plan, checklist, test cases, bug report, test summary и собеседовательный рассказ.

## Компетенции после урока

После урока ты должен уметь:

- писать test plan;
- составлять чек-листы и test cases;
- оформлять баг-репорт с evidence;
- готовить test summary report;
- объяснять проект на собеседовании;
- отвечать на вопросы с альтернативными формулировками.

## Что сделать

Подготовь 5 документов в своей рабочей папке:

```text
test-plan.md
checklist.md
test-cases.md
bug-reports.md
test-summary.md
```

## Test Plan

Минимальная структура:

```text
Project:
Scope:
Out of scope:
Environment:
Test data:
Risks:
Entry criteria:
Exit criteria:
Test types:
Tools:
Deliverables:
```

Что включить в scope:

- Customer Store;
- QA Dashboard;
- user-service;
- product-service;
- order-service;
- payment-service;
- notification-service;
- Redis cache;
- RabbitMQ events;
- Prometheus/Grafana;
- fault injection.

## Checklist

Пример:

```text
Customer Store
- Page opens
- Catalog loads
- Seed catalog works
- Search works
- Category filter works
- Add to cart works
- Quantity changes total
- Account creation works
- Checkout creates order
- Order history shows status

Backend
- Users can be created
- Duplicate email returns 409
- Bad email returns 422
- Product cache returns MISS/HIT
- Payment failure creates payment_failed order
- Payment timeout handled
- RabbitMQ notifications created
```

## Bug Report

Шаблон:

```text
Title:
Environment:
Build:
Preconditions:
Steps to reproduce:
Actual result:
Expected result:
Severity:
Priority:
Evidence:
Logs:
Metrics:
Request ID:
Suspected component:
Workaround:
```

## Test Summary

Шаблон:

```text
Test period:
Scope covered:
Not covered:
Passed checks:
Failed checks:
Critical bugs:
Known risks:
Environment stability:
Recommendation:
```

## Собеседовательный рассказ

Готовый short pitch:

```text
Я работал с локальным микросервисным e-commerce стендом. В нем есть customer storefront, QA dashboard, API gateway, user/product/order/payment/notification services, PostgreSQL базы, Redis cache, RabbitMQ events, Prometheus и Grafana. Я вручную тестировал пользовательский flow покупки, API contracts, cache behavior, payment failures, async notifications, logs/metrics и fault injection scenarios. Для локализации использовал request ID, Docker logs, RabbitMQ UI и Grafana.
```

## STAR истории

Подготовь 5 историй:

1. Happy path checkout.
2. Payment timeout.
3. Redis cache issue.
4. Notification delay через RabbitMQ.
5. Gateway/network issue после fault injection.

Формат:

```text
Situation:
Task:
Action:
Result:
```

## Вопросы на собеседовании

### Вопрос: Какую систему ты тестировал?

Основной ответ:  
Я тестировал микросервисный e-commerce проект с customer storefront и QA dashboard. Backend состоит из user, product, order, payment и notification services. Также есть PostgreSQL, Redis, RabbitMQ, nginx gateway, Prometheus и Grafana.

Альтернативный ответ:  
Это учебный, но production-like стенд интернет-магазина для ручного QA микросервисов.

### Вопрос: Какие компетенции ты получил?

Основной ответ:  
Ручное API testing, e2e checkout testing, negative testing, contract checks, cache testing, async event testing, fault injection, Docker Compose, logs, metrics, Grafana/Prometheus, RabbitMQ diagnostics и оформление QA artifacts.

Альтернативный ответ:  
Я научился тестировать не только UI, но и внутреннее поведение микросервисной системы.

### Вопрос: Какой самый сильный кейс ты можешь рассказать?

Основной ответ:  
Payment timeout. Я включал controlled fault, создавал заказ, видел рост latency в UI и Grafana, находил `payment_timeout` в логах order-service, проверял, что заказ не ломает систему, а переходит в `payment_failed`, затем возвращал payment mode в success.

Альтернативный ответ:  
Асинхронные notifications через RabbitMQ, потому что там нужно учитывать eventual consistency и проверять не только API response, но и очередь/consumer.

### Вопрос: Как ты определяешь severity и priority?

Основной ответ:  
Severity - техническое или пользовательское влияние дефекта. Priority - срочность исправления для бизнеса/релиза. Например, checkout не работает - high severity и high priority. Ошибка в тексте на второстепенной странице - low severity, priority зависит от релиза.

Альтернативный ответ:  
Severity отвечает "насколько больно", priority - "как срочно чинить".

## Критерий завершения урока

У тебя есть полный комплект QA-документов и 5 подготовленных историй для собеседования.
