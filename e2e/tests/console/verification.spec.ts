// The platform checks itself after every update: the operator runs the chart's
// test (zae doctor --sign-in, as its own test account) and records the verdict
// in the Zaentrum's status, and the portal's operator console shows it. This
// test only reads the card; it never presses "verify now", which would ask the
// operator for a run.
import { portal } from '../../support/apps';
import { expect, test } from '../../support/fixtures';

test('the operator console shows the platform’s last check of itself, and that it passed', async ({ page, open, snap }) => {
  await open(portal, '/operator');
  await expect(page.getByText('verification', { exact: true }), 'the verification card').toBeVisible();
  // The verdict, and every check counted: a failed check would name itself below the counts.
  await expect(page.getByText('passed', { exact: true }), 'the result badge').toBeVisible();
  await expect(page.getByText(/^\d+ passed · 0 failed$/), 'the counts').toBeVisible();
  // An administrator can ask for another run; the button is there and idle.
  await expect(page.getByRole('button', { name: 'verify now' })).toBeEnabled();
  await snap('operator console: verification');
});
