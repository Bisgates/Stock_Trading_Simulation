import argparse
import os
from src.prepare_data import PrepareData
from src.trader import TradeManager

class AutoTrade:
    def __init__(self, stocks_data, log_path='logs/'):
        self.stocks_data = stocks_data
        self.trader = TradeManager(self.stocks_data, init_value=1.0, log_path=log_path)
        # self.traders = [TradeManager(self.stocks_data, init_value=0.1, log_path=log_path) for _ in range(10)]
        self.trading_dates = sorted(set(date for data in self.stocks_data.values() for date in data.index))

    def execute(self):
        for date in self.trading_dates:
            if not self.trader.hold_stock:
                for stock_name, data in self.stocks_data.items():
                    if date in data.index and data.loc[date, '10MA'] > data.loc[date, '30MA']:
                        self.trader.buy_stock(date, data.loc[date, 'Close'], stock_name)
                        break
            elif self.trader.hold_stock \
                    and date in self.stocks_data[self.trader.hold_stock].index   \
                    and self.stocks_data[self.trader.hold_stock].loc[date, '10MA'] < self.stocks_data[self.trader.hold_stock].loc[date, '30MA']:
                self.trader.sell_stock(date, 
                                              self.stocks_data[self.trader.hold_stock].loc[date, 'Close'], 
                                              self.trader.hold_stock)
        # if self.trader.hold_stock:    #TODO, sell all stocks at the end
        #     self.trader.sell_stock(self.trading_dates[-1], 
        #                                   self.stocks_data[self.trader.hold_stock].loc[self.trading_dates[-1], 'Close'], 
        #                                   self.trader.hold_stock)

        self.trader.store_transactions()
        total_return = self.trader.display_transactions()
        return total_return
    
    # v_2, more strict
    # def execute(self):
    #     last_10MA = 0 
    #     last_30MA = 0
    #     for date in self.trading_dates:
    #         if not self.trader.hold_stock:
    #             for stock_name, data in self.stocks_data.items():
    #                 if date in data.index and data.loc[date, '10MA'] > data.loc[date, '30MA'] and \
    #                    data.loc[date, '10MA'] > last_10MA and data.loc[date, '30MA'] > last_30MA and \
    #                    data.loc[date, '10MA'] > data.loc[date, 'Close']:
    #                         self.trader.buy_stock(date, data.loc[date, 'Close'], stock_name)
    #                         break
    #         elif self.trader.hold_stock \
    #                 and date in self.stocks_data[self.trader.hold_stock].index   \
    #                 and self.stocks_data[self.trader.hold_stock].loc[date, 'Close'] < self.stocks_data[self.trader.hold_stock].loc[date, '10MA'] \
    #                 and self.stocks_data[self.trader.hold_stock].loc[date, '10MA'] < last_10MA \
    #                 and self.stocks_data[self.trader.hold_stock].loc[date, '30MA'] < last_30MA \
    #                 and self.stocks_data[self.trader.hold_stock].loc[date, '10MA'] < self.stocks_data[self.trader.hold_stock].loc[date, '30MA']:
    #             self.trader.sell_stock(date, 
    #                                           self.stocks_data[self.trader.hold_stock].loc[date, 'Close'], 
    #                                           self.trader.hold_stock)
    #         if date in data.index:
    #             last_10MA = data.loc[date, '10MA']
    #             last_30MA = data.loc[date, '30MA']

    #     self.trader.store_transactions()
    #     total_return = self.trader.display_transactions()
    #     return total_return

def main(files_path=None):
    stocks_data = PrepareData(files_path).stocks_data
    auto_trade = AutoTrade(stocks_data)
    total_return = auto_trade.execute()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stock Trading Visualization and Simulation")
    parser.add_argument('--files_path', type=str, default='stock_data/', help='Path to the directory containing CSV files of stock data')
    args = parser.parse_args()

    main(args.files_path)
