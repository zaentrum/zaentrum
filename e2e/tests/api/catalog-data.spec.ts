// The data set (data/catalog.ts) against this instance's catalog. When the
// library changes, these tests say what moved, by name — read them first when
// a UI test fails on a missing title or person.
import {
  ACCENTED,
  ACTOR,
  AGENT_327,
  BROWSE_MOVIES,
  DIRECTOR,
  HERO,
  PIONEER_ONE,
  SINTEL,
  SPRING,
  TEARS_OF_STEEL,
} from '../../data/catalog';
import { findPerson, findTitle, personDetail, titleDetail, type Season } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { attachJson } from '../../support/pages';

const names = (cast: { name: string; role: string }[] | undefined, role: string) =>
  (cast ?? []).filter((c) => c.role === role).map((c) => c.name);

test.describe('the data set', () => {
  test('its titles are in the catalog, with their year and type', async ({ api }, testInfo) => {
    const found = [];
    for (const ref of [...BROWSE_MOVIES, AGENT_327, PIONEER_ONE]) {
      const item = await findTitle(api, ref);
      expect(item.type).toBe(ref.type);
      found.push({ title: item.title, year: item.year, type: item.type, id: item.id });
    }
    await attachJson(testInfo, 'titles', found);
  });

  test('its movies credit their actors and directors', async ({ api }, testInfo) => {
    const seen: Record<string, unknown> = {};
    for (const ref of [SINTEL, TEARS_OF_STEEL, SPRING, HERO]) {
      const item = await titleDetail(api, ref);
      seen[ref.title] = item.cast;
      expect(names(item.cast, 'director'), `directors of ${ref.title}`).toEqual(
        expect.arrayContaining([...ref.directors]),
      );
    }
    const sintel = await titleDetail(api, SINTEL);
    expect(names(sintel.cast, 'actor').sort(), `actors of ${SINTEL.title}`).toEqual([...SINTEL.actors].sort());
    const tears = await titleDetail(api, TEARS_OF_STEEL);
    // More than the five the detail page shows (tests/ui-changes.spec.ts).
    expect(names(tears.cast, 'actor').length, `actors of ${TEARS_OF_STEEL.title}`).toBeGreaterThan(5);
    await attachJson(testInfo, 'credits', seen);
  });

  test('Pioneer One has one season of six episodes and credits its five lead actors', async ({ api }, testInfo) => {
    const series = await titleDetail(api, PIONEER_ONE);
    expect(names(series.cast, 'actor')).toEqual(expect.arrayContaining([...PIONEER_ONE.actors]));
    const { seasons } = await api.json<{ seasons: Season[] }>(`/api/v1/series/${series.id}/episodes`);
    expect(seasons.map((s) => ({ season: s.season, episodes: s.episodes.map((e) => e.title) }))).toEqual(
      PIONEER_ONE.seasons.map((s) => ({ season: s.season, episodes: [...s.episodes] })),
    );
    await attachJson(testInfo, 'Pioneer One', { cast: series.cast, seasons });
  });

  test('its director and actor are credited on the titles the suite expects', async ({ api }, testInfo) => {
    for (const person of [DIRECTOR, ACTOR]) {
      const detail = await personDetail(api, person.name);
      await attachJson(testInfo, person.name, detail);
      expect(detail.items.map((i) => i.title)).toEqual(
        expect.arrayContaining(person.titles.map((t) => t.title)),
      );
    }
    const accented = await findPerson(api, ACCENTED.name);
    expect(accented.credits).toBeGreaterThanOrEqual(1);
  });
});
