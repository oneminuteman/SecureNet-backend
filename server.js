const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const phishingRoutes = require('./routes/phishingRoutes'); // 👈 Correct path

dotenv.config();

const app = express();
app.use(express.json());

// Use the phishing routes under this path
app.use('/api/phishing', phishingRoutes); // 👈 This must match what you're calling from Postman

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('✅ MongoDB Connected'))
  .catch(err => console.error(err));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
