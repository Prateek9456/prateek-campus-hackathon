from fastapi import FastAPI
import uvicorn
import logging

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

if __name__ == "__main__":
    logging.info("Starting API server on port 8000...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
