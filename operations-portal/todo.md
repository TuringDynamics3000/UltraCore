# UltraCore Operations Portal - TODO

## Phase 1: Foundation & Setup
- [x] Fix dev server file watch issue
- [ ] Set up Supabase client and authentication
- [x] Configure PostgreSQL database schema
- [x] Create DashboardLayout component with sidebar navigation
- [x] Set up tRPC routers for all modules
- [ ] Configure Tailwind theme with UltraCore branding
- [ ] Add environment variables for Supabase

## Phase 2: Portfolio Management Module
- [x] Create portfolio database schema
- [x] Build Portfolio Dashboard with KPI cards
- [x] Implement Portfolio List view
- [x] Build Portfolio Detail page with holdings and performance charts
- [ ] Add Agent Control interface (Alpha, Beta, Gamma, Delta, Epsilon)
- [ ] Implement portfolio rebalancing functionality
- [ ] Add real-time portfolio value updates

## Phase 3: ESG Management Module
- [x] Create ESG data schema
- [ ] Build ESG Data Manager interface
- [ ] Implement Epsilon Agent configuration
- [ ] Create ESG reporting dashboard
- [ ] Add SFDR/TCFD compliance reports
- [ ] Implement ESG scoring visualization

## Phase 4: UltraGrow Loans Module
- [x] Create loan database schema
- [ ] Build Loan List view
- [ ] Implement Loan Detail page
- [ ] Create LTV Monitor dashboard
- [ ] Build Zeta Agent dashboard
- [ ] Add loan approval workflow
- [ ] Implement payment tracking

## Phase 5: User Management
- [ ] Implement Supabase authentication
- [ ] Create user profile management
- [ ] Build RBAC (Role-Based Access Control) system
- [ ] Add user permissions management
- [ ] Implement audit logging

## Phase 6: Kafka Event Streaming
- [ ] Set up Kafka client integration
- [ ] Build Event Stream Viewer
- [ ] Create Topic Monitor dashboard
- [ ] Implement event replay functionality
- [ ] Add event filtering and search

## Phase 7: RL Agent Monitoring
- [x] Create RL metrics schema
- [x] Build Training Dashboard with 5 agents (Alpha, Beta, Gamma, Delta, Epsilon)
- [x] Implement Agent Performance charts with Chart.js
- [x] Create Agent Detail pages with training metrics
- [x] Add training job controls (start/pause/reset/export)
- [ ] Add Explainable AI interface
- [ ] Create Model Management interface

## Phase 8: Data Mesh Integration
- [x] Set up DuckDB WASM client
- [x] Build Data Product Catalog with 72 real ASX ETFs
- [x] Import UltraCore ETF data with Parquet file references
- [x] Add data product search and filtering
- [ ] Integrate DuckDB WASM for in-browser Parquet queries
- [ ] Implement Data Quality dashboard
- [ ] Create Data Lineage Viewer

## Phase 9: MCP Server & Tools
- [ ] Set up MCP server
- [ ] Build Tool Registry interface
- [ ] Implement Tool Execution logs
- [ ] Create Anya AI Monitor
- [ ] Add tool invocation controls

## Phase 10: Real-Time Features
- [ ] Implement WebSocket server
- [ ] Add Supabase real-time subscriptions
- [ ] Create live dashboard updates
- [ ] Add notification system
- [ ] Implement activity feed

## Phase 11: Testing & Quality
- [ ] Write unit tests for tRPC procedures
- [ ] Add integration tests for auth flow
- [ ] Test real-time subscriptions
- [ ] Add E2E tests for critical flows
- [ ] Performance testing and optimization

## Phase 12: Deployment
- [ ] Configure production environment
- [ ] Set up CI/CD pipeline
- [ ] Deploy to staging
- [ ] Production deployment
- [ ] Monitoring and alerting setup

## Current Sprint: RL Agent Monitoring Module
- [x] Build RL Agents list page with agent cards
- [x] Create Agent Detail page with training metrics
- [x] Add performance charts for agent training history
- [x] Implement agent control interface (start/stop/retrain)
- [x] Add training job management dashboard

## Current Sprint: Data Mesh Analytics Module
- [x] Install DuckDB WASM dependencies
- [x] Create ETF catalog page with 72 real ASX ETF products from UltraCore
- [x] Import real UltraCore ETF data with tickers, expense ratios, and AUM
- [x] Update schema to add ETF-specific fields (ticker, expenseRatio, aum)
- [x] Add search and filter functionality
- [x] Display ETF cards with ticker badges, expense ratios, and AUM values
- [x] Integrate DuckDB WASM to load and query Parquet files in browser
- [ ] Build analytics dashboard with ETF comparison charts
- [ ] Add interactive charts for performance/sector/expense analysis
- [ ] Implement SQL query interface for power users

## Current Sprint: DuckDB WASM Integration
- [x] Initialize DuckDB WASM in browser on button click
- [x] Load Parquet files from S3 (72 ETFs uploaded to production storage)
- [x] Fetch and register Parquet files as ArrayBuffers in DuckDB WASM
- [x] Query OHLCV data with SQL (tested with VTS - 100 rows loaded successfully)
- [x] Display query results in data table with pagination
- [x] Add explainer toasts and user guidance throughout the flow
- [x] Implement error handling for failed Parquet loads
- [ ] Create SQL query interface with syntax highlighting
- [ ] Build ETF comparison analytics dashboard
- [ ] Add performance charts (price history, returns, volatility)
- [ ] Implement sector allocation visualization
- [ ] Add expense ratio comparison charts

## Current Sprint: Securities Register UI
- [x] Design Kafka event schema (SecurityCreated, PriceUpdated, CorporateActionAnnounced)
- [x] Create comprehensive Global Asset Register schema (15 tables, 50+ fields)
- [x] Add support for all asset classes (equities, ETFs, bonds, crypto, alternatives)
- [x] Seed register with 63 real securities (28 US stocks, 15 ASX stocks, 15 crypto, 5 alternatives)
- [x] Include real ISINs, contract addresses, market caps, and metadata
- [x] Build Securities List page with asset class filters and search
- [x] Add tRPC routers for securities queries
- [ ] Create Security Detail page with asset-specific views
- [ ] Implement asset-specific detail views (equities, crypto, art, wine, real estate)
- [ ] Add navigation to Securities Register from dashboard
- [ ] Implement Zeta Agent for OpenFIGI API data enrichment
- [ ] Integrate with Data Mesh (securities as data products)
- [ ] Add MCP interface for Anya AI natural language queries

## Current Sprint: Security Detail Pages
- [ ] Research Fiscal.ai API for financial market data integration
- [ ] Design Security Detail page layout with asset-specific sections
- [ ] Create tRPC endpoint for fetching security details with related data
- [ ] Build SecurityDetail.tsx component with routing
- [ ] Implement equity-specific view with price charts (Chart.js + Fiscal.ai data)
- [ ] Add financial metrics display (P/E ratio, dividend yield, 52-week high/low)
- [ ] Create crypto-specific view with blockchain explorer links (Etherscan, Blockchain.com)
- [ ] Add wallet address display and contract information
- [ ] Build artwork detail view with images, provenance, auction history
- [ ] Create wine detail view with vintage info, ratings, storage location
- [ ] Add real estate detail view with property details, valuation history
- [ ] Implement custody information section for all asset types
- [ ] Add tax lot tracking display
- [ ] Create ESG ratings display section
- [ ] Add insurance and restrictions information
- [ ] Implement counterparty risk display
- [ ] Test detail pages for all 63 securities across 6 asset classes

## Current Sprint: Data Enrichment Pipeline for ML/RL
- [x] Design data enrichment pipeline architecture diagram
- [x] Create price_history table for time-series storage
- [x] Implement data persistence layer in securities router
- [x] Add automatic price data capture on API calls
- [ ] Create Kafka event publishers for PriceUpdated events
- [ ] Build scheduled job for daily market data enrichment
- [ ] Implement Parquet export for Data Mesh integration
- [ ] Create Zeta Agent workflow for automated enrichment
- [ ] Add data quality checks and validation
- [ ] Implement rate limiting and API quota management
- [ ] Create monitoring dashboard for enrichment pipeline
- [ ] Test end-to-end data flow from API to ML storage
