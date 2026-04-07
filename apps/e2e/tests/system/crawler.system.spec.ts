import { test, expect, type APIRequestContext } from '@playwright/test';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getClerkToken } from './utils/clerk.fixture.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = resolve(__dirname, '..', '..', 'storageState.json');

const TEST_PREFIX = `system-crawler-${Date.now()}`;
const REDIRECT_BASE = process.env.E2E_REDIRECT_URL!;

const BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

const CRAWLER_UAS = {
  twitterbot: 'Twitterbot/1.0',
  slackbot: 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)',
  facebook: 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
  linkedin: 'LinkedInBot/1.0 (compatible; Mozilla/5.0)',
} as const;

let token: string;
let api: APIRequestContext;
const createdIds: string[] = [];

let testShortCode: string;
let xssShortCode: string;

test.describe('Crawler detection system tests', () => {
  test.beforeAll(async ({ browser, playwright }) => {
    const baseUrl = process.env.E2E_BASE_URL!;
    const apiUrl = process.env.E2E_API_URL!;

    token = await getClerkToken(browser, baseUrl, STATE_FILE);

    api = await playwright.request.newContext({
      baseURL: apiUrl,
      extraHTTPHeaders: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    // Create a test link and generate its OG image
    const linkRes = await api.post('/links', {
      data: {
        title: `${TEST_PREFIX}-crawler`,
        target_url: 'https://example.com',
      },
    });
    const link = await linkRes.json();
    createdIds.push(link.id);
    testShortCode = link.short_code;

    // Pre-generate OG image so it exists for crawler tests
    await api.post(`/links/${link.id}/og-image`);

    // Create a link with XSS title for escaping test
    const xssRes = await api.post('/links', {
      data: {
        title: '<script>alert(1)</script>',
        target_url: 'https://example.com/xss',
      },
    });
    const xssLink = await xssRes.json();
    createdIds.push(xssLink.id);
    xssShortCode = xssLink.short_code;
  });

  test.afterAll(async () => {
    for (const id of createdIds) {
      try {
        await api.delete(`/links/${id}`);
      } catch {
        // best-effort cleanup
      }
    }
    await api.dispose();
  });

  test('browser UA gets 302 redirect', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': BROWSER_UA },
      maxRedirects: 0,
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${testShortCode}`);
    expect(res.status()).toBe(302);
    expect(res.headers()['location']).toContain('example.com');

    await ctx.dispose();
  });

  test('Twitterbot gets 200 with OG HTML', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.twitterbot },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${testShortCode}`);
    expect(res.status()).toBe(200);
    expect(res.headers()['content-type']).toContain('text/html');

    await ctx.dispose();
  });

  test('Slackbot gets 200 with OG HTML', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.slackbot },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${testShortCode}`);
    expect(res.status()).toBe(200);

    await ctx.dispose();
  });

  test('facebookexternalhit gets 200 with OG HTML', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.facebook },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${testShortCode}`);
    expect(res.status()).toBe(200);

    await ctx.dispose();
  });

  test('LinkedInBot gets 200 with OG HTML', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.linkedin },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${testShortCode}`);
    expect(res.status()).toBe(200);

    await ctx.dispose();
  });

  test('OG HTML contains required meta tags', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.twitterbot },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${testShortCode}`);
    expect(res.status()).toBe(200);

    const html = await res.text();

    // OpenGraph meta tags
    expect(html).toContain('og:title');
    expect(html).toContain('og:description');
    expect(html).toContain('og:image');
    expect(html).toContain('og:url');

    // Twitter card meta tags
    expect(html).toContain('twitter:card');
    expect(html).toContain('twitter:image');

    // Meta refresh for crawler fallback
    expect(html).toContain('http-equiv="refresh"');

    // OG image URL contains the short code
    expect(html).toContain(`${testShortCode}.png`);

    await ctx.dispose();
  });

  test('OG HTML escapes title to prevent XSS', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.twitterbot },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/${xssShortCode}`);
    expect(res.status()).toBe(200);

    const html = await res.text();

    // Title should be HTML-escaped
    expect(html).toContain('&lt;script&gt;');
    expect(html).not.toContain('<script>alert(1)</script>');

    await ctx.dispose();
  });

  test('nonexistent short code returns 404', async ({ playwright }) => {
    const ctx = await playwright.request.newContext({
      extraHTTPHeaders: { 'user-agent': CRAWLER_UAS.twitterbot },
    });

    const res = await ctx.get(`${REDIRECT_BASE}/r/nonexistent-${Date.now()}`);
    expect(res.status()).toBe(404);

    await ctx.dispose();
  });
});
