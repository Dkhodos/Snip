import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { type APIRequestContext, expect, test } from "@playwright/test";
import { getClerkToken } from "./utils/clerk.fixture.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = resolve(__dirname, "..", "..", "storageState.json");

const TEST_PREFIX = `system-test-${Date.now()}`;

let token: string;
let api: APIRequestContext;
const createdIds: string[] = [];

test.describe("Links system tests", () => {
	test.beforeAll(async ({ browser, playwright }) => {
		const baseUrl = process.env.E2E_BASE_URL!;
		const apiUrl = process.env.E2E_API_URL!;

		token = await getClerkToken(browser, baseUrl, STATE_FILE);

		api = await playwright.request.newContext({
			baseURL: apiUrl,
			extraHTTPHeaders: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
		});
	});

	test.afterAll(async () => {
		// Clean up all links created in this suite
		for (const id of createdIds) {
			try {
				await api.delete(`/links/${id}`);
			} catch {
				// best-effort cleanup
			}
		}
		await api.dispose();
	});

	test("POST /links creates a link and returns 201", async () => {
		const res = await api.post("/links", {
			data: {
				title: `${TEST_PREFIX}-create`,
				target_url: "https://example.com",
			},
		});

		expect(res.status()).toBe(201);

		const body = await res.json();
		expect(typeof body.id).toBe("string");
		expect(typeof body.short_code).toBe("string");
		expect(body.target_url).toBe("https://example.com");
		expect(body.title).toBe(`${TEST_PREFIX}-create`);
		expect(typeof body.is_active).toBe("boolean");
		expect(typeof body.click_count).toBe("number");

		createdIds.push(body.id);
	});

	test("GET /links returns paginated list", async () => {
		const res = await api.get("/links?page=1&limit=20");
		expect(res.status()).toBe(200);

		const body = await res.json();
		expect(Array.isArray(body.items)).toBe(true);
		expect(typeof body.total).toBe("number");
		expect(body.page).toBe(1);
		expect(body.limit).toBe(20);
	});

	test("GET /links/{id} returns a single link", async () => {
		const createRes = await api.post("/links", {
			data: {
				title: `${TEST_PREFIX}-get`,
				target_url: "https://example.com/get",
			},
		});
		const created = await createRes.json();
		createdIds.push(created.id);

		const res = await api.get(`/links/${created.id}`);
		expect(res.status()).toBe(200);

		const body = await res.json();
		expect(body.id).toBe(created.id);
		expect(body.target_url).toBe("https://example.com/get");
	});

	test("PATCH /links/{id} updates the link", async () => {
		const createRes = await api.post("/links", {
			data: {
				title: `${TEST_PREFIX}-patch`,
				target_url: "https://example.com/patch",
			},
		});
		const created = await createRes.json();
		createdIds.push(created.id);

		const res = await api.patch(`/links/${created.id}`, {
			data: { title: `${TEST_PREFIX}-patch-updated` },
		});
		expect(res.status()).toBe(200);

		const body = await res.json();
		expect(body.title).toBe(`${TEST_PREFIX}-patch-updated`);
	});

	test("DELETE /links/{id} removes the link", async () => {
		const createRes = await api.post("/links", {
			data: {
				title: `${TEST_PREFIX}-delete`,
				target_url: "https://example.com/delete",
			},
		});
		const created = await createRes.json();
		// Do NOT add to createdIds — we're deleting it here

		const deleteRes = await api.delete(`/links/${created.id}`);
		// Backend performs a soft-delete (deactivation); 204 confirms the operation succeeded
		expect(deleteRes.status()).toBe(204);
	});

	test("GET /links supports search query parameter", async () => {
		const res = await api.get(
			`/links?search=${encodeURIComponent(TEST_PREFIX)}&limit=20`,
		);
		expect(res.status()).toBe(200);

		const body = await res.json();
		expect(Array.isArray(body.items)).toBe(true);
	});
});
