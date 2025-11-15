/**
 * Data Enrichment Service for ML/RL Pipeline
 * Automatically persists market data from APIs to database for training
 */

import { getDb } from "./db";
import { priceHistory } from "../drizzle/schema";
import { callDataApi } from "./_core/dataApi";

/**
 * Persist Yahoo Finance price data to database
 */
export async function persistYahooPriceData(
  securityId: string,
  ticker: string,
  chartData: any
): Promise<number> {
  const db = await getDb();
  if (!db || !chartData?.chart?.result?.[0]) return 0;

  const result = chartData.chart.result[0];
  const timestamps = result.timestamp || [];
  const quotes = result.indicators?.quote?.[0];
  const meta = result.meta;

  if (!quotes || !timestamps.length) return 0;

  const records = [];
  for (let i = 0; i < timestamps.length; i++) {
    const timestamp = new Date(timestamps[i] * 1000);
    const date = timestamp.toISOString().split("T")[0];

    records.push({
      id: `${securityId}-${timestamps[i]}`,
      securityId,
      ticker,
      date: new Date(date),
      timestamp,
      open: quotes.open?.[i]?.toString() || null,
      high: quotes.high?.[i]?.toString() || null,
      low: quotes.low?.[i]?.toString() || null,
      close: quotes.close?.[i]?.toString() || null,
      volume: quotes.volume?.[i] || null,
      adjClose: result.indicators?.adjclose?.[0]?.adjclose?.[i]?.toString() || null,
      currency: meta.currency || "USD",
      source: "yahoo_finance",
      interval: meta.dataGranularity || "1d",
    });
  }

  try {
    // Batch insert with ON DUPLICATE KEY UPDATE
    for (const record of records) {
      await db
        .insert(priceHistory)
        .values(record)
        .onDuplicateKeyUpdate({ set: { close: record.close } });
    }

    console.log(`[Enrichment] Persisted ${records.length} price records for ${ticker}`);
    return records.length;
  } catch (error) {
    console.error(`[Enrichment] Error persisting price data for ${ticker}:`, error);
    return 0;
  }
}

/**
 * Enrich security with latest market data
 */
export async function enrichSecurityData(
  securityId: string,
  ticker: string,
  assetClass: string
): Promise<{
  priceRecordsPersisted: number;
  source: string;
}> {
  let priceRecordsPersisted = 0;
  let source = "none";

  try {
    // For equities, use Yahoo Finance
    if (assetClass === "equity") {
      const chartData = await callDataApi("YahooFinance/get_stock_chart", {
        query: {
          symbol: ticker,
          region: "US",
          interval: "1d",
          range: "1mo",
          includeAdjustedClose: true,
        },
      });

      if (chartData) {
        priceRecordsPersisted = await persistYahooPriceData(securityId, ticker, chartData);
        source = "yahoo_finance";
      }
    }

    return {
      priceRecordsPersisted,
      source,
    };
  } catch (error) {
    console.error(`[Enrichment] Error enriching ${ticker}:`, error);
    return {
      priceRecordsPersisted: 0,
      source: "error",
    };
  }
}
