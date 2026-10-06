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

    def calculate_impact_score(self, text: str, sentiment_score: float, event_class: str):
        """
        Calculates a simulated severity/impact score from 1 to 10.
        In a real scenario, this would involve historical backtesting.
        For this prototype, it uses a heuristic combining sentiment magnitude,
        event type baseline, and keyword triggers.
        """
        # Base impact from sentiment magnitude (0 to 5)
        base_impact = abs(sentiment_score) * 5
        
        # Event type modifiers
        event_multipliers = {
            "Macroeconomic": 1.5,
            "Geopolitical": 1.4,
            "Merger and Acquisition": 1.2,
            "Regulatory": 1.2,
            "Credit Event": 1.3,
            "Earnings Report": 1.1,
            "Product Launch": 1.0
        }
        
        multiplier = event_multipliers.get(event_class, 1.0)
        
        # Keyword heuristic boosters
        text_lower = text.lower()
        boost = 0
        high_impact_words = ["surprise", "massive", "crisis", "plunge", "spike", "record", "unexpected"]
        for word in high_impact_words:
            if word in text_lower:
                boost += 1.5
                
        # Calculate final score and clamp between 1 and 10
        final_score = (base_impact * multiplier) + boost
        final_score = max(1, min(10, round(final_score)))
        
        return final_score

if __name__ == "__main__":
    # Quick test of the engine
    engine = NLPEngine()
    
    test_texts = [
        "The company reported a massive profit increase for Q3.",
        "Supply chain disruptions have caused a severe drop in quarterly revenue.",
        "Geopolitical tensions escalate in the Middle East, causing oil prices to spike."
    ]
    
    print("\n--- NLP Engine Sentiment Test ---")
    for t in test_texts:
        sentiment_result = engine.analyze_sentiment(t)
        event_result = engine.classify_event(t)
        impact = engine.calculate_impact_score(t, sentiment_result['score'], event_result['event_class'])
        print(f"Text: {t}")
        print(f"Sentiment: {sentiment_result}")
        print(f"Event Class: {event_result}")
        print(f"Impact Score: {impact}/10\n")
