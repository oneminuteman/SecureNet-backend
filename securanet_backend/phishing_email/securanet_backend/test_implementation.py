#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

# Test the implementation
from myapp.utils.parser import parse_email_header
from myapp.utils.dns_checker import run_dns_checks
from myapp.utils.risk_scorer import score_risk_wrapper

def test_header_analysis():
    """Test the header analysis pipeline without ML."""
    
    # Sample email header
    test_header = """
Return-Path: <test@example.com>
Received: from mail.example.com (mail.example.com [192.168.1.1]) by mail.server.com
From: <test@example.com>
Subject: Test email
Message-ID: <test123@example.com>
"""
    
    print("Testing header analysis pipeline...")
    print("=" * 50)
    
    # Test parsing
    print("1. Testing header parsing...")
    parsed = parse_email_header(test_header)
    print(f"   Parsed headers: {parsed.get('parsed_headers', {}).get('summary', {})}")
    
    # Test DNS checks
    print("\n2. Testing DNS checks...")
    dns = run_dns_checks(parsed)
    print(f"   DNS results: {dns}")
    
    # Test risk scoring
    print("\n3. Testing risk scoring...")
    risk = score_risk_wrapper(parsed, dns)
    print(f"   Risk score: {risk.get('risk_score', 0)}")
    print(f"   Risk reasons: {risk.get('reasons', [])}")
    
    print("\n" + "=" * 50)
    print("Header analysis pipeline test completed!")
    print("Note: ML classification requires the trained model to be available.")

if __name__ == "__main__":
    test_header_analysis() 