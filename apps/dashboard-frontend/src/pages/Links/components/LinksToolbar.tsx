import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { STATUS_FILTERS, type StatusFilter } from "../types";

interface LinksToolbarProps {
	search: string;
	onSearchChange: (value: string) => void;
	status: StatusFilter;
	onStatusChange: (value: StatusFilter) => void;
}

export function LinksToolbar({
	search,
	onSearchChange,
	status,
	onStatusChange,
}: LinksToolbarProps) {
	return (
		<div className="flex shrink-0 flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div className="relative max-w-sm flex-1">
				<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
				<Input
					placeholder="Search links..."
					value={search}
					onChange={(e) => onSearchChange(e.target.value)}
					className="pl-9"
				/>
			</div>
			<div className="flex gap-1">
				{STATUS_FILTERS.map((filter) => (
					<Button
						key={filter.value}
						variant={status === filter.value ? "default" : "outline"}
						size="sm"
						onClick={() => onStatusChange(filter.value)}
					>
						{filter.label}
					</Button>
				))}
			</div>
		</div>
	);
}
