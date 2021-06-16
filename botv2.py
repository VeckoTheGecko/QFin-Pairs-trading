# https://quantpedia.com/Screener/Details/12

import numpy as np
import pandas as pd
from scipy import stats
from math import floor
from datetime import timedelta
from collections import deque
import itertools as it
from decimal import Decimal

import statsmodels.tsa.stattools as ts

class PairsTradingAlgorithm(QCAlgorithm):
    
    def Initialize(self):
        
        # start/end dates can be set with these functions
        self.SetStartDate(2013,3,2)
        self.SetEndDate(2021,3,18)

        self.SetCash(100000)
       
       # a listo f pairs we have determined are cointegrated
        cointegrated_pairs = [
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
            ('PXD','VLO'),
        ]
        
        # tickers includes all elements in cointegrated pairs but unique
        tickers = set()
        for i in cointegrated_pairs:
            for j in i:
                tickers.add(j)
            
        tickers = list(tickers)
        
        # threshold standard deviations to do a trade
        self.threshold = 2

        # all needed past equities
        self.symbols = []
        for i in tickers:
            self.symbols.append(self.AddEquity(i, Resolution.Daily).Symbol)
        
        self.formation_period = 252     # Window of history to consider fo calculations
                                        # i.e. moving average

        # map: stock --> history price
        self.history_price = {}
        for symbol in self.symbols: # add all equities to the stock object
            hist = self.History([symbol], self.formation_period+1, Resolution.Daily)

            # don't trade stocks that don't exist?
            #       !!!
            if hist.empty: 
                self.symbols.remove(symbol)

            else:
                self.history_price[str(symbol)] = deque(maxlen=self.formation_period)
                for tuple in hist.loc[str(symbol)].itertuples():
                    self.history_price[str(symbol)].append(float(tuple.close))

                if len(self.history_price[str(symbol)]) < self.formation_period:
                    self.symbols.remove(symbol)
                    self.history_price.pop(str(symbol))

        # all combinations of symbols
        self.symbol_pairs = list(it.combinations(self.symbols, 2))


        self.Schedule.On(self.DateRules.MonthStart("BKR"), self.TimeRules.AfterMarketOpen("BKR"), self.Rebalance)
        self.count = 0
        self.sorted_pairs = None
        self.coint_pairs  = self.symbol_pairs
        
        
    def OnData(self, data):
        # Update the price series everyday
        for symbol in self.symbols:
            if data.Bars.ContainsKey(symbol) and str(symbol) in self.history_price:
                self.history_price[str(symbol)].append(float(data[symbol].Close)) 
        if self.sorted_pairs is None: return
        
        # look for trades between all pairs
        for i in self.sorted_pairs:

            # calculate the spread of two price series
            spread = np.array(self.history_price[str(i[0])]) - np.array(self.history_price[str(i[1])])
            mean = np.mean(spread)
            std = np.std(spread)
            
            # calculate the ratios to buy and sell in
            ratio = self.Portfolio[i[0]].Price / self.Portfolio[i[1]].Price

            # long-short position is opened when pair prices have diverged by two standard deviations
            if spread[-1] > mean + self.threshold * std:
                if not self.Portfolio[i[0]].Invested and not self.Portfolio[i[1]].Invested:
                    quantity = int(self.CalculateOrderQuantity(i[0], 0.2))
                    self.Sell(i[0], quantity) 
                    self.Buy(i[1],  floor(ratio*quantity))                
            
            elif spread[-1] < mean - self.threshold * std: 
                quantity = int(self.CalculateOrderQuantity(i[0], 0.2))
                if not self.Portfolio[i[0]].Invested and not self.Portfolio[i[1]].Invested:
                    self.Sell(i[1], quantity) 
                    self.Buy(i[0], floor(ratio*quantity))  
                    
            # the position is closed when prices revert back -- all assets are liquidated
            elif self.Portfolio[i[0]].Invested and self.Portfolio[i[1]].Invested and abs(spread[-1]) < abs(mean - self.threshold * std) / 2:
                    self.Liquidate(i[0]) 
                    self.Liquidate(i[1])

    def Rebalance(self):

        # schedule the event to run every 3 months to select pairs with the smallest historical distance
        if self.count % 3 == 0:
            distances = {}
            
            for i in self.coint_pairs:

                # if the pair is valid and the API can provide the data for each equity do so
                # otherwise skip the pair
                try:
                    distances[i] = Pair(i[0], i[1], self.history_price[str(i[0])],  self.history_price[str(i[1])]).distance()
                    self.sorted_pairs = sorted(distances, key = lambda x: distances[x])[:4]
                except:
                    continue
            
            # list of all stocks being traded: contains duplicates but this is trivial
            trading_pairs = [pair[0] for pair in self.sorted_pairs] + [pair[1] for pair in self.sorted_pairs]
                 
            # if a stock previously being traded is no longer being traded liquidate it
            for stock in self.Portfolio.keys():
                if stock not in trading_pairs:
                    self.Liquidate(stock)
        
        self.count += 1
      

# 2 symbols and their corresponding prices 
class Pair:
    def __init__(self, symbol_a, symbol_b, price_a, price_b):
        self.symbol_a = symbol_a
        self.symbol_b = symbol_b
        self.price_a = price_a
        self.price_b = price_b
    
    def distance(self):
        # calculate the sum of squared deviations between two normalized price series
        norm_a = np.array(self.price_a)/self.price_a[0]
        norm_b = np.array(self.price_b)/self.price_b[0]
        return sum((norm_a - norm_b)**2)