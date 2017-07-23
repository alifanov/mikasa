from stockstats import StockDataFrame


class DataPoint:
    def __init__(self, dt):
        self.dt = dt

    def __getattr__(self, key):
        return self.dt[key]


class DataSeries:
    def __init__(self, data, index=0):
        self.data = StockDataFrame.retype(data.copy())
        self.index = index
        self.indicators = []
        self.data.set_index('index')
        data_dict = self.data.to_dict(orient='split')
        self._data = data_dict['data']
        self._columns = data_dict['columns']

    def add_indicator(self, indicator):
        self.data[indicator.title] = indicator.get_data(self.data, 'close')
        self.indicators.append(indicator)
        data_dict = self.data.to_dict(orient='split')
        self._data = data_dict['data']
        self._columns = data_dict['columns']

    def get_dot(self, index):
        return {k: v for k,v in zip(self._columns, self._data[index])}

    def __getitem__(self, index):
        return DataPoint(self.get_dot(index + self.index))

    def __iter__(self):
        self.index = 0
        return self

    def is_end(self):
        return self.index == self.data.shape[0]

    def __next__(self):
        value = self.get_dot(self.index)
        self.index += 1
        if self.index >= self.data.shape[0]:
            raise StopIteration
        return DataPoint(value)


