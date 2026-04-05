import { defineConfig, devices } from '@playwright/test';
import { clerkSetup } from '@clerk/testing/playwright';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: resolve(__dirname, '.env') });

// Side-effect: fetches CLERK_TESTING_TOKEN and sets CLERK_FAPI in process.env
// Must run before tests so setupClerkTestingToken can route Clerk FAPI requests
await clerkSetup();

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 1,
  reporter: [['html'], ['list']],
  use: {
    baseURL: process.env.E2E_BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'setup',
      testMatch: 'setup/auth.setup.ts',
    },
    {
      name: 'e2e',
      testMatch: 'e2e/**/*.spec.ts',
      dependencies: ['setup'],
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'storageState.json',
      },
    },
    {
      name: 'system',
      testMatch: 'system/**/*.spec.ts',
      dependencies: ['setup'],
      use: {
        storageState: 'storageState.json',
      },
    },
  ],
});
