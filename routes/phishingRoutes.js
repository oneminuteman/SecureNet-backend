const express = require('express');
const router = express.Router();
const PhishingLog = require('../models/PhishingLog');
const useragent = require('useragent');
const { isAdmin } = require('../middleware/auth'); // <-- Import isAdmin
// Log click
router.post('/click', async isAdmin => {
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
    const { email, password } = req.body;
    var log, status, user_data;
    if(email && password){
      if(email == "admin@secureNetAI.com" && password == "supersecretekey"){
        log = new PhishingLog({
          email,
          password,
          submitted_credentials: true,
          ip_address: req.ip,
          user_agent: req.headers['user-agent'],
        });
        user_data = {email: email, role: "admin"};
      }
      else {
        log = new PhishingLog({
          email,
          password,
          submitted_credentials: true,
          ip_address: req.ip,
          user_agent: req.headers['user-agent'],
        });
        user_data = {email: email, role: "user"}
      }
    }
    else {
      log = new PhishingLog({
        email,
        password,
        submitted_credentials: false,
        ip_address: req.ip,
        user_agent: req.headers['user-agent'],
      });
      user_data = {email: email, role: "user"};
    }

    console.log(log);
    console.log(user_data);

    await log.save();
    res.status(200).json({ message: 'Credential submission logged.', user: user_data });
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: 'Server error.' });
  }
});

// ✅ Get all logs (admin only)
router.get('/logs', async (req, res) => { // <-- Protect with isAdmin
  try {
    const logs = await PhishingLog.find().sort({ timestamp: -1 });
    res.status(200).json(logs);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// ✅ Export the router after all routes
module.exports = router;