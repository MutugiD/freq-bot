# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class TrialStrategy(IStrategy):


    INTERFACE_VERSION = 2
    minimal_roi = {
      "60": 0.75,
     "40": 0.50,
     "20": 0.25,
     "0": 0.10
     }
     
 
    stoploss = -0.064

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Hyperoptable parameters
    buy_rsi = IntParameter(low=1, high=50, default=40, space='buy', optimize=True, load=True)
    sell_rsi = IntParameter(low=50, high=100, default=85, space='sell', optimize=True, load=True)

    # Optimal timeframe for the strategy.
    timeframe = '1m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
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
     

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        # EMA - Exponential Moving Average
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

        # SMA - Simple Moving Average
        dataframe['sma10'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['sma100'] = ta.SMA(dataframe, timeperiod=100)
        dataframe['sma200'] = ta.SMA(dataframe, timeperiod=200)

 
        # TEMA - Triple Exponential Moving Average
        dataframe['tema'] = ta.TEMA(dataframe, timeperiod=9)

        #BB
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
       
        """
        dataframe.loc[
            (
                # Signal: RSI crosses above 30
                (dataframe['close'].shift(1) > dataframe['ema200'].shift(1)) &
                (qtpylib.crossed_above(dataframe['rsi'], self.buy_rsi.value))  &
                (dataframe['ema50'].shift(1) > dataframe['sma100'].shift(1)) &  
                (dataframe['sma100'].shift(1) > dataframe['sma200'].shift(1)) & 
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        """
        dataframe.loc[
            (
                # Signal: RSI crosses above 85
                (dataframe['close'].shift(1) > dataframe['ema200'].shift(1)) &
                (dataframe['ema50'].shift(1) < dataframe['sma100'].shift(1)) &  
                (qtpylib.crossed_above(dataframe['rsi'], self.sell_rsi.value)) &
                (dataframe['sma50'].shift(1)  <  dataframe['sma200'].shift(1)) & 
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'sell'] = 1
        return dataframe
