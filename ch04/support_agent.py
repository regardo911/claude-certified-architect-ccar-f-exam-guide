# support_agent.py
# repo: optional argv[1] = customer message; bare run = the book's version
import asyncio, json, sys, time
from datetime import datetime, timezone
from claude_agent_sdk import (query, ClaudeAgentOptions, AgentDefinition,
                              HookMatcher, tool, create_sdk_mcp_server,
                              AssistantMessage, ResultMessage)
from claude_agent_sdk.types import ToolUseBlock

CUSTOMERS = {"ana@example.com": "C-77"}
TWO_DAYS_AGO = int(time.time()) - 2 * 86400
ORDERS = {
    "12345": {"customer_id": "C-77", "total": 600.0,
              "status": "damaged", "delivered_at": TWO_DAYS_AGO},
    "12346": {"customer_id": "C-77", "total": 45.0,
              "status": "lost", "delivered_at": None},
}
VERIFIED = set()

def reply(obj):
    return {"content": [{"type": "text", "text": json.dumps(obj)}]}

@tool("get_customer",
      "Find a customer by email address. Returns a verified customer_id. "
      "Call this first, before any order lookup or refund.",
      {"email": str})
async def get_customer(args):
    cid = CUSTOMERS.get(args["email"].strip().lower())
    if cid:
        VERIFIED.add(cid)
    return reply({"customer_id": cid, "verified": bool(cid)})

@tool("lookup_order",
      "Look up one order by its number, such as 12345 or #12345. "
      "Returns status, total and delivery time for that order only.",
      {"order_id": str})
async def lookup_order(args):
    oid = args["order_id"].strip("#")
    return reply({"order_id": oid, **ORDERS.get(oid, {"found": False})})

@tool("process_refund",
      "Refund one order to the customer's original payment method.",
      {"customer_id": str, "order_id": str, "amount": float})
async def process_refund(args):
    return reply({"refund_id": "R-" + args["order_id"].strip("#"),
                  "amount": args["amount"], "status": "refunded"})

@tool("escalate_to_human",
      "Hand the case to a human agent. The human cannot see this chat, "
      "so include everything they need.",
      {"customer_id": str, "order_id": str, "amount": float,
       "root_cause": str, "recommended_action": str})
async def escalate_to_human(args):
    print("HANDOFF:", json.dumps(args))
    return reply({"ticket": "H-1001", "status": "queued"})

support = create_sdk_mcp_server("support", "1.0.0",
    [get_customer, lookup_order, process_refund, escalate_to_human])

def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason}}

async def verified_first(input_data, tool_use_id, context):
    args = input_data["tool_input"]
    order = ORDERS.get(str(args.get("order_id", "")).strip("#"), {})
    owner = order.get("customer_id") or args.get("customer_id")
    if owner not in VERIFIED:
        return deny("Verify the customer with get_customer first.")
    return {}

async def refund_cap(input_data, tool_use_id, context):
    if float(input_data["tool_input"].get("amount", 0)) > 500:
        return deny("Refunds over $500 need a human. Call "
                    "escalate_to_human with the case details.")
    return {}

async def iso_dates(input_data, tool_use_id, context):
    data = json.loads(input_data["tool_response"][0]["text"])
    ts = data.get("delivered_at")
    if isinstance(ts, int):
        data["delivered_at"] = datetime.fromtimestamp(
            ts, timezone.utc).isoformat()
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
            "updatedToolOutput": [{"type": "text",
                                   "text": json.dumps(data)}]}}

S = "mcp__support__"
options = ClaudeAgentOptions(
    model="haiku",
    setting_sources=[],
    system_prompt=(
        "You are a support coordinator. Verify the customer with "
        "get_customer. Then start one order-checker per order, all in "
        "the same response, and give each one the customer_id and order "
        "number in its prompt. Decide refunds from their reports."),
    mcp_servers={"support": support},
    tools=["Agent"],
    allowed_tools=["Agent", S + "get_customer", S + "lookup_order",
                   S + "process_refund", S + "escalate_to_human"],
    agents={"order-checker": AgentDefinition(
        description="Investigates one order and reports its facts.",
        prompt="Look up the order you are given with lookup_order. "
               "Report status, total and delivered_at. Do nothing else.",
        tools=[S + "lookup_order"])},
    hooks={
        "PreToolUse": [
            HookMatcher(matcher=S + "lookup_order|" + S + "process_refund",
                        hooks=[verified_first]),
            HookMatcher(matcher=S + "process_refund", hooks=[refund_cap])],
        "PostToolUse": [
            HookMatcher(matcher=S + "lookup_order", hooks=[iso_dates])]},
    env={"CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1"},
    max_turns=20,
)

PROMPT = ("I'm ana@example.com. Order #12345 arrived smashed and I want "
          "my $600 back. Order #12346 never showed up at all.")

async def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else PROMPT
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    print("TOOL", msg.message_id[-6:], block.name,
                          json.dumps(block.input)[:70])
        elif isinstance(msg, ResultMessage):
            print("DONE", msg.subtype, "turns:", msg.num_turns,
                  "session:", msg.session_id)
            denied = msg.permission_denials or []
            print("DENIED:", [d.get("tool_name") for d in denied])
            print(msg.result)

if __name__ == "__main__":
    asyncio.run(main())
