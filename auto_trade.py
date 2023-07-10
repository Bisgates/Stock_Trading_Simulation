import argparse
from src.prepare_data import PrepareData
from src.trader import TradeManager

class AutoTrade:
    def __init__(self, data):
        self.data = data
        self.trade_manager = TradeManager()
        self.hold_stock = False

    def execute(self):
        for date, row in self.data.iterrows():
            if not self.hold_stock and row['10MA'] > row['30MA']:
                self.trade_manager.buy_stock(date, row['Close'])
                self.hold_stock = True
            elif self.hold_stock and row['10MA'] < row['30MA']:
                self.trade_manager.sell_stock(date, row['Close'])
                self.hold_stock = False

        self.trade_manager.store_transactions()
        self.trade_manager.display_transactions()
        

def main(file_path=None, present_lenth=90):
    data = PrepareData(file_path).data
    auto_trade = AutoTrade(data)
    auto_trade.execute()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stock Trading Visualization and Simulation")
    parser.add_argument('--file_path', type=str, default='stock_data/apple.csv', help='Path to the CSV file containing stock data')
    args = parser.parse_args()

    main(args.file_path)