/**
 * Import Securities from Public Ticker Lists
 * Downloads comprehensive ticker lists and enriches with Yahoo Finance data
 * 
 * Usage: pnpm tsx scripts/import-from-ticker-list.ts
 */

import { getDb } from "../server/db";
import { securities, priceHistory } from "../drizzle/schema";
import { callDataApi } from "../server/_core/dataApi";
import { eq } from "drizzle-orm";

// Comprehensive list of major US stocks (S&P 500, NASDAQ 100, Dow 30)
const MAJOR_US_STOCKS = [
  // Tech Giants (FAANG+)
  "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX",
  
  // Major Tech
  "AMD", "INTC", "CRM", "ORCL", "ADBE", "CSCO", "AVGO", "TXN", "QCOM", "AMAT",
  "ASML", "NOW", "INTU", "PANW", "SNPS", "CDNS", "FTNT", "PLTR", "CRWD",
  
  // Finance
  "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW", "AXP", "USB",
  "PNC", "TFC", "COF", "BK", "STT", "SPGI", "MCO", "CME", "ICE",
  
  // Healthcare
  "UNH", "JNJ", "LLY", "ABBV", "MRK", "PFE", "TMO", "ABT", "DHR", "BMY",
  "AMGN", "GILD", "CVS", "CI", "ELV", "HCA", "ISRG", "REGN", "VRTX", "ZTS",
  
  // Consumer
  "WMT", "HD", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX", "TGT",
  "LOW", "TJX", "DG", "ROST", "ULTA", "YUM", "CMG", "ORLY", "AZO",
  
  // Industrial
  "CAT", "BA", "HON", "UNP", "RTX", "LMT", "GE", "MMM", "DE", "UPS",
  "FDX", "NSC", "CSX", "EMR", "ETN", "ITW", "PH", "ROK", "CARR",
  
  // Energy
  "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
  "KMI", "WMB", "OKE", "FANG", "DVN", "HES", "BKR", "APA",
  
  // Telecom/Media
  "T", "VZ", "TMUS", "CMCSA", "DIS", "NFLX", "CHTR", "PARA", "WBD", "FOXA",
  
  // Real Estate
  "AMT", "PLD", "CCI", "EQIX", "PSA", "WELL", "DLR", "O", "SBAC", "AVB",
  
  // Materials
  "LIN", "APD", "SHW", "ECL", "DD", "NEM", "FCX", "NUE", "VMC", "MLM",
  
  // Utilities
  "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "WEC", "ES",
  
  // Crypto/Fintech
  "COIN", "SQ", "PYPL", "V", "MA", "MSTR", "HOOD", "SOFI",
  
  // AI/Cloud
  "SNOW", "DDOG", "NET", "MDB", "TEAM", "ZS", "OKTA", "TWLO", "DOCU",
  
  // EV/Clean Energy
  "RIVN", "LCID", "NIO", "XPEV", "LI", "ENPH", "SEDG", "FSLR", "RUN",
  
  // Biotech
  "MRNA", "BNTX", "ILMN", "BIIB", "ALNY", "SGEN", "EXAS", "INCY", "NBIX",
  
  // Semiconductors
  "TSM", "AVGO", "QCOM", "TXN", "ADI", "MRVL", "NXPI", "KLAC", "LRCX", "MPWR",
  
  // Retail/E-commerce
  "SHOP", "MELI", "BABA", "JD", "PDD", "SE", "ETSY", "W", "CHWY",
  
  // Aerospace/Defense
  "NOC", "GD", "LHX", "HWM", "TDG", "LDOS", "TXT", "HII",
  
  // Pharma
  "NVO", "RHHBY", "AZN", "SNY", "GSK", "TAK", "NVS", "BAYRY",
  
  // Banks (Regional)
  "KEY", "FITB", "HBAN", "RF", "CFG", "MTB", "ZION", "CMA",
  
  // Insurance
  "BRK.B", "PGR", "ALL", "TRV", "AIG", "MET", "PRU", "AFL", "HIG", "CB",
  
  // Food/Beverage
  "MDLZ", "GIS", "K", "HSY", "CAG", "CPB", "SJM", "HRL", "TSN", "BG",
  
  // Apparel
  "LULU", "GPS", "UAA", "RL", "PVH", "VFC", "HBI", "CROX",
  
  // Hotels/Travel
  "MAR", "HLT", "H", "IHG", "BKNG", "EXPE", "ABNB", "UBER", "LYFT", "DAL", "UAL", "AAL", "LUV",
  
  // Entertainment/Gaming
  "EA", "TTWO", "ATVI", "RBLX", "U", "DKNG", "PENN", "MGM", "WYNN", "LVS",
  
  // Chemicals
  "DOW", "LYB", "EMN", "ALB", "FMC", "CE", "CF", "MOS", "IFF",
  
  // Construction
  "DHI", "LEN", "PHM", "NVR", "TOL", "BLD", "BLDR", "HD", "LOW",
  
  // Auto
  "F", "GM", "STLA", "HMC", "TM", "RACE", "MBGYY", "VWAGY",
  
  // Restaurants
  "MCD", "SBUX", "YUM", "QSR", "DPZ", "CMG", "WEN", "JACK", "DRI", "EAT",
  
  // Healthcare Services
  "MCK", "CAH", "COR", "ABC", "HSIC", "DVA", "DGX", "LH", "HOLX",
  
  // Medical Devices
  "MDT", "ABT", "SYK", "BSX", "EW", "ZBH", "BAX", "BDX", "RMD", "DXCM",
  
  // Software
  "MSFT", "ORCL", "SAP", "ADBE", "CRM", "NOW", "INTU", "WDAY", "ANSS", "CDNS",
  
  // Cybersecurity
  "PANW", "CRWD", "ZS", "FTNT", "OKTA", "CYBR", "S", "TENB",
  
  // Cloud Infrastructure
  "AMZN", "MSFT", "GOOGL", "IBM", "ORCL", "VMW", "DELL", "HPE", "NTAP",
  
  // Payments
  "V", "MA", "AXP", "PYPL", "SQ", "FIS", "FISV", "GPN", "ADYEN",
  
  // Logistics
  "UPS", "FDX", "XPO", "JBHT", "CHRW", "EXPD", "KNX", "LSTR",
  
  // Mining
  "NEM", "GOLD", "FCX", "SCCO", "AA", "CENX", "TECK", "BHP", "RIO", "VALE",
  
  // Oil Services
  "SLB", "HAL", "BKR", "FTI", "NOV", "HP", "WTTR", "CHX",
  
  // Pipelines
  "KMI", "WMB", "OKE", "EPD", "ET", "MPLX", "PAA", "ENLC",
  
  // REITs
  "AMT", "PLD", "CCI", "EQIX", "PSA", "WELL", "DLR", "O", "SBAC", "AVB",
  "EQR", "VTR", "MAA", "ESS", "UDR", "CPT", "AIV", "BXP", "VNO",
  
  // Tobacco
  "MO", "PM", "BTI", "IMBBY",
  
  // Alcohol
  "BUD", "TAP", "STZ", "DEO", "SAM", "BF.B",
  
  // Waste Management
  "WM", "RSG", "WCN", "CWST",
  
  // Water Utilities
  "AWK", "WTR", "WTRG", "SJW", "CWT",
];

/**
 * Fetch and import a single security
 */
async function importAndEnrichSecurity(
  ticker: string,
  enrichPrices: boolean = true
): Promise<{ success: boolean; priceRecords: number; error?: string }> {
  try {
    const db = await getDb();
    if (!db) {
      return { success: false, priceRecords: 0, error: "Database unavailable" };
    }

    // Check if already exists
    const existing = await db
      .select()
      .from(securities)
      .where(eq(securities.ticker, ticker))
      .limit(1);

    if (existing.length > 0 && enrichPrices) {
      console.log(`  ⏭️  ${ticker} already exists, enriching price data...`);
      
      // Just enrich prices
      const enrichResult = await enrichWithPriceData(existing[0].id, ticker, "USD");
      return {
        success: true,
        priceRecords: enrichResult.recordCount,
      };
    } else if (existing.length > 0) {
      return { success: false, priceRecords: 0, error: "Already exists" };
    }

    // Fetch basic info from Yahoo Finance
    console.log(`  📊 Fetching data for ${ticker}...`);
    const chartData = await callDataApi("YahooFinance/get_stock_chart", {
      query: {
        symbol: ticker,
        region: "US",
        interval: "1d",
        range: "1d",
      },
    });

    if (!chartData || !(chartData as any)?.chart?.result?.[0]) {
      return { success: false, priceRecords: 0, error: "Not found in Yahoo Finance" };
    }

    const result = (chartData as any).chart.result[0];
    const meta = result.meta;

    // Generate ID
    const id = `SEC-${ticker}-${Date.now()}`;

    // Insert security
    await db.insert(securities).values({
      id,
      ticker,
      name: meta.longName || meta.shortName || ticker,
      assetClass: "equity",
      marketType: "exchange_traded",
      exchange: meta.exchangeName || meta.exchange || "UNKNOWN",
      currency: meta.currency || "USD",
      lastPrice: meta.regularMarketPrice?.toString(),
      marketCap: meta.marketCap?.toString(),
      isActive: true,
      status: "active",
      source: "yahoo_finance",
      verificationStatus: "verified",
      createdBy: "import-script",
    });

    console.log(`  ✅ Imported ${ticker} - ${meta.longName || ticker}`);

    // Enrich with 5 years of price data
    let priceRecords = 0;
    if (enrichPrices) {
      console.log(`  📈 Fetching 5-year price history...`);
      const enrichResult = await enrichWithPriceData(id, ticker, meta.currency || "USD");
      priceRecords = enrichResult.recordCount;
      console.log(`  ✅ Added ${priceRecords} price records`);
    }

    return { success: true, priceRecords };
  } catch (error) {
    return {
      success: false,
      priceRecords: 0,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

/**
 * Enrich with 5 years of price data
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

    for (let i = 0; i < timestamps.length; i++) {
      const timestamp = new Date(timestamps[i] * 1000);
      const date = timestamp.toISOString().split("T")[0];

      const record = {
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
        currency: meta.currency || currency,
        source: "yahoo_finance",
        interval: "1d",
      };

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

    return { success: true, recordCount: insertedCount };
  } catch (error) {
    return { success: false, recordCount: 0 };
  }
}

/**
 * Main import function
 */
async function importAllSecurities() {
  console.log("🚀 Starting securities import from ticker list...\n");
  console.log(`📊 Importing ${MAJOR_US_STOCKS.length} major US securities`);
  console.log("📅 Fetching 5 years of historical price data for each\n");

  let successCount = 0;
  let failureCount = 0;
  let totalPriceRecords = 0;
  const errors: Array<{ ticker: string; error: string }> = [];

  for (let i = 0; i < MAJOR_US_STOCKS.length; i++) {
    const ticker = MAJOR_US_STOCKS[i];
    
    console.log(`\n[${i + 1}/${MAJOR_US_STOCKS.length}] Processing ${ticker}...`);

    const result = await importAndEnrichSecurity(ticker, true);

    if (result.success) {
      successCount++;
      totalPriceRecords += result.priceRecords;
    } else {
      failureCount++;
      if (result.error && result.error !== "Already exists") {
        errors.push({ ticker, error: result.error });
        console.log(`  ❌ ${ticker}: ${result.error}`);
      }
    }

    // Rate limiting: wait 1 second between requests
    if (i < MAJOR_US_STOCKS.length - 1 && i % 10 === 9) {
      console.log("  ⏳ Pausing 3s for rate limiting...");
      await new Promise((resolve) => setTimeout(resolve, 3000));
    } else if (i < MAJOR_US_STOCKS.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  // Summary
  console.log("\n" + "=".repeat(70));
  console.log("📊 IMPORT SUMMARY");
  console.log("=".repeat(70));
  console.log(`✅ Successfully imported: ${successCount}/${MAJOR_US_STOCKS.length}`);
  console.log(`❌ Failed: ${failureCount}/${MAJOR_US_STOCKS.length}`);
  console.log(`📈 Total price records: ${totalPriceRecords.toLocaleString()}`);
  console.log(`📅 Average records per security: ${Math.round(totalPriceRecords / (successCount || 1))}`);
  console.log("=".repeat(70));

  if (errors.length > 0) {
    console.log("\n❌ Errors:");
    errors.forEach(({ ticker, error }) => {
      console.log(`  - ${ticker}: ${error}`);
    });
  }

  console.log("\n✅ Import complete!");
}

// Run the import
importAllSecurities()
  .then(() => {
    console.log("\n🎉 Securities register populated successfully!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n💥 Fatal error:", error);
    process.exit(1);
  });
