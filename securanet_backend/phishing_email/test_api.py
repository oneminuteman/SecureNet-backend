#!/usr/bin/env python
import os
import sys
import django
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

# Test the API endpoint
from django.test import Client
from django.urls import reverse

def test_api_endpoint():
    """Test the analyze-header API endpoint."""
    
    client = Client()
    
    # Test data
    test_header = """
Return-Path: <test@example.com>
Received: from mail.example.com (mail.example.com [192.168.1.1]) by mail.server.com
From: <test@example.com>
Subject: Test email
Message-ID: <test123@example.com>
"""
    
    # Test the enhanced endpoint
    print("Testing /analyze-header/ endpoint...")
    print("=" * 50)
    
    response = client.post('/analyze-header/', 
                          data=json.dumps({'header': test_header}),
                          content_type='application/json')
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Response:")
        print(f"  Risk Score: {data.get('risk_score', 'N/A')}")
        print(f"  Classification: {data.get('classification', 'N/A')}")
        print(f"  Confidence: {data.get('confidence', 'N/A')}")
        print(f"  Reasons: {data.get('reasons', [])}")
        print("✅ API endpoint working correctly!")
    else:
        print(f"❌ API endpoint failed: {response.content}")
    
    print("\n" + "=" * 50)
    print("API test completed!")

if __name__ == "__main__":
    test_api_endpoint() 