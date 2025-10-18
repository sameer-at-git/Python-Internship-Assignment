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
        print("Step 1: Downloading historical data...")
        self.df = yfinance.download(self.symbol, start=self.start_date, end=self.end_date, interval="1d")
        self.df.columns = self.df.columns.droplevel(1)
        print("Data downloaded successfully.")
        print(f"Number of rows: {len(self.df)}\n")
        return self

    def clean_data(self):
        print("Step 2: Cleaning data...")
        missing_before = self.df.isna().sum().sum()
        duplicates_before = self.df.index.duplicated().sum()
        print(f"Missing values before cleaning: {missing_before}")
        print(f"Duplicate rows before cleaning: {duplicates_before}")

        self.df = self.df[~self.df.index.duplicated(keep='first')]
        self.df = self.df.ffill()

        missing_after = self.df.isna().sum().sum()
        duplicates_after = self.df.index.duplicated().sum()
        print(f"Missing values after cleaning: {missing_after}")
        print(f"Duplicate rows after cleaning: {duplicates_after}\n")
        return self

    def calculate_indicators(self):
        print("Step 3: Calculating moving averages...")
        self.df['MA50'] = self.df['Close'].rolling(50).mean()
        self.df['MA200'] = self.df['Close'].rolling(200).mean()
        print("First 5 rows of moving averages (MA50 and MA200):")
        print(self.df[['Close','MA50','MA200']].head(10))
        print()
        return self

    def identify_golden_crosses(self):
        self.df['Signal'] = (self.df['MA50'] > self.df['MA200']).astype(int)
        self.df['GoldenCross'] = self.df['Signal'].diff() == 1
        golden_dates = self.df.index[self.df['GoldenCross']]
        print("Step 4a: Golden Crosses detected on the following dates:")
        if len(golden_dates) > 0:
            for d in golden_dates:
                print(f" - {d.date()}")
        else:
            print("No golden crosses found.")
        print()
        return golden_dates

    def identify_death_crosses(self):
        self.df['DeathCross'] = self.df['Signal'].diff() == -1
        death_dates = self.df.index[self.df['DeathCross']]
        print("Step 4b: Death Crosses detected on the following dates:")
        if len(death_dates) > 0:
            for d in death_dates:
                print(f" - {d.date()}")
        else:
            print("No death crosses found.")
        print()
        return death_dates

    def execute_trades(self):
        golden_crosses = self.identify_golden_crosses()
        death_crosses = self.identify_death_crosses()
        print("Step 5: Executing trades...\n")

        if len(golden_crosses) == 0:
            print("No golden crosses; no trades executed.\n")
            return self

        for buy_date in golden_crosses:
            if self.position_open:
                continue  # skip if already holding

            buy_price = self.df.loc[buy_date, 'Close']
            max_shares = self.budget // buy_price
            self.position_open = True
            self.buy_price = buy_price
            self.shares_held = max_shares
            print(f"BUY: {self.shares_held} shares at ${self.buy_price:.2f} on {buy_date.date()}")

            # Find next death cross or force sell at end
            future_death = death_crosses[death_crosses > buy_date]
            if len(future_death) > 0:
                sell_date = future_death[0]
                sell_price = self.df.loc[sell_date, 'Close']
                print(f"SELL: {self.shares_held} shares at ${sell_price:.2f} on {sell_date.date()}\n")
            else:
                sell_date = self.df.index[-1]
                sell_price = self.df.loc[sell_date, 'Close']
                print(f"No death cross found after {buy_date.date()}, force selling on last day {sell_date.date()}")
                print(f"FORCE SELL: {self.shares_held} shares at ${sell_price:.2f}\n")

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
            print(f"Step X: Force closing position on last day {last_date.date()}")
            print(f"FORCE SELL: {self.shares_held} shares at ${sell_price:.2f}")
            print(f"Profit/Loss from this position: ${profit_loss:.2f}\n")

            self.trades.append({
             'buy_date': self.buy_date,
             'sell_date': last_date,
             'shares': self.shares_held,
             'buy_price': self.buy_price,
             'sell_price': sell_price,
             'profit_loss': profit_loss
         })
            self.position_open = False
        else:
            print("No open position to force close.\n")
        return self

    def report_results(self):
        print("Step 6: Evaluation & Results\n")
        total_profit = sum(t['profit_loss'] for t in self.trades)
        final_cash = self.budget + total_profit
        print(f"Initial Investment: ${self.budget:.2f}")
        print(f"Final Cash: ${final_cash:.2f}")
        print(f"Total Profit/Loss: ${total_profit:.2f}")
        print(f"Return: {(total_profit/self.budget)*100:.2f}%")
        print("\nAlgorithmic Trading Adventure Completed.\n")
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