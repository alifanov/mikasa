from stockstats import StockDataFrame


class DataPoint:
    def __init__(self, dt):
        self.dt = dt

    def __getattr__(self, key):
        return self.dt[key]


class DataSeriesException(Exception):
    pass


class DataSeries:
    def __init__(self, data, index=0):
        self.data = StockDataFrame.retype(data.copy())
        self.index = index
        self.indicators = []
        self.data.set_index('datetime')
        data_dict = self.data.to_dict(orient='split')
        self._data = data_dict['data']
        self._columns = data_dict['columns']

    def add_indicator(self, indicator):
        self.data[indicator.title] = indicator.get_data(self.data, 'close')
        self.indicators.append(indicator)
        data_dict = self.data.to_dict(orient='split')
        self._data = data_dict['data']
        self._columns = data_dict['columns']

    @property
    def length(self):
        return self.data.shape[0]

    def get_dot(self, index):
        return {k: v for k, v in zip(self._columns, self._data[index])}

    def next(self):
        self.index += 1
        return self._data[self.index]

    def __getitem__(self, index):
        if (index + self.index) < 0:
            raise DataSeriesException('Result index is negative. Inner index: {}. Parameter index: {}'.format(
                self.index,
                index
            ))
        return DataPoint(self.get_dot(index + self.index))

    def is_end(self):
        return self.index == (self.data.shape[0] - 1)