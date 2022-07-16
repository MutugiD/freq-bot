# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from functools import reduce

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class SEMA_NonOpt(IStrategy):


    INTERFACE_VERSION = 2
     
    # ROI table:
    minimal_roi = {
        "0": 0.441,
        "448": 0.182,
        "1011": 0.066,
        "2385": 0
    }

    # Stoploss:
    stoploss = -0.6  # value loaded from strategy

    # Trailing stop:
    trailing_stop = True  # value loaded from strategy
    trailing_stop_positive = 0.293  # value loaded from strategy

    # Buy Hyperoptable parameters
    buy_ema_short = IntParameter(10, 50, default=21)
    buy_ema_long = IntParameter(20, 200, default=100)
    buy_sma_short = IntParameter(10, 120, default=100)
    buy_sma_long = IntParameter(100, 200, default=200)


    #Sell Hyperoptable parameters
    sell_ema_short = IntParameter(10, 50, default=21)
    sell_ema_long = IntParameter(50, 200, default=100)
    sell_sma_short = IntParameter(10, 120, default=100)
    sell_sma_long = IntParameter(50, 200, default=200)

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = False
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    plot_config = {
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            "MACD": {
                'macd': {'color': 'blue'},
                'macdsignal': {'color': 'orange'},
            },
            "RSI": {
                'rsi': {'color': 'red'},
            }
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
     
        #buy indicators       
        dataframe['buy_ema_short'] = ta.EMA(dataframe, timeperiod=self.buy_ema_short.value)
        dataframe['buy_ema_long'] = ta.SMA(dataframe, timeperiod=self.buy_ema_long.value)
        dataframe['buy_sma_short'] = ta.EMA(dataframe, timeperiod=self.buy_sma_short.value)
        dataframe['buy_sma_long'] = ta.SMA(dataframe, timeperiod=self.buy_sma_long.value)
        #sell indicators 
        dataframe['sell_ema_short'] = ta.EMA(dataframe, timeperiod=self.sell_ema_short.value)
        dataframe['sell_ema_long'] = ta.SMA(dataframe, timeperiod=self.sell_ema_long.value)
        dataframe['sell_sma_short'] = ta.EMA(dataframe, timeperiod=self.sell_sma_short.value)
        dataframe['sell_sma_long'] = ta.SMA(dataframe, timeperiod=self.sell_sma_long.value)

        return dataframe
    
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
       
        """
        dataframe.loc[
            (  
                (dataframe['buy_ema_long']  > dataframe['close']) &
                (dataframe['buy_ema_short']  > dataframe['buy_sma_short'] ) &
                (dataframe['buy_sma_short']  > dataframe['buy_sma_long'] ) &
                (dataframe['volume'] > 0)  
            ),
             'buy'] = 1

        return dataframe
    
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    
        dataframe.loc[
            (
                (dataframe['sell_ema_long']  > dataframe['close']) &
                (dataframe['sell_ema_short']  < dataframe['sell_sma_short'] ) &
                (dataframe['sell_sma_short']  < dataframe['sell_sma_long'] ) &
                (dataframe['volume'] > 0)  
            ),
             'sell'] = 1
        return dataframe





