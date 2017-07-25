import pandas as pd

from unittest import TestCase
from .dataset import TEST_DATASET
from ..data import DataSeries
from ..indicators import SMAIndicator


class IndicatorTestCase(TestCase):
    def test_sma(self):
        df = pd.DataFrame(TEST_DATASET).rename(columns={
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
        })
        ds = DataSeries(df)
        ind = SMAIndicator(2)
        self.assertEqual(ind.title, 'sma')
        ds.add_indicator(ind)
        self.assertEqual(ds[1].sma, 2.0)