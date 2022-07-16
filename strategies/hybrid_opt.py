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
class hybrid_opt(IStrategy):


    INTERFACE_VERSION = 2
    
    # ROI table:
    minimal_roi = {
        "0": 0.066,
        "8": 0.033,
        "18": 0.013,
        "42": 0
    }

    # Stoploss:
    stoploss = -0.344

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.034
    trailing_stop_positive_offset = 0.133
    trailing_only_offset_is_reached = True

    # Hyperoptable parameters
    buy_rsi = IntParameter(low=1, high=50, default=40, space='buy', optimize=True, load=True)
    buy_adx = DecimalParameter(20, 40, decimals=1, default=30.1, space="buy")
 
    #sell
    sell_adx = DecimalParameter(20, 40, decimals=1, default=30.1, space="sell")
    sell_rsi = IntParameter(low=50, high=100, default=85, space='sell', optimize=True, load=True)
   
    # Optimal timeframe for the strategy.
    timeframe = '1m'

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
        """
        Generate all indicators used by the strategy
        """
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)

        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['rsi'] = ta.RSI(dataframe)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        """
        dataframe.loc[
            (
            
                (dataframe['adx'] > self.buy_adx.value) & 
                (dataframe['rsi'] < self.buy_rsi.value) &  
                (dataframe['close'] < dataframe['bb_lowerband']) &
                #(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        """
        dataframe.loc[
            (
                (dataframe['adx'] < self.sell_adx.value) & 
                (dataframe['rsi'] > self.sell_rsi.value) &  
                (dataframe['close'] >  dataframe['bb_lowerband']) &
                #(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'sell'] = 1
        return dataframe
