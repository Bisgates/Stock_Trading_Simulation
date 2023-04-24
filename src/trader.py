import csv
import pandas as pd
from collections import defaultdict
from tabulate import tabulate


class TradeManager:
    def __init__(self):
        self.transactions = defaultdict(list)
        self.hold_stock = False

    def buy_stock(self, current_date, close_price):
        self.hold_stock = True
        self.transactions['buy'].append((current_date, close_price))
        print(f"Bought stock on {current_date} at {close_price:.2f}")

    def sell_stock(self, current_date, close_price):
        buy_date, buy_price = self.transactions['buy'][-1]
        return_rate = self.calculate_return_rate(buy_price, close_price)
        self.transactions['sell'].append((current_date, close_price, return_rate))
        print(f"Sold stock on {current_date} at {close_price:.2f}, Return Rate: {return_rate:.2%}\n")
        self.hold_stock = False

    def calculate_return_rate(self, buy_price, sell_price, with_fee=0.003):
        return_rate = (sell_price - buy_price) / buy_price
        if with_fee:
            return_rate *= (1 - with_fee)
        return return_rate
    
    def display_transactions(self):
        transactions_df = pd.read_csv('transactions.csv')

        without_last_row_df = transactions_df.iloc[:-1]
        selected_columns = ['Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Return Rate']
        without_last_row_df = without_last_row_df[selected_columns]
        print(tabulate(without_last_row_df, headers='keys', tablefmt='psql', showindex=False))
        
        last_row_note = transactions_df.iloc[-1]['Notes']
        print(last_row_note)

    def store_transactions(self):
        with open('transactions.csv', 'w', newline='') as csvfile:
            fieldnames = ['Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Return Rate', 'Notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            total_return = 1
            for buy, sell in zip(self.transactions['buy'], self.transactions['sell']):
                writer.writerow({'Buy Date': buy[0], 'Sell Date': sell[0], 'Buy Price': f"{buy[1]:.2f}", 'Sell Price': f"{sell[1]:.2f}", 'Return Rate': f"{sell[2]:.2%}"})
                total_return *= (1 + sell[2])  # sell tuple: (date, price, return_rate)
            total_return -= 1
            
            first_buy_price = self.transactions['buy'][0][1]
            last_sell_price = self.transactions['sell'][-1][1]
            buy_hold_return_rate = self.calculate_return_rate(first_buy_price, last_sell_price)

            writer.writerow({'Notes': f"Total Return: {total_return:.2%}, Buy and Hold Return Rate: {buy_hold_return_rate:.2%}"})

        self.display_transactions()
