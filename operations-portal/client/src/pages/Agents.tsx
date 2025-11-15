import { Activity, Brain, TrendingUp, Zap, Target, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";

export default function Agents() {
  const [, setLocation] = useLocation();
  const { data: agents, isLoading } = trpc.rlAgent.list.useQuery();

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

  if (isLoading) {
    return (
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">RL Agents</h1>
          <p className="text-muted-foreground">Reinforcement learning agent monitoring and management</p>
        </div>

        {/* KPI Cards Loading */}
        <div className="grid gap-6 md:grid-cols-4 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="pb-3">
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
              </CardHeader>
              <CardContent>
                <div className="h-8 w-16 bg-muted animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Agent Cards Loading */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <CardHeader>
                <div className="h-6 w-32 bg-muted animate-pulse rounded mb-2" />
                <div className="h-4 w-48 bg-muted animate-pulse rounded" />
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 w-full bg-muted animate-pulse rounded" />
                  <div className="h-4 w-full bg-muted animate-pulse rounded" />
                  <div className="h-4 w-3/4 bg-muted animate-pulse rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const deployedAgents = agents?.filter(a => a.status === 'deployed').length || 0;
  const trainingAgents = agents?.filter(a => a.status === 'training').length || 0;
  const totalEpisodes = agents?.reduce((sum, a) => sum + a.episodesTrained, 0) || 0;
  const avgReward = agents?.length ? agents.reduce((sum, a) => sum + Number(a.avgReward), 0) / agents.length : 0;

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold">RL Agents</h1>
        <p className="text-muted-foreground">Reinforcement learning agent monitoring and management</p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Total Agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agents?.length || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {deployedAgents} deployed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Training Status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trainingAgents}</div>
            <p className="text-xs text-muted-foreground mt-1">
              agents currently training
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Total Episodes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalEpisodes.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">
              across all agents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              Avg Reward
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgReward.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              mean performance
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Agent Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {agents && agents.length > 0 ? (
          agents.map((agent) => {
            const Icon = getAgentIcon(agent.name);
            return (
              <Card key={agent.id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setLocation(`/agents/${agent.name}`)}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{agent.displayName}</CardTitle>
                        <CardDescription className="text-sm">{agent.modelVersion}</CardDescription>
                      </div>
                    </div>
                    <Badge variant={getStatusColor(agent.status)}>{agent.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {agent.objective}
                  </p>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Episodes Trained</span>
                      <span className="font-medium">{agent.episodesTrained.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Avg Reward</span>
                      <span className="font-medium">{Number(agent.avgReward).toFixed(2)}</span>
                    </div>
                    {agent.lastTrainedAt && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Last Trained</span>
                        <span className="font-medium">
                          {new Date(agent.lastTrainedAt).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>

                  <Button className="w-full mt-4" variant="outline" onClick={(e) => {
                    e.stopPropagation();
                    setLocation(`/agents/${agent.name}`);
                  }}>
                    View Details
                  </Button>
                </CardContent>
              </Card>
            );
          })
        ) : (
          <Card className="col-span-full">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No RL Agents Found</p>
              <p className="text-sm text-muted-foreground">
                No reinforcement learning agents are currently configured
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
