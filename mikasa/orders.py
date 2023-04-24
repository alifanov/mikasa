from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class BaseOrder:
    type: OrderType
    price: float
    volume: float
    executed_at: Optional[datetime]

    def _is_enough_balance(self, balance):
        return balance >= self.price * self.volume

    def _is_enough_fund(self, fund):
        return fund >= self.volume

    def update_trailing_state(self, high, low):
        pass

    def can_be_executed(self, high, low, fund, balance):
        if self.type == OrderType.BUY:
            if not self._is_enough_balance(balance):
                return False
            return low < self.price
        if self.type == OrderType.SELL:
            if not self._is_enough_fund(fund):
                return False
            return high > self.price
        return False

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


class StopOrder(BaseOrder):
    def can_be_executed(self, high, low, balance, fund):
        if self.type == OrderType.BUY:
            if not self._is_enough_balance(balance):
                return False
            return high > self.price
        if self.type == OrderType.SELL:
            if not self._is_enough_fund(fund):
                return False
            return low < self.price
        return False


@dataclass
class TrailingStopLossOrder(StopOrder):
    trail_percent: float

    def update_trailing_state(self, high, low):
        if self.type == OrderType.SELL:
            self.price = low * (1.0 - self.trail_percent)
