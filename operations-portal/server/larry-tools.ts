/**
 * Larry Operations AI - Tool Implementations
 * MCP-style tool registry connecting to real data sources
 */

import { getDb } from "./db";
import { eq, like, and, desc, sql } from "drizzle-orm";
import {
  securities,
  portfolios,
  portfolioHoldings,
  kafkaEvents,
  rlAgents,
  trainingRuns,
  trainingMetrics,
  dataProducts,
  insights,
  esgData,
} from "../drizzle/schema";
import { getUnacknowledgedInsights } from "./larry-conversation";

// ============================================================================
// SECURITIES TOOLS
// ============================================================================

export async function querySecurities(params: {
  search?: string;
  assetClass?: string;
  limit?: number;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const { search, assetClass, limit = 10 } = params;

  let query = db.select().from(securities);

  const conditions = [];
  if (search) {
    conditions.push(
      sql`(${securities.ticker} LIKE ${`%${search}%`} OR ${securities.name} LIKE ${`%${search}%`} OR ${securities.isin} LIKE ${`%${search}%`})`
    );
  }
  if (assetClass) {
    conditions.push(sql`${securities.assetClass} = ${assetClass}`);
  }

  if (conditions.length > 0) {
    query = query.where(and(...conditions)) as any;
  }

  const results = await query.limit(limit);

  return {
    securities: results.map((s) => ({
      ticker: s.ticker,
      name: s.name,
      assetClass: s.assetClass,
      marketCap: s.marketCap,
      sector: s.sector,
      exchange: s.exchange,
      isin: s.isin,
    })),
    total: results.length,
    query: { search, assetClass, limit },
  };
}

export async function getSecurityDetails(params: { ticker: string }) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const security = await db
    .select()
    .from(securities)
    .where(eq(securities.ticker, params.ticker))
    .limit(1);

  if (security.length === 0) {
    throw new Error(`Security not found: ${params.ticker}`);
  }

  const sec = security[0];

  // Get ESG data if available
  const esg = await db
    .select()
    .from(esgData)
    .where(eq(esgData.ticker, params.ticker))
    .limit(1);

  return {
    ticker: sec.ticker,
    name: sec.name,
    assetClass: sec.assetClass,
    sector: sec.sector,
    industry: sec.industry,
    marketCap: sec.marketCap,
    exchange: sec.exchange,
    marketType: sec.marketType,
    currency: sec.currency,
    isin: sec.isin,
    cusip: sec.cusip,
    contractAddress: sec.contractAddress,
    blockchain: sec.blockchain,
    esg: esg.length > 0 ? {
      esgScore: esg[0].esgScore,
      esgRating: esg[0].esgRating,
      environmentScore: esg[0].environmentScore,
      socialScore: esg[0].socialScore,
      governanceScore: esg[0].governanceScore,
      carbonIntensity: esg[0].carbonIntensity,
    } : null,
    updatedAt: sec.updatedAt,
  };
}

// ============================================================================
// PORTFOLIO TOOLS
// ============================================================================

export async function queryPortfolios(params: {
  agent?: string;
  status?: string;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const { agent, status } = params;

  let query = db.select().from(portfolios);

  const conditions = [];
  if (agent) {
    conditions.push(eq(portfolios.agent, agent as any));
  }
  if (status) {
    conditions.push(eq(portfolios.status, status as any));
  }

  if (conditions.length > 0) {
    query = query.where(and(...conditions)) as any;
  }

  const results = await query.orderBy(desc(portfolios.value)).limit(50);

  const totalValue = results.reduce(
    (sum, p) => sum + parseFloat(p.value.toString()),
    0
  );

  return {
    portfolios: results.map((p) => ({
      id: p.id,
      investorName: p.investorName,
      agent: p.agent,
      value: p.value,
      initialInvestment: p.initialInvestment,
      return30d: p.return30d,
      return1y: p.return1y,
      sharpeRatio: p.sharpeRatio,
      volatility: p.volatility,
      maxDrawdown: p.maxDrawdown,
      status: p.status,
      createdAt: p.createdAt,
    })),
    total: results.length,
    totalValue,
    query: { agent, status },
  };
}

export async function getPortfolioDetails(params: { portfolioId: string }) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const portfolio = await db
    .select()
    .from(portfolios)
    .where(eq(portfolios.id, params.portfolioId))
    .limit(1);

  if (portfolio.length === 0) {
    throw new Error(`Portfolio not found: ${params.portfolioId}`);
  }

  const holdings = await db
    .select()
    .from(portfolioHoldings)
    .where(eq(portfolioHoldings.portfolioId, params.portfolioId));

  const p = portfolio[0];

  return {
    id: p.id,
    investorId: p.investorId,
    investorName: p.investorName,
    agent: p.agent,
    value: p.value,
    initialInvestment: p.initialInvestment,
    return30d: p.return30d,
    return1y: p.return1y,
    sharpeRatio: p.sharpeRatio,
    volatility: p.volatility,
    maxDrawdown: p.maxDrawdown,
    status: p.status,
    holdings: holdings.map((h) => ({
      ticker: h.ticker,
      weight: h.weight,
      value: h.value,
    })),
    createdAt: p.createdAt,
    updatedAt: p.updatedAt,
  };
}

// ============================================================================
// KAFKA EVENT TOOLS
// ============================================================================

export async function queryKafkaEvents(params: {
  topic?: string;
  eventType?: string;
  limit?: number;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const { topic, eventType, limit = 20 } = params;

  let query = db.select().from(kafkaEvents);

  const conditions = [];
  if (topic) {
    conditions.push(eq(kafkaEvents.topic, topic));
  }
  // eventType field doesn't exist in schema, skip filtering by it

  if (conditions.length > 0) {
    query = query.where(and(...conditions)) as any;
  }

  const results = await query
    .orderBy(desc(kafkaEvents.timestamp))
    .limit(limit);

  return {
    events: results.map((e) => ({
      id: e.id,
      topic: e.topic,
      key: e.key,
      value: e.value,
      partition: e.partition,
      offset: e.offset,
      timestamp: e.timestamp,
    })),
    total: results.length,
    query: { topic, eventType, limit },
  };
}

// ============================================================================
// RL AGENT TOOLS
// ============================================================================

export async function queryRlAgents(params: { agentName?: string }) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const { agentName } = params;

  let query = db.select().from(rlAgents);

  if (agentName) {
    query = query.where(eq(rlAgents.name, agentName as any)) as any;
  }

  const results = await query;

  return {
    agents: results.map((a) => ({
      name: a.name,
      displayName: a.displayName,
      objective: a.objective,
      modelVersion: a.modelVersion,
      status: a.status,
      createdAt: a.createdAt,
    })),
    total: results.length,
  };
}

export async function getTrainingMetrics(params: {
  agentName: string;
  limit?: number;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const { agentName, limit = 100 } = params;

  // Get latest training run
  const runs = await db
    .select()
    .from(trainingRuns)
    .where(eq(trainingRuns.agentName, agentName as any))
    .orderBy(desc(trainingRuns.startedAt))
    .limit(1);

  if (runs.length === 0) {
    return {
      agentName,
      metrics: [],
      message: "No training runs found for this agent",
    };
  }

  const run = runs[0];

  // Get metrics for this run
  const metrics = await db
    .select()
    .from(trainingMetrics)
    .where(eq(trainingMetrics.runId, run.id))
    .orderBy(desc(trainingMetrics.episode))
    .limit(limit);

  return {
    agentName,
    runId: run.id,
    status: run.status,
    startedAt: run.startedAt,
    completedAt: run.completedAt,
    totalEpisodes: run.totalEpisodes,
    currentEpisode: run.currentEpisode,
    bestReward: run.bestReward,
    avgReward: run.avgReward,
    metrics: metrics.map((m) => ({
      episode: m.episode,
      reward: m.reward,
      sharpeRatio: m.sharpeRatio,
      maxDrawdown: m.maxDrawdown,
      portfolioValue: m.portfolioValue,
      totalReturn: m.totalReturn,
      tradesExecuted: m.tradesExecuted,
      timestamp: m.timestamp,
    })),
  };
}

// ============================================================================
// DATA MESH TOOLS
// ============================================================================

export async function queryDataProducts(params: {
  search?: string;
  category?: string;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const { search, category } = params;

  let query = db.select().from(dataProducts);

  const conditions = [];
  if (search) {
    conditions.push(
      sql`(${dataProducts.name} LIKE ${`%${search}%`} OR ${dataProducts.description} LIKE ${`%${search}%`})`
    );
  }
  if (category) {
    conditions.push(sql`${dataProducts.category} = ${category}`);
  }

  if (conditions.length > 0) {
    query = query.where(and(...conditions)) as any;
  }

  const results = await query.limit(50);

  return {
    products: results.map((p) => ({
      id: p.id,
      name: p.name,
      description: p.description,
      category: p.category,
      format: p.format,
      lastUpdated: p.lastUpdated,
      schema: p.schema,
    })),
    total: results.length,
    query: { search, category },
  };
}

export async function executeSqlQuery(params: {
  query: string;
  dataProductId: string;
}) {
  // This would integrate with DuckDB WASM in production
  // For now, return a placeholder
  return {
    dataProductId: params.dataProductId,
    query: params.query,
    rows: [],
    message:
      "SQL execution requires DuckDB WASM integration (not yet implemented)",
  };
}

// ============================================================================
// INSIGHTS TOOLS
// ============================================================================

export async function getInsights(params: {
  type?: string;
  severity?: string;
}) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const allInsights = await getUnacknowledgedInsights();

  let filtered = allInsights;

  if (params.type) {
    filtered = filtered.filter((i) => i.type === params.type);
  }

  if (params.severity) {
    filtered = filtered.filter((i) => i.severity === params.severity);
  }

  return {
    insights: filtered.map((i) => ({
      id: i.id,
      type: i.type,
      severity: i.severity,
      title: i.title,
      description: i.description,
      data: i.data,
      source: i.source,
      createdAt: i.createdAt,
    })),
    total: filtered.length,
    query: { type: params.type, severity: params.severity },
  };
}

// ============================================================================
// TOOL ROUTER
// ============================================================================

export async function executeLarryTool(
  toolName: string,
  args: any
): Promise<any> {
  console.log(`[Larry Tools] Executing: ${toolName}`, args);

  switch (toolName) {
    case "query_securities":
      return await querySecurities(args);

    case "get_security_details":
      return await getSecurityDetails(args);

    case "query_portfolios":
      return await queryPortfolios(args);

    case "get_portfolio_details":
      return await getPortfolioDetails(args);

    case "query_kafka_events":
      return await queryKafkaEvents(args);

    case "query_rl_agents":
      return await queryRlAgents(args);

    case "get_training_metrics":
      return await getTrainingMetrics(args);

    case "query_data_products":
      return await queryDataProducts(args);

    case "execute_sql_query":
      return await executeSqlQuery(args);

    case "get_insights":
      return await getInsights(args);

    default:
      throw new Error(`Unknown tool: ${toolName}`);
  }
}
