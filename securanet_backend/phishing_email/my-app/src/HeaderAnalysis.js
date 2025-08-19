import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Section({ title, icon, children }) {
  return (
    <div style={{ background: '#fff', borderRadius: 14, boxShadow: '0 2px 12px rgba(99,102,241,0.07)', marginBottom: 32, border: '1.5px solid #e0e7eb', padding: '24px 20px 28px 20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
        <span style={{ fontSize: '1.7rem', marginRight: 2 }}>{icon}</span>
        <span style={{ color: '#1e3a8a', fontSize: '1.18rem', fontWeight: 700, letterSpacing: '0.01em', lineHeight: 1.2 }}>{title}</span>
      </div>
      <div style={{ height: 2, background: 'linear-gradient(90deg, #6366f1 0%, #e0e7ff 100%)', borderRadius: 2, marginBottom: 18, opacity: 0.13 }} />
      {children}
    </div>
  );
}

function InfoIcon({ text }) {
  return (
    <span style={{ marginLeft: 6, cursor: 'pointer', color: '#6366f1' }} title={text}>
      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" stroke="#6366f1" strokeWidth="2" fill="none"/><text x="8" y="12" textAnchor="middle" fontSize="10" fill="#6366f1">i</text></svg>
    </span>
  );
}

function WarningBox({ children }) {
  return (
    <div style={{ background: '#fffbe6', border: '1px solid #fde68a', color: '#b45309', borderRadius: 10, padding: 18, marginBottom: 32, fontWeight: 600, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: 12 }}>
      <span style={{ fontSize: 28 }}>⚠️</span> {children}
    </div>
  );
}

function Badge({ ok, text, color }) {
  let bg = ok ? '#e0e7ff' : '#fee2e2';
  let fg = ok ? (color || '#2563eb') : '#dc2626';
  let border = ok ? (color || '#2563eb') : '#dc2626';
  return (
    <span style={{
      display: 'inline-block',
      background: bg,
      color: fg,
      border: `2px solid ${border}`,
      borderRadius: 8,
      padding: '4px 16px',
      fontWeight: 700,
      fontSize: '1.1rem',
      marginRight: 12,
      marginBottom: 8
    }}>{ok ? '✔' : '✖'} {text}</span>
  );
}

function TagTable({ tags }) {
  if (!tags || Object.keys(tags).length === 0) return <div style={{ color: '#6b7280' }}>No tags found.</div>;
  return (
    <table className="table table-sm" style={{ background: '#f3f4f6', borderRadius: 8, marginTop: 10, tableLayout: 'fixed', width: '100%' }}>
      <colgroup>
        <col style={{ width: '80px' }} />
        <col style={{ width: '220px' }} />
        <col />
      </colgroup>
      <thead><tr><th>Tag</th><th>Value</th><th>Description</th></tr></thead>
      <tbody>
        {Object.entries(tags).map(([k, v]) => (
          <tr key={k}>
            <td>{k}</td>
            <td style={{ maxWidth: 220, wordBreak: 'break-all', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', display: 'block', overflow: 'hidden' }}>{v.value}</td>
            <td>{v.explanation}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function HopTable({ hops }) {
  if (!hops || hops.length === 0) return <div style={{ color: '#6b7280' }}>No relay information found.</div>;
  return (
    <table className="table table-bordered table-sm" style={{ background: '#f3f4f6', borderRadius: 8, marginTop: 10 }}>
      <thead><tr><th>Hop</th><th>Delay</th><th>From</th><th>By</th><th>IP</th><th>Time</th><th>Blacklist</th></tr></thead>
      <tbody>
        {hops.map((hop, i) => (
          <tr key={i}>
            <td>{i + 1}</td>
            <td>{hop.delay == null ? '*' : hop.delay + 's'}</td>
            <td>{hop.from}</td>
            <td>{hop.by}</td>
            <td>{hop.from_ip}</td>
            <td>{hop.timestamp}</td>
            <td>{hop.blacklisted ? <span style={{ color: '#dc2626', fontWeight: 700 }}>⚠ {hop.blacklists?.join(', ')}</span> : <span style={{ color: '#2563eb', fontWeight: 700 }}>✔</span>}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TimelineBar({ timeline }) {
  if (!timeline || timeline.length < 2) return null;
  const max = Math.max(...timeline.filter(x => typeof x === 'number'));
  return (
    <div style={{ margin: '18px 0 10px', padding: 0 }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
        {timeline.map((delay, i) => (
          <div key={i} style={{ width: 40, height: delay && max ? (delay / max) * 60 + 10 : 10, background: '#60a5fa', borderRadius: 4, textAlign: 'center', color: '#fff', fontWeight: 700, fontSize: '0.95rem', display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}>
            {delay ? delay + 's' : '*'}
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 8, fontSize: '0.9rem', color: '#6b7280', marginTop: 2 }}>
        {timeline.map((_, i) => <div key={i} style={{ width: 40, textAlign: 'center' }}>Hop {i + 1}</div>)}
      </div>
    </div>
  );
}

function HeadersTable({ headers }) {
  if (!headers || headers.length === 0) return null;
  return (
    <table className="table table-sm" style={{ background: '#f3f4f6', borderRadius: 8, marginTop: 10 }}>
      <thead><tr><th>Header Name</th><th>Header Value</th></tr></thead>
      <tbody>
        {headers.map((h, i) => <tr key={i}><td>{h.name}</td><td>{h.value}</td></tr>)}
      </tbody>
    </table>
  );
}

function Collapsible({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ cursor: 'pointer', color: '#2563eb', fontWeight: 700 }} onClick={() => setOpen(o => !o)}>
        {open ? '▼' : '▶'} {title}
      </div>
      {open && <div style={{ marginTop: 8 }}>{children}</div>}
    </div>
  );
}

function RiskSummary({ classification, risk_score, confidence }) {
  let color = '#2563eb', bg = '#e0e7ff', icon = 'ℹ️', label = 'Analysis Results';
  let showConfidence = confidence !== undefined && confidence !== null && confidence > 0;
  if (classification) {
    const c = classification.toLowerCase();
    if (c.includes('legit')) {
      color = '#059669'; bg = '#d1fae5'; icon = '✅'; label = 'Legitimate';
    } else if (c.includes('phish') || c.includes('spam')) {
      color = '#dc2626'; bg = '#fee2e2'; icon = '🚨'; label = 'Phishing/Spam';
    } else if (c.includes('suspicious')) {
      color = '#f59e42'; bg = '#fef3c7'; icon = '⚠️'; label = 'Suspicious';
    } else if (c === 'unknown' || c === 'uncertain' || c === '' || c === 'analysis results') {
      label = 'Analysis Results';
    } else {
      label = classification.charAt(0).toUpperCase() + classification.slice(1);
    }
  }
  return (
    <div style={{ background: bg, border: `2px solid ${color}`, borderRadius: 14, boxShadow: '0 2px 12px rgba(99,102,241,0.07)', marginBottom: 32, padding: '18px 24px', display: 'flex', alignItems: 'center', gap: 24 }}>
      <span style={{ fontSize: '2.1rem', marginRight: 8 }}>{icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: '1.13rem', color }}>{label}</div>
        <div style={{ fontSize: '0.98rem', color: '#374151', marginTop: 2 }}>
          Risk Score: <b>{risk_score !== undefined ? risk_score : '?'}</b>
          {showConfidence && (
            <span style={{ marginLeft: 18, color: '#6366f1' }}>Confidence: <b>{Math.round(confidence * 100)}%</b></span>
          )}
        </div>
      </div>
    </div>
  );
}

function HeaderAnalysis({ data }) {
  const navigate = useNavigate();
  if (!data) return null;
  const {
    summary = {},
    copy_paste_warning = [],
    delivery_info = {},
    relay_info = { hops: [], timeline: [] },
    spf_dkim_dmarc_records = {},
    headers_found = [],
    ip_info = {},
    warnings = [],
    classification,
    risk_score,
    confidence
  } = data;
  // Highlight multiple DKIM selectors
  const dkimRecords = Array.isArray(spf_dkim_dmarc_records.dkim) ? spf_dkim_dmarc_records.dkim : [];
  const authResultsList = data.authentication_results_list || [];
  return (
    <div style={{ fontFamily: 'Georgia, Times New Roman, serif', maxWidth: 1400, width: '90vw', margin: 'auto', padding: 20, borderRadius: 16, background: 'linear-gradient(120deg, #e0e7ff 60%, #f0f4ff 100%)', fontSize: '0.97rem', boxShadow: '0 8px 30px rgba(99,102,241,0.13)', border: '2px solid #6366f1' }}>
      <button
        onClick={() => navigate('/')}
        style={{
          background: 'linear-gradient(90deg, #6366f1 0%, #60a5fa 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          padding: '10px 28px',
          fontWeight: 700,
          fontSize: '1.08rem',
          boxShadow: '0 2px 8px rgba(99,102,241,0.10)',
          marginBottom: 28,
          cursor: 'pointer',
          transition: 'background 0.2s',
          float: 'right',
        }}
      >
        + New Analysis
      </button>
      <div style={{ clear: 'both' }} />
      <RiskSummary classification={classification} risk_score={risk_score} confidence={confidence} />
      {dkimRecords.length > 1 && (
        <div className="alert alert-info" style={{ background: '#e0e7ff', color: '#1e3a8a', borderRadius: 10, fontWeight: 600, marginBottom: 24 }}>
          Multiple DKIM signatures found: {dkimRecords.map(d => <span key={d.selector} style={{ marginRight: 8 }}><b>{d.selector}</b></span>)}
        </div>
      )}
      <Section title="Header Analyzed" icon="📋">
        <div><b>Subject:</b> {summary.subject || ''}</div>
        <div><b>From:</b> {(summary.from?.name || '') + ' <' + (summary.from?.email || '') + '>'}</div>
        <div><b>To:</b> {summary.to || ''}</div>
        <div><b>Date:</b> {summary.date || ''}</div>
        <div><b>Message-ID:</b> {summary.message_id || ''}</div>
        <div><b>Return-Path:</b> {summary.return_path || ''}</div>
      </Section>
      {copy_paste_warning && copy_paste_warning.length > 0 && (
        <WarningBox>
          <ul style={{ margin: 0, paddingLeft: 20 }}>{copy_paste_warning.map((w, i) => <li key={i}>{w}</li>)}</ul>
        </WarningBox>
      )}
      <Section title="Delivery Information" icon="📦">
        <div style={{ marginBottom: 18 }}>
          <Badge ok={delivery_info.dmarc?.compliant} text="DMARC Compliant" color="#059669" />
          <Badge ok={delivery_info.spf?.published} text="SPF Published" color="#2563eb" />
          <Badge ok={delivery_info.dkim?.published} text="DKIM Published" color="#a21caf" />
        </div>
        <div style={{ marginBottom: 18 }}>
          <b>Authentication Results:</b>
          <InfoIcon text="Parsed from the Authentication-Results header as seen by the receiving server." />
          <pre style={{ background: '#e0e7ff', borderRadius: 8, padding: 10, fontSize: '1rem', color: '#374151', marginTop: 6, wordBreak: 'break-all', whiteSpace: 'pre-wrap', overflowX: 'auto' }}>{JSON.stringify(delivery_info.authentication_results, null, 2)}</pre>
          {Array.isArray(authResultsList) && authResultsList.length > 1 && (
            <Collapsible title="Show all Authentication-Results headers">
              {authResultsList.map((ar, i) => (
                <pre key={i} style={{ background: '#f3f4f6', borderRadius: 8, padding: 10, fontSize: '0.97rem', color: '#374151', marginBottom: 8 }}>{JSON.stringify(ar, null, 2)}</pre>
              ))}
            </Collapsible>
          )}
        </div>
        <div style={{ marginBottom: 18 }}>
          <b>DMARC Alignment:</b> <Badge ok={delivery_info.dmarc?.alignment} text={delivery_info.dmarc?.alignment ? 'Aligned' : 'Not aligned'} color="#059669" />
          <InfoIcon text="DMARC alignment means the domain in the From address matches the domain authenticated by DMARC." />
          <b>SPF Alignment:</b> <Badge ok={delivery_info.spf?.alignment} text={delivery_info.spf?.alignment ? 'Aligned' : 'Not aligned'} color="#2563eb" />
          <InfoIcon text="SPF alignment means the domain in the From address matches the domain authenticated by SPF." />
          <b>DKIM Alignment:</b> <Badge ok={delivery_info.dkim?.alignment} text={delivery_info.dkim?.alignment ? 'Aligned' : 'Not aligned'} color="#a21caf" />
          <InfoIcon text="DKIM alignment means the domain in the From address matches the domain authenticated by DKIM." />
        </div>
      </Section>
      <Section title="Relay Information" icon="🚚">
        <HopTable hops={relay_info.hops} />
        <TimelineBar timeline={relay_info.timeline} />
      </Section>
      <Section title="SPF Record" icon="🔖">
        <div><b>Domain:</b> {spf_dkim_dmarc_records.spf?.domain || ''}</div>
        <div><b>Record:</b> {spf_dkim_dmarc_records.spf?.record || ''}</div>
        <TagTable tags={spf_dkim_dmarc_records.spf?.tags} />
      </Section>
      <Section title="DMARC Record" icon="🔖">
        <div><b>Domain:</b> {spf_dkim_dmarc_records.dmarc?.domain || ''}</div>
        <div><b>Record:</b> {spf_dkim_dmarc_records.dmarc?.record || ''}</div>
        <TagTable tags={spf_dkim_dmarc_records.dmarc?.tags} />
      </Section>
      <Section title="DKIM Records" icon="🔖">
        {dkimRecords.length === 0 && <div>No DKIM records found.</div>}
        {dkimRecords.map((dkim, i) => (
          <Collapsible key={i} title={`Selector: ${dkim.selector} (${dkim.domain})`} defaultOpen={dkimRecords.length === 1}>
            <div><b>Record:</b> {dkim.record}</div>
            <TagTable tags={dkim.tags} />
            <div style={{ marginTop: 8, fontSize: '0.97rem', color: '#374151', maxWidth: '100%', wordBreak: 'break-all', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}><b>Raw DKIM Signature:</b><br />
              <pre style={{ background: '#f3f4f6', borderRadius: 8, padding: 8, wordBreak: 'break-all', whiteSpace: 'pre-wrap', overflowX: 'auto', maxWidth: '100%' }}>{dkim.raw_signature}</pre>
            </div>
          </Collapsible>
        ))}
      </Section>
      <Section title="Headers Found" icon="📑">
        <HeadersTable headers={headers_found} />
      </Section>
      <Section title="Sender IP Location" icon="🌍">
        <pre style={{ background: '#e0e7ff', borderRadius: 8, padding: 10, fontSize: '1rem', color: '#374151' }}>{JSON.stringify(ip_info, null, 2)}</pre>
      </Section>
      {warnings && warnings.length > 0 && (
        <WarningBox>
          <ul style={{ margin: 0, paddingLeft: 20 }}>{warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>
        </WarningBox>
      )}
    </div>
  );
}

export default HeaderAnalysis; 