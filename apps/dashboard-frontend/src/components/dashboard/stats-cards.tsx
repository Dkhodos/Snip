import { Link2, MousePointerClick, Activity, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useStats } from "@/hooks/use-stats";

const statConfig = [
  {
    label: "Total Links",
    key: "total_links" as const,
    icon: Link2,
    colorClass: "text-primary",
  },
  {
    label: "Total Clicks",
    key: "total_clicks" as const,
    icon: MousePointerClick,
    colorClass: "text-blue-400",
  },
  {
    label: "Active Links",
    key: "active_links" as const,
    icon: Activity,
    colorClass: "text-[hsl(var(--success))]",
  },
  {
    label: "Expired Links",
    key: "expired_links" as const,
    icon: Clock,
    colorClass: "text-[hsl(var(--warning))]",
  },
];

export function StatsCards() {
  const { data, isLoading } = useStats();

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {statConfig.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card key={stat.key}>
            <CardContent className="p-6">
              {isLoading ? (
                <div className="space-y-3">
                  <Skeleton className="ml-auto h-5 w-5" />
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ) : (
                <div className="relative">
                  <Icon
                    className={`absolute right-0 top-0 h-5 w-5 opacity-80 ${stat.colorClass}`}
                  />
                  <div className="space-y-1">
                    <p className="text-3xl font-bold tabular-nums">
                      {data?.[stat.key] ?? 0}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {stat.label}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
