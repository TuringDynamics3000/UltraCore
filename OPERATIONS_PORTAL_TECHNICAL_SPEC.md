# UltraCore Operations Portal - Technical Specification

**Framework:** Shadcn Admin Kit (React Admin + Shadcn UI)  
**Architecture:** Event Sourcing + Data Mesh + Agentic AI + MCP + RL/ML  
**Author:** Manus AI  
**Date:** November 2025

---

## Executive Summary

This document provides the complete technical specification for implementing the **UltraCore Operations Portal** using **Shadcn Admin Kit**. The portal leverages React Admin's proven framework with Shadcn UI's modern design system, custom data providers for Kafka event sourcing and Data Mesh, and built-in MCP server integration for agentic AI operations.

**Technology Decision:** Shadcn Admin Kit was selected over Material UI React Admin for its modern aesthetic, superior performance, built-in MCP support, and direct component customization capabilities—all critical for a professional financial operations portal.

---

## Project Structure

```
ultracore-operations-portal/
├── public/
│   ├── favicon.ico
│   └── ultracore-logo.svg
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   ├── components/
│   │   ├── admin/           # Shadcn Admin Kit components
│   │   ├── ui/              # Shadcn UI primitives
│   │   ├── charts/          # Custom chart components
│   │   └── custom/          # UltraCore-specific components
│   ├── dataProviders/
│   │   ├── kafkaDataProvider.ts
│   │   ├── dataMeshDataProvider.ts
│   │   ├── postgresDataProvider.ts
│   │   ├── mcpDataProvider.ts
│   │   └── rlMetricsDataProvider.ts
│   ├── authProvider/
│   │   └── ultraCoreAuthProvider.ts
│   ├── realtime/
│   │   └── kafkaSubscription.ts
│   ├── modules/
│   │   ├── portfolios/
│   │   │   ├── PortfolioList.tsx
│   │   │   ├── PortfolioDetail.tsx
│   │   │   ├── PortfolioDashboard.tsx
│   │   │   └── AgentControl.tsx
│   │   ├── esg/
│   │   │   ├── EsgDataManager.tsx
│   │   │   ├── EpsilonConfig.tsx
│   │   │   └── EsgReporting.tsx
│   │   ├── loans/
│   │   │   ├── LoanList.tsx
│   │   │   ├── LoanDetail.tsx
│   │   │   ├── LtvMonitor.tsx
│   │   │   └── ZetaAgentDashboard.tsx
│   │   ├── users/
│   │   │   ├── UserList.tsx
│   │   │   ├── UserEdit.tsx
│   │   │   └── RbacManager.tsx
│   │   ├── rl-agents/
│   │   │   ├── TrainingDashboard.tsx
│   │   │   ├── AgentPerformance.tsx
│   │   │   ├── ExplainableAI.tsx
│   │   │   └── ModelManagement.tsx
│   │   ├── kafka/
│   │   │   ├── EventStreamViewer.tsx
│   │   │   ├── TopicMonitor.tsx
│   │   │   └── EventReplay.tsx
│   │   ├── data-mesh/
│   │   │   ├── ProductCatalog.tsx
│   │   │   ├── DataQuality.tsx
│   │   │   └── LineageViewer.tsx
│   │   └── mcp/
│   │       ├── ToolRegistry.tsx
│   │       ├── ToolExecution.tsx
│   │       └── AnyaMonitor.tsx
│   ├── lib/
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── types/
│   │   ├── portfolio.ts
│   │   ├── loan.ts
│   │   ├── agent.ts
│   │   └── event.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── websocket-server/
│   ├── index.ts
│   ├── kafkaConsumer.ts
│   └── socketManager.ts
├── mcp-server/
│   ├── index.ts
│   ├── tools/
│   │   ├── portfolio-tools.ts
│   │   ├── loan-tools.ts
│   │   └── agent-tools.ts
│   └── server.ts
├── .env.example
├── .env.local
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
├── package.json
└── README.md
```

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI framework |
| **Shadcn Admin Kit** | Latest | Admin framework |
| **Shadcn UI** | Latest | Component library |
| **Tailwind CSS** | 3.4.0 | Styling |
| **Radix UI** | Latest | Accessible primitives |
| **TypeScript** | 5.3.0 | Type safety |
| **Vite** | 5.0.0 | Build tool |
| **TanStack Query** | 5.0.0 | Data fetching |
| **React Hook Form** | 7.49.0 | Form management |
| **Recharts** | 2.10.0 | Charts |
| **Socket.io Client** | 4.6.0 | WebSockets |
| **DuckDB WASM** | 1.28.0 | In-browser analytics |

### Backend Services

| Technology | Version | Purpose |
|------------|---------|---------|
| **Node.js** | 18.x | Runtime |
| **Express** | 4.18.0 | REST API |
| **Socket.io** | 4.6.0 | WebSocket server |
| **KafkaJS** | 2.2.4 | Kafka client |
| **Postgres.js** | 3.4.0 | PostgreSQL client |
| **@modelcontextprotocol/sdk** | Latest | MCP server |

### Infrastructure

| Service | Purpose |
|---------|---------|
| **AWS S3** | Static hosting |
| **AWS CloudFront** | CDN |
| **AWS EKS** | Kubernetes |
| **AWS MSK** | Managed Kafka |
| **AWS RDS** | PostgreSQL |
| **AWS Glue** | Data catalog |

---

## Installation & Setup

### Prerequisites

```bash
# Required software
node >= 18.0.0
npm >= 9.0.0
docker >= 24.0.0
kubectl >= 1.28.0
```

### Initial Setup

```bash
# 1. Create project
npx create-react-admin@latest ultracore-operations-portal --ui shadcn

# 2. Navigate to project
cd ultracore-operations-portal

# 3. Install additional dependencies
npm install kafkajs socket.io-client @duckdb/duckdb-wasm recharts

# 4. Install Shadcn UI components
npx shadcn-ui@latest add card
npx shadcn-ui@latest add chart
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add alert

# 5. Configure environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# 6. Start development server
npm run dev
```

### Environment Variables

```bash
# .env.local

# API Endpoints
VITE_API_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3001
VITE_MCP_URL=http://localhost:3002

# Kafka
VITE_KAFKA_BROKERS=localhost:9092

# Data Mesh
VITE_S3_BUCKET=ultracore-data-mesh
VITE_S3_REGION=us-east-1

# PostgreSQL
VITE_DB_HOST=localhost
VITE_DB_PORT=5432
VITE_DB_NAME=ultracore
VITE_DB_USER=ultracore_admin
VITE_DB_PASSWORD=<secret>

# Authentication
VITE_AUTH_DOMAIN=auth.ultracore.com
VITE_AUTH_CLIENT_ID=<client_id>

# Feature Flags
VITE_ENABLE_DARK_MODE=true
VITE_ENABLE_MCP_SERVER=true
VITE_ENABLE_REALTIME=true
```

---

## Core Implementation

### 1. Main Application (App.tsx)

```typescript
// src/App.tsx

import { Admin, Resource, CustomRoutes } from 'react-admin';
import { Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme-provider';

// Data Providers
import { kafkaDataProvider } from './dataProviders/kafkaDataProvider';
import { dataMeshDataProvider } from './dataProviders/dataMeshDataProvider';
import { postgresDataProvider } from './dataProviders/postgresDataProvider';
import { mcpDataProvider } from './dataProviders/mcpDataProvider';
import { rlMetricsDataProvider } from './dataProviders/rlMetricsDataProvider';

// Auth Provider
import { ultraCoreAuthProvider } from './authProvider/ultraCoreAuthProvider';

// Real-time
import { addRealtimeToDataProvider } from './realtime/kafkaSubscription';

// Modules
import { PortfolioList, PortfolioDetail, PortfolioDashboard } from './modules/portfolios';
import { EsgDataManager, EpsilonConfig, EsgReporting } from './modules/esg';
import { LoanList, LoanDetail, LtvMonitor } from './modules/loans';
import { UserList, UserEdit, RbacManager } from './modules/users';
import { TrainingDashboard, AgentPerformance } from './modules/rl-agents';
import { EventStreamViewer, TopicMonitor } from './modules/kafka';
import { ProductCatalog, DataQuality } from './modules/data-mesh';
import { ToolRegistry, AnyaMonitor } from './modules/mcp';

// Layout
import { AppSidebar } from './components/admin/app-sidebar';

// Combine data providers
const dataProvider = {
  'portfolios': postgresDataProvider,
  'portfolio-events': kafkaDataProvider,
  'portfolio-valuations': dataMeshDataProvider,
  'loans': postgresDataProvider,
  'loan-events': kafkaDataProvider,
  'users': postgresDataProvider,
  'rl-training': rlMetricsDataProvider,
  'kafka-events': kafkaDataProvider,
  'data-products': dataMeshDataProvider,
  'mcp-tools': mcpDataProvider,
};

// Add real-time updates
const realtimeDataProvider = addRealtimeToDataProvider(
  dataProvider,
  import.meta.env.VITE_WS_URL
);

export const App = () => (
  <ThemeProvider defaultTheme="system" storageKey="ultracore-theme">
    <Admin
      dataProvider={realtimeDataProvider}
      authProvider={ultraCoreAuthProvider}
      sidebar={AppSidebar}
      dashboard={PortfolioDashboard}
      title="UltraCore Operations"
    >
      {/* Portfolio Management */}
      <Resource
        name="portfolios"
        list={PortfolioList}
        show={PortfolioDetail}
        options={{ label: 'Portfolios' }}
      />

      {/* ESG Management */}
      <Resource
        name="esg-data"
        list={EsgDataManager}
        options={{ label: 'ESG Data' }}
      />

      {/* UltraGrow Loans */}
      <Resource
        name="loans"
        list={LoanList}
        show={LoanDetail}
        options={{ label: 'Loans' }}
      />

      {/* User Management */}
      <Resource
        name="users"
        list={UserList}
        edit={UserEdit}
        options={{ label: 'Users' }}
      />

      {/* RL Agents */}
      <Resource
        name="rl-training"
        list={TrainingDashboard}
        options={{ label: 'RL Agents' }}
      />

      {/* Kafka Events */}
      <Resource
        name="kafka-events"
        list={EventStreamViewer}
        options={{ label: 'Events' }}
      />

      {/* Data Mesh */}
      <Resource
        name="data-products"
        list={ProductCatalog}
        options={{ label: 'Data Products' }}
      />

      {/* MCP Tools */}
      <Resource
        name="mcp-tools"
        list={ToolRegistry}
        options={{ label: 'MCP Tools' }}
      />

      {/* Custom Routes */}
      <CustomRoutes>
        <Route path="/esg/epsilon-config" element={<EpsilonConfig />} />
        <Route path="/esg/reporting" element={<EsgReporting />} />
        <Route path="/loans/ltv-monitor" element={<LtvMonitor />} />
        <Route path="/users/rbac" element={<RbacManager />} />
        <Route path="/rl-agents/performance" element={<AgentPerformance />} />
        <Route path="/kafka/topics" element={<TopicMonitor />} />
        <Route path="/data-mesh/quality" element={<DataQuality />} />
        <Route path="/mcp/anya" element={<AnyaMonitor />} />
      </CustomRoutes>
    </Admin>
  </ThemeProvider>
);
```

---

### 2. Tailwind Configuration (tailwind.config.js)

```javascript
// tailwind.config.js

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // UltraCore brand colors
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          900: '#0c4a6e',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
          500: '#10b981',
          600: '#059669',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // Financial metrics colors
        positive: '#10b981',
        negative: '#ef4444',
        neutral: '#6b7280',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

---

### 3. Portfolio Dashboard Example

```typescript
// src/modules/portfolios/PortfolioDashboard.tsx

import { useGetList } from 'react-admin';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const PortfolioDashboard = () => {
  const { data: portfolios, isLoading } = useGetList('portfolios', {
    pagination: { page: 1, perPage: 100 },
  });

  const { data: metrics } = useGetList('portfolio-valuations', {
    filter: { period: 'last_30_days' },
  });

  if (isLoading) return <div>Loading...</div>;

  const totalAUM = portfolios?.reduce((sum, p) => sum + p.value, 0) || 0;
  const avgReturn = portfolios?.reduce((sum, p) => sum + p.return_30d, 0) / (portfolios?.length || 1);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Portfolio Dashboard</h1>
        <p className="text-muted-foreground">Real-time portfolio monitoring and management</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total AUM</CardTitle>
            <svg className="h-4 w-4 text-muted-foreground" /* ... */ />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${(totalAUM / 1000000).toFixed(2)}M</div>
            <p className="text-xs text-positive">+5.2% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">30-Day Return</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgReturn.toFixed(2)}%</div>
            <p className="text-xs text-muted-foreground">Avg across all portfolios</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Portfolios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portfolios?.length || 0}</div>
            <p className="text-xs text-muted-foreground">Across 5 RL agents</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Sharpe Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.85</div>
            <p className="text-xs text-positive">Excellent risk-adjusted returns</p>
          </CardContent>
        </Card>
      </div>

      {/* Agent Performance */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All Agents</TabsTrigger>
          <TabsTrigger value="alpha">Alpha (Preservation)</TabsTrigger>
          <TabsTrigger value="beta">Beta (Income)</TabsTrigger>
          <TabsTrigger value="gamma">Gamma (Growth)</TabsTrigger>
          <TabsTrigger value="delta">Delta (Aggressive)</TabsTrigger>
          <TabsTrigger value="epsilon">Epsilon (ESG)</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Performance (30 Days)</CardTitle>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Portfolio List */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Portfolios</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {portfolios?.slice(0, 10).map((portfolio) => (
                  <div key={portfolio.id} className="flex items-center justify-between border-b pb-4">
                    <div className="space-y-1">
                      <p className="font-medium">{portfolio.investor_name}</p>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{portfolio.agent}</Badge>
                        <span className="text-sm text-muted-foreground">
                          ${(portfolio.value / 1000).toFixed(1)}K
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${portfolio.return_30d >= 0 ? 'text-positive' : 'text-negative'}`}>
                        {portfolio.return_30d >= 0 ? '+' : ''}{portfolio.return_30d.toFixed(2)}%
                      </p>
                      <p className="text-sm text-muted-foreground">30-day return</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
```

---

## Data Provider Implementations

### Kafka Data Provider

```typescript
// src/dataProviders/kafkaDataProvider.ts

import { DataProvider } from 'react-admin';
import { Kafka, Consumer, Producer } from 'kafkajs';

export const kafkaDataProvider = (
  kafkaConfig: { brokers: string[] }
): DataProvider => {
  const kafka = new Kafka(kafkaConfig);
  const consumer = kafka.consumer({ groupId: 'operations-portal' });
  const producer = kafka.producer();

  const eventCache = new Map<string, any[]>();

  const subscribeToTopics = async (topics: string[]) => {
    await consumer.connect();
    await consumer.subscribe({ topics, fromBeginning: false });
    
    await consumer.run({
      eachMessage: async ({ topic, message }) => {
        const event = JSON.parse(message.value!.toString());
        if (!eventCache.has(topic)) {
          eventCache.set(topic, []);
        }
        eventCache.get(topic)!.push({
          ...event,
          id: `${topic}-${message.offset}`,
          timestamp: message.timestamp,
        });
      },
    });
  };

  return {
    getList: async (resource, params) => {
      const events = eventCache.get(resource) || [];
      
      let filtered = events;
      if (params.filter) {
        filtered = events.filter(event => 
          Object.entries(params.filter).every(([key, value]) => 
            event[key] === value
          )
        );
      }
      
      const { page, perPage } = params.pagination;
      const start = (page - 1) * perPage;
      const end = start + perPage;
      
      return {
        data: filtered.slice(start, end),
        total: filtered.length,
      };
    },

    getOne: async (resource, params) => {
      const events = eventCache.get(resource) || [];
      const event = events.find(e => e.id === params.id);
      if (!event) throw new Error('Event not found');
      return { data: event };
    },

    create: async (resource, params) => {
      await producer.connect();
      await producer.send({
        topic: resource,
        messages: [{ value: JSON.stringify(params.data) }],
      });
      return { data: { ...params.data, id: Date.now() } };
    },

    getMany: async (resource, params) => {
      const events = eventCache.get(resource) || [];
      const data = events.filter(e => params.ids.includes(e.id));
      return { data };
    },

    getManyReference: async (resource, params) => {
      const events = eventCache.get(resource) || [];
      const filtered = events.filter(e => e[params.target] === params.id);
      return { data: filtered, total: filtered.length };
    },

    update: async () => {
      throw new Error('Kafka events are immutable');
    },

    updateMany: async () => {
      throw new Error('Kafka events are immutable');
    },

    delete: async () => {
      throw new Error('Kafka events are immutable');
    },

    deleteMany: async () => {
      throw new Error('Kafka events are immutable');
    },
  };
};
```

---

## WebSocket Server for Real-Time Updates

```typescript
// websocket-server/index.ts

import { Server } from 'socket.io';
import { Kafka } from 'kafkajs';

const io = new Server(3001, {
  cors: { origin: '*' },
});

const kafka = new Kafka({
  brokers: process.env.KAFKA_BROKERS?.split(',') || ['localhost:9092'],
});

io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  
  const consumers = new Map<string, any>();

  socket.on('subscribe', async (topic: string) => {
    if (consumers.has(topic)) return;

    const consumer = kafka.consumer({ groupId: `ws-${socket.id}` });
    await consumer.connect();
    await consumer.subscribe({ topic, fromBeginning: false });

    await consumer.run({
      eachMessage: async ({ topic, message }) => {
        const event = JSON.parse(message.value!.toString());
        socket.emit('event', {
          topic,
          event: {
            ...event,
            id: `${topic}-${message.offset}`,
            timestamp: message.timestamp,
          },
        });
      },
    });

    consumers.set(topic, consumer);
    console.log(`Subscribed to topic: ${topic}`);
  });

  socket.on('unsubscribe', async (topic: string) => {
    const consumer = consumers.get(topic);
    if (consumer) {
      await consumer.disconnect();
      consumers.delete(topic);
      console.log(`Unsubscribed from topic: ${topic}`);
    }
  });

  socket.on('disconnect', async () => {
    console.log(`Client disconnected: ${socket.id}`);
    for (const consumer of consumers.values()) {
      await consumer.disconnect();
    }
  });
});

console.log('WebSocket server listening on port 3001');
```

---

## MCP Server Integration

```typescript
// mcp-server/index.ts

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// Import tool implementations
import { portfolioTools } from './tools/portfolio-tools.js';
import { loanTools } from './tools/loan-tools.js';
import { agentTools } from './tools/agent-tools.js';

const server = new Server(
  {
    name: 'ultracore-operations-portal',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register all tools
const allTools = [
  ...portfolioTools,
  ...loanTools,
  ...agentTools,
];

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: allTools.map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema,
    })),
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const tool = allTools.find(t => t.name === request.params.name);
  
  if (!tool) {
    throw new Error(`Tool not found: ${request.params.name}`);
  }

  const result = await tool.execute(request.params.arguments);
  
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP server running on stdio');
}

main().catch(console.error);
```

---

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile

FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ultracore-operations-portal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: operations-portal
  template:
    metadata:
      labels:
        app: operations-portal
    spec:
      containers:
      - name: portal
        image: ultracore/operations-portal:latest
        ports:
        - containerPort: 80
        env:
        - name: VITE_API_URL
          valueFrom:
            configMapKeyRef:
              name: portal-config
              key: api-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## Testing Strategy

### Unit Tests

```typescript
// src/modules/portfolios/__tests__/PortfolioDashboard.test.tsx

import { render, screen } from '@testing-library/react';
import { AdminContext } from 'react-admin';
import { PortfolioDashboard } from '../PortfolioDashboard';

describe('PortfolioDashboard', () => {
  it('renders KPI cards', () => {
    render(
      <AdminContext>
        <PortfolioDashboard />
      </AdminContext>
    );
    
    expect(screen.getByText('Total AUM')).toBeInTheDocument();
    expect(screen.getByText('30-Day Return')).toBeInTheDocument();
    expect(screen.getByText('Active Portfolios')).toBeInTheDocument();
  });
});
```

### Integration Tests

```typescript
// src/__tests__/integration/kafka-realtime.test.ts

import { kafkaDataProvider } from '@/dataProviders/kafkaDataProvider';
import { Kafka } from 'kafkajs';

describe('Kafka Real-Time Integration', () => {
  it('receives events in real-time', async () => {
    const kafka = new Kafka({ brokers: ['localhost:9092'] });
    const producer = kafka.producer();
    await producer.connect();

    const dataProvider = kafkaDataProvider({ brokers: ['localhost:9092'] });
    
    // Publish event
    await producer.send({
      topic: 'portfolio-events',
      messages: [{ value: JSON.stringify({ type: 'rebalanced' }) }],
    });

    // Wait for event to be received
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Query events
    const result = await dataProvider.getList('portfolio-events', {
      pagination: { page: 1, perPage: 10 },
      sort: { field: 'id', order: 'DESC' },
      filter: {},
    });

    expect(result.data.length).toBeGreaterThan(0);
    expect(result.data[0].type).toBe('rebalanced');
  });
});
```

---

## Performance Optimization

### Code Splitting

```typescript
// src/App.tsx

import { lazy, Suspense } from 'react';

// Lazy load modules
const PortfolioDashboard = lazy(() => import('./modules/portfolios/PortfolioDashboard'));
const EsgDataManager = lazy(() => import('./modules/esg/EsgDataManager'));
const LoanList = lazy(() => import('./modules/loans/LoanList'));

// Wrap in Suspense
<Suspense fallback={<div>Loading...</div>}>
  <PortfolioDashboard />
</Suspense>
```

### Caching Strategy

```typescript
// src/lib/queryClient.ts

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 3,
    },
  },
});
```

---

## Security

### Content Security Policy

```html
<!-- public/index.html -->

<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' wss://ultracore.com https://api.ultracore.com;
  font-src 'self';
">
```

### Authentication Flow

```typescript
// src/authProvider/ultraCoreAuthProvider.ts

import { AuthProvider } from 'react-admin';

export const ultraCoreAuthProvider: AuthProvider = {
  login: async ({ username, password }) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const { token, user } = await response.json();
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      return Promise.resolve();
    }

    return Promise.reject(new Error('Invalid credentials'));
  },

  logout: async () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return Promise.resolve();
  },

  checkAuth: async () => {
    const token = localStorage.getItem('token');
    return token ? Promise.resolve() : Promise.reject();
  },

  checkError: async (error) => {
    if (error.status === 401 || error.status === 403) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return Promise.reject();
    }
    return Promise.resolve();
  },

  getPermissions: async () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return Promise.resolve(user.permissions || []);
  },

  getIdentity: async () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return Promise.resolve({
      id: user.id,
      fullName: user.fullName,
      avatar: user.avatar,
    });
  },
};
```

---

## Monitoring & Observability

### Error Tracking

```typescript
// src/lib/errorTracking.ts

import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});

export const captureError = (error: Error, context?: any) => {
  Sentry.captureException(error, { extra: context });
};
```

### Analytics

```typescript
// src/lib/analytics.ts

import { analytics } from '@segment/analytics-next';

export const trackEvent = (event: string, properties?: any) => {
  analytics.track(event, properties);
};

export const trackPageView = (page: string) => {
  analytics.page(page);
};
```

---

## Conclusion

This technical specification provides a complete blueprint for implementing the UltraCore Operations Portal using Shadcn Admin Kit. The portal leverages modern web technologies, custom data providers for Kafka and Data Mesh, built-in MCP server integration, and a contemporary design system to create a production-grade operations center.

**Next Steps:**
1. Review this specification with the development team
2. Set up development environment
3. Implement core modules (portfolios, ESG, loans)
4. Deploy to staging for testing
5. Launch to production

**Status:** Ready for implementation.
