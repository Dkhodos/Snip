import { type Page } from '@playwright/test';
import { BasePage } from './BasePage.js';

export class LoginPage extends BasePage {
  readonly path = '/';

  constructor(page: Page) {
    super(page);
  }

  async waitForLoad(): Promise<void> {
    await this.page.waitForSelector('input[name="identifier"]', { timeout: 15_000 });
  }

  async login(email: string, password: string): Promise<void> {
    await this.page.fill('input[name="identifier"]', email);
    await this.page.getByRole('button', { name: /continue/i }).click();

    await this.page.waitForSelector('input[type="password"]', { timeout: 10_000 });
    await this.page.fill('input[type="password"]', password);
    await this.page.getByRole('button', { name: /continue/i }).click();

    await this.page.waitForURL(/\/dashboard/, { timeout: 20_000 });
  }
}
