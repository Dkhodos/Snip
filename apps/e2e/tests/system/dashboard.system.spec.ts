import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { type APIRequestContext, expect, test } from "@playwright/test";
import { getClerkToken } from "./utils/clerk.fixture.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = resolve(__dirname, "..", "..", "storageState.json");

let token: string;
let api: APIRequestContext;

test.describe("Dashboard system tests", () => {
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
		await api.dispose();
	});

	test("GET /health returns 200", async () => {
		const res = await api.get("/health");
		expect(res.status()).toBe(200);
	});

	test("GET /stats returns correct shape", async () => {
		const res = await api.get("/stats");
		expect(res.status()).toBe(200);

		const body = await res.json();
		expect(typeof body.total_links).toBe("number");
		expect(typeof body.total_clicks).toBe("number");
		expect(typeof body.active_links).toBe("number");
		expect(typeof body.expired_links).toBe("number");

		expect(body.total_links).toBeGreaterThanOrEqual(0);
		expect(body.total_clicks).toBeGreaterThanOrEqual(0);
		expect(body.active_links).toBeGreaterThanOrEqual(0);
		expect(body.expired_links).toBeGreaterThanOrEqual(0);
	});

	test("GET /clicks/aggregate returns daily time-series", async () => {
		const res = await api.get("/clicks/aggregate");
		expect(res.status()).toBe(200);

		const body = await res.json();
		expect(Array.isArray(body.daily)).toBe(true);

		if (body.daily.length > 0) {
			const first = body.daily[0];
			expect(typeof first.date).toBe("string");
			expect(typeof first.count).toBe("number");
		}
	});
});
