import { trpc } from '../lib/trpc';

export default function Login() {
  const utils = trpc.useUtils();
  const quickLogin = trpc.auth.quickLogin.useMutation({
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.token);
      utils.auth.me.invalidate();
    },
  });

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0f172a' }}>
      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', textAlign: 'center' }}>
        <h1 style={{ marginBottom: '1rem' }}>UltraCore Operations Portal</h1>
        <p style={{ marginBottom: '2rem', color: '#64748b' }}>Standalone JWT Authentication</p>
        <button
          onClick={() => quickLogin.mutate()}
          disabled={quickLogin.isPending}
          style={{
            background: '#3b82f6',
            color: 'white',
            padding: '0.75rem 2rem',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem',
          }}
        >
          {quickLogin.isPending ? 'Logging in...' : 'Login as Admin'}
        </button>
        <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#94a3b8' }}>
          No Manus OAuth required
        </p>
      </div>
    </div>
  );
}
