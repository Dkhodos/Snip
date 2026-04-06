import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import type { Link } from "@/lib/api";
import { ArrowUpDown } from "lucide-react";
import { getLinkStatus, getRelativeTime } from "../helpers";
import { LinkRowActions } from "./LinkRowActions";

interface LinksTableProps {
	data: { items: Link[]; total: number; limit: number } | undefined;
	isLoading: boolean;
	sortBy: string;
	sortOrder: "asc" | "desc";
	onSort: (column: string) => void;
	onEdit: (link: Link) => void;
	onDelete: (link: Link) => void;
	onPreview: (link: Link) => void;
	onCopy: (shortCode: string) => void;
}

export function LinksTable({
	data,
	isLoading,
	onSort,
	onEdit,
	onDelete,
	onPreview,
	onCopy,
}: LinksTableProps) {
	return (
		<div className="min-h-0 flex-1 overflow-auto rounded-md border">
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>
							<button
								type="button"
								className="inline-flex items-center gap-1"
								onClick={() => onSort("title")}
							>
								Title
								<ArrowUpDown className="h-3.5 w-3.5" />
							</button>
						</TableHead>
						<TableHead>Short Code</TableHead>
						<TableHead>Target URL</TableHead>
						<TableHead>Status</TableHead>
						<TableHead>
							<button
								type="button"
								className="inline-flex items-center gap-1"
								onClick={() => onSort("click_count")}
							>
								Clicks
								<ArrowUpDown className="h-3.5 w-3.5" />
							</button>
						</TableHead>
						<TableHead>
							<button
								type="button"
								className="inline-flex items-center gap-1"
								onClick={() => onSort("created_at")}
							>
								Created
								<ArrowUpDown className="h-3.5 w-3.5" />
							</button>
						</TableHead>
						<TableHead className="w-[50px]" />
					</TableRow>
				</TableHeader>
				<TableBody>
					{isLoading
						? Array.from({ length: 8 }).map((_, i) => (
								<TableRow key={`skeleton-${i}`}>
									<TableCell>
										<Skeleton className="h-4 w-24" />
									</TableCell>
									<TableCell>
										<Skeleton className="h-4 w-16" />
									</TableCell>
									<TableCell>
										<Skeleton className="h-4 w-40" />
									</TableCell>
									<TableCell>
										<Skeleton className="h-5 w-16 rounded-full" />
									</TableCell>
									<TableCell>
										<Skeleton className="h-4 w-8" />
									</TableCell>
									<TableCell>
										<Skeleton className="h-4 w-12" />
									</TableCell>
									<TableCell>
										<Skeleton className="h-8 w-8" />
									</TableCell>
								</TableRow>
							))
						: data?.items.map((link) => {
								const statusInfo = getLinkStatus(link);
								return (
									<TableRow key={link.id}>
										<TableCell className="font-medium">
											{link.title || "\u2014"}
										</TableCell>
										<TableCell className="font-mono text-xs">
											{link.short_code}
										</TableCell>
										<TableCell className="max-w-[250px] truncate text-muted-foreground">
											{link.target_url}
										</TableCell>
										<TableCell>
											<Badge variant={statusInfo.variant}>
												{statusInfo.label}
											</Badge>
										</TableCell>
										<TableCell className="text-right tabular-nums">
											{link.click_count}
										</TableCell>
										<TableCell className="text-muted-foreground">
											{getRelativeTime(link.created_at)}
										</TableCell>
										<TableCell>
											<LinkRowActions
												link={link}
												onEdit={onEdit}
												onDelete={onDelete}
												onPreview={onPreview}
												onCopy={onCopy}
											/>
										</TableCell>
									</TableRow>
								);
							})}
					{!isLoading && (!data?.items || data.items.length === 0) && (
						<TableRow>
							<TableCell
								colSpan={7}
								className="h-24 text-center text-muted-foreground"
							>
								No links found. Create your first link!
							</TableCell>
						</TableRow>
					)}
				</TableBody>
			</Table>
		</div>
	);
}
