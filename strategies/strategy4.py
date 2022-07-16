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


class Strategy_4(IStrategy):
  
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Hyperoptable parameters
    buy_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)
    sell_rsi = IntParameter(low=50, high=100, default=70, space='sell', optimize=True, load=True)

    # Optimal timeframe for the strategy.
    timeframe = '5m'

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

    def informative_pairs(self):
  
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        # ADX
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['slowadx'] = ta.ADX(dataframe, 35)

        # Commodity Channel Index: values Oversold:<-100, Overbought:>100
        dataframe['cci'] = ta.CCI(dataframe)

        # Stoch
        stoch = ta.STOCHF(dataframe, 5)
        dataframe['fastd'] = stoch['fastd']
        dataframe['fastk'] = stoch['fastk']
        dataframe['fastk-previous'] = dataframe.fastk.shift(1)
        dataframe['fastd-previous'] = dataframe.fastd.shift(1)

        # Slow Stoch
        slowstoch = ta.STOCHF(dataframe, 50)
        dataframe['slowfastd'] = slowstoch['fastd']
        dataframe['slowfastk'] = slowstoch['fastk']
        dataframe['slowfastk-previous'] = dataframe.slowfastk.shift(1)
        dataframe['slowfastd-previous'] = dataframe.slowfastd.shift(1)

        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)

        dataframe['mean-volume'] = dataframe['volume'].mean()

        return dataframe

    # def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

    #     dataframe.loc[
    #         ( 
    #             (
                   
    #                 (dataframe['adx'] > 50| (dataframe['slowadx']>26)
    #             ) & 
    #             (dataframe['cci'] <-100) &
    #             (
    #                 (dataframe['fastk-previous'] < 20) & 
    #                 (dataframe['fastd-previous'] < 20)
    #             ) & 
    #                 (dataframe['slowfastk-previous'] < 30 ) &
    #                 (dataframe['slowfastd-previous'] < 30 )
    #             ) & 
    #             (dataframe['fastk-previous'] < dataframe['fastd-previous']) & 
    #             (dataframe['close'] > dataframe['ema5']
    #             (dataframe['mean-volume'] > 0.75)
    #         ), 

    #         'buy'] = 1

    #     return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            ( 
                               
                ((dataframe['adx'] > 50| (dataframe['slowadx']>26)) & 
             
                (dataframe['cci'] <-100) & 
                (
                    (dataframe['fastk-previous'] < 20) & 
                    (dataframe['fastd-previous'] < 20)
                ) & 
                    (dataframe['slowfastk-previous'] < 30 ) &
                    (dataframe['slowfastd-previous'] < 30 )
                ) & 
                (dataframe['fastk-previous'] < dataframe['fastd-previous']) &
                (dataframe['fastk'] > dataframe['fastd']) 
               
            ), 

            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            ( 
                (dataframe['slowadx'] < 25) &
                ((dataframe['fastk'] > 70) | dataframe['fastd'] > 70)) & 
                (dataframe['fastk-previous'] < (dataframe['fastd-previous']) &
                (dataframe['close'] > dataframe['ema5'])
            
            ), 

            'sell'] = 1

        return dataframe