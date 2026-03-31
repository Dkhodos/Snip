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

import { FlagsApi } from "../FlagsApi";

const api = new FlagsApi();

beforeEach(() => {
	vi.clearAllMocks();
});

describe("FlagsApi", () => {
	it("getAll calls GET /flags", async () => {
		const data = { dark_mode: true, beta_features: false };
		mockClient.get.mockResolvedValue({ data });
		const result = await api.getAll();
		expect(mockClient.get).toHaveBeenCalledWith("/flags", {
			params: undefined,
		});
		expect(result).toEqual(data);
	});
});
