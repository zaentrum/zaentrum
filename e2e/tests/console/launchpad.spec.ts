// The portal launchpad links the apps where this suite drives them, so a
// moved mount fails here first, with the path that moved.
import { catalogConsole, chino, portal } from '../../support/apps';
import { env } from '../../support/env';
import { expect, test } from '../../support/fixtures';

test('the launchpad links the web client and the catalog console', async ({ page, open, snap }) => {
  await open(portal, '/');
  const main = page.getByRole('main');
  await expect(main.getByRole('heading', { name: 'welcome back' })).toBeVisible();
  await expect(main.locator(`a[href="${env.chinoPath}"]`), `a tile linking ${chino.url()}`).toBeVisible();
  await expect(
    main.locator(`a[href="${env.consolePath}"]`),
    `a tile linking ${catalogConsole.url()}`,
  ).toBeVisible();
  // The admin's own group of tiles: the account really is an administrator.
  await expect(main.getByRole('region', { name: 'settings' })).toBeVisible();
  await snap('launchpad');
});
