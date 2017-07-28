import pandas as pd

from unittest import TestCase
from .dataset import TEST_DATASET
from ..data import DataSeries
from ..indicators import SMAIndicator, RSIIndicator, EMAIndicator, MomentumIndicator


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
        sma = SMAIndicator(2)
        rsi = RSIIndicator(2)
        ema = EMAIndicator(2)
        mom = MomentumIndicator(2)
        self.assertEqual(sma.title, 'sma')
        ds.add_indicator(sma)
        ds.add_indicator(rsi)
        ds.add_indicator(ema)
        ds.add_indicator(mom)
        self.assertEqual(ds[1].sma, 2.0)