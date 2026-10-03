// chino-api as the web client calls it today: the shapes the pages rely on.
// The bearer token is the one the signed-in web client holds (support/fixtures.ts).
import { ACTOR, DIRECTOR, PIONEER_ONE, SINTEL } from '../../data/catalog';
import {
  findPerson,
  findTitle,
  titleDetail,
  type PersonDetail,
  type PersonSummary,
  type Season,
} from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { attachJson } from '../../support/pages';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

test.describe('chino-api contract', () => {
  test('GET /api/v1/items/{id}: every cast entry has a person_id, a name and a role', async ({ api }, testInfo) => {
    for (const ref of [SINTEL, PIONEER_ONE]) {
      const item = await titleDetail(api, ref);
      await attachJson(testInfo, `GET items ${ref.title}`, item);
      expect(item.cast?.length ?? 0, `${ref.title} has credits`).toBeGreaterThan(0);
      for (const entry of item.cast ?? []) {
        expect(entry.person_id, `person_id of ${entry.name}`).toMatch(UUID);
        expect(typeof entry.name === 'string' && entry.name.trim().length > 0, 'a name').toBe(true);
        expect(entry.role, `role of ${entry.name}`).toMatch(/^[a-z][a-z_-]*$/);
      }
    }
  });

  test('GET /api/v1/items/{id}: the person_id of a credit opens that person', async ({ api }, testInfo) => {
    const item = await titleDetail(api, SINTEL);
    const credit = item.cast?.find((c) => c.name === DIRECTOR.name);
    expect(credit, `${DIRECTOR.name} is credited on ${SINTEL.title}`).toBeTruthy();
    const person = await api.json<PersonDetail>(`/api/v1/people/${credit!.person_id}`);
    await attachJson(testInfo, `GET people ${DIRECTOR.name}`, person);
    expect(person.id).toBe(credit!.person_id);
    expect(person.name).toBe(DIRECTOR.name);
    expect(person.items.map((it) => it.title)).toContain(SINTEL.title);
  });

  test('GET /api/v1/series/{id}/episodes: seasons of numbered episodes', async ({ api }, testInfo) => {
    const series = await findTitle(api, PIONEER_ONE);
    const body = await api.json<{ series_id: string; seasons: Season[] }>(`/api/v1/series/${series.id}/episodes`);
    await attachJson(testInfo, `GET series episodes ${PIONEER_ONE.title}`, body);
    expect(body.series_id).toBe(series.id);
    for (const expected of PIONEER_ONE.seasons) {
      const season = body.seasons.find((s) => s.season === expected.season);
      expect(season, `season ${expected.season}`).toBeTruthy();
      expect(season!.episodes.map((e) => e.episode_number)).toEqual(expected.episodes.map((_, i) => i + 1));
      for (const e of season!.episodes) {
        expect(e.type).toBe('episode');
        expect((e as { parent_id?: string }).parent_id).toBe(series.id);
      }
    }
  });

  test('GET /api/v1/people?q=: matches ignore case and accents and carry a credit count', async ({ api }, testInfo) => {
    const body = await api.json<{ people: PersonSummary[]; total: number }>(
      `/api/v1/people?q=${encodeURIComponent(ACTOR.search.toUpperCase())}`,
    );
    await attachJson(testInfo, `GET people q=${ACTOR.search.toUpperCase()}`, body);
    expect(body.total).toBe(body.people.length);
    const hit = body.people.find((p) => p.name === ACTOR.name);
    expect(hit, `${ACTOR.name} is found by "${ACTOR.search.toUpperCase()}"`).toBeTruthy();
    expect(hit!.id).toMatch(UUID);
    expect(hit!.credits).toBeGreaterThanOrEqual(ACTOR.titles.length);

    const empty = await api.json<{ people: PersonSummary[]; total: number }>('/api/v1/people?q=');
    expect(empty).toEqual({ people: [], total: 0 });
  });

  test('GET /api/v1/people/{id}: the person and the titles they are credited on', async ({ api }, testInfo) => {
    const summary = await findPerson(api, ACTOR.name);
    const person = await api.json<PersonDetail>(`/api/v1/people/${summary.id}`);
    await attachJson(testInfo, `GET people ${ACTOR.name}`, person);
    expect(person).toMatchObject({ id: summary.id, name: ACTOR.name });
    for (const ref of ACTOR.titles) {
      const it = person.items.find((i) => i.title === ref.title && i.year === ref.year);
      expect(it, `${ref.title} in the filmography`).toBeTruthy();
      expect(it!.poster_url).toBe(`/api/v1/items/${it!.id}/poster`);
    }
  });

  test('GET /api/v1/people/{id} of an unknown id answers 404', async ({ api }) => {
    const res = await api.get('/api/v1/people/00000000-0000-4000-8000-000000000000');
    expect(res.status()).toBe(404);
  });

  test('a title’s poster_url serves an image', async ({ api }, testInfo) => {
    const item = await findTitle(api, SINTEL);
    expect(item.poster_url).toBeTruthy();
    const res = await api.get(item.poster_url!);
    expect(res.status()).toBe(200);
    expect(res.headers()['content-type']).toMatch(/^image\//);
    const body = await res.body();
    expect(body.length).toBeGreaterThan(1_000);
    await testInfo.attach(`poster of ${SINTEL.title}`, { body, contentType: res.headers()['content-type'] });
  });
});
