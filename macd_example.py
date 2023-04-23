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
        if d[0].macd > 0 > d[-1].macd:
            self.buy(d[0].close, self.get_trade_amount())


class HyperSearch:
    result = []

    def get_best_run(self):
        best_run = sorted(self.result, key=lambda x: x[0])[-1]
        return best_run

    def get_params(self):
        return {
            "pair": ["BTC/USDT", "ETH/USDT"],
            "timeperiod": ["5m", "1h", "1d"],
            "macd": {"short_period": range(2, 12), "long_period": range(3, 30), "signal_period": range(4, 16)},
        }

    def run(self):
        params = self.get_params()
        for pair in params["pair"]:
            for timeperiod in params["timeperiod"]:
                ohlcv = exchange.fetch_ohlcv(pair, timeframe=timeperiod, limit=300)

                df = pd.DataFrame(ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"])
                df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

                macd_params = params["macd"]

                # create DataSeries instance
                for short_period in macd_params["short_period"]:
                    for long_period in macd_params["long_period"]:
                        for signal_period in macd_params["signal_period"]:
                            logger.info(
                                f"Backtesting params: {pair=} {timeperiod=}"
                                f" {short_period=} {long_period=} {signal_period=}"
                            )

                            # create instance of BT and set params
                            class HSMACDBT(MACDBT):
                                def prepare_data(self):
                                    macd_indicator = MACDIndicator(
                                        short_period=short_period,
                                        long_period=long_period,
                                        signal_period=signal_period,
                                    )
                                    self.dataseries.add_indicators(
                                        [
                                            macd_indicator,
                                        ]
                                    )

                            ds = DataSeries(df)
                            bt = HSMACDBT(ds, balance=1000.0, verbose=False)

                            # run backtesting
                            bt.run()
                            logger.info(f"Profit: ${bt.get_profit():.2f}")
                            logger.info(f"ROI: ${bt.get_roi() * 100:.2f}%")

                            self.result.append(
                                (
                                    bt.get_roi(),
                                    bt.get_profit(),
                                    {
                                        "pair": pair,
                                        "timeperiod": timeperiod,
                                        "macd": {
                                            "short_period": short_period,
                                            "long_period": long_period,
                                            "signal_period": signal_period,
                                        },
                                    },
                                )
                            )


if __name__ == "__main__":
    hyper_search = HyperSearch()
    hyper_search.run()
    best_run = hyper_search.get_best_run()
    logger.info(f"Best run: profit={best_run[1]:.2f}")
    logger.info(f"Best run: ROI={best_run[0] * 100.:.2f}")
    best_params = best_run[2]
    logger.info(f"Best params: {best_run=}")

    macd_best_params = best_params["macd"]
    short_period = macd_best_params["short_period"]
    long_period = macd_best_params["long_period"]
    signal_period = macd_best_params["signal_period"]

    # upload and map data from CSV
    ohlcv = exchange.fetch_ohlcv(best_params["pair"], timeframe=best_params["timeperiod"], limit=300)

    df = pd.DataFrame(ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

    # create DataSeries instance
    ds = DataSeries(df)

    # create instance of BT and set params
    class BestMACDBT(MACDBT):
        def prepare_data(self):
            macd_indicator = MACDIndicator(
                short_period=short_period,
                long_period=long_period,
                signal_period=signal_period,
            )
            self.dataseries.add_indicators(
                [
                    macd_indicator,
                ]
            )

    bt = BestMACDBT(ds, balance=1000.0)

    # run backtesting
    bt.run()
    logger.info(f"Profit: ${bt.get_profit():.2f}")
    logger.info(f"ROI: ${bt.get_roi()*100:.2f}%")

    # plot data and indicators
    bt.plot(title=f'{best_params["pair"]} ({best_params["timeperiod"]})')
