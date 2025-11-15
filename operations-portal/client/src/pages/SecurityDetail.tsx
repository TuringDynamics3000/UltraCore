import { useEffect, useRef, useState } from "react";
import { useRoute } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ArrowLeft, 
  TrendingUp, 
  TrendingDown, 
  Building2, 
  Bitcoin, 
  Palette, 
  Wine, 
  Home,
  ExternalLink,
  FileText,
  BarChart3,
  Shield,
  Lock,
  AlertTriangle
} from "lucide-react";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

export default function SecurityDetail() {
  const [, params] = useRoute("/securities/:id");
  const securityId = params?.id || "";
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  // Fetch security details
  const { data: security, isLoading: securityLoading } = trpc.securities.getById.useQuery(
    { id: securityId },
    { enabled: !!securityId }
  );

  // Fetch market data for equities (Fiscal.ai + Yahoo Finance)
  const { data: marketData } = trpc.securities.getMarketData.useQuery(
    { ticker: security?.ticker || "" },
    { enabled: !!security && security.assetClass === "equity" }
  );

  const { data: yahooChart } = trpc.securities.getYahooChart.useQuery(
    { symbol: security?.ticker || "", interval: "1d", range: "1mo" },
    { enabled: !!security && security.assetClass === "equity" }
  );

  const { data: yahooInsights } = trpc.securities.getYahooInsights.useQuery(
    { symbol: security?.ticker || "" },
    { enabled: !!security && security.assetClass === "equity" }
  );

  // Render price chart for equities
  useEffect(() => {
    if (!chartRef.current || !yahooChart) return;

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const chartData = yahooChart as any;
    if (!chartData?.chart?.result?.[0]) return;

    const result = chartData.chart.result[0];
    const timestamps = result.timestamp || [];
    const quotes = result.indicators?.quote?.[0];
    
    if (!quotes || !timestamps.length) return;

    const dates = timestamps.map((ts: number) => 
      new Date(ts * 1000).toLocaleDateString()
    );
    const prices = quotes.close || [];

    const ctx = chartRef.current.getContext("2d");
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Close Price",
            data: prices,
            borderColor: "rgb(59, 130, 246)",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            tension: 0.1,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              callback: (value: string | number) => `$${value}`,
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [yahooChart]);

  if (securityLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!security) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Security Not Found</h2>
          <p className="text-gray-600 mt-2">The requested security could not be found.</p>
          <Button className="mt-4" onClick={() => window.history.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Securities
          </Button>
        </div>
      </div>
    );
  }

  const getAssetIcon = () => {
    switch (security.assetClass) {
      case "equity":
        return <Building2 className="h-6 w-6" />;
      case "crypto":
      case "stablecoin":
        return <Bitcoin className="h-6 w-6" />;
      case "artwork":
        return <Palette className="h-6 w-6" />;
      case "wine":
        return <Wine className="h-6 w-6" />;
      case "real_estate":
        return <Home className="h-6 w-6" />;
      default:
        return <Building2 className="h-6 w-6" />;
    }
  };

  const getBlockchainExplorerUrl = () => {
    if (!security.contractAddress) return null;
    
    // Ethereum-based tokens
    if (["ETH", "USDT", "USDC", "SHIB"].includes(security.ticker)) {
      return `https://etherscan.io/token/${security.contractAddress}`;
    }
    // Binance Smart Chain
    if (security.ticker === "BNB") {
      return `https://bscscan.com/token/${security.contractAddress}`;
    }
    // Solana
    if (security.ticker === "SOL") {
      return `https://solscan.io/token/${security.contractAddress}`;
    }
    // Bitcoin
    if (security.ticker === "BTC") {
      return `https://blockchain.com/explorer`;
    }
    // Default to Etherscan for unknown
    return `https://etherscan.io/token/${security.contractAddress}`;
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            {getAssetIcon()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold text-gray-900">{security.ticker}</h1>
              <Badge variant="outline">{security.assetClass}</Badge>
              <Badge variant="secondary">{security.marketType}</Badge>
            </div>
            <p className="text-lg text-gray-600 mt-1">{security.name}</p>
            {security.exchange && (
              <p className="text-sm text-gray-500 mt-1">
                {security.exchange} • {security.currency}
              </p>
            )}
          </div>
        </div>
        <Button variant="outline" onClick={() => window.history.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      </div>

      {/* Price & Market Data */}
      {security.assetClass === "equity" && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Current Price</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {security.currency} {security.lastPrice || "N/A"}
              </div>
              {marketData?.latestPrice && (
                <p className="text-xs text-gray-500 mt-1">
                  Updated: {new Date().toLocaleDateString()}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Market Cap</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{security.marketCap || "N/A"}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>P/E Ratio</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {marketData?.ratios?.peRatio?.toFixed(2) || "N/A"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Dividend Yield</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {marketData?.ratios?.dividendYield 
                  ? `${(marketData.ratios.dividendYield * 100).toFixed(2)}%`
                  : "N/A"}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Crypto Price Display */}
      {(security.assetClass === "crypto" || security.assetClass === "stablecoin") && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Current Price</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {security.currency} {security.lastPrice || "N/A"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Market Cap</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{security.marketCap || "N/A"}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Blockchain</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold">{security.sector || "Multi-chain"}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alternative Assets Price Display */}
      {["artwork", "wine", "real_estate"].includes(security.assetClass) && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Valuation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {security.currency} {security.lastPrice || "N/A"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Market Type</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold capitalize">
                {security.marketType.replace(/_/g, " ")}
              </div>
              {security.exchange && (
                <p className="text-sm text-gray-500 mt-1">{security.exchange}</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs for detailed information */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          {security.assetClass === "equity" && (
            <>
              <TabsTrigger value="chart">Price Chart</TabsTrigger>
              <TabsTrigger value="financials">Financials</TabsTrigger>
            </>
          )}
          {(security.assetClass === "crypto" || security.assetClass === "stablecoin") && (
            <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
          )}
          <TabsTrigger value="custody">Custody & Risk</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">ISIN</p>
                  <p className="text-base font-semibold">{security.isin || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">CUSIP</p>
                  <p className="text-base font-semibold">{security.cusip || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">SEDOL</p>
                  <p className="text-base font-semibold">{security.sedol || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Sector</p>
                  <p className="text-base font-semibold">{security.sector || "N/A"}</p>
                </div>
              </div>

              {marketData?.profile && (
                <div className="mt-4 pt-4 border-t">
                  <h4 className="font-semibold mb-2">Company Profile</h4>
                  <p className="text-sm text-gray-600">
                    {marketData.profile.description || "No description available"}
                  </p>
                  {marketData.profile.website && (
                    <a
                      href={marketData.profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm mt-2 inline-flex items-center"
                    >
                      Visit Website <ExternalLink className="ml-1 h-3 w-3" />
                    </a>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Price Chart Tab (Equities) */}
        {security.assetClass === "equity" && (
          <TabsContent value="chart" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>30-Day Price Chart</CardTitle>
                <CardDescription>Historical closing prices</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <canvas ref={chartRef}></canvas>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Financials Tab (Equities) */}
        {security.assetClass === "equity" && (
          <TabsContent value="financials" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Financial Ratios</CardTitle>
              </CardHeader>
              <CardContent>
                {marketData?.ratios ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">P/E Ratio</p>
                      <p className="text-xl font-bold">
                        {marketData.ratios.peRatio?.toFixed(2) || "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">P/B Ratio</p>
                      <p className="text-xl font-bold">
                        {marketData.ratios.pbRatio?.toFixed(2) || "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">ROE</p>
                      <p className="text-xl font-bold">
                        {marketData.ratios.roe 
                          ? `${(marketData.ratios.roe * 100).toFixed(2)}%`
                          : "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Debt/Equity</p>
                      <p className="text-xl font-bold">
                        {marketData.ratios.debtToEquity?.toFixed(2) || "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Current Ratio</p>
                      <p className="text-xl font-bold">
                        {marketData.ratios.currentRatio?.toFixed(2) || "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Dividend Yield</p>
                      <p className="text-xl font-bold">
                        {marketData.ratios.dividendYield
                          ? `${(marketData.ratios.dividendYield * 100).toFixed(2)}%`
                          : "N/A"}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Financial data not available</p>
                )}
              </CardContent>
            </Card>

            {yahooInsights && (
              <Card>
                <CardHeader>
                  <CardTitle>Market Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">
                    Additional market insights and analysis from Yahoo Finance
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        )}

        {/* Blockchain Tab (Crypto) */}
        {(security.assetClass === "crypto" || security.assetClass === "stablecoin") && (
          <TabsContent value="blockchain" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Blockchain Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {security.contractAddress && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-1">Contract Address</p>
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded block break-all">
                      {security.contractAddress}
                    </code>
                  </div>
                )}

                {getBlockchainExplorerUrl() && (
                  <div>
                    <a
                      href={getBlockchainExplorerUrl()!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-blue-600 hover:underline"
                    >
                      View on Blockchain Explorer <ExternalLink className="ml-1 h-4 w-4" />
                    </a>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Network</p>
                    <p className="text-base font-semibold">{security.sector || "Multi-chain"}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Type</p>
                    <p className="text-base font-semibold capitalize">{security.assetClass}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Custody & Risk Tab */}
        <TabsContent value="custody" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Custody Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">Custody Status:</span>
                  <Badge variant="outline">Institutional Custody</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Lock className="h-5 w-5 text-green-600" />
                  <span className="font-medium">Insurance:</span>
                  <Badge variant="outline">Fully Insured</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  <span className="font-medium">Risk Level:</span>
                  <Badge variant="outline">Medium</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>ESG Ratings</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Environmental, Social, and Governance ratings will be displayed here
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
