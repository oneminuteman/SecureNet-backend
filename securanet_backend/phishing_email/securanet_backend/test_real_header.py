#!/usr/bin/env python
"""
Test script to debug real email header processing
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

from myapp.utils.parser import parse_email_header
from myapp.utils.dns_checker import run_dns_checks
from myapp.utils.risk_scorer import score_risk_wrapper
from myapp.utils.classifier import classify_header_text

def test_real_header():
    """Test with a real email header to see what's happening."""
    
    # Real email header (you can replace this with the actual header you tested)
    real_header = """
Return-Path: <sender@example.com>
Received: from mail.example.com (mail.example.com [192.168.1.1]) by mail.server.com
From: <sender@example.com>
Subject: Test email
Message-ID: <test123@example.com>
Date: Mon, 23 Jul 2025 10:00:00 +0000
"""
    
    print("🔍 Testing Real Email Header Processing")
    print("=" * 50)
    
    # Test parsing
    print("1. Testing header parsing...")
    parsed = parse_email_header(real_header)
    print(f"   Parsed result keys: {list(parsed.keys())}")
    
    if 'parsed_headers' in parsed:
        summary = parsed['parsed_headers'].get('summary', {})
        print(f"   Summary: {summary}")
    else:
        print(f"   No parsed_headers found. Full result: {parsed}")
    
    # Test DNS checks
    print("\n2. Testing DNS checks...")
    dns = run_dns_checks(parsed)
    print(f"   DNS results: {dns}")
    
    # Test risk scoring
    print("\n3. Testing risk scoring...")
    risk = score_risk_wrapper(parsed, dns)
    print(f"   Risk score: {risk.get('risk_score', 0)}")
    print(f"   Risk reasons: {risk.get('reasons', [])}")
    
    # Test ML classification
    print("\n4. Testing ML classification...")
    ml_result = classify_header_text(real_header)
    print(f"   ML result: {ml_result}")
    
    print("\n" + "=" * 50)
    print("Real header test completed!")
    
    # Show what the frontend would receive
    print("\n📊 Data structure for frontend:")
    result_data = parsed
    result_data["classification"] = ml_result.get("label", "unknown")
    result_data["confidence"] = ml_result.get("confidence", 0.0)
    result_data["risk_score"] = risk.get("risk_score", 0)
    result_data["reasons"] = risk.get("reasons", [])
    
    print(f"   Keys available: {list(result_data.keys())}")
    if 'summary' in result_data:
        print(f"   Summary data: {result_data['summary']}")
    else:
        print("   ❌ No 'summary' key found - this is the problem!")

if __name__ == "__main__":
    test_real_header() 