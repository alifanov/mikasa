from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class BaseOrder:
    type: OrderType
    price: float
    volume: float
    executed_at: Optional[datetime]

    def update_trailing_state(self, high, low):
        pass

    def can_be_executed(self, high, low):
        if self.type == OrderType.BUY:
            return low < self.price
        if self.type == OrderType.SELL:
            return high > self.price

    def execute(self, dt, commission_fraction):
        balance_delta = self.volume * self.price * (1.0 - commission_fraction)
        if self.type == OrderType.BUY:
            self.executed_at = dt
            return self.volume, -balance_delta
        if self.type == OrderType.SELL:
            self.executed_at = dt
            return -self.volume, balance_delta
        raise ValueError("Order type is bad")

    class Meta:
        abstract = True


class LimitOrder(BaseOrder):
    pass


@dataclass
class TrailingStopLossOrder(BaseOrder):
    trail_percent: float

    def update_trailing_state(self, high, low):
        if self.type == OrderType.BUY:
            self.price = low * (1.0 - self.trail_percent)
        if self.type == OrderType.SELL:
            self.price = high * (1.0 - self.trail_percent)
