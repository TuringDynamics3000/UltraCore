import { useAuth } from "@/_core/hooks/useAuth";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { trpc } from "@/lib/trpc";
import { Activity, TrendingUp, Database, Clock, Search, Filter } from "lucide-react";
import { useState } from "react";
import { Streamdown } from 'streamdown';
import { InfoCard } from "@/components/InfoCard";
import { InfoTooltip } from "@/components/InfoTooltip";

export default function KafkaEvents() {
  const { user, loading: authLoading } = useAuth();
  const [searchTicker, setSearchTicker] = useState("");
  const [selectedTopic, setSelectedTopic] = useState<string>("all");
  const [limit, setLimit] = useState(50);

  // Fetch event statistics
  const { data: stats, isLoading: statsLoading } = trpc.securities.getEventStats.useQuery(
    { topic: selectedTopic === "all" ? undefined : selectedTopic },
    { refetchInterval: 5000 } // Refresh every 5 seconds
  );

  // Fetch recent events
  const { data: events, isLoading: eventsLoading } = trpc.securities.getEvents.useQuery(
    {
      topic: selectedTopic === "all" ? undefined : selectedTopic,
      limit,
      offset: 0,
    },
    { refetchInterval: 5000 }
  );

  if (authLoading) {
    return null;
  }

  if (!user) {
    window.location.href = "/";
    return null;
  }

  const topics = [
    { value: "all", label: "All Topics" },
    { value: "securities.prices", label: "Price Updates" },
    { value: "securities.lifecycle", label: "Lifecycle Events" },
    { value: "securities.corporate_actions", label: "Corporate Actions" },
    { value: "securities.esg", label: "ESG Updates" },
  ];

  const getEventTypeBadge = (eventType: string) => {
    const typeMap: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; label: string }> = {
      "security.price.updated": { variant: "default", label: "Price Update" },
      "security.created": { variant: "secondary", label: "Created" },
      "security.updated": { variant: "outline", label: "Updated" },
      "security.corporate_action": { variant: "destructive", label: "Corporate Action" },
      "security.esg.updated": { variant: "secondary", label: "ESG Update" },
    };

    const config = typeMap[eventType] || { variant: "outline" as const, label: eventType };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const filteredEvents = events?.events.filter((event: any) => {
    if (!searchTicker) return true;
    return event.ticker?.toLowerCase().includes(searchTicker.toLowerCase());
  }) || [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Kafka Event Stream</h1>
          <p className="text-muted-foreground mt-2">
            Real-time monitoring of market data events for RL agent consumption
          </p>
        </div>

        {/* Info Card */}
        <InfoCard title="Event-Sourced Architecture">
          <p>
            Every market data update is captured as an event and stored in the kafka_events table.
            RL agents can consume these events via tRPC API for real-time trading simulations or replay
            historical events for backtesting strategies. Events include price updates, corporate actions,
            and ESG rating changes.
          </p>
        </InfoCard>

        {/* Statistics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statsLoading ? "..." : stats?.totalEvents.toLocaleString() || "0"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Across all topics
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Event Rate</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statsLoading ? "..." : "1.2k"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Events per second
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Topics</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statsLoading ? "..." : Object.keys(stats?.topicBreakdown || {}).length}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Publishing events
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Oldest Event</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statsLoading ? "..." : stats?.oldestEvent ? new Date(stats.oldestEvent).toLocaleDateString() : "N/A"}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Event retention
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Topic Breakdown */}
        {stats?.topicBreakdown && Object.keys(stats.topicBreakdown).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Topic Breakdown</CardTitle>
              <CardDescription>Event distribution across Kafka topics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(stats.topicBreakdown).map(([topic, count]) => (
                  <div key={topic} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{topic}</Badge>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">
                        {((count / stats.totalEvents) * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm font-medium">{count.toLocaleString()} events</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Event Search and Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Event Stream</CardTitle>
            <CardDescription>Search and filter real-time market data events</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by ticker..."
                  value={searchTicker}
                  onChange={(e) => setSearchTicker(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Select value={selectedTopic} onValueChange={setSelectedTopic}>
                <SelectTrigger className="w-[200px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {topics.map((topic) => (
                    <SelectItem key={topic.value} value={topic.value}>
                      {topic.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={limit.toString()} onValueChange={(v) => setLimit(parseInt(v))}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="25">25 events</SelectItem>
                  <SelectItem value="50">50 events</SelectItem>
                  <SelectItem value="100">100 events</SelectItem>
                  <SelectItem value="200">200 events</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Event Table */}
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Ticker</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead className="text-right">Price</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {eventsLoading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        Loading events...
                      </TableCell>
                    </TableRow>
                  ) : filteredEvents.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        No events found
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredEvents.map((event: any, idx: number) => (
                      <TableRow key={idx}>
                        <TableCell className="font-mono text-xs">
                          {formatTimestamp(event.timestamp)}
                        </TableCell>
                        <TableCell>{getEventTypeBadge(event.type)}</TableCell>
                        <TableCell className="font-medium">{event.ticker || "N/A"}</TableCell>
                        <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                          {event.type === "security.price.updated" && event.price
                            ? `${event.price.changePercent >= 0 ? "+" : ""}${event.price.changePercent?.toFixed(2)}%`
                            : event.name || "—"}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {event.type === "security.price.updated" && event.price
                            ? `${event.currency || "$"}${event.price.current?.toFixed(2)}`
                            : "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Pagination Info */}
            {events && (
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>
                  Showing {filteredEvents.length} of {events.totalCount} events
                </span>
                {events.hasMore && (
                  <Button variant="outline" size="sm">
                    Load More
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* API Documentation */}
        <Card>
          <CardHeader>
            <CardTitle>API Endpoints for RL Agents</CardTitle>
            <CardDescription>
              Consume events programmatically via tRPC API
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Streamdown>
{`### Available Endpoints

**Get Events by Topic**
\`\`\`typescript
trpc.securities.getEvents.useQuery({
  topic: "securities.prices",
  fromTimestamp: "2024-01-01T00:00:00Z",
  limit: 100,
  offset: 0
})
\`\`\`

**Get Events by Security ID**
\`\`\`typescript
trpc.securities.getEventsBySecurityId.useQuery({
  securityId: "SEC-AAPL-123456",
  fromTimestamp: "2024-01-01T00:00:00Z",
  limit: 100
})
\`\`\`

**Get Latest Prices (Bulk)**
\`\`\`typescript
trpc.securities.getLatestPrices.useQuery({
  securityIds: ["SEC-AAPL-123", "SEC-MSFT-456"],
  limit: 1
})
\`\`\`

**Get Event Statistics**
\`\`\`typescript
trpc.securities.getEventStats.useQuery({
  topic: "securities.prices" // optional
})
\`\`\`
`}
            </Streamdown>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
