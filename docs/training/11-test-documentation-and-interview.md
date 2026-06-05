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

## Перед практикой: что нужно понять

Тестовая документация - это не бюрократия. Это способ передать команде, что именно проверялось, почему это важно, какие риски остаются и какие дефекты подтверждены evidence-ом.

Сильный QA отличается не количеством слов в документе, а качеством мышления: он умеет отделять цель тестирования от шагов, expected behavior от actual behavior, symptom от root cause, severity от priority.

### Какие документы нужны и зачем

В этом уроке ты готовишь набор артефактов, похожий на реальную работу QA в проекте.

| Артефакт | Зачем нужен | Что должен показывать |
| --- | --- | --- |
| Test Plan | Объяснить стратегию тестирования. | Scope, риски, окружение, подход, критерии входа/выхода. |
| Checklist | Быстро покрыть область проверками. | Что должно быть проверено без лишней детализации шагов. |
| Test Cases | Зафиксировать воспроизводимые сценарии. | Preconditions, steps, expected result, test data. |
| Bug Report | Передать дефект разработчику. | Steps, actual, expected, evidence, impact, suspected component. |
| Test Summary | Подвести итог тестового цикла. | Что проверено, что найдено, что заблокировано, residual risk. |

### Test Plan vs Checklist vs Test Case

Test Plan отвечает на вопрос:

```text
Как мы будем тестировать эту систему и какие риски покрываем?
```

Checklist отвечает на вопрос:

```text
Что нужно не забыть проверить?
```

Test Case отвечает на вопрос:

```text
Как точно воспроизвести конкретную проверку и какой результат ожидается?
```

Одна и та же область может быть описана на разных уровнях.

Пример для checkout:

```text
Test Plan:
Проверить критичный e-commerce flow заказа через UI, API и observability.

Checklist:
- Валидный пользователь может оформить заказ.
- Заблокированный пользователь не может оформить заказ.
- Payment decline не создает paid order.
- После заказа появляется notification.

Test Case:
Precondition: user active, product active, stock >= 1, payment mode success.
Steps: открыть магазин, добавить товар, оформить заказ.
Expected: order.status = paid, notification created.
```

### Что такое хороший bug report

Хороший bug report позволяет разработчику воспроизвести проблему без личного созвона с QA.

Минимальный состав:

- title: коротко и конкретно;
- environment: где найдено;
- preconditions: что было настроено;
- steps to reproduce: шаги без пропусков;
- actual result: что произошло;
- expected result: что должно было произойти;
- evidence: скриншоты, response body, status code, request id, logs;
- impact: что теряет пользователь или бизнес;
- severity/priority;
- suspected component, если есть основания.

Плохой баг:

```text
Checkout не работает.
```

Сильный баг:

```text
Checkout returns 504 when payment mode is timeout; order is not created, UI shows raw backend error.
Evidence: request id ..., POST /api/orders -> 504, order-service logs show payment-service timed out.
Impact: user cannot complete purchase during payment provider degradation.
```

### Severity и priority

Severity - насколько серьезно поведение ломает продукт.

Priority - насколько срочно команде нужно это исправить.

Пример:

```text
Опечатка в админском тексте: low severity, low priority.
Checkout не работает для всех пользователей: critical severity, high priority.
Редкий edge case в тестовом dashboard: medium/low severity, низкий priority.
Юридически неверный текст в платежах: может быть low technical severity, но high business priority.
```

На собеседовании важно не называть severity механически. Нужно объяснять impact.

### Evidence важнее догадки

QA может предположить suspected component, но не должен выдавать догадку за факт.

Правильная формулировка:

```text
Suspected component: payment-service, because POST /api/orders returns 504 and order-service logs contain payment timeout with the same request id.
```

Неправильная формулировка:

```text
Проблема в payment-service, потому что я так думаю.
```

Evidence может быть:

- status code;
- response body;
- request/response payload;
- screenshot UI;
- `X-Request-ID`;
- фрагмент логов;
- RabbitMQ queue state;
- Grafana screenshot;
- команда воспроизведения;
- fault flag, который включен.

### Как рассказывать проект на собеседовании

Твоя цель - не перечислить технологии, а показать инженерное мышление.

Слабый рассказ:

```text
Я тестировал микросервисы, Docker, RabbitMQ, Grafana.
```

Сильный рассказ:

```text
Я тестировал учебный e-commerce проект на микросервисах. Пользователь проходит каталог, аккаунт, корзину и checkout. Запросы идут через nginx gateway в отдельные сервисы: user, product, order, payment, notification. Я проверял UI, API-контракты, статусы ответов, Redis cache для товаров, RabbitMQ events для уведомлений, Grafana/Prometheus для метрик и fault flags для production-like отказов. Дефекты локализовал по request id, логам, readiness и состоянию зависимостей.
```

### Что должен проговаривать QA

Перед подготовкой документации проговаривай:

```text
Кто будет читать этот документ?
Какое решение он должен помочь принять?
Есть ли evidence для каждого вывода?
Понятен ли impact?
Не смешал ли я symptom и root cause?
Может ли другой QA воспроизвести проверку по моим шагам?
Смогу ли я защитить этот вывод на собеседовании?
```

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
