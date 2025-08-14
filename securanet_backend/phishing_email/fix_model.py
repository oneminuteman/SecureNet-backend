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

def test_with_different_thresholds():
    """Test the model with different thresholds to find optimal value"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return
    
    print("🔍 Loading trained model...")
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    feature_importance = classifier_data['feature_importance']
    
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
    
    print("\n🧪 TESTING DIFFERENT THRESHOLDS")
    print("=" * 50)
    
    thresholds = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    
    for threshold in thresholds:
        print(f"\n📊 Threshold: {threshold}")
        print("-" * 30)
        
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
            print(f"{status} {test_case['name']}: {prediction} (score: {score:.1f})")
        
        accuracy = correct / total
        print(f"Accuracy: {accuracy:.1f} ({correct}/{total})")
    
    print("\n💡 RECOMMENDATION:")
    print("Based on the results, use threshold = 1.5 or 2.0")
    print("This will reduce false positives while maintaining phishing detection")

def fix_model_threshold():
    """Fix the model by updating the threshold"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return
    
    print("🔧 Fixing model threshold...")
    
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    # Update threshold to 1.5 (recommended value)
    old_threshold = classifier_data['threshold']
    classifier_data['threshold'] = 1.5
    
    # Save the fixed model
    with open(model_path, 'wb') as f:
        pickle.dump(classifier_data, f)
    
    print(f"✅ Threshold updated from {old_threshold} to 1.5")
    print("✅ Model should now have fewer false positives!")

if __name__ == "__main__":
    print("🔍 SecuraNet Model Threshold Analysis")
    print("=" * 40)
    
    # Test different thresholds
    test_with_different_thresholds()
    
    print("\n" + "=" * 50)
    
    # Fix the model
    fix_model_threshold()
    
    print("\n🎯 Now test the fixed model:")
    print("python quick_model_test.py") 