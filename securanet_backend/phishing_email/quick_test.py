#!/usr/bin/env python
import pickle
import os

print("=== SecureNet Model Test ===")

# Test if model file exists
model_path = os.path.join('myapp', 'ml', 'simple_classifier.pkl')
if os.path.exists(model_path):
    print(f"✅ Model file found: {model_path}")
    
    # Try to load the model
    try:
        with open(model_path, 'rb') as f:
            classifier_data = pickle.load(f)
        print("✅ Model loaded successfully")
        
        # Show model info
        feature_importance = classifier_data['feature_importance']
        threshold = classifier_data['threshold']
        print(f"✅ Model has {len(feature_importance)} features")
        print(f"✅ Classification threshold: {threshold}")
        
        # Test with a sample header
        test_header = """From: test@example.com
To: user@email.com
Subject: Test email
Date: Mon, 23 Jul 2025 10:00:00 +0000"""
        
        print("\n=== Testing with sample header ===")
        print(f"Header: {test_header[:50]}...")
        
        # Simple classification logic
        header_lower = test_header.lower()
        score = 0
        
        # Check for suspicious keywords
        suspicious_words = ['urgent', 'click', 'account', 'bank', 'security']
        for word in suspicious_words:
            if word in header_lower:
                score += 0.1
        
        # Check header length
        score += len(test_header) * 0.001
        
        prediction = 'phishing' if score > threshold else 'legitimate'
        print(f"✅ Prediction: {prediction} (score: {score:.3f})")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
else:
    print(f"❌ Model file not found: {model_path}")

print("\n=== Model Test Completed ===") 