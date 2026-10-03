// The three browser apps the suite drives, by where they are mounted and how
// to tell that one has finished signing in.
import { expect, type Locator, type Page } from '@playwright/test';
import { appURL, env } from './env';
import { portalClient, webClient, type InstanceConfig } from './instance';

export interface App {
  name: string;
  url(sub?: string): string;
  clientId(cfg: InstanceConfig): string;
  /** What the app shows once it is signed in. */
  signedIn(page: Page): Locator;
  /** Resolves once the app shows its signed-in chrome. */
  ready(page: Page): Promise<void>;
}

function app(name: string, mountPath: () => string, clientId: App['clientId'], signedIn: App['signedIn']): App {
  return {
    name,
    url: (sub = '/') => appURL(mountPath(), sub),
    clientId,
    signedIn,
    ready: async (page) => {
      await expect(signedIn(page), `${name} is signed in`).toBeVisible({ timeout: 45_000 });
    },
  };
}

/** The web client: home, browse, detail, person and search pages. */
export const chino = app('chino', () => env.chinoPath, webClient, (page) => page.getByRole('searchbox'));

/** The catalog console in browse mode (item list + item detail). */
export const catalogConsole = app('catalog console', () => env.consolePath, portalClient, (page) =>
  page.getByRole('button', { name: 'sign out' }),
);

/** The portal launchpad. */
export const portal = app('portal', () => env.portalPath, portalClient, (page) =>
  page.getByRole('button', { name: 'sign out' }),
);
