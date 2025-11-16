import { Router } from 'express';
import { SignJWT } from 'jose';

const router = Router();

// Hardcoded admin user for development
const ADMIN_USER = {
  id: '1',
  openId: 'admin-local',
  email: 'admin@ultracore.com',
  name: 'Admin',
  role: 'admin' as const,
};

// JWT secret (use environment variable in production)
const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'ultracore-operations-portal-secret-key-change-in-production'
);

// Quick login endpoint (no password for development)
router.post('/api/auth/quick-login', async (req, res) => {
  try {
    // Generate JWT token
    const token = await new SignJWT({
      userId: ADMIN_USER.id,
      openId: ADMIN_USER.openId,
      email: ADMIN_USER.email,
      name: ADMIN_USER.name,
      role: ADMIN_USER.role,
    })
      .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
      .setIssuedAt()
      .setExpirationTime('7d')
      .sign(JWT_SECRET);

    res.json({
      success: true,
      token,
      user: ADMIN_USER,
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ success: false, error: 'Login failed' });
  }
});

// Get current user endpoint
router.get('/api/auth/me', async (req, res) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  try {
    const token = authHeader.substring(7);
    const { jwtVerify } = await import('jose');
    const { payload } = await jwtVerify(token, JWT_SECRET);

    res.json({
      id: payload.userId,
      openId: payload.openId,
      email: payload.email,
      name: payload.name,
      role: payload.role,
    });
  } catch (error) {
    console.error('Auth verification error:', error);
    res.status(401).json({ error: 'Invalid token' });
  }
});

// Logout endpoint
router.post('/api/auth/logout', (req, res) => {
  res.json({ success: true });
});

export default router;
