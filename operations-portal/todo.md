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


## Current Sprint: Populate Securities Register from APIs
- [ ] Create batch enrichment script for all 63 securities
- [ ] Implement Fiscal.ai company profile fetching
- [ ] Implement Yahoo Finance price data fetching
- [ ] Update securities table with fetched metadata
- [ ] Persist historical price data to price_history table
- [ ] Add error handling and retry logic for API failures
- [ ] Create progress tracking and logging
- [ ] Verify data quality and completeness
- [ ] Create scheduled job for daily enrichment
- [ ] Test enrichment on all asset classes


## Current Sprint: Kafka Event Streaming for RL Agents
- [x] Design Kafka event schema (SecurityPriceUpdated, SecurityCreated, CorporateAction)
- [x] Create event publisher service with batching and retry logic
- [x] Integrate event publishing into enrichment pipeline
- [x] Build Kafka consumer API endpoints for RL agents
- [x] Implement event replay functionality for backtesting
- [x] Add event audit trail and monitoring
- [ ] Create WebSocket bridge for real-time event streaming
- [ ] Test event flow end-to-end


## Current Sprint: Complete Operations Portal
- [x] Build Kafka Events Dashboard page
- [x] Add real-time event statistics cards
- [x] Create event search and filtering UI
- [x] Add event timeline visualization
- [x] Fix TypeScript errors in SecurityDetail and PortfolioDetail
- [x] Polish navigation and routing
- [x] Final testing of all modules
- [ ] Create comprehensive README


## Current Sprint: RL Agent Training Dashboard
- [ ] Design training_runs and training_metrics tables
- [ ] Create agent_performance table for portfolio outcomes
- [ ] Add tRPC endpoints for training data retrieval
- [ ] Build Agent Training Dashboard page
- [ ] Add reward curve visualization with Chart.js
- [ ] Create training progress indicators and status badges
- [ ] Implement portfolio performance comparison charts
- [ ] Add training control panel (start/stop/pause)
- [ ] Create agent comparison view
- [ ] Test with sample training data


## Current Sprint: Add Explainers and Hints
- [x] Create InfoTooltip component for metric explanations
- [x] Create InfoCard component for module descriptions
- [x] Add tooltips to Dashboard metrics (AUM, Sharpe Ratio, etc.)
- [x] Add data source badges (Fiscal.ai, Yahoo Finance, Internal)
- [x] Create contextual help for Kafka Events
- [x] Add Securities page explainers (ISIN, CUSIP, Asset Classes)
- [ ] Add explainers to Portfolio metrics (Volatility, Max Drawdown)
- [ ] Add RL concept hints (Reward, Episode, Training Run)
- [ ] Test all tooltips and hints


## Current Sprint: Interactive Onboarding Tour
- [x] Install react-joyride package
- [x] Create OnboardingTour component
- [x] Define tour steps for Dashboard walkthrough
- [x] Add tour steps for Securities module
- [x] Add tour steps for Kafka Events
- [x] Implement localStorage to track tour completion
- [x] Add manual "Start Tour" button in Dashboard
- [x] Add "Skip Tour" and "Next" navigation
- [x] Style tour tooltips to match portal theme
- [x] Test complete tour flow


## Future: UltraWealth Account Creation Integration
- [ ] Design customer onboarding flow (KYC, risk profiling, compliance)
- [ ] Create WealthClient registration form with risk assessment
- [ ] Implement MDA contract signing workflow
- [ ] Build Statement of Advice (SOA) generation and delivery
- [ ] Add portfolio creation wizard with goal selection
- [ ] Integrate ETF universe selection (12 ASX ETFs)
- [ ] Implement fee structure display (0.50% management fee)
- [ ] Add compliance checks (ASIC, AFSL, best interests)
- [ ] Create admin approval workflow for new accounts
- [ ] Build customer self-service sign-up portal option
- [ ] Add Tax File Number validation
- [ ] Implement glide path strategy selection (first home, retirement, wealth accumulation)
- [ ] Create minimum investment validation ($1,000 pod, $100 monthly)
- [ ] Add Anya AI integration for onboarding support


## Current Sprint: Final Portal Completion
- [x] Create comprehensive README.md with architecture overview
- [x] Document all 9 modules and their features
- [x] Add setup and deployment instructions
- [x] Document API endpoints and data models
- [x] Review all modules for completeness (Dashboard, Portfolios, Securities, ESG, Loans, RL Agents, Kafka Events, Data Mesh, MCP Tools)
- [x] Test navigation between all pages
- [x] Verify all tooltips and explainers are working
- [x] Check responsive design on mobile/tablet
- [ ] Final checkpoint and commit to GitHub
- [x] Create deployment guide


## Current Sprint: Anya Operations AI Agent
- [ ] Design event-sourced conversation architecture
- [ ] Create conversations and messages tables for persistence
- [ ] Implement OpenAI Realtime API integration with streaming
- [ ] Add structured outputs with latest OpenAI schemas
- [ ] Build MCP tool registry (Data Mesh queries, Securities lookup, RL metrics)
- [ ] Create function calling handlers for all MCP tools
- [ ] Implement conversation context management with embeddings
- [ ] Build chat UI component with streaming responses
- [ ] Add voice interface (speech-to-text, text-to-speech)
- [ ] Create proactive insights engine monitoring Kafka events
- [ ] Implement RAG over securities/portfolio data with vector search
- [ ] Add explainable AI with reasoning trace visualization
- [ ] Build multi-turn memory with conversation summarization
- [ ] Add agentic workflows with tool chaining
- [ ] Create Anya sidebar widget accessible from all pages
- [ ] Implement conversation history and search
- [ ] Add conversation export and sharing
- [ ] Test end-to-end with complex queries


## Current Sprint: Larry Chat UI
- [x] Create Larry chat page component with split layout
- [x] Build conversation history sidebar
- [x] Add new conversation button
- [x] Implement message list with streaming support
- [x] Add markdown rendering with Streamdown
- [x] Create tool execution indicators
- [x] Add message input with auto-resize textarea
- [x] Add route for /larry page
- [x] Add Larry AI link to sidebar navigation
- [ ] Create floating chat button component
- [ ] Test streaming, history, and tool indicators


## Current: Fix Naming Consistency
- [x] Update System Status "MCP Server (Anya AI)" to "MCP Server (Larry AI)"
- [x] Search for any other Anya references in the codebase
- [x] Verify all references are consistent


## Current: Complete Larry AI System
- [ ] Commit Larry AI to GitHub (TuringDynamics3000/UltraCore)
- [ ] Test live conversations with sample queries
- [ ] Verify OpenAI integration and tool execution
- [ ] Create floating chat button component
- [ ] Integrate floating button into all pages
- [ ] Test complete Larry system end-to-end
