import { Button } from "@/components/ui/button";
import type { Link } from "@/lib/api";
import { Plus } from "lucide-react";
import { useState } from "react";
import { DeleteLinkDialog } from "./components/DeleteLinkDialog";
import { LinkFormDialog } from "./components/LinkFormDialog";
import { LinksPagination } from "./components/LinksPagination";
import { LinksTable } from "./components/LinksTable";
import { LinksToolbar } from "./components/LinksToolbar";
import { OgPreviewDialog } from "./components/OgPreviewDialog";
import { useCopyUrl } from "./hooks/useCopyUrl";
import { useLinks } from "./hooks/useLinks";
import { useLinksTableState } from "./hooks/useLinksTableState";

export function LinksPage() {
	const tableState = useLinksTableState();
	const { copy } = useCopyUrl();

	const { data, isLoading } = useLinks({
		page: tableState.page,
		limit: 20,
		search: tableState.debouncedSearch || undefined,
		sortBy: tableState.sortBy,
		sortOrder: tableState.sortOrder,
		status: tableState.status === "all" ? undefined : tableState.status,
	});

	const [createOpen, setCreateOpen] = useState(false);
	const [editingLink, setEditingLink] = useState<Link | null>(null);
	const [deletingLink, setDeletingLink] = useState<Link | null>(null);
	const [previewingLink, setPreviewingLink] = useState<Link | null>(null);

	const totalPages = data ? Math.ceil(data.total / data.limit) : 0;

	return (
		<div className="flex h-full flex-col gap-6 overflow-hidden">
			<div className="flex shrink-0 items-center justify-between">
				<h1 className="text-2xl font-bold">Links</h1>
				<Button onClick={() => setCreateOpen(true)}>
					<Plus className="mr-2 h-4 w-4" />
					Create Link
				</Button>
			</div>

			<LinksToolbar
				search={tableState.search}
				onSearchChange={tableState.setSearch}
				status={tableState.status}
				onStatusChange={(value) => {
					tableState.setStatus(value);
					tableState.setPage(1);
				}}
			/>

			<LinksTable
				data={data}
				isLoading={isLoading}
				sortBy={tableState.sortBy}
				sortOrder={tableState.sortOrder}
				onSort={tableState.handleSort}
				onEdit={setEditingLink}
				onDelete={setDeletingLink}
				onPreview={setPreviewingLink}
				onCopy={copy}
			/>

			<LinksPagination
				page={tableState.page}
				totalPages={totalPages}
				onPrevious={() => tableState.setPage(Math.max(1, tableState.page - 1))}
				onNext={() =>
					tableState.setPage(Math.min(totalPages, tableState.page + 1))
				}
			/>

			<LinkFormDialog open={createOpen} onOpenChange={setCreateOpen} />

			<LinkFormDialog
				open={!!editingLink}
				onOpenChange={(open) => {
					if (!open) setEditingLink(null);
				}}
				link={editingLink}
			/>

			<DeleteLinkDialog
				open={!!deletingLink}
				onOpenChange={(open) => {
					if (!open) setDeletingLink(null);
				}}
				link={deletingLink}
			/>

			<OgPreviewDialog
				open={!!previewingLink}
				onOpenChange={(open) => {
					if (!open) setPreviewingLink(null);
				}}
				link={previewingLink}
			/>
		</div>
	);
}
