# user-service

Owns user records for the QA lab.

## Endpoints

- `POST /users`
- `GET /users/{user_id}`
- `GET /users`
- `PATCH /users/{user_id}/status`
- `DELETE /users/{user_id}`
- `GET /health`
- `GET /ready`

The service uses PostgreSQL and enforces unique user emails.
