import { test, expect, type APIRequestContext } from '@playwright/test';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getClerkToken } from './utils/clerk.fixture.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = resolve(__dirname, '..', '..', 'storageState.json');

const TEST_PREFIX = `system-og-${Date.now()}`;

let token: string;
let api: APIRequestContext;
const createdIds: string[] = [];

test.describe('OG image system tests', () => {
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

  async function createTestLink(suffix: string) {
    const res = await api.post('/links', {
      data: {
        title: `${TEST_PREFIX}-${suffix}`,
        target_url: 'https://example.com',
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    createdIds.push(body.id);
    return body;
  }

  test('GET /links/{id}/og-image-url returns deterministic URL', async () => {
    const link = await createTestLink('url');

    const res = await api.get(`/links/${link.id}/og-image-url`);
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.og_image_url).toContain(link.short_code);
    expect(body.og_image_url).toContain('.png');
  });

  test('GET /links/{id}/og-image-url is deterministic across calls', async () => {
    const link = await createTestLink('deterministic');

    const res1 = await api.get(`/links/${link.id}/og-image-url`);
    const res2 = await api.get(`/links/${link.id}/og-image-url`);

    const body1 = await res1.json();
    const body2 = await res2.json();
    expect(body1.og_image_url).toBe(body2.og_image_url);
  });

  test('POST /links/{id}/og-image generates image and returns URL', async () => {
    const link = await createTestLink('generate');

    const res = await api.post(`/links/${link.id}/og-image`);
    expect(res.status()).toBe(200);

    const body = await res.json();
    expect(body.og_image_url).toBeTruthy();
    expect(body.og_image_url).toContain('.png');
  });

  test('generated OG image is fetchable via URL', async ({ playwright }) => {
    const link = await createTestLink('fetch');

    const genRes = await api.post(`/links/${link.id}/og-image`);
    expect(genRes.status()).toBe(200);
    const { og_image_url } = await genRes.json();

    // Fetch the image directly (no auth needed — public bucket)
    const publicApi = await playwright.request.newContext();
    const imgRes = await publicApi.get(og_image_url);
    expect(imgRes.status()).toBe(200);

    const contentType = imgRes.headers()['content-type'] ?? '';
    expect(contentType).toMatch(/^image\//);

    await publicApi.dispose();
  });

  test('GET /links/{id}/og-image-url returns 404 for nonexistent link', async () => {
    const fakeId = '00000000-0000-0000-0000-000000000000';
    const res = await api.get(`/links/${fakeId}/og-image-url`);
    expect(res.status()).toBe(404);
  });

  test('POST /links/{id}/og-image returns 404 for nonexistent link', async () => {
    const fakeId = '00000000-0000-0000-0000-000000000000';
    const res = await api.post(`/links/${fakeId}/og-image`);
    expect(res.status()).toBe(404);
  });
});
