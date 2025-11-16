import { Route, Switch } from 'wouter';
import { trpc } from './lib/trpc';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Portfolios from './pages/Portfolios';
import Securities from './pages/Securities';
import ESG from './pages/ESG';
import Loans from './pages/Loans';
import Agents from './pages/Agents';
import Kafka from './pages/Kafka';
import DataMesh from './pages/DataMesh';
import MCP from './pages/MCP';
import Larry from './pages/Larry';

export default function App() {
  const { data: user, isLoading } = trpc.auth.me.useQuery();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/portfolios" component={Portfolios} />
      <Route path="/securities" component={Securities} />
      <Route path="/esg" component={ESG} />
      <Route path="/loans" component={Loans} />
      <Route path="/agents" component={Agents} />
      <Route path="/kafka" component={Kafka} />
      <Route path="/datamesh" component={DataMesh} />
      <Route path="/mcp" component={MCP} />
      <Route path="/larry" component={Larry} />
      <Route>
        <div className="min-h-screen bg-slate-900 flex items-center justify-center">
          <div className="text-white text-xl">404 Not Found</div>
        </div>
      </Route>
    </Switch>
  );
}
