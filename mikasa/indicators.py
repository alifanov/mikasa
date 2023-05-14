class BaseIndicator:
    def __init__(self, title="", draw_inline=True):
        self.title = title
        self.draw_inline = draw_inline

    def draw_extra_charts(self, *args, **kwargs):  # pragma: no cover
        pass


class SMAIndicator(BaseIndicator):
    def __init__(self, period, title="sma"):
        super(SMAIndicator, self).__init__(title)
        self.period = period

    def get_data(self, df, field_name):
        ds = df[field_name]
        return ds.rolling(center=False, window=self.period).mean()


class MomentumIndicator(BaseIndicator):
    def __init__(self, period=14, title="momentum"):
        super(MomentumIndicator, self).__init__(title)
        self.period = period

    def get_data(self, df, field_name):
        shifted = df[field_name].shift(-self.period)
        return 100.0 * df[field_name] / shifted


class RSIIndicator(BaseIndicator):
    def __init__(self, period=14, title="rsi"):
        super(RSIIndicator, self).__init__(title, draw_inline=False)
        self.period = period

    def draw_extra_charts(self, axe):  # pragma: no cover
        axe.axhline(y=20, xmin=0, xmax=1, c="red", zorder=0, linewidth=1)
        axe.axhline(y=80, xmin=0, xmax=1, c="green", zorder=0, linewidth=1)

    def get_data(self, df, field_name):
        ds = df[field_name]
        delta = ds.diff()
        d_up, d_down = delta.copy(), delta.copy()
        d_up[d_up < 0] = 0
        d_down[d_down > 0] = 0

        rol_up = d_up.rolling(center=False, window=self.period).mean()
        rol_down = d_down.rolling(center=False, window=self.period).mean().abs()

        rs = rol_up / rol_down
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi


class EMAIndicator(BaseIndicator):
    def __init__(self, period=14, title="ema"):
        super(EMAIndicator, self).__init__(title)
        self.period = period

    def get_data(self, df, field_name):
        return df["{}_{}_ema".format(field_name, self.period)]


class MACDIndicator(BaseIndicator):
    def __init__(self, short_period=12, long_period=26, signal_period=9, title="macd"):
        super(MACDIndicator, self).__init__(title, draw_inline=False)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
        self.draw_inline = False

    def draw_extra_charts(self, axe):  # pragma: no cover
        axe.axhline(y=0, xmin=0, xmax=1, c="red", zorder=0, linewidth=1)

    def get_data(self, df, field_name):
        short_ema = df[field_name].ewm(span=self.short_period, adjust=False).mean()
        long_ema = df[field_name].ewm(span=self.long_period, adjust=False).mean()
        macd = short_ema - long_ema
        signal_line = macd.ewm(span=self.signal_period, adjust=False).mean()

        result = macd - signal_line
        return result
