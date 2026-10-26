# The portal

The portal is where people sign in to zaentrum. Its home page opens every app,
and its settings are where the people who run the platform change it. This
section is the portal's product spec: what its screens show, who sees what, and
the exact words.

The general patterns come from the [nalet design system](https://nalet.github.io/design-system/),
and this spec doesn't repeat them:

- [Home & tiles](https://nalet.github.io/design-system/patterns/home-and-tiles/):
  one page of tiles in a few fixed groups, and what gets a tile.
- [Top bar](https://nalet.github.io/design-system/patterns/top-bar/): the bar
  across every screen, with the one search.
- [Settings and setup](https://nalet.github.io/design-system/patterns/settings-and-setup/):
  where each kind of setting lives, and an app's setup checklist.
- [App navigation](https://nalet.github.io/design-system/patterns/app-navigation/):
  an app's own views, which get no tiles.

The pictures are mockups of this spec, drawn with the design system's colours,
type and icons. They show the spec, not today's portal: what differs today is
listed on each page. Their source is [img/mockups.html](./img/mockups.html),
and `node scripts/render-mockups.mjs portal` draws them again after a change.

## Pages

| Page | What it covers |
|---|---|
| [Home page](./home.md) | The groups, their tiles, and who sees them |
| [Settings and setup](./settings.md) | Where each kind of setting lives, and an addon's setup checklist |
