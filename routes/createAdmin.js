const mongoose = require('mongoose');
require('dotenv').config();
const User = require('./models/User');

// Connect and create admin
(async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ Connected to MongoDB');

    const result = await User.createAdminIfNotExists();
    console.log(result);

    await mongoose.disconnect();
  } catch (err) {
    console.error('❌ Error:', err.message);
  }
})();
