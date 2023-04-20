import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    type: OrderType
    price: float
    volume: float
    executed_at: Optional[datetime] = None

    def can_be_executed(self):
        return True

    def execute(self, dt, commission_fraction):
        if self.type == OrderType.BUY:
            self.executed_at = dt
            return self.volume, -self.volume * self.price * (1.0 - commission_fraction)
        if self.type == OrderType.SELL:
            self.executed_at = dt
            return -self.volume, self.volume * self.price * (1.0 - commission_fraction)
        raise ValueError("Order type is bad")


class BTException(Exception):
    pass


class BT:
    trade_pct = 0.01
    trade_amount = None
    commission_fraction = 0.001

    def __init__(self, dataseries, balance=1000.0):
        self.dataseries = dataseries
        self.balance = balance
        self.start_balance = balance
        self.fund = 0
        self.open_orders = []
        self.order_history = []

    def get_trade_amount(self):
        if self.trade_amount is None:
            return self.balance * self.trade_pct
        return self.trade_amount

    def prepare_data(self):
        pass

    def buy(self, price, shares_volume):
        if self.balance < price * shares_volume:
            logger.warning("Can not execute order due to not enough balance")
            return

        dt = self.dataseries[0].datetime
        order = Order(type=OrderType.BUY, price=price, volume=shares_volume)
        self.open_orders.append(order)
        logger.info(f"[BUY] created {dt=} {price=:.2f} {shares_volume=:.2f}")

    def sell(self, price):
        if self.fund:
            dt = self.dataseries[0].datetime
            order = Order(type=OrderType.SELL, price=price, volume=self.fund)
            self.open_orders.append(order)
            logger.info(f"[SELL] created {dt=} {price=:.2f} volume={self.fund:.2f}")

    def process_bar(self):
        pass

    def get_profit(self):
        return self.balance - self.start_balance

    def get_roi(self):
        return 1.0 * self.get_profit() / self.start_balance

    def go(self):
        return self.dataseries.next()

    def process_open_orders(self):
        dt = self.dataseries[0].datetime
        rest_orders = []
        for order in self.open_orders:
            if order.can_be_executed():
                fund, balance = order.execute(
                    dt=self.dataseries[0].datetime, commission_fraction=self.commission_fraction
                )
                self.order_history.append(order)
                self.fund += fund
                self.balance += balance
                logger.info(f"Executed [{order.type}] {dt=} balance={self.balance:.2f}")
            else:
                rest_orders.append(order)
        self.open_orders = rest_orders

    def run(self):
        self.prepare_data()

        while not self.dataseries.is_end():
            self.process_open_orders()
            self.process_bar()
            self.go()

        self.process_open_orders()

    def plot(self):  # pragma: no cover
        data = self.dataseries.data
        data.set_index("datetime", inplace=True)
        headers = ["close"]
        outline_indicators = []
        outline_data = {}
        for ind in self.dataseries.indicators:
            if ind.draw_inline:
                headers.append(ind.title)
            else:
                outline_indicators.append(ind)
                outline_data[ind.title] = data[ind.title]
                data.drop(ind.title, inplace=True, axis=1)

        data = data[headers]
        nrows = len(outline_indicators) + 1
        fig, axes = plt.subplots(nrows=nrows, ncols=1)

        data.plot(ax=axes[0], sharex=True)

        for i, oi in enumerate(outline_indicators):
            outline_data[oi.title].plot(ax=axes[i + 1], sharex=True, title=oi.title)
            oi.draw_extra_charts(axes[i + 1])

        buy_orders = [it for it in self.open_orders if it.type == OrderType.BUY]
        sell_orders = [it for it in self.open_orders if it.type == OrderType.SELL]

        self._draw_orders(buy_orders, marker="g^")

        self._draw_orders(sell_orders, marker="rv")

        plt.show()

    def _draw_orders(self, orders, marker):
        order_datetimes = [order.executed_at for order in orders]
        order_prices = [order.price for order in orders]
        plt.plot(order_datetimes, order_prices, marker)
