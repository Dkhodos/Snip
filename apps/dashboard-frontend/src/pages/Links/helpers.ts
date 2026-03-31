import type { Link } from "@/lib/api";

export function getRelativeTime(dateStr: string): string {
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

export function getLinkStatus(link: Link): {
	label: string;
	variant: "success" | "secondary" | "warning";
} {
	if (!link.is_active) {
		return { label: "Inactive", variant: "secondary" };
	}
	if (link.expires_at && new Date(link.expires_at) < new Date()) {
		return { label: "Expired", variant: "warning" };
	}
	return { label: "Active", variant: "success" };
}
