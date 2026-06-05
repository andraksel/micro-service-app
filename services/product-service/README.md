# product-service

Owns product catalog and stock data.

## Cache behavior

`GET /products/{product_id}` uses Redis before PostgreSQL.

Cache key format:

```text
product:{product_id}
```

The TTL is configured by `CACHE_TTL_SECONDS`. Responses include:

- `X-Cache: MISS` when the product is loaded from PostgreSQL.
- `X-Cache: HIT` when the product is served from Redis.

Product updates and deletes invalidate the related cache entry.
