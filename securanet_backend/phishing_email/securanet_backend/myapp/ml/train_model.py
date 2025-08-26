import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import re
from ..header_tools.header_parser import analyze_header
from ..header_tools.risk_scoring import score_risk

def extract_structured_features(header):
    parsed = analyze_header(header)
    summary = parsed.get('parsed_headers', {}).get('summary', {})
    dns = parsed.get('dns_checks', {})
    risk = score_risk(parsed.get('parsed_headers', {}), dns, parsed.get('ip_info', {}))
    routing = parsed.get('parsed_headers', {}).get('routing', [])
    suspicious_keywords = [
        "urgent", "suspended", "verify", "update", "password", "account", "login", "click", "confirm", "security", "alert", "reset", "invoice", "payment", "bank", "limited", "immediately", "action required"
    ]
    subject = summary.get('subject', '')
    has_suspicious = int(any(word in subject.lower() for word in suspicious_keywords))
    return [
        summary.get('from', {}).get('email', '').split('@')[-1] if summary.get('from', {}).get('email') else '',  # sender domain
        subject,
        int(dns.get('spf', {}).get('has_spf', 0)),
        int(dns.get('dkim', {}).get('has_dkim', 0)),
        int(dns.get('dmarc', {}).get('has_dmarc', 0)),
        risk.get('risk_score', 0),
        len(routing),
        has_suspicious
    ]

def structured_feature_names():
    return [
        'sender_domain', 'subject', 'spf', 'dkim', 'dmarc', 'risk_score', 'num_hops', 'has_suspicious_keyword'
    ]

def train_header_classifier():
    """
    Trains a pipeline for email header classification using both TF-IDF and structured features.
    """
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset', 'headers.csv')
    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    X = df['text']
    y = df['label']
    # Extract structured features for all headers
    structured_X = np.array([extract_structured_features(h) for h in X])
    # Split the data
    X_train, X_test, y_train, y_test, struct_train, struct_test = train_test_split(
        X, y, structured_X, test_size=0.2, random_state=42, stratify=y
    )
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
    # Fit union on training data
    union.fit(list(X_train), struct_train)
    # Transform both train and test
    X_train_combined = union.transform(list(X_train), struct_train)
    X_test_combined = union.transform(list(X_test), struct_test)
    # Train classifier
    clf = LogisticRegression(random_state=42, max_iter=1000, C=1.0)
    clf.fit(X_train_combined, y_train)
    y_pred = clf.predict(X_test_combined)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    # Save the pipeline and classifier together
    model_path = os.path.join(os.path.dirname(__file__), 'header_classifier.pkl')
    joblib.dump({'union': union, 'clf': clf}, model_path)
    print(f"\nModel saved to: {model_path}")
    return clf

if __name__ == "__main__":
    train_header_classifier() 