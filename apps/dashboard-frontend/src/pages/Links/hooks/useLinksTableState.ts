import { useEffect, useState } from "react";
import type { StatusFilter } from "../types";

interface LinksTableState {
	search: string;
	debouncedSearch: string;
	page: number;
	sortBy: string;
	sortOrder: "asc" | "desc";
	status: StatusFilter;
	setSearch: (value: string) => void;
	setPage: (value: number) => void;
	setStatus: (value: StatusFilter) => void;
	handleSort: (column: string) => void;
}

export function useLinksTableState(): LinksTableState {
	const [search, setSearch] = useState("");
	const [debouncedSearch, setDebouncedSearch] = useState("");
	const [page, setPage] = useState(1);
	const [sortBy, setSortBy] = useState("created_at");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
	const [status, setStatus] = useState<StatusFilter>("all");

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearch(search);
			setPage(1);
		}, 300);
		return () => clearTimeout(timer);
	}, [search]);

	function handleSort(column: string) {
		if (sortBy === column) {
			setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
		} else {
			setSortBy(column);
			setSortOrder("asc");
		}
	}

	return {
		search,
		debouncedSearch,
		page,
		sortBy,
		sortOrder,
		status,
		setSearch,
		setPage,
		setStatus,
		handleSort,
	};
}
