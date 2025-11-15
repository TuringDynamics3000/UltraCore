/**
 * Larry Operations AI - Conversation Service
 * Event-sourced conversation management with full persistence
 */

import { eq, desc, and } from "drizzle-orm";
import { getDb } from "./db";
import { conversations, messages, toolExecutions, insights, conversationEmbeddings } from "../drizzle/schema";
import type { InsertConversation, InsertMessage, InsertToolExecution, InsertInsight } from "../drizzle/schema";
import { randomUUID } from "crypto";

// ============================================================================
// CONVERSATION MANAGEMENT
// ============================================================================

export async function createConversation(userId: number, title?: string): Promise<string> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const conversationId = randomUUID();
  const conversation: InsertConversation = {
    id: conversationId,
    userId,
    title: title || "New Conversation",
    status: "active",
    messageCount: 0,
  };

  await db.insert(conversations).values(conversation);
  return conversationId;
}

export async function getConversation(conversationId: string) {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(conversations)
    .where(eq(conversations.id, conversationId))
    .limit(1);

  return result[0] || null;
}

export async function getUserConversations(userId: number) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(conversations)
    .where(and(eq(conversations.userId, userId), eq(conversations.status, "active")))
    .orderBy(desc(conversations.updatedAt))
    .limit(50);
}

export async function archiveConversation(conversationId: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(conversations)
    .set({ status: "archived" })
    .where(eq(conversations.id, conversationId));
}

// ============================================================================
// MESSAGE MANAGEMENT
// ============================================================================

export async function addMessage(
  conversationId: string,
  role: "user" | "assistant" | "system" | "tool",
  content: string | null,
  options?: {
    toolCalls?: any[];
    toolCallId?: string;
    reasoning?: string;
    tokens?: number;
    model?: string;
  }
): Promise<string> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const messageId = randomUUID();
  const message: InsertMessage = {
    id: messageId,
    conversationId,
    role,
    content,
    toolCalls: options?.toolCalls,
    toolCallId: options?.toolCallId,
    reasoning: options?.reasoning,
    tokens: options?.tokens,
    model: options?.model,
  };

  await db.insert(messages).values(message);

  // Update conversation metadata
  await db
    .update(conversations)
    .set({
      messageCount: (await getMessageCount(conversationId)),
      lastMessageAt: new Date(),
    })
    .where(eq(conversations.id, conversationId));

  return messageId;
}

export async function getMessages(conversationId: string, limit: number = 100) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(messages)
    .where(eq(messages.conversationId, conversationId))
    .orderBy(messages.createdAt)
    .limit(limit);
}

export async function getMessageCount(conversationId: string): Promise<number> {
  const db = await getDb();
  if (!db) return 0;

  const result = await db
    .select()
    .from(messages)
    .where(eq(messages.conversationId, conversationId));

  return result.length;
}

// ============================================================================
// TOOL EXECUTION TRACKING
// ============================================================================

export async function createToolExecution(
  messageId: string,
  toolName: string,
  input: any
): Promise<string> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const executionId = randomUUID();
  const execution: InsertToolExecution = {
    id: executionId,
    messageId,
    toolName,
    input,
    status: "pending",
  };

  await db.insert(toolExecutions).values(execution);
  return executionId;
}

export async function completeToolExecution(
  executionId: string,
  output: any,
  duration: number
) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(toolExecutions)
    .set({
      output,
      duration,
      status: "success",
      completedAt: new Date(),
    })
    .where(eq(toolExecutions.id, executionId));
}

export async function failToolExecution(executionId: string, error: string, duration: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(toolExecutions)
    .set({
      error,
      duration,
      status: "error",
      completedAt: new Date(),
    })
    .where(eq(toolExecutions.id, executionId));
}

export async function getToolExecutions(messageId: string) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(toolExecutions)
    .where(eq(toolExecutions.messageId, messageId))
    .orderBy(toolExecutions.createdAt);
}

// ============================================================================
// INSIGHTS MANAGEMENT
// ============================================================================

export async function createInsight(
  type: "anomaly" | "opportunity" | "risk" | "recommendation",
  severity: "low" | "medium" | "high" | "critical",
  title: string,
  description: string,
  data?: any,
  source?: string
): Promise<string> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const insightId = randomUUID();
  const insight: InsertInsight = {
    id: insightId,
    type,
    severity,
    title,
    description,
    data,
    source,
    acknowledged: false,
  };

  await db.insert(insights).values(insight);
  return insightId;
}

export async function getUnacknowledgedInsights() {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(insights)
    .where(eq(insights.acknowledged, false))
    .orderBy(desc(insights.createdAt))
    .limit(50);
}

export async function acknowledgeInsight(insightId: string, userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(insights)
    .set({
      acknowledged: true,
      acknowledgedBy: userId,
      acknowledgedAt: new Date(),
    })
    .where(eq(insights.id, insightId));
}

// ============================================================================
// CONVERSATION CONTEXT & SUMMARIZATION
// ============================================================================

export async function getConversationContext(conversationId: string, maxMessages: number = 20) {
  const db = await getDb();
  if (!db) return { messages: [], summary: null };

  const conversation = await getConversation(conversationId);
  const recentMessages = await db
    .select()
    .from(messages)
    .where(eq(messages.conversationId, conversationId))
    .orderBy(desc(messages.createdAt))
    .limit(maxMessages);

  return {
    messages: recentMessages.reverse(),
    summary: conversation?.summary || null,
  };
}

export async function updateConversationSummary(conversationId: string, summary: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(conversations)
    .set({ summary })
    .where(eq(conversations.id, conversationId));
}

export async function updateConversationTitle(conversationId: string, title: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(conversations)
    .set({ title })
    .where(eq(conversations.id, conversationId));
}

// ============================================================================
// EMBEDDINGS FOR RAG
// ============================================================================

export async function storeEmbedding(
  conversationId: string,
  messageId: string | null,
  embedding: number[],
  content: string,
  metadata?: any
) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const embeddingId = randomUUID();
  await db.insert(conversationEmbeddings).values({
    id: embeddingId,
    conversationId,
    messageId,
    embedding: JSON.stringify(embedding),
    content,
    metadata,
  });

  return embeddingId;
}

// ============================================================================
// ANALYTICS
// ============================================================================

export async function getConversationStats(conversationId: string) {
  const db = await getDb();
  if (!db) return null;

  const conversation = await getConversation(conversationId);
  if (!conversation) return null;

  const allMessages = await getMessages(conversationId);
  const executions = await Promise.all(
    allMessages.map((msg) => getToolExecutions(msg.id))
  );

  const totalTokens = allMessages.reduce((sum, msg) => sum + (msg.tokens || 0), 0);
  const totalToolCalls = executions.flat().length;
  const avgResponseTime =
    executions.flat().reduce((sum, exec) => sum + (exec.duration || 0), 0) /
    (totalToolCalls || 1);

  return {
    messageCount: allMessages.length,
    totalTokens,
    totalToolCalls,
    avgResponseTime,
    createdAt: conversation.createdAt,
    lastMessageAt: conversation.lastMessageAt,
  };
}
