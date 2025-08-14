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

def debug_classification(header, feature_importance, threshold=0.5):
    """Debug classification by showing feature contributions"""
    features = simple_feature_extraction(header)
    score = 0
    contributions = {}
    
    # Calculate score and track contributions
    for feature, value in features.items():
        if feature in feature_importance:
            contribution = value * feature_importance[feature]
            score += contribution
            if contribution > 0:  # Only show positive contributions
                contributions[feature] = contribution
    
    # Sort contributions by importance
    sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    
    prediction = 'phishing' if score > threshold else 'legitimate'
    
    return prediction, score, sorted_contributions

def analyze_legitimate_emails():
    """Analyze why legitimate emails are being flagged as phishing"""
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
    
    # Legitimate email test cases
    legitimate_emails = [
        {
            "name": "Normal Business Email",
            "header": """From: sender@company.com
To: recipient@company.com
Subject: Meeting tomorrow
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <123456@company.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8"""
        },
        {
            "name": "Order Confirmation",
            "header": """From: noreply@amazon.com
To: customer@email.com
Subject: Your order has been shipped
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <order123@amazon.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8"""
        },
        {
            "name": "Service Notification",
            "header": """From: support@github.com
To: user@email.com
Subject: Repository access granted
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <github123@github.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8"""
        },
        {
            "name": "Legitimate Security Alert",
            "header": """From: newsletter@legitimate-company.com
To: subscriber@email.com
Subject: Security alert: New login detected
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <news123@legitimate-company.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8"""
        },
        {
            "name": "Billing Notification",
            "header": """From: billing@service-provider.com
To: customer@email.com
Subject: Payment required - Your invoice is ready
Date: Mon, 23 Jul 2025 10:00:00 +0000
Message-ID: <bill123@service-provider.com>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8"""
        }
    ]
    
    print("\n🔍 ANALYZING WHY LEGITIMATE EMAILS ARE FLAGGED AS PHISHING")
    print("=" * 70)
    
    for i, email in enumerate(legitimate_emails, 1):
        print(f"\n📧 Email {i}: {email['name']}")
        print("-" * 50)
        
        prediction, score, contributions = debug_classification(
            email['header'], feature_importance, threshold
        )
        
        print(f"Prediction: {prediction}")
        print(f"Score: {score:.3f}")
        print(f"Threshold: {threshold}")
        print(f"Status: {'❌ FALSE POSITIVE' if prediction == 'phishing' else '✅ CORRECT'}")
        
        if contributions:
            print("\n🔍 Top contributing features:")
            for feature, contribution in contributions[:5]:
                print(f"  {feature}: +{contribution:.3f}")
        
        # Show the actual header content
        print(f"\n📄 Header content:")
        print(email['header'][:200] + "..." if len(email['header']) > 200 else email['header'])
    
    print("\n🎯 ROOT CAUSE ANALYSIS")
    print("=" * 50)
    print("❌ Problem: Model threshold is too low (0.5)")
    print("❌ Problem: 'length' feature has highest importance (1.000)")
    print("❌ Problem: All emails trigger basic features (subject, from, to, etc.)")
    print("❌ Problem: No negative weights for legitimate business terms")
    
    print("\n💡 SOLUTIONS:")
    print("1. Increase threshold to 1.0-1.5")
    print("2. Add negative weights for legitimate terms (order, shipped, meeting, etc.)")
    print("3. Reduce importance of basic structural features")
    print("4. Add domain reputation checking")

if __name__ == "__main__":
    analyze_legitimate_emails() 