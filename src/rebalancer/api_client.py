import requests
import logging
from config import RebalancerConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RiskEngineClient:
    """
    Client to interact with the core AI/NLP Risk Engine API.
    """
    def __init__(self):
        self.api_url = RebalancerConfig.RISK_ENGINE_API_URL
        logging.info(f"Initialized RiskEngineClient targeting {self.api_url}")

    def fetch_latest_signals(self):
        """
        Fetches the latest risk signals from the core engine.
        For the hackathon demo, if the API is down, we can fallback to reading the CSV directly.
        """
        try:
            logging.info("Fetching latest risk signals from API...")
            response = requests.get(self.api_url)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "success":
                signals = data.get("data", [])
                logging.info(f"Successfully retrieved {len(signals)} signals.")
                return signals
            else:
                logging.warning("API returned a non-success status.")
                return []
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to Risk Engine API: {e}")
            logging.info("Attempting local CSV fallback...")
            return self._fallback_load_csv()

    def _fallback_load_csv(self):
        import pandas as pd
        import os
        try:
            # Try to find the file relative to the script or root
            paths_to_try = [
                "../../data/news_with_sentiment_and_impact.csv",
                "../data/news_with_sentiment_and_impact.csv",
                "data/news_with_sentiment_and_impact.csv"
            ]
            
            for path in paths_to_try:
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    records = df.to_dict(orient="records")
                    logging.info(f"Fallback successful. Loaded {len(records)} records from CSV.")
                    return records
                    
            logging.error("Fallback failed: CSV file not found.")
            return []
        except Exception as e:
            logging.error(f"Error during CSV fallback: {e}")
            return []

if __name__ == "__main__":
    client = RiskEngineClient()
    signals = client.fetch_latest_signals()
    if signals:
        print(f"Sample Signal: {signals[0]}")
