#!/usr/bin/env node
// Renders a spec section's drawings: every <figure class="shot" id="…"> in an
// .html file in docs/<section>/img/ (mockups.html, screens.html, …) becomes
// docs/<section>/img/<id>.png, at twice the size.
//
//   npx -p playwright@1.63.0 node scripts/render-mockups.mjs chino [id …]
//   (or PLAYWRIGHT=/path/to/node_modules/playwright node scripts/render-mockups.mjs portal)
//
// Edit the drawings in the HTML, never the PNGs. The pages load their fonts from
// Google Fonts, so it needs the network.
import { createRequire } from 'node:module';
import { readdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [section, ...only] = process.argv.slice(2);
if (!section) throw new Error('usage: render-mockups.mjs <section> [id …], e.g. chino or portal');
const dir = path.join(root, 'docs', section, 'img');

const browser = await chromium.launch();
try {
  // wide enough for a whole computer screen (1280) with its frame and notes
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 1600, height: 1000 } });
  for (const html of readdirSync(dir).filter((name) => name.endsWith('.html')).sort()) {
    await page.goto(pathToFileURL(path.join(dir, html)).href, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const missing = await page.evaluate(() =>
      ['Inter', 'JetBrains Mono'].filter((f) => !document.fonts.check(`16px "${f}"`)));
    if (missing.length) throw new Error(`${html}: fonts did not load: ${missing.join(', ')}`);
    const ids = await page.$$eval('figure.shot', (els) => els.map((el) => el.id));
    for (const id of ids) {
      if (only.length && !only.includes(id)) continue;
      const file = path.join(dir, `${id}.png`);
      await page.locator(`#${id}`).screenshot({ path: file });
      console.log(`  ${path.relative(root, file)}`);
    }
  }
} finally {
  await browser.close();
}
