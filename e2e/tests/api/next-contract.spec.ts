// The NEXT backend round's contract for credits and people, as the web client
// will read it through chino-api. Tagged @next and left out of the default
// run until that round is deployed; run it with `npm run test:next`.
//
// Today these fail: chino-api's cast entry carries only person_id, name and
// role, and a person only id, name and items. katalog-api is gaining the
// fields; chino-api has to pass them through as well — including its cut of a
// title's credits to eight entries, which would drop a series' writer or a
// film's composer once the crew is listed.
import { ACTOR, DIRECTOR, PIONEER_ONE, SINTEL } from '../../data/catalog';
import { findPerson, personDetail, titleDetail, type CastEntry, type PersonSummary } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { attachJson } from '../../support/pages';

const byRole = (cast: CastEntry[] | undefined, role: string) => (cast ?? []).filter((c) => c.role === role);

test.describe('next round: credits and people', { tag: '@next' }, () => {
  test('cast entries carry job, character, order and episode_count', async ({ api }, testInfo) => {
    const sintel = await titleDetail(api, SINTEL);
    await attachJson(testInfo, `GET items ${SINTEL.title}`, sintel);
    for (const actor of byRole(sintel.cast, 'actor')) {
      expect.soft(actor.character ?? null, `the character ${actor.name} plays`).toEqual(expect.stringMatching(/\S/));
      expect.soft(actor.order, `the billing order of ${actor.name}`).toEqual(expect.any(Number));
    }
    for (const crew of (sintel.cast ?? []).filter((c) => c.role !== 'actor')) {
      expect.soft(crew.job ?? null, `the job of ${crew.name} (${crew.role})`).toEqual(expect.stringMatching(/\S/));
    }

    const series = await titleDetail(api, PIONEER_ONE);
    await attachJson(testInfo, `GET items ${PIONEER_ONE.title}`, series);
    const leads = byRole(series.cast, 'actor').filter((a) => (PIONEER_ONE.actors as readonly string[]).includes(a.name));
    expect(leads.map((a) => a.name).sort(), 'the lead actors').toEqual([...PIONEER_ONE.actors].sort());
    for (const actor of leads) {
      expect.soft(actor.episode_count, `the episodes ${actor.name} is in`).toBe(PIONEER_ONE.actorEpisodeCount);
    }
  });

  test('a series’ credits name its creator and a writer', async ({ api }, testInfo) => {
    const series = await titleDetail(api, PIONEER_ONE);
    await attachJson(testInfo, `GET items ${PIONEER_ONE.title}`, series);
    expect(byRole(series.cast, 'creator').map((c) => c.name)).toContain(PIONEER_ONE.creator);
    expect(byRole(series.cast, 'writer').length, 'writers credited').toBeGreaterThan(0);
  });

  test('a movie’s credits hold its director, writer, producer and composer', async ({ api }, testInfo) => {
    const sintel = await titleDetail(api, SINTEL);
    await attachJson(testInfo, `GET items ${SINTEL.title}`, sintel);
    const roles = new Set((sintel.cast ?? []).map((c) => c.role));
    for (const role of SINTEL.crewRoles) expect.soft([...roles], `a ${role} credited`).toContain(role);
    expect(byRole(sintel.cast, 'actor').map((a) => a.name).sort()).toEqual([...SINTEL.actors].sort());
  });

  test('the cast comes in billing order', async ({ api }, testInfo) => {
    const series = await titleDetail(api, PIONEER_ONE);
    await attachJson(testInfo, `GET items ${PIONEER_ONE.title}`, series);
    const actors = byRole(series.cast, 'actor');
    // The lead actors come first, in TMDB's billing order; any guest actors after them.
    expect(actors.slice(0, PIONEER_ONE.actors.length).map((a) => a.name), 'the first actors listed').toEqual([
      ...PIONEER_ONE.actors,
    ]);
    const orders = actors.map((a) => a.order);
    expect(orders.every((o) => typeof o === 'number'), `billing orders ${JSON.stringify(orders)}`).toBe(true);
    expect([...orders].sort((a, b) => a! - b!), 'billing orders ascend').toEqual(orders);
  });

  test('GET /api/v1/people/{id} has a biography, a birth date, has_profile and per-title roles', async ({ api }, testInfo) => {
    const actor = await personDetail(api, ACTOR.name);
    await attachJson(testInfo, `GET people ${ACTOR.name}`, actor);
    expect.soft(actor.biography ?? '', 'biography').toContain(ACTOR.biographyExcerpt);
    expect.soft(actor.birth_date, 'birth_date').toBe(ACTOR.birthDate);
    expect.soft(typeof actor.has_profile, 'has_profile').toBe('boolean');
    if (actor.has_profile) expect.soft(actor.profile_url ?? null, 'profile_url').toEqual(expect.stringMatching(/^\/api\/v1\//));
    for (const ref of ACTOR.titles) {
      const it = actor.items.find((i) => i.title === ref.title);
      expect.soft(it?.roles ?? [], `${ACTOR.name}'s roles on ${ref.title}`).toContain('actor');
    }

    const director = await personDetail(api, DIRECTOR.name);
    await attachJson(testInfo, `GET people ${DIRECTOR.name}`, director);
    for (const ref of DIRECTOR.titles) {
      const it = director.items.find((i) => i.title === ref.title);
      expect.soft(it?.roles ?? [], `${DIRECTOR.name}'s roles on ${ref.title}`).toContain('director');
    }
  });

  test('a profile_url serves an image', async ({ api }, testInfo) => {
    const candidates = [ACTOR.name, ...SINTEL.actors, DIRECTOR.name];
    let withPortrait: { name: string; url: string } | undefined;
    for (const name of new Set(candidates)) {
      const person = await personDetail(api, name);
      if (person.has_profile && person.profile_url) {
        withPortrait = { name, url: person.profile_url };
        break;
      }
    }
    expect(withPortrait, `one of ${[...new Set(candidates)].join(', ')} has a portrait`).toBeTruthy();
    const res = await api.get(withPortrait!.url);
    expect(res.status()).toBe(200);
    expect(res.headers()['content-type']).toMatch(/^image\//);
    const body = await res.body();
    expect(body.length).toBeGreaterThan(1_000);
    await testInfo.attach(`portrait of ${withPortrait!.name}`, { body, contentType: res.headers()['content-type'] });
  });

  test('people search says whether each person has a portrait', async ({ api }, testInfo) => {
    const body = await api.json<{ people: PersonSummary[] }>(`/api/v1/people?q=${encodeURIComponent(ACTOR.search)}`);
    await attachJson(testInfo, `GET people q=${ACTOR.search}`, body);
    const hit = await findPerson(api, ACTOR.name);
    expect(typeof hit.has_profile, 'has_profile on a search result').toBe('boolean');
  });
});
