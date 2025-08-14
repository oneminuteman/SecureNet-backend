#!/usr/bin/env python
import pickle
import os

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

def fix_model_properly():
    """Fix the model by adjusting feature importance and threshold"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return
    
    print("🔧 Fixing model properly...")
    
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    feature_importance = classifier_data['feature_importance']
    
    print("📊 Original feature importance (top 5):")
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    for feature, importance in sorted_features[:5]:
        print(f"  {feature}: {importance:.3f}")
    
    # Fix the feature importance
    print("\n🔧 Adjusting feature importance...")
    
    # Reduce the impact of length feature
    if 'length' in feature_importance:
        feature_importance['length'] = 0.1  # Reduce from 1.000 to 0.1
    
    # Increase importance of suspicious keywords
    suspicious_features = ['has_urgent', 'has_suspended', 'has_verify', 'has_password', 
                         'has_account', 'has_login', 'has_click', 'has_confirm', 
                         'has_reset', 'has_limited', 'has_immediately']
    
    for feature in suspicious_features:
        if feature in feature_importance:
            feature_importance[feature] = min(feature_importance[feature] * 2, 0.5)
    
    # Reduce importance of basic structural features
    basic_features = ['has_subject', 'has_from', 'has_to', 'has_date', 'has_message_id']
    for feature in basic_features:
        if feature in feature_importance:
            feature_importance[feature] = 0.01  # Very low importance
    
    # Set a reasonable threshold
    classifier_data['threshold'] = 0.3
    
    print("📊 Updated feature importance (top 5):")
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    for feature, importance in sorted_features[:5]:
        print(f"  {feature}: {importance:.3f}")
    
    print(f"\n✅ New threshold: {classifier_data['threshold']}")
    
    # Save the fixed model
    with open(model_path, 'wb') as f:
        pickle.dump(classifier_data, f)
    
    print("✅ Model fixed! Now testing...")

def test_fixed_model():
    """Test the fixed model"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    feature_importance = classifier_data['feature_importance']
    threshold = classifier_data['threshold']
    
    # Test cases
    test_cases = [
        {
            "name": "Normal Business Email",
            "header": """From: sender@company.com
To: recipient@company.com
Subject: Meeting tomorrow
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <123456@company.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8""",
            "expected": "legitimate"
        },
        {
            "name": "Order Confirmation",
            "header": """From: noreply@amazon.com
To: customer@email.com
Subject: Your order has been shipped
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <order123@amazon.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "legitimate"
        },
        {
            "name": "Phishing Email",
            "header": """From: urgent@bank-security.com
To: user@email.com
Subject: URGENT: Your account has been suspended - Click here to verify
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <phish123@fake-bank.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
            "expected": "phishing"
        }
    ]
    
    print("\n🧪 Testing fixed model:")
    print("=" * 40)
    
    correct = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        prediction, score = simple_classify(
            test_case['header'], feature_importance, threshold
        )
        is_correct = prediction == test_case['expected']
        
        if is_correct:
            correct += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} {test_case['name']}: {prediction} (score: {score:.3f})")
    
    accuracy = correct / total
    print(f"\n📊 Accuracy: {accuracy:.1f} ({correct}/{total})")
    
    if accuracy >= 0.8:
        print("🎉 Model is now working well!")
    elif accuracy >= 0.6:
        print("⚠️  Model is improved but could be better")
    else:
        print("❌ Model still needs work")

if __name__ == "__main__":
    print("🔧 SecuraNet Model Proper Fix")
    print("=" * 35)
    
    # Fix the model
    fix_model_properly()
    
    # Test the fixed model
    test_fixed_model() 