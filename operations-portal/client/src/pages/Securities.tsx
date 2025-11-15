import { useState } from "react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Building2, Bitcoin, Palette, Wine, Home, Search, TrendingUp, Globe } from "lucide-react";

export default function Securities() {
  const [, setLocation] = useLocation();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAssetClass, setSelectedAssetClass] = useState<string>("all");

  // Fetch all securities
  const { data: securities, isLoading } = trpc.securities.list.useQuery({
    assetClass: selectedAssetClass === "all" ? undefined : selectedAssetClass,
    search: searchQuery || undefined,
  });

  const formatPrice = (price: string | null, currency: string | null) => {
    if (!price) return "N/A";
    const numPrice = parseFloat(price);
    if (isNaN(numPrice)) return price;
    
    if (numPrice >= 1000000) {
      return `${currency || "$"}${(numPrice / 1000000).toFixed(2)}M`;
    } else if (numPrice >= 1000) {
      return `${currency || "$"}${(numPrice / 1000).toFixed(2)}K`;
    } else if (numPrice < 1) {
      return `${currency || "$"}${numPrice.toFixed(6)}`;
    }
    return `${currency || "$"}${numPrice.toFixed(2)}`;
  };

  const formatMarketCap = (marketCap: string | null) => {
    if (!marketCap) return "N/A";
    const num = parseFloat(marketCap);
    if (isNaN(num)) return marketCap;
    
    if (num >= 1000000000000) {
      return `$${(num / 1000000000000).toFixed(2)}T`;
    } else if (num >= 1000000000) {
      return `$${(num / 1000000000).toFixed(2)}B`;
    } else if (num >= 1000000) {
      return `$${(num / 1000000).toFixed(2)}M`;
    }
    return `$${num.toFixed(0)}`;
  };

  const getAssetClassIcon = (assetClass: string) => {
    switch (assetClass) {
      case "equity":
      case "etf":
        return <Building2 className="h-5 w-5" />;
      case "crypto":
      case "stablecoin":
        return <Bitcoin className="h-5 w-5" />;
      case "artwork":
        return <Palette className="h-5 w-5" />;
      case "wine":
        return <Wine className="h-5 w-5" />;
      case "real_estate":
        return <Home className="h-5 w-5" />;
      default:
        return <TrendingUp className="h-5 w-5" />;
    }
  };

  const getAssetClassColor = (assetClass: string) => {
    switch (assetClass) {
      case "equity":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "etf":
        return "bg-indigo-500/10 text-indigo-500 border-indigo-500/20";
      case "crypto":
        return "bg-orange-500/10 text-orange-500 border-orange-500/20";
      case "stablecoin":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "artwork":
        return "bg-purple-500/10 text-purple-500 border-purple-500/20";
      case "wine":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "real_estate":
        return "bg-amber-500/10 text-amber-500 border-amber-500/20";
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

  const getMarketTypeLabel = (marketType: string) => {
    switch (marketType) {
      case "exchange_traded":
        return "Exchange";
      case "otc":
        return "OTC";
      case "private":
        return "Private";
      case "decentralized":
        return "Decentralized";
      case "physical":
        return "Physical";
      default:
        return marketType;
    }
  };

  // Calculate summary stats
  const totalSecurities = securities?.length || 0;
  const totalMarketCap = securities?.reduce((sum, s) => sum + (parseFloat(s.marketCap || "0") || 0), 0) || 0;
  const assetClassCounts = securities?.reduce((acc, s) => {
    acc[s.assetClass] = (acc[s.assetClass] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  return (
    <div className="container mx-auto py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Global Securities Register</h1>
          <p className="text-muted-foreground mt-1">
            Comprehensive asset register covering equities, crypto, and alternatives
          </p>
        </div>
        <Button onClick={() => setLocation("/securities/new")}>
          <Globe className="mr-2 h-4 w-4" />
          Add Security
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Securities</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalSecurities}</div>
            <p className="text-xs text-muted-foreground">
              Across {Object.keys(assetClassCounts).length} asset classes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Market Cap</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatMarketCap(totalMarketCap.toString())}</div>
            <p className="text-xs text-muted-foreground">
              Combined valuation
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Equities</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(assetClassCounts.equity || 0) + (assetClassCounts.etf || 0)}</div>
            <p className="text-xs text-muted-foreground">
              Stocks & ETFs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Digital Assets</CardTitle>
            <Bitcoin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(assetClassCounts.crypto || 0) + (assetClassCounts.stablecoin || 0)}</div>
            <p className="text-xs text-muted-foreground">
              Crypto & Stablecoins
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search Securities</CardTitle>
          <CardDescription>Find securities by ticker, name, ISIN, or contract address</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by ticker, name, ISIN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Asset Class Tabs */}
      <Tabs value={selectedAssetClass} onValueChange={setSelectedAssetClass}>
        <TabsList>
          <TabsTrigger value="all">All ({totalSecurities})</TabsTrigger>
          <TabsTrigger value="equity">Equities ({assetClassCounts.equity || 0})</TabsTrigger>
          <TabsTrigger value="crypto">Crypto ({assetClassCounts.crypto || 0})</TabsTrigger>
          <TabsTrigger value="artwork">Art ({assetClassCounts.artwork || 0})</TabsTrigger>
          <TabsTrigger value="wine">Wine ({assetClassCounts.wine || 0})</TabsTrigger>
          <TabsTrigger value="real_estate">Real Estate ({assetClassCounts.real_estate || 0})</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedAssetClass} className="space-y-4 mt-6">
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading securities...</div>
          ) : securities && securities.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {securities.map((security) => (
                <Card
                  key={security.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setLocation(`/securities/${security.id}`)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${getAssetClassColor(security.assetClass)}`}>
                          {getAssetClassIcon(security.assetClass)}
                        </div>
                        <div>
                          <CardTitle className="text-lg">{security.ticker}</CardTitle>
                          <CardDescription className="line-clamp-1">{security.name}</CardDescription>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Price</span>
                      <span className="font-semibold">{formatPrice(security.lastPrice, security.currency)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Market Cap</span>
                      <span className="font-semibold">{formatMarketCap(security.marketCap)}</span>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className={getAssetClassColor(security.assetClass)}>
                        {security.assetClass}
                      </Badge>
                      <Badge variant="outline">
                        {getMarketTypeLabel(security.marketType)}
                      </Badge>
                      {security.exchange && (
                        <Badge variant="outline" className="text-xs">
                          {security.exchange}
                        </Badge>
                      )}
                    </div>

                    {security.sector && (
                      <div className="text-xs text-muted-foreground">
                        {security.sector}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              No securities found. Try adjusting your filters.
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
