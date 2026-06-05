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

## Перед практикой: что нужно понять

`payment-service` в этом проекте имитирует внешний платежный dependency. В реальном магазине это мог бы быть банк, платежный шлюз, антифрод или сторонний провайдер.

Для QA платежи важны потому, что они напрямую связаны с деньгами, статусом заказа и доверием пользователя.

### Что такое controlled dependency

Controlled dependency - это зависимость, поведение которой можно управляемо менять в тестовой среде.

В проекте payment mode можно переключать:

| Mode | Что имитирует | Ожидаемое поведение заказа |
| --- | --- | --- |
| `success` | Платеж авторизован. | Заказ становится `paid`. |
| `failure` | Платеж отклонен бизнесом. | Заказ становится `payment_failed`. |
| `timeout` | Платежный сервис долго не отвечает. | Клиент получает timeout/error, система не должна зависать навсегда. |
| `random` | Нестабильное поведение. | Нужно проверять устойчивость и диагностируемость. |
| stop/pause контейнера | Техническая недоступность сервиса. | Ошибка должна быть понятной и локализуемой. |

Это полезно для обучения, потому что в реальном проекте QA не должен ждать, пока банк "случайно сломается". Он должен уметь воспроизводить сценарий контролируемо.

### Business failure vs technical failure

Business failure - это штатный отказ по бизнес-причине.

Пример:

```text
Карта отклонена.
Платежный провайдер ответил declined.
Заказ должен стать payment_failed.
Система работает корректно.
```

Technical failure - это проблема инфраструктуры или связи.

Пример:

```text
payment-service не отвечает.
Запрос превысил timeout.
Сервис недоступен.
Сеть или контейнер сломан.
```

Эти сценарии нельзя смешивать. Если банк отклонил платеж, пользователю можно показать "платеж отклонен". Если платежный сервис недоступен, пользователь должен получить другой смысл: "платеж временно недоступен, попробуйте позже".

### Что такое timeout

Timeout - это ситуация, когда сервис не получил ответ за допустимое время.

Timeout опасен тем, что он создает неопределенность:

```text
Пользователь нажал checkout.
order-service отправил запрос в payment-service.
payment-service слишком долго не отвечает.
order-service должен решить, сколько ждать и что вернуть клиенту.
```

Плохое поведение:

- UI бесконечно крутит spinner;
- заказ зависает в промежуточном статусе без объяснения;
- создаются дубли заказов при повторном клике;
- backend возвращает `500` без понятной причины;
- в логах нет `X-Request-ID`, по которому можно найти цепочку.

### Что такое resilience

Resilience - это способность системы переживать сбои зависимостей без полного развала.

Для QA это не абстрактное слово. В проверках resilience ты смотришь:

- есть ли timeout, а не бесконечное ожидание;
- возвращается ли корректный status code;
- не создаются ли дубли;
- сохраняется ли понятный статус заказа;
- есть ли логи и метрики для диагностики;
- восстанавливается ли система после возврата payment-service в `success`.

### Как payment влияет на order-service

`order-service` вызывает `payment-service` во время checkout.

Логика ожидается такая:

```text
payment authorized -> order.status = paid
payment declined   -> order.status = payment_failed
payment timeout    -> ошибка должна быть обработана и объяснима
payment unavailable -> dependency error, а не случайный успех
```

Если payment-service сломан, `user-service` и `product-service` могут быть полностью здоровы. Поэтому QA должен локализовать именно платежную часть, а не писать "checkout не работает" без анализа.

### Что должен проговаривать QA

Перед проверкой платежей проговаривай:

```text
Я моделирую бизнес-отказ или технический отказ?
Какой payment mode включен?
Какой статус заказа ожидается?
Какой status code ожидается от API?
Что увидит пользователь?
Где в логах и Grafana я подтвержу проблему?
Как вернуть систему в baseline?
```

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
