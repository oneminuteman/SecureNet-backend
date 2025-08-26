# SecuraNet AI - Email Header Analyzer

A Django-based cybersecurity platform that provides comprehensive email header analysis with machine learning classification.

## 🚀 Features

- **Email Header Parsing**: Extracts sender information, routing chain, authentication headers
- **DNS Security Checks**: SPF, DKIM, and DMARC validation
- **Risk Scoring**: Automated risk assessment based on multiple factors
- **ML Classification**: AI-powered classification of headers as legitimate or suspicious
- **REST API**: Easy-to-use API endpoints for integration

## 📁 Project Structure

```
securanet_backend/
├── myapp/
│   ├── ml/
│   │   ├── dataset/
│   │   │   └── headers.csv          # Training dataset
│   │   ├── train_model.py           # ML model training script
│   │   └── header_classifier.pkl    # Trained model (generated)
│   ├── utils/
│   │   ├── parser.py                # Header parsing utility
│   │   ├── dns_checker.py           # DNS validation utility
│   │   ├── risk_scorer.py           # Risk scoring utility
│   │   └── classifier.py            # ML classification utility
│   ├── header_tools/                # Existing header analysis tools
│   ├── views.py                     # API endpoints
│   ├── urls.py                      # URL routing
│   └── apps.py                      # App configuration with model loading
└── requirements.txt                 # Python dependencies
```

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the ML Model**:
   ```bash
   cd securanet_backend
   python manage.py shell -c "from myapp.ml.train_model import train_header_classifier; train_header_classifier()"
   ```

3. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

## 📡 API Endpoints

### 1. Enhanced Header Analysis (with ML)
**POST** `/analyze-header/`

**Request**:
```json
{
  "header": "Return-Path: <sender@example.com>\nReceived: from mail.example.com...\nFrom: <sender@example.com>\nSubject: Test email"
}
```

**Response**:
```json
{
  "parsed": {
    "summary": {
      "from": {"name": "", "email": "sender@example.com"},
      "sender_ip": "192.168.1.1",
      "subject": "Test email"
    },
    "authentication": {},
    "routing": [...],
    "dkim_signature": {}
  },
  "dns": {
    "spf": {"has_spf": true, "spf_record": "v=spf1 include:_spf.google.com ~all"},
    "dkim": {"has_dkim": false, "error": "DKIM record not found"},
    "dmarc": {"has_dmarc": true, "dmarc_record": "v=DMARC1; p=quarantine;"}
  },
  "risk_score": 4,
  "reasons": ["No DKIM record found", "No DMARC policy found"],
  "classification": "ham",
  "confidence": 0.85,
  "ip_info": {
    "country": "United States",
    "city": "New York",
    "isp": "Example ISP"
  }
}
```

### 2. Legacy Header Analysis
**POST** `/analyze/`

Uses the original analysis pipeline without ML classification.

## 🤖 Machine Learning Model

The system uses a **TfidfVectorizer + LogisticRegression** pipeline for classification:

- **Features**: TF-IDF vectors with 1-2 gram features
- **Training Data**: Sample dataset with 10 email headers (5 legitimate, 5 suspicious)
- **Model Persistence**: Saved as `header_classifier.pkl` using joblib
- **Auto-loading**: Model loads automatically when Django starts

### Training the Model

```python
from myapp.ml.train_model import train_header_classifier
train_header_classifier()
```

### Model Performance

The model achieves high accuracy on the training dataset and provides confidence scores for predictions.

## 🔧 Configuration

### Model Loading
The ML model is automatically loaded in `apps.py`:

```python
def ready(self):
    from joblib import load
    model_path = os.path.join(os.path.dirname(__file__), 'ml', 'header_classifier.pkl')
    MyappConfig.model = load(model_path)
```

### Risk Scoring
Risk factors include:
- Missing or invalid sender email
- SPF record absence or strict policy
- DKIM record absence
- DMARC policy absence
- Unknown IP geolocation

## 🧪 Testing

### Test the Implementation
```bash
python test_implementation.py
```

### API Testing with curl
```bash
curl -X POST http://localhost:8000/analyze-header/ \
  -H "Content-Type: application/json" \
  -d '{
    "header": "Return-Path: <test@example.com>\nReceived: from mail.example.com\nFrom: <test@example.com>\nSubject: Test"
  }'
```

## 📊 Sample Dataset

The training dataset (`ml/dataset/headers.csv`) includes:
- **Legitimate emails**: From trusted domains (Google, Microsoft, Amazon, etc.)
- **Suspicious emails**: Phishing attempts, scams, spam
- **Features**: Full email headers with authentication signatures

## 🔒 Security Features

1. **Input Validation**: All headers are validated before processing
2. **Error Handling**: Graceful error handling with informative messages
3. **DNS Security**: Comprehensive SPF/DKIM/DMARC validation
4. **IP Analysis**: Geolocation and ISP information
5. **Risk Assessment**: Multi-factor risk scoring

## 🚀 Deployment

1. **Production Setup**:
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Configure environment variables
   - Set up proper logging

2. **Model Updates**:
   - Retrain model with new data
   - Replace `header_classifier.pkl`
   - Restart Django application

## 📝 Dependencies

- Django >= 5.2.3
- Django REST Framework >= 3.14.0
- scikit-learn >= 1.3.0
- pandas >= 2.0.0
- joblib >= 1.3.0
- dnspython >= 2.4.0
- requests >= 2.31.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is part of the SecuraNet AI cybersecurity platform.
