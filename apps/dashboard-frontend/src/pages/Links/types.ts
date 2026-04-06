export type StatusFilter = "all" | "active" | "inactive" | "expired";

export const STATUS_FILTERS: { label: string; value: StatusFilter }[] = [
	{ label: "All", value: "all" },
	{ label: "Active", value: "active" },
	{ label: "Inactive", value: "inactive" },
	{ label: "Expired", value: "expired" },
];
