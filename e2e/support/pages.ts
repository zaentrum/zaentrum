// Small page-level helpers shared by the UI specs, and JSON attachments for
// the API specs.
import { expect, type Locator, type Page, type TestInfo } from '@playwright/test';

export function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Expect an <img> to have loaded a real picture (not just to exist). */
export async function expectImageLoaded(img: Locator, what = 'the image'): Promise<void> {
  await expect(img, `${what} is on the page`).toBeVisible();
  await img.scrollIntoViewIfNeeded();
  await expect
    .poll(() => img.evaluate((el: HTMLImageElement) => (el.complete ? el.naturalWidth : -1)), {
      message: `${what} has loaded`,
    })
    .toBeGreaterThan(0);
}

/** A poster in the web client: an <img> whose alt text is the title. (A
 *  missing poster is replaced by an aria-hidden placeholder, which this does
 *  not match.) The first one: a looping rail repeats its cards. */
export function poster(scope: Page | Locator, title: string): Locator {
  return scope.getByRole('img', { name: title, exact: true }).first();
}

/** The block of the web client's detail page next to the poster: the title
 *  heading, year, type, genres, description and the credit blocks. */
export function titleInfo(page: Page, title: string): Locator {
  return page.getByRole('heading', { level: 1, name: title, exact: true }).locator('xpath=..');
}

/** A labelled block of names on the detail page ("Starring", "Director"):
 *  the label and the names that follow it. */
export function creditBlock(scope: Page | Locator, label: string | RegExp): Locator {
  return scope.getByText(label, { exact: true }).locator('xpath=..');
}

/** Attach data to the report — the API specs' counterpart of a screenshot. */
export async function attachJson(testInfo: TestInfo, name: string, data: unknown): Promise<void> {
  await testInfo.attach(`${name}.json`, {
    body: JSON.stringify(data, null, 2),
    contentType: 'application/json',
  });
}
