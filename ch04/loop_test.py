# loop_test.py
# Runs loop.py's control flow against a stand-in client.
# No API key and no model call: it proves the stop rule.
import os
os.environ.setdefault("ANTHROPIC_API_KEY", "not-used")
from types import SimpleNamespace as NS
import loop

script = [
    NS(stop_reason="tool_use", content=[
        NS(type="text", text="Checking."),
        NS(type="tool_use", id="tu_1", name="lookup_order",
           input={"order_id": "#12345"})]),
    NS(stop_reason="end_turn", content=[
        NS(type="text", text="Order #12345 was delivered. Total $600.")]),
]
sent = []

def fake_create(**kwargs):
    sent.append(len(kwargs["messages"]))
    return script[len(sent) - 1]

loop.client = NS(messages=NS(create=fake_create))
print(loop.run("Where is my order #12345?"))
print("requests sent:", len(sent), "| messages at each call:", sent)

loop.client = NS(messages=NS(create=lambda **kw: NS(
    stop_reason="max_tokens", content=[NS(type="text", text="Ord")])))
try:
    loop.run("Where is my order #12345?")
except RuntimeError as err:
    print("RuntimeError:", err)
