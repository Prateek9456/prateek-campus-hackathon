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
        self.transaction_log = []
        
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
        
        # Determine dominant event classification (simplification for prototype)
        event_counts = {}
        for s in signals:
            cls = s['event_class']
            event_counts[cls] = event_counts.get(cls, 0) + 1
        dominant_event = max(event_counts, key=event_counts.get) if event_counts else "Unknown"
        logging.info(f"Dominant Market Event Theme: {dominant_event}")
        
        df = self.portfolio.get_portfolio()
        
        # Core Rebalancing Logic:
        # If sentiment is highly positive, we might overweight Tech/Consumer Discretionary.
        # If sentiment is highly negative, we might overweight defensive sectors (Healthcare, Staples).
        
        # Event Modifier Logic:
        # Geopolitical / Macroeconomic events trigger stronger defensive rotations.
        event_multiplier = 1.0
        if dominant_event in ["Geopolitical", "Macroeconomic"]:
            event_multiplier = 1.5
            logging.info("Applying high-volatility event multiplier to rebalancing weights.")
            
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
                    adjustment = self.config.SENTIMENT_ADJUSTMENT_FACTOR * event_multiplier
                # Reduce Growth/Cyclical
                elif sector in ["Technology", "Consumer Discretionary", "Financials"]:
                    adjustment = -self.config.SENTIMENT_ADJUSTMENT_FACTOR * event_multiplier
                    
            # Apply adjustment
            new_weight = current_weight + adjustment
            
            # Apply Clamping based on config
            new_weight = max(self.config.MIN_WEIGHT_PER_ASSET, min(self.config.MAX_WEIGHT_PER_ASSET, new_weight))
            
            # Log transaction if weight changed
            if abs(new_weight - current_weight) > 0.001:
                self.transaction_log.append({
                    "ticker": row['ticker'],
                    "old_weight": round(current_weight, 4),
                    "new_weight": round(new_weight, 4),
                    "action": "BUY" if new_weight > current_weight else "SELL"
                })
            
            # Update dataframe
            df.at[index, 'current_weight'] = new_weight
            
        # Normalize weights to ensure they sum to 1.0 (100%)
        total_weight = df['current_weight'].sum()
        df['current_weight'] = df['current_weight'] / total_weight
        
        self.portfolio.portfolio_df = df
        logging.info(f"Rebalancing complete. Recorded {len(self.transaction_log)} transaction events.")
        return df

    def display_transaction_log(self):
        if not self.transaction_log:
            print("No transactions recorded.")
            return
            
        print("\n--- Transaction Log ---")
        log_df = pd.DataFrame(self.transaction_log)
        print(log_df.to_string(index=False))
        print("-----------------------\n")

if __name__ == "__main__":
    engine = RebalanceEngine()
    print("Initial Portfolio:")
    engine.portfolio.display_portfolio()
    
    print("\nExecuting Rebalance...")
    engine.execute_rebalance()
    
    print("\nPost-Rebalance Portfolio:")
    engine.portfolio.display_portfolio()
    
    engine.display_transaction_log()
