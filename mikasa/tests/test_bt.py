import pandas as pd

from unittest import TestCase, mock

import pytest

from mikasa import OrderType
from .dataset import TEST_DATASET
from ..data import DataSeries
from ..bt import BT


class BTTestCase(TestCase):
    def _get_bt(self):
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
        return bt

    def test_bt_trade_amount(self):
        bt = self._get_bt()
        with pytest.raises(ValueError):
            bt.get_trade_amount(None)
        self.assertEqual(bt.get_trade_amount(1.0), 0.015)
        bt.trade_amount = 0.001
        self.assertEqual(bt.get_trade_amount(1.0), 0.001)

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

        bt = BT(ds, balance=1.5, verbose=True)
        self.assertEqual(bt.balance, 1.5)

        bt.process_bar()
        self.assertEqual(bt.balance, 1.5)

        self.assertIsNone(bt.buy(100.0, 1.0))

        bt.buy(ds[0].close, 1.0)

        bt.go()
        bt.process_open_orders()
        self.assertIsNotNone(bt.fund)
        bt.sell(ds[0].close)
        bt.go()
        bt.process_open_orders()
        self.assertEqual(bt.fund, 0)
        self.assertEqual(bt.get_profit(), 1.4985)
        self.assertEqual(bt.get_roi(), 0.999)

        self.assertEqual(bt.dataseries[0].close, 3.5)

        buy_orders = [it for it in bt.order_history if it.type == OrderType.BUY]

        class MockedAxes:
            def plot(self, *args, **kwargs):
                pass

        ma = MockedAxes()
        ma.plot = mock.Mock()

        bt._draw_orders(buy_orders, marker="g^", ax=ma)
        ma.plot.assert_called()

    def test_bt_strategy(self):
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
