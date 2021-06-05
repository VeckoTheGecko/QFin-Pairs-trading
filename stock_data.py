import os
import pandas as pd
import numpy as np
from datetime import datetime

import itertools

from process_csv import group_companies_by_sector, get_company_names

print("This file uses ticker_data from Quant connect. The data is assumed to be stored in a folder 'S&P500_3monthdata/ticker_breakdown' in the root directory.\n"+ \
      "Specify Stock. DATA_FOLDER = <new_folder> to change this folder.")

class Stock:
    DATA_FOLDER = "S&P500_3monthdata/ticker_breakdown"
    LIST        = [file.split(".")[0] for file in os.listdir(DATA_FOLDER)]

    def __init__(self, stock_name):
        self.name = stock_name
        self.file_path = os.path.join(self.DATA_FOLDER, f"{stock_name}.csv")
    
    def one_minute(self):
        df = pd.read_csv(self.file_path, names = ["time_str", "price"])
        
        # Creating a proper time column
        df["time"] = df["time_str"].apply(datetime.strptime, args = ('%Y-%m-%d %H:%M:%S',))
        df = df.drop(columns="time_str")
        
        return df[["time", "price"]] # Leaving out the original string column
    
    def any_minute(self, period):
        df = self.one_minute()
        
        # Grouping into 5min bins
        df.set_index('time', inplace=True)
        df_group = df.groupby(pd.Grouper(level='time', freq=f'{period}T'))["price"].agg('mean')
        df_group.dropna(inplace=True)
        df_group = df_group.to_frame().reset_index()
        return df_group

    def all_by_industry():
        """
        return dictionary of stocks by industry
            {sector : list_of_stocks}
        """
        sector_symbols_map, symbol_company_map = group_companies_by_sector('constituents_csv.csv')

        stocks_by_industry = {}
        for sector in sector_symbols_map.keys():
            stocks_by_industry[sector] = []

        for sector, symbols in sector_symbols_map.items():
            for symbol in symbols:
                stocks_by_industry[sector].append(Stock(symbol))

        return stocks_by_industry

    def all_industries():
        sector_symbols_map, symbol_company_map = group_companies_by_sector('constituents_csv.csv')
        return list(sector_symbols_map.keys())

    def cointegration(s1, s2):
        """
        return the p value of cointegration between 2 stocks
        """

        return 0.04

    def analyze_industries(industries_to_analyze=[], p_value=0.05):
        stocks_by_industry  = Stock.all_by_industry()
        relevant_stocks     = {k : v for k, v in stocks_by_industry.items() if k in industries_to_analyze}

        for industry, stocklist in relevant_stocks.items():
            print(f'\n\n{industry}')
            for i in itertools.combinations(stocklist, 2):
                i = sorted(i, key=lambda x: x.name)
                stock1, stock2 = i

                # filename = f'{significance}_{stock1.name}_{stock2.name}'
                print(stock1, stock2)
    
    def five_minute(self):
        return self.any_minute(5)
    
    def ten_minute(self):
        return self.any_minute(10)

    def __repr__(self):
        return f"<Stock='{self.name}'>"