import pytest

import pandas as pd

from ..data import DataPoint, DataSeries, DataSeriesException
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
            'Volume': 'volume',
        })
        ds = DataSeries(df)
        self.assertEqual(ds.index, 0)
        self.assertEqual(ds.length, 3)

        self.assertEqual(ds[0].close, 1.5)

        ds.next()
        self.assertEqual(ds.index, 1)

        ds.next()
        self.assertEqual(ds.index, 2)
        self.assertEqual(ds.is_end(), True)

        self.assertEqual(ds[-2].close, 1.5)

        with pytest.raises(DataSeriesException):
            ds[-3]