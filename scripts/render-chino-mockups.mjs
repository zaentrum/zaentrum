#!/usr/bin/env node
// Renders the chino spec's mockups: every <figure class="shot" id="…"> in
// docs/chino/img/mockups.html becomes docs/chino/img/<id>.png, at twice the size.
//
//   npx -p playwright@1.63.0 node scripts/render-chino-mockups.mjs
//   (or PLAYWRIGHT=/path/to/node_modules/playwright node scripts/render-chino-mockups.mjs)
//
// Edit the mockups in the HTML, never the PNGs. The page loads its fonts from
// Google Fonts, so it needs the network.
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dir = path.join(root, 'docs', 'chino', 'img');
const only = process.argv.slice(2);

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 1400, height: 900 } });
  await page.goto(pathToFileURL(path.join(dir, 'mockups.html')).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const missing = await page.evaluate(() =>
    ['Inter', 'JetBrains Mono'].filter((f) => !document.fonts.check(`16px "${f}"`)));
  if (missing.length) throw new Error(`fonts did not load: ${missing.join(', ')}`);
  const ids = await page.$$eval('figure.shot', (els) => els.map((el) => el.id));
  for (const id of ids) {
    if (only.length && !only.includes(id)) continue;
    const file = path.join(dir, `${id}.png`);
    await page.locator(`#${id}`).screenshot({ path: file });
    console.log(`  ${path.relative(root, file)}`);
  }
} finally {
  await browser.close();
}
