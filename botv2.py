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
        
        self.SetStartDate(2020,3,2)
        # self.SetEndDate(2021,3,18)
        self.SetCash(100000)
        
        self.p_value = 0.05
        
        # SYM1 = 'MA'
        # SYM2 = 'V'
        
        # SYM1 = 'AAPL'
        # SYM2 = 'QCOM'
        
        # SYM1 = 'ADBE'
        # SYM2 = 'APH'
       
        some_pairs = [
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
        
        s = set()
        for i in some_pairs:
            for j in i:
                s.add(j)
            
        tickers = list(s) 
        
        self.threshold = 2
        self.symbols = []
        for i in tickers:
            self.symbols.append(self.AddEquity(i, Resolution.Daily).Symbol)
        
        self.pairs = {}
        self.formation_period = 252

        self.history_price = {}
        for symbol in self.symbols:
            hist = self.History([symbol], self.formation_period+1, Resolution.Daily)
            if hist.empty: 
                self.symbols.remove(symbol)
            else:
                self.history_price[str(symbol)] = deque(maxlen=self.formation_period)
                for tuple in hist.loc[str(symbol)].itertuples():
                    self.history_price[str(symbol)].append(float(tuple.close))
                if len(self.history_price[str(symbol)]) < self.formation_period:
                    self.symbols.remove(symbol)
                    self.history_price.pop(str(symbol))

        self.symbol_pairs = list(it.combinations(self.symbols, 2))  
        # Add the benchmark
        # self.AddEquity(SYM1, Resolution.Daily)
        # self.AddEquity(SYM2, Resolution.Daily) 
        self.Schedule.On(self.DateRules.MonthStart("BKR"), self.TimeRules.AfterMarketOpen("BKR"), self.Rebalance)
        self.count = 0
        self.sorted_pairs = None
        # self.coint_pairs  = self.symbol_pairs
        
        
    def OnData(self, data):
        # Update the price series everyday
        for symbol in self.symbols:
            if data.Bars.ContainsKey(symbol) and str(symbol) in self.history_price:
                self.history_price[str(symbol)].append(float(data[symbol].Close)) 
        if self.sorted_pairs is None: return
        
        for i in self.sorted_pairs:
            # calculate the spread of two price series
            spread = np.array(self.history_price[str(i[0])]) - np.array(self.history_price[str(i[1])])
            mean = np.mean(spread)
            std = np.std(spread)
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
                    
            # the position is closed when prices revert back
            elif self.Portfolio[i[0]].Invested and self.Portfolio[i[1]].Invested and abs(spread[-1]) < abs(mean - self.threshold * std) / 2:
                    self.Liquidate(i[0]) 
                    self.Liquidate(i[1])                
                    
    def cointegrated(self, stocks):
        history = (self.history_price[str(stocks[0])],  self.history_price[str(stocks[1])])
        # history = (history[0][-self.formation_period//2:], history[1][-self.formation_period//2:])
        p_val = ts.coint(*history)[1]
        
        return p_val  <= self.p_value

    def Rebalance(self):
        # schedule the event to fire every half year to select pairs with the smallest historical distance
        
        if self.count % 6 == 0:
            distances = {}
            # self.Debug("one")
            
            # if self.count % 100 == 0:
            #     self.count_pairs = list(
            #         filter(
            #             lambda s: self.cointegrated(s),
            #             self.symbol_pairs
            #             )
            #         )
                
            # self.Debug("two")
                
            for i in self.symbol_pairs:
                distances[i] = Pair(i[0], i[1], self.history_price[str(i[0])],  self.history_price[str(i[1])]).distance()
                self.sorted_pairs = sorted(distances, key = lambda x: distances[x])[:4]
        
        self.count += 1
            
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