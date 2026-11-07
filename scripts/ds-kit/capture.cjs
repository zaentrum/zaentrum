// capture.cjs: renders the design system's real components (catalog.jsx, with the
// package installed here) in a browser and saves what they render, for gen-ds.py:
//   out/catalog-markup.json   each example's markup, the open menus', the dialog's, the toasts'
//   out/catalog.png           every example, to compare the kit's drawings with
// and copies the package's stylesheet, unchanged, to spec/chino/img/ds/nalet-<version>.css.
//   npm install && PLAYWRIGHT=<path to playwright> node capture.cjs && python3 gen-ds.py out/catalog-markup.json ../../spec/chino/img/ds.js
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const here = __dirname, out = path.join(here, 'out');
fs.mkdirSync(out, { recursive: true });
const pkg = path.join(here, 'node_modules', '@nalet', 'design-system');
const version = JSON.parse(fs.readFileSync(path.join(pkg, 'package.json'), 'utf8')).version;
const tokens = fs.readFileSync(path.join(pkg, 'dist', 'tokens.css'), 'utf8');
const styles = fs.readFileSync(path.join(pkg, 'dist', 'assets', 'index.css'), 'utf8');

// the spec's copy of the stylesheet
const vendored = path.join(here, '..', '..', 'spec', 'chino', 'img', 'ds', `nalet-${version}.css`);
fs.mkdirSync(path.dirname(vendored), { recursive: true });
fs.writeFileSync(vendored, `/* @nalet/design-system ${version}: dist/tokens.css and dist/assets/index.css (its styles.css),
   copied unchanged from the release tarball nalet-design-system-${version}.tgz
   (github.com/nalet/design-system, tag v${version}). MIT License, Copyright (c) 2026 nalet.
   Update by copying both files of a newer release; never edit them here. */\n${tokens}\n${styles}`);

// the catalog page
require('esbuild').buildSync({ entryPoints: [path.join(here, 'catalog.jsx')], bundle: true, format: 'iife', jsx: 'automatic',
  define: { 'process.env.NODE_ENV': '"production"' }, outfile: path.join(out, 'catalog.js'), logLevel: 'warning' });
fs.writeFileSync(path.join(out, 'ds.css'), tokens + '\n' + styles);
fs.writeFileSync(path.join(out, 'catalog.html'), `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ds catalog</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="ds.css"><style>body{margin:0;background:#0B0F19;color:#E6E6E6;font:14px/1.45 Inter,system-ui,sans-serif}</style></head>
<body><div id="root"></div><script src="catalog.js"></script></body></html>`);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
  page.on('pageerror', (e) => console.log('PAGEERROR', e.message));
  await page.goto('file://' + path.join(out, 'catalog.html'));
  await page.waitForTimeout(1500);
  await page.evaluate(() => document.fonts.ready);
  const m = {};
  for (const id of await page.$$eval('[data-ex]', (els) => els.map((e) => e.dataset.ex))) {
    m[id] = await page.$eval(`[data-ex="${id}"] .ex-body`, (e) => e.innerHTML);
  }
  const portals = () => page.evaluate(() => [...document.body.children]
    .filter((e) => e.id !== 'root' && e.tagName !== 'SCRIPT' && e.style.display !== 'none').map((e) => e.outerHTML).join('\n\n'));
  m['portals-closed'] = await portals();
  m['toaster'] = await page.evaluate(() => { const t = document.querySelector('.nc-toaster'); return t ? t.outerHTML : ''; });
  await page.evaluate(() => [...document.body.children].forEach((e) => { if (e.id !== 'root' && e.tagName !== 'SCRIPT') e.style.display = 'none'; }));
  await page.screenshot({ path: path.join(out, 'catalog.png'), fullPage: true });
  for (const [name, ex] of [['actionmenu-open', 'actionmenu'], ['actionmenu-labelled-open', 'actionmenu-labelled'], ['multiselect-open', 'multiselect']]) {
    await page.click(`[data-ex="${ex}"] button`);
    await page.waitForTimeout(400);
    m[name] = (await page.$eval(`[data-ex="${ex}"] .ex-body`, (e) => e.innerHTML)) + '\n<!-- portals -->\n' + (await portals());
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);
  }
  fs.writeFileSync(path.join(out, 'catalog-markup.json'), JSON.stringify(m, null, 1));
  console.log(`@nalet/design-system ${version}: ${Object.keys(m).length} examples; stylesheet -> ${path.relative(process.cwd(), vendored)}`);
  await browser.close();
})();
