import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { fetchLinks } from "@/lib/api";

interface UseLinksParams {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: string;
  status?: string;
}

export function useLinks(params: UseLinksParams = {}) {
  const { page = 1, limit = 20, search, sortBy, sortOrder, status } = params;
  return useQuery({
    queryKey: ["links", { page, limit, search, sortBy, sortOrder, status }],
    queryFn: () => fetchLinks(page, limit, search, sortBy, sortOrder, status),
    placeholderData: keepPreviousData,
  });
}
