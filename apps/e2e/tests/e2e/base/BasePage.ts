import { expect, type Page } from "@playwright/test";

export abstract class BasePage {
	abstract readonly path: string;

	constructor(protected readonly page: Page) {}

	async navigate(): Promise<void> {
		await this.page.goto(this.path);
		await this.waitForLoad();
	}

	async waitForLoad(): Promise<void> {
		await this.page.waitForLoadState("networkidle");
	}

	async expectOnPage(): Promise<void> {
		await expect(this.page).toHaveURL(new RegExp(this.path));
	}

	getHeading(name: string) {
		return this.page.getByRole("heading", { name });
	}

	async takeScreenshot(name: string): Promise<void> {
		await this.page.screenshot({ path: `test-results/${name}.png` });
	}
}
