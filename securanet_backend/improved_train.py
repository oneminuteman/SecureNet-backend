#!/usr/bin/env python
import csv
import os
import re
from collections import Counter
import pickle
import numpy as np

def improved_feature_extraction(header):
    """Extract improved features from email header"""
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
    
    # High-risk suspicious keywords (stronger weight)
    high_risk_words = [
        'urgent', 'suspended', 'verify', 'password', 'account',
        'login', 'click', 'confirm', 'reset', 'limited', 'immediately'
    ]
    
    # Medium-risk suspicious keywords
    medium_risk_words = [
        'update', 'security', 'alert', 'invoice', 'payment', 'bank',
        'action required', 'expire', 'verify', 'confirm'
    ]
    
    # Low-risk keywords (legitimate business terms)
    legitimate_words = [
        'order', 'shipped', 'delivery', 'confirmation', 'receipt',
        'meeting', 'schedule', 'appointment', 'newsletter', 'update'
    ]
    
    # Add high-risk features with higher weight
    for word in high_risk_words:
        features[f'high_risk_{word}'] = int(word in header_lower) * 2
    
    # Add medium-risk features
    for word in medium_risk_words:
        features[f'medium_risk_{word}'] = int(word in header_lower)
    
    # Add legitimate features (negative weight)
    for word in legitimate_words:
        features[f'legitimate_{word}'] = int(word in header_lower) * -1
    
    # Additional features
    features['has_html_content'] = int('text/html' in header_lower)
    features['has_plain_content'] = int('text/plain' in header_lower)
    features['exclamation_count'] = header.count('!')
    features['question_count'] = header.count('?')
    features['uppercase_ratio'] = sum(1 for c in header if c.isupper()) / len(header) if len(header) > 0 else 0
    
    return features

def improved_classify(header, feature_importance, threshold=0.5):
    """Classify email header using improved feature importance"""
    features = improved_feature_extraction(header)
    score = 0
    
    # Weight features by importance
    for feature, value in features.items():
        if feature in feature_importance:
            score += value * feature_importance[feature]
    
    # Threshold-based classification
    return 'phishing' if score > threshold else 'legitimate', score

def find_optimal_threshold(headers, labels, feature_importance):
    """Find optimal threshold for best F1 score"""
    thresholds = np.arange(0.1, 2.0, 0.1)
    best_f1 = 0
    best_threshold = 0.5
    
    for threshold in thresholds:
        tp, tn, fp, fn = 0, 0, 0, 0
        
        for header, label in zip(headers, labels):
            prediction, _ = improved_classify(header, feature_importance, threshold)
            
            if prediction == 'phishing' and label == 'phishing':
                tp += 1
            elif prediction == 'legitimate' and label == 'legitimate':
                tn += 1
            elif prediction == 'phishing' and label == 'legitimate':
                fp += 1
            elif prediction == 'legitimate' and label == 'phishing':
                fn += 1
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    return best_threshold, best_f1

def train_improved_classifier():
    """Train an improved rule-based classifier"""
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
    print("Extracting improved features...")
    all_features = []
    for header in headers:
        features = improved_feature_extraction(header)
        all_features.append(features)
    
    # Calculate feature importance based on correlation with labels
    print("Calculating feature importance...")
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
    
    # Find optimal threshold
    print("Finding optimal threshold...")
    optimal_threshold, best_f1 = find_optimal_threshold(headers, labels, feature_importance)
    
    print(f"Optimal threshold: {optimal_threshold:.3f}")
    print(f"Best F1 score: {best_f1:.3f}")
    
    # Sort features by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 15 most important features:")
    for feature, importance in sorted_features[:15]:
        print(f"  {feature}: {importance:.3f}")
    
    # Evaluate on training data
    correct = 0
    total = len(headers)
    tp, tn, fp, fn = 0, 0, 0, 0
    
    for i, header in enumerate(headers):
        prediction, _ = improved_classify(header, feature_importance, optimal_threshold)
        if prediction == labels[i]:
            correct += 1
        
        if prediction == 'phishing' and labels[i] == 'phishing':
            tp += 1
        elif prediction == 'legitimate' and labels[i] == 'legitimate':
            tn += 1
        elif prediction == 'phishing' and labels[i] == 'legitimate':
            fp += 1
        elif prediction == 'legitimate' and labels[i] == 'phishing':
            fn += 1
    
    accuracy = correct / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\nTraining Metrics:")
    print(f"Accuracy: {accuracy:.3f} ({correct}/{total})")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1-Score: {f1_score:.3f}")
    print(f"True Positives: {tp}")
    print(f"True Negatives: {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    
    # Save the improved classifier
    classifier_data = {
        'feature_importance': feature_importance,
        'threshold': optimal_threshold,
        'training_metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
    }
    
    model_path = os.path.join('myapp', 'ml', 'improved_classifier.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(classifier_data, f)
    
    print(f"\nImproved classifier saved to: {model_path}")
    
    return classifier_data

if __name__ == "__main__":
    print("Starting improved email header classifier training...")
    train_improved_classifier()
    print("Training completed!") 