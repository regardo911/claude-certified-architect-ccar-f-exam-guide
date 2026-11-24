# fork_test.py
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def ask(prompt, **kw):
    opts = ClaudeAgentOptions(model="haiku", setting_sources=[], **kw)
    result = None
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, ResultMessage):
            result = msg                 # read the whole stream
    return result.session_id, result.result

async def main():
    base, _ = await ask("Remember: the refund cap is $500. Reply OK.")
    fork, a1 = await ask("What is the refund cap?",
                         resume=base, fork_session=True)
    same, a2 = await ask("Say the cap again.", resume=base)
    print("base  ", base)
    print("fork  ", fork, "->", a1)
    print("resume", same, "->", a2)

asyncio.run(main())
