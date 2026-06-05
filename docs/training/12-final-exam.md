# Урок 12. Итоговый экзамен

## Цель урока

Проверить, что ты можешь самостоятельно пройти весь проект как сильный ручной QA: от пользовательского сценария до внутренней диагностики и собеседовательного объяснения.

## Компетенции после урока

После финального экзамена ты должен уметь:

- самостоятельно поднимать весь стенд и проверять его готовность;
- проходить полный пользовательский путь интернет-магазина от каталога до заказа;
- связывать действия в UI с API, сервисами, базами, Redis, RabbitMQ и observability;
- проверять позитивные, негативные и деградационные сценарии без автоматизации;
- локализовать дефект по evidence, а не по догадке;
- пользоваться fault flags для controlled failure scenarios;
- формулировать impact для пользователя и для бизнеса;
- описывать expected behavior, actual behavior, severity, priority и suspected component;
- готовить тестовую документацию уровня middle/middle+ QA;
- уверенно рассказывать проект на собеседовании в технических терминах.

## Перед экзаменом: что должно сложиться в голове

Итоговый экзамен проверяет не память команд, а цельное понимание системы. Ты должен уметь пройти путь от пользовательского действия до внутренних последствий и обратно.

Если коротко, ты должен видеть систему так:

```text
Пользователь
  -> Customer Store
  -> nginx gateway
  -> API конкретного сервиса
  -> база или dependency
  -> side effects
  -> logs/metrics/evidence
```

### Карта сервисов, которую нужно уметь объяснить

| Компонент | Роль в системе | Что проверяет QA |
| --- | --- | --- |
| `nginx` | Отдает UI и проксирует `/api/*` в сервисы. | Роутинг, gateway errors, доступность UI/API. |
| `user-service` | Владеет пользователями и статусами. | Создание, validation, unique email, `active/blocked/deleted`. |
| `product-service` | Владеет каталогом и stock. | Товары, цена, статус, stock, Redis cache. |
| `order-service` | Оркестрирует checkout. | Интеграционный flow, сумма, статусы заказа, side effects. |
| `payment-service` | Имитирует платежный dependency. | Success, decline, timeout, resilience. |
| `notification-service` | Создает уведомления по событиям. | RabbitMQ consumer, eventual consistency, idempotency. |
| PostgreSQL DBs | Хранят данные конкретных сервисов. | Целостность данных и readiness сервисов. |
| Redis | Кеширует товары. | `HIT/MISS`, stale data, invalidation. |
| RabbitMQ | Передает события между сервисами. | Queue, exchange, consumer, ack, потеря/дубли событий. |
| Prometheus | Собирает метрики. | Error rate, request rate, latency, targets. |
| Grafana | Показывает dashboards. | Визуальное подтверждение деградации и восстановления. |

### Главная цепочка checkout

На экзамене ты должен без подсказок объяснить:

```text
1. Пользователь выбирает товар в Customer Store.
2. UI отправляет POST /api/orders.
3. nginx проксирует запрос в order-service.
4. order-service запрашивает user-service.
5. order-service запрашивает product-service.
6. order-service вызывает payment-service.
7. order-service сохраняет заказ.
8. order-service публикует событие в RabbitMQ.
9. notification-service читает событие.
10. Пользователь видит заказ и уведомление.
```

Важно понимать, где синхронная часть, а где асинхронная. Ответ `POST /api/orders` не всегда означает, что notification уже создана.

### Как думать при дефекте

Используй не угадывание, а диагностическую цепочку:

```text
1. Что увидел пользователь?
2. Какой API был вызван?
3. Какой status code и response body вернулись?
4. Есть ли X-Request-ID?
5. Через gateway проблема повторяется?
6. Напрямую в сервис проблема повторяется?
7. /ready сервиса зеленый?
8. Есть ли ошибки в логах?
9. Какая dependency участвует: DB, Redis, RabbitMQ, payment?
10. Что показывают Grafana/Prometheus?
11. Какой suspected component подтвержден evidence-ом?
12. Как вернуть baseline?
```

Если ты проходишь эту цепочку спокойно и последовательно, ты демонстрируешь уровень, близкий к работе на реальном проекте.

### Как отвечать на экзамене и собеседовании

Каждый ответ строится по схеме:

```text
Контекст -> Действие -> Evidence -> Вывод -> Impact
```

Пример:

```text
Контекст: Я проверял checkout при payment timeout.
Действие: Переключил payment mode в timeout и отправил POST /api/orders.
Evidence: API вернул 504, в логах order-service по request id видно payment timed out, в Grafana выросла latency/error rate.
Вывод: проблема локализуется в payment dependency handling.
Impact: пользователь не может завершить покупку, система должна показать понятную ошибку и не создавать дубли.
```

### Минимальный уровень для зачета

Перед экзаменом ты должен уметь:

- поднять и остановить стенд;
- отличить `Running` от `Healthy`;
- объяснить nginx и gateway;
- пройти UI flow магазина;
- проверить API через gateway;
- проверить сервис напрямую;
- прочитать Swagger;
- объяснить основные status codes;
- проверить Redis cache;
- открыть RabbitMQ и найти очередь;
- открыть Grafana и Prometheus;
- включить fault flag и вернуть baseline;
- оформить баг с evidence;
- рассказать проект без чтения с листа.

## Условия

- Не пользоваться pytest как основным способом проверки.
- Можно использовать UI, API, Docker, RabbitMQ, Grafana, Prometheus, логи и fault flags.
- Все выводы подтверждать evidence.

## Часть 1. Запуск

1. Подними стенд:

```powershell
docker compose up -d --build
```

2. Проверь:

```powershell
docker compose ps
py -3 scripts\fault_lab.py smoke
```

3. Открой:

```text
http://localhost:8080/store.html
http://localhost:8080
http://localhost:3000
http://localhost:15672
```

Критерий: ты можешь объяснить, что означает каждый URL.

## Часть 2. Пользовательский flow

1. Открой Customer Store.
2. Seed demo catalog.
3. Создай account.
4. Добавь товары в cart.
5. Checkout.
6. Проверь orders.
7. Проверь notifications.

Критерий: заказ создан, статус понятен, events найдены.

## Часть 3. API и контракт

Проверь:

- duplicate email -> `409`;
- bad email -> `422`;
- product cache -> `MISS/HIT`;
- unknown user in order -> business error;
- payment failure -> `payment_failed`;
- payment timeout -> controlled handling.

Критерий: ты можешь объяснить каждый status code.

## Часть 4. RabbitMQ

1. Останови notification-service:

```powershell
py -3 scripts\fault_lab.py enable notification-service-stop
```

2. Создай заказ.
3. Посмотри RabbitMQ queue.
4. Восстанови:

```powershell
py -3 scripts\fault_lab.py disable notification-service-stop
```

5. Проверь, что события обработались.

Критерий: ты можешь объяснить eventual consistency.

## Часть 5. Observability

1. Создай несколько заказов.
2. Открой Grafana.
3. Найди request rate.
4. Включи timeout.
5. Найди рост latency.
6. Найди логи по order-service.

Критерий: ты можешь связать действие в UI с метриками и логами.

## Часть 6. Fault injection

Пройди 5 fault flags:

```text
payment-timeout
payment-service-stop
redis-stop
rabbitmq-stop
gateway-stop
```

Для каждого заполни:

```text
Flag:
Symptom:
User impact:
Broken component:
Evidence:
Restore command:
Production fix:
```

## Часть 7. Документация

Подготовь:

- test plan;
- checklist;
- 10 test cases;
- 3 bug reports;
- test summary;
- 5 STAR stories.

## Финальные вопросы

Ответь вслух:

1. Как устроена система?
2. Что происходит при checkout?
3. Где используется Redis?
4. Где используется RabbitMQ?
5. Что такое eventual consistency?
6. Как ты проверяешь payment timeout?
7. Как ты локализуешь дефект?
8. Что показывает Grafana?
9. Чем `health` отличается от `ready`?
10. Какой production fix ты предложишь для зависшего сервиса?

## Как отвечать на финальные вопросы

### Вопрос: Как устроена система?

Основной ответ:  
Это микросервисный e-commerce стенд. Пользователь работает через `Customer Store`, тестировщик может управлять системой через `QA Dashboard`, внешний вход идет через `nginx` gateway. За пользователей отвечает `user-service`, за каталог и Redis cache - `product-service`, за оформление заказа - `order-service`, за платежи - `payment-service`, за события и письма - `notification-service` через RabbitMQ. Данные сервисов лежат в отдельных PostgreSQL базах. Метрики собирает Prometheus, визуализирует Grafana.

Альтернативный ответ:  
Это учебный интернет-магазин, где можно проверить весь путь от UI до инфраструктуры: gateway, API, сервисы, базы, кеш, очередь, логи и метрики.

### Вопрос: Что происходит при checkout?

Основной ответ:  
UI отправляет `POST /api/orders`. Gateway проксирует запрос в `order-service`. `order-service` проверяет пользователя в `user-service`, товары и остатки в `product-service`, вызывает `payment-service`, сохраняет заказ в своей БД и публикует событие в RabbitMQ. `notification-service` читает событие и создает notification.

Альтернативный ответ:  
Checkout - это интеграционный flow: один пользовательский клик проходит через несколько сервисов, синхронные API-вызовы и асинхронное событие.

### Вопрос: Где используется Redis?

Основной ответ:  
Redis используется в `product-service` для кеширования чтения товаров. Это проверяется через заголовок `X-Cache`: первый запрос обычно дает `MISS`, повторный - `HIT`.

Альтернативный ответ:  
Redis ускоряет чтение каталога и дает тестировщику отдельный класс проверок: cache hit, cache miss, invalidation и поведение при отказе кеша.

### Вопрос: Где используется RabbitMQ?

Основной ответ:  
RabbitMQ используется между `order-service` и `notification-service`. После создания заказа `order-service` публикует событие, а `notification-service` асинхронно его обрабатывает и сохраняет notification.

Альтернативный ответ:  
RabbitMQ нужен для eventual consistency: заказ может быть создан раньше, чем уведомление появится.

### Вопрос: Что такое eventual consistency?

Основной ответ:  
Это модель, при которой разные части системы становятся согласованными не мгновенно, а через некоторое время. В проекте заказ создается сразу, а notification появляется после обработки события RabbitMQ.

Альтернативный ответ:  
Это нормальная задержка асинхронной системы, если она укладывается в ожидаемый SLA и событие не потеряно.

### Вопрос: Как ты проверяешь payment timeout?

Основной ответ:  
Я включаю controlled failure через payment mode `timeout` или fault flag `payment-timeout`, создаю заказ, фиксирую симптом в UI/API, смотрю статус заказа, latency в Grafana и логи `order-service`/`payment-service`. После проверки восстанавливаю стенд и запускаю smoke.

Альтернативный ответ:  
Проверяю не только факт timeout, но и то, что система возвращает контролируемый результат, не зависает бесконечно и остается диагностируемой.

### Вопрос: Как ты локализуешь дефект?

Основной ответ:  
Иду от пользовательского симптома к технической цепочке: UI, Network/API response, gateway, readiness, логи нужного сервиса, состояние БД/Redis/RabbitMQ, метрики Grafana. Гипотезу подтверждаю evidence: статусом, логом, request id, метрикой или состоянием очереди.

Альтернативный ответ:  
Я не начинаю с перезапуска. Сначала сужаю область отказа и доказываю, какой компонент сломан.

### Вопрос: Что показывает Grafana?

Основной ответ:  
Grafana показывает метрики из Prometheus: request rate, статусы ответов, latency, ошибки, состояние сервисов. Для QA это способ увидеть, как пользовательские действия или fault flags влияют на систему.

Альтернативный ответ:  
Grafana помогает перейти от единичного бага к системному наблюдению: растет ли latency, есть ли всплеск 5xx, какой сервис деградирует.

### Вопрос: Чем `health` отличается от `ready`?

Основной ответ:  
`health` обычно отвечает на вопрос, жив ли процесс. `ready` отвечает, готов ли сервис принимать рабочие запросы, включая зависимости: БД, Redis, RabbitMQ или другие критичные компоненты.

Альтернативный ответ:  
`health` - сервис запущен, `ready` - сервис реально готов к работе.

### Вопрос: Какой production fix ты предложишь для зависшего сервиса?

Основной ответ:  
Сначала нужен recovery: вывести сервис из зависания, восстановить трафик, проверить smoke. Затем root cause: посмотреть логи, метрики, thread/blocking symptoms, dependency timeouts, connection pools, memory/CPU. Production fix может включать timeout, retry policy, circuit breaker, health/readiness tuning, лимиты ресурсов, алерты и исправление конкретного дефекта в коде.

Альтернативный ответ:  
Перезапуск - это восстановление, но не полноценный fix. Fix должен устранять причину и снижать вероятность повторения.

## Оценка

Сильный уровень:

- Ты сам поднимаешь стенд.
- Ты сам проходишь customer journey.
- Ты сам находишь, где смотреть evidence.
- Ты умеешь сломать и восстановить систему.
- Ты можешь объяснить каждый сервис.
- Ты можешь отвечать на вопросы без чтения шпаргалки.
- Ты можешь оформить результаты как тестировщик.

Средний уровень:

- Ты проходишь сценарии, но пока путаешь сервисы или evidence.

Начальный уровень:

- Ты нажимаешь кнопки, но не можешь объяснить, что происходит внутри.

## Критерий завершения курса

Курс завершен, когда ты можешь за 20-30 минут показать проект другому человеку: пройти магазин, открыть QA Dashboard, сломать payment timeout, найти проблему в логах/Grafana, восстановить стенд и объяснить архитектуру.
