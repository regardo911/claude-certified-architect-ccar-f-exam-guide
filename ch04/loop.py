# loop.py
# repo: optional argv[1] = prompt; bare run = the book's version
import json, sys
import anthropic

client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY

TOOLS = [{
    "name": "lookup_order",
    "description": "Look up one order by its number, such as #12345. "
                   "Returns status and total for that order only.",
    "input_schema": {"type": "object",
                     "properties": {"order_id": {"type": "string"}},
                     "required": ["order_id"]},
}]

def run_tool(name, args):
    if name == "lookup_order":
        return {"order_id": args["order_id"], "status": "delivered",
                "total": 600}
    return {"error": f"unknown tool {name}"}

def run(prompt, max_turns=25):
    messages = [{"role": "user", "content": prompt}]
    for _ in range(max_turns):                       # backstop only
        resp = client.messages.create(
            model="claude-haiku-5-5", max_tokens=1024,
            tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            return "".join(b.text for b in resp.content
                           if b.type == "text")
        if resp.stop_reason != "tool_use":
            raise RuntimeError(f"stopped on {resp.stop_reason}")

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                out = run_tool(block.name, block.input)
                results.append({"type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(out)})
        messages.append({"role": "user", "content": results})
    raise RuntimeError("hit the max_turns backstop")

if __name__ == "__main__":
    print(run(sys.argv[1] if len(sys.argv) > 1
              else "Where is my order #12345?"))
