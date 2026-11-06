# Screens

Every screen of the chino apps, and how far the spec has drawn it. The spec
draws a whole screen at three sizes, so each app sees its own layout next to the
others:

| Size | Drawn at | Used by |
|---|---|---|
| Computer | 1280 × 800 | the web on a computer, from 1024 wide |
| Phone | 360 dp wide | the phone app, and the web on a phone |
| TV | 960 × 540 dp, the grid Android TV lays out on | both TV apps |

A tablet runs the phone app and has the phone's layout, until the spec draws one
for it.

A screen's page says what the screen is for and what's on it, in order. It has
the drawings at the three sizes and the screen's states: loading, empty,
couldn't load, and offline where that applies. Under **not built like this yet**
it lists where each app differs today, and those lists are the work still to do.
The frame around every screen (the top bar, the phone's tabs and the TV's rail)
is drawn on [home](./home.md).

## The map

**Drawn** is what the spec has. The app columns are what each app has today:
**built**, **not built** where the app lacks a screen the others have, or **—**
where the screen isn't part of that app.

| Screen | Page | Drawn | Web | Phone app | Android TV | Samsung TV |
|---|---|---|---|---|---|---|
| Add a server | — | — | — ¹ | built | built | built |
| Sign in | — | — | — ² | built | built ³ | built ³ |
| Who's watching | — | — | — | built | built | built |
| Home | [Home](./home.md) | computer, phone, TV | built | built | built | built |
| Movies and shows | — | — | built | built | built | built |
| Watchlist and lists | — | — | built | built | built | built |
| Search | — | — | built | built | built | built |
| Zap | — | — | built | built | built | built |
| Title page | [Title actions](./title-actions.md) | its actions | built | built | built | built |
| Person | — | — | built | built | built | built |
| Player | [Playback](./playback.md), [subtitles](./subtitles.md) | its menus and subtitles | built | built | built | built |
| Downloads | [Downloads and offline](./downloads.md) | phone | — | built | — | — |
| Casting | [Casting](./casting.md) | phone: the bar | — | built | — | — |
| Notifications | — | — | built ⁴ | built | built | built |
| Settings | — | — | built | built | built | built |
| Account | — | — | built | built | built | not built |
| Delete account | — | — | built | built | built | built |
| Report a bug | — | — | built | built | built | not built |
| When a page couldn't load | [Playback](./playback.md#when-a-page-couldnt-load) | — | built | built | built | not built |
| A new version | — | — | built ⁵ | — | — | — |

1. The web app comes from the server it belongs to.
2. The server's own sign-in page.
3. With a code entered on another device.
4. A panel under the bell, not a screen of its own.
5. The web offers to reload when a new version is out, and to be installed as an app.

The Samsung TV app isn't released; its column shows what its code has.

## Drawings

The drawings use the design system's colours, type and icons, at version 0.4.0.
Whole screens come from [img/screens.html](./img/screens.html), parts such as
controls, menus and dialogs from [img/mockups.html](./img/mockups.html), and
`node scripts/render-mockups.mjs chino` draws both again after a change. The
titles in them are films and shows the reference demo carries.
