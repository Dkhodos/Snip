import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockClient } = vi.hoisted(() => {
	const mockClient = {
		get: vi.fn(),
		post: vi.fn(),
		patch: vi.fn(),
		delete: vi.fn(),
		defaults: { headers: { common: {} } },
	};
	return { mockClient };
});

vi.mock("axios", () => ({
	default: { create: () => mockClient },
}));

import { StatsApi } from "../StatsApi";

const api = new StatsApi();

beforeEach(() => {
	vi.clearAllMocks();
});

describe("StatsApi", () => {
	it("getStats calls GET /stats", async () => {
		const data = {
			total_links: 10,
			total_clicks: 100,
			active_links: 8,
			expired_links: 2,
		};
		mockClient.get.mockResolvedValue({ data });
		const result = await api.getStats();
		expect(mockClient.get).toHaveBeenCalledWith("/stats", {
			params: undefined,
		});
		expect(result).toEqual(data);
	});
});
