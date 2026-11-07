# The portal

The portal is where people sign in to zaentrum. Its home page opens every app,
in spaces, and its settings are where the people who run the platform change
it. This section is the portal's product spec: what its screens show, who sees
what, and the exact words.

The general patterns come from the [nalet design system](https://nalet.github.io/design-system/),
and this spec doesn't repeat them:

- [Home & tiles](https://nalet.github.io/design-system/patterns/home-and-tiles/):
  tiles in groups, what gets a tile, and how the search finds them.
- [Top bar](https://nalet.github.io/design-system/patterns/top-bar/): the bar
  across every screen, with the one search.
- [Settings and setup](https://nalet.github.io/design-system/patterns/settings-and-setup/):
  where each kind of setting lives, and an app's setup checklist.
- [App navigation](https://nalet.github.io/design-system/patterns/app-navigation/):
  an app's own views, which get no tiles.

The home page has the form of the [chino chapters](../chino/README.md): first
what is deployed, in screenshots of the public demo, then the target, then
every difference between the two as a numbered change, and only a change the
owner approved is built. Its target figures are drawn on chino's drawing kit,
the design system's stylesheet and components with the portal's frame; their
source is [img/home.html](./img/home.html). The settings page shows the target
only, in a mockup whose source is [img/mockups.html](./img/mockups.html), and
nothing on it is built until a change to it is approved.
`node scripts/render-mockups.mjs portal` draws the pictures again after a change.

## Pages

| Page | What it covers |
|---|---|
| [Home page](./home.md) | As deployed, then the target: the spaces bar under the top bar, the spaces and their tiles, the search across spaces, who sees what, and the changes between the two |
| [Settings and setup](./settings.md) | Where each kind of setting lives, and an addon's setup checklist |
