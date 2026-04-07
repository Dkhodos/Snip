import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";
import { expect, test as setup } from "@playwright/test";

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = resolve(__dirname, "..", "..", "storageState.json");

setup("authenticate", async ({ page }) => {
	const baseUrl = process.env.E2E_BASE_URL!;

	// Route Clerk FAPI requests to inject the testing token (bypasses device verification)
	await setupClerkTestingToken({ page });

	await page.goto(baseUrl);
	await page.waitForLoadState("networkidle");

	// Sign in programmatically via Clerk backend — no UI form, no device check
	// clerk.signIn finds the user by email, creates a sign-in token, signs in via window.Clerk
	await clerk.signIn({
		page,
		emailAddress: process.env.E2E_EMAIL!,
	});

	// Wait for Clerk session to be active and app to redirect to dashboard
	await page.waitForURL(/\/dashboard/, { timeout: 20_000 });
	await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

	// Persist auth state (cookies + localStorage with Clerk session) for all test projects
	await page.context().storageState({ path: STATE_FILE });
});
