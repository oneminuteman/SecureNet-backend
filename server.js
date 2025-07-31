// Load environment variables first
const dotenv = require('dotenv');
dotenv.config();

// Import dependencies
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

// Initialize express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Import routes
const phishingRoutes = require('./routes/phishingRoutes');
const authRoutes = require('./routes/auth');
const adminRoutes = require('./routes/admin');

// Base health check route
app.get('/', (req, res) => {
  res.send('✅ SecureNet backend is live!');
});

// Use routes
app.use('/api/auth', authRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/phishing', phishingRoutes);

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => console.log('✅ MongoDB Connected'))
  .catch(err => {
    console.error('❌ MongoDB connection error:', err.message);
    process.exit(1); // Optional: stop server if DB fails
  });

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running at http://localhost:${PORT}`));
