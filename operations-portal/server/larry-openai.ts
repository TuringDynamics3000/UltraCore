/**
 * Larry Operations AI - OpenAI Integration
 * Latest structured outputs and function calling with GPT-4
 */

import { invokeLLM } from "./_core/llm";
import type { Message as OpenAIMessage } from "./_core/llm";
import {
  addMessage,
  createToolExecution,
  completeToolExecution,
  failToolExecution,
  getConversationContext,
  updateConversationTitle,
} from "./larry-conversation";

// ============================================================================
// SYSTEM PROMPT
// ============================================================================

const LARRY_SYSTEM_PROMPT = `You are Larry, the AI operations assistant for UltraCore wealth management platform. You have access to comprehensive operational data including:

**Your Capabilities:**
- Query 454 securities across equities, crypto, art, wine, and real estate
- Analyze 12 active portfolios managed by 5 RL agents (Alpha, Beta, Gamma, Delta, Epsilon)
- Monitor real-time Kafka event streams (1.2k events/sec)
- Access 137 data products in the Data Mesh including 72 ASX ETFs
- Track 48 active UltraGrow loans ($2.4M total)
- Review ESG metrics (85% coverage)
- Monitor RL agent training progress and performance
- Execute SQL queries on DuckDB WASM for analytics

**Your Personality:**
- Professional yet approachable
- Data-driven and precise
- Proactive in surfacing insights
- Explain complex financial concepts clearly
- Always cite data sources

**Response Format:**
- Use markdown for formatting
- Include relevant metrics and numbers
- Provide actionable recommendations
- Show reasoning for complex analyses
- Link to relevant portal pages when helpful

**Current Context:**
- Total AUM: $45.2M
- System Health: 98.5%
- Active Portfolios: 12
- Securities Universe: 454 instruments
- Event Rate: 1.2k/sec

When users ask questions, leverage your tools to provide accurate, data-backed answers. Always explain your reasoning and cite specific data points.`;

// ============================================================================
// TOOL DEFINITIONS (MCP-style)
// ============================================================================

export const LARRY_TOOLS = [
  {
    type: "function" as const,
    function: {
      name: "query_securities",
      description: "Search and retrieve information about securities in the global register. Supports filtering by ticker, asset class, sector, or market cap.",
      parameters: {
        type: "object",
        properties: {
          search: {
            type: "string",
            description: "Search term (ticker, name, ISIN, or contract address)",
          },
          assetClass: {
            type: "string",
            enum: ["equity", "crypto", "bond", "etf", "art", "wine", "real_estate"],
            description: "Filter by asset class",
          },
          limit: {
            type: "number",
            description: "Maximum number of results to return (default: 10)",
          },
        },
        required: [],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_security_details",
      description: "Get comprehensive details for a specific security including price history, fundamentals, and ESG ratings.",
      parameters: {
        type: "object",
        properties: {
          ticker: {
            type: "string",
            description: "Security ticker symbol (e.g., AAPL, BTC-USD)",
          },
        },
        required: ["ticker"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "query_portfolios",
      description: "Retrieve portfolio information including holdings, performance metrics, and agent assignments.",
      parameters: {
        type: "object",
        properties: {
          agent: {
            type: "string",
            enum: ["alpha", "beta", "gamma", "delta", "epsilon"],
            description: "Filter by RL agent",
          },
          status: {
            type: "string",
            enum: ["active", "paused", "closed"],
            description: "Filter by portfolio status",
          },
        },
        required: [],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_portfolio_details",
      description: "Get detailed information about a specific portfolio including holdings breakdown and performance history.",
      parameters: {
        type: "object",
        properties: {
          portfolioId: {
            type: "string",
            description: "Portfolio ID",
          },
        },
        required: ["portfolioId"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "query_kafka_events",
      description: "Search recent Kafka events for market data updates, security price changes, or system events.",
      parameters: {
        type: "object",
        properties: {
          topic: {
            type: "string",
            description: "Kafka topic name",
          },
          eventType: {
            type: "string",
            enum: ["SecurityPriceUpdated", "SecurityCreated", "CorporateActionAnnounced"],
            description: "Type of event",
          },
          limit: {
            type: "number",
            description: "Maximum number of events to return (default: 20)",
          },
        },
        required: [],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "query_rl_agents",
      description: "Get information about RL trading agents including training status, performance metrics, and portfolio assignments.",
      parameters: {
        type: "object",
        properties: {
          agentName: {
            type: "string",
            enum: ["alpha", "beta", "gamma", "delta", "epsilon"],
            description: "Specific agent to query",
          },
        },
        required: [],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_training_metrics",
      description: "Retrieve training metrics for an RL agent including reward curves, episode progress, and Sharpe ratios.",
      parameters: {
        type: "object",
        properties: {
          agentName: {
            type: "string",
            enum: ["alpha", "beta", "gamma", "delta", "epsilon"],
            description: "Agent name",
          },
          limit: {
            type: "number",
            description: "Number of recent episodes to return (default: 100)",
          },
        },
        required: ["agentName"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "query_data_products",
      description: "Search the Data Mesh catalog for data products including ETFs, market data, and analytics datasets.",
      parameters: {
        type: "object",
        properties: {
          search: {
            type: "string",
            description: "Search term for product name or description",
          },
          category: {
            type: "string",
            description: "Filter by category (e.g., 'ETF', 'Market Data', 'Analytics')",
          },
        },
        required: [],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "execute_sql_query",
      description: "Execute a SQL query on DuckDB WASM to analyze Parquet files in the Data Mesh. Use for complex analytics.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "SQL query to execute (SELECT statements only)",
          },
          dataProductId: {
            type: "string",
            description: "Data product ID to query against",
          },
        },
        required: ["query", "dataProductId"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_insights",
      description: "Retrieve proactive insights generated by the system including anomalies, opportunities, and risks.",
      parameters: {
        type: "object",
        properties: {
          type: {
            type: "string",
            enum: ["anomaly", "opportunity", "risk", "recommendation"],
            description: "Filter by insight type",
          },
          severity: {
            type: "string",
            enum: ["low", "medium", "high", "critical"],
            description: "Filter by severity level",
          },
        },
        required: [],
      },
    },
  },
];

// ============================================================================
// CHAT COMPLETION WITH STREAMING
// ============================================================================

export interface LarryChatOptions {
  conversationId: string;
  userMessage: string;
  userId: number;
  onToken?: (token: string) => void;
  onToolCall?: (toolName: string, args: any) => void;
  onComplete?: (response: string, reasoning?: string) => void;
}

export async function chatWithLarry(options: LarryChatOptions) {
  const { conversationId, userMessage, userId, onToken, onToolCall, onComplete } = options;

  // Add user message to conversation
  await addMessage(conversationId, "user", userMessage);

  // Get conversation context
  const context = await getConversationContext(conversationId, 20);

  // Build messages array for OpenAI
  const openaiMessages: OpenAIMessage[] = [
    { role: "system", content: LARRY_SYSTEM_PROMPT },
    ...context.messages.map((msg) => ({
      role: msg.role as "user" | "assistant" | "system",
      content: msg.content || "",
    })),
  ];

  // Call OpenAI with function calling
  const response = await invokeLLM({
    messages: openaiMessages,
    tools: LARRY_TOOLS,
    tool_choice: "auto",
  });

  const assistantMessage = response.choices[0].message;
  const toolCalls = assistantMessage.tool_calls;

  // Handle tool calls if present
  if (toolCalls && toolCalls.length > 0) {
    const toolResults = [];

    for (const toolCall of toolCalls) {
      const toolName = toolCall.function.name;
      const toolArgs = JSON.parse(toolCall.function.arguments);

      if (onToolCall) {
        onToolCall(toolName, toolArgs);
      }

      // Execute tool and track execution
      const executionId = await createToolExecution(
        conversationId,
        toolName,
        toolArgs
      );

      const startTime = Date.now();
      try {
        const toolResult = await executeTool(toolName, toolArgs);
        const duration = Date.now() - startTime;

        await completeToolExecution(executionId, toolResult, duration);
        toolResults.push({
          tool_call_id: toolCall.id,
          role: "tool" as const,
          content: JSON.stringify(toolResult),
        });
      } catch (error: any) {
        const duration = Date.now() - startTime;
        await failToolExecution(executionId, error.message, duration);
        toolResults.push({
          tool_call_id: toolCall.id,
          role: "tool" as const,
          content: JSON.stringify({ error: error.message }),
        });
      }
    }

    // Add tool call message
    await addMessage(conversationId, "assistant", null, {
      toolCalls: toolCalls.map((tc) => ({
        id: tc.id,
        name: tc.function.name,
        arguments: tc.function.arguments,
      })),
      model: response.model,
    });

    // Add tool results and get final response
    const finalMessages = [
      ...openaiMessages,
      {
        role: "assistant" as const,
        content: assistantMessage.content,
        tool_calls: toolCalls,
      },
      ...toolResults,
    ];

    const finalResponse = await invokeLLM({
      messages: finalMessages,
      tools: LARRY_TOOLS,
      tool_choice: "none",
    });

    const finalContent = finalResponse.choices[0].message.content || "";

    // Save final response
    await addMessage(conversationId, "assistant", finalContent, {
      model: finalResponse.model,
      tokens: finalResponse.usage?.total_tokens,
    });

    // Generate conversation title if first exchange
    if (context.messages.length === 0) {
      const title = await generateConversationTitle(userMessage, finalContent);
      await updateConversationTitle(conversationId, title);
    }

    if (onComplete) {
      onComplete(finalContent);
    }

    return {
      content: finalContent,
      toolCalls: toolCalls.map((tc) => tc.function.name),
      model: finalResponse.model,
      tokens: finalResponse.usage?.total_tokens,
    };
  } else {
    // No tool calls, just save the response
    const rawContent = assistantMessage.content || "";
    const content = typeof rawContent === 'string' ? rawContent : JSON.stringify(rawContent);

    await addMessage(conversationId, "assistant", content, {
      model: response.model,
      tokens: response.usage?.total_tokens,
    });

    // Generate conversation title if first exchange
    if (context.messages.length === 0) {
      const title = await generateConversationTitle(userMessage, content);
      await updateConversationTitle(conversationId, title);
    }

    if (onComplete && typeof content === 'string') {
      onComplete(content);
    }

    return {
      content,
      toolCalls: [],
      model: response.model,
      tokens: response.usage?.total_tokens,
    };
  }
}

// ============================================================================
// TOOL EXECUTION ROUTER
// ============================================================================

import { executeLarryTool } from "./larry-tools";

async function executeTool(toolName: string, args: any): Promise<any> {
  return await executeLarryTool(toolName, args);
}

// ============================================================================
// CONVERSATION TITLE GENERATION
// ============================================================================

async function generateConversationTitle(
  userMessage: string,
  assistantResponse: string
): Promise<string> {
  try {
    const response = await invokeLLM({
      messages: [
        {
          role: "system",
          content:
            "Generate a concise 3-5 word title for this conversation. Return only the title, no quotes or explanation.",
        },
        {
          role: "user",
          content: `User: ${userMessage}\n\nAssistant: ${assistantResponse}`,
        },
      ],
    });

    const content = response.choices[0].message.content;
    if (typeof content === 'string') {
      return content.trim() || "New Conversation";
    }
    return "New Conversation";
  } catch (error) {
    console.error("[Larry] Failed to generate title:", error);
    return "New Conversation";
  }
}
