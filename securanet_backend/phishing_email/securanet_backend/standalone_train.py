#!/usr/bin/env python
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import re

def extract_structured_features(header):
    """Extract structured features from email header"""
    # Simple feature extraction without Django dependencies
    suspicious_keywords = [
        "urgent", "suspended", "verify", "update", "password", "account", 
        "login", "click", "confirm", "security", "alert", "reset", 
        "invoice", "payment", "bank", "limited", "immediately", "action required"
    ]
    
    # Extract basic features
    subject = ""
    sender_domain = ""
    has_suspicious = 0
    
    # Simple parsing
    lines = header.split('\n')
    for line in lines:
        if line.lower().startswith('subject:'):
            subject = line.split(':', 1)[1].strip() if ':' in line else ""
        elif line.lower().startswith('from:'):
            from_line = line.split(':', 1)[1].strip() if ':' in line else ""
            if '@' in from_line:
                sender_domain = from_line.split('@')[-1].strip()
    
    has_suspicious = int(any(word in subject.lower() for word in suspicious_keywords))
    
    return [
        sender_domain,
        subject,
        0,  # spf (simplified)
        0,  # dkim (simplified)
        0,  # dmarc (simplified)
        0,  # risk_score (simplified)
        len(lines),  # num_hops (approximated)
        has_suspicious
    ]

def train_header_classifier():
    """Trains a pipeline for email header classification"""
    dataset_path = os.path.join('myapp', 'ml', 'dataset', 'headers.csv')
    
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at: {dataset_path}")
        return None
    
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    X = df['text']
    y = df['label']
    
    # Extract structured features for all headers
    print("Extracting structured features...")
    structured_X = np.array([extract_structured_features(h) for h in X])
    
    # Split the data
    X_train, X_test, y_train, y_test, struct_train, struct_test = train_test_split(
        X, y, structured_X, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Setting up feature pipelines...")
    # Pipelines for text and structured features
    text_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        ))
    ])
    
    struct_pipeline = Pipeline([
        ('to_array', FunctionTransformer(lambda x: x, validate=False)),
        ('scaler', StandardScaler(with_mean=False)),
    ])
    
    # Combine features
    union = FeatureUnion([
        ('text', text_pipeline),
        ('struct', struct_pipeline)
    ])
    
    print("Fitting feature union...")
    # Fit union on training data
    union.fit(list(X_train), struct_train)
    
    # Transform both train and test
    print("Transforming features...")
    X_train_combined = union.transform(list(X_train), struct_train)
    X_test_combined = union.transform(list(X_test), struct_test)
    
    # Train classifier
    print("Training classifier...")
    clf = LogisticRegression(random_state=42, max_iter=1000, C=1.0)
    clf.fit(X_train_combined, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test_combined)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the pipeline and classifier together
    model_path = os.path.join('myapp', 'ml', 'header_classifier.pkl')
    joblib.dump({'union': union, 'clf': clf}, model_path)
    print(f"\nModel saved to: {model_path}")
    
    return clf

if __name__ == "__main__":
    print("Starting email header classifier training...")
    train_header_classifier()
    print("Training completed!") 