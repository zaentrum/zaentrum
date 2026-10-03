// The web client's detail pages: what a title shows about itself and its credits.
import { HERO, PIONEER_ONE, SINTEL, SPRING } from '../../data/catalog';
import { chino } from '../../support/apps';
import { findTitle } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { creditBlock, escapeRegExp, expectImageLoaded, poster, titleInfo } from '../../support/pages';

test.describe('title detail pages', () => {
  test('a movie’s detail page shows its poster, its year and its credits', async ({ page, open, api, snap }) => {
    const sintel = await findTitle(api, SINTEL);
    await open(chino, `/i/${sintel.id}`);
    const info = titleInfo(page, SINTEL.title);
    await expect(info).toBeVisible();
    await expect(info.getByText(String(SINTEL.year), { exact: true })).toBeVisible();
    await expect(info.getByText('movie', { exact: true })).toBeVisible();
    await expectImageLoaded(poster(page, SINTEL.title), 'the poster');

    const starring = creditBlock(info, 'Starring');
    for (const actor of SINTEL.actors) {
      await expect(starring.getByRole('link', { name: actor, exact: true })).toBeVisible();
    }
    const directed = creditBlock(info, /^Directors?$/);
    for (const director of SINTEL.directors) {
      await expect(directed.getByRole('link', { name: director, exact: true })).toBeVisible();
    }
    await snap('Sintel');
  });

  for (const movie of [SPRING, HERO]) {
    test(`the detail page of ${movie.title} (${movie.year}) names its director`, async ({ page, open, api, snap }) => {
      const item = await findTitle(api, movie);
      await open(chino, `/i/${item.id}`);
      const info = titleInfo(page, movie.title);
      await expect(info).toBeVisible();
      const directed = creditBlock(info, /^Directors?$/);
      for (const director of movie.directors) {
        await expect(directed.getByRole('link', { name: director, exact: true })).toBeVisible();
      }
      await snap(movie.title);
    });
  }

  test('a series’ detail page shows its season, its six episodes and its cast', async ({ page, open, api, snap }) => {
    const series = await findTitle(api, PIONEER_ONE);
    await open(chino, `/i/${series.id}`);
    const info = titleInfo(page, PIONEER_ONE.title);
    await expect(info).toBeVisible();
    await expect(info.getByText('series', { exact: true })).toBeVisible();

    const starring = creditBlock(info, 'Starring');
    for (const actor of PIONEER_ONE.actors) {
      await expect(starring.getByRole('link', { name: actor, exact: true })).toBeVisible();
    }

    await expect(page.getByRole('heading', { level: 2, name: 'Episodes' })).toBeVisible();
    for (const { season, episodes } of PIONEER_ONE.seasons) {
      // The first season opens by itself; its header says how many episodes it has.
      await expect(page.getByRole('button', { name: `Season ${season} ${episodes.length} episodes` })).toBeVisible();
      for (const [i, title] of episodes.entries()) {
        const code = `S${String(season).padStart(2, '0')}E${String(i + 1).padStart(2, '0')}`;
        // An episode row: its code and title (it also holds the row's own buttons).
        const row = page.getByRole('button', { name: new RegExp(`\\b${code} ${escapeRegExp(title)}\\b`) });
        await expect(row).toBeVisible();
      }
    }
    await snap('Pioneer One');
  });
});
