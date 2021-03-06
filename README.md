[![CircleCI](https://circleci.com/gh/alifanov/mikasa/tree/master.svg?style=shield)](https://circleci.com/gh/alifanov/mikasa/tree/master)

[![Code Climate](https://codeclimate.com/github/alifanov/mikasa/badges/gpa.svg)](https://codeclimate.com/github/alifanov/mikasa)

# Mikasa

Simple backtesting tool

## Installation

```python
pip install git+https://github.com/alifanov/mikasa.git
```

## Usage

```python
import pandas as pd
from mikasa import BT, DataSeries, SMAIndicator

# create strategy for backtesting
class SMABT(BT):
    # set up how to process each bar
    def process_bar(self):
        d = self.datas[0]
        if not self.position:
            if d[0].sma and d[-1].close < d[-1].sma:
                if d[0].close > d[0].sma:
                    self.buy(d[0].close, 500.0)
        else:
            if d[0].sma and d[-1].close > d[-1].sma:
                if d[0].close < d[0].sma:
                    self.sell(d[0].close)

# upload and map data from CSV
df = pd.read_csv('btc_etc.csv').rename(columns={
    'Close': 'close',
    'Date time': 'datetime',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Volume': 'volume'
})

# create DataSeries instance
ds = DataSeries(df, indicators=[
    SMAIndicator(period=200)
])

# create instance of BT and set params
bt = SMABT([ds], balance=1000.0)

# run backtesting
bt.run()
print('Profit: ${:.2f}'.format(bt.get_profit()))
print('ROI: ${:.2%}'.format(bt.get_roi()))

# plot data and indicators
bt.plot()
```