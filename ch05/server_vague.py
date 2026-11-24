# server.py
import json, os
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("support")
TOKEN = os.environ.get("SUPPORT_API_TOKEN", "")

def fail(category, retryable, message):
    raise ToolError(json.dumps({"errorCategory": category,
                                "isRetryable": retryable,
                                "message": message}))

@mcp.tool()
def get_customer(email: str) -> dict:
    """Retrieves customer information."""
    if not TOKEN:
        fail("permission", False, "Server has no API token.")
    if "@" not in email:
        fail("validation", False, f"'{email}' is not an email address.")
    return {"customer_id": "C-77", "verified": True}

@mcp.tool()
def lookup_order(order_id: str) -> dict:
    """Retrieves order details."""
    oid = order_id.strip("#")
    if oid == "99999":
        fail("transient", True, "Order service timed out after 5s.")
    if oid != "12345":
        return {"order_id": oid, "found": False}
    return {"order_id": oid, "found": True, "total": 600,
            "status": "delivered"}

@mcp.tool()
def process_refund(customer_id: str, order_id: str, amount: float) -> dict:
    """Refund one order. Needs the verified customer_id from
    get_customer. Refunds over $500 are refused: escalate those."""
    if amount > 500:
        fail("business", False, "Refunds over $500 need a human agent. "
             "Tell the customer a specialist will review it today.")
    return {"refund_id": "R-" + order_id.strip("#"), "amount": amount}

@mcp.resource("policy://refunds")
def refund_policy() -> str:
    """The refund rules agents must follow."""
    return ("Refunds up to $500: agent may approve. Over $500: escalate. "
            "Damaged items: refund or replace, customer's choice.")

if __name__ == "__main__":
    mcp.run()
