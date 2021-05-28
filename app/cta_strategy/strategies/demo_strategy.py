import pandas as pd
from typing import Any

pd.set_option('precision', 11)

from app.cta_strategy.template import (
    CtaTemplate
)

from trader.object import (
    BarData,
    TickData
)
from trader.utility import (
    BarGenerator,
    ArrayManager
)


class DemoStrategy(CtaTemplate):

    auther = "Demo Test"

    # 定义参数
    n = 20
    m = 1

    # 定义变量
    median1 = 0.0
    upper1 = 0.0
    lower1 = 0.0

    median2 = 0.0
    upper2 = 0.0
    lower2 = 0.0

    parameters = ["n"]

    dataframe = pd.DataFrame()

    variables = ["lower1", "median1", "upper1", "lower2", "median2", "upper2", 'dataframe']

    def __init__(self,
                 ct_engine: Any,
                 strategy_name: str,
                 vt_symbol: str,
                 setting: dict):
        super().__init__(ct_engine, strategy_name, vt_symbol, setting)

        # self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(500)

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(1) # 注意这里是获取最新k线的 天数

    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        # 更新  实盘的时候都需要tick合成
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        df = pd.DataFrame(am.close_array, columns=['close'], dtype=float)
        df['median'] = df['close'].rolling(self.n, min_periods=1).mean()
        df['std'] = df['close'].rolling(self.n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
        # df['z_score'] = abs(df['close'] - df['median']) / df['std']
        # df['m'] = df['z_score'].rolling(window=self.n).max().shift(1)

        # df['upper'] = df['median'] + df['m'] * df['std']
        # df['lower'] = df['median'] - df['m'] * df['std']
        df['upper'] = df['median'] + 2 * df['std']
        df['lower'] = df['median'] - 2 * df['std']

        self.median1 = df.iloc[-1]['median']
        self.median2 = df.iloc[-2]['median']

        self.upper1 = df.iloc[-1]['upper']
        self.upper2 = df.iloc[-2]['upper']

        self.lower1 = df.iloc[-1]['lower']
        self.lower2 = df.iloc[-2]['lower']

        self.dataframe = {
            'datetime': am.datetime_array,
            'open': am.open_array,
            'close': am.close_array,
            'high': am.high_array,
            'low': am.low_array,
            'upper': df['upper'].fillna(0).to_numpy(),
            'median': df['median'].fillna(0).to_numpy(),
            'lower': df['lower'].fillna(0).to_numpy()
        }

        close1 = df.iloc[-1]['close']
        close2 = df.iloc[-2]['close']

        condition1 = (close1 > self.upper1) and (close2 <= self.upper2)  # 开多
        condition2 = (close1 < self.lower1) and (close2 >= self.lower2)  # 开空

        condition3 = (close1 < self.median1) and (close2 >= self.median2)  # 平多
        condition4 = (close1 > self.median1) and (close2 <= self.median2)  # 平空

        if self.pos == 0:
            print("开多")
            self.buy(close1, 1)
        #     if condition1:
        #         self.buy(close1, 1)
        #     elif condition2:
        #         self.short(close1, 1)
        #
        # if self.pos > 0:
        #     if condition3:
        #         self.sell(close1, 1)
        #         if condition2:
        #             self.short(close1, 1)
        #
        # if self.pos < 0:
        #     if condition4:
        #         self.cover(close1, 1)
        #         if condition1:
        #             self.buy(close1, 1)

        # 更新图形界面
        self.put_event()

    def on_15min_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        df = pd.DataFrame(am.close_array, columns=['close'], dtype=float)
        df['median'] = df['close'].rolling(self.n, min_periods=1).mean()
        df['std'] = df['close'].rolling(self.n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
        df['z_score'] = abs(df['close'] - df['median']) / df['std']
        df['m'] = df['z_score'].rolling(window=self.n).max().shift(1)

        df['upper'] = df['median'] + df['m'] * df['std']
        df['lower'] = df['median'] - df['m'] * df['std']

        median1 = df.iloc[-1]['median']
        median2 = df.iloc[-2]['median']

        upper1 = df.iloc[-1]['upper']
        upper2 = df.iloc[-2]['upper']

        lower1 = df.iloc[-1]['lower']
        lower2 = df.iloc[-2]['lower']

        close1 = df.iloc[-1]['close']
        close2 = df.iloc[-2]['close']

        condition1 = (close1 > upper1) and (close2 <= upper2)  # 开多
        condition2 = (close1 < lower1) and (close2 >= lower2)  # 开空

        condition3 = (close1 < median1) and (close2 >= median2)  # 平多
        condition4 = (close1 > median1) and (close2 <= median2)  # 平空

        if self.pos == 0:
            if condition1:
                self.buy(close1, 1)
            elif condition2:
                self.short(close1, 1)

        if self.pos > 0:
            if condition3:
                self.sell(close1, 1)
                if condition2:
                    self.short(close1, 1)

        if self.pos < 0:
            if condition4:
                self.cover(close1, 1)
                if condition1:
                    self.buy(close1, 1)


        # 更新图形界面
        self.put_event()



