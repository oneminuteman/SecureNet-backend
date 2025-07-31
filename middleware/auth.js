// middleware/auth.js
const jwt = require('jsonwebtoken');

function isAdmin(req, res, next) {
  // Check for the token in the Authorization header
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'No token provided or malformed Authorization header' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Check if the user is an admin
    if (decoded.role !== 'admin') {
      return res.status(403).json({ message: 'Access denied. Admins only.' });
    }

    // Attach decoded user to request for downstream use
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ message: 'Invalid or expired token' });
  }
}

module.exports = isAdmin;

