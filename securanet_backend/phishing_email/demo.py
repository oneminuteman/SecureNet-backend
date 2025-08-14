#!/usr/bin/env python
"""
SecuraNet AI - Email Header Analyzer Demo

This script demonstrates the complete email header analysis pipeline
including parsing, DNS checks, risk scoring, and ML classification.
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

def demo_header_analysis():
    """Demonstrate the complete header analysis pipeline."""
    
    print("🔒 SecuraNet AI - Email Header Analyzer Demo")
    print("=" * 60)
    
    # Sample email headers for demonstration
    test_headers = [
        {
            "name": "Legitimate Email (Google)",
            "header": """
Return-Path: <sender@gmail.com>
Received: from mail.google.com (mail.google.com [142.250.190.78]) by mail.example.com
From: <sender@gmail.com>
Subject: Your order confirmation
Message-ID: <abc123@gmail.com>
DKIM-Signature: v=1; a=rsa-sha256; d=gmail.com; s=20210112;
Authentication-Results: mail.example.com; dkim=pass header.d=gmail.com;
"""
        },
        {
            "name": "Suspicious Email (Phishing)",
            "header": """
Return-Path: <phishing@malicious.net>
Received: from suspicious.server.net (suspicious.server.net [10.0.0.1]) by mail.example.com
From: <phishing@malicious.net>
Subject: Your account has been suspended - URGENT
Message-ID: <phish123@malicious.net>
"""
        }
    ]
    
    for i, test_case in enumerate(test_headers, 1):
        print(f"\n📧 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Step 1: Parse the header
        print("1️⃣ Parsing email header...")
        parsed = parse_email_header(test_case['header'])
        
        if parsed.get('parsed_headers', {}).get('summary'):
            summary = parsed['parsed_headers']['summary']
            print(f"   From: {summary.get('from', {}).get('email', 'N/A')}")
            print(f"   Subject: {summary.get('subject', 'N/A')}")
            print(f"   Sender IP: {summary.get('sender_ip', 'N/A')}")
        
        # Step 2: DNS checks
        print("\n2️⃣ Running DNS security checks...")
        dns = run_dns_checks(parsed)
        
        spf_status = "✅" if dns.get('spf', {}).get('has_spf') else "❌"
        dkim_status = "✅" if dns.get('dkim', {}).get('has_dkim') else "❌"
        dmarc_status = "✅" if dns.get('dmarc', {}).get('has_dmarc') else "❌"
        
        print(f"   SPF: {spf_status}")
        print(f"   DKIM: {dkim_status}")
        print(f"   DMARC: {dmarc_status}")
        
        # Step 3: Risk scoring
        print("\n3️⃣ Calculating risk score...")
        risk = score_risk_wrapper(parsed, dns)
        print(f"   Risk Score: {risk.get('risk_score', 0)}/10")
        print(f"   Risk Level: {risk.get('level', 'Unknown')}")
        if risk.get('reasons'):
            print(f"   Risk Factors: {', '.join(risk['reasons'])}")
        
        # Step 4: ML classification
        print("\n4️⃣ Machine Learning classification...")
        ml_result = classify_header_text(test_case['header'])
        
        if ml_result.get('error'):
            print(f"   ⚠️  ML Model: {ml_result['error']}")
        else:
            label_emoji = "✅" if ml_result.get('label') == 'ham' else "🚨"
            print(f"   Classification: {label_emoji} {ml_result.get('label', 'unknown')}")
            print(f"   Confidence: {ml_result.get('confidence', 0):.2f}")
        
        # Step 5: IP information
        print("\n5️⃣ IP geolocation...")
        ip_info = parsed.get('ip_info', {})
        if ip_info.get('error'):
            print(f"   ⚠️  {ip_info['error']}")
        else:
            print(f"   Country: {ip_info.get('country', 'Unknown')}")
            print(f"   City: {ip_info.get('city', 'Unknown')}")
            print(f"   ISP: {ip_info.get('isp', 'Unknown')}")
        
        print("\n" + "=" * 60)
    
    print("\n🎯 Demo completed!")
    print("\nTo use the API:")
    print("curl -X POST http://localhost:8000/analyze-header/ \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"header\": \"your email header here\"}'")

if __name__ == "__main__":
    demo_header_analysis() 