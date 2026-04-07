import { expect, test } from "@playwright/test";
import { DashboardPage } from "./base/DashboardPage.js";
import { LinksPage } from "./base/LinksPage.js";

test.describe("Redirect flow", () => {
	test("visiting a redirect link increments the dashboard click count", async ({
		page,
		context,
	}) => {
		const dashboard = new DashboardPage(page);
		const links = new LinksPage(page);
		const redirectBase = process.env.E2E_REDIRECT_URL!;
		let shortCode = "";

		// ── Step 1: Record initial Total Clicks from dashboard ───────────────────
		await dashboard.navigate();
		const initialClicks = await dashboard.getStatValue("Total Clicks");

		// ── Step 2: Create a test link ───────────────────────────────────────────
		const title = `redirect-test-${Date.now()}`;
		await links.navigate();
		await links.createLink({ title, targetUrl: "https://example.com" });

		const row = page.getByRole("row").filter({ hasText: title });
		await expect(row).toBeVisible();
		shortCode = (
			(await row.getByRole("cell").nth(1).textContent()) ?? ""
		).trim();
		expect(shortCode).toBeTruthy();

		// ── Step 3: Visit the redirect URL in a separate tab ────────────────────
		// Redirect endpoint is /r/{short_code} on the redirect service
		const redirectPage = await context.newPage();
		await redirectPage.goto(`${redirectBase}/r/${shortCode}`);

		// Redirect service returns 302; Playwright follows it automatically
		await expect(redirectPage).toHaveURL(/example\.com/, { timeout: 15_000 });
		await redirectPage.close();

		// ── Step 4: Verify Total Clicks increased on the dashboard ───────────────
		// Click count is incremented synchronously in Postgres before the 302 is returned,
		// so it should be visible immediately on the next dashboard load.
		// Use toPass as a safety net in case of any brief propagation lag.
		await expect(async () => {
			await dashboard.navigate();
			const updatedClicks = await dashboard.getStatValue("Total Clicks");
			expect(updatedClicks).toBeGreaterThan(initialClicks);
		}).toPass({ timeout: 15_000, intervals: [1_000, 2_000, 3_000] });

		// ── Cleanup ──────────────────────────────────────────────────────────────
		await links.navigate();
		await links.deleteLink(shortCode);
	});
});
