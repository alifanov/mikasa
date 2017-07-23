# Mikasa

Simple backtesting tool

Project named after person of "Attack on Titan"

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
    def __init__(self, ds, balance, period):
        super(SMABT, self).__init__(ds, balance)
        # add indicator
        self.ds.add_indicator(SMAIndicator(period=period))

    # set up how to process each bar
    def process_bar(self):
        if not self.position:
            if self.ds[0].sma and self.ds[-1].close < self.ds[-1].sma:
                if self.ds[0].close > self.ds[0].sma:
                    self.buy(self.ds[0].close, 1000.0)
        else:
            if self.ds[0].sma and self.ds[-1].close > self.ds[-1].sma:
                if self.ds[0].close < self.ds[0].sma:
                    self.sell(self.ds[0].close)

# upload and map data from CSV
df = pd.read_csv('btc_etc.csv').rename(columns={
    'Close': 'close',
    'Date time': 'datetime',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Volume': 'volume'
})

# create DataSeriaes instance
ds = DataSeries(df)

# create instance of BT and set params
bt = SMABT(ds, balance=1000.0, period=200)

# run backtesting
bt.run()
print('Profit: ${:.2f}'.format(bt.get_profit()))
print('ROI: ${:.2%}'.format(bt.get_roi()))

# plot data and indicators
bt.plot()
```