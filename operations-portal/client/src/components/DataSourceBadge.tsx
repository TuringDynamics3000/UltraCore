import { Badge } from "@/components/ui/badge";
import { Database, TrendingUp, Server } from "lucide-react";

interface DataSourceBadgeProps {
  source: "fiscal_ai" | "yahoo_finance" | "internal" | "kafka" | "manual";
  className?: string;
}

const sourceConfig = {
  fiscal_ai: {
    label: "Fiscal.ai",
    icon: TrendingUp,
    variant: "secondary" as const,
  },
  yahoo_finance: {
    label: "Yahoo Finance",
    icon: TrendingUp,
    variant: "outline" as const,
  },
  internal: {
    label: "Internal",
    icon: Database,
    variant: "default" as const,
  },
  kafka: {
    label: "Kafka Stream",
    icon: Server,
    variant: "secondary" as const,
  },
  manual: {
    label: "Manual Entry",
    icon: Database,
    variant: "outline" as const,
  },
};

export function DataSourceBadge({ source, className = "" }: DataSourceBadgeProps) {
  const config = sourceConfig[source];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={`gap-1 ${className}`}>
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}
