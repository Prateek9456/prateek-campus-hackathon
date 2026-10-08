import logging
import pandas as pd
from config import RebalancerConfig
from portfolio import MockPortfolio
from api_client import RiskEngineClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RebalanceEngine:
    """
    Core engine for the Tactical Index Rebalancing Module.
    """
    def __init__(self):
        self.portfolio = MockPortfolio()
        self.client = RiskEngineClient()
        self.config = RebalancerConfig()
        
    def execute_rebalance(self):
        """
        Fetches signals and executes the rebalancing algorithm.
        """
        signals = self.client.fetch_latest_signals()
        if not signals:
            logging.warning("No signals received. Skipping rebalance.")
            return self.portfolio.get_portfolio()
            
        logging.info("Starting portfolio rebalancing based on AI Risk Signals...")
        
        # Calculate aggregate sentiment
        # In a real scenario, sentiment would be mapped to specific tickers.
        # For this prototype, we simulate a macro-level adjustment.
        aggregate_sentiment = sum([s['sentiment_score'] for s in signals]) / len(signals)
        logging.info(f"Aggregate Market Sentiment: {aggregate_sentiment:.4f}")
        
        df = self.portfolio.get_portfolio()
        
        # Core Rebalancing Logic:
        # If sentiment is highly positive, we might overweight Tech/Consumer Discretionary.
        # If sentiment is highly negative, we might overweight defensive sectors (Healthcare, Staples).
        
        for index, row in df.iterrows():
            current_weight = row['current_weight']
            sector = row['sector']
            
            adjustment = 0
            
            # Simple heuristic algorithm
            if aggregate_sentiment > 0.2:
                # Bullish: Boost Growth/Cyclical
                if sector in ["Technology", "Consumer Discretionary", "Financials"]:
                    adjustment = self.config.SENTIMENT_ADJUSTMENT_FACTOR
                # Reduce Defensive
                elif sector in ["Consumer Staples", "Healthcare"]:
                    adjustment = -self.config.SENTIMENT_ADJUSTMENT_FACTOR
                    
            elif aggregate_sentiment < -0.2:
                # Bearish: Boost Defensive
                if sector in ["Consumer Staples", "Healthcare"]:
                    adjustment = self.config.SENTIMENT_ADJUSTMENT_FACTOR
                # Reduce Growth/Cyclical
                elif sector in ["Technology", "Consumer Discretionary", "Financials"]:
                    adjustment = -self.config.SENTIMENT_ADJUSTMENT_FACTOR
                    
            # Apply adjustment
            new_weight = current_weight + adjustment
            
            # Update dataframe
            df.at[index, 'current_weight'] = new_weight
            
        # Normalize weights to ensure they sum to 1.0 (100%)
        total_weight = df['current_weight'].sum()
        df['current_weight'] = df['current_weight'] / total_weight
        
        self.portfolio.portfolio_df = df
        logging.info("Rebalancing complete.")
        return df

if __name__ == "__main__":
    engine = RebalanceEngine()
    print("Initial Portfolio:")
    engine.portfolio.display_portfolio()
    
    print("\nExecuting Rebalance...")
    engine.execute_rebalance()
    
    print("\nPost-Rebalance Portfolio:")
    engine.portfolio.display_portfolio()
