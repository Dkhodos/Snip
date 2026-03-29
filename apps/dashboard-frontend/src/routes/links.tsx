import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  Search,
  ArrowUpDown,
  MoreHorizontal,
  Copy,
  Pencil,
  Trash2,
  Plus,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLinks } from "@/hooks/use-links";
import { LinkFormDialog } from "@/components/links/link-form-dialog";
import { DeleteLinkDialog } from "@/components/links/delete-link-dialog";
import type { Link } from "@/lib/api";

export const Route = createFileRoute("/links")({
  component: LinksPage,
});

type StatusFilter = "all" | "active" | "inactive" | "expired";

const statusFilters: { label: string; value: StatusFilter }[] = [
  { label: "All", value: "all" },
  { label: "Active", value: "active" },
  { label: "Inactive", value: "inactive" },
  { label: "Expired", value: "expired" },
];

function getRelativeTime(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60_000);
  const diffHours = Math.floor(diffMs / 3_600_000);
  const diffDays = Math.floor(diffMs / 86_400_000);
  const diffWeeks = Math.floor(diffDays / 7);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffWeeks < 4) return `${diffWeeks}w ago`;
  return date.toLocaleDateString();
}

function getLinkStatus(
  link: Link,
): { label: string; variant: "success" | "secondary" | "warning" } {
  if (!link.is_active) {
    return { label: "Inactive", variant: "secondary" };
  }
  if (link.expires_at && new Date(link.expires_at) < new Date()) {
    return { label: "Expired", variant: "warning" };
  }
  return { label: "Active", variant: "success" };
}

function LinksPage() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [status, setStatus] = useState<StatusFilter>("all");

  const [createOpen, setCreateOpen] = useState(false);
  const [editingLink, setEditingLink] = useState<Link | null>(null);
  const [deletingLink, setDeletingLink] = useState<Link | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading } = useLinks({
    page,
    limit: 20,
    search: debouncedSearch || undefined,
    sortBy,
    sortOrder,
    status: status === "all" ? undefined : status,
  });

  function handleSort(column: string) {
    if (sortBy === column) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
  }

  function handleCopyUrl(shortCode: string) {
    const baseUrl = window.location.origin.replace("dashboard.", "");
    navigator.clipboard.writeText(`${baseUrl}/${shortCode}`);
  }

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

      <div className="flex shrink-0 flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search links..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-1">
          {statusFilters.map((filter) => (
            <Button
              key={filter.value}
              variant={status === filter.value ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setStatus(filter.value);
                setPage(1);
              }}
            >
              {filter.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <button
                  type="button"
                  className="inline-flex items-center gap-1"
                  onClick={() => handleSort("title")}
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
                  onClick={() => handleSort("click_count")}
                >
                  Clicks
                  <ArrowUpDown className="h-3.5 w-3.5" />
                </button>
              </TableHead>
              <TableHead>
                <button
                  type="button"
                  className="inline-flex items-center gap-1"
                  onClick={() => handleSort("created_at")}
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
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-40" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-16 rounded-full" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-8" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-8" /></TableCell>
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
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => handleCopyUrl(link.short_code)}
                            >
                              <Copy className="mr-2 h-4 w-4" />
                              Copy URL
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => setEditingLink(link)}
                            >
                              <Pencil className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => setDeletingLink(link)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
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

      {totalPages > 1 && (
        <div className="flex shrink-0 items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      <LinkFormDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
      />

      <LinkFormDialog
        open={!!editingLink}
        onOpenChange={(open) => { if (!open) setEditingLink(null); }}
        link={editingLink}
      />

      <DeleteLinkDialog
        open={!!deletingLink}
        onOpenChange={(open) => { if (!open) setDeletingLink(null); }}
        link={deletingLink}
      />
    </div>
  );
}
