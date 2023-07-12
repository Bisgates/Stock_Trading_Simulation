import os
import pickle
import pandas as pd
from random import sample
from pathlib import Path

class PrepareData:
    def __init__(self, file_path, max_stocks_num=100):
        self.stocks_data = {}
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            data = self.read_and_preprocess_data(df)
            stock_name = os.path.splitext(file_path)[0].split('/')[-1]
            self.stocks_data[stock_name] = data
        elif file_path.endswith('.pkl'):
            with open(file_path, 'rb') as f:
                df = pickle.load(f)
            # self.stocks = sample(list(df.keys()), max_stocks_num)   # all
            self.stocks = Path('stock_list/hushen300.txt').read_text().split()
            self.stocks = sample(self.stocks, max_stocks_num)
            self.stocks_data = {stock:df[stock] for stock in self.stocks}
        else:   # a bunch of csv files
            for file_name in os.listdir(file_path):
                if file_name.endswith('.csv'):
                    csv_path = os.path.join(file_path, file_name)
                    df = pd.read_csv(csv_path)
                    data = self.read_and_preprocess_data(df)
                    stock_name = os.path.splitext(file_name)[0]
                    self.stocks_data[stock_name] = data
        
    def calculate_score(self, row):
        # improve needed
        new_open = row['New_Open']
        new_high = row['New_High']
        new_low = row['New_Low']
        new_close = row['New_Close']

        if new_low == new_open:
            return 1
        elif new_close > new_open and new_low != new_open:
            return 0.5
        elif new_high == new_open:
            return -1
        elif new_close < new_open and new_high != new_open:
            return -0.5
        else:
            return 0
        
    def calculate_growth_rate(self, row):
        growth_rate = (round(row['Close']/row['Open'], 4) - 1)*100
        return growth_rate
        
    def calculate_new_values(self, prev_open, prev_close, current_open, current_high, current_low, current_close):
        new_close = (current_open + current_high + current_low + current_close) / 4
        new_open = (prev_open + prev_close) / 2
        new_high = max(current_high, new_open, new_close)
        new_low = min(current_low, new_open, new_close)

        return new_open, new_high, new_low, new_close

    def read_and_preprocess_data(self, data):
        
        # Add '10MA' and '30MA' columns
        data['10MA'] = data['Close'].rolling(window=10).mean()
        data['30MA'] = data['Close'].rolling(window=30).mean()
        data['60MA'] = data['Close'].rolling(window=60).mean()
        
        # Initialize new columns
        data['New_Open'] = data['Open']
        data['New_High'] = data['High']
        data['New_Low'] = data['Low']
        data['New_Close'] = data['Close']

        # Calculate new values for each row
        for i in range(1, len(data)):
            prev_open, prev_close = data.loc[i - 1, ['New_Open', 'New_Close']]
            current_open, current_high, current_low, current_close = data.loc[i, ['Open', 'High', 'Low', 'Close']]

            new_open, new_high, new_low, new_close = self.calculate_new_values(prev_open, prev_close, current_open, current_high, current_low, current_close)

            data.at[i, 'New_Open'] = new_open
            data.at[i, 'New_High'] = new_high
            data.at[i, 'New_Low'] = new_low
            data.at[i, 'New_Close'] = new_close


        # Add 'score' column and calculate scores for each row
        data['score'] = data.apply(self.calculate_score, axis=1)
        data['growth_rate'] = data.apply(self.calculate_growth_rate, axis=1)
        
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        return data
