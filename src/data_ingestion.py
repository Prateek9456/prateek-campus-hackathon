import pandas as pd
import json
import logging
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataIngestor:
    def __init__(self, source_type="mock"):
        """
        Initialize the Data Ingestor.
        :param source_type: Type of data source ('mock', 'api', etc.)
        """
        self.source_type = source_type
        logging.info(f"Initialized DataIngestor with source_type: {self.source_type}")

    def fetch_mock_data(self):
        """
        Fetch simulated financial news data for testing the pipeline.
        Returns a list of dictionaries containing news headlines.
        """
        logging.info("Fetching mock financial news data...")
        mock_news = [
            {
                "id": 1,
                "timestamp": datetime.now().isoformat(),
                "text": "Federal Reserve announces a surprise 50 bps rate cut to stimulate growth.",
                "source": "Financial Times Mock"
            },
            {
                "id": 2,
                "timestamp": datetime.now().isoformat(),
                "text": "Tech giant XYZ reports record Q3 earnings, beating analyst expectations by 15%.",
                "source": "WSJ Mock"
            },
            {
                "id": 3,
                "timestamp": datetime.now().isoformat(),
                "text": "Geopolitical tensions escalate in the Middle East, causing oil prices to spike.",
                "source": "Reuters Mock"
            }
        ]
        return mock_news

    def ingest(self):
        """
        Main ingestion method. Routes to the appropriate fetcher based on source_type.
        """
        if self.source_type == "mock":
            data = self.fetch_mock_data()
        else:
            raise NotImplementedError(f"Data source {self.source_type} not implemented yet.")
        
        # In a real scenario, this might push to a queue or a database.
        # For Phase 1, we just return it as a pandas DataFrame.
        df = pd.DataFrame(data)
        logging.info(f"Ingested {len(df)} records successfully.")
        return df

import os
import sys

# Ensure src is in path to import nlp_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nlp_engine import NLPEngine

if __name__ == "__main__":
    ingestor = DataIngestor(source_type="mock")
    data_df = ingestor.ingest()
    print("\nIngested Data Sample:")
    print(data_df.head())
    
    logging.info("Initializing NLP Engine for Sentiment Analysis...")
    nlp = NLPEngine()
    
    logging.info("Applying sentiment analysis to ingested data...")
    # Apply sentiment analysis
    sentiments = data_df['text'].apply(nlp.analyze_sentiment)
    
    # Unpack the dictionary returned by analyze_sentiment into separate columns
    data_df['sentiment_label'] = sentiments.apply(lambda x: x['label'])
    data_df['sentiment_score'] = sentiments.apply(lambda x: x['score'])
    data_df['sentiment_confidence'] = sentiments.apply(lambda x: x['confidence'])
    
    print("\nData with Sentiment Analysis:")
    print(data_df[['id', 'sentiment_label', 'sentiment_score', 'text']].head())
    
    # Save the mock data to our data directory for tracking
    output_path = "data/news_with_sentiment.csv"
    
    # Ensure we are saving relative to the project root
    if not os.path.exists('data'):
        os.makedirs('data')
        
    data_df.to_csv(output_path, index=False)
    logging.info(f"Saved enriched data to {output_path}")
