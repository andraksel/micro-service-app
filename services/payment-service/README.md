# payment-service

Simulates an external payment dependency for resilience testing.

## Test controls

`POST /test-controls/payment-mode`

```json
{
  "mode": "success"
}
```

Supported modes:

- `success`
- `failure`
- `timeout`
- `random`

This endpoint is local/testing-only and exists to make failure scenarios deterministic.
