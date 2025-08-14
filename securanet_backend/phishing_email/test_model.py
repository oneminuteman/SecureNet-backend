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
    return 'phishing' if score > threshold else 'legitimate'

def test_trained_model():
    """Test the trained simple classifier"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("Model file not found!")
        return
    
    print("Loading trained model...")
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    feature_importance = classifier_data['feature_importance']
    threshold = classifier_data['threshold']
    
    # Test with sample email headers
    test_headers = [
        # Legitimate email header
        """From: sender@company.com
To: recipient@company.com
Subject: Meeting tomorrow
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <123456@company.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8""",
        
        # Phishing email header
        """From: urgent@bank-security.com
To: user@email.com
Subject: URGENT: Your account has been suspended - Click here to verify
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <phish123@fake-bank.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8""",
        
        # Another phishing example
        """From: security@paypal-verify.com
To: customer@email.com
Subject: Limited time offer - Update your payment information now
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <fake456@scam-site.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8"""
    ]
    
    print("\nTesting model with sample headers:")
    print("=" * 50)
    
    for i, header in enumerate(test_headers, 1):
        prediction = simple_classify(header, feature_importance, threshold)
        print(f"Test {i}: {prediction}")
        print(f"Header preview: {header[:100]}...")
        print("-" * 30)
    
    print("\nModel testing completed!")

if __name__ == "__main__":
    test_trained_model() 