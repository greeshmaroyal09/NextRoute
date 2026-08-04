from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount_inr: Decimal

    def __add__(self, other: Money) -> Money:
        return Money(self.amount_inr + other.amount_inr)

    def __sub__(self, other: Money) -> Money:
        return Money(self.amount_inr - other.amount_inr)

    def format(self) -> str:
        return f"₹{self.amount_inr:,.2f}".replace(".00", "")
