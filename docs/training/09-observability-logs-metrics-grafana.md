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

## Перед практикой: что нужно понять

Observability - это способность понять внутреннее состояние системы по внешним сигналам: логам, метрикам, traces/request id и health checks.

Для QA observability превращает "у меня не работает" в технически полезное расследование: где сломалось, когда, с каким запросом, как часто и насколько сильно влияет на пользователя.

### Логи, метрики и dashboards - это разные инструменты

| Инструмент | Что показывает | Когда использовать |
| --- | --- | --- |
| Logs | Конкретные события и ошибки. | Нужно расследовать один запрос или один дефект. |
| Metrics | Числа во времени: rate, latency, errors. | Нужно понять масштаб и деградацию. |
| Grafana | Визуальные панели по метрикам. | Нужно быстро увидеть состояние системы. |
| Prometheus | Хранилище метрик и язык запросов PromQL. | Нужно точно запросить метрику. |
| Health/ready | Готовность сервиса к работе. | Нужно понять, можно ли слать трафик. |

QA должен уметь использовать все эти уровни. Логи отвечают "что случилось с этим запросом". Метрики отвечают "это единичный случай или массовая проблема".

### Что такое X-Request-ID

`X-Request-ID` - это идентификатор запроса. Он помогает связать действия пользователя с логами сервисов.

Пример расследования:

```text
UI получил 504 при checkout.
QA берет X-Request-ID из ответа или логов gateway.
Ищет этот id в логах order-service.
Видит timeout при вызове payment-service.
Проверяет payment-service logs и metrics.
Формулирует suspected component: payment-service/dependency timeout.
```

Без request id расследование превращается в угадывание, особенно если стендом пользуются несколько человек.

### Что такое request rate, error rate и latency

Request rate - сколько запросов приходит в сервис за единицу времени. Если rate резко вырос, сервис может быть под нагрузкой или UI может делать лишние запросы.

Error rate - доля или количество ошибочных ответов. Если после включения fault flag выросли `5xx`, это подтверждает влияние поломки.

Latency - время ответа. Важны не только средние значения, но и хвосты.

`p95 latency` означает:

```text
95% запросов быстрее этого значения,
5% запросов медленнее.
```

Если средняя latency нормальная, но p95 высокий, часть пользователей все равно страдает.

### Что такое Prometheus

Prometheus собирает метрики с сервисов. Он периодически ходит на `/metrics` и сохраняет значения.

В проекте сервисы отдают метрики по gateway:

```text
/api/users/metrics
/api/products/metrics
/api/orders/metrics
/api/payments/metrics
/api/notifications/metrics
```

Prometheus удобен для точных вопросов:

```text
Сколько запросов было в order-service?
Сколько из них вернули 5xx?
Какая latency у payment-service?
Все ли targets доступны?
```

### Что такое Grafana

Grafana показывает dashboards поверх метрик. Ее задача - дать быстрый обзор состояния системы.

QA смотрит Grafana не "для красоты", а чтобы:

- подтвердить деградацию;
- увидеть, какой сервис начал ошибаться;
- сравнить поведение до и после fault flag;
- приложить скриншот как evidence;
- понять, восстановилась ли система после reset.

### Функциональный дефект vs деградация

Функциональный дефект:

```text
При валидном заказе система возвращает неправильный статус.
```

Деградация:

```text
Заказы иногда создаются, но checkout стал отвечать по 8 секунд.
```

Оба сценария важны. Деградация может быть даже опаснее, потому что система "как будто работает", но пользовательский опыт и конверсия падают.

### Что должен проговаривать QA

Перед расследованием проговаривай:

```text
Я ищу конкретный дефект или системную деградацию?
Какой request id связан с проблемой?
В каком сервисе выросли ошибки?
Выросла ли latency?
Что показывает Grafana?
Что показывает Prometheus?
Какие логи подтверждают suspected component?
```

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
