const express = require('express');
const router = express.Router();
const PhishingLog = require('../models/PhishingLog');

// POST /api/phishing/click
router.post('/click', async (req, res) => {
  try {
    const { user_id } = req.body;
    const log = new PhishingLog({ user_id, clicked: true });
    await log.save();
    res.status(201).json({ message: 'Click logged.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// POST /api/phishing/submit
router.post('/submit', async (req, res) => {
  try {
    const { user_id } = req.body;
    const updated = await PhishingLog.findOneAndUpdate(
      { user_id },
      { submitted_credentials: true },
      { new: true }
    );
    if (!updated) return res.status(404).json({ error: 'User not found' });
    res.status(200).json({ message: 'Credential submission logged.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// GET /api/phishing/logs
router.get('/logs', async (req, res) => {
  try {
    const logs = await PhishingLog.find();
    res.status(200).json(logs);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Could not fetch logs.' });
  }
});

module.exports = router;
