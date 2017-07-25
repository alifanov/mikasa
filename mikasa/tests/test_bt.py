import pandas as pd

from unittest import TestCase
from .dataset import TEST_DATASET
from ..data import DataSeries
from ..bt import Trade


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