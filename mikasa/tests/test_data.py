import pandas as pd

from ..data import DataPoint, DataSeries
from unittest import TestCase

from .dataset import TEST_DATASET


class DataTestCase(TestCase):
    def test_datapoint(self):
        dp = DataPoint({'foo': 'bar'})
        self.assertEqual(dp.foo, 'bar')

    def test_dataseries(self):
        df = pd.DataFrame(TEST_DATASET).rename(columns={
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
        })
        ds = DataSeries(df)
        self.assertEqual(ds.index, 0)

        self.assertEqual(ds[0].close, 1.5)
        self.assertEqual(ds.get_dot(0)['close'], 1.5)

        next(ds)
        self.assertEqual(ds.index, 1)
        next(ds)
        self.assertEqual(ds.index, 2)
        self.assertEqual(ds.is_end(), True)
