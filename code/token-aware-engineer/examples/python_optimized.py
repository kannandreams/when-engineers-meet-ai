from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class Order:
    customer_id: str
    quantity: int
    unit_price: Decimal


def calculate_customer_totals(orders: Iterable[Order]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}

    for order in orders:
        if (
            not order.customer_id
            or order.quantity <= 0
            or order.unit_price <= 0
        ):
            continue

        totals[order.customer_id] = (
            totals.get(order.customer_id, Decimal("0"))
            + order.quantity * order.unit_price
        )

    return totals