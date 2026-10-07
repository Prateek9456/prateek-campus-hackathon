from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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

# Add CORS middleware to allow the Streamlit dashboard or other modules to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global error handler for validation errors to ensure clean JSON responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Invalid request payload", "details": exc.errors()},
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

# Initialize NLP Engine globally for the API
try:
    from nlp_engine import NLPEngine
    logging.info("Initializing NLP Engine for API...")
    nlp = NLPEngine()
except Exception as e:
    logging.error(f"Failed to initialize NLP engine: {e}")
    nlp = None

@app.post("/api/signals/analyze", response_model=RiskSignalResponse)
def analyze_text_realtime(request: AnalyzeTextRequest):
    """
    On-the-fly analysis of a single text/headline.
    """
    if nlp is None:
        raise HTTPException(status_code=503, detail="NLP Engine is currently unavailable")
        
    try:
        # Run sentiment analysis
        sentiment = nlp.analyze_sentiment(request.text)
        
        # Run event classification
        event = nlp.classify_event(request.text)
        
        # Calculate impact
        impact = nlp.calculate_impact_score(request.text, sentiment['score'], event['event_class'])
        
        return {
            "id": None,
            "text": request.text,
            "sentiment_label": sentiment['label'],
            "sentiment_score": sentiment['score'],
            "sentiment_confidence": sentiment['confidence'],
            "event_class": event['event_class'],
            "event_confidence": event['classification_confidence'],
            "impact_score": impact
        }
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze text")

if __name__ == "__main__":
    logging.info("Starting API server on port 8000...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
