const express = require('express');
const router = express.Router();
const { isAdmin } = require('../middleware/auth');

router.get('/dashboard', isAdmin => {
  res.json({ message: 'Welcome, admin!' });
});

module.exports = router;