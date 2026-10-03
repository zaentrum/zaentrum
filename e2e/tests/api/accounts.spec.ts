// The accounts are what the suite takes them for. A "viewer" that is in fact
// an administrator would hide every permission the viewer is meant to lack.
// (The response names the account, so it is not attached to the report.)
import { expect, test } from '../../support/fixtures';

test('the viewer account is signed in and is not an administrator', async ({ api }) => {
  const me = await api.json<{ isAdmin: boolean; roles: string[] }>('/api/portal/me');
  expect(me.isAdmin, 'the viewer is an administrator').toBe(false);
});
