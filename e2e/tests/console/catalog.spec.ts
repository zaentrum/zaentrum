// The catalog console (browse mode): find a title, open it, read its cast.
import { PIONEER_ONE, SINTEL } from '../../data/catalog';
import { catalogConsole } from '../../support/apps';
import { openCastTab, openInConsole } from '../../support/console';
import { expect, test } from '../../support/fixtures';

const CASES = [
  {
    ref: SINTEL,
    credits: [...SINTEL.actors.map((n) => ['actor', n]), ...SINTEL.directors.map((n) => ['director', n])],
  },
  { ref: PIONEER_ONE, credits: PIONEER_ONE.actors.map((n) => ['actor', n]) },
];

test.describe('catalog console', () => {
  for (const { ref, credits } of CASES) {
    test(`the console opens ${ref.title} and its cast tab lists role and name`, async ({ page, open, snap }) => {
      await open(catalogConsole, '/');
      await openInConsole(page, ref);
      const table = await openCastTab(page);
      await expect(table.getByRole('columnheader', { name: 'role', exact: true })).toBeVisible();
      await expect(table.getByRole('columnheader', { name: 'name', exact: true })).toBeVisible();
      for (const [role, name] of credits) {
        // A row with this role and this name (more columns may join them later).
        const row = table
          .getByRole('row')
          .filter({ has: page.getByRole('cell', { name: role, exact: true }) })
          .filter({ has: page.getByRole('cell', { name, exact: true }) });
        await expect(row.first(), `${role} ${name}`).toBeVisible();
      }
      await snap(`${ref.title} cast tab`);
    });
  }
});
