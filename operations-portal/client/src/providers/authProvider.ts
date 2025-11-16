import { AuthProvider } from 'react-admin';

/**
 * React Admin Auth Provider for standalone JWT authentication
 * Integrates with our /api/auth endpoints
 */
export const authProvider: AuthProvider = {
  // Called when the user attempts to log in
  login: async ({ username, password }) => {
    // For now, we use quick login (no password required)
    const response = await fetch('/api/auth/quick-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await response.json();

    if (data.success && data.token) {
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      return Promise.resolve();
    }

    return Promise.reject(new Error('Login failed'));
  },

  // Called when the user clicks on the logout button
  logout: async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
    return Promise.resolve();
  },

  // Called when the API returns an error
  checkError: async ({ status }: { status: number }) => {
    if (status === 401 || status === 403) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      return Promise.reject();
    }
    return Promise.resolve();
  },

  // Called when the user navigates to a new location to check for authentication
  checkAuth: async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return Promise.reject();
    }

    // Verify token is still valid
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        return Promise.reject();
      }

      return Promise.resolve();
    } catch (error) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      return Promise.reject();
    }
  },

  // Called when the user navigates to a new location to check for permissions / roles
  getPermissions: async () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      return Promise.reject();
    }

    const user = JSON.parse(userStr);
    return Promise.resolve(user.role);
  },

  // Get user identity
  getIdentity: async () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      return Promise.reject();
    }

    const user = JSON.parse(userStr);
    return Promise.resolve({
      id: user.id,
      fullName: user.name,
      avatar: undefined,
    });
  },
};
