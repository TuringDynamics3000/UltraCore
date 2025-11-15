# UltraCore Operations Portal

**Comprehensive management portal for UltraCore wealth management operations**

The UltraCore Operations Portal is a production-grade web application that provides real-time monitoring and management capabilities for institutional wealth management operations. Built with modern web technologies and event-driven architecture, the portal integrates portfolio management, reinforcement learning agent monitoring, global securities register, ESG data management, and real-time event streaming into a unified operational dashboard.

---

## Architecture Overview

The Operations Portal implements a **three-tier architecture** with event sourcing and data mesh integration, designed for scalability, real-time responsiveness, and ML/RL training data collection.

### Technology Stack

**Frontend**
- React 19 with TypeScript for type-safe component development
- Tailwind CSS 4 for utility-first styling and responsive design
- tRPC 11 for end-to-end type-safe API communication
- Chart.js for financial data visualization and performance charts
- React Joyride for interactive onboarding tours
- Wouter for lightweight client-side routing

**Backend**
- Node.js 22 with Express 4 for API server
- tRPC 11 routers for type-safe procedure definitions
- Drizzle ORM for database schema management and migrations
- MySQL/TiDB for relational data storage
- Superjson for seamless Date and BigInt serialization

**External Integrations**
- Fiscal.ai API for company profiles, financial statements, and market data
- Yahoo Finance API (via Manus Data API Hub) for real-time stock prices and charts
- Manus OAuth for authentication and session management
- S3-compatible storage for file uploads and Parquet datasets

**Data Pipeline**
- Event-sourced architecture with Kafka event publishing
- Time-series price data storage for ML/RL training
- Automatic data enrichment on API calls
- DuckDB WASM for in-browser analytics on Parquet files

---

## Core Modules

The Operations Portal consists of nine integrated modules, each serving a specific operational function within the wealth management platform.

### 1. Dashboard

The central command center provides real-time KPI monitoring and system health status. Key metrics include Total Assets Under Management ($45.2M), Active Portfolios (12), Active Loans (48), and System Health (98.5%). The dashboard features an interactive onboarding tour for new users, InfoCard explainers for portal functionality, and quick navigation to all modules through visual module cards.

### 2. Portfolios

Portfolio management interface for tracking investment holdings, performance metrics, and asset allocations across managed accounts. The module displays portfolio value trends, asset class breakdowns, and individual holding details. Future enhancements will include agent control interfaces for the five RL agents (Alpha, Beta, Gamma, Delta, Epsilon) and portfolio rebalancing functionality.

### 3. Securities

**Dynamic Securities Register** combining static master data with real-time market intelligence. The register contains 454 major US securities across multiple asset classes including equities, cryptocurrencies, artwork, fine wine, and real estate. Each security record includes ISINs, contract addresses, market caps, custody information, and ESG ratings.

**Key Features:**
- Asset class filtering (All, Equities, Crypto, Art, Wine, Real Estate)
- Search by ticker, name, ISIN, or contract address
- Real-time price data from Fiscal.ai and Yahoo Finance APIs
- Security detail pages with asset-specific views
- Blockchain explorer links for crypto assets
- Provenance and auction history for artwork
- Vintage information and ratings for wine
- Property details and valuation history for real estate

**Data Enrichment Pipeline:**
- Automatic persistence of API responses to price_history table
- 5 years of historical OHLCV data for ML/RL training
- Event publishing to Kafka on every price update
- Scheduled daily enrichment jobs for all securities

### 4. ESG Data

Environmental, Social, and Governance metrics management with 85% coverage across the securities universe. The module tracks ESG scores, SFDR/TCFD compliance reports, and Epsilon Agent configuration for ESG-focused portfolio optimization.

### 5. UltraGrow Loans

Loan applications and payment tracking system with $2.4M in active loans. The module monitors Loan-to-Value (LTV) ratios, tracks payment schedules, and integrates with the Zeta Agent for automated loan processing and risk assessment.

### 6. RL Agents

**Reinforcement Learning Agent Monitoring Dashboard** tracking five trading agents: Alpha, Beta, Gamma, Delta, and Epsilon. The module displays training progress, reward curves, portfolio performance metrics, and training job controls. Each agent implements different trading strategies and risk profiles, with real-time performance comparison across agents.

**Agent Capabilities:**
- Training run management (start/pause/reset/export)
- Reward curve visualization with Chart.js
- Episode progress tracking
- Portfolio outcome analysis
- Sharpe ratio and volatility metrics
- Training hyperparameter display

### 7. Kafka Events

**Event Stream Monitoring Dashboard** for real-time market data event consumption. The module displays event statistics (1.2k events/sec), active topics, event timeline visualization, and provides search/filtering capabilities. All price updates from the Securities module automatically publish SecurityPriceUpdated events to the kafka_events table.

**Event Schema:**
- SecurityPriceUpdated: Ticker, price, timestamp, source
- SecurityCreated: New security registration events
- CorporateActionAnnounced: Dividends, splits, mergers

**Consumer API:**
- tRPC endpoints for RL agents to consume events
- Event replay functionality for backtesting
- Time-range filtering for historical analysis
- Audit trail for compliance and debugging

### 8. Data Mesh

**Data Product Catalog and Analytics** with 137 data products including 72 real ASX ETFs. The module integrates DuckDB WASM for in-browser Parquet file queries, enabling SQL-based analytics without server round-trips. Each ETF data product includes ticker, expense ratio, AUM, and historical OHLCV data stored in Parquet format on S3.

**Analytics Capabilities:**
- Interactive SQL query interface
- ETF comparison charts
- Performance analysis (returns, volatility, Sharpe ratio)
- Sector allocation visualization
- Expense ratio comparison

### 9. MCP Tools

Model Context Protocol tools registry with 24 tools for Anya AI integration. The module provides tool execution logs, invocation controls, and monitoring for the Anya AI assistant that supports customer onboarding and portfolio management queries.

---

## User Experience Features

### Interactive Onboarding Tour

First-time users are automatically guided through a 9-step interactive tour covering Dashboard KPIs, module navigation, Securities register, Kafka Events, and RL Agents. The tour uses react-joyride with custom styling matching the portal theme, localStorage persistence to track completion, and a manual "Start Tour" button for returning users.

### Contextual Explainers

The portal includes comprehensive educational elements throughout the interface to improve financial literacy and system understanding:

**InfoTooltip Component:** Hover tooltips explaining financial metrics such as Total AUM, Sharpe Ratio, Volatility, and Max Drawdown. Each tooltip provides concise definitions and context for interpreting the metric.

**InfoCard Component:** Welcome cards and module descriptions that explain functionality and guide users to relevant features. Cards include data source attribution badges showing whether information comes from Fiscal.ai, Yahoo Finance, or internal databases.

**DataSourceBadge Component:** Visual badges indicating the origin of market data, enabling users to understand data provenance and trust the information displayed.

### Responsive Design

The portal implements mobile-first responsive design with Tailwind CSS breakpoints, ensuring usability across desktop, tablet, and mobile devices. The DashboardLayout component features a collapsible sidebar for optimal screen space utilization.

---

## Database Schema

The Operations Portal uses a comprehensive relational schema with 15+ tables covering securities, portfolios, ESG data, loans, RL training metrics, and event streaming.

### Core Tables

**securities** - Global asset register with 454 securities
- Fields: ticker, name, assetClass, assetType, isin, cusip, contractAddress, marketCap, price, exchange, marketType, sector, industry, country, custodian, esgRating, taxLots, insuranceDetails, restrictions, counterpartyRisk, metadata
- Supports: Equities, Crypto, Bonds, ETFs, Art, Wine, Real Estate

**priceHistory** - Time-series price data for ML/RL training
- Fields: securityId, timestamp, open, high, low, close, volume, adjustedClose, source, interval
- 5 years of historical OHLCV data per security
- Automatic population on API calls

**kafkaEvents** - Event sourcing for market data updates
- Fields: topic, eventType, payload, timestamp, source
- Published on every price update
- Consumed by RL agents for training

**portfolios** - Investment portfolio master data
- Fields: name, clientId, totalValue, cashBalance, performance, riskProfile, strategy, status

**holdings** - Portfolio security positions
- Fields: portfolioId, securityId, quantity, averageCost, currentValue, unrealizedGainLoss

**esgData** - Environmental, Social, Governance metrics
- Fields: securityId, esgScore, environmentScore, socialScore, governanceScore, carbonIntensity, sfdrClassification

**loans** - UltraGrow loan applications
- Fields: borrowerId, amount, interestRate, term, status, ltvRatio, collateralValue, paymentSchedule

**trainingRuns** - RL agent training job records
- Fields: agentName, status, startedAt, completedAt, totalEpisodes, finalReward, hyperparameters

**trainingMetrics** - Episode-level training metrics
- Fields: trainingRunId, episode, reward, loss, epsilon, portfolioValue, sharpeRatio

**dataProducts** - Data Mesh catalog
- Fields: productId, name, description, category, schema, parquetPath, owner, quality

---

## API Endpoints

The portal exposes type-safe tRPC procedures for all operations, eliminating the need for manual REST API documentation. All procedures are defined in `server/routers.ts` with automatic TypeScript type inference.

### Authentication

```typescript
trpc.auth.me.useQuery()  // Get current user
trpc.auth.logout.useMutation()  // Logout user
```

### Securities

```typescript
trpc.securities.list.useQuery({ assetClass, search })
trpc.securities.getById.useQuery({ id })
trpc.securities.fiscalProfile.useQuery({ ticker })
trpc.securities.yahooChart.useQuery({ ticker, interval, range })
trpc.securities.priceHistory.useQuery({ securityId, startDate, endDate })
```

### Kafka Events

```typescript
trpc.securities.kafkaEvents.useQuery({ topic, eventType, limit })
trpc.securities.kafkaStats.useQuery()
trpc.securities.kafkaReplay.useMutation({ startTime, endTime })
```

### Portfolios

```typescript
trpc.portfolios.list.useQuery()
trpc.portfolios.getById.useQuery({ id })
trpc.portfolios.holdings.useQuery({ portfolioId })
```

### RL Agents

```typescript
trpc.agents.list.useQuery()
trpc.agents.getById.useQuery({ id })
trpc.agents.trainingRuns.useQuery({ agentName })
trpc.agents.startTraining.useMutation({ agentName, hyperparameters })
```

---

## Setup Instructions

### Prerequisites

- Node.js 22.13.0 or later
- pnpm 10.4.1 or later
- MySQL or TiDB database instance
- Fiscal.ai API key (optional, for market data enrichment)

### Installation

```bash
# Clone the repository
git clone https://github.com/TuringDynamics3000/UltraCore.git
cd UltraCore/operations-portal

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials and API keys

# Run database migrations
pnpm db:push

# Seed the database with sample data
pnpm tsx scripts/seed-securities-register.ts

# Start the development server
pnpm dev
```

The portal will be available at `http://localhost:3001`.

### Environment Variables

```env
DATABASE_URL=mysql://user:password@host:port/database
JWT_SECRET=your-jwt-secret
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://login.manus.im
FISCAL_AI_API_KEY=your-fiscal-ai-key (optional)
```

### Database Migration

The portal uses Drizzle ORM for schema management. To apply migrations:

```bash
# Generate migration files
pnpm drizzle-kit generate

# Apply migrations to database
pnpm db:push
```

### Seeding Data

The portal includes seed scripts for populating initial data:

```bash
# Seed 454 securities with real market data
pnpm tsx scripts/import-from-ticker-list.ts

# Seed 72 ASX ETFs for Data Mesh
pnpm tsx scripts/seed-data-products.ts
```

---

## Deployment

### Production Build

```bash
# Build frontend and backend
pnpm build

# Start production server
pnpm start
```

### Docker Deployment

```bash
# Build Docker image
docker build -t ultracore-operations-portal .

# Run container
docker run -p 3001:3001 \
  -e DATABASE_URL=mysql://... \
  -e JWT_SECRET=... \
  ultracore-operations-portal
```

### Environment Configuration

For production deployment, ensure the following environment variables are configured:

- `DATABASE_URL` - Production database connection string
- `JWT_SECRET` - Secure random string for session signing
- `OAUTH_SERVER_URL` - Manus OAuth backend URL
- `VITE_OAUTH_PORTAL_URL` - Manus login portal URL
- `FISCAL_AI_API_KEY` - Fiscal.ai API key for market data
- `NODE_ENV=production` - Enable production optimizations

---

## Development Workflow

### Project Structure

```
operations-portal/
├── client/                 # Frontend React application
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # tRPC client and utilities
│   │   ├── App.tsx        # Routes and layout
│   │   └── main.tsx       # Application entry point
│   └── index.html         # HTML template
├── server/                # Backend Express + tRPC server
│   ├── _core/             # Framework plumbing (OAuth, context)
│   ├── db.ts              # Database query helpers
│   ├── routers.ts         # tRPC procedure definitions
│   ├── fiscal-ai.ts       # Fiscal.ai API client
│   ├── enrichment.ts      # Data enrichment service
│   ├── kafka-publisher.ts # Kafka event publisher
│   └── kafka-consumer.ts  # Kafka event consumer
├── drizzle/               # Database schema and migrations
│   └── schema.ts          # Drizzle ORM schema definitions
├── scripts/               # Utility scripts
│   ├── seed-securities-register.ts
│   ├── import-from-ticker-list.ts
│   └── discover-and-import-securities.ts
├── shared/                # Shared types and constants
└── storage/               # S3 storage helpers
```

### Adding New Features

**1. Define Database Schema** in `drizzle/schema.ts`:

```typescript
export const newTable = mysqlTable("new_table", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});
```

**2. Create Database Helpers** in `server/db.ts`:

```typescript
export async function getNewItems() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(newTable);
}
```

**3. Add tRPC Procedures** in `server/routers.ts`:

```typescript
newFeature: router({
  list: publicProcedure.query(async () => {
    return await getNewItems();
  }),
}),
```

**4. Create Frontend Page** in `client/src/pages/NewFeature.tsx`:

```typescript
export default function NewFeature() {
  const { data, isLoading } = trpc.newFeature.list.useQuery();
  // Render UI
}
```

**5. Add Route** in `client/src/App.tsx`:

```typescript
<Route path="/new-feature" component={NewFeature} />
```

### Testing

```bash
# Run TypeScript type checking
pnpm tsc --noEmit

# Run linting
pnpm eslint .

# Run tests (when implemented)
pnpm test
```

---

## Future Enhancements

### Planned Features

**UltraWealth Account Creation Integration** - Customer onboarding flow with KYC, risk profiling, MDA contract signing, Statement of Advice generation, and portfolio creation wizard. Integration with the 12 ASX ETF universe and glide path strategies (first home, retirement, wealth accumulation).

**WebSocket Real-Time Streaming** - Socket.io integration for pushing live price updates to connected clients, enabling sub-second latency for high-frequency trading simulations and real-time dashboard updates.

**RL Training Metrics Dashboard** - Enhanced visualization of training progress with reward curves, episode statistics, hyperparameter tuning history, and portfolio outcome analysis across all five agents.

**Data Mesh SQL Query Interface** - Interactive SQL editor with syntax highlighting for power users to query Parquet files directly in the browser using DuckDB WASM, with result export to CSV/JSON.

**Explainable AI Interface** - Visualization of RL agent decision-making process, showing which features influenced trading decisions and portfolio allocations at each timestep.

**Compliance Reporting** - Automated generation of regulatory reports including ASIC compliance, AFSL requirements, SOA tracking, and best interests duty documentation.

---

## Contributing

The UltraCore Operations Portal is an internal tool for TuringDynamics3000. For questions or feature requests, contact the development team.

---

## License

Proprietary - All rights reserved by TuringDynamics3000

---

## Acknowledgments

Built with modern web technologies and best practices for institutional wealth management operations. Special thanks to the Manus platform for providing authentication, data APIs, and deployment infrastructure.

---

**Version:** 1.0.0  
**Last Updated:** November 16, 2025  
**Maintained by:** TuringDynamics3000 Development Team
