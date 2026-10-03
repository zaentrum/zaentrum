// The setup project: sign each account in once, through the instance's real
// Keycloak login page, and save the signed-in browser state (cookies of the
// Keycloak session + the apps' tokens in localStorage) under e2e/.auth/.
// Every other project starts from that state instead of signing in again.
//
// The test drives its own browser context and closes it before it ends, and
// the project records no trace, screenshot or video: nothing a report keeps
// may show what was typed into the login form.
import fs from 'node:fs';
import path from 'node:path';
import { test as setup, type Browser } from '@playwright/test';
import { catalogConsole, chino, portal, type App } from '../../support/apps';
import { exposeCredentials, signInOnKeycloak, waitForToken } from '../../support/auth';
import { authFile, credentials, type Account } from '../../support/env';
import { instanceConfig } from '../../support/instance';
import { guardReadOnly } from '../../support/readonly';

async function signIn(browser: Browser, account: Account, apps: App[]) {
  credentials(account); // fail fast, naming any missing variable
  const cfg = await instanceConfig();
  const context = await browser.newContext({ storageState: undefined });
  const blocked: string[] = [];
  await guardReadOnly(context, (what) => blocked.push(what));
  try {
    const page = await context.newPage();
    const binding = await exposeCredentials(page, account);
    const [first, ...others] = apps;
    // The first app sends the browser to Keycloak's login page …
    await page.goto(first.url());
    await signInOnKeycloak(page, account, binding);
    await first.ready(page);
    await waitForToken(page, cfg.oidcIssuer, first.clientId(cfg));
    // … the others ride the Keycloak session it opened (single sign-on).
    for (const app of others) {
      await page.goto(app.url());
      await app.ready(page);
      await waitForToken(page, cfg.oidcIssuer, app.clientId(cfg));
    }
    const file = authFile(account);
    await context.storageState({ path: file });
    // A Keycloak session and live tokens: readable by this user only.
    fs.chmodSync(path.dirname(file), 0o700);
    fs.chmodSync(file, 0o600);
  } finally {
    await context.close();
  }
  if (blocked.length) setup.info().annotations.push({ type: 'blocked write', description: blocked.join('\n') });
}

setup('viewer signs in through Keycloak', async ({ browser }) => {
  await signIn(browser, 'viewer', [chino]);
});

setup('admin signs in through Keycloak', async ({ browser }) => {
  await signIn(browser, 'admin', [catalogConsole, portal, chino]);
});
