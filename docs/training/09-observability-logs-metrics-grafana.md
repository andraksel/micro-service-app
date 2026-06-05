# Урок 09. Observability: логи, метрики, Grafana и Prometheus

## Цель урока

Научиться использовать observability как инструмент QA: смотреть логи, request ID, метрики, latency, error rate и состояние targets.

## Компетенции после урока

После урока ты должен уметь:

- использовать `X-Request-ID` для расследования;
- читать JSON-логи сервисов;
- пользоваться Prometheus queries;
- читать Grafana dashboard;
- понимать request rate, error rate, p95 latency;
- отличать функциональный дефект от деградации.

## Что сделать

1. Открой Grafana:

```text
http://localhost:3000
admin / admin
```

2. Найди dashboard:

```text
Microservices QA Lab Overview
```

3. Открой Prometheus:

```text
http://localhost:9090
```

4. Выполни query:

```promql
sum by (service) (rate(http_requests_total[1m]))
```

5. Выполни:

```promql
histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))
```

6. В QA Dashboard создай заказ.

7. Снова посмотри Grafana.

8. Включи payment timeout:

```powershell
py -3 scripts\fault_lab.py enable payment-timeout
```

9. Создай заказ.

10. Посмотри p95 latency.

11. Верни состояние:

```powershell
py -3 scripts\fault_lab.py disable payment-timeout
```

## Логи

Смотреть order-service:

```powershell
docker compose logs --tail=100 order-service
```

Смотреть payment-service:

```powershell
docker compose logs --tail=100 payment-service
```

Смотреть product-service:

```powershell
docker compose logs --tail=100 product-service
```

## Что искать в логах

```text
timestamp
level
service
message
request_id
method
path
status_code
duration_ms
event
error
dependency
```

## PromQL queries

Request rate:

```promql
sum by (service) (rate(http_requests_total[1m]))
```

Status codes:

```promql
sum by (service, status_code) (rate(http_requests_total[1m]))
```

P95 latency:

```promql
histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))
```

5xx errors:

```promql
sum(increase(http_requests_total{status_code=~"5.."}[5m]))
```

Targets:

```promql
up{job=~".*-service"}
```

## Вопросы на собеседовании

### Вопрос: Что такое observability?

Основной ответ:  
Observability - способность понимать внутреннее состояние системы по внешним сигналам: logs, metrics, traces. В этом проекте есть JSON-логи, Prometheus metrics и Grafana dashboards.

Альтернативный ответ:  
Это возможность расследовать поведение системы без прямого доступа к коду во время инцидента.

### Вопрос: Зачем QA смотреть Grafana?

Основной ответ:  
Потому что UI может формально работать, но система уже деградирует: растет latency, появляются 5xx, падают targets, увеличивается error rate. QA может увидеть проблему раньше, чем она станет явной для пользователя.

Альтернативный ответ:  
Метрики помогают увидеть не только факт ошибки, но и масштаб влияния.

### Вопрос: Что такое p95 latency?

Основной ответ:  
Это значение, быстрее которого уложились 95% запросов. Если p95 растет, значит значимая часть пользователей начинает ждать дольше.

Альтернативный ответ:  
Это показатель хвостовой задержки, полезный для оценки качества сервиса.

### Вопрос: Зачем нужен `X-Request-ID`?

Основной ответ:  
Он связывает логи разных сервисов в один пользовательский запрос. По request ID можно пройти цепочку gateway -> order-service -> dependencies.

Альтернативный ответ:  
Это correlation ID для расследования.

## Критерий завершения урока

Ты можешь создать запрос, найти его в логах, увидеть эффект в Grafana и объяснить метрики.
