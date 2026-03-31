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

import { LinksApi } from "../LinksApi";

const api = new LinksApi();

beforeEach(() => {
	vi.clearAllMocks();
});

describe("LinksApi", () => {
	describe("list", () => {
		it("sends default page and limit", async () => {
			mockClient.get.mockResolvedValue({ data: { items: [], total: 0 } });
			await api.list();
			expect(mockClient.get).toHaveBeenCalledWith("/links", {
				params: {
					page: 1,
					limit: 20,
					search: undefined,
					sort_by: undefined,
					sort_order: undefined,
					status: undefined,
				},
			});
		});

		it("maps camelCase params to snake_case", async () => {
			mockClient.get.mockResolvedValue({ data: { items: [], total: 0 } });
			await api.list(2, 10, "test", "click_count", "desc", "active");
			expect(mockClient.get).toHaveBeenCalledWith("/links", {
				params: {
					page: 2,
					limit: 10,
					search: "test",
					sort_by: "click_count",
					sort_order: "desc",
					status: "active",
				},
			});
		});
	});

	describe("getById", () => {
		it("calls GET /links/:id", async () => {
			mockClient.get.mockResolvedValue({ data: { id: "abc" } });
			const result = await api.getById("abc");
			expect(mockClient.get).toHaveBeenCalledWith("/links/abc", {
				params: undefined,
			});
			expect(result).toEqual({ id: "abc" });
		});
	});

	describe("create", () => {
		it("calls POST /links with body", async () => {
			const body = { target_url: "https://example.com", title: "New" };
			mockClient.post.mockResolvedValue({ data: { id: "1", ...body } });
			const result = await api.create(body);
			expect(mockClient.post).toHaveBeenCalledWith("/links", body);
			expect(result.title).toBe("New");
		});
	});

	describe("update", () => {
		it("calls PATCH /links/:id with body", async () => {
			const body = { title: "Updated" };
			mockClient.patch.mockResolvedValue({ data: { id: "1", ...body } });
			const result = await api.update("1", body);
			expect(mockClient.patch).toHaveBeenCalledWith("/links/1", body);
			expect(result.title).toBe("Updated");
		});
	});

	describe("remove", () => {
		it("calls DELETE /links/:id", async () => {
			mockClient.delete.mockResolvedValue({});
			await api.remove("abc");
			expect(mockClient.delete).toHaveBeenCalledWith("/links/abc");
		});
	});
});
