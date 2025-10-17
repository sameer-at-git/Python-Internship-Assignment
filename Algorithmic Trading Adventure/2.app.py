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
        self.position_open = False
        self.buy_price = 0
        self.shares_held = 0
        self.budget = 5000
        
    def download_data(self):
        self.df = yfinance.download(self.symbol, start=self.start_date, end=self.end_date, interval="1d")
        self.df.columns = self.df.columns.droplevel(1)
        return self
        
    def clean_data(self):
        self.df = self.df[~self.df.index.duplicated(keep='first')]
        self.df = self.df.ffill()
        return self
        
    def calculate_indicators(self):
        self.df['MA50'] = self.df['Close'].rolling(window=50).mean()
        self.df['MA200'] = self.df['Close'].rolling(window=200).mean()
        return self
        
    def identify_golden_cross(self):
        self.df['Signal'] = 0
        mask = (self.df['MA50'] > self.df['MA200'])
        self.df['Signal'] = mask.astype(int)
        self.df['GoldenCross'] = self.df['Signal'].diff() == 1
        return self.df.index[self.df['GoldenCross']]
        
    def identify_death_cross(self):
        self.df['DeathCross'] = self.df['Signal'].diff() == -1
        return self.df.index[self.df['DeathCross']]
        
    def execute_strategy(self):
        golden_cross_dates = self.identify_golden_cross()
        
        if len(golden_cross_dates) == 0:
            print("No golden cross found in the given period")
            return self
            
        buy_date = golden_cross_dates[0]
        buy_price = self.df.loc[buy_date, 'Close']
        max_shares = self.budget // buy_price
        
        print(f"Golden Cross detected on {buy_date}")
        print(f"BUY: {max_shares} shares at ${buy_price:.2f}")
        
        self.position_open = True
        self.shares_held = max_shares
        self.buy_price = buy_price
        
        death_cross_dates = self.identify_death_cross()
        sell_dates_after_buy = death_cross_dates[death_cross_dates > buy_date]
        
        if len(sell_dates_after_buy) > 0:
            sell_date = sell_dates_after_buy[0]
            sell_price = self.df.loc[sell_date, 'Close']
            
            print(f"Death Cross detected on {sell_date}")
            print(f"SELL: {self.shares_held} shares at ${sell_price:.2f}")
            
            profit_loss = (sell_price - self.buy_price) * self.shares_held
            final_cash = self.shares_held * sell_price
            
            self.position_open = False
        else:
            sell_date = self.df.index[-1]
            sell_price = self.df['Close'].iloc[-1]
            
            print(f"No Death Cross found - Force closing on last day {sell_date}")
            print(f"FORCE SELL: {self.shares_held} shares at ${sell_price:.2f}")
            
            profit_loss = (sell_price - self.buy_price) * self.shares_held
            final_cash = self.shares_held * sell_price
            
            self.position_open = False
        
        print(f"\nInitial Investment: ${self.budget:.2f}")
        print(f"Final Cash: ${final_cash:.2f}")
        print(f"Profit/Loss: ${profit_loss:.2f}")
        print(f"Return: {(profit_loss/self.budget)*100:.2f}%")
        
        return self
        
    def run(self):
        print(f"Starting algorithmic trading for {self.symbol} ({self.start_date} to {self.end_date})")
        
        (self.download_data()
         .clean_data()
         .calculate_indicators()
         .execute_strategy())
        
        return self

if __name__ == "__main__":
    trader = AlgorithmicTrading("AAPL", "2018-01-01", "2023-12-31")
    trader.run()