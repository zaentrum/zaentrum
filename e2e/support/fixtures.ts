// The suite's `test`: Playwright's, plus
//   - a read-only guard on every browser context (support/readonly.ts),
//   - `snap(name)`: attach a full-page screenshot to the report,
//   - `open(app, path)`: open a page of an app with a live session,
//   - `api`: chino-api calls with the bearer token the signed-in web client holds.
import { test as base, expect, type APIRequestContext, type APIResponse } from '@playwright/test';
import { chino, type App } from './apps';
import { waitForToken, storedUser } from './auth';
import { authFile, env, type Account } from './env';
import { instanceConfig, webClient } from './instance';
import { guardReadOnly } from './readonly';
import { fullPageShot } from './screenshots';

export interface Api {
  /** GET a chino-api path ("/api/v1/items/<id>") with the account's token. */
  get(path: string): Promise<APIResponse>;
  /** GET, expect 200 and JSON, return the parsed body. */
  json<T = unknown>(path: string): Promise<T>;
}

interface TestFixtures {
  snap: (name: string) => Promise<void>;
  open: (app: App, path?: string) => Promise<void>;
  api: Api;
}

interface WorkerFixtures {
  /** Which signed-in account the project runs as (set per project). */
  account: Account;
  /** The web client's access token for that account, kept fresh. */
  bearer: { token(): Promise<string> };
}

export const test = base.extend<TestFixtures, WorkerFixtures>({
  account: ['viewer', { option: true, scope: 'worker' }],

  context: async ({ context }, use, testInfo) => {
    const blocked = new Set<string>();
    await guardReadOnly(context, (what) => blocked.add(what));
    await use(context);
    if (blocked.size) {
      testInfo.annotations.push({ type: 'blocked write', description: [...blocked].join('\n') });
    }
  },

  page: async ({ page }, use, testInfo) => {
    await use(page);
    // Instead of the built-in failure screenshot: this one masks who is signed in.
    if (testInfo.status !== testInfo.expectedStatus) {
      await fullPageShot(page, testInfo, 'at failure').catch(() => undefined);
    }
  },

  snap: async ({ page }, use, testInfo) => {
    await use((name) => fullPageShot(page, testInfo, name));
  },

  open: async ({ page }, use) => {
    await use(async (app, path = '/') => {
      // Land on the app's root first. With an expired access token the app
      // signs in again through the Keycloak session and returns to its root,
      // which would lose a deep link; afterwards the token is fresh.
      await page.goto(app.url('/'));
      const login = page.locator('#kc-form-login');
      await expect(app.signedIn(page).or(login), `${app.name} is signed in`).toBeVisible({ timeout: 45_000 });
      if (await login.isVisible()) {
        throw new Error(
          `${app.name} sent the browser to the Keycloak login form: the session the setup ` +
            'project saved has ended (a run longer than the realm’s session idle time?) — run again',
        );
      }
      if (path !== '/') await page.goto(app.url(path));
    });
  },

  bearer: [
    async ({ browser, account }, use) => {
      const cfg = await instanceConfig();
      const context = await browser.newContext({
        storageState: authFile(account),
        serviceWorkers: 'block',
        baseURL: env.baseURL,
      });
      await guardReadOnly(context, () => undefined);
      const page = await context.newPage();
      let loaded = false;
      const fresh = async () => {
        // The signed-in SPA renews its own token; read what it holds now
        // and reload it only when that token is about to expire.
        let user = loaded ? await storedUser(page, cfg.oidcIssuer, webClient(cfg)) : null;
        if (!user || (user.expires_at ?? 0) - Date.now() / 1000 < 60) {
          await page.goto(chino.url('/'));
          await chino.ready(page);
          loaded = true;
          user = await waitForToken(page, cfg.oidcIssuer, webClient(cfg));
        }
        return user.access_token;
      };
      let pending: Promise<string> | undefined;
      await use({
        // One lookup at a time, however many requests ask at once.
        token: () => (pending ??= fresh().finally(() => (pending = undefined))),
      });
      await context.close();
    },
    { scope: 'worker', timeout: 90_000 },
  ],

  api: async ({ playwright, bearer }, use) => {
    const request: APIRequestContext = await playwright.request.newContext({ baseURL: env.baseURL });
    const get = async (path: string) =>
      request.get(path, {
        headers: { Authorization: `Bearer ${await bearer.token()}`, Accept: 'application/json' },
      });
    await use({
      get,
      async json<T>(path: string) {
        const res = await get(path);
        expect(res.status(), `GET ${path}`).toBe(200);
        expect(res.headers()['content-type'] ?? '', `GET ${path} content type`).toContain('application/json');
        return (await res.json()) as T;
      },
    });
    await request.dispose();
  },
});

export { expect };
