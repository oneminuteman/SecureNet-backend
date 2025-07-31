const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    trim: true,
  },
  email: {
    type: String,
    required: true,
    lowercase: true,
    unique: true,
  },
  password: {
    type: String,
    required: true,
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user',
  },
}, { timestamps: true });

// 🔐 Hash password before saving
userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 10);
  next();
});

// 🛠️ Static method to create admin safely
userSchema.statics.createAdminIfNotExists = async function () {
  const email = 'admin@secureNetAI.com';
  const existing = await this.findOne({ email });
  if (existing) return '⚠️ Admin already exists';

  const admin = new this({
    username: 'admin',
    email,
    password: 'supersecretekey', // will be hashed by pre-save
    role: 'admin',
  });
  await admin.save();
  return '✅ Admin user created';
};

const User = mongoose.model('User', userSchema);
module.exports = User;
