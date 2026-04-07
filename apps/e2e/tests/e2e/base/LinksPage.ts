import { expect } from "@playwright/test";
import type {
	CreateLinkOptions,
	LinkStatus,
	UpdateLinkOptions,
} from "../types/links.types.js";
import { BasePage } from "./BasePage.js";

export class LinksPage extends BasePage {
	readonly path = "/links";

	async waitForLoad(): Promise<void> {
		await this.page.waitForLoadState("networkidle");
		await expect(this.getHeading("Links")).toBeVisible();
	}

	// ── Creation ────────────────────────────────────────────────────────────────

	async createLink(opts: CreateLinkOptions): Promise<void> {
		await this.page.getByRole("button", { name: /create link/i }).click();
		await this.page.waitForSelector('[role="dialog"]');

		const dialog = this.page.locator('[role="dialog"]');
		await dialog.locator("#title").fill(opts.title);
		await dialog.locator("#target_url").fill(opts.targetUrl);

		if (opts.shortCode) {
			await dialog.locator("#custom_code").fill(opts.shortCode);
		}

		await dialog.getByRole("button", { name: /^create link$/i }).click();
		await this.page.waitForSelector('[role="dialog"]', { state: "hidden" });
		await this.page.waitForLoadState("networkidle");
	}

	// ── Search & Filter ─────────────────────────────────────────────────────────

	async searchLinks(query: string): Promise<void> {
		const input = this.page.getByPlaceholder(/search/i);
		await input.fill(query);
		// Wait for the 300ms debounce + network request
		await this.page.waitForTimeout(400);
		await this.page.waitForLoadState("networkidle");
	}

	async filterByStatus(status: LinkStatus): Promise<void> {
		await this.page.getByRole("button", { name: status, exact: true }).click();
		await this.page.waitForLoadState("networkidle");
	}

	// ── Table interactions ───────────────────────────────────────────────────────

	getLinkRow(shortCode: string) {
		return this.page.getByRole("row").filter({ hasText: shortCode });
	}

	async expectLinkVisible(shortCode: string): Promise<void> {
		await expect(this.getLinkRow(shortCode)).toBeVisible();
	}

	async expectLinkNotVisible(shortCode: string): Promise<void> {
		await expect(this.getLinkRow(shortCode)).not.toBeVisible();
	}

	async sortBy(column: "Title" | "Clicks" | "Created"): Promise<void> {
		await this.page.getByRole("columnheader", { name: column }).click();
		await this.page.waitForLoadState("networkidle");
	}

	// ── Row actions ──────────────────────────────────────────────────────────────

	private async openRowMenu(shortCode: string): Promise<void> {
		const row = this.getLinkRow(shortCode);
		await row.getByRole("button").last().click();
		await this.page.waitForSelector('[role="menu"]');
	}

	async editLink(shortCode: string, updates: UpdateLinkOptions): Promise<void> {
		await this.openRowMenu(shortCode);
		await this.page.getByRole("menuitem", { name: /edit/i }).click();
		await this.page.waitForSelector('[role="dialog"]');

		const dialog = this.page.locator('[role="dialog"]');

		if (updates.title !== undefined) {
			await dialog.locator("#title").clear();
			await dialog.locator("#title").fill(updates.title);
		}

		if (updates.targetUrl !== undefined) {
			await dialog.locator("#target_url").clear();
			await dialog.locator("#target_url").fill(updates.targetUrl);
		}

		await dialog.getByRole("button", { name: /^save changes$/i }).click();
		await this.page.waitForSelector('[role="dialog"]', { state: "hidden" });
		await this.page.waitForLoadState("networkidle");
	}

	async deleteLink(shortCode: string): Promise<void> {
		await this.openRowMenu(shortCode);
		await this.page.getByRole("menuitem", { name: /delete/i }).click();

		// Confirm deletion in the alert dialog
		await this.page.waitForSelector('[role="alertdialog"]');
		await this.page
			.getByRole("button", { name: /delete/i })
			.last()
			.click();
		await this.page.waitForSelector('[role="alertdialog"]', {
			state: "hidden",
		});
		await this.page.waitForLoadState("networkidle");
	}

	async copyLinkUrl(shortCode: string): Promise<void> {
		await this.openRowMenu(shortCode);
		await this.page.getByRole("menuitem", { name: /copy url/i }).click();
	}

	// ── OG Preview ──────────────────────────────────────────────────────────────

	async openOgPreview(shortCode: string): Promise<void> {
		await this.openRowMenu(shortCode);
		await this.page
			.getByRole("menuitem", { name: /preview og image/i })
			.click();
		await this.page.waitForSelector('[role="dialog"]');
	}

	getOgDialog() {
		return this.page
			.locator('[role="dialog"]')
			.filter({ hasText: /OG Image Preview/i });
	}

	async waitForOgImageLoaded(): Promise<void> {
		const dialog = this.getOgDialog();
		await dialog
			.locator('img[alt="OG preview"]')
			.waitFor({ state: "visible", timeout: 20_000 });
	}

	async clickRegenerate(): Promise<void> {
		const dialog = this.getOgDialog();
		await dialog.getByRole("button", { name: /regenerate/i }).click();
	}

	async clickCopyOgUrl(): Promise<void> {
		const dialog = this.getOgDialog();
		await dialog.getByRole("button", { name: /copy url/i }).click();
	}

	async closeOgDialog(): Promise<void> {
		// Press Escape to close — avoids ambiguity between X button and footer Close button
		await this.page.keyboard.press("Escape");
		await this.page.waitForSelector('[role="dialog"]', { state: "hidden" });
	}

	getOgImageSrc(): Promise<string | null> {
		const dialog = this.getOgDialog();
		return dialog.locator('img[alt="OG preview"]').getAttribute("src");
	}

	// ── Pagination ───────────────────────────────────────────────────────────────

	async nextPage(): Promise<void> {
		await this.page.getByRole("button", { name: /next/i }).click();
		await this.page.waitForLoadState("networkidle");
	}

	async prevPage(): Promise<void> {
		await this.page.getByRole("button", { name: /previous/i }).click();
		await this.page.waitForLoadState("networkidle");
	}
}
