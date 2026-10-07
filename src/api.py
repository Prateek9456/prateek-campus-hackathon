from fastapi import FastAPI, HTTPException
import uvicorn
import logging
import pandas as pd
from schemas import SignalListResponse, AnalyzeTextRequest, RiskSignalResponse

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="AI/NLP Risk Engine API",
    description="API for distributing real-time financial risk signals to downstream modules.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """
    Health check endpoint.
    """
    return {"status": "online", "message": "Welcome to the AI/NLP Risk Engine API"}

@app.get("/api/status")
def api_status():
    """
    Returns the status of the core services.
    """
    return {
        "api": "operational",
        "nlp_engine": "standby",
        "data_ingestion": "standby"
    }

@app.get("/api/signals/latest", response_model=SignalListResponse)
def get_latest_signals():
    """
    Fetches the latest pre-processed risk signals from the data pipeline output.
    """
    try:
        df = pd.read_csv("../data/news_with_sentiment_and_impact.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("data/news_with_sentiment_and_impact.csv")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Processed signals not found")
            
    # Convert dataframe to list of dicts matching our schema
    records = df.to_dict(orient="records")
    return {
        "status": "success",
        "count": len(records),
        "data": records
    }

if __name__ == "__main__":
    logging.info("Starting API server on port 8000...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
