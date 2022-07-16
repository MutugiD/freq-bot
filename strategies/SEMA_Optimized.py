from pandas import DataFrame
from functools import reduce

import talib.abstract as ta

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter, 
                                IStrategy, IntParameter)
import freqtrade.vendor.qtpylib.indicators as qtpylib

class SEMA_Opt(IStrategy):

    timeframe = '1m'
     
    
    # minimal_roi = {
    #     "0": 0.55,
    #     "335": 0.212,
    #     "772": 0.086,
    #     "2108": 0
    # }
    minimal_roi = {
        "0": 0.10,
        "20": 0.25,
        "40": 0.37,
        "80": 0.4
    }

    # Stoploss:
    stoploss = -0.50

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.107
    trailing_only_offset_is_reached = True

    # minimal_roi = {
    #     "0": 0.067,
    #     "8": 0.034,
    #     "20": 0.015,
    #     "43": 0
    # }

    # # Stoploss:
    # stoploss = -0.346

    # # Trailing stop:
    # trailing_stop = True
    # trailing_stop_positive = 0.045
    # trailing_stop_positive_offset = 0.113
    # trailing_only_offset_is_reached = True

    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

   # Buy parameter spaces
    buy_ema_short = IntParameter(3, 50, default=10)
    buy_ema_long = IntParameter(15, 200, default=175)
    buy_sma_short = IntParameter(3, 75, default=50)
    buy_sma_long = IntParameter(50, 200, default=200)

    sell_ema_short = IntParameter(3, 50, default=10)
    sell_ema_long = IntParameter(15, 200, default=175)
    sell_sma_short = IntParameter(3, 75, default=50)
    sell_sma_long = IntParameter(50, 200, default=200)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Generate all indicators used by the strategy"""

        # Calculate all ema_short values
        for val in self.buy_ema_short.range:
            dataframe[f'ema_short_{val}'] = ta.EMA(dataframe, timeperiod=val)
        for val in self.buy_sma_short.range:
            dataframe[f'sma_short_{val}'] = ta.SMA(dataframe, timeperiod=val)

        # Calculate all ema_long values
        for val in self.buy_ema_long.range:
            dataframe[f'ema_long_{val}'] = ta.EMA(dataframe, timeperiod=val)
        for val in self.buy_sma_long.range:
            dataframe[f'sma_long_{val}'] = ta.SMA(dataframe, timeperiod=val)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        conditions.append(dataframe[f'ema_long_{self.buy_ema_long.value}']> dataframe['close'])
        conditions.append(dataframe[f'ema_short_{self.buy_ema_short.value}'] > dataframe[f'sma_short_{self.buy_sma_short.value}'])
        conditions.append(dataframe[f'sma_short_{self.buy_sma_short.value}'] > dataframe[f'sma_long_{self.buy_sma_long.value}'])
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        conditions.append(dataframe[f'ema_long_{self.buy_ema_long.value}'] < dataframe['close'])
        conditions.append(dataframe[f'ema_short_{self.buy_ema_short.value}'] <  dataframe[f'sma_short_{self.buy_sma_short.value}'])
        conditions.append(dataframe[f'sma_short_{self.buy_sma_short.value}'] <  dataframe[f'sma_long_{self.buy_sma_long.value}'])
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'] = 1
        return dataframe
