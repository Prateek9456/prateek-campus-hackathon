import os

class RebalancerConfig:
    """
    Configuration settings for the Tactical Index Rebalancing Module.
    """
    # API Endpoint for fetching risk signals
    RISK_ENGINE_API_URL = os.getenv("RISK_ENGINE_API_URL", "http://localhost:8000/api/signals/latest")
    
    # Rebalancing constraints
    MAX_WEIGHT_PER_ASSET = 0.20  # Max 20% weight per stock to avoid over-concentration
    MIN_WEIGHT_PER_ASSET = 0.01  # Min 1% weight per stock
    
    # Base adjustment factor for sentiment
    # E.g., A sentiment score of +1.0 could adjust the weight by +5%
    SENTIMENT_ADJUSTMENT_FACTOR = 0.05
    
    # Thresholds for triggering rebalancing
    MIN_IMPACT_THRESHOLD = 4  # Only rebalance if impact score is >= 4
