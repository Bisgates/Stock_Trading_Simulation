import csv
import pandas as pd
from collections import defaultdict
from rich.console import Console
from rich.table import Table

from datetime import datetime

class TradeManager:
    def __init__(self):
        self.transactions = defaultdict(list)
        self.hold_stock = False
        self.buy_date = None

    def buy_stock(self, current_date, close_price, stock_name):
        self.hold_stock = True
        buy_date = current_date.strftime('%Y-%m-%d')
        self.buy_date = datetime.strptime(buy_date, '%Y-%m-%d')  # assuming the date is in 'YYYY-MM-DD' format
        self.transactions['buy'].append((buy_date, close_price, stock_name))
        print(f"Bought {stock_name} on {buy_date} at {close_price:.2f}")

    def sell_stock(self, current_date, close_price, stock_name):
        sell_date = current_date.strftime('%Y-%m-%d')
        self.sell_date = datetime.strptime(sell_date, '%Y-%m-%d')  # assuming the date is in 'YYYY-MM-DD' format
        hold_duration = (self.sell_date - self.buy_date).days
        buy_price = self.transactions['buy'][-1][1]
        return_rate = self.calculate_return_rate(buy_price, close_price)
        self.transactions['sell'].append((sell_date, close_price, return_rate, hold_duration))
        print(f"Sold {stock_name} on {sell_date} at {close_price:.2f}, Return Rate: {return_rate:.2%}, Hold Duration: {hold_duration} days\n")
        self.hold_stock = False

    def calculate_return_rate(self, buy_price, sell_price, with_fee=0.003):
        return_rate = (sell_price - buy_price) / buy_price
        if with_fee:
            return_rate *= (1 - with_fee)
        return return_rate
    
    def store_transactions(self):
        with open('transactions.csv', 'w', newline='') as csvfile:
            fieldnames = ['Stock Name', 'Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Return Rate', 'Hold Duration', 'Notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            total_return = 1
            for buy, sell in zip(self.transactions['buy'], self.transactions['sell']):
                writer.writerow({'Stock Name': buy[2],
                                 'Buy Date': buy[0], 
                                 'Sell Date': sell[0], 
                                 'Buy Price': f"{buy[1]:.2f}", 
                                 'Sell Price': f"{sell[1]:.2f}", 
                                 'Return Rate': f"{sell[2]:.2%}", 
                                 'Hold Duration': sell[3]})
                total_return *= (1 + sell[2])  # sell tuple: (date, price, return_rate, hold_duration)
            total_return -= 1
            
            first_buy_price = self.transactions['buy'][0][1]
            last_sell_price = self.transactions['sell'][-1][1]
            buy_hold_return_rate = self.calculate_return_rate(first_buy_price, last_sell_price)

            writer.writerow({'Notes': f"Total Return: {total_return:.2%}, Buy and Hold Return Rate: {buy_hold_return_rate:.2%}"})
    
    def display_transactions(self):
        transactions_df = pd.read_csv('transactions.csv')

        without_last_row_df = transactions_df.iloc[:-1]
        selected_columns = ['Stock Name', 'Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Return Rate', 'Hold Duration']
        without_last_row_df = without_last_row_df[selected_columns]

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Stock Name", justify="right")
        table.add_column("Buy Date", justify="right")
        table.add_column("Sell Date", justify="right")
        table.add_column("Buy Price", justify="right")
        table.add_column("Sell Price", justify="right")
        table.add_column("Return Rate", justify="right")
        table.add_column("Hold Duration", justify="right")

        for _, row in without_last_row_df.iterrows():
            return_rate = float(row['Return Rate'].strip('%')) / 100
            if return_rate > 0:
                color = "green"
            else:
                color = "red"
            if abs(return_rate) > 0.1:
                style = "bold " + color
            else:
                style = color
            table.add_row(
                row['Stock Name'], 
                row['Buy Date'], 
                row['Sell Date'], 
                str(row['Buy Price']), 
                str(row['Sell Price']), 
                f"[{style}]{row['Return Rate']}[/]", 
                str(int(row['Hold Duration']))
            )

        console.print(table)

        last_row_note = transactions_df.iloc[-1]['Notes']
        console.print(last_row_note)
