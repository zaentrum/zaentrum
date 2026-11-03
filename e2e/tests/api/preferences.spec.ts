// A person's preferences and a list by kind: the contract of the backend
// round that builds them. Reads only: the read-only guard rules out PATCH.
import { expect, test } from '../../support/fixtures';

type Lists = { lists: { id: string; counts?: { movie: number; series: number } }[] };

test.describe('preferences and lists by kind @next', () => {
  test('GET /api/config offers both features', async ({ api }) => {
    const config = await api.json<{ features: Record<string, boolean> }>('/api/config');
    expect(config.features.preferences).toBe(true);
    expect(config.features.watchlist_kinds).toBe(true);
  });

  test('GET /api/v1/me/preferences says whether lists split by kind', async ({ api }) => {
    const prefs = await api.json<{ watchlist_by_kind: boolean }>('/api/v1/me/preferences');
    expect(typeof prefs.watchlist_by_kind).toBe('boolean');
  });

  test('counts come only when asked for, and match each row', async ({ api }) => {
    const plain = await api.json<Lists>('/api/v1/me/watchlists');
    expect(plain.lists.every((l) => l.counts === undefined)).toBe(true);

    const counted = await api.json<Lists>('/api/v1/me/watchlists?include=counts');
    for (const list of counted.lists) {
      expect(list.counts, `counts of ${list.id}`).toBeDefined();
      const row = (kind: string) => api.json<{ items: string[] }>(`/api/v1/me/watchlists/${list.id}?kind=${kind}`);
      const [movies, shows] = await Promise.all([row('movie'), row('series')]);
      expect(movies.items.length).toBe(list.counts!.movie);
      expect(shows.items.length).toBe(list.counts!.series);
      expect(movies.items.filter((id) => shows.items.includes(id))).toEqual([]);
    }
  });
});
