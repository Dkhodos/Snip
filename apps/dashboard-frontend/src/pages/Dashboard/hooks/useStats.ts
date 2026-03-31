import { statsApi } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export function useStats() {
	return useQuery({ queryKey: ["stats"], queryFn: () => statsApi.getStats() });
}
