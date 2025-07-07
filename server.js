const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const cors = require('cors'); // 👈 ADD THIS
const phishingRoutes = require('./routes/phishingRoutes');

dotenv.config();

const app = express();
app.use(cors()); // 👈 AND THIS
app.use(express.json());

app.use('/api/phishing', phishingRoutes);

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('✅ MongoDB Connected'))
  .catch(err => console.error(err));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
