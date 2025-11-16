import { trpc } from '../lib/trpc';

export default function Dashboard() {
  const { data: user } = trpc.auth.me.useQuery();
  const utils = trpc.useUtils();
  const logout = trpc.auth.logout.useMutation({
    onSuccess: () => {
      localStorage.removeItem('auth_token');
      utils.auth.me.invalidate();
    },
  });

  const larryTest = trpc.larry.test.useQuery();

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', color: 'white', padding: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>🚀 UltraCore Operations Portal</h1>
        <div>
          <span style={{ marginRight: '1rem' }}>Welcome, {user?.name}</span>
          <button
            onClick={() => logout.mutate()}
            style={{
              background: '#ef4444',
              color: 'white',
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Logout
          </button>
        </div>
      </header>

      <div style={{ background: '#1e293b', padding: '2rem', borderRadius: '8px', marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>✅ Manus Independence Status</h2>
        <ul style={{ lineHeight: '2' }}>
          <li>✅ Standalone JWT Authentication</li>
          <li>✅ Direct OpenAI SDK Integration</li>
          <li>✅ No Manus OAuth Dependency</li>
          <li>✅ Hosted in UltraCore Repository</li>
        </ul>
      </div>

      <div style={{ background: '#1e293b', padding: '2rem', borderRadius: '8px' }}>
        <h2 style={{ marginBottom: '1rem' }}>🤖 Larry AI Status</h2>
        {larryTest.isLoading && <p>Testing Larry AI...</p>}
        {larryTest.data && <p style={{ color: '#10b981' }}>{larryTest.data.message}</p>}
        {larryTest.error && <p style={{ color: '#ef4444' }}>Error: {larryTest.error.message}</p>}
      </div>
    </div>
  );
}
