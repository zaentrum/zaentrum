// End-to-end tests against a running zaentrum instance — the public demo by
// default. See README.md for the variables, the projects and the tags.
import { defineConfig, devices } from '@playwright/test';
import { authFile, env, type Account } from './support/env';

const CI = !!process.env.CI;

// A report from CI is an artifact other people can download. Traces carry
// request headers (bearer tokens) and a failure's page snapshot carries the
// text on screen, so CI keeps neither; screenshots mask who is signed in.
if (CI) process.env.PLAYWRIGHT_NO_COPY_PROMPT ??= '1';

const signedInAs = (account: Account) => ({ storageState: authFile(account), account });

export default defineConfig<{}, { account: Account }>({
  testDir: './tests',
  outputDir: './test-results',
  // A small cluster: a few calm workers, generous but bounded waits, and no
  // retries by default — a test that needs a retry to pass is reported.
  workers: Number(process.env.E2E_WORKERS ?? 2),
  retries: Number(process.env.E2E_RETRIES ?? 0),
  timeout: 90_000,
  expect: { timeout: 15_000 },
  forbidOnly: CI,
  // Next-round contract tests run only when asked for (E2E_NEXT=1).
  grepInvert: env.includeNext ? undefined : /@next\b/,
  reporter: [
    ['list'],
    ...(CI ? [['github'] as ['github']] : []),
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
  ],
  use: {
    ...devices['Desktop Chrome'],
    baseURL: env.baseURL,
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    // The web client registers a service worker that caches its shell; a
    // cached shell would hide a fresh deploy from the very test checking it.
    serviceWorkers: 'block',
    actionTimeout: 15_000,
    navigationTimeout: 45_000,
    trace: CI ? 'off' : 'retain-on-failure',
    // Failure screenshots come from support/fixtures.ts, masked.
    screenshot: 'off',
  },
  projects: [
    {
      name: 'setup',
      testMatch: /setup\/.*\.setup\.ts$/,
      use: { trace: 'off', screenshot: 'off', video: 'off' },
    },
    {
      name: 'chino',
      testMatch: /chino\/.*\.spec\.ts$/,
      dependencies: ['setup'],
      use: signedInAs('viewer'),
    },
    {
      name: 'api',
      testMatch: /api\/.*\.spec\.ts$/,
      dependencies: ['setup'],
      use: signedInAs('viewer'),
    },
    {
      name: 'console',
      testMatch: /console\/.*\.spec\.ts$/,
      dependencies: ['setup'],
      use: signedInAs('admin'),
    },
    {
      name: 'ui-changes',
      testMatch: /ui-changes\.spec\.ts$/,
      dependencies: ['setup'],
      use: signedInAs('viewer'),
    },
  ],
});
