from stock_data import Stock
import random as rand
import itertools as iter
import numpy as np
import matplotlib.pyplot as plt
import statsmodels

# num_mins = 24180

class BotBase:
    # Buy but negative
    def Sell(self, stockNumber, volume=1):
        self.bank                       += volume * self.prices[stockNumber][self.time]
        self.stocksOwned[stockNumber]   -= volume

    # Sell but negative
    def Buy(self, stockNumber, volume=1):
        self.bank                       -= volume * self.prices[stockNumber][self.time]
        self.stocksOwned[stockNumber]   += volume

    # Sets everything to 0 through buying or selling
    def Liquidate(self, stockNumber):
        volume  = self.stocksOwned[stockNumber]
        price   = self.prices[stockNumber][self.time]

        self.stocksOwned[stockNumber] = 0

        netchange = volume * price
        self.bank += netchange
        
    # for the output, don't worry about this
    def output_init(self):
        self.output                 = {}

        time = self.time

        self.output['finished']     = False
        self.output['print']        = []
        self.output['time']         = self.time


class FakeBot(BotBase):
    def __init__(self, stocks):
        self.Initialize(stocks)

    def Initialize(self, stocks):
        self.past_intervals = 30    # how many previous datapoints do you consider for calculations
        self.time           = self.past_intervals # current index of the time
        self.end_time       = 1199 #min([len(i.pricedata) - self.past_intervals for i in stocks])

        self.z_threshold    = 2.0

        self.stocks         = stocks
        self.prices         = [s.pricedata for s in self.stocks]
        
        self.Invested       = False
        self.bank           = 100
        self.stocksOwned    = [0 for i in self.stocks]

        # self.output = {}

        self.output_init()

    def Debug(self, obj):
        self.output['print'] = self.output.get('print', []) + [obj]

    def worth(self):
        return self.bank + sum([i*j[self.time] for i, j in zip(self.stocksOwned, self.prices)])

    def OnData(self):
        self.time += 1
        plt.scatter(self.time, self.prices[0][self.time],color = 'black', s = 1)
        plt.scatter(self.time, self.prices[1][self.time],color = 'black', s = 1)
        self.output_init()
        interval = self.time % 30
        if interval == 0 and not self.Invested:
          #if self.Invested:
          '''trading = "LIQUIDATE"
          self.Invested = False
          self.Liquidate(0)
          self.Liquidate(1)'''
          self.update_stocks()
          self.prices = [s.pricedata for s in self.stocks]

        if self.time == self.end_time:
            self.output['finished'] = True
            return self.output

        prevbank = self.bank

        self.history(self.prices)
        z_score = self.get_z_score(*self.prices)

        trading = 'no'

        flat_amt = 10
        ratio = flat_amt * (self.prices[0][self.time] / self.prices[1][self.time])

        if abs(z_score) > self.z_threshold:
            if not self.Invested:
                self.Invested = True
                # Need to determine buy ratio
                if z_score > 0.0:
                    trading = f'BUY {self.stocks[1]}, SELL {self.stocks[0]}'
                    self.Sell(0,flat_amt)
                    self.Buy(1, ratio)

                else:
                    trading = f'SELL {self.stocks[1]}, BUY {self.stocks[0]}'
                    self.Sell(1,ratio)
                    self.Buy(0, flat_amt)
        elif abs(z_score) < self.z_threshold / 2:
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
            

    def history(self, data_list, time_int = 30):
        return data_list[self.time - time_int: self.time]

    def get_z_score(self, stockA_data, stockB_data):
        stockA = np.array(self.history(stockA_data))
        stockB = np.array(self.history(stockB_data))

        diff = stockA-stockB

        mean = np.mean(diff)
        SD = np.std(diff)
        
        z = (diff[-1]-mean)/SD 
        return z

    def update_stocks(self):
        stocklist = [
          'COP','FANG','EOG','HAL','PXD']
        p_value = 1
        stockA = None
        stockB = None
        for i in range(len(stocklist)):
          for j in range(i+1, len(stocklist)):
            _, p, _ = statsmodels.tsa.stattools.coint(self.history(Stock(stocklist[i]).pricedata,60),self.history(Stock(stocklist[j]).pricedata,60))
            if p < p_value:
              print(stocklist[i])
              print(stocklist[j])
              stockA = Stock(stocklist[i])
              stockB = Stock(stocklist[j])
              p_value = p
        self.stocks = [stockA, stockB]
      

        

def get_subset_stocks():
    # 'ADBE', 'IBM
    # 'AMD', 'CDNS'
    stocklist = ['COP', 'EOG'] # add stocks here
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

    initial_bank = bot.bank
    print(initial_bank)
    bank      = np.zeros(bot.end_time + 1)

    

    buypoints = []
    buyprices = []

    sellpoints = []
    sellprices = []

    print(f"endtime: {bot.end_time}")

    plt.ion()

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

            print(f'{currtime}:', end="\r")
            bank[currtime] = bot.worth()

            if output['finished']:
                halt = True
                break

            if output['trading'] != 'no':
                bought1 = output['trading'][:3] == 'BUY'
                p1 = int(output['price1'])

                if output['trading'][:3] == 'BUY':
                    buypoints.append(currtime)
                    buyprices.append(p1)

                    # print('buy')

                else:
                    sellpoints.append(currtime)
                    sellprices.append(p1)

                    # print('buy')

            # continue

            if output['print'] is None or output['print'] == []:
                print('\tNothing to print')

            for obj in output['print']:
                name = ''# obj.__name__
                print(f'\t{name} :: {obj}')

    print("bot terminated")

    plt.scatter(buypoints, buyprices, color = "red", marker = "x")
    plt.scatter(sellpoints, sellprices, color = "green", marker = ".")

    plt.plot(100*(bank - initial_bank)/initial_bank)

    plt.savefig("plot_data.png")
    print("figure saved")
    print("Net profit was: ", bank[-1] - initial_bank)
if __name__ == '__main__':
    test(manual=True)