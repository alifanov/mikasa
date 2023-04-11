from stockstats import StockDataFrame


class DataPoint:
    def __init__(self, dt):
        self.dt = dt

    def __getattr__(self, key):
        return self.dt[key]


class DataSeriesException(Exception):
    pass


class DataSeries:
    def __init__(self, data, index=0, indicators=None):
        self.data = StockDataFrame.retype(data.copy())
        self.index = index
        self.indicators = indicators
        if indicators is not None:
            for indicator in self.indicators:
                self.data[indicator.title] = indicator.get_data(self.data, "close")
        data_dict = self.data.to_dict(orient="split")
        self._data = [DataPoint({k: v for k, v in zip(data_dict["columns"], d)}) for d in data_dict["data"]]

    @property
    def length(self):
        return self.data.shape[0]

    def next(self):
        self.index += 1
        return self._data[self.index]

    def __getitem__(self, index):
        if (index + self.index) < 0:
            raise DataSeriesException(
                "Result index is negative. Inner index: {}. Parameter index: {}".format(self.index, index)
            )
        return self._data[index + self.index]

    def is_end(self):
        return self.index == (self.length - 1)
