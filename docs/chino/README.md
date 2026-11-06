# The chino apps

chino is how people watch the library: on the web, on Android TV, on a phone or
a tablet, and on Samsung TVs. This section is chino's product spec: what its
screens show, what each state looks like, and the exact words. Every chino app
follows it, so a title, a download or a subtitle behaves the same everywhere.

The general rules come from the [nalet design system](https://nalet.github.io/design-system/),
and this spec doesn't repeat them:

- [Meaningful text](https://nalet.github.io/design-system/foundations/meaningful-text/):
  every sentence true, on every installation, in the reader's words.
- [Empty states](https://nalet.github.io/design-system/patterns/empty-states/#when-it-couldnt-load-say-why):
  what a screen says when it couldn't load, by cause.
- [TV focus](https://nalet.github.io/design-system/patterns/tv-focus/): the one
  focus style on a TV, and its safe area.
- [Colour](https://nalet.github.io/design-system/styles/colour/#contrast): a
  label or an icon on a filled colour is dark.

The pictures are drawings of this spec, made with the design system's colours,
type and icons. They show the spec, not one app. A whole screen is drawn at
three sizes, computer, phone and TV, and [screens](./screens.md) maps every
screen to its drawings and to what each app has today. The sources are
[img/screens.html](./img/screens.html) for whole screens and
[img/mockups.html](./img/mockups.html) for parts, and
`node scripts/render-mockups.mjs chino` draws them again after a change.

## Pages

| Page | What it covers |
|---|---|
| [Screens](./screens.md) | Every screen, the sizes it's drawn at, and what each app has today |
| [Home](./home.md) | The first screen after signing in, at all three sizes, with the frame around every screen |
| [Title actions](./title-actions.md) | Play, add to list, watched and liked: one size and one look everywhere |
| [Playback](./playback.md) | Resume and play, a finished title, the quality notices, the picture fitted and filled, and what a page says when it couldn't load |
| [Subtitles](./subtitles.md) | How subtitles look, the menu, and what switches on by itself |
| [Downloads and offline](./downloads.md) | Taking titles along on a phone or a tablet |
| [Casting](./casting.md) | Watching on a TV from the phone |
| [Words](./words.md) | The words chino uses for its own things |
