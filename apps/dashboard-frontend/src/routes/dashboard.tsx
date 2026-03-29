import { createFileRoute } from "@tanstack/react-router";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { ClicksChart } from "@/components/dashboard/clicks-chart";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <StatsCards />
        <ClicksChart />
      </div>
    </div>
  );
}
