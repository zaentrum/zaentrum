// The web client's person page (/person/:id under the app's mount) and how a
// title's credits lead to it.
import { DIRECTOR, SINTEL } from '../../data/catalog';
import { chino } from '../../support/apps';
import { findPerson, findTitle } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { creditBlock, titleInfo } from '../../support/pages';

test.describe('people', () => {
  test('a cast name on a detail page links to that person’s page', async ({ page, open, api, snap }) => {
    // The link has to keep the app's mount path: the demo serves chino at
    // /chino/, and a bare "/person/<id>" left the app for a 404 until the
    // detail page built it the way search does.
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
