import logging

import numpy as np
import pandas as pd

from mikasa import BT, DataSeries, MACDIndicator
import ccxt

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
exchange = ccxt.binance()


# create strategy for backtesting
class MACDBT(BT):
    trade_amount = 0.005

    def prepare_data(self):
        macd_indicator = MACDIndicator()
        self.dataseries.add_indicators(
            [
                macd_indicator,
            ]
        )

    # set up how to process each bar
    def process_bar(self):
        d = self.dataseries
        if np.isnan(d[0].macd):
            return
        if d[0].macd > 0 and d[-1].macd < 0:
            self.buy(d[0].close, self.get_trade_amount())
        elif d[0].macd < 0 and d[-1].macd > 0:
            self.sell(d[0].close)


if __name__ == "__main__":
    # upload and map data from CSV
    ohlcv = exchange.fetch_ohlcv("BTC/USDT", timeframe="1d", limit=100)

    df = pd.DataFrame(ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

    # create DataSeries instance
    ds = DataSeries(df)

    # create instance of BT and set params
    bt = MACDBT(ds, balance=1000.0)

    # run backtesting
    bt.run()
    logger.info(f"Profit: ${bt.get_profit():.2f}")
    logger.info(f"ROI: ${bt.get_roi()*100:.2f}%")

    # plot data and indicators
    bt.plot()
