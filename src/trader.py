import csv
from collections import defaultdict


class TradeManager:
    def __init__(self):
        self.transactions = defaultdict(list)
        self.hold_stock = False

    def buy_stock(self, current_date, close_price):
        self.hold_stock = True
        self.transactions['buy'].append((current_date, close_price))

    # def sell_stock(self, current_date, close_price):
    #     buy_date, buy_price = self.transactions['buy'][-1]
    #     change_rate = self.calculate_change_rate(buy_price, close_price)
    #     self.transactions['sell'].append((current_date, close_price, change_rate))
    #     self.hold_stock = False

    def sell_stock(self, current_date, close_price):
        buy_date, buy_price = self.transactions['buy'][-1]
        change_rate = self.calculate_change_rate(buy_price, close_price)
        self.transactions['sell'].append((current_date, close_price, change_rate))
        print(f"Sold stock on {current_date} at {close_price:.2f}, Change Rate: {change_rate:.2%}")
        self.hold_stock = False

    def calculate_change_rate(self, buy_price, sell_price):
        return (sell_price - buy_price) / buy_price

    # def store_transactions(self):
    #     with open('transactions.csv', 'w', newline='') as csvfile:
    #         fieldnames = ['Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Change Rate']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #         writer.writeheader()

    #         for buy, sell in zip(self.transactions['buy'], self.transactions['sell']):
    #             writer.writerow({'Buy Date': buy[0], 'Sell Date': sell[0], 'Buy Price': f"{buy[1]:.2f}", 'Sell Price': f"{sell[1]:.2f}", 'Change Rate': f"{sell[2]:.2%}"})

    #     print("Transactions have been saved to transactions.csv")

    #     with open('transactions.csv', 'r') as csvfile:
    #         content = csvfile.read()
    #         print("\nTransaction CSV Content:\n")
    #         print(content)

    def store_transactions(self):
        with open('transactions.csv', 'w', newline='') as csvfile:
            fieldnames = ['Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Change Rate', 'Notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for buy, sell in zip(self.transactions['buy'], self.transactions['sell']):
                writer.writerow({'Buy Date': buy[0], 'Sell Date': sell[0], 'Buy Price': f"{buy[1]:.2f}", 'Sell Price': f"{sell[1]:.2f}", 'Change Rate': f"{sell[2]:.2%}"})

            total_profit = 0
            for buy, sell in zip(self.transactions['buy'], self.transactions['sell']):
                total_profit += sell[1] - buy[1]  # sell tuple: (date, price, change_rate)

            first_buy_price = self.transactions['buy'][0][1]
            last_sell_price = self.transactions['sell'][-1][1]
            buy_hold_profit = last_sell_price - first_buy_price
            buy_hold_change_rate = self.calculate_change_rate(first_buy_price, last_sell_price)

            writer.writerow({'Notes': f"Total Profit: {total_profit:.2f}, Buy and Hold Profit: {buy_hold_profit:.2f}, Buy and Hold Change Rate: {buy_hold_change_rate:.2%}"})
