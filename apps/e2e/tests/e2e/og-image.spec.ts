import { test, expect } from '@playwright/test';
import { LinksPage } from './base/LinksPage.js';

const TEST_PREFIX = `e2e-og-${Date.now()}`;

function testLink(suffix: string) {
  return {
    title: `${TEST_PREFIX}-${suffix}`,
    targetUrl: 'https://example.com',
  };
}

/** Extract the short code from the first matching row. */
async function getShortCode(linksPage: LinksPage, title: string, page: import('@playwright/test').Page): Promise<string> {
  const row = page.getByRole('row').filter({ hasText: title });
  await expect(row).toBeVisible();
  const shortCodeCell = row.getByRole('cell').nth(1);
  return ((await shortCodeCell.textContent()) ?? '').trim();
}

test.describe('OG image preview', () => {
  let linksPage: LinksPage;
  const createdShortCodes: string[] = [];

  test.beforeEach(async ({ page }) => {
    linksPage = new LinksPage(page);
    await linksPage.navigate();
  });

  test.afterAll(async ({ browser }) => {
    if (createdShortCodes.length === 0) return;
    const context = await browser.newContext({ storageState: 'storageState.json' });
    const page = await context.newPage();
    const cleanup = new LinksPage(page);
    await cleanup.navigate();
    for (const shortCode of createdShortCodes) {
      try {
        await cleanup.deleteLink(shortCode);
      } catch {
        // best-effort cleanup
      }
    }
    await context.close();
  });

  test('opens OG preview dialog and shows title', async ({ page }) => {
    const link = testLink('dialog');
    await linksPage.createLink(link);
    const shortCode = await getShortCode(linksPage, link.title, page);
    createdShortCodes.push(shortCode);

    await linksPage.openOgPreview(shortCode);

    const dialog = linksPage.getOgDialog();
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText('OG Image Preview')).toBeVisible();
    await expect(dialog.getByText(link.title)).toBeVisible();

    await linksPage.closeOgDialog();
  });

  test('loads OG image in preview dialog', async ({ page }) => {
    const link = testLink('image');
    await linksPage.createLink(link);
    const shortCode = await getShortCode(linksPage, link.title, page);
    createdShortCodes.push(shortCode);

    await linksPage.openOgPreview(shortCode);
    await linksPage.waitForOgImageLoaded();

    const src = await linksPage.getOgImageSrc();
    expect(src).toBeTruthy();
    expect(src).toContain(shortCode);
    expect(src).toContain('.png');

    await linksPage.closeOgDialog();
  });

  test('regenerate button creates new image with cache bust', async ({ page }) => {
    const link = testLink('regen');
    await linksPage.createLink(link);
    const shortCode = await getShortCode(linksPage, link.title, page);
    createdShortCodes.push(shortCode);

    await linksPage.openOgPreview(shortCode);
    await linksPage.waitForOgImageLoaded();
    const srcBefore = await linksPage.getOgImageSrc();

    await linksPage.clickRegenerate();
    // Wait for the regeneration to complete — image reloads
    await linksPage.waitForOgImageLoaded();

    const srcAfter = await linksPage.getOgImageSrc();
    expect(srcAfter).toBeTruthy();
    // After regeneration the URL includes a ?t= cache-bust parameter
    expect(srcAfter).not.toBe(srcBefore);
    expect(srcAfter).toContain('?t=');

    await linksPage.closeOgDialog();
  });

  test('copy URL copies OG image URL to clipboard', async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);

    const link = testLink('copy');
    await linksPage.createLink(link);
    const shortCode = await getShortCode(linksPage, link.title, page);
    createdShortCodes.push(shortCode);

    await linksPage.openOgPreview(shortCode);
    await linksPage.waitForOgImageLoaded();
    await linksPage.clickCopyOgUrl();

    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    expect(clipboardText).toContain(shortCode);
    expect(clipboardText).toContain('.png');

    await linksPage.closeOgDialog();
  });

  test('close button dismisses dialog', async ({ page }) => {
    const link = testLink('close');
    await linksPage.createLink(link);
    const shortCode = await getShortCode(linksPage, link.title, page);
    createdShortCodes.push(shortCode);

    await linksPage.openOgPreview(shortCode);
    await expect(linksPage.getOgDialog()).toBeVisible();

    await linksPage.closeOgDialog();
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });
});
