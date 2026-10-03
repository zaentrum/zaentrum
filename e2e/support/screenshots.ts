// Full-page screenshots for the HTML report, so a run doubles as a gallery
// of what each page looks like: run before a UI change and after it, and
// compare the two reports. Nothing here asserts on pixels — the data on a
// live instance changes.
import type { Locator, Page, TestInfo } from '@playwright/test';

/** Elements that show who is signed in. They are masked in every capture,
 *  so a report never shows an account name. */
function identity(page: Page): Locator[] {
  return [
    page.locator('.sh__bar-right'), // portal + catalog console: name badge, sign out
    page.locator('button[title="Account"]'), // chino: the account avatar
  ];
}

/** Inner scroll containers keep a page's content out of a plain full-page
 *  capture (chino scrolls its <main>, not the document). Grow the viewport
 *  to the tallest of them for the shot, then put it back. */
async function contentHeight(page: Page): Promise<number> {
  return page.evaluate(() => {
    const viewport = document.documentElement.clientHeight;
    let height = document.documentElement.scrollHeight;
    for (const el of Array.from(document.querySelectorAll<HTMLElement>('body *'))) {
      const overflowY = getComputedStyle(el).overflowY;
      if ((overflowY === 'auto' || overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 1) {
        height = Math.max(height, viewport + (el.scrollHeight - el.clientHeight));
      }
    }
    return height;
  });
}

/** Wait (bounded) for the images now on screen to finish loading. */
async function onScreenImagesComplete(page: Page, timeout: number): Promise<void> {
  await page
    .waitForFunction(
      () =>
        Array.from(document.images)
          .filter((img) => {
            const r = img.getBoundingClientRect();
            return r.width > 0 && r.height > 0 && r.bottom > 0 && r.right > 0 &&
              r.top < window.innerHeight && r.left < window.innerWidth;
          })
          .every((img) => img.complete),
      undefined,
      { timeout },
    )
    .catch(() => undefined); // a slow poster must not fail a test
}

/** Wait (bounded) until no image request has been in flight for `quietMs`.
 *  Growing the viewport starts lazy images, and an app may swap an image's
 *  URL after it rendered (chino adds its artwork token), so "complete" alone
 *  can be true a moment before the picture the page ends up with. */
async function imageRequestsQuiet(page: Page, quietMs: number, timeout: number): Promise<void> {
  let inFlight = 0;
  let last = Date.now();
  const started = (r: { resourceType(): string }) => {
    if (r.resourceType() === 'image') {
      inFlight += 1;
      last = Date.now();
    }
  };
  const ended = (r: { resourceType(): string }) => {
    if (r.resourceType() === 'image') {
      inFlight = Math.max(0, inFlight - 1);
      last = Date.now();
    }
  };
  page.on('request', started);
  page.on('requestfinished', ended);
  page.on('requestfailed', ended);
  try {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline && (inFlight > 0 || Date.now() - last < quietMs)) {
      await page.waitForTimeout(100);
    }
  } finally {
    page.off('request', started);
    page.off('requestfinished', ended);
    page.off('requestfailed', ended);
  }
}

async function imagesSettled(page: Page): Promise<void> {
  await onScreenImagesComplete(page, 8_000);
  await imageRequestsQuiet(page, 500, 8_000);
  await onScreenImagesComplete(page, 4_000);
}

const MAX_HEIGHT = 12_000;

/** Attach a full-page PNG of the page as it is now. */
export async function fullPageShot(page: Page, testInfo: TestInfo, name: string): Promise<void> {
  if (page.isClosed()) return;
  const viewport = page.viewportSize();
  try {
    const height = Math.min(await contentHeight(page), MAX_HEIGHT);
    if (viewport && height > viewport.height) {
      await page.setViewportSize({ width: viewport.width, height });
    }
    await imagesSettled(page);
    const body = await page.screenshot({
      fullPage: true,
      animations: 'disabled',
      mask: identity(page),
      timeout: 20_000,
    });
    await testInfo.attach(`${name}.png`, { body, contentType: 'image/png' });
  } finally {
    if (viewport && !page.isClosed()) await page.setViewportSize(viewport);
  }
}
