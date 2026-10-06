import logging
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NLPEngine:
    def __init__(self, sentiment_model="ProsusAI/finbert", zero_shot_model="facebook/bart-large-mnli"):
        """
        Initialize the NLP Risk Engine with models for sentiment analysis and event classification.
        """
        logging.info(f"Loading Sentiment model: {sentiment_model}...")
        self.tokenizer = AutoTokenizer.from_pretrained(sentiment_model)
        self.model = AutoModelForSequenceClassification.from_pretrained(sentiment_model)
        
        # Check if GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        logging.info(f"Sentiment model loaded successfully on device: {self.device}")
        
        logging.info(f"Loading Zero-Shot Classification model: {zero_shot_model}...")
        # Using pipeline for zero-shot for simplicity and robustness
        from transformers import pipeline
        # device=0 for CUDA, -1 for CPU
        pipeline_device = 0 if torch.cuda.is_available() else -1
        self.classifier = pipeline("zero-shot-classification", model=zero_shot_model, device=pipeline_device)
        logging.info("Zero-Shot Classification model loaded successfully.")

    def analyze_sentiment(self, text: str):
        """
        Analyze the sentiment of a given financial text.
        Returns a dictionary with sentiment label and a numerical score (-1.0 to 1.0).
        """
        # FinBERT labels: 0 -> positive, 1 -> negative, 2 -> neutral
        # We will map these to a continuous score
        
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
        
        # Get the predicted class index
        pred_idx = torch.argmax(probabilities, dim=-1).item()
        
        # FinBERT specific mapping
        labels = ["positive", "negative", "neutral"]
        predicted_label = labels[pred_idx]
        
        # Calculate a continuous score:
        # positive prob - negative prob (ignoring neutral for the direct scale, or scaling it)
        # This gives a clean -1.0 to 1.0 signal for our downstream rebalancer
        pos_prob = probabilities[0][0].item()
        neg_prob = probabilities[0][1].item()
        
        sentiment_score = pos_prob - neg_prob
        
        return {
            "label": predicted_label,
            "score": round(sentiment_score, 4),
            "confidence": round(probabilities[0][pred_idx].item(), 4)
        }

    def classify_event(self, text: str):
        """
        Categorize the financial event into predefined classes using zero-shot classification.
        """
        candidate_labels = [
            "Geopolitical", 
            "Macroeconomic", 
            "Credit Event", 
            "Merger and Acquisition", 
            "Product Launch",
            "Regulatory",
            "Earnings Report"
        ]
        
        # Perform classification
        result = self.classifier(text, candidate_labels)
        
        # The highest scoring label is the first in the list
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        
        return {
            "event_class": top_label,
            "classification_confidence": round(top_score, 4)
        }

if __name__ == "__main__":
    # Quick test of the engine
    engine = NLPEngine()
    
    test_texts = [
        "The company reported a massive profit increase for Q3.",
        "Supply chain disruptions have caused a severe drop in quarterly revenue.",
        "The CEO mentioned that the new product launch is proceeding as planned."
    ]
    
    print("\n--- NLP Engine Sentiment Test ---")
    for t in test_texts:
        sentiment_result = engine.analyze_sentiment(t)
        event_result = engine.classify_event(t)
        print(f"Text: {t}")
        print(f"Sentiment: {sentiment_result}")
        print(f"Event Class: {event_result}\n")
