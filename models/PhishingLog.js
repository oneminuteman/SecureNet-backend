// models/PhishingLog.js

const mongoose = require('mongoose');

const PhishingLogSchema = new mongoose.Schema({
  user_id: {
    type: String,
    required: true
  },
  clicked: {
    type: Boolean,
    default: false
  },
  submitted_credentials: {
    type: Boolean,
    default: false
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('PhishingLog', PhishingLogSchema);
