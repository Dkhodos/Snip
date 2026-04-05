import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
	Area,
	AreaChart,
	CartesianGrid,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
import { formatDate } from "../helpers";
import { useAggregateClicks } from "../hooks/useAggregateClicks";

export function ClicksChart() {
	const { data, isLoading } = useAggregateClicks();

	return (
		<Card>
			<CardHeader>
				<CardTitle className="text-lg">Click Activity</CardTitle>
				<CardDescription>Last 30 days</CardDescription>
			</CardHeader>
			<CardContent>
				{isLoading ? (
					<Skeleton className="h-[300px] w-full" />
				) : (
					<ResponsiveContainer width="100%" height={300}>
						<AreaChart data={data?.daily ?? []}>
							<defs>
								<linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
									<stop
										offset="5%"
										stopColor="hsl(173, 80%, 50%)"
										stopOpacity={0.3}
									/>
									<stop
										offset="95%"
										stopColor="hsl(173, 80%, 50%)"
										stopOpacity={0}
									/>
								</linearGradient>
							</defs>
							<CartesianGrid
								strokeDasharray="3 3"
								opacity={0.1}
								vertical={false}
							/>
							<XAxis
								dataKey="date"
								tickFormatter={formatDate}
								tick={{ fontSize: 12 }}
								tickLine={false}
								axisLine={false}
							/>
							<YAxis tick={false} tickLine={false} axisLine={false} width={0} />
							<Tooltip
								contentStyle={{
									backgroundColor: "hsl(var(--card))",
									color: "hsl(var(--foreground))",
									border: "1px solid hsl(var(--border))",
									borderRadius: "0.5rem",
									fontSize: "0.875rem",
								}}
								labelFormatter={(label) => formatDate(String(label))}
							/>
							<Area
								type="monotone"
								dataKey="count"
								stroke="hsl(173, 80%, 50%)"
								strokeWidth={2}
								fill="url(#colorClicks)"
							/>
						</AreaChart>
					</ResponsiveContainer>
				)}
			</CardContent>
		</Card>
	);
}
