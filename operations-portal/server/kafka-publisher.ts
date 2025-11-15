/**
 * Kafka Event Publisher Service
 * Publishes market data events for consumption by RL agents
 */

import { getDb } from "./db";
import { kafkaEvents } from "../drizzle/schema";

// Event Types
export type SecurityEventType =
  | "security.created"
  | "security.updated"
  | "security.price.updated"
  | "security.corporate_action"
  | "security.esg.updated";

export interface SecurityPriceUpdatedEvent {
  type: "security.price.updated";
  timestamp: string;
  securityId: string;
  ticker: string;
  price: {
    current: number;
    previous?: number;
    change?: number;
    changePercent?: number;
  };
  volume?: number;
  marketCap?: number;
  currency: string;
  source: string;
  exchange?: string;
}

export interface SecurityCreatedEvent {
  type: "security.created";
  timestamp: string;
  securityId: string;
  ticker: string;
  name: string;
  assetClass: string;
  exchange?: string;
  currency: string;
}

export interface CorporateActionEvent {
  type: "security.corporate_action";
  timestamp: string;
  securityId: string;
  ticker: string;
  actionType: "dividend" | "split" | "merger" | "acquisition" | "spinoff";
  details: Record<string, any>;
}

export type SecurityEvent =
  | SecurityPriceUpdatedEvent
  | SecurityCreatedEvent
  | CorporateActionEvent;

/**
 * Kafka Event Publisher
 */
export class KafkaPublisher {
  private eventBuffer: SecurityEvent[] = [];
  private readonly BATCH_SIZE = 100;
  private readonly FLUSH_INTERVAL = 5000; // 5 seconds
  private flushTimer: NodeJS.Timeout | null = null;

  constructor() {
    // Start auto-flush timer
    this.startAutoFlush();
  }

  /**
   * Publish a single event
   */
  async publish(event: SecurityEvent): Promise<void> {
    this.eventBuffer.push(event);

    // Flush if buffer is full
    if (this.eventBuffer.length >= this.BATCH_SIZE) {
      await this.flush();
    }
  }

  /**
   * Publish multiple events at once
   */
  async publishBatch(events: SecurityEvent[]): Promise<void> {
    this.eventBuffer.push(...events);

    // Flush if buffer is full
    if (this.eventBuffer.length >= this.BATCH_SIZE) {
      await this.flush();
    }
  }

  /**
   * Flush buffered events to database
   */
  async flush(): Promise<number> {
    if (this.eventBuffer.length === 0) return 0;

    const db = await getDb();
    if (!db) {
      console.error("[Kafka] Database unavailable, dropping events");
      this.eventBuffer = [];
      return 0;
    }

    const eventsToFlush = [...this.eventBuffer];
    this.eventBuffer = [];

    try {
      // Insert events in batches
      for (const event of eventsToFlush) {
        const topic = this.getTopicForEvent(event.type);
        const key = this.getKeyForEvent(event);

        await db.insert(kafkaEvents).values({
          id: `${event.type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          topic,
          key,
          value: JSON.stringify(event),
          partition: 0,
          offset: Date.now(),
          timestamp: new Date(event.timestamp),
        });
      }

      console.log(`[Kafka] Flushed ${eventsToFlush.length} events`);
      return eventsToFlush.length;
    } catch (error) {
      console.error("[Kafka] Error flushing events:", error);
      return 0;
    }
  }

  /**
   * Get Kafka topic for event type
   */
  private getTopicForEvent(eventType: SecurityEventType): string {
    const topicMap: Record<SecurityEventType, string> = {
      "security.created": "securities.lifecycle",
      "security.updated": "securities.lifecycle",
      "security.price.updated": "securities.prices",
      "security.corporate_action": "securities.corporate_actions",
      "security.esg.updated": "securities.esg",
    };

    return topicMap[eventType] || "securities.general";
  }

  /**
   * Get Kafka key for event (used for partitioning)
   */
  private getKeyForEvent(event: SecurityEvent): string {
    return event.securityId;
  }

  /**
   * Start auto-flush timer
   */
  private startAutoFlush(): void {
    this.flushTimer = setInterval(() => {
      this.flush().catch((err) => console.error("[Kafka] Auto-flush error:", err));
    }, this.FLUSH_INTERVAL);
  }

  /**
   * Stop auto-flush timer
   */
  stop(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }
}

// Singleton instance
let publisherInstance: KafkaPublisher | null = null;

export function getKafkaPublisher(): KafkaPublisher {
  if (!publisherInstance) {
    publisherInstance = new KafkaPublisher();
  }
  return publisherInstance;
}

/**
 * Helper function to publish price update event
 */
export async function publishPriceUpdate(params: {
  securityId: string;
  ticker: string;
  price: number;
  previousPrice?: number;
  volume?: number;
  marketCap?: number;
  currency: string;
  source: string;
  exchange?: string;
}): Promise<void> {
  const publisher = getKafkaPublisher();

  const event: SecurityPriceUpdatedEvent = {
    type: "security.price.updated",
    timestamp: new Date().toISOString(),
    securityId: params.securityId,
    ticker: params.ticker,
    price: {
      current: params.price,
      previous: params.previousPrice,
      change: params.previousPrice ? params.price - params.previousPrice : undefined,
      changePercent: params.previousPrice
        ? ((params.price - params.previousPrice) / params.previousPrice) * 100
        : undefined,
    },
    volume: params.volume,
    marketCap: params.marketCap,
    currency: params.currency,
    source: params.source,
    exchange: params.exchange,
  };

  await publisher.publish(event);
}

/**
 * Helper function to publish security created event
 */
export async function publishSecurityCreated(params: {
  securityId: string;
  ticker: string;
  name: string;
  assetClass: string;
  exchange?: string;
  currency: string;
}): Promise<void> {
  const publisher = getKafkaPublisher();

  const event: SecurityCreatedEvent = {
    type: "security.created",
    timestamp: new Date().toISOString(),
    securityId: params.securityId,
    ticker: params.ticker,
    name: params.name,
    assetClass: params.assetClass,
    exchange: params.exchange,
    currency: params.currency,
  };

  await publisher.publish(event);
}

/**
 * Helper function to publish corporate action event
 */
export async function publishCorporateAction(params: {
  securityId: string;
  ticker: string;
  actionType: "dividend" | "split" | "merger" | "acquisition" | "spinoff";
  details: Record<string, any>;
}): Promise<void> {
  const publisher = getKafkaPublisher();

  const event: CorporateActionEvent = {
    type: "security.corporate_action",
    timestamp: new Date().toISOString(),
    securityId: params.securityId,
    ticker: params.ticker,
    actionType: params.actionType,
    details: params.details,
  };

  await publisher.publish(event);
}
