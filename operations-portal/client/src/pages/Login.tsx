import { useState } from 'react';
import { useLocation } from 'wouter';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Login() {
  const [, setLocation] = useLocation();
  const [loading, setLoading] = useState(false);

  const handleQuickLogin = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/quick-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const data = await response.json();

      if (data.success && data.token) {
        // Store token in localStorage
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to dashboard
        setLocation('/');
      } else {
        alert('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Card className="w-[400px]">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="text-4xl">🚀</div>
          </div>
          <CardTitle className="text-2xl text-center">UltraCore Operations Portal</CardTitle>
          <CardDescription className="text-center">
            Comprehensive management portal for UltraCore operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Button
              onClick={handleQuickLogin}
              disabled={loading}
              className="w-full"
              size="lg"
            >
              {loading ? 'Logging in...' : 'Quick Login as Admin'}
            </Button>
            
            <div className="text-xs text-center text-muted-foreground">
              <p>✅ Standalone JWT Authentication</p>
              <p>✅ No Manus OAuth Dependency</p>
              <p>✅ Direct OpenAI SDK Integration</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
