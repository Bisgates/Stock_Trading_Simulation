import csv
import pandas as pd
from collections import defaultdict
from rich.console import Console
from rich.table import Table
import json

from datetime import datetime

class TradeManager:
    def __init__(self, init_value=1.0, trader_id=0, log_path=''):
        self.transactions = defaultdict(list)
        self.hold_stock = None
        self.buy_date = None
        self.trader_id = trader_id
        self.log_path = log_path
        self.init_value = init_value
        self.current_value = init_value

    def buy_stock(self, current_date, close_price, stock_name):
        self.hold_stock = stock_name
        buy_date = current_date.strftime('%Y-%m-%d')
        self.buy_date = datetime.strptime(buy_date, '%Y-%m-%d') 
        self.transactions['buy'].append((buy_date, close_price, self.hold_stock))
        print(f"Bought {self.hold_stock} on {buy_date} at {close_price:.2f}")

    def sell_stock(self, current_date, close_price, stock_name):
        sell_date = current_date.strftime('%Y-%m-%d')
        self.sell_date = datetime.strptime(sell_date, '%Y-%m-%d') 
        hold_duration = (self.sell_date - self.buy_date).days
        buy_price = self.transactions['buy'][-1][1]
        return_rate = self.calculate_return_rate(buy_price, close_price)
        self.transactions['sell'].append((sell_date, close_price, return_rate, hold_duration))
        self.current_value *= (1 + return_rate)
        print(f"Sold {self.hold_stock} on {sell_date} at {close_price:.2f}, Return Rate: {return_rate:.2%}, Hold Duration: {hold_duration} days\n")
        self.hold_stock = None

    def calculate_return_rate(self, buy_price, sell_price, with_fee=0.003):
        return_rate = (sell_price - buy_price) / buy_price
        if with_fee:
            return_rate *= (1 - with_fee)
        return return_rate
    
    def store_transactions(self):
        with open(self.log_path + 'transactions.csv', 'w', newline='') as csvfile:
            fieldnames = ['Stock Name', 'Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Return Rate', 'Hold Duration', 'Notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for buy, sell in zip(self.transactions['buy'], self.transactions['sell']):
                writer.writerow({'Stock Name': buy[2],
                                 'Buy Date': buy[0], 
                                 'Sell Date': sell[0], 
                                 'Buy Price': f"{buy[1]:.2f}", 
                                 'Sell Price': f"{sell[1]:.2f}", 
                                 'Return Rate': f"{sell[2]:.2%}", 
                                 'Hold Duration': sell[3]})

        trade_infos = {}
        total_return = self.current_value / self.init_value - 1
        trade_infos['total_return'] = total_return
        trade_infos['buy_hold_return_rate'] = self.calculate_return_rate(self.transactions['buy'][0][1], self.transactions['sell'][-1][1])

        json.dump(trade_infos, open(self.log_path + 'trade_infos.json', 'w'))
    
    def display_transactions(self):
        transactions_df = pd.read_csv(self.log_path + 'transactions.csv')
        trade_infos = json.load(open(self.log_path + 'trade_infos.json', 'r'))

        selected_columns = ['Stock Name', 'Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Return Rate', 'Hold Duration']
        transactions_df = transactions_df[selected_columns]

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Stock Name", justify="right")
        table.add_column("Buy Date", justify="right")
        table.add_column("Sell Date", justify="right")
        table.add_column("Buy Price", justify="right")
        table.add_column("Sell Price", justify="right")
        table.add_column("Return Rate", justify="right")
        table.add_column("Hold Duration", justify="right")

        for _, row in transactions_df.iterrows():
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
        
        # trade infos
        conclude_table = Table(show_header=True, header_style="bold magenta")
        conclude_table.add_column(f'{self.trader_id}_th Trader', justify="right")
        conclude_table.add_column("Value", justify="right")
        conclude_table.add_row('Total Return', "{:.2f}%".format(trade_infos['total_return']*100))
        conclude_table.add_row('Buy & Hold Return', "{:.2f}%".format(trade_infos['buy_hold_return_rate']*100))
        conclude_table.add_row('Init Value', "{:.2f}".format(self.init_value))
        conclude_table.add_row('Current Value', "{:.2f}".format(self.current_value))
        console.print(conclude_table)
