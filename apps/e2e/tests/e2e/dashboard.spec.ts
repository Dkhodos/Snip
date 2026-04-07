import { expect, test } from "@playwright/test";
import { DashboardPage } from "./base/DashboardPage.js";

test.describe("Dashboard page", () => {
	let dashboard: DashboardPage;

	test.beforeEach(async ({ page }) => {
		dashboard = new DashboardPage(page);
		await dashboard.navigate();
	});

	test("shows Dashboard heading", async () => {
		await expect(dashboard.getHeading("Dashboard")).toBeVisible();
	});

	test("renders all four stat cards", async () => {
		await dashboard.expectAllStatsVisible();
	});

	test("renders the clicks chart", async () => {
		await expect(dashboard.clicksChart()).toBeVisible();
	});
});
