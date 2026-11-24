# schema.py
def nullable(t):
    return {"anyOf": [{"type": t}, {"type": "null"}]}

EXTRACT_INVOICE = {
    "name": "extract_invoice",
    "description": "Record the fields of one invoice. Use null for any "
                   "field the document does not state. Never guess.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "vendor": {"type": "string"},
            "invoice_number": nullable("string"),
            "invoice_date": nullable("string"),
            "currency": {"type": "string",
                         "enum": ["USD", "EUR", "GBP", "other"]},
            "currency_other": nullable("string"),
            "category": {"type": "string",
                         "enum": ["software", "hardware", "services",
                                  "travel", "other", "unclear"]},
            "category_detail": nullable("string"),
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "description": {"type": "string"},
                        "amount_cents": {"type": "integer"}},
                    "required": ["description", "amount_cents"]}},
            "stated_total_cents": nullable("integer"),
        },
        "required": ["vendor", "invoice_number", "invoice_date",
                     "currency", "currency_other", "category",
                     "category_detail", "line_items",
                     "stated_total_cents"],
    },
}
