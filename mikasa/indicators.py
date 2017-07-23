class BaseIndicator:
    def __init__(self, title='', draw_inline=True):
        self.title = title
        self.draw_inline = draw_inline

    def draw_extra_charts(self, *args, **kwargs):
        pass


class SMAIndicator(BaseIndicator):
    def __init__(self, period, title='sma'):
        super(SMAIndicator, self).__init__(title)
        self.period = period

    def get_data(self, df, field_name):
        ds = df[field_name]
        return ds.rolling(center=False, window=self.period).mean()


class MomentumIndicator(BaseIndicator):
    def __init__(self, period=14, title='momentum'):
        super(MomentumIndicator, self).__init__(title)
        self.period = period

    def get_data(self, df, field_name):
        ds = df[field_name]
        if len(ds) > self.period - 1:
            return ds[-1] * 100 / ds[-self.period]
        return None


class RSIIndicator(BaseIndicator):
    def __init__(self, period=14, title='rsi'):
        super(RSIIndicator, self).__init__(title, draw_inline=False)
        self.period = period

    def draw_extra_charts(self, axe):
        axe.axhline(y=20, xmin=0, xmax=1, c='red', zorder=0, linewidth=1)
        axe.axhline(y=80, xmin=0, xmax=1, c='green', zorder=0, linewidth=1)

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
    def __init__(self, period, title='ema'):
        super(EMAIndicator, self).__init__(title)
        self.period = period

    def get_data(self, df, field_name):
        return df['{}_{}_ema'.format(field_name, self.period)]


