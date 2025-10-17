import subprocess
import sys

try:
    import yfinance
except ImportError:
    print("Installing yfinance...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance
    
import pandas as pd

class AlgorithmicTrading:
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.df = None
        self.budget = 5000
        self.position_open = False
        self.shares_held = 0
        self.buy_price = 0
        self.trades = []  

    def download_data(self):
        self.df = yfinance.download(self.symbol, start=self.start_date, end=self.end_date, interval="1d")
        self.df.columns = self.df.columns.droplevel(1)
        return self

    def clean_data(self):
        self.df = self.df[~self.df.index.duplicated(keep='first')]
        self.df = self.df.ffill()
        return self

    def calculate_indicators(self):
        self.df['MA50'] = self.df['Close'].rolling(50).mean()
        self.df['MA200'] = self.df['Close'].rolling(200).mean()
        return self

    def identify_golden_crosses(self):
        self.df['Signal'] = (self.df['MA50'] > self.df['MA200']).astype(int)
        self.df['GoldenCross'] = self.df['Signal'].diff() == 1
        return self.df.index[self.df['GoldenCross']]

    def identify_death_crosses(self):
        self.df['DeathCross'] = self.df['Signal'].diff() == -1
        return self.df.index[self.df['DeathCross']]

    def execute_trades(self):
        golden_crosses = self.identify_golden_crosses()
        death_crosses = self.identify_death_crosses()

        for buy_date in golden_crosses:
            if self.position_open:
                continue  
            buy_price = self.df.loc[buy_date, 'Close']
            max_shares = self.budget // buy_price
            self.position_open = True
            self.buy_price = buy_price
            self.shares_held = max_shares

            future_death = death_crosses[death_crosses > buy_date]
            if len(future_death) > 0:
                sell_date = future_death[0]
            else:
                sell_date = self.df.index[-1]

            sell_price = self.df.loc[sell_date, 'Close']
            profit_loss = (sell_price - self.buy_price) * self.shares_held

            self.trades.append({
                'buy_date': buy_date,
                'sell_date': sell_date,
                'shares': self.shares_held,
                'buy_price': self.buy_price,
                'sell_price': sell_price,
                'profit_loss': profit_loss
            })

            self.position_open = False

        return self

    def force_close_position(self):
        if self.position_open:
            last_date = self.df.index[-1]
            sell_price = self.df.loc[last_date, 'Close']
            profit_loss = (sell_price - self.buy_price) * self.shares_held
            self.trades.append({
                'buy_date': self.buy_date,
                'sell_date': last_date,
                'shares': self.shares_held,
                'buy_price': self.buy_price,
                'sell_price': sell_price,
                'profit_loss': profit_loss
            })
            self.position_open = False
        return self

    def report_results(self):
        total_profit = sum(t['profit_loss'] for t in self.trades)
        final_cash = self.budget + total_profit
        print(f"Initial Investment: ${self.budget}")
        print(f"Final Cash: ${final_cash}")
        print(f"Total Profit/Loss: ${total_profit}")
        if self.budget:
            print(f"Return: {(total_profit/self.budget)*100:.2f}%")
        return self

    def run(self):
        (self.download_data()
             .clean_data()
             .calculate_indicators()
             .execute_trades()
             .force_close_position()
             .report_results())
        return self


if __name__ == "__main__":
    trader = AlgorithmicTrading("AAPL", "2018-01-01", "2023-12-31")
    trader.run()