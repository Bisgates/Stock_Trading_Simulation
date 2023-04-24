import mplfinance as mpf
import matplotlib.pyplot as plt
from src.prepare_data import PrepareData
from src.trader import TradeManager


class CandlestickChart:
    def __init__(self, file_path, present_lenth=15):
        self.data = PrepareData(file_path).data
        self.start_date = self.data.index[0]
        self.style = self.create_mpf_style()
        self.present_lenth = present_lenth
        self.trade_manager = TradeManager()

    def create_mpf_style(self):
        mc = mpf.make_marketcolors(up='g', down='r', wick={'up': 'g', 'down': 'r'})
        return mpf.make_mpf_style(marketcolors=mc)

    def update_chart(self):
        end_date_index = self.data.index.get_loc(self.start_date) + self.present_lenth
        end_date = self.data.index[end_date_index]
        self.current_date = end_date
        data_to_display = self.data[self.start_date:end_date]

        self.fig.clf()
        splt = self.fig.subplots(nrows=2, ncols=1, sharex=True)

        # Plot original data
        mpf.plot(data_to_display, type='candle', style=self.style, axtitle="Original Data", axisoff=True, ax=splt[0])

        # Plot new data
        mpf.plot(data_to_display, type='candle', style=self.style, columns=['New_Open', 'New_High', 'New_Low', 'New_Close', 'Volume'], axtitle="New Data", axisoff=True, ax=splt[1])

        # Display price information on the top-left corner
        prices = data_to_display.iloc[-1]
        price_info = f"High: {prices['High']:.2f}  Open: {prices['Open']:.2f}\nLow: {prices['Low']:.2f}  Close: {prices['Close']:.2f}"
        splt[0].text(0, 1.05, price_info, transform=splt[0].transAxes, fontsize=10, backgroundcolor='white')

        plt.draw()

    def on_key(self, event):
        if event.key == 'l':
            start_date_index = self.data.index.get_loc(self.start_date) + 1
            self.start_date = self.data.index[start_date_index]
        elif event.key == 'j':
            start_date_index = self.data.index.get_loc(self.start_date) - 1
            if start_date_index >= 0:
                self.start_date = self.data.index[start_date_index]
        elif event.key == 'b':
            if not self.trade_manager.hold_stock:
                close_price = self.data.loc[self.current_date, 'Close']
                self.trade_manager.buy_stock(self.current_date, close_price)
                print(f"Bought stock on {self.current_date} at {close_price:.2f}")
        elif event.key == 'c':
            if self.trade_manager.hold_stock:
                close_price = self.data.loc[self.current_date, 'Close']
                self.trade_manager.sell_stock(self.current_date, close_price)
                print(f"Sold stock on {self.current_date} at {close_price:.2f}")
        elif event.key == 'q':
            self.trade_manager.store_transactions()
            plt.close()

        self.update_chart()


    def display(self):
        self.fig = plt.figure(figsize=(12, 8))
        self.update_chart()

        plt.xticks(rotation=45)
        plt.tight_layout()

        key_event = lambda event: self.on_key(event)
        self.fig.canvas.mpl_connect('key_press_event', key_event)
        plt.show()

file_path = 'stock_data/apple.csv'
candlestick_chart = CandlestickChart(file_path, present_lenth=30)
candlestick_chart.display()