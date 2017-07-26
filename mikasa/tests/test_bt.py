import pandas as pd

from unittest import TestCase
from .dataset import TEST_DATASET
from ..data import DataSeries
from ..bt import Trade, BT


class TradeTestCase(TestCase):
    def test_trade(self):
        t = Trade()
        t.open('2017-01-01', 100.0, 1.0)
        self.assertEqual(t.status, 'OPEN')
        self.assertEqual(t.volume, 1.0)
        self.assertEqual(t.open_price, 100.0)
        self.assertEqual(t.open_datetime, '2017-01-01')

        t.close('2017-01-02', 200.0)
        self.assertEqual(t.status, 'CLOSE')
        self.assertEqual(t.close_datetime, '2017-01-02')
        self.assertEqual(t.close_price, 200.0)
        self.assertEqual(t.get_profit(), 100.0)


class BTTestCase(TestCase):
    def test_bt(self):
        df = pd.DataFrame(TEST_DATASET).rename(columns={
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
        })
        ds = DataSeries(df)
        bt = BT(ds, balance=1.0)
        self.assertEqual(bt.balance, 1.0)

        bt.buy(ds[0].close, 1.0)
        self.assertIsNotNone(bt.position)

        bt.go()
        bt.sell(ds[0].close)
        self.assertIsNone(bt.position)
        self.assertEqual(bt.get_profit(), 1.0)
        self.assertEqual(bt.get_roi(), 1.0)

    def test_bt_strat(self):
        class SimpleBT(BT):
            def process_bar(self):
                if self.ds[0].close == 1.5:
                    if not self.position:
                        self.buy(self.ds[0].close, 1.0)
                if self.ds[0].close == 2.5:
                    if self.position:
                        self.sell(self.ds[0].close)

        df = pd.DataFrame(TEST_DATASET).rename(columns={
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
        })
        ds = DataSeries(df)
        bt = SimpleBT(ds, balance=1.0)
        bt.run()

        self.assertIsNone(bt.position)
        self.assertEqual(bt.get_profit(), 1.0)
        self.assertEqual(bt.get_roi(), 1.0)