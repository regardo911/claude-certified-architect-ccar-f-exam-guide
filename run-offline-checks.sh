#!/usr/bin/env bash
# runs the book's no-key scripts from their own folders and compares each
# one's real stdout with the lines its chapter prints. no key, no network.
set -uo pipefail
cd "$(dirname "$0")" || exit 1
PY="${PYTHON:-python}"
unset ANTHROPIC_API_KEY   # prove none of these needs one

if ! "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
  echo "Need Python 3.11+ as '$PY'. Activate the .venv from the README first."
  exit 1
fi

ran=0; passed=0
err="$(mktemp)"; trap 'rm -f "$err"' EXIT

result() {  # result <label> <want> <got>
  ran=$((ran + 1))
  if [ "$3" = "$2" ]; then
    passed=$((passed + 1)); echo "PASS $1"
  else
    echo "FAIL $1"
    diff <(printf '%s\n' "$2") <(printf '%s\n' "$3") | sed 's/^/    /'
    tail -5 "$err" | sed 's/^/    stderr: /'
  fi
}

check() {  # check <folder> <script>; the expected stdout comes in on stdin
  local want got
  want="$(cat)"
  got="$(cd "$1" && "$PY" "$2" 2>"$err")"
  result "$1/$2" "$want" "$got"
}

check ch04 loop_test.py <<'EOF'
Order #12345 was delivered. Total $600.
requests sent: 2 | messages at each call: [1, 3]
RuntimeError: stopped on max_tokens
EOF

check ch04 hook_test.py <<'EOF'
lookup before verify: {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'Verify the customer with get_customer first.'}}
lookup after verify:  {}
refund $45: allow
refund $500: allow
refund $600: deny
EOF

# stdout only: the two "Tool ... failed" lines are the server's own stderr log
check ch05 test_client.py <<'EOF'
tools: ['get_customer', 'lookup_order', 'process_refund']
resources: ['policy://refunds']
lookup_order #12345 isError=False
    {   "order_id": "12345",   "found": true,   "total": 600,   "status": "delivered" }
lookup_order #55555 isError=False
    {   "order_id": "55555",   "found": false }
lookup_order #99999 isError=True
    Error executing tool lookup_order: {"errorCategory": "transient", "isRetryable": true, "message": "Order service timed out after 5s."}
process_refund #12345 isError=True
    Error executing tool process_refund: {"errorCategory": "business", "isRetryable": false, "message": "Refunds over $500 need a human agent. Tell the customer a specialist will review it today."}
EOF

check ch07 check_test.py <<'EOF'
017: (242351, ['line items add to 242351 cents but stated_total_cents is 242851'])
018: (98414, [])
EOF

# make_invoices.py: run it, then read the 100 files it wrote and recount.
# ch07/invoices/ stays (gitignored): batch.py reads it next.
got="$(cd ch07 && "$PY" make_invoices.py 2>"$err" && "$PY" - 2>>"$err" <<'EOF'
import re
from pathlib import Path


def cents(s):
    return round(float(s.replace(",", "")) * 100)

off, no_number = [], 0
for p in sorted(Path("invoices").glob("invoice-*.txt")):
    t = p.read_text()
    items = sum(cents(m) for m in re.findall(r"\.{3,} \$([\d,]+\.\d\d)", t))
    total = cents(re.search(r"TOTAL DUE: \$([\d,]+\.\d\d)", t).group(1))
    if items != total:
        off.append(f"{p.stem[-3:]}(+{total - items})")
    if "Invoice INV-" not in t:
        no_number += 1
print("totals off, in cents:", " ".join(off))
print("no invoice number:", no_number)
EOF
)"
result "ch07/make_invoices.py" "wrote 100 invoices
totals off, in cents: 017(+500) 034(+500) 051(+500) 068(+500) 085(+500)
no invoice number: 11" "$got"

echo "$passed of $ran passed"
[ "$ran" -gt 0 ] && [ "$passed" -eq "$ran" ]
