import { expect } from "@playwright/test";
import { BasePage } from "./BasePage.js";

const STAT_LABELS = [
	"Total Links",
	"Total Clicks",
	"Active Links",
	"Expired Links",
] as const;

export class DashboardPage extends BasePage {
	readonly path = "/dashboard";

	async waitForLoad(): Promise<void> {
		await this.page.waitForLoadState("networkidle");
		await expect(this.getHeading("Dashboard")).toBeVisible();
	}

	statCard(label: (typeof STAT_LABELS)[number]) {
		return this.page.getByText(label).first();
	}

	clicksChart() {
		return this.page.locator(".recharts-wrapper").first();
	}

	async getStatValue(label: (typeof STAT_LABELS)[number]): Promise<number> {
		// DOM: <p class="text-3xl">{number}</p> is the preceding sibling of <p class="text-sm">{label}</p>
		const text = await this.page
			.locator("p.text-sm")
			.filter({ hasText: label })
			.locator("xpath=preceding-sibling::p[1]")
			.textContent();
		return parseInt((text ?? "0").trim(), 10);
	}

	async expectAllStatsVisible(): Promise<void> {
		for (const label of STAT_LABELS) {
			await expect(this.statCard(label)).toBeVisible();
		}
	}
}
