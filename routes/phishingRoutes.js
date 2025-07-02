const express = require('express');
const router = express.Router();
const PhishingLog = require('../models/PhishingLog');

// Log a phishing click
router.post('/click', async (req, res) => {
  try {
    const { user_id } = req.body;
    const log = new PhishingLog({ user_id, clicked: true });
    await log.save();
    res.status(201).json({ message: 'Click logged.' });
  } catch (err) {
    console.error('Error in /click:', err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// Log fake credential submission
router.post('/submit', async (req, res) => {
  try {
    const { user_id } = req.body;
    await PhishingLog.findOneAndUpdate(
      { user_id, clicked: true },
      { submitted_credentials: true },
      { new: true }
    );
    res.status(200).json({ message: 'Credential submission logged.' });
  } catch (err) {
    console.error('Error in /submit:', err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// Get all phishing logs
router.get('/logs', async (req, res) => {
  try {
    const logs = await PhishingLog.find();
    res.status(200).json(logs);
  } catch (err) {
    console.error('Error in /logs:', err);
    res.status(500).json({ error: 'Could not fetch logs.' });
  }
});

module.exports = router;
