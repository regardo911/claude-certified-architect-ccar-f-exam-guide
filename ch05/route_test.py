# route_test.py
import asyncio, sys
from claude_agent_sdk import (query, ClaudeAgentOptions, AssistantMessage,
                              ResultMessage)
from claude_agent_sdk.types import ToolUseBlock

SERVER = sys.argv[1] if len(sys.argv) > 1 else "server.py"
PROMPT = sys.argv[2] if len(sys.argv) > 2 else "check my order #12345"
RUNS = int(sys.argv[3]) if len(sys.argv) > 3 else 10

support = {"type": "stdio", "command": sys.executable, "args": [SERVER],
           "env": {"SUPPORT_API_TOKEN": "test-token"}}

async def first_tool():
    opts = ClaudeAgentOptions(
        model="haiku", setting_sources=[], max_turns=4,
        mcp_servers={"support": support}, strict_mcp_config=True,
        tools=[], allowed_tools=["mcp__support__get_customer",
                                 "mcp__support__lookup_order"])
    first = None
    async for msg in query(prompt=PROMPT, options=opts):
        if isinstance(msg, AssistantMessage) and first is None:
            for b in msg.content:
                if isinstance(b, ToolUseBlock) and "support" in b.name:
                    first = b.name.split("__")[-1]
                    break
    return first

async def main():
    tally = {}
    for _ in range(RUNS):
        name = await first_tool()
        tally[name] = tally.get(name, 0) + 1
    print(f"{SERVER}: '{PROMPT}' x{RUNS} -> {tally}")

asyncio.run(main())
