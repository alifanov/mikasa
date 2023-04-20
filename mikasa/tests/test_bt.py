import pandas as pd

from unittest import TestCase
from .dataset import TEST_DATASET
from ..data import DataSeries
from ..bt import BT


class BTTestCase(TestCase):
    def test_bt(self):
        df = pd.DataFrame(TEST_DATASET).rename(
            columns={
                "Datetime": "datetime",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
            }
        )
        ds = DataSeries(df)

        bt = BT(ds, balance=1.5)
        self.assertEqual(bt.balance, 1.5)

        bt.process_bar()
        self.assertEqual(bt.balance, 1.5)

        bt.buy(ds[0].close, 1.0)
        self.assertIsNotNone(bt.fund)

        bt.go()
        bt.process_open_orders()
        bt.sell(ds[0].close)
        bt.go()
        bt.process_open_orders()
        self.assertEqual(bt.fund, 0)
        self.assertEqual(bt.get_profit(), 1.4985)
        self.assertEqual(bt.get_roi(), 0.999)

        self.assertEqual(bt.dataseries[0].close, 3.5)

    def test_bt_strat(self):
        class SimpleBT(BT):
            def process_bar(self):
                if self.dataseries[0].close == 1.5:
                    self.buy(self.dataseries[0].close, 1.0)
                if self.dataseries[0].close == 3.0:
                    self.sell(self.dataseries[0].close)

        df = pd.DataFrame(TEST_DATASET).rename(
            columns={
                "Datetime": "datetime",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
            }
        )
        ds = DataSeries(df)
        bt = SimpleBT(ds, balance=1.5)
        bt.run()

        self.assertEqual(bt.fund, 0)
        self.assertEqual(bt.get_profit(), 1.4985)
        self.assertEqual(bt.get_roi(), 0.999)
