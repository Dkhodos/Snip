import { Button } from "@/components/ui/button";

interface LinksPaginationProps {
	page: number;
	totalPages: number;
	onPrevious: () => void;
	onNext: () => void;
}

export function LinksPagination({
	page,
	totalPages,
	onPrevious,
	onNext,
}: LinksPaginationProps) {
	if (totalPages <= 1) return null;

	return (
		<div className="flex shrink-0 items-center justify-between">
			<p className="text-sm text-muted-foreground">
				Page {page} of {totalPages}
			</p>
			<div className="flex gap-2">
				<Button
					variant="outline"
					size="sm"
					onClick={onPrevious}
					disabled={page <= 1}
				>
					Previous
				</Button>
				<Button
					variant="outline"
					size="sm"
					onClick={onNext}
					disabled={page >= totalPages}
				>
					Next
				</Button>
			</div>
		</div>
	);
}
