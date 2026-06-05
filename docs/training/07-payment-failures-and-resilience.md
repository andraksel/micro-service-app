# Урок 07. Payment failures и resilience

## Цель урока

Научиться проверять управляемые отказы payment-service: success, decline, timeout, random, stop, pause.

## Компетенции после урока

После урока ты должен уметь:

- моделировать business failure и technical failure;
- понимать controlled dependency;
- проверять timeout handling;
- локализовать проблему payment-service;
- смотреть влияние отказов на order status;
- объяснять resilience на собеседовании.

## Что сделать

Через QA Dashboard:

1. Выбери payment mode `success`.
2. Создай заказ.
3. Ожидай `paid`.

Затем:

1. Выбери payment mode `failure`.
2. Создай заказ.
3. Ожидай `payment_failed`.

Затем:

1. Выбери payment mode `timeout`.
2. Создай заказ.
3. Засеки, что запрос дольше обычного.
4. Ожидай `payment_failed`.

Через CLI:

```powershell
py -3 scripts\fault_lab.py enable payment-timeout
py -3 scripts\fault_lab.py disable payment-timeout
```

Останов payment-service:

```powershell
py -3 scripts\fault_lab.py enable payment-service-stop
py -3 scripts\fault_lab.py restore-all
```

## Business failure vs technical failure

Business failure:

```text
payment declined
```

Система работает, но бизнес-операция отказана.

Technical failure:

```text
payment-service unavailable
timeout
network error
```

Система или dependency работает некорректно.

## Куда смотреть и почему

Payment-service logs:

```powershell
docker compose logs --tail=100 payment-service
```

Order-service logs:

```powershell
docker compose logs --tail=100 order-service
```

Grafana:

```text
P95 Latency
Requests By Status
5xx Errors In 5m
```

## Что проверить

| Сценарий | Ожидаемый результат |
| --- | --- |
| `success` | Order status `paid`. |
| `failure` | Order status `payment_failed`. |
| `timeout` | Order status `payment_failed`, latency выше. |
| `random` | Часть заказов `paid`, часть `payment_failed`. |
| service stopped | Controlled error/degraded behavior, не падение всего стенда. |
| service paused | Timeout handling. |

## Вопросы на собеседовании

### Вопрос: Что такое controlled dependency?

Основной ответ:  
Это зависимость, поведение которой можно управлять в тестовой среде. В проекте payment-service может возвращать success, failure, timeout или random. Это позволяет проверять сценарии, которые сложно стабильно получить от реального провайдера платежей.

Альтернативный ответ:  
Тестовый double или sandbox dependency с управляемыми режимами.

### Вопрос: Чем payment decline отличается от timeout?

Основной ответ:  
Decline - бизнес-ответ: платеж обработан и отклонен. Timeout - техническая проблема: сервис не ответил вовремя. Для QA это разные классы риска и разные ожидаемые реакции системы.

Альтернативный ответ:  
Decline - ожидаемый бизнес-сценарий, timeout - отказ инфраструктуры или зависимости.

### Вопрос: Что такое resilience?

Основной ответ:  
Resilience - способность системы сохранять контролируемое поведение при сбоях зависимостей: timeout, retry, fallback, circuit breaker, корректный статус заказа, понятная ошибка и отсутствие полного падения.

Альтернативный ответ:  
Устойчивость системы к частичным отказам.

## Критерий завершения урока

Ты можешь смоделировать payment decline/timeout/service stop, показать эффект в UI, логах и Grafana, и объяснить expected behavior.
