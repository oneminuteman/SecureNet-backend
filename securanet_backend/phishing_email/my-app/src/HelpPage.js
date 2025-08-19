import React from 'react';

const sectionIcon = (icon, label) => (
  <span style={{ fontSize: 22, marginRight: 10 }} aria-label={label} role="img">{icon}</span>
);

export default function HelpPage() {
  return (
    <div className="d-flex justify-content-center align-items-start min-vh-100 main-bg" style={{ paddingTop: 40 }}>
      <div className="card shadow-lg p-4" style={{ maxWidth: 850, width: '100%', borderRadius: 20, background: 'linear-gradient(120deg, #f8fafc 60%, #e0e7ff 100%)', border: 'none' }}>
        <h1 className="mb-4 text-center" style={{ color: '#4338ca', fontWeight: 800, letterSpacing: 1 }}>How to Get Email Headers</h1>
        <p className="lead text-center mb-5" style={{ color: '#374151' }}>
          Email headers contain technical details about the sender, recipient, and delivery path. Use the guide below to find and copy headers from your email client.
        </p>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('📧', 'Gmail')}Gmail</h2>
          <ol>
            <li>Open the message you’d like to view headers for.</li>
            <li>Click the down arrow next to Reply, at the top-right of the message pane.</li>
            <li>Select <b>Show original</b>.</li>
            <li>The full headers will appear in a new window. Right-click inside the headers and choose Select All, then right-click again and choose Copy.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('💼', 'Outlook')}Outlook (Desktop)</h2>
          <ol>
            <li>Double click on the email message so that it is opened in its own window.</li>
            <li>On the Message tab, in the Options section, click the small arrow in the corner.</li>
            <li>This opens the Message Options window. The Internet Headers are at the bottom.</li>
            <li>Right-click inside the headers, choose Select All, then right-click again and choose Copy.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('🌐', 'Outlook.com')}Outlook.com (Web)</h2>
          <ol>
            <li>Click to open the email message.</li>
            <li>On the top message action menu, click the three dots (More actions) on the far right.</li>
            <li>Select <b>View message source</b>.</li>
            <li>Copy all the text in the new window.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('📨', 'Yahoo')}Yahoo Mail</h2>
          <ol>
            <li>Click on an email to open it.</li>
            <li>Click the More icon (...).</li>
            <li>Select <b>View Raw Message</b>.</li>
            <li>Copy all the text in the new window.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('🍏', 'Apple Mail')}Apple Mail</h2>
          <ol>
            <li>Open Apple Mail and the email you wish to view.</li>
            <li>Click <b>View</b> &rarr; <b>Message</b> &rarr; <b>All Headers</b>.</li>
            <li>Headers will display in the window below your inbox. Copy the text.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('🔒', 'Proton Mail')}Proton Mail</h2>
          <ol>
            <li>Open the email in Proton Mail web or app.</li>
            <li>Go to More (3-dot icon) &rarr; <b>View headers</b>.</li>
            <li>Copy all the text in the new window.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('📬', 'Zoho Mail')}Zoho Mail</h2>
          <ol>
            <li>Open the email whose headers you would like to view.</li>
            <li>Click the More Actions drop-down on the right corner of the email.</li>
            <li>Choose the <b>Show Original</b> option.</li>
            <li>Copy all the text in the new window.</li>
          </ol>
        </div>
        <div className="mb-4">
          <h2 className="h4 mt-4" style={{ color: '#6366f1' }}>{sectionIcon('❓', 'Other Clients')}Other Clients</h2>
          <p>If your email client is not listed, check its documentation for how to view full message headers. Usually, the option is called "Show Original," "View Source," or "Internet Headers."</p>
        </div>
        <div className="mt-5 text-center">
          <a href="/" className="btn btn-lg btn-primary px-4 shadow-sm" style={{ borderRadius: 8, fontWeight: 600, letterSpacing: 1 }}>Back to Analyzer</a>
        </div>
      </div>
    </div>
  );
} 