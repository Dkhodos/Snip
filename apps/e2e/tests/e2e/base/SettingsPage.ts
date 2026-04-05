import { type Page, expect } from '@playwright/test';
import { BasePage } from './BasePage.js';

export class SettingsPage extends BasePage {
  readonly path = '/settings';

  constructor(page: Page) {
    super(page);
  }

  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    await expect(this.getHeading('Settings')).toBeVisible();
  }

  orgNameInput() {
    return this.page.getByLabel(/organization name/i).first();
  }

  orgImageSection() {
    return this.page.getByText('Organization image').first();
  }

  membersSection() {
    return this.page.getByText(/members/i).first();
  }
}
