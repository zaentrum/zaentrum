// Driving the catalog console. Its item page carries action buttons
// (enrich, identify, edit, delete, package, …); the suite only ever clicks a
// title link and the tabs.
import { expect, type Page } from '@playwright/test';
import type { TitleRef } from '../data/catalog';
import { catalogConsole } from './apps';
import { escapeRegExp } from './pages';

/** Search the console's item list for a title and open it. */
export async function openInConsole(page: Page, ref: TitleRef): Promise<void> {
  const main = page.getByRole('main');
  await main.getByRole('textbox', { name: 'search' }).fill(ref.title);
  const row = main
    .getByRole('row')
    .filter({ has: page.getByRole('cell', { name: ref.title, exact: true }) })
    .filter({ has: page.getByRole('cell', { name: ref.type, exact: true }) })
    .filter({ has: page.getByRole('cell', { name: String(ref.year), exact: true }) });
  await expect(row).toHaveCount(1);
  await row.getByText(ref.title, { exact: true }).click();
  await expect(page).toHaveURL(new RegExp(`^${escapeRegExp(catalogConsole.url('/item/'))}[0-9a-f-]{36}$`));
  await expect(main.getByRole('heading', { level: 1, name: ref.title, exact: true })).toBeVisible();
}

/** Open an item page's cast tab and return its table. */
export async function openCastTab(page: Page) {
  const tab = page.getByRole('tab', { name: /^cast \(\d+\)$/ });
  await tab.click();
  await expect(tab).toHaveAttribute('aria-selected', 'true');
  return page.getByRole('main').getByRole('table');
}
