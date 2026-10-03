// The web client's search: titles, and people under "Cast & crew".
import { ACCENTED, ACTOR, SINTEL } from '../../data/catalog';
import { chino } from '../../support/apps';
import { findPerson } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { escapeRegExp, expectImageLoaded, poster } from '../../support/pages';
import type { Page } from '@playwright/test';

/** Type a query into the header's search box and submit it, as a viewer would. */
async function search(page: Page, query: string) {
  const box = page.getByRole('searchbox');
  await box.fill(query);
  await box.press('Enter');
  await expect(page).toHaveURL(chino.url(`/search?q=${encodeURIComponent(query)}`));
}

/** A person's card in the "Cast & crew" section: their name and "· N titles". */
function personCard(page: Page, name: string) {
  return page
    .getByRole('main')
    .getByRole('button', { name: new RegExp(`${escapeRegExp(name)}.*· \\d+ titles?`) });
}

test.describe('search', () => {
  test('search finds a title by its name', async ({ page, open, snap }) => {
    await open(chino, '/');
    await search(page, SINTEL.title);
    const main = page.getByRole('main');
    await expect(main.getByRole('heading', { level: 3, name: SINTEL.title, exact: true })).toBeVisible();
    await expectImageLoaded(poster(main, SINTEL.title), `the poster of "${SINTEL.title}"`);
    await snap(`search ${SINTEL.title}`);
  });

  test('search finds a person under “Cast & crew” and opens their page', async ({ page, open, api, snap }) => {
    const actor = await findPerson(api, ACTOR.name);
    await open(chino, '/');
    await search(page, ACTOR.search);
    await expect(page.getByRole('heading', { level: 2, name: 'Cast & crew' })).toBeVisible();
    const card = personCard(page, ACTOR.name);
    await expect(card).toBeVisible();
    await snap(`search ${ACTOR.search}`);

    await card.click();
    await expect(page).toHaveURL(chino.url(`/person/${actor.id}`));
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();
    for (const title of ACTOR.titles) {
      await expect(page.getByRole('heading', { level: 3, name: title.title, exact: true })).toBeVisible();
    }
    await snap(ACTOR.name);
  });

  test('search finds a person without the accent their name carries', async ({ page, open, snap }) => {
    await open(chino, '/');
    await search(page, ACCENTED.search);
    await expect(page.getByRole('heading', { level: 2, name: 'Cast & crew' })).toBeVisible();
    await expect(personCard(page, ACCENTED.name)).toBeVisible();
    await snap(`search ${ACCENTED.search}`);
  });
});
