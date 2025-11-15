import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import * as db from "./db";
import { fiscalAI } from "./fiscal-ai";
import { callDataApi } from "./_core/dataApi";
import { persistYahooPriceData, enrichSecurityData } from "./enrichment";
import { getKafkaConsumer } from "./kafka-consumer";
import { createConversation, getUserConversations, getMessages, getConversationStats } from "./larry-conversation";
import { chatWithLarry } from "./larry-openai";

// ============================================================================
// PORTFOLIO ROUTER
// ============================================================================

const portfolioRouter = router({
  list: protectedProcedure.query(async () => {
    return await db.getPortfolios();
  }),

  getById: protectedProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    return await db.getPortfolioById(input.id);
  }),

  getByAgent: protectedProcedure
    .input(z.object({ agent: z.enum(["alpha", "beta", "gamma", "delta", "epsilon"]) }))
    .query(async ({ input }) => {
      return await db.getPortfoliosByAgent(input.agent);
    }),

  create: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        investorId: z.number(),
        investorName: z.string(),
        agent: z.enum(["alpha", "beta", "gamma", "delta", "epsilon"]),
        value: z.string(),
        initialInvestment: z.string(),
        return30d: z.string().optional(),
        return1y: z.string().optional(),
        sharpeRatio: z.string().optional(),
        volatility: z.string().optional(),
        maxDrawdown: z.string().optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      await db.logAudit({
        userId: ctx.user.id,
        action: "CREATE_PORTFOLIO",
        resource: "portfolio",
        resourceId: input.id,
        details: `Created portfolio ${input.investorName} with agent ${input.agent}`,
      });
      return await db.createPortfolio(input);
    }),

  update: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        value: z.string().optional(),
        return30d: z.string().optional(),
        return1y: z.string().optional(),
        sharpeRatio: z.string().optional(),
        volatility: z.string().optional(),
        maxDrawdown: z.string().optional(),
        status: z.enum(["active", "paused", "closed"]).optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      const { id, ...updates } = input;
      await db.logAudit({
        userId: ctx.user.id,
        action: "UPDATE_PORTFOLIO",
        resource: "portfolio",
        resourceId: id,
        details: `Updated portfolio ${id}`,
      });
      await db.updatePortfolio(id, updates);
      return { success: true };
    }),

  getHoldings: protectedProcedure
    .input(z.object({ portfolioId: z.string() }))
    .query(async ({ input }) => {
      return await db.getPortfolioHoldings(input.portfolioId);
    }),

  // Dashboard stats
  stats: protectedProcedure.query(async () => {
    const portfolios = await db.getPortfolios();
    const totalAUM = portfolios.reduce((sum, p) => sum + parseFloat(p.value), 0);
    const totalReturn = totalAUM > 0
      ? portfolios.reduce((sum, p) => sum + parseFloat(p.return30d || "0") * parseFloat(p.value), 0) / totalAUM
      : 0;
    const activeCount = portfolios.filter(p => p.status === "active").length;

    return {
      totalAUM,
      totalReturn,
      activeCount,
      totalCount: portfolios.length,
    };
  }),
});

// ============================================================================
// ESG ROUTER
// ============================================================================

const esgRouter = router({
  list: protectedProcedure.query(async () => {
    return await db.getEsgData();
  }),

  getByTicker: protectedProcedure.input(z.object({ ticker: z.string() })).query(async ({ input }) => {
    return await db.getEsgDataByTicker(input.ticker);
  }),

  upsert: protectedProcedure
    .input(
      z.object({
        ticker: z.string(),
        name: z.string(),
        esgRating: z.enum(["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]).optional(),
        esgScore: z.number().optional(),
        environmentScore: z.number().optional(),
        socialScore: z.number().optional(),
        governanceScore: z.number().optional(),
        carbonIntensity: z.string().optional(),
        controversyScore: z.number().optional(),
        provider: z.string().optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      await db.logAudit({
        userId: ctx.user.id,
        action: "UPSERT_ESG_DATA",
        resource: "esg_data",
        resourceId: input.ticker,
        details: `Updated ESG data for ${input.ticker}`,
      });
      await db.upsertEsgData(input);
      return { success: true };
    }),

  stats: protectedProcedure.query(async () => {
    const esgData = await db.getEsgData();
    const avgEsgScore = esgData.length > 0
      ? esgData.reduce((sum, e) => sum + (e.esgScore || 0), 0) / esgData.length
      : 0;
    const avgCarbonIntensity = esgData.length > 0
      ? esgData.reduce((sum, e) => sum + parseFloat(e.carbonIntensity || "0"), 0) / esgData.length
      : 0;
    const ratingDistribution = esgData.reduce((acc, e) => {
      const rating = e.esgRating || "N/A";
      acc[rating] = (acc[rating] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalAssets: esgData.length,
      avgEsgScore,
      avgCarbonIntensity,
      ratingDistribution,
    };
  }),
});

// ============================================================================
// ULTRAGROW LOANS ROUTER
// ============================================================================

const loanRouter = router({
  list: protectedProcedure.query(async () => {
    return await db.getLoans();
  }),

  getById: protectedProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    return await db.getLoanById(input.id);
  }),

  getByPortfolio: protectedProcedure
    .input(z.object({ portfolioId: z.string() }))
    .query(async ({ input }) => {
      return await db.getLoansByPortfolio(input.portfolioId);
    }),

  create: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        investorId: z.number(),
        portfolioId: z.string(),
        amount: z.string(),
        portfolioValue: z.string(),
        ltv: z.string(),
        termMonths: z.number(),
        feeRate: z.string(),
        monthlyPayment: z.string(),
        remainingBalance: z.string(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      await db.logAudit({
        userId: ctx.user.id,
        action: "CREATE_LOAN",
        resource: "loan",
        resourceId: input.id,
        details: `Created loan ${input.id} for $${input.amount}`,
      });
      return await db.createLoan(input);
    }),

  update: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        status: z.enum(["pending", "active", "paid", "defaulted", "liquidated"]).optional(),
        remainingBalance: z.string().optional(),
        ltv: z.string().optional(),
        portfolioValue: z.string().optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      const { id, ...updates } = input;
      await db.logAudit({
        userId: ctx.user.id,
        action: "UPDATE_LOAN",
        resource: "loan",
        resourceId: id,
        details: `Updated loan ${id}`,
      });
      await db.updateLoan(id, updates);
      return { success: true };
    }),

  getPayments: protectedProcedure
    .input(z.object({ loanId: z.string() }))
    .query(async ({ input }) => {
      return await db.getLoanPayments(input.loanId);
    }),

  stats: protectedProcedure.query(async () => {
    const loans = await db.getLoans();
    const totalLoaned = loans.reduce((sum, l) => sum + parseFloat(l.amount), 0);
    const totalOutstanding = loans.reduce((sum, l) => sum + parseFloat(l.remainingBalance), 0);
    const avgLTV = loans.reduce((sum, l) => sum + parseFloat(l.ltv), 0) / loans.length;
    const activeCount = loans.filter(l => l.status === "active").length;

    return {
      totalLoaned,
      totalOutstanding,
      avgLTV,
      activeCount,
      totalCount: loans.length,
    };
  }),
});

// ============================================================================
// RL AGENTS ROUTER
// ============================================================================

const rlAgentRouter = router({
  list: protectedProcedure.query(async () => {
    return await db.getRlAgents();
  }),

  getByName: protectedProcedure
    .input(z.object({ name: z.enum(["alpha", "beta", "gamma", "delta", "epsilon"]) }))
    .query(async ({ input }) => {
      return await db.getRlAgentByName(input.name);
    }),

  upsert: protectedProcedure
    .input(
      z.object({
        name: z.enum(["alpha", "beta", "gamma", "delta", "epsilon"]),
        displayName: z.string(),
        objective: z.string(),
        modelVersion: z.string(),
        status: z.enum(["training", "deployed", "paused"]).optional(),
        episodesTrained: z.number().optional(),
        avgReward: z.string().optional(),
        lastTrainedAt: z.date().optional(),
        deployedAt: z.date().optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      await db.logAudit({
        userId: ctx.user.id,
        action: "UPSERT_RL_AGENT",
        resource: "rl_agent",
        resourceId: input.name,
        details: `Updated RL agent ${input.name}`,
      });
      await db.upsertRlAgent(input);
      return { success: true };
    }),

  getTrainingRuns: protectedProcedure
    .input(z.object({ agentName: z.string().optional() }))
    .query(async ({ input }) => {
      return await db.getTrainingRuns(input.agentName as any);
    }),
});

// ============================================================================
// KAFKA ROUTER
// ============================================================================

const kafkaRouter = router({
  listTopics: protectedProcedure.query(async () => {
    return await db.getKafkaTopics();
  }),
});

// ============================================================================
// DATA MESH ROUTER
// ============================================================================

const dataMeshRouter = router({
  listProducts: protectedProcedure.query(async () => {
    return await db.getDataProducts();
  }),

  getByName: protectedProcedure.input(z.object({ name: z.string() })).query(async ({ input }) => {
    return await db.getDataProductByName(input.name);
  }),

  upsert: protectedProcedure
    .input(
      z.object({
        name: z.string(),
        description: z.string(),
        category: z.enum([
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
        ]),
        s3Path: z.string(),
        format: z.enum(["parquet", "csv", "json"]),
        schema: z.string().optional(),
        rowCount: z.number().optional(),
        sizeBytes: z.number().optional(),
        owner: z.string(),
        status: z.enum(["active", "deprecated", "archived"]).optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      await db.logAudit({
        userId: ctx.user.id,
        action: "UPSERT_DATA_PRODUCT",
        resource: "data_product",
        resourceId: input.name,
        details: `Updated data product ${input.name}`,
      });
      await db.upsertDataProduct(input);
      return { success: true };
    }),
});

// ============================================================================
// MCP TOOLS ROUTER
// ============================================================================

const mcpRouter = router({
  listTools: protectedProcedure.query(async () => {
    return await db.getMcpTools();
  }),

  getByName: protectedProcedure.input(z.object({ name: z.string() })).query(async ({ input }) => {
    return await db.getMcpToolByName(input.name);
  }),

  getExecutions: protectedProcedure
    .input(z.object({ toolId: z.number().optional(), limit: z.number().optional() }))
    .query(async ({ input }) => {
      return await db.getMcpExecutions(input.toolId, input.limit);
    }),
});

// ============================================================================
// AUDIT LOG ROUTER
// ============================================================================

const auditRouter = router({
  list: protectedProcedure
    .input(
      z.object({
        userId: z.number().optional(),
        resource: z.string().optional(),
        startDate: z.date().optional(),
        endDate: z.date().optional(),
        limit: z.number().optional(),
      })
    )
    .query(async ({ input }) => {
      return await db.getAuditLogs(input);
    }),
});

// ============================================================================
// SECURITIES REGISTER ROUTER
// ============================================================================

const securitiesRouter = router({ list: protectedProcedure
    .input(
      z.object({
        assetClass: z.string().optional(),
        marketType: z.string().optional(),
        search: z.string().optional(),
        exchange: z.string().optional(),
        sector: z.string().optional(),
        limit: z.number().optional(),
      })
    )
    .query(async ({ input }) => {
      return await db.getSecurities(input);
    }),

  getById: protectedProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    return await db.getSecurityById(input.id);
  }),

  getByTicker: protectedProcedure.input(z.object({ ticker: z.string() })).query(async ({ input }) => {
    return await db.getSecurityByTicker(input.ticker);
  }),

  create: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        ticker: z.string(),
        name: z.string(),
        assetClass: z.string(),
        marketType: z.string(),
        exchange: z.string().optional(),
        currency: z.string(),
        lastPrice: z.string().optional(),
        marketCap: z.string().optional(),
      })
    )
    .mutation(async ({ input, ctx }) => {
      await db.logAudit({
        userId: ctx.user.id,
        action: "CREATE_SECURITY",
        resource: "security",
        resourceId: input.id,
        details: `Created security ${input.ticker} - ${input.name}`,
      });
      return { success: true };
    }),

  // Fiscal.ai integration endpoints
  getMarketData: protectedProcedure
    .input(z.object({ ticker: z.string() }))
    .query(async ({ input }) => {
      try {
        const [profile, latestPrice, ratios] = await Promise.all([
          fiscalAI.getCompanyProfile(input.ticker).catch(() => null),
          fiscalAI.getLatestPrice(input.ticker).catch(() => null),
          fiscalAI.getCompanyRatios(input.ticker, "annual", 1).catch(() => []),
        ]);

        return {
          profile,
          latestPrice,
          ratios: ratios.length > 0 ? ratios[0] : null,
        };
      } catch (error) {
        console.error("Fiscal.ai API error:", error);
        return { profile: null, latestPrice: null, ratios: null };
      }
    }),

  getPriceHistory: protectedProcedure
    .input(
      z.object({
        ticker: z.string(),
        fromDate: z.string().optional(),
        toDate: z.string().optional(),
      })
    )
    .query(async ({ input }) => {
      try {
        return await fiscalAI.getStockPrices(input.ticker, input.fromDate, input.toDate);
      } catch (error) {
        console.error("Fiscal.ai price history error:", error);
        return [];
      }
    }),

  getFinancials: protectedProcedure
    .input(
      z.object({
        ticker: z.string(),
        period: z.enum(["annual", "quarterly"]).default("annual"),
      })
    )
    .query(async ({ input }) => {
      try {
        const [incomeStatement, balanceSheet, cashFlow] = await Promise.all([
          fiscalAI.getIncomeStatement(input.ticker, input.period, 5).catch(() => []),
          fiscalAI.getBalanceSheet(input.ticker, input.period, 5).catch(() => []),
          fiscalAI.getCashFlowStatement(input.ticker, input.period, 5).catch(() => []),
        ]);

        return {
          incomeStatement,
          balanceSheet,
          cashFlow,
        };
      } catch (error) {
        console.error("Fiscal.ai financials error:", error);
        return { incomeStatement: [], balanceSheet: [], cashFlow: [] };
      }
    }),

  // Yahoo Finance integration endpoints
  getYahooInsights: protectedProcedure
    .input(z.object({ symbol: z.string() }))
    .query(async ({ input }) => {
      try {
        const result = await callDataApi("YahooFinance/get_stock_insights", {
          query: { symbol: input.symbol },
        });
        return result;
      } catch (error) {
        console.error("Yahoo Finance insights error:", error);
        return null;
      }
    }),

  getYahooChart: protectedProcedure
    .input(
      z.object({
        symbol: z.string(),
        interval: z.string().default("1d"),
        range: z.string().default("1mo"),
      })
    )
    .query(async ({ input }) => {
      try {
        const result = await callDataApi("YahooFinance/get_stock_chart", {
          query: {
            symbol: input.symbol,
            region: "US",
            interval: input.interval,
            range: input.range,
            includeAdjustedClose: true,
            events: "div,split",
          },
        });

        // AUTO-PERSIST: Store price data for ML/RL training
        if (result) {
          const security = await db.getSecurityByTicker(input.symbol);
          if (security) {
            persistYahooPriceData(security.id, input.symbol, result).catch((err) =>
              console.error("Background persist error:", err)
            );
          }
        }

        return result;
      } catch (error) {
        console.error("Yahoo Finance chart error:", error);
        return null;
      }
    }),

  // Manual enrichment endpoint for batch operations
  enrichSecurity: protectedProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input, ctx }) => {
      const security = await db.getSecurityById(input.id);
      if (!security) {
        throw new Error("Security not found");
      }

      const result = await enrichSecurityData(security.id, security.ticker, security.assetClass);

      await db.logAudit({
        userId: ctx.user.id,
        action: "ENRICH_SECURITY",
        resource: "security",
        resourceId: security.id,
        details: `Enriched ${security.ticker}: ${result.priceRecordsPersisted} records from ${result.source}`,
      });

      return result;
    }),

  // Kafka event streaming endpoints
  getEvents: protectedProcedure
    .input(
      z.object({
        topic: z.string().optional(),
        fromTimestamp: z.string().optional(),
        toTimestamp: z.string().optional(),
        limit: z.number().default(100),
        offset: z.number().default(0),
      })
    )
    .query(async ({ input }) => {
      const consumer = getKafkaConsumer();
      return await consumer.consume({
        topic: input.topic,
        fromTimestamp: input.fromTimestamp ? new Date(input.fromTimestamp) : undefined,
        toTimestamp: input.toTimestamp ? new Date(input.toTimestamp) : undefined,
        limit: input.limit,
        offset: input.offset,
      });
    }),

  getEventsBySecurityId: protectedProcedure
    .input(
      z.object({
        securityId: z.string(),
        fromTimestamp: z.string().optional(),
        toTimestamp: z.string().optional(),
        limit: z.number().default(100),
        offset: z.number().default(0),
      })
    )
    .query(async ({ input }) => {
      const consumer = getKafkaConsumer();
      return await consumer.consumeBySecurityId(input.securityId, {
        fromTimestamp: input.fromTimestamp ? new Date(input.fromTimestamp) : undefined,
        toTimestamp: input.toTimestamp ? new Date(input.toTimestamp) : undefined,
        limit: input.limit,
        offset: input.offset,
      });
    }),

  getLatestPrices: protectedProcedure
    .input(
      z.object({
        securityIds: z.array(z.string()),
        limit: z.number().default(1),
      })
    )
    .query(async ({ input }) => {
      const consumer = getKafkaConsumer();
      const result = await consumer.getLatestPrices(input.securityIds, input.limit);
      
      // Convert Map to object for JSON serialization
      const obj: Record<string, any[]> = {};
      result.forEach((value, key) => {
        obj[key] = value;
      });
      return obj;
    }),

  getEventStats: protectedProcedure
    .input(z.object({ topic: z.string().optional() }))
    .query(async ({ input }) => {
      const consumer = getKafkaConsumer();
      return await consumer.getStats(input.topic);
    }),
});

// ============================================================================
// MAIN APP ROUTER
// ============================================================================

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Feature routers
  portfolio: portfolioRouter,
  esg: esgRouter,
  loan: loanRouter,
  rlAgent: rlAgentRouter,
  kafka: kafkaRouter,
  dataMesh: dataMeshRouter,
  mcp: mcpRouter,

  // Larry Operations AI
  larry: router({
    // Create new conversation
    createConversation: protectedProcedure
      .input(z.object({ title: z.string().optional() }))
      .mutation(async ({ ctx, input }) => {
        const conversationId = await createConversation(ctx.user.id, input.title);
        return { conversationId };
      }),

    // Get user's conversations
    getConversations: protectedProcedure.query(async ({ ctx }) => {
      return await getUserConversations(ctx.user.id);
    }),

    // Get messages for a conversation
    getMessages: protectedProcedure
      .input(z.object({ conversationId: z.string(), limit: z.number().optional() }))
      .query(async ({ input }) => {
        return await getMessages(input.conversationId, input.limit);
      }),

    // Send message to Larry
    sendMessage: protectedProcedure
      .input(
        z.object({
          conversationId: z.string(),
          message: z.string(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const response = await chatWithLarry({
          conversationId: input.conversationId,
          userMessage: input.message,
          userId: ctx.user.id,
        });
        return response;
      }),

    // Get conversation stats
    getStats: protectedProcedure
      .input(z.object({ conversationId: z.string() }))
      .query(async ({ input }) => {
        return await getConversationStats(input.conversationId);
      }),
  }),
  audit: auditRouter,
  securities: securitiesRouter,
});

export type AppRouter = typeof appRouter;
