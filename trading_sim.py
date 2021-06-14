from stock_data import Stock
import random as rand
import itertools as iter
import numpy as np
import matplotlib.pyplot as plt

# num_mins = 24180

class FakeBot:
    def __init__(self, stocks):
        self.Initialize(stocks)

    def Initialize(self, stocks):
        self.past_intervals = 30
        self.time           = self.past_intervals
        self.end_time       = min([len(i.pricedata) - self.past_intervals for i in stocks])

        self.z_threshold    = 2.0

        self.stocks         = stocks
        self.prices         = [s.pricedata for s in self.stocks]
        
        self.Invested       = False
        self.bank           = 100000
        self.stocksOwned    = [0 for i in self.stocks]

        # self.output = {}

        self.output_init()

    def Sell(self, stockNumber, volume=1):
        self.bank                       += volume * self.prices[stockNumber][self.time]
        self.stocksOwned[stockNumber]   -= volume

    def Buy(self, stockNumber, volume=1):
        self.bank                       -= volume * self.prices[stockNumber][self.time]
        self.stocksOwned[stockNumber]   += volume

    def Liquidate(self, stockNumber):
        volume  = self.stocksOwned[stockNumber]
        price   = self.prices[stockNumber][self.time]

        self.stocksOwned[stockNumber] = 0

        netchange = volume * price

        self.bank += netchange

    def OnData(self):
        self.time += 1
        self.output_init()

        time_ints = np.arange(len(self.prices[0]))

        if self.time == self.end_time:
            self.output['finished'] = True
            return self.output

        prevbank = self.bank

        self.history(self.prices)
        z_score = self.get_z_score(*self.prices)

        trading = 'no'

        if abs(z_score) > self.z_threshold:
            if not self.Invested:
                self.Invested = True
                # Need to determine buy ratio
                if z_score > 0.0:
                    self.Sell(0,1)
                    self.Buy(1, 1)
                    trading = f'BUY {self.stocks[1]}, SELL {self.stocks[0]}'
                else:
                    trading = f'SELL {self.stocks[1]}, BUY {self.stocks[0]}'
                    self.Sell(1,1)
                    self.Buy(0, 1)
        else:
            if self.Invested:
                trading = "LIQUIDATE"
                self.Invested = False
                self.Liquidate(0)
                self.Liquidate(1)

        currbank = self.bank
        gain = currbank - prevbank

        self.Debug(gain)
        self.Debug(self.stocksOwned)
        self.Debug(trading)
        
        self.output['price0'] = self.prices[0][self.time] 
        self.output['price1'] = self.prices[1][self.time]

        self.output['trading'] = trading
        
        return self.output
            
    def output_init(self):
        self.output                 = {}

        time = self.time

        self.output['finished']     = False
        self.output['print']        = []
        self.output['time']         = self.time

    def Debug(self, obj):
        self.output['print'] = self.output.get('print', []) + [obj]


    def history(self, data_list):
        return data_list[self.time - self.past_intervals: self.time]

    def get_z_score(self, stockA_data, stockB_data):
        stockA = np.array(self.history(stockA_data))
        stockB = np.array(self.history(stockB_data))

        diff = stockA-stockB

        mean = np.mean(diff)
        SD = np.std(diff)
        
        z = (diff[-1]-mean)/SD 
        return z
        

def get_subset_stocks():
    stocklist = ['EOG', 'COP'] # add stocks here
    stocks = [Stock(i) for i in stocklist]

    return stocks

# somenumber in [0, nC2]
def stock_choice(stocks, some_number):
    return list(iter.combinations(stocks, 2))[some_number]

def two_stocks(n=0):
    return stock_choice(get_subset_stocks(), n)

def test(manual=True):
    stocks = two_stocks()
    bot = FakeBot(stocks)
    halt = False
    print("ah")
    time_ints = np.arange(bot.end_time)
    print("oh")
    for stock in stocks:
        print("wow")
        plt.plot(time_ints, np.array(stock.pricedata[:bot.end_time]))
        print("geez")

    print("oh boy")

    buypoints = []
    buyprices = []

    sellpoints = []
    sellprices = []



    while True:
        if halt:
            break

        # if manual:
            # input()

        for i in range(10):
            # if halt:
            #     break
                
            output = bot.OnData()

            currtime = int(output['time'])

            print(f'{currtime}:')

            if output['finished']:
                halt = True
                break

            if output['trading'] != 'no':
                bought1 = output['trading'][:3] == 'BUY'
                p1 = int(output['price1'])

                if output['trading'][:3] == 'BUY':
                    buypoints.append(currtime)
                    buyprices.append(p1)

                    print('bought')

                elif output['trading'] == 'LIQUIDATE':
                    sellpoints.append(currtime)
                    sellprices.append(p1)

                    print('sold')

            continue

            if output['print'] is None or output['print'] == []:
                print('\tNothing to print')

            for obj in output['print']:
                name = ''# obj.__name__
                print(f'\t{name} :: {obj}')

    plt.scatter(buypoints, buyprices, color = "red", marker = "x")
    plt.scatter(sellpoints, sellprices, color = "green", marker = "x")
    print("bot terminated")
    plt.savefig("plot_data.png")
    print("figure saved")

if __name__ == '__main__':
    test(manual=True)