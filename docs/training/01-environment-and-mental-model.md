# Урок 01. Окружение и ментальная модель системы

## Цель урока

Научиться запускать весь стенд, понимать состав сервисов и объяснять архитектуру проекта простым техническим языком.

## Компетенции после урока

После урока ты должен уметь:

- запускать и останавливать весь проект через Docker Compose;
- проверять состояние контейнеров;
- отличать `Running` от `Healthy`;
- объяснять назначение каждого сервиса;
- понимать, что такое gateway, service-owned database, Redis, RabbitMQ, Prometheus и Grafana;
- объяснять, почему QA должен уметь смотреть не только UI, но и инфраструктурное состояние.

## Что сделать

1. Открой PowerShell.

2. Перейди в проект:

```powershell
cd C:\microservices-qa-lab
```

3. Подними все сервисы:

```powershell
docker compose up -d --build
```

4. Проверь контейнеры:

```powershell
docker compose ps
```

5. Запусти smoke:

```powershell
py -3 scripts\fault_lab.py smoke
```

6. Открой основные инструменты:

```text
Customer Store: http://localhost:8080/store.html
QA Dashboard:   http://localhost:8080
Grafana:        http://localhost:3000 admin / admin
Prometheus:     http://localhost:9090
RabbitMQ:       http://localhost:15672 guest / guest
```

## Куда смотреть и почему

`docker compose ps`: показывает, какие контейнеры подняты и какие прошли healthcheck. Если контейнер `Running`, это значит процесс жив. Если `Healthy`, значит healthcheck сервиса прошел.

`fault_lab.py smoke`: проверяет пользовательски важные readiness endpoints. Это ближе к QA-проверке, чем просто `docker compose ps`.

`QA Dashboard`: нужен тестировщику для ручного управления системой: создать пользователя, продукт, заказ, переключить payment mode, посмотреть notifications.

`Customer Store`: нужен, чтобы почувствовать систему как реальный пользователь: витрина, корзина, аккаунт, checkout, история заказов.

`Grafana/Prometheus`: нужны для диагностики поведения после действий: выросла ли latency, есть ли ошибки, живы ли scrape targets.

`RabbitMQ`: нужен для проверки асинхронной части: сообщения, очереди, consumer, события заказа.

## Что записать в рабочий журнал

```text
Дата:
Команда запуска:
Сколько контейнеров поднялось:
Какие сервисы Healthy:
Smoke result:
Какие web tools открылись:
Проблемы при запуске:
Как решал:
```

## Типовые ошибки новичка

- Смотреть только UI и не проверять `docker compose ps`.
- Путать `Running` и `Healthy`.
- Не понимать, что `nginx` - это gateway, а не backend-сервис.
- Думать, что если магазин открылся, то вся система полностью исправна.
- Не сохранять evidence при проблеме.

## Вопросы на собеседовании

### Вопрос: Как ты запускал проект?

Основной ответ:  
Я запускал весь стенд через Docker Compose командой `docker compose up -d --build`. После запуска проверял `docker compose ps`, затем запускал smoke через `py -3 scripts\fault_lab.py smoke`, чтобы убедиться, что gateway, users, products, orders, payments, notifications, Prometheus и Grafana отвечают.

Альтернативный короткий ответ:  
Через Docker Compose. Проверял не только факт запуска контейнеров, но и readiness endpoints.

### Вопрос: Чем `Running` отличается от `Healthy`?

Основной ответ:  
`Running` означает, что процесс контейнера запущен. `Healthy` означает, что прошел healthcheck, например сервис ответил на `/ready`, PostgreSQL прошел `pg_isready`, Redis ответил на `PING`. Сервис может быть `Running`, но еще не готов обрабатывать рабочие запросы.

Альтернативный ответ:  
`Running` - состояние контейнера, `Healthy` - состояние приложения внутри контейнера.

### Вопрос: Какие сервисы есть в проекте?

Основной ответ:  
Есть `user-service`, `product-service`, `order-service`, `payment-service`, `notification-service`, `nginx` gateway, PostgreSQL базы для сервисов, Redis, RabbitMQ, Prometheus и Grafana.

Альтернативный ответ:  
Это микросервисный магазин: отдельные сервисы для пользователей, товаров, заказов, платежей и уведомлений плюс инфраструктура для кеша, очередей и наблюдаемости.

## Критерий завершения урока

Ты можешь с нуля поднять проект, открыть все web-инструменты, объяснить назначение каждого сервиса и показать smoke result.
