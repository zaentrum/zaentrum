// Signing in through the instance's real Keycloak login page, and reading
// the access token a signed-in single-page app holds.
import { expect, type Page } from '@playwright/test';
import { credentials, type Account } from './env';

/** Make an account's credentials available to the page's login form.
 *
 *  They reach the form through a binding the page calls, never as an argument
 *  of a Playwright call: those arguments are written into the report's steps
 *  (`Fill "…" locator('#password')`), and a report from CI is an artifact
 *  others can download. Call it before the page navigates; it returns the
 *  binding's name for signInOnKeycloak(). */
export async function exposeCredentials(page: Page, account: Account): Promise<string> {
  const { username, password } = credentials(account);
  const name = `__e2eCredential_${Math.random().toString(36).slice(2)}`;
  await page.exposeBinding(name, (_source, field: unknown) => (field === 'password' ? password : username));
  return name;
}

/** Fill and submit the Keycloak login form the app redirected to.
 *  Selectors are the stock Keycloak ids (#username, #password, #kc-login),
 *  which the instance's own login theme keeps, so any instance works. */
export async function signInOnKeycloak(page: Page, account: Account, binding: string): Promise<void> {
  await page.locator('#username').waitFor({ state: 'visible', timeout: 45_000 });
  await page.evaluate(async (name) => {
    const credential = (window as unknown as Record<string, (field: string) => Promise<string>>)[name];
    for (const field of ['username', 'password']) {
      const input = document.getElementById(field) as HTMLInputElement;
      input.value = await credential(field);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, binding);
  await page.locator('#kc-login').click();

  // Back in an app means signed in. Still on a Keycloak page means it said
  // no or asks for something: report what, but never the credentials.
  const left = await page
    .waitForURL((url) => !url.pathname.includes('/realms/'), { timeout: 30_000 })
    .then(() => true)
    .catch(() => false);
  if (left) return;

  const alert = page.locator('[role="alert"], #input-error, .kc-feedback-text').first();
  if (await alert.isVisible().catch(() => false)) {
    const said = (await alert.innerText()).trim().replace(/\s+/g, ' ');
    throw new Error(`Keycloak refused the ${account} account: "${said}"`);
  }
  if (await page.locator('#kc-form-login').isVisible().catch(() => false)) {
    throw new Error(`Keycloak kept showing the login form for the ${account} account`);
  }
  // A required action (update password, verify e-mail, terms, OTP setup):
  // completing it would change account data, which these tests never do.
  throw new Error(
    `Keycloak asks the ${account} account for a required action ("${await page.title()}" ` +
      `at ${new URL(page.url()).pathname}); complete it by hand once, then rerun`,
  );
}

/** The oidc-client-ts user record an app keeps in localStorage under
 *  `oidc.user:<issuer>:<client_id>` (react-oidc-context + WebStorageStateStore). */
export interface StoredUser {
  access_token: string;
  refresh_token?: string;
  expires_at?: number;
  profile?: Record<string, unknown>;
}

/** Read the signed-in user an app on this page holds, for one OIDC client. */
export async function storedUser(page: Page, issuer: string, clientId: string): Promise<StoredUser | null> {
  const key = `oidc.user:${issuer}:${clientId}`;
  const raw = await page.evaluate((k) => window.localStorage.getItem(k), key);
  if (!raw) return null;
  try {
    const user = JSON.parse(raw) as StoredUser;
    return user.access_token ? user : null;
  } catch {
    return null;
  }
}

/** Wait until the app on this page holds an access token that is still
 *  valid for at least `minValidSec` seconds, and return it. */
export async function waitForToken(
  page: Page,
  issuer: string,
  clientId: string,
  minValidSec = 60,
): Promise<StoredUser> {
  let user: StoredUser | null = null;
  await expect
    .poll(
      async () => {
        user = await storedUser(page, issuer, clientId);
        if (!user) return 'no token yet';
        const left = (user.expires_at ?? 0) - Date.now() / 1000;
        return left >= minValidSec ? 'fresh' : `expires in ${Math.round(left)}s`;
      },
      { message: `a fresh ${clientId} token in localStorage`, timeout: 45_000 },
    )
    .toBe('fresh');
  return user!;
}
