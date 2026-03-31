import { ClicksChart } from "./components/ClicksChart";
import { StatsCards } from "./components/StatsCards";

export function DashboardPage() {
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
