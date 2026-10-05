// The web client plays a title's own trailer — an extra this server keeps and
// packaged apart from the title — on the trailer page, opened from the title's
// detail page, without a word about the viewer's progress or watched state.
import type { Request } from '@playwright/test';
import { SINTEL } from '../../data/catalog';
import { chino } from '../../support/apps';
import { findTitle } from '../../support/catalog';
import { expect, test } from '../../support/fixtures';
import { titleInfo } from '../../support/pages';

interface Extra {
  id: string;
  kind: string;
  play_path: string;
}

/** The calls of the full player that a trailer never makes: a trailer has no
 *  progress, watched state, segments, trickplay, next episode or warm-up. */
const PLAYER_ONLY = /\/(progress|watched|segments|trickplay|prewarm|next)\b|\/play\/info\b/;

test.describe('trailers', () => {
  test('a title’s own trailer plays on the trailer page, and nothing is written about it', async ({ page, open, api, snap }) => {
    const sintel = await findTitle(api, SINTEL);
    const detail = await api.json<{ extras?: Extra[] }>(`/api/v1/items/${sintel.id}`);
    const trailer = (detail.extras ?? []).find((e) => e.kind === 'trailer');
    expect(trailer, 'Sintel has a trailer of its own').toBeTruthy();

    // Every call from the click on: the trailer page's.
    let onTrailer = false;
    const calls: string[] = [];
    page.on('request', (r: Request) => {
      if (onTrailer) calls.push(`${r.method()} ${new URL(r.url()).pathname}`);
    });

    await open(chino, `/i/${sintel.id}`);
    await expect(titleInfo(page, SINTEL.title)).toBeVisible();
    const button = page.getByRole('link', { name: 'Trailer', exact: true });
    await expect(button).toBeVisible();
    onTrailer = true;
    await button.click();
    await expect(page).toHaveURL(chino.url(`/trailer/${sintel.id}/${trailer!.id}`));

    // It plays: the clock passes two seconds (muted, should the browser
    // refuse sound without a click).
    await page.waitForFunction(
      () => {
        const video = document.querySelector('video');
        return !!video && video.currentTime > 2;
      },
      undefined,
      { timeout: 45_000, polling: 500 },
    );
    await snap('Sintel trailer');
    expect(
      calls.some((c) => c.startsWith('GET ') && c.endsWith(`/extras/${trailer!.id}/play/master.m3u8`)),
      'the extra’s own master was played',
    ).toBe(true);
    expect(calls.filter((c) => PLAYER_ONLY.test(c)), 'calls only the full player makes').toEqual([]);

    // Escape closes it, back on the title.
    await page.keyboard.press('Escape');
    await expect(titleInfo(page, SINTEL.title)).toBeVisible();
  });
});
