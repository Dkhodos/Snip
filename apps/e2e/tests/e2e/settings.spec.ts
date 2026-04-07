import { expect, test } from "@playwright/test";
import { SettingsPage } from "./base/SettingsPage.js";

test.describe("Settings page", () => {
	let settingsPage: SettingsPage;

	test.beforeEach(async ({ page }) => {
		settingsPage = new SettingsPage(page);
		await settingsPage.navigate();
	});

	test("shows Settings heading", async () => {
		await expect(settingsPage.getHeading("Settings")).toBeVisible();
	});

	test("org name input is visible", async () => {
		await expect(settingsPage.orgNameInput()).toBeVisible();
	});

	test("organization image section is visible", async () => {
		await expect(settingsPage.orgImageSection()).toBeVisible();
	});

	test("members section is visible", async () => {
		await expect(settingsPage.membersSection()).toBeVisible();
	});
});
