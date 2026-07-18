# site/ — the zaentrum product page

A static, self-contained landing page published to GitHub Pages at
**https://zaentrum.github.io/zaentrum/** by [`.github/workflows/pages.yml`](../.github/workflows/pages.yml).
It presents the product and links into the **wiki** for the technical docs — the
wiki stays the manual; this page is the front door.

## Files

| File | What | Edit? |
|---|---|---|
| `index.html` | the page — hand-authored. copy is lowercase/terse per the nalet voice | yes |
| `site.css` | landing-specific layout on top of the design-system tokens | yes |
| `nalet.css` | **vendored verbatim** from `@nalet/design-system` (`dist/assets/index.css`) — tokens + all `nc-*` components | no — refresh only |
| `favicon.svg` | **vendored** from `zaentrum-portal/public/favicon.svg` (the `>z` mark) | no — refresh only |

Fonts (Inter + JetBrains Mono) load from Google Fonts, matching the platform;
the design system deliberately does not bundle them.

## Refresh the vendored design system

```bash
cp <portal>/node_modules/@nalet/design-system/dist/assets/index.css site/nalet.css
```

## Design constraints (nalet design system)

Dark-only, square frames (`border-radius: 0`), monospace headings (JetBrains
Mono) with Inter body, a single blue accent (`#58A6FF`), lowercase copy, no emoji
or exclamation marks. If it starts to look like a glossy SaaS landing page, it has
drifted off-brand.
