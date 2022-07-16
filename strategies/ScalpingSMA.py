from pandas import DataFrame
from functools import reduce

import talib.abstract as ta

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter, 
                                IStrategy, IntParameter)
import freqtrade.vendor.qtpylib.indicators as qtpylib

class ScalpingSMA(IStrategy):
    INTERFACE_VERSION = 2
    timeframe = '1m'
    # ROI table:
    # ROI table:
    # ROI table:
    minimal_roi = {
        "0": 0.067,
        "6": 0.026,
        "13": 0.007,
        "30": 0
    }

    # Stoploss:
    stoploss = -0.228

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.048
    trailing_stop_positive_offset = 0.136
    trailing_only_offset_is_reached = False


    # Hyperoptable parameters
    buy_rsi = IntParameter(low=20, high=45, default=22, space='buy', optimize=True, load=True)
    buy_rsi_enabled = CategoricalParameter([True, False], default=False, space="buy")
    sell_rsi = IntParameter(low=65, high=90, default=86, space='sell', optimize=True, load=True)
    sell_rsi_enabled = CategoricalParameter([True, False], default=False, space="sell")

    # Optimal timeframe for the strategy.
    timeframe = '1m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = False
    sell_profit_only = False
    ignore_roi_if_buy_signal = False
   
    
    buy_sma_short = IntParameter(3, 9, default=7)
    buy_sma_medium = IntParameter(6, 10, default=8)
    buy_sma_long = IntParameter(10, 18, default=17)
    # buy_sma_short = IntParameter(5, 20, default=9)
    # buy_sma_medium = IntParameter(10, 30, default=21)
    # buy_sma_long = IntParameter(25, 40, default=30)
    buy_ema = IntParameter(10, 30, default=14)
    sell_ema = IntParameter(10, 30, default=13)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # Calculate all ema_short values
        # for val in self.buy_rsi.range:
        #     dataframe[f'buy_rsi_{val}'] = ta.RSI(dataframe, timeperiod=val)
        # for val in self.sell_rsi.range:
        #     dataframe[f'sell_rsi_{val}'] = ta.RSI(dataframe, timeperiod=val)
        for val in self.buy_ema.range:
            dataframe[f'buy_ema_{val}'] = ta.EMA(dataframe, timeperiod=val)
        for val in self.buy_ema.range:
            dataframe[f'buy_ema_{val}'] = ta.EMA(dataframe, timeperiod=val)
        for val in self.sell_ema.range:
            dataframe[f'sell_ema_{val}'] = ta.EMA(dataframe, timeperiod=val)
        for val in self.buy_sma_short.range:
            dataframe[f'sma_short_{val}'] = ta.SMA(dataframe, timeperiod=val)
        for val in self.buy_sma_short.range:
            dataframe[f'sma_short_{val}'] = ta.SMA(dataframe, timeperiod=val)
        for val in self.buy_sma_medium.range:
            dataframe[f'sma_medium_{val}'] = ta.SMA(dataframe, timeperiod=val)
        for val in self.buy_sma_long.range:
            dataframe[f'sma_long_{val}'] = ta.SMA(dataframe, timeperiod=val)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        
        # if self.buy_rsi_enabled.value:
        #     conditions.append(dataframe[f'buy_rsi_{self.buy_rsi.value}'] > self.buy_rsi.value)
        conditions.append(qtpylib.crossed_above(
                dataframe['close'], dataframe[f'buy_ema_{self.buy_ema.value}'], 
            ))
        conditions.append(qtpylib.crossed_above(
                dataframe[f'sma_short_{self.buy_sma_short.value}'], dataframe[f'sma_medium_{self.buy_sma_medium.value}']
            ))
        conditions.append(qtpylib.crossed_above(
                dataframe[f'sma_short_{self.buy_sma_short.value}'], dataframe[f'sma_long_{self.buy_sma_long.value}']
            ))
         
        # Check that volume is not 0
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # if self.sell_rsi_enabled.value:
        #     conditions.append(dataframe[f'sell_rsi_{self.sell_rsi.value}'] > self.buy_rsi.value)
        conditions.append(qtpylib.crossed_above(
                dataframe[f'sell_ema_{self.sell_ema.value}'], dataframe['close']
            ))
        conditions.append(qtpylib.crossed_above(
                dataframe[f'sma_medium_{self.buy_sma_medium.value}'], dataframe[f'sma_short_{self.buy_sma_short.value}']
            ))
        conditions.append(qtpylib.crossed_above(
                dataframe[f'sma_long_{self.buy_sma_long.value}'], dataframe[f'sma_short_{self.buy_sma_short.value}']
            ))
        
        # Check that volume is not 0
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'] = 1
        return dataframe
