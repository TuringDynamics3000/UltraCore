import { Route, Switch } from 'wouter';
import { trpc } from './lib/trpc';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

export default function App() {
  const { data: user, isLoading } = trpc.auth.me.useQuery();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Login />;
  }

  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/dashboard" component={Dashboard} />
      <Route>404 Not Found</Route>
    </Switch>
  );
}
