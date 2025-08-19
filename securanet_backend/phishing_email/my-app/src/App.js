import React, { useState } from 'react';
import './App.css';
import HeaderAnalysis from './HeaderAnalysis';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import HelpPage from './HelpPage';

function InfoBanner({ onClose }) {
  return (
    <div className="alert alert-info d-flex align-items-center justify-content-between mb-4" role="alert" style={{ borderRadius: 12, background: 'linear-gradient(90deg, #e0e7ff 0%, #f0f4ff 100%)', color: '#1e3a8a', fontSize: '1.08rem', boxShadow: '0 2px 12px rgba(99,102,241,0.07)' }}>
      <div>
        <span role="img" aria-label="info" style={{ fontSize: '1.3rem', marginRight: 8 }}>ℹ️</span>
        <strong>What is an email header?</strong> The header contains technical details about the sender, recipient, and how the email was delivered. Analyzing it helps detect phishing, spoofing, and other threats.
        <Link to="/help" className="ms-2" style={{ color: '#6366f1', textDecoration: 'underline', fontWeight: 500 }}>Learn more</Link>
      </div>
      <button type="button" className="btn-close ms-3" aria-label="Close info" onClick={onClose} style={{ filter: 'invert(40%)' }}></button>
    </div>
  );
}

function ResultsPage() {
  const location = useLocation();
  const result = location.state?.result;
  if (!result) {
    return <div style={{ fontFamily: 'Segoe UI, Arial, sans-serif', textAlign: 'center', marginTop: 80 }}>No analysis result found. Please analyze an email header first.</div>;
  }
  return <HeaderAnalysis data={result} />;
}

function MainApp() {
  const [header, setHeader] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showInfo, setShowInfo] = useState(true);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/analyze-header/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ header }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || 'An error occurred.');
      } else {
        setResult(data);
        navigate('/results', { state: { result: data } });
      }
    } catch (err) {
      setError('Network error.');
    }
    setLoading(false);
  };

  return (
    <div className="main-bg min-vh-100 d-flex flex-column" style={{ fontFamily: 'Segoe UI, Arial, sans-serif' }}>
      {/* Landing Header */}
      <header className="py-5 px-3 text-center landing-header">
        <div className="d-flex flex-column align-items-center justify-content-center">
          <img src="/logo192.png" alt="SecuraNet Logo" style={{ width: 72, height: 72, marginBottom: 16 }} />
          <h1 className="display-4 fw-bold mb-2" style={{ color: '#1e3a8a', letterSpacing: 1 }}>SecuraNet Email Header Analyzer</h1>
          <p className="lead mb-3" style={{ maxWidth: 600, color: '#374151' }}>
            Instantly analyze email headers for security, authenticity, and risk. Powered by advanced AI and security best practices.
          </p>
          <span className="badge bg-primary fs-6 mb-2" style={{ background: 'linear-gradient(90deg, #6366f1 0%, #60a5fa 100%)' }}>Your first line of defense against phishing and spoofing</span>
        </div>
      </header>
      <main className="flex-grow-1 d-flex flex-column align-items-center justify-content-start px-2">
        <div className="card shadow-lg border-0 mb-4" style={{ maxWidth: 900, width: '100%', borderRadius: 18 }}>
          <div className="card-body p-4">
            <h2 className="card-title mb-3 text-center" style={{ color: '#1e3a8a', fontWeight: 700, fontSize: '2rem' }}>Analyze an Email Header</h2>
            <div className="d-flex flex-column flex-md-row gap-4 align-items-stretch">
              <form onSubmit={handleSubmit} autoComplete="off" style={{ flex: 2, minWidth: 0 }}>
              <div className="mb-3 position-relative">
                <label htmlFor="headerInput" className="form-label fw-semibold" style={{ color: '#374151' }}>
                  Paste Raw Email Header
                  <span className="ms-1" tabIndex="0" data-bs-toggle="tooltip" title="You can find the email header in your email client's 'Show Original' or 'View Source' option. Paste the full header here for best results.">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#6366f1" viewBox="0 0 16 16">
  <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 13A6 6 0 1 1 8 2a6 6 0 0 1 0 12z"/>
  <path d="M8.93 6.588a.5.5 0 0 0-.854-.354l-2.29 2.29a.5.5 0 0 0 .708.708l1.147-1.146V10.5a.5.5 0 0 0 1 0V6.588zM8 4.5a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1z"/>
</svg>
                    </span>
                  </label>
                  <textarea
                    id="headerInput"
                    className="form-control"
                    style={{ minHeight: 120, fontFamily: 'monospace', fontSize: '1rem' }}
                    value={header}
                    onChange={e => setHeader(e.target.value)}
                    placeholder="Paste the full raw email header here..."
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary w-100 fw-bold" style={{ fontSize: '1.15rem', borderRadius: 8 }} disabled={loading}>
                  {loading ? 'Analyzing...' : 'Analyze Header'}
                </button>
                {error && (
                  <div className="alert alert-danger mt-3" role="alert">
                    {error}
                  </div>
                )}
              </form>
              {showInfo && (
                <div className="d-none d-md-block flex-shrink-0" style={{ flex: 1, minWidth: 260, maxWidth: 320 }}>
                  <InfoBanner onClose={() => setShowInfo(false)} />
                </div>
              )}
            </div>
            {/* Show InfoBanner below form on mobile */}
            {showInfo && (
              <div className="d-block d-md-none mt-3">
                <InfoBanner onClose={() => setShowInfo(false)} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/help" element={<HelpPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
}

export default App;