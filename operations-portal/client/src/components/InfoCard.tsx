import { Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface InfoCardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function InfoCard({ title, children, className = "" }: InfoCardProps) {
  return (
    <Card className={`border-blue-200 bg-blue-50/50 ${className}`}>
      <CardContent className="pt-4">
        <div className="flex gap-3">
          <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            {title && <h4 className="font-semibold text-blue-900 mb-1">{title}</h4>}
            <div className="text-sm text-blue-800">{children}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
