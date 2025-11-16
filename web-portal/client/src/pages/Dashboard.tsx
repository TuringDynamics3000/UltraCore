import { trpc } from '../lib/trpc';

export default function Dashboard() {
  const { data: user } = trpc.auth.me.useQuery();

  const stats = [
    { label: 'Total Portfolios', value: '12', change: '+2 this month', positive: true },
    { label: 'Securities Universe', value: '454', change: '72 ETFs tracked', positive: true },
    { label: 'Active Loans', value: '48', change: '$2.4M deployed', positive: true },
    { label: 'RL Agents Running', value: '5', change: 'All operational', positive: true },
  ];

  const modules = [
    { name: 'Portfolios', icon: '📊', description: '12 portfolios under management', href: '/portfolios' },
    { name: 'Securities', icon: '💼', description: '454 instruments tracked', href: '/securities' },
    { name: 'ESG Scoring', icon: '🌱', description: 'Environmental, Social, Governance', href: '/esg' },
    { name: 'UltraGrow Loans', icon: '💰', description: '48 active loans', href: '/loans' },
    { name: 'RL Agents', icon: '🤖', description: 'Alpha, Beta, Gamma, Delta, Epsilon', href: '/agents' },
    { name: 'Kafka Streaming', icon: '📡', description: 'Real-time event processing', href: '/kafka' },
    { name: 'Data Mesh', icon: '🗄️', description: '72 ETF parquet files', href: '/datamesh' },
    { name: 'MCP Integration', icon: '🔌', description: 'Model Context Protocol', href: '/mcp' },
    { name: 'Larry AI', icon: '💬', description: 'Operations Assistant', href: '/larry' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🚀</span>
            <h1 className="text-2xl font-bold text-white">UltraCore Operations Portal</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-300">Welcome, {user?.name || 'Admin'}</span>
            <button
              onClick={() => {
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
              }}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* KPI Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-blue-500/50 transition-all"
            >
              <div className="text-slate-400 text-sm mb-2">{stat.label}</div>
              <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
              <div className={`text-sm ${stat.positive ? 'text-green-400' : 'text-red-400'}`}>
                {stat.change}
              </div>
            </div>
          ))}
        </div>

        {/* Modules Grid */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Operations Modules</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((module) => (
              <a
                key={module.name}
                href={module.href}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-blue-500/50 hover:scale-105 transition-all group"
              >
                <div className="text-4xl mb-4">{module.icon}</div>
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                  {module.name}
                </h3>
                <p className="text-slate-400 text-sm">{module.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Manus Independence Status */}
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">✅</span>
            Manus Independence Status
          </h2>
          <div className="space-y-3">
            {[
              'Standalone JWT Authentication',
              'Direct OpenAI SDK Integration',
              'No Manus OAuth Dependency',
              'Hosted in UltraCore Repository',
              'Full Source Code Control',
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 text-slate-300">
                <span className="text-green-400">✓</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
