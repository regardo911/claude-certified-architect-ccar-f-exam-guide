# extract.py
# repo: optional argv[1] = document path; bare run = the book's version
import json, sys
from typing import Literal, Optional
import anthropic
from pydantic import BaseModel, ValidationError
from schema import EXTRACT_INVOICE

client = anthropic.Anthropic()

SYSTEM = """You extract invoices into the extract_invoice tool.
Rules:
- Amounts are integer cents: "$1,204.50" becomes 120450.
- Dates are YYYY-MM-DD. "3rd March" with no year stays null.
- If a field is not in the document, use null. Do not infer it.
- category "unclear" when two categories fit equally well."""

class LineItem(BaseModel):
    description: str
    amount_cents: int

class Invoice(BaseModel):
    vendor: str
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    currency: Literal["USD", "EUR", "GBP", "other"]
    currency_other: Optional[str]
    category: Literal["software", "hardware", "services",
                      "travel", "other", "unclear"]
    category_detail: Optional[str]
    line_items: list[LineItem]
    stated_total_cents: Optional[int]

def call(messages):
    resp = client.messages.create(
        model="claude-haiku-5-5", max_tokens=2048, system=SYSTEM,
        tools=[EXTRACT_INVOICE],
        tool_choice={"type": "tool", "name": "extract_invoice"},
        messages=messages)
    block = next(b for b in resp.content if b.type == "tool_use")
    return resp, block

def check(inv):
    calculated = sum(item.amount_cents for item in inv.line_items)
    problems = []
    if inv.stated_total_cents is not None and \
            calculated != inv.stated_total_cents:
        problems.append(f"line items add to {calculated} cents but "
                        f"stated_total_cents is {inv.stated_total_cents}")
    if inv.currency == "other" and not inv.currency_other:
        problems.append("currency is 'other' but currency_other is null")
    return calculated, problems

def extract(document, max_retries=2):
    messages = [{"role": "user", "content": document}]
    previous = None
    for attempt in range(1, max_retries + 2):
        resp, block = call(messages)
        try:
            inv = Invoice.model_validate(block.input)
            calculated, problems = check(inv)
        except ValidationError as e:
            inv, problems = None, [str(e)]
        if not problems:
            return {"invoice": inv.model_dump(), "attempts": attempt,
                    "calculated_total_cents": calculated,
                    "conflict_detected": False}
        if block.input == previous:          # same answer twice: the
            break                            # document disagrees itself
        previous = block.input
        if attempt > max_retries:
            break
        messages += [
            {"role": "assistant", "content": resp.content},
            {"role": "user", "content": [{
                "type": "tool_result", "tool_use_id": block.id,
                "is_error": True,
                "content": "Validation failed: " + "; ".join(problems) +
                           ". Re-read the document and call "
                           "extract_invoice again. If the document "
                           "itself disagrees, copy what it says."}]}]
    return {"invoice": block.input, "attempts": attempt,
            "conflict_detected": True, "problems": problems,
            "route": "human_review"}

if __name__ == "__main__":
    doc = open(sys.argv[1] if len(sys.argv) > 1 else "invoice-001.txt").read()
    print(json.dumps(extract(doc), indent=2))
