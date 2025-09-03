
<<<<<<< HEAD
# SecureNet-backend
  **this is the backend directory .Final project found in KAKA branch**


**SecureNet AI** is an advanced cybersecurity suite designed to protect users from digital threats through intelligent monitoring and detection. Developed as a group project, SecureNet AI leverages artificial intelligence and modern web technologies to deliver three core security functionalities:

1. **File Management & Security Monitoring**
2. **Phishing Detection**
3. **Clone Site Detection**

---

## Group Members

- **Josh King** (`joshking-vs`)
- _[Add your team members here, e.g. Jane Doe (`janedoe`), Alex Smith (`alexsmith`)]_

---

## Functionalities

### 1. File Management & Security Monitoring

Monitors file system activity in real-time, detects suspicious file changes, and provides actionable security recommendations.  
Features include:
- Directory selection and monitoring controls
- Risk-level classification of file events (`Safe`, `Suspicious`, `Dangerous`)
- Integration with AI for security analysis and recommendations

### 2. Phishing Detection

Analyzes messages (emails, SMS, etc.) to identify and flag potential phishing attempts.  
Features include:
- Paste or input message content for instant analysis
- AI-powered classification (`Not Suspicious`, `Suspicious`, with confidence scores)
- Modern UI for clear verdicts and actionable feedback

### 3. Clone Site Detection

Detects fraudulent websites that mimic legitimate ones, helping prevent credential theft and scam interactions.  
Features include:
- URL input and real-time scanning
- Multiple threat intelligence sources (Google Safe Browsing, VirusTotal, etc.)
- Screenshot capture and scan history logging

---

## Technologies Used

- **React.js** (Frontend)
- **Bootstrap** & **Custom CSS** (UI/UX)
- **Django REST Framework** (Backend API)
- **AI/ML Models** for phishing and clone site detection
- **Axios** for API calls
- **Toastify** for notifications

---

## Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/<your-org>/securenet-ai.git
   cd securenet-ai
   ```

2. **Install dependencies**  
   - Frontend:  
     ```bash
     npm install
     ```
   - Backend:  
     ```bash
     pip install -r requirements.txt
     ```

3. **Start development servers**  
   - Frontend:  
     ```bash
     npm start
     ```
   - Backend:  
     ```bash
     python manage.py runserver
     ```

---

## Usage

- **File Monitoring:**  
  Navigate to the File Monitoring dashboard to select directories and monitor security events.
- **Phishing Detection:**  
  Go to Phishing Detection, paste message content, and analyze for threats.
- **Clone Site Detection:**  
  Open the Clone Site Scanner, input a URL, and review scan results and screenshots.

---

