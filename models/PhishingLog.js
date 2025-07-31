const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const phishingLogSchema = new mongoose.Schema({
  email: String,
  password: String,
  clicked: {
    type: Boolean,
    default: false,
  },
  submitted_credentials: {
    type: Boolean,
    default: false,
  },
  ip_address: String,
  user_agent: String,
  timestamp: {
    type: Date,
    default: Date.now,
  }
});

// Encrypt password before saving
phishingLogSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  try {
    const salt = await bcrypt.genSalt(10);
    if(this.password != ""){
      this.password = await bcrypt.hash(this.password, salt);
    }
    else {
      this.password = "";
    }
    next();
  } catch (err) {
    next(err);
  }
});

module.exports = mongoose.model('PhishingLog', phishingLogSchema);
