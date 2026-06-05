# Урок 10. Fault injection и локализация дефектов

## Цель урока

Научиться намеренно ломать систему фича-флагами, воспроизводить production-like симптомы, локализовать компонент и возвращать стенд в baseline.

## Компетенции после урока

После урока ты должен уметь:

- использовать `scripts/fault_lab.py`;
- включать и выключать fault flags;
- отличать проблему gateway, сервиса, БД, Redis, RabbitMQ и observability;
- собирать evidence;
- писать runbook локализации;
- объяснять production-grade fix.

## Перед практикой: что нужно понять

Fault injection - это намеренное внесение неисправностей в систему, чтобы проверить диагностику, устойчивость и восстановление.

В реальном production проблемы возникают сами: база недоступна, очередь забилась, сервис завис, кеш устарел, gateway route сломан. В учебном проекте ты создаешь такие ситуации управляемо через `scripts/fault_lab.py`.

### Зачем тестировщику ломать приложение

Цель не в том, чтобы "сломать ради слома". Цель - научиться видеть систему как инженер:

- какой симптом увидит пользователь;
- какой API status code появится;
- какой сервис является suspected component;
- какие зависимости затронуты;
- как собрать evidence;
- как вернуть baseline;
- какой production fix предложить.

Такой навык отличает ручного QA, который просто кликает UI, от QA, который помогает команде быстро находить причину инцидента.

### Что такое symptom и root cause

Symptom - то, что видно снаружи.

Пример:

```text
Checkout возвращает 504.
```

Root cause - реальная причина.

Пример:

```text
payment-service работает в режиме timeout.
```

Один симптом может иметь разные причины:

```text
UI не создает заказ
  -> order-service упал
  -> payment-service timeout
  -> user-service возвращает blocked user
  -> product-service не отвечает
  -> nginx route сломан
  -> RabbitMQ недоступен и order-service не ready
```

Задача QA - не угадать, а сузить пространство причин evidence-ом.

### Что такое baseline

Baseline - полностью рабочее состояние стенда.

В этом проекте baseline означает:

- все контейнеры подняты;
- `/ready` основных сервисов возвращает успех;
- payment mode = `success`;
- fault flags выключены;
- smoke проходит;
- UI открывается;
- можно создать пользователя, товар, заказ и уведомление.

Перед любым fault injection нужно понимать, как вернуть baseline. Иначе ты не сможешь отличить новую поломку от старого мусора в окружении.

### Что такое blast radius

Blast radius - зона влияния поломки.

Примеры:

| Поломка | Blast radius |
| --- | --- |
| `user-db` недоступна | Создание пользователей, checkout для проверки пользователя, `/api/users/ready`. |
| Redis недоступен | Кеш товаров, `/api/products/ready`, скорость/поведение чтения товара. |
| RabbitMQ недоступен | Готовность order/notification flow, уведомления, async часть. |
| `payment-service` timeout | Checkout и статус заказа, но каталог и аккаунты могут работать. |
| nginx route сломан | UI/API через gateway падают, прямой порт сервиса может работать. |

Хороший баг-репорт описывает blast radius. Это помогает команде понять приоритет.

### Локализация по слоям

Диагностику удобно вести сверху вниз:

```text
1. UI symptom
2. Network/API response
3. Gateway route
4. Target service /ready
5. Logs target service
6. Dependency: DB, Redis, RabbitMQ, payment
7. Metrics/Grafana
8. Recovery/reset
```

Если UI падает, не начинай сразу с базы. Сначала проверь API. Если API через gateway падает, проверь прямой порт сервиса. Если прямой порт работает, смотри nginx. Если прямой порт не работает, смотри сервис и его dependencies.

### Recovery vs fix

Recovery - вернуть систему в рабочее состояние.

Пример:

```text
Перезапустить контейнер.
Сбросить fault flag.
Вернуть payment mode success.
```

Fix - устранить причину, чтобы проблема не повторялась.

Пример:

```text
Добавить timeout handling.
Исправить route в nginx.
Добавить retry/backoff.
Добавить readiness check.
Исправить cache invalidation.
```

На собеседовании важно разделять эти понятия. Restart может восстановить сервис, но не всегда является исправлением дефекта.

### Что должен проговаривать QA

Перед включением fault flag проговаривай:

```text
Что именно ломает этот флаг?
Какой пользовательский симптом я ожидаю?
Какой service/dependency должен измениться?
Какие проверки докажут root cause?
Какой blast radius?
Как вернуть baseline?
Что было бы production-grade fix?
```

## Что сделать

Посмотреть все флаги:

```powershell
py -3 scripts\fault_lab.py list
```

Посмотреть описание:

```powershell
py -3 scripts\fault_lab.py show payment-timeout
```

Включить поломку:

```powershell
py -3 scripts\fault_lab.py enable payment-timeout
```

Проверить симптом:

1. Создай заказ.
2. Посмотри статус.
3. Посмотри latency в Grafana.
4. Посмотри логи order-service.

Выключить:

```powershell
py -3 scripts\fault_lab.py disable payment-timeout
py -3 scripts\fault_lab.py smoke
```

Если система в непонятном состоянии:

```powershell
py -3 scripts\fault_lab.py restore-all
```

## Обязательные сценарии

Пройди минимум эти fault flags:

```text
payment-timeout
payment-service-stop
redis-stop
rabbitmq-stop
notification-service-stop
gateway-stop
prometheus-stop
```

## Как локализовать

1. Что видит пользователь?
2. Какой endpoint отвечает ошибкой?
3. Что показывает `docker compose ps`?
4. Что показывает smoke?
5. Есть ли ошибка в логах gateway?
6. Есть ли ошибка в логах сервиса-оркестратора?
7. Жива ли dependency?
8. Есть ли события в RabbitMQ?
9. Есть ли деградация в Grafana?
10. Какой минимальный restore нужен?

## Таблица локализации

| Симптом | Вероятная зона |
| --- | --- |
| UI не открывается | nginx/gateway/static UI. |
| `/api/users/ready` падает | user-service или user-db. |
| Catalog пустой | product-service/product-db/data. |
| Cache не HIT | Redis/cache invalidation. |
| Checkout медленный | payment timeout/order dependency. |
| Нет notification | RabbitMQ или notification-service. |
| Grafana пустая | Prometheus/Grafana/datasource. |

## Вопросы на собеседовании

### Вопрос: Что такое fault injection?

Основной ответ:  
Это намеренное внесение контролируемых отказов в систему, чтобы проверить поведение при production-like проблемах: падение сервиса, timeout, сетевой разрыв, отказ БД, потеря очереди.

Альтернативный ответ:  
Это способ тренировать resilience и runbook диагностику.

### Вопрос: Как ты локализуешь проблему в микросервисах?

Основной ответ:  
Иду от пользовательского симптома к технической цепочке: UI, gateway response, service readiness, logs, dependency state, RabbitMQ/Redis, metrics. Использую request ID и проверяю каждый сервис по flow.

Альтернативный ответ:  
Не угадываю, а сужаю область по evidence.

### Вопрос: Почему просто restart - не полноценный фикс?

Основной ответ:  
Restart может временно восстановить сервис, но не устраняет root cause. В реальном проекте нужно понять причину: memory leak, deadlock, bad deployment, network issue, DB pool exhaustion, timeout config.

Альтернативный ответ:  
Restart - recovery action, но не root-cause fix.

## Критерий завершения урока

Ты можешь включить fault flag, воспроизвести симптом, доказать причину evidence-ом, восстановить стенд и объяснить production fix.
