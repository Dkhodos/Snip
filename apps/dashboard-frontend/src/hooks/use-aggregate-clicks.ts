import { useQuery } from "@tanstack/react-query";
import { fetchAggregateClicks } from "@/lib/api";

export function useAggregateClicks() {
  return useQuery({
    queryKey: ["clicks", "aggregate"],
    queryFn: fetchAggregateClicks,
  });
}
