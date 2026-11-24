# batch.py
import json, sys, time
from pathlib import Path
import anthropic
from anthropic.types.message_create_params import (
    MessageCreateParamsNonStreaming)
from anthropic.types.messages.batch_create_params import Request
from extract import SYSTEM, Invoice, check
from schema import EXTRACT_INVOICE

client = anthropic.Anthropic()

def request_for(custom_id, text):
    return Request(custom_id=custom_id,
                   params=MessageCreateParamsNonStreaming(
                       model="claude-haiku-5-5", max_tokens=2048,
                       system=SYSTEM, tools=[EXTRACT_INVOICE],
                       tool_choice={"type": "tool",
                                    "name": "extract_invoice"},
                       messages=[{"role": "user", "content": text}]))

def submit(docs):
    batch = client.messages.batches.create(
        requests=[request_for(cid, text) for cid, text in docs.items()])
    print("submitted", batch.id, len(docs), "requests")
    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            return batch
        time.sleep(60)

def collect(batch):
    done, failed = {}, []
    for r in client.messages.batches.results(batch.id):
        if r.result.type == "succeeded":
            block = next(b for b in r.result.message.content
                         if b.type == "tool_use")
            done[r.custom_id] = block.input
        else:
            failed.append((r.custom_id, r.result.type))
    return done, failed

def flag_conflicts(done):
    flagged = {}
    for cid, fields in done.items():
        calculated, problems = check(Invoice.model_validate(fields))
        if problems:
            flagged[cid] = problems
    return flagged

if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "invoices")
    docs = {p.stem: p.read_text() for p in sorted(folder.glob("*.txt"))}
    done, failed = collect(submit(docs))
    print(len(done), "succeeded; failed:", failed)
    if failed:
        retry = {cid: docs[cid] for cid, _ in failed}
        more, still = collect(submit(retry))
        done.update(more)
        print("after resubmit:", len(done), "succeeded; still:", still)
    flagged = flag_conflicts(done)
    print("totals that don't add up:", sorted(flagged))
    Path("extracted.json").write_text(json.dumps(done, indent=2))
