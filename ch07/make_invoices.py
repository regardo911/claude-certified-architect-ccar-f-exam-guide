# make_invoices.py
import random
from pathlib import Path

random.seed(7)
VENDORS = ["Northwind Cloud", "Contoso Hardware", "Fabrikam Travel",
           "Tailspin Consulting", "Litware Software"]
out = Path("invoices")
out.mkdir(exist_ok=True)
for n in range(1, 101):
    lines = [(f"Item {i}", random.randint(1000, 90000))
             for i in range(1, random.randint(2, 5))]
    total = sum(c for _, c in lines)
    if n % 17 == 0:
        total += 500                      # a total that does not add up
    body = [VENDORS[n % 5].upper(),
            f"Invoice INV-{3000 + n}" if n % 9 else "",  # 1 in 9 has none
            ""]
    body += [f"  {d} ......... ${c / 100:,.2f}" for d, c in lines]
    body += ["", f"  TOTAL DUE: ${total / 100:,.2f}"]
    (out / f"invoice-{n:03d}.txt").write_text("\n".join(body) + "\n")
print("wrote", len(list(out.glob("*.txt"))), "invoices")
