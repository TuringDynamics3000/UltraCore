import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, decimal, boolean, json, date, bigint } from "drizzle-orm/pg-core";

/**
 * UltraCore Operations Portal Database Schema
 * Comprehensive schema for portfolios, ESG, loans, RL agents, and system management
 */

// ============================================================================
// USERS & AUTHENTICATION
// ============================================================================

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: pgEnum("role", ["user", "admin", "operations", "analyst"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// ============================================================================
// PORTFOLIOS
// ============================================================================

export const portfolios = pgTable("portfolios", {
  id: varchar("id", { length: 64 }).primaryKey(),
  investorId: integer("investor_id").notNull(),
  investorName: varchar("investor_name", { length: 255 }).notNull(),
  agent: pgEnum("agent", ["alpha", "beta", "gamma", "delta", "epsilon"]).notNull(),
  value: numeric("value", { precision: 15, scale: 2 }).notNull(),
  initialInvestment: numeric("initial_investment", { precision: 15, scale: 2 }).notNull(),
  return30d: numeric("return_30d", { precision: 8, scale: 4 }),
  return1y: numeric("return_1y", { precision: 8, scale: 4 }),
  sharpeRatio: numeric("sharpe_ratio", { precision: 8, scale: 4 }),
  volatility: numeric("volatility", { precision: 8, scale: 4 }),
  maxDrawdown: numeric("max_drawdown", { precision: 8, scale: 4 }),
  status: pgEnum("status", ["active", "paused", "closed"]).default("active").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type Portfolio = typeof portfolios.$inferSelect;
export type InsertPortfolio = typeof portfolios.$inferInsert;

export const portfolioHoldings = pgTable("portfolio_holdings", {
  id: serial("id").primaryKey(),
  portfolioId: varchar("portfolio_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 20 }).notNull(),
  weight: numeric("weight", { precision: 8, scale: 6 }).notNull(),
  value: numeric("value", { precision: 15, scale: 2 }).notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type PortfolioHolding = typeof portfolioHoldings.$inferSelect;

// ============================================================================
// ESG DATA
// ============================================================================

export const esgData = pgTable("esg_data", {
  id: serial("id").primaryKey(),
  ticker: varchar("ticker", { length: 20 }).notNull().unique(),
  name: varchar("name", { length: 255 }).notNull(),
  esgRating: varchar("esg_rating", { length: 10 }),
  esgScore: integer("esg_score"),
  environmentScore: integer("environment_score"),
  socialScore: integer("social_score"),
  governanceScore: integer("governance_score"),
  carbonIntensity: numeric("carbon_intensity", { precision: 10, scale: 2 }),
  controversyScore: integer("controversy_score"),
  provider: varchar("provider", { length: 50 }),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type EsgData = typeof esgData.$inferSelect;
export type InsertEsgData = typeof esgData.$inferInsert;

// ============================================================================
// ULTRAGROW LOANS
// ============================================================================

export const loans = pgTable("loans", {
  id: varchar("id", { length: 64 }).primaryKey(),
  portfolioId: varchar("portfolio_id", { length: 64 }).notNull(),
  investorId: integer("investor_id").notNull(),
  amount: numeric("amount", { precision: 15, scale: 2 }).notNull(),
  portfolioValue: numeric("portfolio_value", { precision: 15, scale: 2 }).notNull(),
  ltv: numeric("ltv", { precision: 5, scale: 4 }).notNull(),
  termMonths: integer("term_months").notNull(),
  feeRate: numeric("fee_rate", { precision: 5, scale: 4 }).notNull(),
  monthlyPayment: numeric("monthly_payment", { precision: 15, scale: 2 }).notNull(),
  remainingBalance: numeric("remaining_balance", { precision: 15, scale: 2 }).notNull(),
  status: pgEnum("status", ["pending", "active", "paid", "defaulted", "liquidated"]).default("pending").notNull(),
  approvedBy: integer("approved_by"),
  approvedAt: timestamp("approved_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type Loan = typeof loans.$inferSelect;
export type InsertLoan = typeof loans.$inferInsert;

export const loanPayments = pgTable("loan_payments", {
  id: serial("id").primaryKey(),
  loanId: varchar("loan_id", { length: 64 }).notNull(),
  amount: numeric("amount", { precision: 15, scale: 2 }).notNull(),
  principal: numeric("principal", { precision: 15, scale: 2 }).notNull(),
  fee: numeric("fee", { precision: 15, scale: 2 }).notNull(),
  dueDate: timestamp("due_date").notNull(),
  paidDate: timestamp("paid_date"),
  status: pgEnum("status", ["pending", "paid", "late", "missed"]).default("pending").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type LoanPayment = typeof loanPayments.$inferSelect;

// ============================================================================
// RL AGENTS & TRAINING
// ============================================================================

export const rlAgents = pgTable("rl_agents", {
  id: serial("id").primaryKey(),
  name: pgEnum("name", ["alpha", "beta", "gamma", "delta", "epsilon"]).notNull().unique(),
  displayName: varchar("display_name", { length: 100 }).notNull(),
  objective: text("objective").notNull(),
  modelVersion: varchar("model_version", { length: 50 }).notNull(),
  status: pgEnum("status", ["training", "deployed", "paused", "deprecated"]).default("deployed").notNull(),
  episodesTrained: integer("episodes_trained").default(0).notNull(),
  avgReward: numeric("avg_reward", { precision: 10, scale: 4 }),
  lastTrainedAt: timestamp("last_trained_at"),
  deployedAt: timestamp("deployed_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type RlAgent = typeof rlAgents.$inferSelect;
export type InsertRlAgent = typeof rlAgents.$inferInsert;

// Training runs table moved to RL AGENT TRAINING section below

// ============================================================================
// KAFKA EVENTS (Metadata only - actual events in Kafka)
// ============================================================================

export const kafkaTopics = pgTable("kafka_topics", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 255 }).notNull().unique(),
  description: text("description"),
  partitions: integer("partitions").default(1).notNull(),
  replicationFactor: integer("replication_factor").default(1).notNull(),
  enabled: boolean("enabled").default(true).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type KafkaTopic = typeof kafkaTopics.$inferSelect;

// Kafka Events - Actual event data for audit/replay
export const kafkaEvents = pgTable("kafka_events", {
  id: varchar("id", { length: 128 }).primaryKey(),
  topic: varchar("topic", { length: 255 }).notNull(),
  key: varchar("key", { length: 255 }).notNull(),
  value: json("value").notNull(),
  partition: integer("partition").default(0).notNull(),
  offset: bigint("offset", { mode: "number" }).notNull(),
  timestamp: timestamp("timestamp").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type KafkaEvent = typeof kafkaEvents.$inferSelect;
export type InsertKafkaEvent = typeof kafkaEvents.$inferInsert;

// ============================================================================
// RL AGENT TRAINING
// ============================================================================

export const trainingRuns = pgTable("training_runs", {
  id: varchar("id", { length: 64 }).primaryKey(),
  agentName: pgEnum("agent_name", ["alpha", "beta", "gamma", "delta", "epsilon"]).notNull(),
  status: pgEnum("status", ["running", "paused", "completed", "failed"]).default("running").notNull(),
  startedAt: timestamp("started_at").defaultNow().notNull(),
  completedAt: timestamp("completed_at"),
  totalEpisodes: integer("total_episodes").default(0).notNull(),
  currentEpisode: integer("current_episode").default(0).notNull(),
  bestReward: numeric("best_reward", { precision: 15, scale: 4 }),
  avgReward: numeric("avg_reward", { precision: 15, scale: 4 }),
  portfolioValue: numeric("portfolio_value", { precision: 15, scale: 2 }),
  sharpeRatio: numeric("sharpe_ratio", { precision: 8, scale: 4 }),
  errorMessage: text("error_message"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type TrainingRun = typeof trainingRuns.$inferSelect;
export type InsertTrainingRun = typeof trainingRuns.$inferInsert;

export const trainingMetrics = pgTable("training_metrics", {
  id: serial("id").primaryKey(),
  runId: varchar("run_id", { length: 64 }).notNull(),
  episode: integer("episode").notNull(),
  reward: numeric("reward", { precision: 15, scale: 4 }).notNull(),
  portfolioValue: numeric("portfolio_value", { precision: 15, scale: 2 }).notNull(),
  totalReturn: numeric("total_return", { precision: 8, scale: 4 }),
  sharpeRatio: numeric("sharpe_ratio", { precision: 8, scale: 4 }),
  maxDrawdown: numeric("max_drawdown", { precision: 8, scale: 4 }),
  tradesExecuted: integer("trades_executed").default(0).notNull(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
});

export type TrainingMetric = typeof trainingMetrics.$inferSelect;
export type InsertTrainingMetric = typeof trainingMetrics.$inferInsert;

export const agentPerformance = pgTable("agent_performance", {
  id: serial("id").primaryKey(),
  agentName: pgEnum("agent_name", ["alpha", "beta", "gamma", "delta", "epsilon"]).notNull(),
  totalRuns: integer("total_runs").default(0).notNull(),
  successfulRuns: integer("successful_runs").default(0).notNull(),
  avgReward: numeric("avg_reward", { precision: 15, scale: 4 }),
  bestReward: numeric("best_reward", { precision: 15, scale: 4 }),
  avgSharpeRatio: numeric("avg_sharpe_ratio", { precision: 8, scale: 4 }),
  avgReturn: numeric("avg_return", { precision: 8, scale: 4 }),
  totalEpisodes: integer("total_episodes").default(0).notNull(),
  lastTrainedAt: timestamp("last_trained_at"),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type AgentPerformance = typeof agentPerformance.$inferSelect;
export type InsertAgentPerformance = typeof agentPerformance.$inferInsert;

// ============================================================================
// DATA MESH PRODUCTS
// ============================================================================

export const dataProducts = pgTable("data_products", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 255 }).notNull().unique(),
  ticker: varchar("ticker", { length: 20 }),
  description: text("description"),
  category: pgEnum("category", [
    "australian_equities",
    "us_equities",
    "international",
    "asia_pacific",
    "technology",
    "healthcare",
    "financials",
    "energy",
    "commodities",
    "fixed_income",
    "dividend_income",
    "esg_sustainable",
    "broad_market",
    "other"
  ]).notNull(),
  expenseRatio: varchar("expense_ratio", { length: 20 }),
  aum: varchar("aum", { length: 50 }),
  s3Path: varchar("s3_path", { length: 500 }).notNull(),
  format: varchar("format", { length: 50 }).notNull(),
  schema: text("schema"),
  rowCount: integer("row_count"),
  sizeBytes: integer("size_bytes"),
  owner: varchar("owner", { length: 100 }),
  status: pgEnum("status", ["active", "deprecated", "archived"]).default("active").notNull(),
  lastUpdated: timestamp("last_updated").defaultNow().notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type DataProduct = typeof dataProducts.$inferSelect;
export type InsertDataProduct = typeof dataProducts.$inferInsert;

// ============================================================================
// MCP TOOLS REGISTRY
// ============================================================================

export const mcpTools = pgTable("mcp_tools", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 255 }).notNull().unique(),
  description: text("description").notNull(),
  category: pgEnum("category", ["portfolio", "esg", "loan", "agent", "data", "system"]).notNull(),
  inputSchema: text("input_schema").notNull(),
  enabled: boolean("enabled").default(true).notNull(),
  executionCount: integer("execution_count").default(0).notNull(),
  lastExecuted: timestamp("last_executed"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type McpTool = typeof mcpTools.$inferSelect;

export const mcpExecutions = pgTable("mcp_executions", {
  id: serial("id").primaryKey(),
  toolId: integer("tool_id").notNull(),
  toolName: varchar("tool_name", { length: 255 }).notNull(),
  input: text("input").notNull(),
  output: text("output"),
  status: pgEnum("status", ["success", "error", "timeout"]).notNull(),
  duration: integer("duration"),
  executedBy: varchar("executed_by", { length: 100 }),
  executedAt: timestamp("executed_at").defaultNow().notNull(),
});

export type McpExecution = typeof mcpExecutions.$inferSelect;

// ============================================================================
// AUDIT LOG
// ============================================================================

export const auditLog = pgTable("audit_log", {
  id: serial("id").primaryKey(),
  userId: integer("user_id"),
  action: varchar("action", { length: 100 }).notNull(),
  resource: varchar("resource", { length: 100 }).notNull(),
  resourceId: varchar("resource_id", { length: 64 }),
  details: text("details"),
  ipAddress: varchar("ip_address", { length: 45 }),
  userAgent: text("user_agent"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type AuditLog = typeof auditLog.$inferSelect;

// ============================================================================
/**
 * GLOBAL ASSET REGISTER
 * 
 * Comprehensive securities and alternative assets registry for UltraCore
 * Supports: Traditional securities, crypto, alternatives (art, wine, real estate), off-market assets
 * 
 * Event-sourced architecture with Kafka for full audit trail and regulatory compliance
 */

// ============================================================================
// GLOBAL ASSET REGISTER - Main Table
// ============================================================================

export const securities = pgTable("securities", {
  // Primary Identification
  id: varchar("id", { length: 64 }).primaryKey(), // Internal ID, ISIN, crypto address, or custom ID
  ticker: varchar("ticker", { length: 50 }).notNull(), // Stock ticker, crypto symbol, or custom identifier
  name: text("name").notNull(),
  
  // Asset Classification
  assetClass: pgEnum("asset_class", [
    // Traditional Securities (On-Market)
    "equity",              // Listed stocks
    "etf",                 // Exchange-Traded Funds
    "bond",                // Fixed Income
    "reit",                // Real Estate Investment Trusts
    "mutual_fund",         // Mutual Funds
    
    // Derivatives & Structured Products
    "option",              // Options contracts
    "future",              // Futures contracts
    "swap",                // Swaps
    "structured_product",  // CDOs, CLOs, Structured Notes
    
    // Digital Assets
    "crypto",              // Bitcoin, Ethereum, Altcoins
    "stablecoin",          // USDT, USDC, DAI
    "nft",                 // Non-Fungible Tokens
    "tokenized_asset",     // Tokenized real estate, art, etc.
    
    // Alternative Assets (Off-Market)
    "artwork",             // Fine art, paintings, sculptures
    "collectible",         // Rare coins, stamps, memorabilia
    "wine",                // Fine wine investments
    "real_estate",         // Physical property
    "private_equity",      // Private company shares
    "venture_capital",     // VC fund interests
    "hedge_fund",          // Hedge fund units
    "commodity",           // Gold, Silver, Oil (physical or paper)
    "forex",               // Currency pairs
    
    // Other
    "other"                // Catch-all for unique assets
  ]).notNull(),
  
  // Market Classification
  marketType: pgEnum("market_type", [
    "exchange_traded",     // Listed on public exchange (ASX, NYSE, NASDAQ)
    "otc",                 // Over-the-counter
    "private",             // Private placement, not publicly traded
    "decentralized",       // Crypto DEX, blockchain-based
    "physical"             // Physical asset (art, wine, real estate)
  ]).notNull(),
  
  // Exchange/Platform
  exchange: varchar("exchange", { length: 100 }), // ASX, NYSE, Binance, Sothebys, Private, etc.
  tradingVenue: varchar("trading_venue", { length: 100 }), // Primary trading venue
  
  // Currency/Denomination
  currency: varchar("currency", { length: 10 }).default("AUD").notNull(), // AUD, USD, BTC, ETH, etc.
  denomination: varchar("denomination", { length: 50 }), // For bonds: face value unit, for art: valuation currency
  
  // Global Identifiers (Traditional Securities)
  isin: varchar("isin", { length: 12 }).unique(), // International Securities Identification Number
  sedol: varchar("sedol", { length: 7 }).unique(), // Stock Exchange Daily Official List
  cusip: varchar("cusip", { length: 9 }).unique(), // CUSIP
  figi: varchar("figi", { length: 12 }).unique(), // Financial Instrument Global Identifier (Bloomberg)
  lei: varchar("lei", { length: 20 }).unique(), // Legal Entity Identifier
  
  // Digital Asset Identifiers
  contractAddress: varchar("contract_address", { length: 100 }), // Smart contract address (Ethereum, etc.)
  blockchain: varchar("blockchain", { length: 50 }), // Ethereum, Bitcoin, Solana, Polygon, etc.
  tokenStandard: varchar("token_standard", { length: 20 }), // ERC-20, ERC-721, ERC-1155, BEP-20, etc.
  
  // Alternative Asset Identifiers
  registryId: varchar("registry_id", { length: 100 }), // Land registry, art registry, wine registry ID
  certificateNumber: varchar("certificate_number", { length: 100 }), // Authentication certificate
  appraisalId: varchar("appraisal_id", { length: 100 }), // Professional appraisal reference
  
  // Classification & Metadata
  sector: varchar("sector", { length: 100 }),
  industry: varchar("industry", { length: 100 }),
  country: varchar("country", { length: 2 }), // ISO 3166-1 alpha-2
  region: varchar("region", { length: 100 }), // Geographic region
  
  // Asset-Specific Details (JSON for flexibility)
  metadata: json("metadata"), // Flexible storage for asset-specific data
  // Examples:
  // - Art: {artist, year, medium, dimensions, provenance, condition}
  // - Wine: {vintage, producer, region, bottle_size, storage_conditions}
  // - Real Estate: {address, sqm, bedrooms, property_type, zoning}
  // - Crypto: {total_supply, circulating_supply, consensus_mechanism}
  
  // Valuation & Pricing
  lastPrice: numeric("last_price", { precision: 20, scale: 8 }), // Support crypto decimals
  lastPriceDate: timestamp("last_price_date"),
  lastVolume: bigint("last_volume", { mode: "number" }),
  marketCap: numeric("market_cap", { precision: 20, scale: 2 }),
  
  // Liquidity & Trading
  isLiquid: boolean("is_liquid").default(true), // Can it be easily sold?
  minTradeSize: numeric("min_trade_size", { precision: 20, scale: 8 }),
  lotSize: numeric("lot_size", { precision: 20, scale: 8 }),
  
  // Status & Lifecycle
  listingDate: date("listing_date"),
  delistingDate: date("delisting_date"),
  maturityDate: date("maturity_date"), // For bonds, options, futures
  isActive: boolean("is_active").default(true).notNull(),
  status: pgEnum("status", [
    "active",
    "suspended",
    "delisted",
    "matured",
    "defaulted",
    "sold"           // For unique assets like art
  ]).default("active").notNull(),
  
  // Data Integration
  parquetUrl: text("parquet_url"), // Link to historical OHLCV data in S3
  dataProductId: varchar("data_product_id", { length: 64 }), // Link to Data Mesh product
  externalDataSources: json("external_data_sources"), // APIs, data providers
  
  // Regulatory & Compliance
  regulatoryClassification: varchar("regulatory_classification", { length: 100 }),
  isRegulated: boolean("is_regulated").default(true),
  custodian: varchar("custodian", { length: 255 }), // Who holds the asset
  
  // Audit Trail
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  createdBy: varchar("created_by", { length: 64 }), // user ID or 'zeta-agent'
  source: varchar("source", { length: 50 }).default("manual").notNull(), // 'manual', 'openfigi', 'zeta-agent', 'blockchain'
  verificationStatus: pgEnum("verification_status", [
    "unverified",
    "pending",
    "verified",
    "disputed"
  ]).default("unverified").notNull(),
  verifiedBy: varchar("verified_by", { length: 64 }), // user ID or 'zeta-agent'
  verifiedAt: timestamp("verified_at"),
});

export type Security = typeof securities.$inferSelect;
export type InsertSecurity = typeof securities.$inferInsert;

// ============================================================================
// CORPORATE ACTIONS & EVENTS
// ============================================================================

export const corporateActions = pgTable("corporate_actions", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }).notNull(),
  actionType: pgEnum("action_type", [
    "dividend",
    "split",
    "reverse_split",
    "merger",
    "acquisition",
    "spinoff",
    "delisting",
    "rights_issue",
    "bonus_issue",
    "buyback",
    "name_change",
    "ticker_change",
    // Crypto-specific
    "hard_fork",
    "airdrop",
    "token_burn",
    "staking_reward",
    // Alternative assets
    "appraisal_update",
    "ownership_transfer",
    "restoration",        // For art
    "recertification"     // For collectibles, wine
  ]).notNull(),
  announcementDate: date("announcement_date").notNull(),
  effectiveDate: date("effective_date").notNull(),
  recordDate: date("record_date"),
  paymentDate: date("payment_date"),
  details: json("details"), // Flexible storage for action-specific data
  status: pgEnum("status", ["announced", "confirmed", "completed", "cancelled"]).default("announced").notNull(),
  impactOnHoldings: json("impact_on_holdings"), // How this affects portfolio holdings
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type CorporateAction = typeof corporateActions.$inferSelect;
export type InsertCorporateAction = typeof corporateActions.$inferInsert;

// ============================================================================
// SECURITY EVENTS (Kafka Event Store - Materialized View)
// ============================================================================

export const securityEvents = pgTable("security_events", {
  id: varchar("id", { length: 64 }).primaryKey(), // Event ID from Kafka
  eventType: varchar("event_type", { length: 50 }).notNull(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }),
  eventData: json("event_data").notNull(), // Full event payload
  source: varchar("source", { length: 50 }).notNull(), // 'user', 'zeta-agent', 'openfigi-api', 'blockchain'
  userId: varchar("user_id", { length: 64 }),
  timestamp: timestamp("timestamp").notNull(),
  kafkaOffset: bigint("kafka_offset", { mode: "number" }), // Kafka partition offset
  kafkaPartition: integer("kafka_partition"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type SecurityEvent = typeof securityEvents.$inferSelect;
export type InsertSecurityEvent = typeof securityEvents.$inferInsert;

// ============================================================================
// PRICE HISTORY (For assets not in Data Mesh Parquet files)
// ============================================================================

export const priceHistory = pgTable("price_history", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }).notNull(),
  date: date("date").notNull(),
  timestamp: timestamp("timestamp").notNull(), // Precise timestamp for intraday data
  open: numeric("open", { precision: 20, scale: 8 }),
  high: numeric("high", { precision: 20, scale: 8 }),
  low: numeric("low", { precision: 20, scale: 8 }),
  close: numeric("close", { precision: 20, scale: 8 }).notNull(),
  volume: bigint("volume", { mode: "number" }),
  adjClose: numeric("adj_close", { precision: 20, scale: 8 }),
  marketCap: numeric("market_cap", { precision: 20, scale: 2 }),
  currency: varchar("currency", { length: 10 }).default("USD").notNull(),
  source: varchar("source", { length: 50 }).default("yahoo-finance").notNull(),
  interval: varchar("interval", { length: 10 }).default("1d").notNull(), // '1d', '1h', '5m', etc.
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type PriceHistory = typeof priceHistory.$inferSelect;
export type InsertPriceHistory = typeof priceHistory.$inferInsert;

// ============================================================================
// VALUATIONS (For alternative assets requiring periodic appraisals)
// ============================================================================

export const valuations = pgTable("valuations", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  valuationDate: date("valuation_date").notNull(),
  valuationAmount: numeric("valuation_amount", { precision: 20, scale: 2 }).notNull(),
  currency: varchar("currency", { length: 10 }).notNull(),
  valuationType: pgEnum("valuation_type", [
    "market",              // Current market value
    "appraisal",           // Professional appraisal
    "insurance",           // Insurance valuation
    "liquidation",         // Forced sale value
    "replacement",         // Replacement cost
    "fair_value"           // Accounting fair value
  ]).notNull(),
  appraiser: varchar("appraiser", { length: 255 }), // Appraiser name or firm
  appraisalDocument: text("appraisal_document"), // S3 URL to appraisal PDF
  methodology: text("methodology"), // Valuation methodology description
  notes: text("notes"),
  confidence: pgEnum("confidence", ["low", "medium", "high"]).default("medium"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  createdBy: varchar("created_by", { length: 64 }),
});

export type Valuation = typeof valuations.$inferSelect;
export type InsertValuation = typeof valuations.$inferInsert;

// ============================================================================
// FRACTIONAL OWNERSHIP (For shared assets)
// ============================================================================

export const securityOwnership = pgTable("security_ownership", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  portfolioId: varchar("portfolio_id", { length: 64 }), // Link to portfolio
  ownerId: varchar("owner_id", { length: 64 }).notNull(), // User or entity ID
  ownerName: varchar("owner_name", { length: 255 }),
  ownershipType: pgEnum("ownership_type", [
    "full",                // 100% ownership
    "fractional",          // Partial ownership
    "beneficial",          // Beneficial owner (not legal owner)
    "nominee",             // Held by nominee
    "syndicate",           // Part of syndicate
    "trust"                // Held in trust
  ]).notNull(),
  ownershipPercentage: numeric("ownership_percentage", { precision: 10, scale: 6 }), // Up to 6 decimals
  units: numeric("units", { precision: 20, scale: 8 }), // Number of units/shares/tokens owned
  acquisitionDate: date("acquisition_date").notNull(),
  acquisitionPrice: numeric("acquisition_price", { precision: 20, scale: 8 }),
  acquisitionCurrency: varchar("acquisition_currency", { length: 10 }),
  syndicationAgreement: text("syndication_agreement"), // S3 URL to agreement
  coOwners: json("co_owners"), // Array of co-owner details
  votingRights: boolean("voting_rights").default(true),
  transferRestrictions: text("transfer_restrictions"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityOwnership = typeof securityOwnership.$inferSelect;
export type InsertSecurityOwnership = typeof securityOwnership.$inferInsert;

// ============================================================================
// LENDING & BORROWING (Securities lending, crypto staking)
// ============================================================================

export const securityLending = pgTable("security_lending", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }).notNull(),
  lendingType: pgEnum("lending_type", [
    "securities_lending",  // Traditional stock lending
    "crypto_staking",      // Staking for rewards
    "crypto_lending",      // DeFi lending
    "collateral",          // Used as collateral
    "repo"                 // Repurchase agreement
  ]).notNull(),
  lender: varchar("lender", { length: 255 }),
  borrower: varchar("borrower", { length: 255 }),
  platform: varchar("platform", { length: 255 }), // Lending platform/protocol
  quantity: numeric("quantity", { precision: 20, scale: 8 }).notNull(),
  collateralValue: numeric("collateral_value", { precision: 20, scale: 2 }),
  interestRate: numeric("interest_rate", { precision: 8, scale: 4 }), // Annual percentage
  stakingRewardRate: numeric("staking_reward_rate", { precision: 8, scale: 4 }),
  startDate: date("start_date").notNull(),
  endDate: date("end_date"),
  lockupPeriod: integer("lockup_period"), // Days
  status: pgEnum("status", ["active", "completed", "defaulted", "recalled"]).default("active").notNull(),
  rewardsEarned: numeric("rewards_earned", { precision: 20, scale: 8 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityLending = typeof securityLending.$inferSelect;
export type InsertSecurityLending = typeof securityLending.$inferInsert;

// ============================================================================
// TAX LOT TRACKING (Cost basis for tax reporting)
// ============================================================================

export const taxLots = pgTable("tax_lots", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  portfolioId: varchar("portfolio_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }).notNull(),
  acquisitionDate: date("acquisition_date").notNull(),
  quantity: numeric("quantity", { precision: 20, scale: 8 }).notNull(),
  costBasis: numeric("cost_basis", { precision: 20, scale: 8 }).notNull(), // Per unit
  totalCost: numeric("total_cost", { precision: 20, scale: 2 }).notNull(),
  currency: varchar("currency", { length: 10 }).notNull(),
  acquisitionMethod: pgEnum("acquisition_method", [
    "purchase",
    "gift",
    "inheritance",
    "airdrop",
    "staking_reward",
    "dividend_reinvestment",
    "stock_split",
    "merger",
    "conversion"
  ]).notNull(),
  taxTreatment: pgEnum("tax_treatment", [
    "short_term",          // < 1 year
    "long_term",           // >= 1 year
    "tax_deferred",        // Retirement account
    "tax_exempt",          // Municipal bonds, etc.
    "capital_gains",
    "ordinary_income"
  ]),
  disposalDate: date("disposal_date"),
  disposalPrice: numeric("disposal_price", { precision: 20, scale: 8 }),
  disposalMethod: pgEnum("disposal_method", ["sale", "gift", "donation", "loss", "transfer"]),
  realizedGainLoss: numeric("realized_gain_loss", { precision: 20, scale: 2 }),
  isWashSale: boolean("is_wash_sale").default(false),
  status: pgEnum("status", ["open", "closed", "transferred"]).default("open").notNull(),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type TaxLot = typeof taxLots.$inferSelect;
export type InsertTaxLot = typeof taxLots.$inferInsert;

// ============================================================================
// ESG RATINGS (Link to ESG module)
// ============================================================================

export const securityEsgRatings = pgTable("security_esg_ratings", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }).notNull(),
  ratingDate: date("rating_date").notNull(),
  
  // ESG Scores (0-100)
  environmentalScore: numeric("environmental_score", { precision: 5, scale: 2 }),
  socialScore: numeric("social_score", { precision: 5, scale: 2 }),
  governanceScore: numeric("governance_score", { precision: 5, scale: 2 }),
  overallEsgScore: numeric("overall_esg_score", { precision: 5, scale: 2 }),
  
  // Ratings
  esgRating: varchar("esg_rating", { length: 10 }), // AAA, AA, A, BBB, etc.
  ratingProvider: varchar("rating_provider", { length: 100 }), // MSCI, Sustainalytics, etc.
  
  // Carbon & Climate
  carbonIntensity: numeric("carbon_intensity", { precision: 15, scale: 4 }), // tCO2e per $M revenue
  carbonFootprint: numeric("carbon_footprint", { precision: 20, scale: 2 }), // Total tCO2e
  climateRisk: pgEnum("climate_risk", ["low", "medium", "high", "severe"]),
  
  // Controversies
  controversyLevel: pgEnum("controversy_level", ["none", "low", "moderate", "high", "severe"]),
  controversyDetails: text("controversy_details"),
  
  // SDG Alignment (UN Sustainable Development Goals)
  sdgAlignment: json("sdg_alignment"), // Array of SDG numbers (1-17) and impact scores
  
  // Impact Metrics
  impactMetrics: json("impact_metrics"), // Custom impact KPIs
  
  source: varchar("source", { length: 100 }),
  dataQuality: pgEnum("data_quality", ["low", "medium", "high"]).default("medium"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityEsgRating = typeof securityEsgRatings.$inferSelect;
export type InsertSecurityEsgRating = typeof securityEsgRatings.$inferInsert;

// ============================================================================
// COUNTERPARTY RISK (For derivatives, OTC trades)
// ============================================================================

export const counterparties = pgTable("counterparties", {
  id: varchar("id", { length: 64 }).primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  legalName: varchar("legal_name", { length: 255 }),
  lei: varchar("lei", { length: 20 }).unique(), // Legal Entity Identifier
  entityType: pgEnum("entity_type", [
    "bank",
    "broker_dealer",
    "exchange",
    "custodian",
    "clearing_house",
    "hedge_fund",
    "private_equity",
    "insurance_company",
    "corporate",
    "government",
    "individual"
  ]).notNull(),
  country: varchar("country", { length: 2 }),
  creditRating: varchar("credit_rating", { length: 10 }), // AAA, AA+, etc.
  ratingAgency: varchar("rating_agency", { length: 50 }), // S&P, Moody's, Fitch
  riskLevel: pgEnum("risk_level", ["low", "medium", "high", "critical"]).default("medium"),
  isRegulated: boolean("is_regulated").default(true),
  regulators: json("regulators"), // Array of regulatory bodies
  exposureLimit: numeric("exposure_limit", { precision: 20, scale: 2 }),
  currentExposure: numeric("current_exposure", { precision: 20, scale: 2 }),
  collateralRequired: boolean("collateral_required").default(false),
  status: pgEnum("status", ["active", "suspended", "defaulted", "inactive"]).default("active").notNull(),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type Counterparty = typeof counterparties.$inferSelect;
export type InsertCounterparty = typeof counterparties.$inferInsert;

// ============================================================================
// INSURANCE & PROTECTION
// ============================================================================

export const securityInsurance = pgTable("security_insurance", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }),
  policyNumber: varchar("policy_number", { length: 100 }).notNull(),
  insurer: varchar("insurer", { length: 255 }).notNull(),
  insuranceType: pgEnum("insurance_type", [
    "property",            // For real estate
    "fine_art",            // For artwork
    "collectibles",        // For collectibles
    "transit",             // During transport
    "storage",             // While in storage
    "cyber",               // For digital assets
    "title",               // Title insurance
    "credit_default"       // CDS for bonds
  ]).notNull(),
  coverageAmount: numeric("coverage_amount", { precision: 20, scale: 2 }).notNull(),
  currency: varchar("currency", { length: 10 }).notNull(),
  deductible: numeric("deductible", { precision: 20, scale: 2 }),
  premium: numeric("premium", { precision: 20, scale: 2 }),
  premiumFrequency: pgEnum("premium_frequency", ["monthly", "quarterly", "annual"]),
  effectiveDate: date("effective_date").notNull(),
  expiryDate: date("expiry_date").notNull(),
  policyDocument: text("policy_document"), // S3 URL
  status: pgEnum("status", ["active", "expired", "cancelled", "claimed"]).default("active").notNull(),
  claimHistory: json("claim_history"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityInsurance = typeof securityInsurance.$inferSelect;
export type InsertSecurityInsurance = typeof securityInsurance.$inferInsert;

// ============================================================================
// PHYSICAL LOCATION & CUSTODY
// ============================================================================

export const securityLocations = pgTable("security_locations", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }),
  locationType: pgEnum("location_type", [
    "vault",               // Bank vault, secure storage
    "gallery",             // Art gallery
    "warehouse",           // General warehouse
    "cold_storage",        // Crypto cold wallet
    "hot_wallet",          // Crypto hot wallet
    "custodian",           // Financial custodian
    "exchange",            // Crypto exchange
    "property",            // Physical property location
    "cellar",              // Wine cellar
    "safe_deposit_box",
    "personal_residence"
  ]).notNull(),
  facilityName: varchar("facility_name", { length: 255 }),
  address: text("address"),
  city: varchar("city", { length: 100 }),
  country: varchar("country", { length: 2 }),
  coordinates: varchar("coordinates", { length: 50 }), // Lat/Long
  custodian: varchar("custodian", { length: 255 }),
  custodianContact: varchar("custodian_contact", { length: 255 }),
  walletAddress: varchar("wallet_address", { length: 255 }), // For crypto
  walletType: varchar("wallet_type", { length: 50 }), // Ledger, Trezor, MetaMask, etc.
  securityMeasures: json("security_measures"), // Array of security features
  accessRestrictions: text("access_restrictions"),
  environmentalConditions: json("environmental_conditions"), // Temperature, humidity for wine/art
  lastVerified: timestamp("last_verified"),
  verifiedBy: varchar("verified_by", { length: 64 }),
  status: pgEnum("status", ["active", "in_transit", "relocated", "disposed"]).default("active").notNull(),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityLocation = typeof securityLocations.$inferSelect;
export type InsertSecurityLocation = typeof securityLocations.$inferInsert;

// ============================================================================
// RESTRICTIONS & LOCK-UPS
// ============================================================================

export const securityRestrictions = pgTable("security_restrictions", {
  id: varchar("id", { length: 64 }).primaryKey(),
  securityId: varchar("security_id", { length: 64 }).notNull(),
  ticker: varchar("ticker", { length: 50 }),
  restrictionType: pgEnum("restriction_type", [
    "lockup",              // Lock-up period
    "vesting",             // Vesting schedule
    "transfer_restriction", // Cannot transfer
    "trading_restriction", // Cannot trade
    "regulatory",          // Regulatory restriction
    "contractual",         // Contractual obligation
    "blackout",            // Blackout period
    "insider_trading"      // Insider trading restriction
  ]).notNull(),
  startDate: date("start_date").notNull(),
  endDate: date("end_date"),
  vestingSchedule: json("vesting_schedule"), // Array of vesting milestones
  percentageRestricted: numeric("percentage_restricted", { precision: 5, scale: 2 }),
  quantityRestricted: numeric("quantity_restricted", { precision: 20, scale: 8 }),
  reason: text("reason"),
  legalDocument: text("legal_document"), // S3 URL to agreement
  canSell: boolean("can_sell").default(false),
  canTransfer: boolean("can_transfer").default(false),
  canPledge: boolean("can_pledge").default(false),
  penaltyForViolation: text("penalty_for_violation"),
  status: pgEnum("status", ["active", "expired", "waived", "violated"]).default("active").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityRestriction = typeof securityRestrictions.$inferSelect;
export type InsertSecurityRestriction = typeof securityRestrictions.$inferInsert;

// ============================================================================
// RELATED SECURITIES (Parent/child relationships)
// ============================================================================

export const securityRelationships = pgTable("security_relationships", {
  id: varchar("id", { length: 64 }).primaryKey(),
  parentSecurityId: varchar("parent_security_id", { length: 64 }).notNull(),
  childSecurityId: varchar("child_security_id", { length: 64 }).notNull(),
  relationshipType: pgEnum("relationship_type", [
    "stock_split",         // Parent split into child
    "reverse_split",       // Child merged into parent
    "merger",              // Two securities merged
    "spinoff",             // Child spun off from parent
    "conversion",          // Convertible bond → equity
    "underlying",          // Derivative → underlying asset
    "etf_holding",         // ETF → constituent security
    "index_component",     // Index → component stock
    "adr_ordinary",        // ADR → ordinary shares
    "preferred_common",    // Preferred → common stock
    "warrant_stock",       // Warrant → underlying stock
    "option_stock",        // Option → underlying stock
    "token_asset"          // Tokenized asset → physical asset
  ]).notNull(),
  relationshipRatio: varchar("relationship_ratio", { length: 50 }), // e.g., "2:1", "1:10"
  effectiveDate: date("effective_date").notNull(),
  endDate: date("end_date"),
  conversionPrice: numeric("conversion_price", { precision: 20, scale: 8 }),
  details: json("details"),
  status: pgEnum("status", ["active", "completed", "cancelled"]).default("active").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export type SecurityRelationship = typeof securityRelationships.$inferSelect;
export type InsertSecurityRelationship = typeof securityRelationships.$inferInsert;


// ============================================================================
// ANYA OPERATIONS AI
// ============================================================================

export const conversations = pgTable("conversations", {
  id: varchar("id", { length: 64 }).primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  title: varchar("title", { length: 500 }),
  summary: text("summary"),
  status: pgEnum("status", ["active", "archived"]).default("active").notNull(),
  messageCount: integer("message_count").default(0).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  lastMessageAt: timestamp("last_message_at"),
});

export type Conversation = typeof conversations.$inferSelect;
export type InsertConversation = typeof conversations.$inferInsert;

export const messages = pgTable("messages", {
  id: varchar("id", { length: 64 }).primaryKey(),
  conversationId: varchar("conversation_id", { length: 64 }).notNull().references(() => conversations.id),
  role: pgEnum("role", ["user", "assistant", "system", "tool"]).notNull(),
  content: text("content"),
  toolCalls: json("tool_calls"), // Array of {id, name, arguments}
  toolCallId: varchar("tool_call_id", { length: 64 }), // For tool response messages
  reasoning: text("reasoning"), // Larry's internal reasoning trace
  tokens: integer("tokens"), // Token count for this message
  model: varchar("model", { length: 100 }), // OpenAI model used
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type Message = typeof messages.$inferSelect;
export type InsertMessage = typeof messages.$inferInsert;

export const toolExecutions = pgTable("tool_executions", {
  id: varchar("id", { length: 64 }).primaryKey(),
  messageId: varchar("message_id", { length: 64 }).notNull().references(() => messages.id),
  toolName: varchar("tool_name", { length: 200 }).notNull(),
  input: json("input").notNull(),
  output: json("output"),
  error: text("error"),
  duration: integer("duration"), // Milliseconds
  status: pgEnum("status", ["pending", "success", "error"]).default("pending").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  completedAt: timestamp("completed_at"),
});

export type ToolExecution = typeof toolExecutions.$inferSelect;
export type InsertToolExecution = typeof toolExecutions.$inferInsert;

export const insights = pgTable("insights", {
  id: varchar("id", { length: 64 }).primaryKey(),
  type: pgEnum("type", ["anomaly", "opportunity", "risk", "recommendation"]).notNull(),
  severity: pgEnum("severity", ["low", "medium", "high", "critical"]).notNull(),
  title: varchar("title", { length: 500 }).notNull(),
  description: text("description").notNull(),
  data: json("data"), // Related data (security, portfolio, agent, etc.)
  source: varchar("source", { length: 200 }), // kafka_event, scheduled_analysis, etc.
  acknowledged: boolean("acknowledged").default(false).notNull(),
  acknowledgedBy: integer("acknowledged_by").references(() => users.id),
  acknowledgedAt: timestamp("acknowledged_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type Insight = typeof insights.$inferSelect;
export type InsertInsight = typeof insights.$inferInsert;

export const conversationEmbeddings = pgTable("conversation_embeddings", {
  id: varchar("id", { length: 64 }).primaryKey(),
  conversationId: varchar("conversation_id", { length: 64 }).notNull().references(() => conversations.id),
  messageId: varchar("message_id", { length: 64 }).references(() => messages.id),
  embedding: json("embedding").notNull(), // Vector embedding for RAG
  content: text("content").notNull(), // Text that was embedded
  metadata: json("metadata"), // Additional context
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type ConversationEmbedding = typeof conversationEmbeddings.$inferSelect;
export type InsertConversationEmbedding = typeof conversationEmbeddings.$inferInsert;
