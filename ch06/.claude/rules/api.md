---
paths:
  - "src/api/**/*"
---
# API handlers
- async/await only. No .then() chains.
- Return errors as { error: { code, message } } with an HTTP status.
- Log the order_id on every error path.
