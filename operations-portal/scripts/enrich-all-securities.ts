/**
 * Batch Securities Enrichment Script
 * Populates securities register with 5 years of historical data from Yahoo Finance and Fiscal.ai
 * 
 * Usage: pnpm tsx scripts/enrich-all-securities.ts
 */

import { getDb } from "../server/db";
import { securities, priceHistory } from "../drizzle/schema";
import { callDataApi } from "../server/_core/dataApi";
import { fiscalAI } from "../server/fiscal-ai";
import { eq } from "drizzle-orm";

interface EnrichmentResult {
  ticker: string;
  success: boolean;
  priceRecords: number;
  profileUpdated: boolean;
  error?: string;
}

/**
 * Fetch and persist 5 years of price data from Yahoo Finance
 */
async function enrichPriceData(
  securityId: string,
  ticker: string,
  currency: string
): Promise<{ success: boolean; recordCount: number; error?: string }> {
  try {
    console.log(`  📊 Fetching 5-year price history for ${ticker}...`);

    const chartData = await callDataApi("YahooFinance/get_stock_chart", {
      query: {
        symbol: ticker,
        region: "US",
        interval: "1d",
        range: "5y", // 5 years of data
        includeAdjustedClose: true,
        events: "div,split",
      },
    });

    if (!chartData || !(chartData as any)?.chart?.result?.[0]) {
      return { success: false, recordCount: 0, error: "No data returned" };
    }

    const result = (chartData as any).chart.result[0];
    const timestamps = result.timestamp || [];
    const quotes = result.indicators?.quote?.[0];
    const meta = result.meta;

    if (!quotes || !timestamps.length) {
      return { success: false, recordCount: 0, error: "Empty dataset" };
    }

    const db = await getDb();
    if (!db) {
      return { success: false, recordCount: 0, error: "Database unavailable" };
    }

    let insertedCount = 0;
    const batchSize = 100;

    for (let i = 0; i < timestamps.length; i += batchSize) {
      const batch = [];
      const end = Math.min(i + batchSize, timestamps.length);

      for (let j = i; j < end; j++) {
        const timestamp = new Date(timestamps[j] * 1000);
        const date = timestamp.toISOString().split("T")[0];

        batch.push({
          id: `${securityId}-${timestamps[j]}`,
          securityId,
          ticker,
          date: new Date(date),
          timestamp,
          open: quotes.open?.[j]?.toString() || null,
          high: quotes.high?.[j]?.toString() || null,
          low: quotes.low?.[j]?.toString() || null,
          close: quotes.close?.[j]?.toString() || null,
          volume: quotes.volume?.[j] || null,
          adjClose: result.indicators?.adjclose?.[0]?.adjclose?.[j]?.toString() || null,
          currency: meta.currency || currency,
          source: "yahoo_finance",
          interval: "1d",
        });
      }

      // Batch insert with ON DUPLICATE KEY UPDATE
      for (const record of batch) {
        try {
          await db
            .insert(priceHistory)
            .values(record)
            .onDuplicateKeyUpdate({ set: { close: record.close } });
          insertedCount++;
        } catch (err) {
          // Skip duplicates silently
        }
      }
    }

    console.log(`  ✅ Inserted ${insertedCount} price records for ${ticker}`);
    return { success: true, recordCount: insertedCount };
  } catch (error) {
    console.error(`  ❌ Error fetching price data for ${ticker}:`, error);
    return {
      success: false,
      recordCount: 0,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

/**
 * Fetch company profile from Fiscal.ai and update security metadata
 */
async function enrichCompanyProfile(
  securityId: string,
  ticker: string
): Promise<{ success: boolean; error?: string }> {
  try {
    console.log(`  🏢 Fetching company profile for ${ticker}...`);

    const profile = await fiscalAI.getCompanyProfile(ticker);

    if (!profile) {
      return { success: false, error: "No profile data" };
    }

    const db = await getDb();
    if (!db) {
      return { success: false, error: "Database unavailable" };
    }

    // Update security with profile data
    const updates: any = {};
    if (profile.sector) updates.sector = profile.sector;
    if (profile.industry) updates.industry = profile.industry;
    if (profile.marketCap) updates.marketCap = profile.marketCap.toString();
    if (profile.description) updates.description = profile.description;
    if (profile.website) updates.website = profile.website;

    if (Object.keys(updates).length > 0) {
      await db.update(securities).set(updates).where(eq(securities.id, securityId));
      console.log(`  ✅ Updated profile for ${ticker}`);
    }

    return { success: true };
  } catch (error) {
    console.error(`  ⚠️  Could not fetch Fiscal.ai profile for ${ticker}:`, error);
    // Don't fail the enrichment if Fiscal.ai fails, Yahoo Finance is primary
    return { success: false, error: "Fiscal.ai unavailable" };
  }
}

/**
 * Fetch latest price and update security
 */
async function updateLatestPrice(
  securityId: string,
  ticker: string
): Promise<{ success: boolean; price?: string }> {
  try {
    const chartData = await callDataApi("YahooFinance/get_stock_chart", {
      query: {
        symbol: ticker,
        region: "US",
        interval: "1d",
        range: "1d",
        includeAdjustedClose: true,
      },
    });

    if (!chartData || !(chartData as any)?.chart?.result?.[0]) {
      return { success: false };
    }

    const result = (chartData as any).chart.result[0];
    const meta = result.meta;
    const latestPrice = meta.regularMarketPrice;
    const marketCap = meta.marketCap;

    if (!latestPrice) {
      return { success: false };
    }

    const db = await getDb();
    if (!db) {
      return { success: false };
    }

    const updates: any = {
      lastPrice: latestPrice.toString(),
      updatedAt: new Date(),
    };

    if (marketCap) {
      updates.marketCap = marketCap.toString();
    }

    await db.update(securities).set(updates).where(eq(securities.id, securityId));

    console.log(`  💰 Updated latest price: ${ticker} = $${latestPrice}`);
    return { success: true, price: latestPrice.toString() };
  } catch (error) {
    console.error(`  ❌ Error updating price for ${ticker}:`, error);
    return { success: false };
  }
}

/**
 * Enrich a single security with all available data
 */
async function enrichSecurity(security: any): Promise<EnrichmentResult> {
  console.log(`\n🔄 Enriching ${security.ticker} (${security.name})...`);

  const result: EnrichmentResult = {
    ticker: security.ticker,
    success: false,
    priceRecords: 0,
    profileUpdated: false,
  };

  try {
    // Only enrich equities with Yahoo Finance (for now)
    if (security.assetClass === "equity") {
      // 1. Fetch 5 years of price data
      const priceResult = await enrichPriceData(
        security.id,
        security.ticker,
        security.currency
      );
      result.priceRecords = priceResult.recordCount;

      if (!priceResult.success) {
        result.error = priceResult.error;
        return result;
      }

      // 2. Update latest price
      await updateLatestPrice(security.id, security.ticker);

      // 3. Fetch company profile from Fiscal.ai (optional)
      const profileResult = await enrichCompanyProfile(security.id, security.ticker);
      result.profileUpdated = profileResult.success;

      result.success = true;
      console.log(`✅ Successfully enriched ${security.ticker}`);
    } else {
      console.log(`⏭️  Skipping ${security.ticker} (${security.assetClass} - not yet supported)`);
      result.success = true; // Mark as success to not retry
    }
  } catch (error) {
    console.error(`❌ Failed to enrich ${security.ticker}:`, error);
    result.error = error instanceof Error ? error.message : String(error);
  }

  return result;
}

/**
 * Main enrichment function
 */
async function enrichAllSecurities() {
  console.log("🚀 Starting batch enrichment of all securities...\n");
  console.log("📅 Fetching 5 years of historical price data");
  console.log("🔄 This may take several minutes due to API rate limits\n");

  const db = await getDb();
  if (!db) {
    console.error("❌ Database connection failed");
    process.exit(1);
  }

  // Fetch all securities
  const allSecurities = await db.select().from(securities);
  console.log(`📊 Found ${allSecurities.length} securities to enrich\n`);

  const results: EnrichmentResult[] = [];
  let successCount = 0;
  let failureCount = 0;
  let totalPriceRecords = 0;

  for (let i = 0; i < allSecurities.length; i++) {
    const security = allSecurities[i];
    console.log(`\n[${i + 1}/${allSecurities.length}] Processing ${security.ticker}...`);

    const result = await enrichSecurity(security);
    results.push(result);

    if (result.success) {
      successCount++;
      totalPriceRecords += result.priceRecords;
    } else {
      failureCount++;
    }

    // Rate limiting: wait 2 seconds between requests to avoid API throttling
    if (i < allSecurities.length - 1) {
      console.log("⏳ Waiting 2s to respect API rate limits...");
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  }

  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("📊 ENRICHMENT SUMMARY");
  console.log("=".repeat(60));
  console.log(`✅ Successful: ${successCount}/${allSecurities.length}`);
  console.log(`❌ Failed: ${failureCount}/${allSecurities.length}`);
  console.log(`📈 Total price records inserted: ${totalPriceRecords.toLocaleString()}`);
  console.log(`📅 Average records per security: ${Math.round(totalPriceRecords / successCount)}`);
  console.log("=".repeat(60));

  // Failed securities
  if (failureCount > 0) {
    console.log("\n❌ Failed Securities:");
    results
      .filter((r) => !r.success)
      .forEach((r) => {
        console.log(`  - ${r.ticker}: ${r.error || "Unknown error"}`);
      });
  }

  console.log("\n✅ Enrichment complete!");
}

// Run the enrichment
enrichAllSecurities()
  .then(() => {
    console.log("\n🎉 All done! Securities register is now populated with 5 years of data.");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n💥 Fatal error:", error);
    process.exit(1);
  });
