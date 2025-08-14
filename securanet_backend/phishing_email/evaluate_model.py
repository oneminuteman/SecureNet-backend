#!/usr/bin/env python
import pickle
import os
from collections import Counter

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
    return 'phishing' if score > threshold else 'legitimate', score

def evaluate_model():
    """Comprehensive model evaluation"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return
    
    print("🔍 Loading trained model...")
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    feature_importance = classifier_data['feature_importance']
    threshold = classifier_data['threshold']
    
    print(f"📊 Model threshold: {threshold}")
    print(f"📈 Number of features: {len(feature_importance)}")
    
    # Test dataset with known labels
    test_cases = [
        # Legitimate emails
        {
            "header": """From: sender@company.com
To: recipient@company.com
Subject: Meeting tomorrow
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <123456@company.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8""",
            "expected": "legitimate",
            "description": "Normal business email"
        },
        {
            "header": """From: noreply@amazon.com
To: customer@email.com
Subject: Your order has been shipped
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <order123@amazon.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "legitimate",
            "description": "Legitimate order confirmation"
        },
        {
            "header": """From: support@github.com
To: user@email.com
Subject: Repository access granted
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <github123@github.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8""",
            "expected": "legitimate",
            "description": "Legitimate service notification"
        },
        
        # Phishing emails
        {
            "header": """From: urgent@bank-security.com
To: user@email.com
Subject: URGENT: Your account has been suspended - Click here to verify
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <phish123@fake-bank.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "phishing",
            "description": "Phishing with urgent keywords"
        },
        {
            "header": """From: security@paypal-verify.com
To: customer@email.com
Subject: Limited time offer - Update your payment information now
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <fake456@scam-site.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "phishing",
            "description": "Phishing with payment keywords"
        },
        {
            "header": """From: admin@microsoft-verify.net
To: user@email.com
Subject: Your password will expire - Click to reset immediately
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <fake789@scam-site.net>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "phishing",
            "description": "Phishing with password reset keywords"
        },
        
        # Edge cases
        {
            "header": """From: newsletter@legitimate-company.com
To: subscriber@email.com
Subject: Security alert: New login detected
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <news123@legitimate-company.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8""",
            "expected": "legitimate",
            "description": "Legitimate security alert"
        },
        {
            "header": """From: billing@service-provider.com
To: customer@email.com
Subject: Payment required - Your invoice is ready
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <bill123@service-provider.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "legitimate",
            "description": "Legitimate billing notification"
        }
    ]
    
    print("\n🧪 Testing model with comprehensive dataset...")
    print("=" * 60)
    
    results = []
    correct = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        prediction, score = simple_classify(test_case['header'], feature_importance, threshold)
        is_correct = prediction == test_case['expected']
        
        if is_correct:
            correct += 1
        
        results.append({
            'case': i,
            'prediction': prediction,
            'expected': test_case['expected'],
            'score': score,
            'correct': is_correct,
            'description': test_case['description']
        })
        
        status = "✅" if is_correct else "❌"
        print(f"{status} Test {i}: {prediction} (expected: {test_case['expected']}) - Score: {score:.3f}")
        print(f"   Description: {test_case['description']}")
        print()
    
    # Calculate metrics
    accuracy = correct / total
    predictions = [r['prediction'] for r in results]
    expected = [r['expected'] for r in results]
    
    # Confusion matrix
    tp = sum(1 for r in results if r['prediction'] == 'phishing' and r['expected'] == 'phishing')
    tn = sum(1 for r in results if r['prediction'] == 'legitimate' and r['expected'] == 'legitimate')
    fp = sum(1 for r in results if r['prediction'] == 'phishing' and r['expected'] == 'legitimate')
    fn = sum(1 for r in results if r['prediction'] == 'legitimate' and r['expected'] == 'phishing')
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print("📊 MODEL PERFORMANCE METRICS")
    print("=" * 40)
    print(f"Accuracy: {accuracy:.3f} ({correct}/{total})")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1-Score: {f1_score:.3f}")
    print()
    print("Confusion Matrix:")
    print(f"True Positives (TP): {tp}")
    print(f"True Negatives (TN): {tn}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print()
    
    # Feature importance analysis
    print("🔍 TOP FEATURES BY IMPORTANCE")
    print("=" * 40)
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    for feature, importance in sorted_features[:10]:
        print(f"{feature}: {importance:.3f}")
    
    print("\n🎯 EVALUATION SUMMARY")
    print("=" * 40)
    if accuracy >= 0.8:
        print("✅ Model performs well (Accuracy >= 80%)")
    elif accuracy >= 0.6:
        print("⚠️  Model performs moderately (Accuracy 60-80%)")
    else:
        print("❌ Model needs improvement (Accuracy < 60%)")
    
    if precision < 0.7:
        print("⚠️  High false positive rate - model may be too sensitive")
    if recall < 0.7:
        print("⚠️  High false negative rate - model may miss phishing emails")
    
    print(f"\n💡 Recommendations:")
    if accuracy < 0.8:
        print("- Consider retraining with more diverse data")
        print("- Adjust threshold (current: {threshold})")
        print("- Add more sophisticated features")
    else:
        print("- Model is ready for production use")
        print("- Consider fine-tuning for specific use cases")

if __name__ == "__main__":
    evaluate_model() 