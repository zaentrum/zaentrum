# Downloads and offline

On a phone or a tablet, people can download a title and watch it without a
connection: on a train, on a plane, wherever the signal drops. A download is a
copy on the device, with its subtitles, kept for the account that made it, and
it plays even when the server can't be reached.

This page says “phone” throughout; on a tablet (600 dp wide and more) the app
says “tablet”.

## One status per title

The download control sits with the [title actions](./title-actions.md). It
shows the title's download status and offers the one thing that makes sense in
it.

| Status | The control says | What people can do |
|---|---|---|
| Not on the phone | “download · 1.4 GB” | Download it |
| Waiting its turn | “queued · 1.4 GB” | Cancel |
| Waiting for Wi-Fi | “waiting for Wi-Fi · 1.4 GB” | Cancel; it starts by itself on Wi-Fi |
| Waiting for a connection | “waiting for a connection · 1.4 GB” | Cancel; it starts by itself once the phone is online |
| On its way | “downloading 42% · 1.4 GB”, with a thin bar | Cancel |
| On the phone | “downloaded · 1.4 GB” | Play it, delete it |
| Needs a check | “downloaded · check needed”, and “Downloads are checked with the server every 30 days. This one plays again once the server can be reached.” | Nothing until the server can be reached |
| Failed | “couldn't download”, and the reason in a sentence | “try again”, or remove it from the list |
| Can't come along | “can't be downloaded”, and “This title can only be streamed.” | Nothing |

- The size is the size of exactly what will be downloaded at the chosen quality,
  as the server reports it: the same number before and after. When it isn't
  known, it is left out rather than guessed.
- Status and size are one text, and wrap as one; “check needed” stays together.
- The percentage changes at most once a second.
- A failure's sentence is a reason, never an instruction, because the control
  already offers “try again”. The reasons:
  - “Not enough space on this phone.”
  - “Can't reach the server.”
  - “This title isn't available to this account anymore.”
  - “The server has turned downloads off.”
  - “The server ran into a problem.”
  - “The server didn't accept the download.”
  - “The download stopped before it was done.”
- When the server has turned downloads off, a title's page offers no download.

### Series

Each episode has its own control. A season offers its episodes at once:

- “download season 1 · 8 episodes · 9.6 GB”, only when every episode of the
  season can be downloaded and none is on the phone or on its way yet;
- “download 6 episodes · 7.2 GB”, when some can only be streamed;
- “download 2 more episodes · 724 MB” (“1 more episode”), once some are on the
  phone or on their way.

A series that is partly on the phone says how far: “3 of 8 downloaded”. When the
server can't be reached, its page says only what is on the phone, “2 episodes on
this phone”, with no check mark while one of them needs a check.

## Whose downloads they are

A download belongs to the account that made it. Another account on the same
phone doesn't see it, so a child's account never plays a movie meant for a
parent. When a sign-in expires, nothing is hidden: signing in again as the same
account brings everything back. With several accounts on the phone and no server
to ask, the app opens on the account picker first, then on that account's
downloads.

Signing out, removing an account and changing the server delete that account's
downloads, so the app asks first. The title is the action, the confirming
button repeats it and is the danger button, and the body names what goes:

| Action | Title | It says |
|---|---|---|
| Sign out | “sign out” | “Your 23 downloads, 12.4 GB, are deleted from this phone.” |
| Remove an account | “remove account” | “The 23 downloads of Anna, 12.4 GB, are deleted from this phone.” |
| Change the server | “change server” | “Your 23 downloads, 12.4 GB, are deleted from this phone.” |

With one download: “Your download, 281 MB, is deleted from this phone.” and “The
download of Anna, 281 MB, is deleted from this phone.” With none, the action
works as it always does, unless something is casting: while it is, the
question is asked anyway and adds “Casting on Living Room TV stops.”

A download also goes when the server says the account may no longer watch the
title, because it left the library or the account's limit changed, after two such
answers at least an hour apart. The app says so once: “This title isn't
available to this account anymore, so it was deleted from this phone.” For
several at once, a banner on the downloads screen: “3 downloads were deleted
from this phone: they aren't available to this account anymore.”, with the
titles under details.

## The downloads screen

Everything on the phone, newest first, grouped by series and season, with
movies in a group of their own. Each title shows its status and size and plays
from there. A failed title shows its reason and no size: a failed download
frees what it had downloaded so far.

At the top, one line: “12.4 GB used by downloads · 18 GB free on this phone”.
With nothing downloaded, only “18 GB free on this phone”. The storage line and
the questions compute one total, from the bytes, rounded once.

- **Delete one** from the title's menu or its control. It asks nothing.
- **Delete all** at the end of the list asks once, in a dialog titled “delete
  all downloads”: “This removes 23 downloads, 12.4 GB, from this phone.”, with
  “cancel” and “delete all”. It counts only what is on the phone; with only failed entries left, it
  says “This clears the list of downloads.”
- **Empty**: “nothing downloaded yet”, and “Titles you download show up here,
  ready to watch without a connection.”

## When the server can't be reached

The app opens on the downloads screen with an information banner, “Can't reach
the server. Your downloads still play.”, or only “Can't reach the server.” when
nothing is downloaded. It has no close button while the server can't be
reached, and the bell is hidden.

- **A downloaded title's page** is built from what is on the phone, with the
  banner on top, under the top bar. What needs the server is left out: the
  Watchlist and other lists, the watched and liked marks, the trailer and the
  people. A title that
  needs its check shows play or resume dimmed, with the sentence that says why.
- **The player** offers the subtitles that came with the download, named as
  online. A title without subtitles offers only “off”.
- **Every other screen** that needs the server shows its couldn't-load screen.
- **Watch progress** made offline is kept and sent once the server can be
  reached, with nothing for people to do. Queued downloads then carry on.

## Settings

- **Download quality**: named as in the player's quality menu, with the size
  of an hour of video as the server reports it: “Medium (720p) · about 932 MB an hour”.
  Where too few titles have a quality to tell its size reliably, the size is
  left out.
- **Download over Wi-Fi only**: on by default.

## For the builders

- A download takes all of the title's subtitle tracks with it.
- Downloads wait only for the network, and for Wi-Fi when that setting is on;
  never for a charger, which would keep a background service running for hours.
- A download not checked with the server for 30 days asks for the server before
  it plays; with the server reachable, the check runs without anything on
  screen.
- Sizes: one decimal without a trailing zero (“18 GB”), MB below 1 GB.
