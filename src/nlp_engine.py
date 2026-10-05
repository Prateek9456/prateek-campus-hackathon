import logging
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NLPEngine:
    def __init__(self, model_name="ProsusAI/finbert"):
        """
        Initialize the NLP Risk Engine with a pre-trained Financial BERT model.
        """
        logging.info(f"Loading NLP model: {model_name}. This might take a moment on first run...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Check if GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        logging.info(f"Model loaded successfully on device: {self.device}")

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
        result = engine.analyze_sentiment(t)
        print(f"Text: {t}")
        print(f"Result: {result}\n")
