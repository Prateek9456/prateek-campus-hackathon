import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockPortfolio:
    """
    Simulates a synthetic stock index portfolio (e.g., a subset of S&P 100).
    Tracks the tickers, sector metadata, and their current weights.
    """
    
    def __init__(self):
        # A mock index of 10 major companies across different sectors
        self.holdings = [
            {"ticker": "AAPL", "sector": "Technology", "initial_weight": 0.15},
            {"ticker": "MSFT", "sector": "Technology", "initial_weight": 0.15},
            {"ticker": "GOOGL", "sector": "Technology", "initial_weight": 0.10},
            {"ticker": "AMZN", "sector": "Consumer Discretionary", "initial_weight": 0.10},
            {"ticker": "JPM", "sector": "Financials", "initial_weight": 0.10},
            {"ticker": "JNJ", "sector": "Healthcare", "initial_weight": 0.10},
            {"ticker": "XOM", "sector": "Energy", "initial_weight": 0.08},
            {"ticker": "WMT", "sector": "Consumer Staples", "initial_weight": 0.08},
            {"ticker": "PG", "sector": "Consumer Staples", "initial_weight": 0.07},
            {"ticker": "BA", "sector": "Industrials", "initial_weight": 0.07},
        ]
        
        # Initialize current weights
        self.portfolio_df = pd.DataFrame(self.holdings)
        self.portfolio_df['current_weight'] = self.portfolio_df['initial_weight']
        
        logging.info("Initialized mock S&P index portfolio with 10 assets.")

    def get_portfolio(self):
        """Returns the current state of the portfolio."""
        return self.portfolio_df.copy()

    def display_portfolio(self):
        """Prints the current portfolio nicely formatted."""
        print("\n--- Current Portfolio Weights ---")
        df_display = self.portfolio_df[['ticker', 'sector', 'current_weight']].copy()
        df_display['current_weight'] = df_display['current_weight'].apply(lambda x: f"{x:.1%}")
        print(df_display.to_string(index=False))
        print(f"Total Weight: {self.portfolio_df['current_weight'].sum():.1%}\n")

if __name__ == "__main__":
    # Quick test
    portfolio = MockPortfolio()
    portfolio.display_portfolio()
