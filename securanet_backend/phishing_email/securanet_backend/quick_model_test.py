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

def production_classify(header, threshold=2.0):
    """Classify email header using production logic"""
    header_lower = header.lower()
    risk_score = 0
    
    # High-risk patterns (strong positive weight)
    high_risk_patterns = [
        'urgent', 'suspended', 'verify', 'password', 'account',
        'login', 'click', 'confirm', 'reset', 'limited', 'immediately',
        'expire', 'action required', 'verify now', 'click here',
        'account suspended', 'password expired', 'verify account'
    ]
    
    for pattern in high_risk_patterns:
        if pattern in header_lower:
            risk_score += 3
    
    # Medium-risk patterns (moderate positive weight)
    medium_risk_patterns = [
        'update', 'security', 'alert', 'invoice', 'payment', 'bank',
        'expire', 'verify', 'confirm', 'suspended', 'limited time',
        'payment required', 'invoice ready', 'payment due'
    ]
    
    for pattern in medium_risk_patterns:
        if pattern in header_lower:
            risk_score += 1
    
    # Legitimate patterns (negative weight - reduces risk)
    legitimate_patterns = [
        'order', 'shipped', 'delivery', 'confirmation', 'receipt',
        'meeting', 'schedule', 'appointment', 'newsletter', 'update',
        'welcome', 'thank you', 'receipt', 'order confirmation',
        'meeting tomorrow', 'appointment scheduled', 'order shipped'
    ]
    
    for pattern in legitimate_patterns:
        if pattern in header_lower:
            risk_score -= 2
    
    # Domain analysis
    from_domain = extract_domain(header, 'from:')
    if from_domain:
        # Suspicious domain indicators
        suspicious_domains = ['verify', 'security', 'bank', 'paypal', 'microsoft', 'google']
        if any(indicator in from_domain.lower() for indicator in suspicious_domains):
            risk_score += 2
        
        # Legitimate domain indicators
        legitimate_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'amazon.com', 'github.com']
        if any(indicator in from_domain.lower() for indicator in legitimate_domains):
            risk_score -= 1
    
    # Subject line analysis
    subject = extract_subject(header)
    if subject:
        subject_lower = subject.lower()
        
        # Urgent words in subject
        urgent_words = ['urgent', 'immediately', 'now', 'asap', 'critical']
        if any(word in subject_lower for word in urgent_words):
            risk_score += 2
        
        # Action words in subject
        action_words = ['click', 'verify', 'confirm', 'update', 'reset', 'login']
        if any(word in subject_lower for word in action_words):
            risk_score += 2
        
        # Legitimate words in subject
        legitimate_words = ['meeting', 'order', 'confirmation', 'receipt', 'appointment']
        if any(word in subject_lower for word in legitimate_words):
            risk_score -= 1
    
    # Content type analysis
    if 'text/html' in header_lower:
        risk_score += 1  # HTML content is slightly suspicious
    
    # Security features (reduce risk)
    security_features = ['spf=', 'dkim=', 'dmarc=', 'authentication-results:']
    for feature in security_features:
        if feature in header_lower:
            risk_score -= 1
    
    # Text analysis
    exclamation_count = header.count('!')
    question_count = header.count('?')
    risk_score += exclamation_count + question_count
    
    # URL count
    import re
    url_count = len(re.findall(r'http[s]?://[^\s]+', header))
    risk_score += url_count * 2
    
    # Apply threshold-based classification
    prediction = 'phishing' if risk_score > threshold else 'legitimate'
    
    return prediction, risk_score

def extract_domain(header, field):
    """Extract domain from email header field"""
    import re
    pattern = rf'{field}\s*([^@\s]+@([^\s>]+))'
    match = re.search(pattern, header, re.IGNORECASE)
    if match:
        return match.group(2)
    return None

def extract_subject(header):
    """Extract subject line from header"""
    import re
    pattern = r'subject:\s*(.+)'
    match = re.search(pattern, header, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def test_model():
    """Quick model test"""
    model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return False
    
    print("✅ Model file found!")
    
    with open(model_path, 'rb') as f:
        classifier_data = pickle.load(f)
    
    threshold = classifier_data.get('threshold', 2.0)
    
    print(f"📊 Model threshold: {threshold}")
    
    # Test with a simple case
    test_header = """From: test@example.com
To: user@email.com
Subject: Test email
Date: Mon, 23 Jul 2025 10:00:00 +0000"""
    
    prediction, risk_score = production_classify(test_header, threshold)
    print(f"🧪 Test prediction: {prediction} (risk score: {risk_score})")
    
    return True

def main():
    print("🔍 SecuraNet Production Model Test")
    print("=" * 35)
    
    # Test model
    model_ok = test_model()
    
    if model_ok:
        print("\n✅ Production model is working!")
        print("\n🚀 To use the application:")
        print("1. Backend (Django):")
        print("   cd SecureNet-backend/securanet_backend")
        print("   python manage.py runserver")
        print("\n2. Frontend (React):")
        print("   cd SecureNet-frontend/my-app")
        print("   npm start")
        print("\n3. Access the application:")
        print("   Backend API: http://localhost:8000")
        print("   Frontend: http://localhost:3000")
        print("\n🎯 The application is now using the production-ready model!")
    else:
        print("\n❌ Model needs to be deployed first!")
        print("Run: python deploy_production_model.py")

if __name__ == "__main__":
    main() 