# reliable_agent.py
import asyncio, json, sys
from claude_agent_sdk import (ClaudeSDKClient, ClaudeAgentOptions,
                              AgentDefinition, HookMatcher, tool,
                              create_sdk_mcp_server, AssistantMessage,
                              ResultMessage)
from claude_agent_sdk.types import ToolUseBlock

KEEP = ["order_id", "status", "total", "items", "delivered_on"]
CASE = {}                      # the case-facts block lives here

def big_record(oid, total, status):
    rec = {f"warehouse_field_{i}": f"value-{i}" for i in range(35)}
    rec.update(order_id=oid, status=status, total=total,
               items=["blender"], delivered_on="2 days ago")
    return rec

ORDERS = {"12345": big_record("12345", 600.0, "damaged"),
          "12347": big_record("12347", 89.0, "delivered")}

def reply(obj, error=False):
    return {"content": [{"type": "text", "text": json.dumps(obj)}],
            "is_error": error}

@tool("lookup_order", "Look up one order by number, such as 12345.",
      {"order_id": str})
async def lookup_order(args):
    oid = args["order_id"].strip("#")
    if oid == "12346":
        return reply({"errorCategory": "transient", "isRetryable": True,
                      "message": "Order service timed out after 5s."},
                     error=True)
    if oid not in ORDERS:
        return reply({"order_id": oid, "found": False})
    return reply(ORDERS[oid])

@tool("escalate_to_human",
      "Hand the case to a human. They cannot see this chat.",
      {"customer_id": str, "summary": str, "recommended_action": str})
async def escalate_to_human(args):
    CASE["escalated"] = True
    print("  HANDOFF:", json.dumps(args)[:160])
    return reply({"ticket": "H-1002", "status": "queued"})

@tool("record_fact",
      "Save one thing the customer stated: an amount, a date, a "
      "promise they say they were given. Saved facts are shown to you "
      "on every turn.", {"key": str, "value": str})
async def record_fact(args):
    CASE.setdefault("customer_stated", {})[args["key"]] = args["value"]
    return reply({"saved": args["key"]})

support = create_sdk_mcp_server("support", "1.0.0",
                                [lookup_order, escalate_to_human,
                                 record_fact])

async def trim_and_record(input_data, tool_use_id, context):
    data = json.loads(input_data["tool_response"][0]["text"])
    if not data.get("order_id") or data.get("found") is False:
        return {}
    slim = {k: data[k] for k in KEEP if k in data}
    CASE.setdefault("orders", {})[slim["order_id"]] = slim
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
            "updatedToolOutput": [{"type": "text",
                                   "text": json.dumps(slim)}]}}

async def inject_case_facts(input_data, tool_use_id, context):
    if not CASE:
        return {}
    return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
            "additionalContext": "CASE FACTS (authoritative, keep exact):\n"
                                 + json.dumps(CASE, indent=1)}}

SYSTEM = """You are a support agent for one customer, customer_id C-77.

Escalate with escalate_to_human when, and only when:
- the customer asks for a human. Do it on the first ask. Do not
  investigate first.
- policy does not cover the request (for example, price matching a
  competitor; policy only covers our own price drops).
- you cannot make progress after two attempts.
Do not escalate because the customer sounds upset, and do not rate
your own confidence. If the issue is routine, say you understand and
offer to fix it.

Examples:
Customer: "This is the third time I've asked. Get me a person."
-> escalate_to_human now. No lookup first.
Customer: "I'm furious, my blender arrived broken!"
-> Acknowledge it, look up the order, offer a refund or replacement.
Customer: "Another store has it $20 cheaper, match it."
-> Policy is silent on competitor prices: escalate_to_human.

When the customer states an amount, a date or a promise, save it with
record_fact before you answer.

Delegate every order lookup to an order-checker, one per order, all in
the same response. End every answer with a line that starts
"Coverage:" naming what you confirmed and what you could not check."""

options = ClaudeAgentOptions(
    model="haiku", setting_sources=[], system_prompt=SYSTEM,
    mcp_servers={"support": support}, tools=["Agent"],
    allowed_tools=["Agent", "mcp__support__lookup_order",
                   "mcp__support__escalate_to_human",
                   "mcp__support__record_fact"],
    agents={"order-checker": AgentDefinition(
        description="Looks up one order and reports what it found.",
        prompt="Look up the order you are given. If the tool returns "
               "isRetryable true, retry once. If it still fails, report "
               "JSON: {\"status\": \"failed\", \"failure_type\", "
               "\"attempted\", \"partial_results\", \"alternatives\"}. "
               "Never report a failure as an empty result.",
        tools=["mcp__support__lookup_order"])},
    hooks={"PostToolUse": [HookMatcher(matcher="mcp__support__lookup_order",
                                       hooks=[trim_and_record])],
           "UserPromptSubmit": [HookMatcher(hooks=[inject_case_facts])]},
    env={"CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1"},
    max_turns=20,
)

async def turn(client, text):
    print("USER:", text)
    await client.query(text)
    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, ToolUseBlock):
                    print("  TOOL", b.name.split("__")[-1],
                          json.dumps(b.input)[:80])
        elif isinstance(msg, ResultMessage):
            print("AGENT:", (msg.result or "").strip(), "\n")

async def main(script):
    async with ClaudeSDKClient(options=options) as client:
        for line in script:
            await turn(client, line)

SCRIPTS = {
    "human": ["Hi. I want to talk to a human, please."],
    "timeout": ["Order 12345 arrived broken and order 12346 never came. "
                "What can you do?"],
    "compact": ["My blender, order 12345, arrived smashed. I want the $600 "
                "back, and you promised me a refund by Friday last time.",
                "Also, what's your returns address?",
                "And do you sell replacement jugs?",
                "/compact",
                "Remind me: exactly which order, what amount, and what did "
                "you promise last time?"],
}

if __name__ == "__main__":
    if "--no-facts" in sys.argv:
        options.hooks.pop("UserPromptSubmit")
    asyncio.run(main(SCRIPTS[sys.argv[1]]))
