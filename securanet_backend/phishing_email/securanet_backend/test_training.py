#!/usr/bin/env python
import sys
import os

print("Testing training environment...")

# Test basic imports
try:
    import pandas as pd
    print("✓ pandas imported successfully")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    print("✓ scikit-learn imported successfully")
except ImportError as e:
    print(f"✗ scikit-learn import failed: {e}")

try:
    import joblib
    print("✓ joblib imported successfully")
except ImportError as e:
    print(f"✗ joblib import failed: {e}")

# Test Django setup
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")

# Test dataset availability
dataset_path = os.path.join('myapp', 'ml', 'dataset', 'headers.csv')
if os.path.exists(dataset_path):
    print(f"✓ Dataset found at: {dataset_path}")
else:
    print(f"✗ Dataset not found at: {dataset_path}")

print("Environment test completed!") 