import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  LayoutDashboard, 
  Leaf,
  DollarSign,
  Brain,
  Activity,
  Database,
  Wrench,
  TrendingUp,
  Users,
  AlertCircle,
  HelpCircle
} from "lucide-react";
import { useLocation } from "wouter";
import { InfoTooltip } from "@/components/InfoTooltip";
import { InfoCard } from "@/components/InfoCard";
import { OnboardingTour } from "@/components/OnboardingTour";
import { Button } from "@/components/ui/button";

export default function Home() {
  const [, setLocation] = useLocation();
  const [runTour, setRunTour] = useState(false);

  useEffect(() => {
    // Check if user has completed the tour
    const tourCompleted = localStorage.getItem('ultracore-tour-completed');
    if (!tourCompleted) {
      // Auto-start tour for first-time users after a short delay
      setTimeout(() => setRunTour(true), 1000);
    }
  }, []);

  const handleTourFinish = () => {
    setRunTour(false);
    localStorage.setItem('ultracore-tour-completed', 'true');
  };

  const handleStartTour = () => {
    setRunTour(true);
  };

  const modules = [
    {
      title: "Portfolios",
      description: "Manage investment portfolios and holdings",
      icon: LayoutDashboard,
      path: "/portfolios",
      stats: "12 Active",
      color: "text-blue-600"
    },
    {
      title: "ESG Data",
      description: "Environmental, Social, and Governance metrics",
      icon: Leaf,
      path: "/esg",
      stats: "85% Coverage",
      color: "text-green-600"
    },
    {
      title: "UltraGrow Loans",
      description: "Loan applications and payment tracking",
      icon: DollarSign,
      path: "/loans",
      stats: "$2.4M Active",
      color: "text-emerald-600"
    },
    {
      title: "RL Agents",
      description: "Reinforcement learning agent monitoring",
      icon: Brain,
      path: "/agents",
      stats: "5 Agents",
      color: "text-purple-600"
    },
    {
      title: "Kafka Events",
      description: "Real-time event stream monitoring",
      icon: Activity,
      path: "/kafka",
      stats: "1.2k/sec",
      color: "text-orange-600"
    },
    {
      title: "Data Mesh",
      description: "Data product catalog and analytics",
      icon: Database,
      path: "/data-mesh",
      stats: "137 Products",
      color: "text-cyan-600"
    },
    {
      title: "MCP Tools",
      description: "Model Context Protocol tools registry",
      icon: Wrench,
      path: "/mcp",
      stats: "24 Tools",
      color: "text-indigo-600"
    }
  ];

  const kpis = [
    {
      title: "Total AUM",
      value: "$45.2M",
      change: "+12.5%",
      trend: "up",
      icon: TrendingUp,
      tooltip: "Assets Under Management: Total market value of all portfolios managed by the platform"
    },
    {
      title: "Active Portfolios",
      value: "12",
      change: "+2",
      trend: "up",
      icon: LayoutDashboard
    },
    {
      title: "Active Loans",
      value: "48",
      change: "+8",
      trend: "up",
      icon: DollarSign
    },
    {
      title: "System Health",
      value: "98.5%",
      change: "+0.3%",
      trend: "up",
      icon: Activity
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Operations Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Comprehensive management portal for UltraCore operations
          </p>
        </div>
        <Button variant="outline" onClick={handleStartTour} className="gap-2">
          <HelpCircle className="h-4 w-4" />
          Start Tour
        </Button>
      </div>

      {/* Info Card */}
      <InfoCard title="Welcome to UltraCore Operations Portal">
        <p>
          This dashboard provides real-time monitoring and management of all UltraCore systems including
          portfolio management, RL agent training, event streaming, and data analytics. Navigate through
          the modules below to access specific functionality.
        </p>
      </InfoCard>

      {/* KPI Cards */}
      <div data-tour="kpi-cards" className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi) => (
          <Card key={kpi.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-1">
                {kpi.title}
                {(kpi as any).tooltip && <InfoTooltip content={(kpi as any).tooltip} />}
              </CardTitle>
              <kpi.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                <span className="text-green-600">{kpi.change}</span> from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Module Grid */}
      <div data-tour="modules">
        <h2 className="text-xl font-semibold mb-4">Modules</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {modules.map((module, index) => (
            <Card 
              key={module.path}
              data-tour={index === 0 ? "portfolios-module" : index === 2 ? "securities-module" : index === 4 ? "kafka-module" : index === 3 ? "rl-agents-module" : undefined}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setLocation(module.path)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-muted ${module.color}`}>
                      <module.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{module.title}</CardTitle>
                      <CardDescription className="text-xs mt-1">
                        {module.stats}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {module.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            System Status
          </CardTitle>
          <CardDescription>
            Real-time monitoring of UltraCore infrastructure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Kafka Event Bus</span>
              <span className="text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Data Mesh</span>
              <span className="text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">RL Agent Training</span>
              <span className="text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">MCP Server (Anya AI)</span>
              <span className="text-sm font-medium text-green-600">Operational</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Onboarding Tour */}
      <OnboardingTour run={runTour} onFinish={handleTourFinish} />
    </div>
  );
}
