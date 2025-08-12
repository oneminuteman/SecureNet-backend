from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .header_tools.header_parser import analyze_header
from .header_tools.risk_scoring import score_risk

class EmailHeaderAnalyzerTests(APITestCase):
    def setUp(self):
        self.valid_header = (
            "From: test@example.com\n"
            "Subject: Test\n"
            "Received: from mail.example.com (mail.example.com [1.2.3.4]) by mx.example.com; Thu, 10 Jul 2025 09:00:19 -0700 (PDT)\n"
            "DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector;\n"
            "Authentication-Results: mx.example.com; dkim=pass header.d=example.com; dmarc=pass; spf=pass\n"
        )
        self.malformed_header = "From: not-an-email\nSubject\nReceived: something weird"

    def test_analyze_endpoint_valid(self):
        url = reverse('analyze_email_header')
        response = self.client.post(url, {"header": self.valid_header}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('parsed_headers', response.data)
        self.assertIn('risk_analysis', response.data)

    def test_analyze_endpoint_invalid(self):
        url = reverse('analyze_email_header')
        response = self.client.post(url, {"header": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_analyze_header_endpoint_valid(self):
        url = reverse('analyze_header')
        response = self.client.post(url, {"header": self.valid_header}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('parsed', response.data)
        self.assertIn('risk_score', response.data)
        self.assertIn('classification', response.data)

    def test_analyze_header_endpoint_invalid(self):
        url = reverse('analyze_header')
        response = self.client.post(url, {"header": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_header_parser_valid(self):
        result = analyze_header(self.valid_header)
        self.assertIn('parsed_headers', result)
        self.assertIn('dns_checks', result)
        self.assertIn('ip_info', result)

    def test_header_parser_malformed(self):
        result = analyze_header(self.malformed_header)
        self.assertIn('parsed_headers', result)
        self.assertIn('dns_checks', result)
        self.assertIn('ip_info', result)

    def test_risk_scoring(self):
        parsed = analyze_header(self.valid_header)["parsed_headers"]
        dns = analyze_header(self.valid_header)["dns_checks"]
        ip_info = analyze_header(self.valid_header)["ip_info"]
        risk = score_risk(parsed, dns, ip_info)
        self.assertIn('risk_score', risk)
        self.assertIn('level', risk)
        self.assertIn('reasons', risk)
