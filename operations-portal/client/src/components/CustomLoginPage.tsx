import { useState } from 'react';
import { useLogin, useNotify } from 'react-admin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Rocket } from 'lucide-react';

export default function CustomLoginPage() {
  const [loading, setLoading] = useState(false);
  const login = useLogin();
  const notify = useNotify();

  const handleQuickLogin = async () => {
    setLoading(true);
    try {
      await login({ quickLogin: true });
      // Redirect handled by React Admin
    } catch (error) {
      notify('Login failed', { type: 'error' });
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-4 text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
            <Rocket className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold">UltraCore Operations Portal</CardTitle>
          <CardDescription>
            Professional operations management for UltraCore
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleQuickLogin}
            disabled={loading}
            className="w-full h-12 text-base font-semibold"
            size="lg"
          >
            {loading ? 'Signing in...' : 'Quick Login as Admin'}
          </Button>
          <p className="text-xs text-center text-muted-foreground mt-4">
            Standalone JWT Authentication • No External Dependencies
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
