import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

// Clerk token injection
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

// Types
export interface Link {
  id: string;
  org_id: string;
  short_code: string;
  target_url: string;
  title: string | null;
  click_count: number;
  is_active: boolean;
  created_by: string | null;
  created_at: string;
  expires_at: string | null;
}

export interface LinkListResponse {
  items: Link[];
  total: number;
  page: number;
  limit: number;
}

export interface CreateLinkRequest {
  target_url: string;
  title: string;
  custom_short_code?: string;
}

export interface UpdateLinkRequest {
  target_url?: string;
  title?: string;
  is_active?: boolean;
}

export interface DailyClicks {
  date: string;
  count: number;
}

export interface ClicksResponse {
  link_id: string;
  total_clicks: number;
  daily: DailyClicks[];
}

export interface StatsResponse {
  total_links: number;
  total_clicks: number;
  active_links: number;
  expired_links: number;
}

export interface AggregateClicksResponse {
  daily: DailyClicks[];
}

export type FeatureFlags = Record<string, boolean>;

// API functions
export async function fetchLinks(
  page = 1,
  limit = 20,
  search?: string,
  sort_by?: string,
  sort_order?: string,
  status?: string,
): Promise<LinkListResponse> {
  const { data } = await api.get<LinkListResponse>("/links", {
    params: { page, limit, search, sort_by, sort_order, status },
  });
  return data;
}

export async function fetchLink(id: string): Promise<Link> {
  const { data } = await api.get<Link>(`/links/${id}`);
  return data;
}

export async function createLink(body: CreateLinkRequest): Promise<Link> {
  const { data } = await api.post<Link>("/links", body);
  return data;
}

export async function updateLink(id: string, body: UpdateLinkRequest): Promise<Link> {
  const { data } = await api.patch<Link>(`/links/${id}`, body);
  return data;
}

export async function deleteLink(id: string): Promise<void> {
  await api.delete(`/links/${id}`);
}

export async function fetchClicks(linkId: string): Promise<ClicksResponse> {
  const { data } = await api.get<ClicksResponse>(`/links/${linkId}/clicks`);
  return data;
}

export async function fetchFlags(): Promise<FeatureFlags> {
  const { data } = await api.get<FeatureFlags>("/flags");
  return data;
}

export async function fetchStats(): Promise<StatsResponse> {
  const { data } = await api.get<StatsResponse>("/stats");
  return data;
}

export async function fetchAggregateClicks(): Promise<AggregateClicksResponse> {
  const { data } = await api.get<AggregateClicksResponse>("/clicks/aggregate");
  return data;
}

export async function seedDevData(): Promise<{ message: string; links_created: number }> {
  const { data } = await api.post("/dev/seed");
  return data;
}
