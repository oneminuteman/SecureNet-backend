#!/usr/bin/env python
import csv
import os
import re
from collections import Counter
import pickle

def simple_feature_extraction(header):
    """Extract simple features from email header"""
    header_lower = header.lower()
    
    # Basic features
    features = {
        'length': len(header),
        'num_lines': header.count('\n'),
        'has_subject': int('subject:' in header_lower),
        'has_from': int('from:' in header_lower),
        'has_to': int('to:' in header_lower),
        'has_date': int('date:' in header_lower),
        'has_message_id': int('message-id:' in header_lower),
        'has_received': int('received:' in header_lower),
        'has_return_path': int('return-path:' in header_lower),
        'has_x_mailer': int('x-mailer:' in header_lower),
        'has_user_agent': int('user-agent:' in header_lower),
        'has_mime_version': int('mime-version:' in header_lower),
        'has_content_type': int('content-type:' in header_lower),
        'has_content_transfer_encoding': int('content-transfer-encoding:' in header_lower),
    }
    
    # Suspicious keywords
    suspicious_words = [
        'urgent', 'suspended', 'verify', 'update', 'password', 'account',
        'login', 'click', 'confirm', 'security', 'alert', 'reset',
        'invoice', 'payment', 'bank', 'limited', 'immediately', 'action required'
    ]
    
    for word in suspicious_words:
        features[f'has_{word}'] = int(word in header_lower)
    
    return features

def simple_classify(header, feature_importance, threshold=0.5):
    """Classify email header using feature importance"""
    features = simple_feature_extraction(header)
    score = 0
    
    # Weight features by importance
    for feature, value in features.items():
        if feature in feature_importance:
            score += value * feature_importance[feature]
    
    # Threshold-based classification
    return 'phishing' if score > threshold else 'legitimate'

def train_simple_classifier():
    """Train a simple rule-based classifier"""
    dataset_path = os.path.join('myapp', 'ml', 'dataset', 'headers.csv')
    
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at: {dataset_path}")
        return None
    
    print(f"Loading dataset from: {dataset_path}")
    
    # Load data
    headers = []
    labels = []
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            headers.append(row['text'])
            labels.append(row['label'])
    
    print(f"Loaded {len(headers)} samples")
    print(f"Label distribution: {Counter(labels)}")
    
    # Extract features
    print("Extracting features...")
    all_features = []
    for header in headers:
        features = simple_feature_extraction(header)
        all_features.append(features)
    
    # Simple rule-based classification
    print("Training simple classifier...")
    
    # Calculate feature importance based on correlation with labels
    feature_importance = {}
    for feature_name in all_features[0].keys():
        positive_count = 0
        total_positive = 0
        total_negative = 0
        
        for i, features in enumerate(all_features):
            if labels[i] == 'phishing':
                total_positive += 1
                if features[feature_name] > 0:
                    positive_count += 1
            else:
                total_negative += 1
        
        if total_positive > 0:
            feature_importance[feature_name] = positive_count / total_positive
        else:
            feature_importance[feature_name] = 0
    
    # Sort features by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 10 most important features:")
    for feature, importance in sorted_features[:10]:
        print(f"  {feature}: {importance:.3f}")
    
    # Evaluate on training data
    correct = 0
    total = len(headers)
    
    for i, header in enumerate(headers):
        prediction = simple_classify(header, feature_importance)
        if prediction == labels[i]:
            correct += 1
    
    accuracy = correct / total
    print(f"\nTraining Accuracy: {accuracy:.3f} ({correct}/{total})")
    
    # Save the classifier data (without the function)
    classifier_data = {
        'feature_importance': feature_importance,
        'threshold': 0.5
    }
    
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(classifier_data, f)
    
    print(f"Simple classifier saved to: {model_path}")
    
    return classifier_data

if __name__ == "__main__":
    print("Starting simple email header classifier training...")
    train_simple_classifier()
    print("Training completed!") 