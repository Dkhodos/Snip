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
