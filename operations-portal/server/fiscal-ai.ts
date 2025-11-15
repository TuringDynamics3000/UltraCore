/**
 * Fiscal.ai API Client for UltraCore Operations Portal
 * Based on UltraCore repository implementation
 * Provides institutional-grade financial data for securities
 */

interface FiscalAIConfig {
  apiKey: string;
  baseUrl: string;
}

interface CompanyProfile {
  ticker: string;
  companyName: string;
  sector?: string;
  industry?: string;
  description?: string;
  marketCap?: number;
  employees?: number;
  website?: string;
  ceo?: string;
  founded?: string;
}

interface StockPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjClose?: number;
}

interface FinancialRatios {
  ticker: string;
  date: string;
  peRatio?: number;
  pbRatio?: number;
  debtToEquity?: number;
  currentRatio?: number;
  quickRatio?: number;
  roe?: number;
  roa?: number;
  dividendYield?: number;
  payoutRatio?: number;
}

class FiscalAIClient {
  private config: FiscalAIConfig;

  constructor(apiKey?: string) {
    this.config = {
      apiKey: apiKey || process.env.FISCAL_AI_API_KEY || "",
      baseUrl: "https://api.fiscal.ai",
    };

    if (!this.config.apiKey) {
      console.warn("[Fiscal.ai] API key not configured. Set FISCAL_AI_API_KEY environment variable.");
    }
  }

  private async request<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    if (!this.config.apiKey) {
      throw new Error("Fiscal.ai API key not configured");
    }

    const url = new URL(`${this.config.baseUrl}/${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "X-API-KEY": this.config.apiKey,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Fiscal.ai API error (${response.status}): ${errorText}`);
    }

    return response.json();
  }

  /**
   * Get company profile with sector, industry, description
   */
  async getCompanyProfile(ticker: string): Promise<CompanyProfile> {
    return this.request<CompanyProfile>("v2/company/profile", { ticker });
  }

  /**
   * Get historical stock prices
   */
  async getStockPrices(
    ticker: string,
    fromDate?: string,
    toDate?: string
  ): Promise<StockPrice[]> {
    const params: Record<string, string> = { ticker };
    if (fromDate) params.from = fromDate;
    if (toDate) params.to = toDate;
    
    const result = await this.request<any>("v1/company/stock-prices", params);
    
    // Handle both array and object responses
    if (Array.isArray(result)) {
      return result;
    } else if (result.data && Array.isArray(result.data)) {
      return result.data;
    }
    return [];
  }

  /**
   * Get latest stock price
   */
  async getLatestPrice(ticker: string): Promise<StockPrice | null> {
    const prices = await this.getStockPrices(ticker);
    return prices.length > 0 ? prices[0] : null;
  }

  /**
   * Get financial ratios time series
   */
  async getCompanyRatios(
    ticker: string,
    period: "annual" | "quarterly" = "annual",
    limit: number = 5
  ): Promise<FinancialRatios[]> {
    return this.request<FinancialRatios[]>("v1/company/ratios", {
      ticker,
      period,
      limit,
    });
  }

  /**
   * Get income statement
   */
  async getIncomeStatement(
    ticker: string,
    period: "annual" | "quarterly" = "annual",
    limit: number = 5
  ): Promise<any[]> {
    return this.request<any[]>("v1/company/financials/income-statement/standardized", {
      ticker,
      period,
      limit,
    });
  }

  /**
   * Get balance sheet
   */
  async getBalanceSheet(
    ticker: string,
    period: "annual" | "quarterly" = "annual",
    limit: number = 5
  ): Promise<any[]> {
    return this.request<any[]>("v1/company/financials/balance-sheet/standardized", {
      ticker,
      period,
      limit,
    });
  }

  /**
   * Get cash flow statement
   */
  async getCashFlowStatement(
    ticker: string,
    period: "annual" | "quarterly" = "annual",
    limit: number = 5
  ): Promise<any[]> {
    return this.request<any[]>("v1/company/financials/cash-flow/standardized", {
      ticker,
      period,
      limit,
    });
  }

  /**
   * Get SEC filings
   */
  async getCompanyFilings(ticker: string, limit: number = 10): Promise<any[]> {
    return this.request<any[]>("v2/company/filings", { ticker, limit });
  }

  /**
   * Get earnings summary
   */
  async getEarningsSummary(ticker: string): Promise<any> {
    return this.request<any>("v1/company/earnings-summary", { ticker });
  }

  /**
   * Search companies
   */
  async searchCompanies(query?: string, limit: number = 100): Promise<any[]> {
    const params: Record<string, any> = { limit };
    if (query) params.search = query;
    return this.request<any[]>("v2/companies-list", params);
  }
}

// Export singleton instance
export const fiscalAI = new FiscalAIClient();

// Export types
export type {
  CompanyProfile,
  StockPrice,
  FinancialRatios,
};
