import os
import re
import json
import logging
import numpy as np
import torch
from pathlib import Path
from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    pipeline,
    set_seed,
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from sklearn.utils.class_weight import compute_class_weight

# ============================ CONFIG ============================
MODEL_DIR = Path("securanet_backend/phishing_model")
LOGGING_DIR = MODEL_DIR / "logs"
ENHANCED_DATASET_PATH = "enhanced_phishing_dataset.json"
LOGGING_DIR.mkdir(parents=True, exist_ok=True)

# Set logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOGGING_DIR / "training.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

set_seed(42)

# Critical samples to add (hand-picked edge cases)
CRITICAL_SAMPLES = [
    # Short phishing examples
    {"text": "Don't miss out you!", "label": 1},
    {"text": "Last chance!", "label": 1},
    {"text": "Limited offer!", "label": 1},
    {"text": "Claim now!", "label": 1},
    {"text": "Act fast!", "label": 1},
    
    # Legitimate urgency
    {"text": "Don't miss our annual sale", "label": 0},
    {"text": "Limited seats for webinar", "label": 0},
    {"text": "Final hours: Summer clearance", "label": 0},
    {"text": "Early bird discount ending soon", "label": 0},
    
    # Grammatical variations
    {"text": "Dont miss out u!", "label": 1},
    {"text": "Verfy your accont", "label": 1},
    {"text": "Urgent: Acount suspenshion", "label": 1},
    {"text": "Win $$$ prize!", "label": 1},
    
    # Mixed-content examples
    {"text": "Your package arrives tomorrow. Claim discount now!", "label": 0},
    {"text": "Account alert: Limited offer inside", "label": 1},
    {"text": "Meeting reminder: Special offer for attendees", "label": 0},
    {"text": "Security notice: Verify your account", "label": 0}
]

# ============================ DATASET ENHANCEMENT ============================
def preprocess_text(text):
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r"\s+", " ", text.strip().lower())

def create_enhanced_dataset(original_data):
    """Create and save enhanced dataset with critical samples and augmentation"""
    # Remove duplicates
    unique_data = {preprocess_text(item['text']): item for item in original_data}
    unique_data = list(unique_data.values())
    
    # Add critical samples
    enhanced_data = unique_data + CRITICAL_SAMPLES
    
    # Add augmented samples
    augmented = []
    for item in enhanced_data:
        text = item["text"]
        label = item["label"]
        
        # Add typo variations for phishing
        if label == 1 and len(text) < 60:
            # Duplicate vowels
            augmented.append({
                "text": re.sub(r'([aeiou])', r'\1\1', text),
                "label": 1
            })
            # Extra punctuation
            augmented.append({
                "text": text.replace('!', '!!').replace(' ', '  '),
                "label": 1
            })
            
        # Add synonym replacement for legit
        if label == 0 and len(text) > 40:
            augmented.append({
                "text": text.replace("don't miss", "remember to join"),
                "label": 0
            })
            augmented.append({
                "text": text.replace("limited", "exclusive"),
                "label": 0
            })
    
    # Combine all data
    full_data = enhanced_data + augmented
    
    # Balance classes
    phishing = [item for item in full_data if item['label'] == 1]
    legitimate = [item for item in full_data if item['label'] == 0]
    
    min_size = min(len(phishing), len(legitimate))
    balanced_data = (
        phishing[:min_size] + 
        legitimate[:min_size]
    )
    
    # Shuffle and save
    np.random.shuffle(balanced_data)
    
    # Preprocess all text
    for item in balanced_data:
        item["text"] = preprocess_text(item["text"])
    
    with open(ENHANCED_DATASET_PATH, 'w') as f:
        json.dump(balanced_data, f, indent=2)
    
    logger.info(f"Created enhanced dataset with {len(balanced_data)} samples "
                f"({min_size} phishing, {min_size} legitimate)")
    return balanced_data

def load_dataset():
    """Load dataset, create enhanced version if needed"""
    if Path(ENHANCED_DATASET_PATH).exists():
        logger.info(f"Loading enhanced dataset from {ENHANCED_DATASET_PATH}")
        with open(ENHANCED_DATASET_PATH, 'r') as f:
            data = json.load(f)
            return Dataset.from_dict({"text": [item["text"] for item in data], 
                                      "label": [item["label"] for item in data]})
    
    logger.info("Creating enhanced dataset...")
    
    # Load original dataset from file
    ORIGINAL_DATASET_PATH = "phishing_dataset.json"
    try:
        with open(ORIGINAL_DATASET_PATH, 'r') as f:
            original_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Original dataset file not found at: {ORIGINAL_DATASET_PATH}")
        return None
    
    enhanced_data = create_enhanced_dataset(original_data)
    return Dataset.from_dict({"text": [item["text"] for item in enhanced_data], 
                             "label": [item["label"] for item in enhanced_data]})

# ============================ TOKENIZATION ============================
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

# ============================ METRICS & THRESHOLD CALIBRATION ============================
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=-1)
    return {
        "f1": f1_score(labels, preds),
        "accuracy": accuracy_score(labels, preds),
        "precision": precision_score(labels, preds),
        "recall": recall_score(labels, preds),
    }

def find_optimal_threshold(trainer, dataset):
    """Find best decision threshold using validation set"""
    predictions = trainer.predict(dataset)
    probs = torch.softmax(torch.tensor(predictions.predictions), dim=-1).numpy()
    phishing_probs = probs[:, 1]
    labels = predictions.label_ids

    best_thresh = 0.4
    best_f1 = 0
    for thresh in np.arange(0.3, 0.7, 0.01):
        preds = (phishing_probs >= thresh).astype(int)
        f1 = f1_score(labels, preds)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh

    logger.info(f"Optimal threshold: {best_thresh:.3f} (F1: {best_f1:.4f})")
    return best_thresh

# ============================ TRAINING ============================
class WeightedLossTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss

def main():
    # Load dataset
    dataset = load_dataset()
    if dataset is None or len(dataset) == 0:
        logger.error("No valid dataset available for training")
        return None, None, 0.4

    # Split dataset
    train_val = dataset.train_test_split(test_size=0.3)
    train_dataset_raw = train_val["train"]
    val_dataset_raw = train_val["test"]
    
    # Tokenize
    global tokenizer
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    
    train_tokenized = train_dataset_raw.map(tokenize_function, batched=True, remove_columns=["text"])
    val_tokenized = val_dataset_raw.map(tokenize_function, batched=True, remove_columns=["text"])
    
    # Prepare for training
    train_tokenized = train_tokenized.rename_column("label", "labels").with_format("torch")
    val_tokenized = val_tokenized.rename_column("label", "labels").with_format("torch")
    
    # Model and weights
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
    
    # FIXED: Proper class weight calculation with numpy arrays
    labels = train_dataset_raw["label"]
    class_labels = np.unique(labels)  # Get unique class labels as numpy array
    class_weights = compute_class_weight(
        "balanced", 
        classes=class_labels,
        y=labels
    )
    weights = torch.tensor(class_weights, dtype=torch.float)
    logger.info(f"Class weights: {weights.tolist()}")

    # Training configuration
    training_args = TrainingArguments(
        output_dir=str(MODEL_DIR),
        evaluation_strategy="steps",
        eval_steps=200,
        save_steps=200,
        logging_dir=str(LOGGING_DIR),
        logging_steps=100,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=32,
        num_train_epochs=7,
        learning_rate=2e-5,
        weight_decay=0.01,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        seed=42,
        #fp16=True,
        remove_unused_columns=False,
    )

    trainer = WeightedLossTrainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=val_tokenized,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        class_weights=weights,
    )

    # Train and save
    logger.info("Starting training...")
    trainer.train()
    logger.info("Training complete.")
    
    # Find optimal threshold
    optimal_threshold = find_optimal_threshold(trainer, val_tokenized)
    
    trainer.save_model(str(MODEL_DIR))
    tokenizer.save_pretrained(str(MODEL_DIR))
    
    # Create classifier with confidence levels
    classifier = pipeline("text-classification", model=str(MODEL_DIR), tokenizer=str(MODEL_DIR), return_all_scores=True)
    
    def classify_text(text, threshold=optimal_threshold):
        text = preprocess_text(text)
        result = classifier(text)[0]
        
        # Get probabilities
        prob_phish = next(pred['score'] for pred in result if pred['label'] == 'LABEL_1')
        prob_legit = next(pred['score'] for pred in result if pred['label'] == 'LABEL_0')
        
        # Calculate confidence
        diff = abs(prob_phish - prob_legit)
        if diff > 0.3:
            confidence = "high"
        elif diff > 0.15:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "text": text,
            "phishing_probability": prob_phish,
            "is_phishing": prob_phish >= threshold,
            "confidence": confidence
        }

    return classifier, classify_text, optimal_threshold

# ============================ RUN ============================
if __name__ == "__main__":
    classifier, classify_func, threshold = main()
    if classifier and classify_func:
        tests = [
            "Don't miss out you!",
            "URGENT: Verify account now!",
            "Meeting reminder: 2pm in conference room",
            "Claim your $1000 prize now!",
            "Your package delivery is scheduled for tomorrow"
        ]
        
        print(f"\nOptimal Threshold: {threshold:.3f}\n")
        for text in tests:
            result = classify_func(text)
            print(f"Text: {text}")
            print(f"→ Phishing: {result['is_phishing']} ({result['phishing_probability']:.2%})")
            print(f"→ Confidence: {result['confidence']}\n")

    # Save enhanced dataset path to config
    with open("dataset_config.json", "w") as f:
        json.dump({"enhanced_dataset": ENHANCED_DATASET_PATH}, f)
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--threshold", type=float, default=0.4)
    # args = parser.parse_args()
    # classifier, classify_func = main()
    # result = classify_func("Enter your details to claim reward!", threshold=args.threshold)
    # print(result)
    # Optional: enable CLI via argparse
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--threshold", type=float, default=0.4)
    # args = parser.parse_args()
    # classifier, classify_func = main()
    # result = classify_func("Enter your details to claim reward!", threshold=args.threshold)
    # print(result)
