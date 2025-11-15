/**
 * Kafka Consumer API for RL Agents
 * Provides event streaming and replay capabilities
 */

import { getDb } from "./db";
import { kafkaEvents } from "../drizzle/schema";
import { eq, gte, lte, and, desc, asc } from "drizzle-orm";
import type { SecurityEvent } from "./kafka-publisher";

export interface ConsumeOptions {
  topic?: string;
  fromTimestamp?: Date;
  toTimestamp?: Date;
  limit?: number;
  offset?: number;
  orderBy?: "asc" | "desc";
}

export interface EventBatch {
  events: SecurityEvent[];
  hasMore: boolean;
  nextOffset: number;
  totalCount: number;
}

/**
 * Kafka Consumer for RL Agents
 */
export class KafkaConsumer {
  /**
   * Consume events from a topic
   */
  async consume(options: ConsumeOptions = {}): Promise<EventBatch> {
    const db = await getDb();
    if (!db) {
      return { events: [], hasMore: false, nextOffset: 0, totalCount: 0 };
    }

    const {
      topic,
      fromTimestamp,
      toTimestamp,
      limit = 100,
      offset = 0,
      orderBy = "asc",
    } = options;

    // Build query conditions
    const conditions = [];
    if (topic) {
      conditions.push(eq(kafkaEvents.topic, topic));
    }
    if (fromTimestamp) {
      conditions.push(gte(kafkaEvents.timestamp, fromTimestamp));
    }
    if (toTimestamp) {
      conditions.push(lte(kafkaEvents.timestamp, toTimestamp));
    }

    // Fetch events
    const query = db
      .select()
      .from(kafkaEvents)
      .where(conditions.length > 0 ? and(...conditions) : undefined)
      .limit(limit + 1) // Fetch one extra to check if there are more
      .offset(offset);

    // Apply ordering
    const results = await (orderBy === "desc"
      ? query.orderBy(desc(kafkaEvents.timestamp))
      : query.orderBy(asc(kafkaEvents.timestamp)));

    // Check if there are more events
    const hasMore = results.length > limit;
    const events = results.slice(0, limit);

    // Parse event values
    const parsedEvents: SecurityEvent[] = events.map((event) => {
      try {
        return typeof event.value === "string"
          ? JSON.parse(event.value)
          : event.value;
      } catch {
        return event.value as any;
      }
    });

    return {
      events: parsedEvents,
      hasMore,
      nextOffset: offset + events.length,
      totalCount: events.length,
    };
  }

  /**
   * Consume events by security ID
   */
  async consumeBySecurityId(
    securityId: string,
    options: Omit<ConsumeOptions, "topic"> = {}
  ): Promise<EventBatch> {
    const db = await getDb();
    if (!db) {
      return { events: [], hasMore: false, nextOffset: 0, totalCount: 0 };
    }

    const {
      fromTimestamp,
      toTimestamp,
      limit = 100,
      offset = 0,
      orderBy = "asc",
    } = options;

    // Build query conditions
    const conditions = [eq(kafkaEvents.key, securityId)];
    if (fromTimestamp) {
      conditions.push(gte(kafkaEvents.timestamp, fromTimestamp));
    }
    if (toTimestamp) {
      conditions.push(lte(kafkaEvents.timestamp, toTimestamp));
    }

    // Fetch events
    const query = db
      .select()
      .from(kafkaEvents)
      .where(and(...conditions))
      .limit(limit + 1)
      .offset(offset);

    const results = await (orderBy === "desc"
      ? query.orderBy(desc(kafkaEvents.timestamp))
      : query.orderBy(asc(kafkaEvents.timestamp)));

    const hasMore = results.length > limit;
    const events = results.slice(0, limit);

    const parsedEvents: SecurityEvent[] = events.map((event) => {
      try {
        return typeof event.value === "string"
          ? JSON.parse(event.value)
          : event.value;
      } catch {
        return event.value as any;
      }
    });

    return {
      events: parsedEvents,
      hasMore,
      nextOffset: offset + events.length,
      totalCount: events.length,
    };
  }

  /**
   * Get latest events for multiple securities
   */
  async getLatestPrices(
    securityIds: string[],
    limit: number = 1
  ): Promise<Map<string, SecurityEvent[]>> {
    const db = await getDb();
    if (!db) {
      return new Map();
    }

    const result = new Map<string, SecurityEvent[]>();

    for (const securityId of securityIds) {
      const events = await db
        .select()
        .from(kafkaEvents)
        .where(
          and(
            eq(kafkaEvents.key, securityId),
            eq(kafkaEvents.topic, "securities.prices")
          )
        )
        .orderBy(desc(kafkaEvents.timestamp))
        .limit(limit);

      const parsedEvents: SecurityEvent[] = events.map((event) => {
        try {
          return typeof event.value === "string"
            ? JSON.parse(event.value)
            : event.value;
        } catch {
          return event.value as any;
        }
      });

      result.set(securityId, parsedEvents);
    }

    return result;
  }

  /**
   * Replay events for backtesting
   */
  async replay(
    fromTimestamp: Date,
    toTimestamp: Date,
    topic?: string,
    batchSize: number = 1000
  ): Promise<AsyncGenerator<SecurityEvent[], void, unknown>> {
    const db = await getDb();
    if (!db) {
      return (async function* () {})();
    }

    const self = this;

    return (async function* () {
      let offset = 0;
      let hasMore = true;

      while (hasMore) {
        const batch = await self.consume({
          topic,
          fromTimestamp,
          toTimestamp,
          limit: batchSize,
          offset,
          orderBy: "asc",
        });

        if (batch.events.length > 0) {
          yield batch.events;
        }

        hasMore = batch.hasMore;
        offset = batch.nextOffset;
      }
    })();
  }

  /**
   * Get event statistics
   */
  async getStats(topic?: string): Promise<{
    totalEvents: number;
    oldestEvent?: Date;
    newestEvent?: Date;
    topicBreakdown: Record<string, number>;
  }> {
    const db = await getDb();
    if (!db) {
      return { totalEvents: 0, topicBreakdown: {} };
    }

    // Get all events (or filtered by topic)
    const conditions = topic ? [eq(kafkaEvents.topic, topic)] : [];
    const events = await db
      .select()
      .from(kafkaEvents)
      .where(conditions.length > 0 ? and(...conditions) : undefined);

    const totalEvents = events.length;
    const oldestEvent = events.length > 0
      ? new Date(Math.min(...events.map((e) => e.timestamp.getTime())))
      : undefined;
    const newestEvent = events.length > 0
      ? new Date(Math.max(...events.map((e) => e.timestamp.getTime())))
      : undefined;

    // Topic breakdown
    const topicBreakdown: Record<string, number> = {};
    for (const event of events) {
      topicBreakdown[event.topic] = (topicBreakdown[event.topic] || 0) + 1;
    }

    return {
      totalEvents,
      oldestEvent,
      newestEvent,
      topicBreakdown,
    };
  }
}

// Singleton instance
let consumerInstance: KafkaConsumer | null = null;

export function getKafkaConsumer(): KafkaConsumer {
  if (!consumerInstance) {
    consumerInstance = new KafkaConsumer();
  }
  return consumerInstance;
}
