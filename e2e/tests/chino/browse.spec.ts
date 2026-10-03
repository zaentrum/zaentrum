// The web client's home and browse pages: the catalog shows up, with posters.
import { BROWSE_MOVIES, SINTEL } from '../../data/catalog';
import { chino } from '../../support/apps';
import { findTitle } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { expectImageLoaded, poster } from '../../support/pages';

test.describe('home and browse', () => {
  test('home shows rails of titles with their posters', async ({ page, open, snap }) => {
    await open(chino, '/');
    const main = page.getByRole('main');
    await expect(main.getByRole('heading', { level: 2, name: /^Recently added/ }).first()).toBeVisible();
    // The first rail of titles: a heading per card, a poster per card.
    const rail = main.getByRole('heading', { level: 2, name: /^Recently added/ }).first().locator('xpath=../..');
    const cards = rail.getByRole('heading', { level: 3 });
    await expect(cards.first()).toBeVisible();
    const titles = [...new Set((await cards.allInnerTexts()).map((t) => t.trim()))].slice(0, 3);
    expect(titles.length, 'titles in the first rail').toBeGreaterThan(0);
    for (const title of titles) {
      await expectImageLoaded(poster(rail, title), `the poster of "${title}"`);
    }
    await snap('home');
  });

  test('the movies page shows the data set’s titles, each with its poster', async ({ page, open, snap }) => {
    await open(chino, '/');
    await page.getByRole('navigation').getByRole('button', { name: 'Movies', exact: true }).click();
    const main = page.getByRole('main');
    await expect(main.getByRole('heading', { level: 1, name: 'Movies' })).toBeVisible();
    await expect(main.getByText(/You've reached the end of the catalogue — \d+ movies/)).toBeVisible();
    for (const movie of BROWSE_MOVIES) {
      await expect(main.getByRole('heading', { level: 3, name: movie.title, exact: true })).toBeVisible();
      await expectImageLoaded(poster(main, movie.title), `the poster of "${movie.title}"`);
    }
    await main.evaluate((el) => el.scrollTo(0, 0));
    await snap('movies');
  });

  test('a card on the movies page opens the title’s detail page', async ({ page, open, api, snap }) => {
    const sintel = await findTitle(api, SINTEL);
    await open(chino, '/');
    await page.getByRole('navigation').getByRole('button', { name: 'Movies', exact: true }).click();
    // The card's title is part of the card; clicking it opens the detail page
    // (the card's buttons — play, add to list — are not touched).
    await page.getByRole('main').getByRole('heading', { level: 3, name: SINTEL.title, exact: true }).click();
    await expect(page).toHaveURL(chino.url(`/i/${sintel.id}`));
    await expect(page.getByRole('heading', { level: 1, name: SINTEL.title })).toBeVisible();
    await snap('detail after the click');
  });
});
