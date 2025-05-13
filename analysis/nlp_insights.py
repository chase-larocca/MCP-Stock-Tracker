from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
import torch

# Load FinBERT model + tokenizer
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

labels = ["positive", "neutral", "negative"]

def analyze_sentiment(text: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = softmax(outputs.logits, dim=1).squeeze().tolist()
    best_idx = int(torch.argmax(outputs.logits))

    return {
        "sentiment": labels[best_idx],
        "confidence": round(probs[best_idx], 3)
    }
