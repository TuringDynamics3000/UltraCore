import { useRoute, useLocation } from "wouter";
import { ArrowLeft, Brain, TrendingUp, Activity, Target, Zap, Play, Pause, RotateCcw, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { trpc } from "@/lib/trpc";
import { useEffect, useRef } from "react";
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default function AgentDetail() {
  const [, params] = useRoute("/agents/:name");
  const [, setLocation] = useLocation();
  const agentName = params?.name || "";

  const { data: agent, isLoading } = trpc.rlAgent.getByName.useQuery({ name: agentName as any });
  const { data: trainingRuns } = trpc.rlAgent.getTrainingRuns.useQuery(
    { agentName },
    { enabled: !!agentName }
  );

  const rewardChartRef = useRef<HTMLCanvasElement>(null);
  const rewardChartInstanceRef = useRef<Chart | null>(null);

  const getAgentIcon = (name: string) => {
    const icons: Record<string, any> = {
      alpha: Brain,
      beta: Target,
      gamma: Activity,
      delta: TrendingUp,
      epsilon: Zap,
    };
    return icons[name] || Brain;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed':
        return 'default';
      case 'training':
        return 'secondary';
      case 'paused':
        return 'outline';
      default:
        return 'outline';
    }
  };

  // Generate reward chart
  useEffect(() => {
    if (!agent || !rewardChartRef.current) return;

    // Generate mock training history data
    const episodes = 50;
    const labels: string[] = [];
    const rewards: number[] = [];
    const avgReward = Number(agent.avgReward);

    for (let i = 0; i < episodes; i++) {
      labels.push(`Ep ${i * 1000}`);
      // Simulate learning curve: starts low, increases with diminishing returns
      const progress = i / episodes;
      const learningCurve = avgReward * (1 - Math.exp(-3 * progress));
      const noise = (Math.random() - 0.5) * avgReward * 0.2;
      rewards.push(Math.max(0, learningCurve + noise));
    }

    // Destroy existing chart
    if (rewardChartInstanceRef.current) {
      rewardChartInstanceRef.current.destroy();
    }

    const ctx = rewardChartRef.current.getContext('2d');
    if (!ctx) return;

    rewardChartInstanceRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Reward per Episode',
            data: rewards,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: (context: any) => {
                return `Reward: ${context.parsed.y.toFixed(2)}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxTicksLimit: 10,
            },
          },
          y: {
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
            },
            ticks: {
              callback: (value: any) => {
                return value.toFixed(0);
              },
            },
          },
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false,
        },
      },
    });

    return () => {
      if (rewardChartInstanceRef.current) {
        rewardChartInstanceRef.current.destroy();
      }
    };
  }, [agent]);

  if (isLoading) {
    return (
      <div className="container py-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/agents")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="h-8 w-48 bg-muted animate-pulse rounded" />
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="container py-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/agents")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-3xl font-bold">Agent Not Found</h1>
        </div>
      </div>
    );
  }

  const Icon = getAgentIcon(agent.name);

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => setLocation("/agents")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-primary/10">
              <Icon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">{agent.displayName}</h1>
              <p className="text-muted-foreground">{agent.modelVersion}</p>
            </div>
          </div>
        </div>
        <Badge variant={getStatusColor(agent.status)} className="text-base px-4 py-1">
          {agent.status}
        </Badge>
      </div>

      {/* Objective */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Objective</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{agent.objective}</p>
        </CardContent>
      </Card>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Episodes Trained</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agent.episodesTrained.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Total training episodes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Average Reward</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Number(agent.avgReward).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Mean episode reward
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Model Version</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agent.modelVersion}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Current deployment
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Last Trained</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agent.lastTrainedAt ? new Date(agent.lastTrainedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Most recent session
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Training Performance Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Training Performance</CardTitle>
            <CardDescription>
              Reward progression over training episodes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <canvas ref={rewardChartRef} />
            </div>
          </CardContent>
        </Card>

        {/* Agent Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Controls</CardTitle>
            <CardDescription>
              Manage agent training and deployment
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full" variant="default">
              <Play className="h-4 w-4 mr-2" />
              Start Training
            </Button>
            <Button className="w-full" variant="outline">
              <Pause className="h-4 w-4 mr-2" />
              Pause Training
            </Button>
            <Button className="w-full" variant="outline">
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset Agent
            </Button>
            <Button className="w-full" variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export Model
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Training Runs History */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Training History</CardTitle>
          <CardDescription>
            Recent training runs and their outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          {trainingRuns && trainingRuns.length > 0 ? (
            <div className="space-y-4">
              {trainingRuns.slice(0, 5).map((run) => (
                <div key={run.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <div className="font-medium">Run #{run.id}</div>
                    <div className="text-sm text-muted-foreground">
                      {run.episodes} episodes • Avg Reward: {Number(run.avgReward || 0).toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant={run.status === 'completed' ? 'default' : 'secondary'}>
                      {run.status}
                    </Badge>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(run.startedAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No training runs found</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
