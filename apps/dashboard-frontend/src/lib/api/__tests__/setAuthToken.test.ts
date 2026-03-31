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

import { setAuthToken } from "../BaseApi";

beforeEach(() => {
	mockClient.defaults.headers.common = {};
});

describe("setAuthToken", () => {
	it("sets Bearer token on shared client", () => {
		setAuthToken("my-token");
		expect(mockClient.defaults.headers.common.Authorization).toBe(
			"Bearer my-token",
		);
	});

	it("removes Authorization header when null", () => {
		setAuthToken("my-token");
		setAuthToken(null);
		expect(mockClient.defaults.headers.common.Authorization).toBeUndefined();
	});
});
