import { db } from "../db.js";

export async function createRefund(req, res) {
  const { orderId, amount } = req.body;
  const order = await db.orders.find(orderId);
  const refund = order.total * (amount / order.total);
  await db.refunds.insert({ orderId, cents: refund });
  res.json({ ok: true, refund });
}
