import { type Browser } from '@playwright/test';
import { createClerkClient } from '@clerk/backend';

/**
 * Extracts a live Clerk JWT from the already-authenticated browser storage state.
 * Loads storageState into a headless context, navigates to the app so Clerk
 * initialises, then calls window.Clerk.session.getToken() to retrieve a fresh JWT.
 */
export async function getClerkToken(
  browser: Browser,
  baseUrl: string,
  storageStatePath: string,
): Promise<string> {
  const context = await browser.newContext({ storageState: storageStatePath });
  const page = await context.newPage();

  try {
    await page.goto(baseUrl);
    await page.waitForLoadState('networkidle');

    const token = await page.evaluate<string>(() => {
      return new Promise((resolve, reject) => {
        const clerk = (window as unknown as { Clerk?: { session?: { getToken: () => Promise<string> } } }).Clerk;
        if (!clerk?.session) {
          reject(new Error('Clerk session not found — auth setup may have failed'));
          return;
        }
        clerk.session.getToken().then(resolve).catch(reject);
      });
    });

    if (!token) throw new Error('Clerk returned an empty token');
    return token;
  } finally {
    await context.close();
  }
}

/**
 * Smoke-checks that the Clerk secret key is valid by listing users.
 * Throws if the secret key is missing or invalid.
 */
export async function verifyClerkConnection(): Promise<void> {
  const secretKey = process.env.CLERK_SECRET_KEY;
  if (!secretKey) throw new Error('CLERK_SECRET_KEY is not set in .env');

  const clerk = createClerkClient({ secretKey });
  await clerk.users.getUserList({ limit: 1 });
}
