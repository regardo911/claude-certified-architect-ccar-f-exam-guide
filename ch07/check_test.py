# check_test.py
# The validation layer. No API key, no model call.
import os
os.environ.setdefault("ANTHROPIC_API_KEY", "not-used")
from extract import Invoice, check

def item(desc, cents):
    return {"description": desc, "amount_cents": cents}

inv017 = Invoice(vendor="Fabrikam Travel", invoice_number="INV-3017",
                 invoice_date=None, currency="USD", currency_other=None,
                 category="travel", category_detail=None,
                 line_items=[item("Item 1", 42175), item("Item 2", 62027),
                             item("Item 3", 77750), item("Item 4", 60399)],
                 stated_total_cents=242851)
inv018 = Invoice(vendor="Tailspin Consulting", invoice_number=None,
                 invoice_date=None, currency="USD", currency_other=None,
                 category="services", category_detail=None,
                 line_items=[item("Item 1", 40291), item("Item 2", 33561),
                             item("Item 3", 24562)],
                 stated_total_cents=98414)
print("017:", check(inv017))
print("018:", check(inv018))
