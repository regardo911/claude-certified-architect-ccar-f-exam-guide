import { test } from "node:test";

// cases for createRefund in ./refunds.js, written up from /review's findings.
// fill each one in once src/db.js exists.
test.todo("rejects the request when orderId or amount is missing");
test.todo("returns 404 when no order has that orderId");
test.todo("rejects a refund when the order total is 0");
test.todo("stores the refund as integer cents");
test.todo("rejects an amount larger than the order total");
test.todo("rejects a caller who is not allowed to refund the order");
