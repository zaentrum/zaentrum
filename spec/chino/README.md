# 1 Introduction

chino is how people watch the library: on the web, on a phone or a tablet, on
Android TV and on Samsung TVs. This specification describes every chino screen:
what it shows, how it behaves, what it says in each state, and how it looks on a
computer, a phone and a TV.

> **What is deployed, and what is the target.** Each chapter shows first what
> the apps do today, under “As deployed”, with screenshots of the deployed web;
> then the target, the drawings and rules of how the screens are meant to be, on
> the design system 0.4.0; then, under “Changes”, every difference between the
> two as a numbered change with its status. Only a change the owner approved is
> built, one at a time, and anything no change names stays as it is deployed.

## 1.1 Scope

The specification covers the four chino apps:

| App | Runs on | Sizes |
|---|---|---|
| The web app | any browser | computer, phone |
| The phone app | Android phones and tablets (iOS later) | phone |
| The Android TV app | Android TV and Google TV | TV |
| The Samsung TV app | Samsung TVs (not released yet) | TV |

It doesn't cover the server, the portal ([the portal's pages](../portal/README.md))
or the consoles where a server is set up.

## 1.2 How to read the figures

Every screen is drawn at three sizes, and each drawing is a numbered figure that
the text refers to: figure 4.2 is the second figure of chapter 4.

| Size | Drawn at | Used by |
|---|---|---|
| Computer | 1280 × 800 | the web on a computer, from 1024 wide |
| Phone | 360 dp wide | the phone app, and the web on a phone |
| TV | 960 × 540 dp, the grid Android TV lays out on | both TV apps |

A tablet runs the phone app and has the phone's layout until this specification
draws one of its own.

Pink marks are notes on a drawing, never part of a screen. A pink number points
at a part of the screen, and the numbered list under the figure's caption says
what that part is and does. On a TV, a dashed pink outline shows the safe area,
the part of the screen that every TV shows in full.

The drawings show how the screens should be, on the
[nalet design system](https://nalet.github.io/design-system/) 0.4.0, and not how
any one app looks today. How the apps look today is in each chapter's section
“As deployed”, in screenshots of the web taken on the demo. The drawings' films
and shows are those the reference demo carries.

## 1.3 How a chapter is built

A chapter specifies one screen, or a few that belong together, in the same
order:

1. **Purpose**: what the screen is for, and how people get to it.
2. **As deployed**: what each app shows and does today, with screenshots of
   the deployed apps, taken on the demo, which runs the same build.
3. **The target**: the screen at each size, a figure for the computer, then the
   phone held upright and sideways, and the TV, with the rules behind what it
   shows and does.
4. **Changes**: every difference between the two, one numbered change per row
   (11.C1, 11.C2 …), with the apps it's built in and its status: proposed,
   approved, built, verified. Only an approved change is built, one at a time;
   anything no change names stays as it is deployed.
5. **States**: loading, empty, couldn't load and offline, with figures for the
   ones that matter.
6. **Words**: every text the screen shows, exactly.

Chapters 2 to 17 have this form; chapter 18 holds the words they share. A
change the owner approves is named by its number, as in “approve 11.C2”; its
status then moves to approved, built once it is in the apps, and verified once
the deployed apps show it.

## 1.4 The chapters

| No. | Chapter | What it covers |
|---|---|---|
| 1 | Introduction | this chapter |
| 2 | [The frame](./frame.md) | the top bar, the phone's tabs, the TV's rail, the avatar's menu |
| 3 | [Getting started](./start.md) | adding a server, signing in, who's watching |
| 4 | [Home](./home.md) | the first screen after signing in |
| 5 | [Movies and shows](./browse.md) | the library by kind, with filters |
| 6 | [The title page](./title-actions.md) | a movie or a show, and what can be done with it |
| 7 | [People](./person.md) | a person and what of theirs the library has |
| 8 | [Watchlist and lists](./watchlist.md) | the watchlist and named lists |
| 9 | [Search](./search.md) | the one search, and its results |
| 10 | [Zap](./zap.md) | zapping through scenes of the library |
| 11 | [The player](./playback.md) | watching, and the player's controls and menus |
| 12 | [Subtitles](./subtitles.md) | the audio and subtitles panel, how subtitles look, and what switches on by itself |
| 13 | [Downloads and offline](./downloads.md) | taking titles along on a phone or a tablet |
| 14 | [Casting](./casting.md) | watching on a TV from the phone |
| 15 | [Notifications](./notifications.md) | the bell and what it holds |
| 16 | [Settings and account](./settings.md) | settings, the account, signing out, reporting a bug |
| 17 | [When something goes wrong](./errors.md) | what a screen says when it can't do its job, by cause |
| 18 | [Words](./words.md) | the words chino uses for its own things |

## 1.5 The design system

The general rules come from the nalet design system, and this specification
doesn't repeat them:

- [Meaningful text](https://nalet.github.io/design-system/foundations/meaningful-text/):
  every sentence true, on every installation, in the reader's words.
- [Content and voice](https://nalet.github.io/design-system/foundations/content-voice/):
  the two voices, the monospace face in lowercase for chrome and the body face
  in sentence case for text.
- [Empty states](https://nalet.github.io/design-system/patterns/empty-states/#when-it-couldnt-load-say-why):
  what a screen says when it couldn't load, by cause.
- [Loading and progress](https://nalet.github.io/design-system/patterns/loading-and-progress/):
  what a screen shows while it waits.
- [TV focus](https://nalet.github.io/design-system/patterns/tv-focus/): the one
  focus style on a TV, and its safe area.
- [Colour](https://nalet.github.io/design-system/styles/colour/#contrast): a
  label or an icon on a filled colour is dark.

## 1.6 The drawings' sources

Whole screens are drawn in one file per chapter, `img/ch04-home.html` for
chapter 4 and so on, and parts such as controls, menus and dialogs in
[img/mockups.html](./img/mockups.html). They share one stylesheet
([img/screens.css](./img/screens.css)), and [img/frame.js](./img/frame.js)
draws the frame of chapter 2 around every screen and places the pink marks.
`node scripts/render-mockups.mjs chino` draws every figure again after a change.
