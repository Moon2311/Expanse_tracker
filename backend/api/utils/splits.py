from decimal import Decimal


def split_amount_equally(total, n_people: int) -> list[Decimal]:
    """Return n Decimal shares that sum exactly to total (two decimal places)."""
    if n_people <= 0:
        return []
    total = Decimal(str(total)).quantize(Decimal("0.01"))
    cents = int(total * 100)
    base, rem = divmod(cents, n_people)
    out = []
    for i in range(n_people):
        c = base + (1 if i < rem else 0)
        out.append(Decimal(c) / Decimal(100))
    return out
