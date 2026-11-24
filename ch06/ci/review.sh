#!/usr/bin/env bash
# repo: optional $1 = file to review; bare run = the book's version
set -euo pipefail
SCHEMA="$(cat ci/findings.schema.json)"

claude -p "Review ${1:-src/api/refunds.js} against docs/review-standards.md." \
  --model haiku \
  --output-format json \
  --json-schema "$SCHEMA" \
  --tools "Read,Grep,Glob" \
  --max-budget-usd 1 \
  < /dev/null > review.json

jq -e '.structured_output.findings' review.json > findings.json \
  || { echo "No structured output. See review.json"; exit 1; }
jq -r '.[] | "\(.file):\(.line) [\(.severity)] \(.message)"' findings.json
