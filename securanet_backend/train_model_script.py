#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

# Now import and run the training
from myapp.ml.train_model import train_header_classifier

if __name__ == "__main__":
    print("Training email header classifier...")
    train_header_classifier()
    print("Training completed!") 