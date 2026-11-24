# hook_test.py
import asyncio
import support_agent as sa

async def main():
    S = "mcp__support__"
    def call(name, **args):
        return {"tool_name": S + name, "tool_input": args}

    print("lookup before verify:",
          await sa.verified_first(call("lookup_order", order_id="12345"),
                                  None, None))
    sa.VERIFIED.add("C-77")
    print("lookup after verify: ",
          await sa.verified_first(call("lookup_order", order_id="12345"),
                                  None, None))
    for amount in (45, 500, 600):
        out = await sa.refund_cap(call("process_refund", customer_id="C-77",
                                       order_id="12345", amount=amount),
                                  None, None)
        decision = out.get("hookSpecificOutput", {}).get(
            "permissionDecision", "allow")
        print(f"refund ${amount}: {decision}")

asyncio.run(main())
