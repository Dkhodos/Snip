import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockClient } = vi.hoisted(() => {
	const mockClient = {
		get: vi.fn(),
		post: vi.fn(),
		patch: vi.fn(),
		delete: vi.fn(),
		defaults: { headers: { common: {} as Record<string, string> } },
	};
	return { mockClient };
});

vi.mock("axios", () => ({
	default: { create: () => mockClient },
}));

import { LinksApi } from "../LinksApi";

const api = new LinksApi();

beforeEach(() => {
	vi.clearAllMocks();
});

describe("BaseApi", () => {
	it("get delegates to sharedClient.get and unwraps data", async () => {
		mockClient.get.mockResolvedValue({ data: { items: [], total: 0 } });
		const result = await api.list();
		expect(mockClient.get).toHaveBeenCalledWith("/links", {
			params: expect.any(Object),
		});
		expect(result).toEqual({ items: [], total: 0 });
	});

	it("post delegates to sharedClient.post and unwraps data", async () => {
		const link = { id: "1", short_code: "abc" };
		mockClient.post.mockResolvedValue({ data: link });
		const result = await api.create({
			target_url: "https://example.com",
			title: "Test",
		});
		expect(mockClient.post).toHaveBeenCalledWith("/links", {
			target_url: "https://example.com",
			title: "Test",
		});
		expect(result).toEqual(link);
	});

	it("patch delegates to sharedClient.patch and unwraps data", async () => {
		const link = { id: "1", title: "Updated" };
		mockClient.patch.mockResolvedValue({ data: link });
		const result = await api.update("1", { title: "Updated" });
		expect(mockClient.patch).toHaveBeenCalledWith("/links/1", {
			title: "Updated",
		});
		expect(result).toEqual(link);
	});

	it("delete delegates to sharedClient.delete", async () => {
		mockClient.delete.mockResolvedValue({});
		await api.remove("1");
		expect(mockClient.delete).toHaveBeenCalledWith("/links/1");
	});

	it("propagates errors from axios", async () => {
		mockClient.get.mockRejectedValue(new Error("Network error"));
		await expect(api.list()).rejects.toThrow("Network error");
	});
});
