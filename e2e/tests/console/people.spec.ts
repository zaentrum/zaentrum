// The catalog console's person record and its posters: a person's credits list
// the titles they are credited on, each linking back to its item, and an
// item's poster loads (the console fetches artwork with the bearer token, as a
// plain <img> cannot send it).
import { ACTOR, SINTEL } from '../../data/catalog';
import { catalogConsole } from '../../support/apps';
import { openCastTab, openInConsole } from '../../support/console';
import { expect, test } from '../../support/fixtures';
import { expectImageLoaded } from '../../support/pages';

test.describe('the console’s people', () => {
  test('a person record lists the person’s credits, each title linking back to its item', async ({ page, open, snap }) => {
    await open(catalogConsole, '/');
    await openInConsole(page, SINTEL);
    const cast = await openCastTab(page);
    await cast.getByRole('link', { name: ACTOR.name, exact: true }).click();
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();

    const tab = page.getByRole('tab', { name: /^credits \(\d+\)$/ });
    await tab.click();
    await expect(tab).toHaveAttribute('aria-selected', 'true');
    const credits = page.getByRole('main').getByRole('table');
    for (const title of ACTOR.titles) {
      await expect(credits.getByRole('link', { name: title.title, exact: true }), `${title.title} is credited`).toBeVisible();
    }
    await snap(`${ACTOR.name}: credits`);

    await credits.getByRole('link', { name: SINTEL.title, exact: true }).click();
    await expect(page.getByRole('main').getByRole('heading', { level: 1, name: SINTEL.title, exact: true })).toBeVisible();
  });

  test('an item’s poster loads in the console', async ({ page, open, snap }) => {
    await open(catalogConsole, '/');
    await openInConsole(page, SINTEL);
    await expectImageLoaded(page.locator('img.kat__obj-poster'), `${SINTEL.title}'s poster`);
    await snap(`${SINTEL.title} in the console`);
  });
});
