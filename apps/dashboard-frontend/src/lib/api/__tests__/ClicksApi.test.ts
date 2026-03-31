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

import { ClicksApi } from "../ClicksApi";

const api = new ClicksApi();

beforeEach(() => {
	vi.clearAllMocks();
});

describe("ClicksApi", () => {
	it("getForLink calls GET /links/:id/clicks", async () => {
		const data = { link_id: "link-1", total_clicks: 5, daily: [] };
		mockClient.get.mockResolvedValue({ data });
		const result = await api.getForLink("link-1");
		expect(mockClient.get).toHaveBeenCalledWith("/links/link-1/clicks", {
			params: undefined,
		});
		expect(result).toEqual(data);
	});

	it("getAggregate calls GET /clicks/aggregate", async () => {
		const data = { daily: [{ date: "2025-01-01", count: 10 }] };
		mockClient.get.mockResolvedValue({ data });
		const result = await api.getAggregate();
		expect(mockClient.get).toHaveBeenCalledWith("/clicks/aggregate", {
			params: undefined,
		});
		expect(result).toEqual(data);
	});
});
