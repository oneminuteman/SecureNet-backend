## Privacy Notice

This service processes email headers for the purpose of security analysis. The following privacy protections are in place:

- **Data Minimization:** Only the email header you submit is processed. No message content or attachments are required or stored.
- **Logging:** For security and debugging, a short preview of the header is logged, but all email addresses and IP addresses are masked in logs. No full headers, email addresses, or IPs are stored in logs.
- **Data Retention:** No raw headers or analysis results are stored beyond the duration of the request. Logs are retained only for operational monitoring and do not contain sensitive data.
- **User Rights:** If you have concerns about your data, you may contact the service operator to request deletion of any log entries related to your use.
- **Security:** All data is processed in memory and is not shared with third parties.

This service is intended for security research and educational use. For production or commercial deployments, review and adapt privacy practices to your jurisdiction and use case. 

## Getting Started (Developer Onboarding)

### 1. Installation

```bash
# Clone the repository
 git clone <your-repo-url>
 cd SecureNet-backend

# (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Server

```bash
python securanet_backend/manage.py runserver
```

- The API will be available at: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/swagger/
- Redoc: http://127.0.0.1:8000/redoc/

### 3. Running Tests

```bash
python manage.py test myapp
```

### 4. Retraining the ML Model

- Place your labeled dataset at `securanet_backend/myapp/ml/dataset/headers.csv` (columns: `text`, `label`).
- Retrain the model:

```bash
python -m myapp.ml.train_model
```
- The model will be saved as `securanet_backend/myapp/ml/header_classifier.pkl`.

### 5. Example API Usage

#### Using `curl`

```bash
curl -X POST http://127.0.0.1:8000/analyze-header/ \
  -H 'Content-Type: application/json' \
  -d '{"header": "From: test@example.com\nSubject: Test\n..."}'
```

#### Using Python

```python
import requests
header = """From: test@example.com\nSubject: Test\n..."""
response = requests.post(
    "http://127.0.0.1:8000/analyze-header/",
    json={"header": header}
)
print(response.json())
```

--- 