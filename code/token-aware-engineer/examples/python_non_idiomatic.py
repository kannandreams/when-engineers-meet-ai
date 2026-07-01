from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class Order:
    customer_id: str
    quantity: int
    unit_price: Decimal

    @property
    def total_value(self) -> Decimal:
        return Decimal(self.quantity) * self.unit_price


def is_valid_order(order: Order) -> bool:
    if not order.customer_id:
        return False

    if order.quantity <= 0:
        return False

    if order.unit_price <= Decimal("0"):
        return False

    return True


def calculate_customer_totals(
    orders: Iterable[Order],
) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}

    for order in orders:
        if not is_valid_order(order):
            continue

        current_total = totals.get(order.customer_id, Decimal("0"))
        updated_total = current_total + order.total_value
        totals[order.customer_id] = updated_total

    return totals