import argparse
import os
from src.prepare_data import PrepareData
from src.trader import TradeManager

class AutoTrade:
    def __init__(self, stocks_data):
        self.stocks_data = stocks_data
        self.trade_manager = TradeManager()
        self.hold_stock = None

    def execute(self):
        for date in sorted(set(date for data in self.stocks_data.values() for date in data.index)):
            if not self.hold_stock:
                for stock_name, data in self.stocks_data.items():
                    if date in data.index and data.loc[date, '10MA'] > data.loc[date, '30MA']:
                        self.trade_manager.buy_stock(date, data.loc[date, 'Close'], stock_name)
                        self.hold_stock = stock_name
                        break
            elif self.hold_stock is not None and date in self.stocks_data[self.hold_stock].index and self.stocks_data[self.hold_stock].loc[date, '10MA'] < self.stocks_data[self.hold_stock].loc[date, '30MA']:
                self.trade_manager.sell_stock(date, self.stocks_data[self.hold_stock].loc[date, 'Close'], self.hold_stock)
                self.hold_stock = None

        self.trade_manager.store_transactions()
        self.trade_manager.display_transactions()
        

def main(files_path=None):
    stocks_data = {}
    if files_path.endswith('.csv'):
        data = PrepareData(files_path).data
        stock_name = os.path.splitext(files_path)[0].split('/')[-1]
        stocks_data[stock_name] = data
    else:
        for file_name in os.listdir(files_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(files_path, file_name)
                data = PrepareData(file_path).data
                stock_name = os.path.splitext(file_name)[0]
                stocks_data[stock_name] = data
    auto_trade = AutoTrade(stocks_data)
    auto_trade.execute()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stock Trading Visualization and Simulation")
    parser.add_argument('--files_path', type=str, default='stock_data/', help='Path to the directory containing CSV files of stock data')
    args = parser.parse_args()

    main(args.files_path)
