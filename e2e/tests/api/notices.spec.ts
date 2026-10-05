// Notices: what an addon tells one person. The viewer posts one to themselves
// from the sample addon, as its console does, and reads it through chino-api,
// as every app does; then marks it read and deletes it, so the run leaves
// nothing behind. (The notice names nobody, so it is fine in the report.)
import { expect, test } from '../../support/fixtures';
import { env } from '../../support/env';

interface Notice {
  id: string;
  addon: string;
  title: string;
  body: string;
  readAt: string | null;
}

interface NoticeList {
  notices: Notice[];
  unread: number;
  available: boolean;
}

test('a notice reaches its person through chino-api, is read and deleted', async ({ api, bearer, playwright }) => {
  const request = await playwright.request.newContext({ baseURL: env.baseURL });
  const headers = async () => ({ Authorization: `Bearer ${await bearer.token()}`, Accept: 'application/json' });
  let id = '';
  try {
    const before = await api.json<NoticeList>('/api/v1/notices');
    expect(before.available, 'chino-api reaches portal-api for notices').toBe(true);

    const title = `End-to-end ${Date.now()}`;
    const posted = await request.post('/api/portal/me/notices', {
      headers: await headers(),
      data: { addon: 'sample', title, body: 'A notice the end-to-end suite sends itself.' },
    });
    expect(posted.status(), 'POST /api/portal/me/notices').toBe(201);
    id = ((await posted.json()) as Notice).id;

    const after = await api.json<NoticeList>('/api/v1/notices');
    const mine = after.notices.find((n) => n.id === id);
    expect(mine, 'the new notice is in the list').toBeDefined();
    expect(mine?.title).toBe(title);
    expect(mine?.addon).toBe('sample');
    expect(mine?.readAt ?? null, 'a new notice is unread').toBeNull();
    expect(after.unread).toBe(before.unread + 1);
    expect(after.notices[0]?.id, 'newest first').toBe(id);

    const read = await request.post(`/api/v1/notices/${id}/read`, { headers: await headers() });
    expect(read.status(), 'POST /api/v1/notices/{id}/read').toBe(200);
    expect(((await read.json()) as { unread: number }).unread).toBe(before.unread);

    const deleted = await request.delete(`/api/v1/notices/${id}`, { headers: await headers() });
    expect(deleted.status(), 'DELETE /api/v1/notices/{id}').toBe(204);
    id = '';
    const gone = await api.json<NoticeList>('/api/v1/notices');
    expect(gone.notices.map((n) => n.title), 'the deleted notice is gone').not.toContain(title);
  } finally {
    // A failed step above still leaves nothing behind.
    if (id) await request.delete(`/api/v1/notices/${id}`, { headers: await headers() }).catch(() => {});
    await request.dispose();
  }
});

test("another person's notice is not found, to read or to delete", async ({ bearer, playwright }) => {
  const request = await playwright.request.newContext({ baseURL: env.baseURL });
  const headers = { Authorization: `Bearer ${await bearer.token()}`, Accept: 'application/json' };
  try {
    // A well-formed id that is not the viewer's answers as one that is not there.
    const nobody = '00000000-0000-4000-8000-000000000000';
    expect((await request.post(`/api/v1/notices/${nobody}/read`, { headers })).status()).toBe(404);
    expect((await request.delete(`/api/v1/notices/${nobody}`, { headers })).status()).toBe(404);
  } finally {
    await request.dispose();
  }
});
