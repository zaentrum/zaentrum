// UI changes the team can implement against: one spec per change, each with
// the assertion it will make once the change is live.
//
// Every spec opens its page and attaches a screenshot first, then stops at
// `notYet()` (a runtime test.fixme), so a default run reports these as
// skipped and the report shows each page as it is today. To implement one:
// build the change, run `npm run test:ui-changes` (E2E_FIXME=run executes
// the assertions of all of them), and when its spec passes against the
// instance, delete its notYet() line so it guards the change from then on.
//
// The data they show is live (tests/api/credits-people.spec.ts proves it):
// creators and the rest of the crew, characters, billing order, episode
// counts, portraits, biographies and birth data. What is missing is the UI.
import type { Page } from '@playwright/test';
import { ACTOR, DIRECTOR, PIONEER_ONE, SINTEL, TEARS_OF_STEEL } from '../data/catalog';
import { catalogConsole, chino, type App } from '../support/apps';
import { findPerson, findTitle, titleDetail, type CastEntry } from '../support/catalog';
import { openCastTab, openInConsole } from '../support/console';
import { authFile, env } from '../support/env';
import { expect, test } from '../support/fixtures';
import { creditBlock, escapeRegExp, expectImageLoaded, titleInfo } from '../support/pages';

/** Stop here (test.fixme) unless E2E_FIXME=run: the change is not built yet. */
function notYet(what: string) {
  test.fixme(!env.runFixme, `not implemented yet: ${what}`);
}

/** Open a title's detail page in the web client and wait for its heading. */
async function openDetail(page: Page, open: (app: App, path?: string) => Promise<void>, id: string, title: string) {
  await open(chino, `/i/${id}`);
  await expect(titleInfo(page, title)).toBeVisible();
  return titleInfo(page, title);
}

const sameRole = (cast: CastEntry[] | undefined, role: string) => (cast ?? []).filter((c) => c.role === role);

test.describe('web client — the detail page', () => {
  test('a series’ detail page says “Created by Josh Bernhard”, linked to his person page', async ({ page, open, api, snap }) => {
    const series = await findTitle(api, PIONEER_ONE);
    const info = await openDetail(page, open, series.id, PIONEER_ONE.title);
    await snap('Pioneer One');
    notYet('the creator of a series on its detail page');

    const creator = await findPerson(api, PIONEER_ONE.creator);
    const link = creditBlock(info, 'Created by').getByRole('link', { name: PIONEER_ONE.creator, exact: true });
    await expect(link).toBeVisible();
    await link.click();
    await expect(page).toHaveURL(chino.url(`/person/${creator.id}`));
  });

  test('the detail page lists the crew by role, each under its label: Director, Writer, Producer, Music', async ({ page, open, api, snap }) => {
    const detail = await titleDetail(api, SINTEL);
    const info = await openDetail(page, open, detail.id, SINTEL.title);
    await snap('Sintel');
    notYet('crew grouped by role on the detail page');

    const labels: [string, string][] = [
      ['Director', 'director'],
      ['Writer', 'writer'],
      ['Producer', 'producer'],
      ['Music', 'composer'],
    ];
    for (const [label, role] of labels) {
      const block = creditBlock(info, new RegExp(`^${label}s?$`));
      await expect(block, `a "${label}" block`).toBeVisible();
      const credited = sameRole(detail.cast, role).map((c) => c.name);
      expect(credited.length, `the API credits a ${role} on ${SINTEL.title}`).toBeGreaterThan(0);
      for (const name of credited) {
        await expect(block.getByRole('link', { name, exact: true })).toBeVisible();
      }
    }
    await expect(creditBlock(info, /^Directors?$/).getByRole('link', { name: DIRECTOR.name, exact: true })).toBeVisible();
  });

  test('the detail page lists the actors in billing order, each with the character they play', async ({ page, open, api, snap }) => {
    const detail = await titleDetail(api, PIONEER_ONE);
    const info = await openDetail(page, open, detail.id, PIONEER_ONE.title);
    await snap('Pioneer One');
    notYet('billing order and characters on the detail page');

    const actors = sameRole(detail.cast, 'actor').slice(0, PIONEER_ONE.actors.length);
    expect(actors.map((a) => a.name), 'the API lists the lead actors first, in billing order').toEqual([
      ...PIONEER_ONE.actors,
    ]);
    for (const a of actors) expect(a.character, `the API names ${a.name}'s character`).toBeTruthy();
    // Each name, in billing order, followed by that actor's character.
    const sequence = actors.map((a) => `${escapeRegExp(a.name)}[\\s\\S]*?${escapeRegExp(a.character!)}`).join('[\\s\\S]*?');
    await expect(creditBlock(info, 'Starring')).toHaveText(new RegExp(sequence));
  });

  test('the detail page shows the whole cast, not just the first five (Tears of Steel has seven actors)', async ({ page, open, api, snap }) => {
    const detail = await titleDetail(api, TEARS_OF_STEEL);
    const info = await openDetail(page, open, detail.id, TEARS_OF_STEEL.title);
    await snap('Tears of Steel');
    notYet('the full cast on the detail page');

    const actors = sameRole(detail.cast, 'actor').map((a) => a.name);
    expect(actors.length, 'actors the API credits').toBeGreaterThan(5);
    // A "full cast" control may stand between the first names and the rest.
    const more = info.getByRole('button', { name: /full cast|all cast|show all/i });
    if (await more.isVisible()) await more.click();
    for (const name of actors) {
      await expect(info.getByRole('link', { name, exact: true }), `${name} is listed`).toBeVisible();
    }
  });
});

test.describe('web client — the person page', () => {
  test('the person page shows the person’s portrait as an image, not initials', async ({ page, open, api, snap }) => {
    const actor = await findPerson(api, ACTOR.name);
    await open(chino, `/person/${actor.id}`);
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();
    await snap(ACTOR.name);
    notYet('portraits on the person page');

    await expectImageLoaded(page.getByRole('img', { name: ACTOR.name, exact: true }), `${ACTOR.name}'s portrait`);
  });

  test('the person page shows the biography', async ({ page, open, api, snap }) => {
    const actor = await findPerson(api, ACTOR.name);
    await open(chino, `/person/${actor.id}`);
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();
    await snap(ACTOR.name);
    notYet('the biography on the person page');

    await expect(page.getByText(ACTOR.biographyExcerpt)).toBeVisible();
  });

  test('the person page shows the birth date and the birthplace', async ({ page, open, api, snap }) => {
    const actor = await findPerson(api, ACTOR.name);
    await open(chino, `/person/${actor.id}`);
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();
    await snap(ACTOR.name);
    notYet('birth date and birthplace on the person page');

    // 1957-03-03, in whichever of the common spellings the page settles on.
    await expect(page.getByText(/3 March 1957|March 3, 1957|1957-03-03|03\.03\.1957/)).toBeVisible();
    await expect(page.getByText(ACTOR.birthplace)).toBeVisible();
  });

  test('the person page names the person’s role on each title (“Director” on Sintel for Colin Levy)', async ({ page, open, api, snap }) => {
    const director = await findPerson(api, DIRECTOR.name);
    await open(chino, `/person/${director.id}`);
    await expect(page.getByRole('heading', { level: 1, name: DIRECTOR.name })).toBeVisible();
    await snap(DIRECTOR.name);
    notYet('per-title roles on the person page');

    for (const title of DIRECTOR.titles) {
      const card = page.getByRole('heading', { level: 3, name: title.title, exact: true }).locator('xpath=../..');
      await expect(card, `the ${title.title} card`).toContainText(/Director/i);
    }
  });

  test('the person page says what the person is known for (“Acting”)', async ({ page, open, api, snap }) => {
    const actor = await findPerson(api, ACTOR.name);
    await open(chino, `/person/${actor.id}`);
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();
    await snap(ACTOR.name);
    notYet('"known for" on the person page');

    await expect(page.getByText(/Known for:?\s*Acting/i)).toBeVisible();
  });
});

test.describe('web client — search', () => {
  async function searchFor(page: Page, open: (app: App, path?: string) => Promise<void>, q: string) {
    await open(chino, '/');
    const box = page.getByRole('searchbox');
    await box.fill(q);
    await box.press('Enter');
    await expect(page.getByRole('heading', { level: 2, name: 'Cast & crew' })).toBeVisible();
  }

  test('search does not say “No results” when only people match (“hoffman”)', async ({ page, open, snap }) => {
    await searchFor(page, open, ACTOR.search);
    await snap(`search ${ACTOR.search}`);
    notYet('a search headline that counts people');

    await expect(page.getByRole('heading', { level: 1 })).not.toHaveText(/^No results/);
  });

  test('search’s “Cast & crew” cards show the portrait of people who have one', async ({ page, open, snap }) => {
    await searchFor(page, open, ACTOR.search);
    await snap(`search ${ACTOR.search}`);
    notYet('portraits on the search page');

    const card = page.getByRole('main').getByRole('button', { name: new RegExp(escapeRegExp(ACTOR.name)) });
    await expectImageLoaded(card.getByRole('img', { name: ACTOR.name, exact: true }), `${ACTOR.name}'s portrait`);
  });
});

test.describe('catalog console — the cast tab', () => {
  test.use({ storageState: authFile('admin') });

  test('the cast tab shows job, character and order columns', async ({ page, open, snap }) => {
    await open(catalogConsole, '/');
    await openInConsole(page, SINTEL);
    const table = await openCastTab(page);
    await snap('Sintel cast tab');
    notYet('job, character and order in the console');

    for (const header of ['job', 'character', 'order']) {
      await expect(table.getByRole('columnheader', { name: header, exact: true })).toBeVisible();
    }
    const director = table.getByRole('row', { name: new RegExp(`^director ${escapeRegExp(DIRECTOR.name)}\\b`) });
    await expect(director).toContainText('Director');
    for (const name of SINTEL.actors) {
      const row = table.getByRole('row', { name: new RegExp(`^actor ${escapeRegExp(name)}\\b`) });
      // A character, then a billing position.
      await expect(row).toHaveText(new RegExp(`${escapeRegExp(name)}.*\\S.*\\d`));
    }
  });

  test('the cast tab of a series shows how many episodes each credit covers', async ({ page, open, snap }) => {
    await open(catalogConsole, '/');
    await openInConsole(page, PIONEER_ONE);
    const table = await openCastTab(page);
    await snap('Pioneer One cast tab');
    notYet('episode counts in the console');

    await expect(table.getByRole('columnheader', { name: 'episodes', exact: true })).toBeVisible();
    for (const name of PIONEER_ONE.actors) {
      const row = table.getByRole('row', { name: new RegExp(`^actor ${escapeRegExp(name)}\\b`) });
      await expect(row.getByRole('cell', { name: String(PIONEER_ONE.actorEpisodeCount), exact: true })).toBeVisible();
    }
  });

  test('the cast tab links each name to that person’s record', async ({ page, open, snap }) => {
    await open(catalogConsole, '/');
    await openInConsole(page, SINTEL);
    const table = await openCastTab(page);
    await snap('Sintel cast tab');
    notYet('a person record in the console');

    const link = table.getByRole('link', { name: ACTOR.name, exact: true });
    await expect(link, `${ACTOR.name}'s name is a link`).toBeVisible();
    await link.click();
    await expect(page.getByRole('heading', { level: 1, name: ACTOR.name })).toBeVisible();
    await expect(page.getByText(ACTOR.birthplace)).toBeVisible();
  });
});
