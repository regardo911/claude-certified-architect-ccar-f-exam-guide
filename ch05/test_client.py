# test_client.py
import os, anyio
os.environ["SUPPORT_API_TOKEN"] = "test-token"
from mcp import Client
from server import mcp

CASES = [("lookup_order", {"order_id": "#12345"}),
         ("lookup_order", {"order_id": "#55555"}),
         ("lookup_order", {"order_id": "#99999"}),
         ("process_refund", {"customer_id": "C-77",
                             "order_id": "#12345", "amount": 600})]

async def main():
    async with Client(mcp) as c:
        print("tools:", [t.name for t in (await c.list_tools()).tools])
        print("resources:", [str(r.uri) for r in
                             (await c.list_resources()).resources])
        for name, args in CASES:
            r = await c.call_tool(name, args)
            print(f"{name} {args.get('order_id')} isError={r.is_error}")
            print("   ", r.content[0].text.replace("\n", " "))

anyio.run(main)
