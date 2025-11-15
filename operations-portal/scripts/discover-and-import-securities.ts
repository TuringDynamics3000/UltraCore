/**
 * Securities Discovery and Import Script
 * Discovers ALL available securities from Fiscal.ai and Yahoo Finance
 * Imports them into the securities register with full metadata
 * 
 * Usage: pnpm tsx scripts/discover-and-import-securities.ts
 */

import { getDb } from "../server/db";
import { securities, priceHistory } from "../drizzle/schema";
import { callDataApi } from "../server/_core/dataApi";
import { fiscalAI } from "../server/fiscal-ai";
import { eq } from "drizzle-orm";

interface DiscoveredSecurity {
  ticker: string;
  name: string;
  exchange?: string;
  sector?: string;
  industry?: string;
  marketCap?: string;
  currency?: string;
}

/**
 * Discover all available companies from Fiscal.ai
 */
async function discoverFromFiscalAI(): Promise<DiscoveredSecurity[]> {
  console.log("🔍 Discovering securities from Fiscal.ai...");
  
  try {
    // Fiscal.ai companies-list endpoint can return up to 10,000+ companies
    const companies = await fiscalAI.searchCompanies(undefined, 10000);
    
    if (!companies || !Array.isArray(companies)) {
      console.error("❌ No companies returned from Fiscal.ai");
      return [];
    }

    console.log(`✅ Discovered ${companies.length} companies from Fiscal.ai`);

    return companies.map((company: any) => ({
      ticker: company.ticker || company.symbol,
      name: company.companyName || company.name,
      exchange: company.exchangeShortName || company.exchange,
      sector: company.sector,
      industry: company.industry,
      marketCap: company.marketCap?.toString(),
      currency: company.currency || "USD",
    }));
  } catch (error) {
    console.error("❌ Error discovering from Fiscal.ai:", error);
    return [];
  }
}

/**
 * Verify security exists in Yahoo Finance
 */
async function verifyYahooFinance(ticker: string): Promise<boolean> {
  try {
    const chartData = await callDataApi("YahooFinance/get_stock_chart", {
      query: {
        symbol: ticker,
        region: "US",
        interval: "1d",
        range: "1d",
      },
    });

    return !!(chartData as any)?.chart?.result?.[0];
  } catch {
    return false;
  }
}

/**
 * Import a security into the database
 */
async function importSecurity(
  security: DiscoveredSecurity,
  verifyYahoo: boolean = false
): Promise<{ success: boolean; error?: string }> {
  try {
    const db = await getDb();
    if (!db) {
      return { success: false, error: "Database unavailable" };
    }

    // Optional: Verify in Yahoo Finance first
    if (verifyYahoo) {
      const exists = await verifyYahooFinance(security.ticker);
      if (!exists) {
        return { success: false, error: "Not found in Yahoo Finance" };
      }
    }

    // Check if already exists
    const existing = await db
      .select()
      .from(securities)
      .where(eq(securities.ticker, security.ticker))
      .limit(1);

    if (existing.length > 0) {
      return { success: false, error: "Already exists" };
    }

    // Generate ID
    const id = `SEC-${security.ticker}-${Date.now()}`;

    // Insert security
    await db.insert(securities).values({
      id,
      ticker: security.ticker,
      name: security.name,
      assetClass: "equity", // Default to equity
      marketType: "exchange_traded",
      exchange: security.exchange || "UNKNOWN",
      currency: security.currency || "USD",
      sector: security.sector,
      industry: security.industry,
      marketCap: security.marketCap,
      isActive: true,
      status: "active",
      source: "fiscal_ai",
      verificationStatus: "unverified",
      createdBy: "discovery-script",
    });

    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

/**
 * Enrich security with 5 years of price data
 */
async function enrichWithPriceData(
  securityId: string,
  ticker: string,
  currency: string
): Promise<{ success: boolean; recordCount: number }> {
  try {
    const chartData = await callDataApi("YahooFinance/get_stock_chart", {
      query: {
        symbol: ticker,
        region: "US",
        interval: "1d",
        range: "5y",
        includeAdjustedClose: true,
      },
    });

    if (!chartData || !(chartData as any)?.chart?.result?.[0]) {
      return { success: false, recordCount: 0 };
    }

    const result = (chartData as any).chart.result[0];
    const timestamps = result.timestamp || [];
    const quotes = result.indicators?.quote?.[0];
    const meta = result.meta;

    if (!quotes || !timestamps.length) {
      return { success: false, recordCount: 0 };
    }

    const db = await getDb();
    if (!db) {
      return { success: false, recordCount: 0 };
    }

    let insertedCount = 0;

    // Insert in batches of 100
    for (let i = 0; i < timestamps.length; i += 100) {
      const batch = [];
      const end = Math.min(i + 100, timestamps.length);

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

      for (const record of batch) {
        try {
          await db
            .insert(priceHistory)
            .values(record)
            .onDuplicateKeyUpdate({ set: { close: record.close } });
          insertedCount++;
        } catch {
          // Skip duplicates
        }
      }
    }

    // Update latest price
    const latestPrice = meta.regularMarketPrice;
    if (latestPrice) {
      await db
        .update(securities)
        .set({
          lastPrice: latestPrice.toString(),
          marketCap: meta.marketCap?.toString(),
          updatedAt: new Date(),
        })
        .where(eq(securities.id, securityId));
    }

    return { success: true, recordCount: insertedCount };
  } catch (error) {
    console.error(`Error enriching ${ticker}:`, error);
    return { success: false, recordCount: 0 };
  }
}

/**
 * Main discovery and import function
 */
async function discoverAndImportAll() {
  console.log("🚀 Starting securities discovery and import...\n");

  // Step 1: Discover from Fiscal.ai
  const discovered = await discoverFromFiscalAI();
  
  if (discovered.length === 0) {
    console.error("❌ No securities discovered. Exiting.");
    process.exit(1);
  }

  console.log(`\n📊 Discovered ${discovered.length} securities`);
  console.log("🔄 Starting import process...\n");

  let importedCount = 0;
  let skippedCount = 0;
  let errorCount = 0;
  let totalPriceRecords = 0;

  // Step 2: Import securities (first 1000 to avoid overwhelming the system)
  const securitiesToImport = discovered.slice(0, 1000);
  console.log(`📥 Importing first ${securitiesToImport.length} securities...\n`);

  for (let i = 0; i < securitiesToImport.length; i++) {
    const security = securitiesToImport[i];
    
    if (i % 10 === 0) {
      console.log(`\n[${i + 1}/${securitiesToImport.length}] Processing ${security.ticker}...`);
    }

    // Import security
    const importResult = await importSecurity(security, false);
    
    if (!importResult.success) {
      if (importResult.error === "Already exists") {
        skippedCount++;
      } else {
        errorCount++;
        console.log(`  ❌ ${security.ticker}: ${importResult.error}`);
      }
      continue;
    }

    importedCount++;
    console.log(`  ✅ Imported ${security.ticker}`);

    // Step 3: Enrich with price data (every 5th security to save time)
    if (i % 5 === 0) {
      const db = await getDb();
      if (db) {
        const imported = await db
          .select()
          .from(securities)
          .where(eq(securities.ticker, security.ticker))
          .limit(1);

        if (imported.length > 0) {
          console.log(`  📊 Enriching ${security.ticker} with 5-year price history...`);
          const enrichResult = await enrichWithPriceData(
            imported[0].id,
            security.ticker,
            security.currency || "USD"
          );

          if (enrichResult.success) {
            totalPriceRecords += enrichResult.recordCount;
            console.log(`  ✅ Added ${enrichResult.recordCount} price records`);
          }
        }
      }
    }

    // Rate limiting
    if (i % 10 === 0 && i > 0) {
      console.log("  ⏳ Pausing 5s for rate limiting...");
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }

  // Summary
  console.log("\n" + "=".repeat(70));
  console.log("📊 IMPORT SUMMARY");
  console.log("=".repeat(70));
  console.log(`✅ Successfully imported: ${importedCount}`);
  console.log(`⏭️  Skipped (already exist): ${skippedCount}`);
  console.log(`❌ Errors: ${errorCount}`);
  console.log(`📈 Total price records: ${totalPriceRecords.toLocaleString()}`);
  console.log("=".repeat(70));

  console.log("\n✅ Discovery and import complete!");
  console.log(`\n💡 TIP: Run the full enrichment script to add price data to all securities:`);
  console.log(`   pnpm tsx scripts/enrich-all-securities.ts`);
}

// Run the discovery
discoverAndImportAll()
  .then(() => {
    console.log("\n🎉 All done!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n💥 Fatal error:", error);
    process.exit(1);
  });
