import logging

import numpy as np
import pandas as pd

from mikasa import BT, DataSeries, SMAIndicator
import ccxt

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
exchange = ccxt.binance()


# create strategy for backtesting
class SMABT(BT):
    # set up how to process each bar
    def process_bar(self):
        d = self.datas[0]
        if np.isnan(d[0].sma):
            return
        if not self.position:
            if d[-1].close < d[-1].sma:
                if d[0].close > d[0].sma:
                    self.buy(d[0].close, 0.001)
        else:
            if d[-1].close > d[-1].sma:
                if d[0].close < d[0].sma:
                    self.sell(d[0].close)


if __name__ == "__main__":
    # upload and map data from CSV
    ohlcv = exchange.fetch_ohlcv("BTC/USDT", timeframe="1d", limit=1000)

    df = pd.DataFrame(ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

    # create DataSeries instance
    ds = DataSeries(df, indicators=[SMAIndicator(period=100)])

    # create instance of BT and set params
    bt = SMABT([ds], balance=1000.0)

    # run backtesting
    bt.run()
    logger.info(f"Profit: ${bt.get_profit():.2f}")
    logger.info(f"ROI: ${bt.get_roi()*100:.2f}%")

    # plot data and indicators
    bt.plot()
