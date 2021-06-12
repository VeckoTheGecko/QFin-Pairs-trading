# This file was created by `lean create "ProjectName"``
import numpy as np
import pandas as pd

from QuantConnect import Resolution
from QuantConnect.Algorithm import QCAlgorithm

# Overall Strategy
# - prelim
#   - on pairs
#   - For now use EOG and COP

# - Initialization
#   - set short and long position both to False
#   - Load symbols of pairs

# - On every minute (or 5 minutes or whatever)
#   - Preliminary Calculations:
#       - Get history
#       - Average data over 5 minute bins
#       - Calculate moving average and standard deviation
#       - Compare difference between two stock prices to avg
#           - Difference is defined to be EOG - COP
#           - Calculate z-score: (price_difference - mean_difference)/std_dev_difference
#           - z-score is equivalent to finding how many SDs from the mean a datapoint is
# 
#   - Purchasing Decisions
#       - If difference is more than 2 SD from mean
#           - Buy stock if not already bought
#               - Calc (price of EOG/price of COP)
#                   - For each EOG stock bought/sold, sell/buy (EOG/COP) COP stocks
#   
#               - If z-score is positive
#                   - Short EOG long COP
#   
#               - If z-score is negative
#                   - Short COP long EOG
# 
#       - Otherwise (less than 2 SD from mean)
#           - Liquidate all stock if already bought
# 
#       - Otherwise do nothing...
# 
#   - Filtering Pairs:
#       - Trade those with low least squares regression

# - Constants
#   - 

# - Principles
#   - Calculating Buy/Sell Amount:
#       - When taking a long and short position: both should have the same monetary value
#       - e.g. if COP is valued at $2/share and EOG is worth $6/share then buy 3 COP and sell 1 EOG
# 
#   - Liquidating:
#       - Get amount owned of every stock to 0



class PairsTrader(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2021, 4, 2)   # Set Start Date
        self.SetCash(100000)            # Set Strategy Cash

        self.past_intervals = 120   # Careful of bugs
        self.bin_size       = 5
        self.z_threshold    = 2.0

        self.iterations     = -1

        self.pairs = (
            ('BKR','OKE'),
            ('CVX','XOM'),
            ('CVX','PXD'),
            ('COP','FANG'),
            ('COP','EOG'),
            ('COP','HAL'),
            ('COP','PXD'),
            ('FANG','XOM'),
            ('FANG','HAL'),
            ('FANG','PXD'),
            ('EOG','XOM'),
            ('EOG','HAL'),
            ('EOG','HES'),
            ('EOG','NOV'),
            ('EOG','OXY'),
            ('EOG','OKE'),
            ('EOG','PSX'),
            ('EOG','SLB'),
            ('XOM','PXD'),
            ('HAL','PXD'),
            ('HFC','VLO'),
            ('MPC','PSX'),
            ('MPC','VLO'),
            ('NOV','OKE'),
            ('NOV','SLB'),
            ('OXY','PXD'),
            ('PXD','VLO')
        )

        for symbol in self.unique_symbols(self.pairs):
            self.AddEquity(symbol, Resolution.Minute)

        price_map = self.history_map(self.pairs)
        self.pairs = sorted(self.pairs, key=lambda pair: self.least_squares_residuals(pair[0], pair[1], price_map))[:4]

    def stock_history(self, symbols):
        return self.History(symbols, self.past_intervals*self.bin_size, Resolution.Minute)

    def unique_symbols(self, pairs):
        '''
        Returns a list of unique symbols
        Avoids getting the history of the same element multiple times
        Tested
        '''
        symbols = set()
        [[symbols.add(symbol) for symbol in pair] for pair in pairs]
        return list(symbols)

    def history_map(self, pairs):
        '''
        Returns a map from symbols to arrays of the close prices
        '''
        symbols = self.unique_symbols(pairs)
        histories = self.stock_history(symbols)

        hist_map = {}

        for symbol in symbols:
            minute_arr = np.array(histories["close"].loc[symbol])
            average_arr = np.mean(minute_arr.reshape(-1, self.bin_size), axis=1)
            hist_map[symbol] = average_arr

        return hist_map

    def get_trading_pairs(self):
        return self.pairs

    def least_squares_residuals(self, stock1, stock2, price_map):
        '''
        Stole this from quantconnect -- it's calculating their square residuals
        '''
        prices1 = price_map[stock1]
        prices2 = price_map[stock2]

        norm1 = np.array(prices1)/prices1[0]
        norm2 = np.array(prices2)/prices2[0]

        diff = norm1 - norm2
        sq_diff = diff**2
        
        return np.sum(sq_diff)

    def get_z_score(self, stock1, stock2):
        difference = stock1 - stock2
        average = np.mean(difference)
        SD = np.std(difference)
        
        z = (difference[-1] - average) / SD
        return z


    def OnData(self, data):
        '''
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        self.iterations += 1
        if (self.iterations % (3 * self.bin_size)) != 0:
            return

        pairs = self.get_trading_pairs()
        histories = self.history_map(pairs)

        for pair in pairs:
            z_score = self.get_z_score(histories[pair[0]],histories[pair[1]])

            if abs(z_score) > self.z_threshold:
                if not self.Portfolio.Invested:
                    
                    # Need to determine buy ratio
                    if z_score > 0.0:
                        self.Sell(pair[0],1)
                        self.Buy(pair[1], 1)
                    else:
                        self.Sell(pair[1],1)
                        self.Buy(pair[0], 1)
            else:
                if self.Portfolio.Invested:
                    self.Liquidate(pair[0])
                    self.Liquidate(pair[1])
        
        # self.Quit()


# Pairs list:
# BKR~OKE
# CVX~XOM
# CVX~PXD
# COP~FANG
# COP~EOG
# COP~HAL
# COP~PXD
# FANG~XOM
# FANG~HAL
# FANG~PXD
# EOG~XOM
# EOG~HAL
# EOG~HES
# EOG~NOV
# EOG~OXY
# EOG~OKE
# EOG~PSX
# EOG~SLB
# XOM~PXD
# HAL~PXD
# HFC~VLO
# MPC~PSX
# MPC~VLO
# NOV~OKE
# NOV~SLB
# OXY~PXD
# PXD~VLO