---
paths:
  - "**/*.test.*"
---
# Tests
- One behaviour per test. Name it "does X when Y".
- Use the fixtures in test/fixtures/. Never call the real payment API.
- Every bug fix ships with a test that failed before the fix.
