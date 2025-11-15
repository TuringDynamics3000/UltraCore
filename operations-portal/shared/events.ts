/**
 * Kafka Event Schema for UltraCore Securities Register
 * 
 * Event Sourcing Pattern:
 * - All security changes are captured as immutable events
 * - Events are stored in Kafka topics for audit trail
 * - Database state is derived from event stream (materialized view)
 * - Enables time-travel queries and regulatory compliance
 */

export type EventType =
  | 'SecurityCreated'
  | 'SecurityUpdated'
  | 'PriceUpdated'
  | 'CorporateActionAnnounced'
  | 'IdentifierMapped'
  | 'SecurityDelisted'
  | 'DividendAnnounced'
  | 'StockSplitAnnounced';

export interface BaseEvent {
  eventId: string;
  eventType: EventType;
  timestamp: Date;
  source: string; // 'user', 'zeta-agent', 'openfigi-api', 'manual'
  userId?: string;
  metadata?: Record<string, unknown>;
}

export interface SecurityCreatedEvent extends BaseEvent {
  eventType: 'SecurityCreated';
  data: {
    securityId: string;
    ticker: string;
    name: string;
    assetClass: 'equity' | 'etf' | 'bond' | 'commodity' | 'derivative';
    exchange: string;
    currency: string;
    isin?: string;
    sedol?: string;
    cusip?: string;
    figi?: string;
    sector?: string;
    industry?: string;
    country: string;
    listingDate?: Date;
  };
}

export interface SecurityUpdatedEvent extends BaseEvent {
  eventType: 'SecurityUpdated';
  data: {
    securityId: string;
    updates: Partial<SecurityCreatedEvent['data']>;
    previousValues: Partial<SecurityCreatedEvent['data']>;
  };
}

export interface PriceUpdatedEvent extends BaseEvent {
  eventType: 'PriceUpdated';
  data: {
    securityId: string;
    ticker: string;
    price: number;
    currency: string;
    volume?: number;
    source: string; // 'yahoo-finance', 'asx-api', 'manual'
  };
}

export interface CorporateActionAnnouncedEvent extends BaseEvent {
  eventType: 'CorporateActionAnnounced';
  data: {
    securityId: string;
    ticker: string;
    actionType: 'dividend' | 'split' | 'merger' | 'spinoff' | 'delisting';
    announcementDate: Date;
    effectiveDate: Date;
    details: Record<string, unknown>;
  };
}

export interface IdentifierMappedEvent extends BaseEvent {
  eventType: 'IdentifierMapped';
  data: {
    securityId: string;
    ticker: string;
    identifierType: 'ISIN' | 'CUSIP' | 'SEDOL' | 'FIGI';
    identifierValue: string;
    source: string; // 'openfigi-api', 'manual', 'zeta-agent'
    confidence: number; // 0.0 to 1.0
  };
}

export interface SecurityDelistedEvent extends BaseEvent {
  eventType: 'SecurityDelisted';
  data: {
    securityId: string;
    ticker: string;
    delistingDate: Date;
    reason?: string;
  };
}

export interface DividendAnnouncedEvent extends BaseEvent {
  eventType: 'DividendAnnounced';
  data: {
    securityId: string;
    ticker: string;
    dividendAmount: number;
    currency: string;
    exDividendDate: Date;
    paymentDate: Date;
    recordDate: Date;
    frequency: 'quarterly' | 'semi-annual' | 'annual' | 'special';
  };
}

export interface StockSplitAnnouncedEvent extends BaseEvent {
  eventType: 'StockSplitAnnounced';
  data: {
    securityId: string;
    ticker: string;
    splitRatio: string; // e.g., "2:1", "3:2"
    effectiveDate: Date;
  };
}

export type SecurityEvent =
  | SecurityCreatedEvent
  | SecurityUpdatedEvent
  | PriceUpdatedEvent
  | CorporateActionAnnouncedEvent
  | IdentifierMappedEvent
  | SecurityDelistedEvent
  | DividendAnnouncedEvent
  | StockSplitAnnouncedEvent;

/**
 * Kafka Topics for Securities Register
 */
export const KAFKA_TOPICS = {
  SECURITIES: 'ultracore.securities',
  PRICES: 'ultracore.securities.prices',
  CORPORATE_ACTIONS: 'ultracore.securities.corporate-actions',
  IDENTIFIERS: 'ultracore.securities.identifiers',
} as const;
