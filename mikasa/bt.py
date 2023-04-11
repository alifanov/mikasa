import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class Trade:
    status = "OPEN"
    open_price = None
    close_price = None
    volume = None
    open_datetime = None
    close_datetime = None

    def __repr__(self):  # pragma: no cover
        return "Price: {} Volume: {} Status: {}".format(self.open_price, self.volume, self.status)

    def open(self, datetime, price, volume):
        self.status = "OPEN"
        self.open_price = price
        self.volume = volume
        self.open_datetime = datetime

        return self.volume * self.open_price

    def close(self, datetime, price):
        self.status = "CLOSE"
        self.close_price = price
        self.close_datetime = datetime

        return self.volume * self.close_price

    def get_profit(self):
        return self.volume * (self.close_price - self.open_price)


class BTException(Exception):
    pass


class BT:
    def __init__(self, datas, balance=1000.0):
        if not isinstance(datas, list):
            raise BTException("datas argument should be list")
        self.datas = datas
        self.balance = balance
        self.start_balance = balance
        self.position = None
        self.trades = []

    def buy(self, price, shares_volume):
        trade = Trade()
        ds = self.datas[0]
        dt = ds[0].datetime
        self.balance -= trade.open(dt, price, shares_volume)
        self.trades.append(trade)
        self.position = trade
        logger.info(f"[BUY] {shares_volume=} {price=} @ {dt} => balance={self.balance:.2f}")

    def sell(self, price):
        ds = self.datas[0]
        dt = ds[0].datetime
        profit = self.position.close(dt, price)
        self.balance += profit
        self.position = None
        logger.info(f"[SELL] {profit=:.2f} {price=} @ {dt} => balance={self.balance:.2f}")

    def process_bar(self):
        pass

    def get_profit(self):
        return self.balance - self.start_balance

    def get_roi(self):
        return 1.0 * self.get_profit() / self.start_balance

    def go(self):
        return [d.next() for d in self.datas]

    def run(self):
        while not self.datas[0].is_end():
            self.process_bar()
            [d.next() for d in self.datas]

    def plot(self):  # pragma: no cover
        for d in self.datas:
            data = d.data
            data.set_index("datetime", inplace=True)
            headers = ["close"]
            outline_indicators = []
            outline_data = {}
            for ind in d.indicators:
                if ind.draw_inline:
                    headers.append(ind.title)
                else:
                    outline_indicators.append(ind)
                    outline_data[ind.title] = data[ind.title]
                    data.drop(ind.title, inplace=True, axis=1)

            data = data[headers]
            nrows = len(outline_indicators) + 1
            fig, axes = plt.subplots(nrows=nrows, ncols=1)

            data.plot(ax=axes, sharex=True)

            for i, oi in enumerate(outline_indicators):
                outline_data[oi.title].plot(ax=axes[i + 1], sharex=True)
                oi.draw_extra_charts(axes[i + 1])

        trade_open_datetimes = [trade.open_datetime for trade in self.trades]
        trade_open_prices = [trade.open_price for trade in self.trades]
        plt.plot(trade_open_datetimes, trade_open_prices, "g^")

        trade_close_datetimes = [trade.close_datetime for trade in self.trades]
        trade_close_prices = [trade.close_price for trade in self.trades]
        plt.plot(trade_close_datetimes, trade_close_prices, "rv")

        plt.show()
