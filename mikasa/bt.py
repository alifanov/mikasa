import matplotlib.pyplot as plt


class Trade:
    status = 'OPEN'
    open_price = None
    close_price = None
    volume = None
    open_datetime = None
    close_datetime = None

    def __repr__(self): # pragma: no cover
        return 'Price: {} Volume: {} Status: {}'.format(self.open_price, self.volume, self.status)

    def open(self, datetime, price, volume):
        self.status = 'OPEN'
        self.open_price = price
        self.volume = volume
        self.open_datetime = datetime

    def close(self, datetime, price):
        self.status = 'CLOSE'
        self.close_price = price
        self.close_datetime = datetime

    def get_profit(self):
        return self.volume * (self.close_price - self.open_price)


class BT:
    def __init__(self, ds, balance=1000.0):
        self.ds = ds
        self.balance = balance
        self.start_balance = balance
        self.end_balance = balance
        self.position = None
        self.trades = []

    def buy(self, price, shares_volume):
        trade = Trade()
        trade.open(self.ds.index, price, shares_volume)
        self.trades.append(trade)
        self.position = trade

    def sell(self, price):
        self.position.close(self.ds.index, price)
        self.balance += self.position.get_profit()
        self.position = None

    def process_bar(self):
        pass

    def get_profit(self):
        return self.balance - self.start_balance

    def get_roi(self):
        return 1.0 * self.get_profit() / self.start_balance

    def go(self):
        return self.ds.next()

    def run(self):
        while not self.ds.is_end():
            self.process_bar()
            self.ds.next()

    def plot(self): # pragma: no cover
        data = self.ds.data
        data = data.set_index('datetime')
        headers = ['close']
        outline_indicators = []
        outline_data = {}
        for ind in self.ds.indicators:
            if ind.draw_inline:
                headers.append(ind.title)
            else:
                outline_indicators.append(ind)
                outline_data[ind.title] = data[ind.title]
                data.drop(ind.title, inplace=True, axis=1)

        data = data[headers]
        fig, axes = plt.subplots(nrows=len(outline_indicators) + 1, ncols=1)
        data.plot(ax=axes[0], sharex=True)
        for i, oi in enumerate(outline_indicators):
            outline_data[oi.title].plot(ax=axes[i + 1], sharex=True)
            oi.draw_extra_charts(axes[i + 1])

        # data.plot(marker='o', markersize=4)

        trade_open_datetimes = [trade.open_datetime for trade in self.trades]
        trade_open_prices = [trade.open_price for trade in self.trades]
        plt.plot(trade_open_datetimes, trade_open_prices, 'g^')

        trade_close_datetimes = [trade.close_datetime for trade in self.trades]
        trade_close_prices = [trade.close_price for trade in self.trades]
        plt.plot(trade_close_datetimes, trade_close_prices, 'rv')

        plt.show()
