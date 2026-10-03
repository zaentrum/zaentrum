// The web client's person page (/person/:id under the app's mount) and how a
// title's credits lead to it.
import { DIRECTOR, SINTEL } from '../../data/catalog';
import { chino } from '../../support/apps';
import { findPerson, findTitle } from '../../support/catalog';
import { env } from '../../support/env';
import { expect, test } from '../../support/fixtures';
import { creditBlock, titleInfo } from '../../support/pages';

test.describe('people', () => {
  test('a cast name on a detail page links to that person’s page', async ({ page, open, api, snap }) => {
    // KNOWN BUG while this marker stands: the detail page links a name to
    // "/person/<id>" without the app's mount path. Mounted at "/" that works;
    // under a path (the demo serves chino at /chino/) it leaves the app for a
    // 404. The search page builds the same link with the mount path and works.
    // Remove the marker once the link is fixed; the test then has to pass.
    test.fail(env.chinoPath !== '/', 'bug: cast links on the detail page drop the app’s mount path');

    const sintel = await findTitle(api, SINTEL);
    const director = await findPerson(api, DIRECTOR.name);
    await open(chino, `/i/${sintel.id}`);
    const link = creditBlock(titleInfo(page, SINTEL.title), /^Directors?$/).getByRole('link', {
      name: DIRECTOR.name,
      exact: true,
    });
    await expect(link).toBeVisible();
    await link.click();
    await page.waitForLoadState('domcontentloaded');
    await snap('after clicking the director');
    // Where the click lands is settled by now; no need for the long default wait.
    await expect(page).toHaveURL(chino.url(`/person/${director.id}`), { timeout: 5_000 });
    await expect(page.getByRole('heading', { level: 1, name: DIRECTOR.name })).toBeVisible();
  });

  test('the person page shows the name and a filmography holding their titles', async ({ page, open, api, snap }) => {
    const director = await findPerson(api, DIRECTOR.name);
    await open(chino, `/person/${director.id}`);
    await expect(page.getByRole('heading', { level: 1, name: DIRECTOR.name })).toBeVisible();
    await expect(page.getByText(/^\d+ titles?$/)).toBeVisible();
    for (const title of DIRECTOR.titles) {
      await expect(page.getByRole('heading', { level: 3, name: title.title, exact: true })).toBeVisible();
    }
    await snap(DIRECTOR.name);
  });
});
