#!/usr/bin/env python
"""
Test script to verify the API fixes are working
"""

import requests
import json

def test_api():
    """Test the API endpoints to see if the fixes are working."""
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if the root endpoint works
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Test the analyze-header endpoint with a real email header
    print("\n🔍 Testing analyze-header endpoint...")
    
    test_header = """
Return-Path: <sender@example.com>
Received: from mail.example.com (mail.example.com [192.168.1.1]) by mail.server.com
From: <sender@example.com>
Subject: Test email
Message-ID: <test123@example.com>
Date: Mon, 23 Jul 2025 10:00:00 +0000
"""
    
    try:
        response = requests.post(
            f"{base_url}/analyze-header/",
            json={"header": test_header},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Analyze-header endpoint working!")
            data = response.json()
            print(f"   Keys in response: {list(data.keys())}")
            
            # Check if the expected data structure is present
            if 'summary' in data:
                print("✅ Summary data present!")
                summary = data['summary']
                print(f"   Subject: {summary.get('subject', 'N/A')}")
                print(f"   From: {summary.get('from', 'N/A')}")
            else:
                print("❌ Summary data missing!")
                
            if 'delivery_info' in data:
                print("✅ Delivery info present!")
                delivery = data['delivery_info']
                print(f"   SPF published: {delivery.get('spf', {}).get('published', 'N/A')}")
                print(f"   DKIM published: {delivery.get('dkim', {}).get('published', 'N/A')}")
                print(f"   DMARC compliant: {delivery.get('dmarc', {}).get('compliant', 'N/A')}")
            else:
                print("❌ Delivery info missing!")
                
            if 'ip_info' in data:
                print("✅ IP info present!")
                ip_info = data['ip_info']
                print(f"   Country: {ip_info.get('country', 'N/A')}")
            else:
                print("❌ IP info missing!")
                
        else:
            print(f"❌ Analyze-header endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Analyze-header endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("API test completed!")

if __name__ == "__main__":
    test_api() 