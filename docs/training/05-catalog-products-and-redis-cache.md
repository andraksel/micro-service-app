# Урок 05. Каталог, товары, stock и Redis cache

## Цель урока

Научиться тестировать каталог товаров, остатки, фильтры, кеширование и инвалидацию кеша.

## Компетенции после урока

После урока ты должен уметь:

- проверять товарный каталог через UI и API;
- тестировать цену, stock, status и описание продукта;
- понимать `X-Cache: MISS` и `X-Cache: HIT`;
- объяснять, как Redis влияет на поведение чтения;
- проверять cache invalidation после изменения продукта;
- описывать риски кеширования на собеседовании.

## Что сделать

Через Customer Store:

1. Открой `http://localhost:8080/store.html`.
2. Нажми `Seed demo catalog`.
3. Проверь карточки товаров.
4. Проверь поиск.
5. Проверь фильтр category.
6. Проверь сортировку price asc/desc.
7. Добавь товар в корзину.

Через QA Dashboard:

1. Создай отдельный продукт.
2. Нажми `Check cache`.
3. Убедись:

```text
first MISS
second HIT
```

Через API:

```powershell
Invoke-WebRequest -Uri http://localhost:8080/api/products/PRODUCT_ID -UseBasicParsing
Invoke-WebRequest -Uri http://localhost:8080/api/products/PRODUCT_ID -UseBasicParsing
```

Смотри header:

```text
X-Cache
```

## Куда смотреть и почему

Customer Store показывает бизнес-сторону: товар виден пользователю, его можно добавить в корзину.

QA Dashboard показывает technical evidence: `X-Cache`, raw product JSON.

Redis напрямую можно проверить так:

```powershell
docker compose exec redis redis-cli KEYS "*"
```

Product-service logs:

```powershell
docker compose logs --tail=100 product-service
```

Ищи события:

```text
product_cache_hit
product_cache_miss
product_created
product_updated
```

## Cache testing

Проверка cache miss:

1. Создать новый продукт.
2. Первый раз запросить по ID.
3. Ожидать `X-Cache: MISS`.

Проверка cache hit:

1. Повторить GET по тому же ID.
2. Ожидать `X-Cache: HIT`.

Проверка invalidation:

1. Получить продукт дважды, чтобы был `HIT`.
2. Изменить продукт через `PATCH /api/products/{id}`.
3. Получить продукт снова.
4. Ожидать `MISS`, потому что старый кеш должен быть сброшен.

## Риски кеширования

- Пользователь может увидеть устаревшие данные.
- Баг может воспроизводиться только после первого запроса.
- Кеш может скрывать проблемы БД.
- Неверная invalidation приводит к старым ценам или stock.
- Cold cache может перегрузить БД после рестарта Redis.

## Практическое задание

Смоделируй потерю кеша:

```powershell
py -3 scripts\fault_lab.py enable redis-cache-flush
```

Потом снова проверь товар:

```text
first request after flush -> MISS
second request -> HIT
```

## Вопросы на собеседовании

### Вопрос: Что означает `X-Cache: MISS`?

Основной ответ:  
Это значит, что нужной записи не было в Redis, поэтому product-service взял данные из базы и положил их в кеш.

Альтернативный ответ:  
Данные пришли из primary storage, а не из кеша.

### Вопрос: Что означает `X-Cache: HIT`?

Основной ответ:  
Это значит, что product-service нашел товар в Redis и вернул его из кеша, не обращаясь к БД за основным чтением.

Альтернативный ответ:  
Сработал cached read.

### Вопрос: Почему cache invalidation сложна?

Основной ответ:  
Потому что после изменения данных нужно гарантированно убрать или обновить старую запись в кеше. Если этого не сделать, пользователи увидят устаревшие цены, описания или остатки.

Альтернативный ответ:  
Самая сложная часть кеша - не положить данные, а вовремя удалить старые.

### Вопрос: Как тестировать кеш?

Основной ответ:  
Нужно проверять последовательность запросов: первый read дает `MISS`, второй read дает `HIT`, update сбрасывает кеш, следующий read снова дает `MISS`. Также нужно тестировать поведение при недоступном Redis.

Альтернативный ответ:  
Проверяю headers, логи product-service и состояние Redis.

## Критерий завершения урока

Ты можешь доказать через UI, API, headers и логи, что Redis cache работает и инвалидируется.
