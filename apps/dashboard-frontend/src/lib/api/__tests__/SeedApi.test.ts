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

import { SeedApi } from "../SeedApi";

const api = new SeedApi();

beforeEach(() => {
	vi.clearAllMocks();
});

describe("SeedApi", () => {
	it("seed calls POST /dev/seed", async () => {
		const data = { message: "Seeded", links_created: 5 };
		mockClient.post.mockResolvedValue({ data });
		const result = await api.seed();
		expect(mockClient.post).toHaveBeenCalledWith("/dev/seed", undefined);
		expect(result).toEqual(data);
	});
});
