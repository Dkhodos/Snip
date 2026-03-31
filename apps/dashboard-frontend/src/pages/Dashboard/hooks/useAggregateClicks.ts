import { clicksApi } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export function useAggregateClicks() {
	return useQuery({
		queryKey: ["clicks", "aggregate"],
		queryFn: () => clicksApi.getAggregate(),
	});
}
