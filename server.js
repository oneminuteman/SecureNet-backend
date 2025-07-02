console.log("✅ Server file started");

const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const phishingRoutes = require('./routes/phishingRoutes');

const app = express();
app.use(bodyParser.json());
app.use(cors());

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/secureNetDB', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log("MongoDB Connected"))
  .catch(err => console.log(err));

// Use phishing routes
app.use('/api/phishing', phishingRoutes);

// Test route to confirm server is running
app.get("/", (req, res) => {
  res.send("✅ SecureNet Phishing Server is Live!");
});


// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
