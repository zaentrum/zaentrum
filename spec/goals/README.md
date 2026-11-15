# What zaentrum is for

zaentrum is for a household that owns films, shows and music and wants to enjoy
them on every screen it has, from a server it runs itself. And it is open:
anyone can run it, look into it, change it and add to it.

Two things are not goals, and nothing in the platform is built for them:

- **A household's own photos and home videos.** zaentrum is for what a
  household owns, not for what it made itself.
- **Books to read.** zaentrum plays what is watched or listened to; a book has
  its place in it as an audiobook.

Everything else in the specification follows from that, one step at a time:

1. **What people want.** To watch their films and shows, to listen to their
   music. These are the goals the platform exists for.
2. **What that takes.** To watch a film, the platform has to know the film: so
   a library has to be kept. A household is several people: so they have to be
   told apart. And somebody has to run it. These goals exist only because the
   first ones do.
3. **What being open adds.** Anyone can add what the platform leaves out, and
   anyone can check that it does what it says.
4. **How well.** Each goal has qualities: what "well" means for it, what
   measures that, what it is today, and the target.
5. **What the platform does for it.** The [capabilities](../capabilities/README.md):
   every area of them is for one goal, and so is every
   [expectation](../capabilities/expectations.md).
6. **What does it.** The components of the [architecture](../architecture/README.md)
   that serve those capabilities.

So a capability is there because a goal needs it, and a goal is met when what
is expected of it is there and its qualities reach their targets.

On the site the goals are also a [map](https://zaentrum.github.io/spec/goals/map/):
a band for each kind of goal, a card for each goal, and in it a tile for each
group of capabilities that is for it, coloured by how much of it is built,
whether it holds a capability nothing serves yet, or how deep it is specified.
Pointing at a goal draws the goals it needs and the goals that need it.

> **Written by hand, counted by a program.** The goals are
> [goals.csv](./goals.csv) and their qualities [qualities.csv](./qualities.csv);
> the picture, the tables and the numbers on this page are computed from them
> and from the two layers below. A check fails when an area, an expectation or
> a quality is for no goal, or a goal has nothing below it.

## How to read it

A goal is one of three kinds:

| Kind | Means |
|---|---|
| what people want | what a household does with its media: the reason the platform exists |
| what that takes | what has to be there for it: it serves no one by itself |
| what being open adds | what an open product owes the people who run, check and extend it |

An arrow in the picture leads from a goal to a goal it **needs**: watching
needs a library, a library needs a platform that runs.

A **quality** is one sentence of what a goal has to be met with, its kind after
ISO/IEC 25010, what measures it, and what it is **today**: a number where one
was measured, the plain fact where the documentation or the code states it,
“not measured” otherwise. A **target** marked proposed is a proposal: it counts
once the owner approves it, and until then nothing says whether today is good
enough.

## The cascade

<!-- generated: cascade -->
```mermaid
flowchart TD
  subgraph k_use["what people want"]
    g_watch["Watch films and shows"]; g_listen["Listen to music, audiobooks and podcasts"]; g_live["Watch live channels"]
  end
  subgraph k_enable["what that takes"]
    g_library["Keep the library"]; g_people["Share it with a household"]; g_run["Run it oneself"]
  end
  subgraph k_open["what being open adds"]
    g_extend["Make it one's own"]; g_trust["Trust it"]
  end
  k_use --> g_library
  k_use --> g_people
  k_use --> g_run
  g_library --> g_run
  g_people --> g_run
  g_run --> g_trust
  g_extend --> g_run
```
<!-- end: cascade -->

## The goals

<!-- generated: goals -->
| Goal | Is | Needs | Expected of it | Capabilities | Qualities |
|---|---|---|---|---|---|
| [Watch films and shows](#watch-films-and-shows) | what people want | [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Run it oneself](#run-it-oneself) | 14: 9 partly, 4 not there, 1 not checked | 150 in 15 areas, 17 served by nothing | 5, 5 with a target, 5 approved |
| [Listen to music, audiobooks and podcasts](#listen-to-music-audiobooks-and-podcasts) | what people want | [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Run it oneself](#run-it-oneself) | 2: 2 not there | 2 in 1 area, 1 served by nothing | — |
| [Watch live channels](#watch-live-channels) | what people want | [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Run it oneself](#run-it-oneself) | 1: 1 not there | 1 in 1 area | — |
| [Keep the library](#keep-the-library) | what that takes | [Run it oneself](#run-it-oneself) | 12: 1 there, 5 partly, 5 not there, 1 decided otherwise | 54 in 3 areas, 14 served by nothing | 4, 4 with a target, 4 approved |
| [Share it with a household](#share-it-with-a-household) | what that takes | [Run it oneself](#run-it-oneself) | 11: 1 there, 5 partly, 5 not there | 17 in 1 area, 10 served by nothing | 2, 2 with a target, 2 approved |
| [Run it oneself](#run-it-oneself) | what that takes | [Trust it](#trust-it) | 12: 2 there, 6 partly, 4 not there | 66 in 4 areas, 23 served by nothing | 5, 5 with a target, 5 approved |
| [Make it one's own](#make-it-ones-own) | what being open adds | [Run it oneself](#run-it-oneself) | 5: 2 there, 1 partly, 2 not there | 12 in 1 area, 2 served by nothing | 1, 1 with a target, 1 approved |
| [Trust it](#trust-it) | what being open adds | — | 4: 1 partly, 3 not there | 4 in 1 area, 3 served by nothing | 4, 4 with a target, 4 approved |
<!-- end: goals -->

<!-- generated: by-goal -->
## Watch films and shows

A household watches the films and shows it owns, on every screen it has. It needs: [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Run it oneself](#run-it-oneself).

- **Expected of it:** [14 expectations](../capabilities/expectations.md#watch-films-and-shows): 9 partly, 4 not there, 1 not checked.
- **Capabilities:** [Connecting and signing in](../capabilities/chino.md#connecting-and-signing-in) (20), [The frame](../capabilities/chino.md#the-frame) (10), [Home](../capabilities/chino.md#home) (11), [Movies and shows](../capabilities/chino.md#movies-and-shows) (11), [The title page](../capabilities/chino.md#the-title-page) (11), [People](../capabilities/chino.md#people) (2), [Watchlist and lists](../capabilities/chino.md#watchlist-and-lists) (11), [Search](../capabilities/chino.md#search) (7), [Zap](../capabilities/chino.md#zap) (9), [The player](../capabilities/chino.md#the-player) (22), [Subtitles](../capabilities/chino.md#subtitles) (9), [Downloads and offline](../capabilities/chino.md#downloads-and-offline) (5), [Casting](../capabilities/chino.md#casting) (6), [Notifications](../capabilities/chino.md#notifications) (5), [Settings and account](../capabilities/chino.md#settings-and-account) (11).
- **Served by:** `chino-web`, `chino-mobile`, `chino-androidtv`, `chino-tizen`, `portal-api`, `chino-api`, `chino-stream`, `katalog-api`.

| It has to | Quality | Measured by | Today | Target | Says so |
|---|---|---|---|---|---|
| A title starts soon after it is chosen | performance efficiency | seconds from play to the first picture, on each kind of device | not measured | a packaged title at home: half within 2 s, nine in ten within 4 s; a title converted while it plays: within 10 s | — |
| A title plays through without stalling | reliability | stalls in an hour of playing | not measured; the apps send how playback went, and no page shows it | no stall in nine of ten hours played at home, by the counts the server keeps of what the apps report | — |
| It plays on the screens a household owns | compatibility | the kinds of device with an app, and where each is had | the web, Android and iOS phones and tablets, Android TV and Samsung TVs; none from a public store | the web; Android and iOS phones and tablets, Android TV and Samsung TVs, each from its public store | [The apps](../../docs/releases.md#the-apps) |
| It speaks the household's languages | interaction capability | the languages of the apps and the consoles | English | English and German, complete in every app and console; a further language is one file | — |
| People who see or hear less can use it | interaction capability | the accessibility level the apps meet | none is stated, and no app is checked with a screen reader | WCAG 2.2 AA on the web; in the apps every screen passes a walk with the device's screen reader | — |

## Listen to music, audiobooks and podcasts

It listens to its music, audiobooks and podcasts, in one app. It needs: [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Run it oneself](#run-it-oneself).

- **Expected of it:** [2 expectations](../capabilities/expectations.md#listen-to-music-audiobooks-and-podcasts): 2 not there.
- **Capabilities:** [Music, audiobooks and podcasts](../capabilities/platform.md#music-audiobooks-and-podcasts) (2).
- **Served by:** `katalog-api`.

No quality is stated for it yet.

## Watch live channels

It watches live channels, and what it recorded of them. It needs: [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Run it oneself](#run-it-oneself).

- **Expected of it:** [1 expectation](../capabilities/expectations.md#watch-live-channels): 1 not there.
- **Capabilities:** [Live channels](../capabilities/platform.md#live-channels) (1).
- **Served by:** no component yet.

No quality is stated for it yet.

## Keep the library

To watch or listen, the platform has to know what the household owns: take it in, describe it, and make it ready to play on every device. It needs: [Run it oneself](#run-it-oneself). Needed by: [Watch films and shows](#watch-films-and-shows), [Listen to music, audiobooks and podcasts](#listen-to-music-audiobooks-and-podcasts), [Watch live channels](#watch-live-channels).

- **Expected of it:** [12 expectations](../capabilities/expectations.md#keep-the-library): 1 there, 5 partly, 5 not there, 1 decided otherwise.
- **Capabilities:** [The catalog](../capabilities/catalog.md#the-catalog) (24), [The library and its originals](../capabilities/catalog.md#the-library-and-its-originals) (16), [Preparing titles to play](../capabilities/catalog.md#preparing-titles-to-play) (14).
- **Served by:** `zaentrum-portal`, `portal-api`, `katalog-manager-ui`, `chino-api`, `live-worker`, `katalog-api`, `katalog-manager`, `zae`.

| It has to | Quality | Measured by | Today | Target | Says so |
|---|---|---|---|---|---|
| A new file is ready to watch without work | functional suitability | steps by hand from a file's arrival to a title that plays | one: a scan, started by hand | none: a file that arrives is found, described and made ready to play by itself | [Getting content in](../../docs/self-hosting.md#getting-content-in) |
| A title is recognised for what it is | functional suitability | the share of titles matched without a hand | not measured | 95 of 100 titles named the usual way matched without a hand; the rest listed for an admin | — |
| Nothing of the library is lost | reliability | what a dead disk costs | the bundled databases: up to a day, by their daily dumps; the files: what their storage keeps | the databases: a day at most, kept apart from them; the files: the admin's to back up, and the catalog is rebuilt from them | [zaentrum-operator, README.md](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/README.md#backups-of-the-bundled-postgres-specbackup) |
| A title keeps the picture and the sound that matter | functional suitability | what a package keeps of its original | every track in stereo, 5.1 where turned on, HDR10 or HLG; originals stay unless set to go | as today: what ADR-0015 keeps; lossless sound and Dolby Vision stay with an original that is kept | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |

## Share it with a household

A household is several people: each signs in, sees what they may, and keeps a place, lists and a history of their own. It needs: [Run it oneself](#run-it-oneself). Needed by: [Watch films and shows](#watch-films-and-shows), [Listen to music, audiobooks and podcasts](#listen-to-music-audiobooks-and-podcasts), [Watch live channels](#watch-live-channels).

- **Expected of it:** [11 expectations](../capabilities/expectations.md#share-it-with-a-household): 1 there, 5 partly, 5 not there.
- **Capabilities:** [People and roles](../capabilities/portal.md#people-and-roles) (17).
- **Served by:** `zaentrum-portal`, `portal-api`, `chino-api`.

| It has to | Quality | Measured by | Today | Target | Says so |
|---|---|---|---|---|---|
| A child sees only what it may | security | ways around a rating cap | one: switching accounts on a shared device asks for nothing | none: on a shared device an account without a cap is behind a code | — |
| Someone who forgot a password is back in soon | interaction capability | who resets it, and how | an admin, with a new invite link from the people page; nothing is sent | the person, by a link sent by mail, where mail is set up; else an admin, in the portal | [First run](../../docs/self-hosting.md#first-run) |

## Run it oneself

Somebody runs it: installs it, makes it reachable, keeps it up to date, backs it up, and learns when it fails. It needs: [Trust it](#trust-it). Needed by: [Watch films and shows](#watch-films-and-shows), [Listen to music, audiobooks and podcasts](#listen-to-music-audiobooks-and-podcasts), [Watch live channels](#watch-live-channels), [Keep the library](#keep-the-library), [Share it with a household](#share-it-with-a-household), [Make it one's own](#make-it-ones-own).

- **Expected of it:** [12 expectations](../capabilities/expectations.md#run-it-oneself): 2 there, 6 partly, 4 not there.
- **Capabilities:** [The portal's home](../capabilities/portal.md#the-portals-home) (6), [Apps, spaces, tiles and extensions](../capabilities/portal.md#apps-spaces-tiles-and-extensions) (5), [Running the platform](../capabilities/portal.md#running-the-platform) (24), [Installing and configuring](../capabilities/platform.md#installing-and-configuring) (31).
- **Served by:** `zaentrum-portal`, `portal-api`, `chino-api`, `chino-stream`, `live-worker`, `katalog-api`, `katalog-manager`, `katalog-ingest`, `zaentrum-operator`, `zae`.

| It has to | Quality | Measured by | Today | Target | Says so |
|---|---|---|---|---|---|
| Someone who has not seen it installs it in an evening | flexibility | time from nothing to a film on the TV | not measured; a TV or a phone needs a name and an https certificate of one's own first | 30 minutes from the install command to a film on a TV at home, with no name or certificate of one's own | [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance) |
| It runs on the machine a household has | flexibility | the processors it runs on, and the memory it takes | amd64 alone; no smallest machine is named | amd64 and arm64; 4 cores and 8 GB of memory named as the smallest machine, and tested on it | [Appliance](../../docs/prerequisites.md#appliance) |
| An update never leaves it broken | reliability | what follows an update that fails | the platform checks itself after each update; nothing says how one is undone | an update that fails its own check goes back to the version before by itself, and says so | [updating](../../docs/updating.md) |
| After a dead disk it is back, with little lost | reliability | time and loss to a working platform on another machine | the bundled databases restore into the install that made them; there is no way to another machine | working on another machine within an hour, a day lost at most, from a backup kept apart | [zaentrum-operator, README.md](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/README.md#backups-of-the-bundled-postgres-specbackup) |
| Whoever runs it learns of a failure before the household does | reliability | how a failure reaches them | it is shown in the portal to whoever looks; nothing is sent | a mail and a notice to the admins within 15 minutes of a part failing, a volume filling or a backup missing | — |

## Make it one's own

The platform leaves things out on purpose; anyone adds them as an addon, without changing the platform. It needs: [Run it oneself](#run-it-oneself).

- **Expected of it:** [5 expectations](../capabilities/expectations.md#make-it-ones-own): 2 there, 1 partly, 2 not there.
- **Capabilities:** [Addons](../capabilities/portal.md#addons) (12).
- **Served by:** `chino-web`, `chino-mobile`, `chino-androidtv`, `chino-tizen`, `zaentrum-portal`, `portal-api`, `chino-api`, `zaentrum-operator`, `zae`.

| It has to | Quality | Measured by | Today | Target | Says so |
|---|---|---|---|---|---|
| What an addon builds on stays as it is | compatibility | the promise on the platform's interfaces | none: the platform is at version 0, its resource at v1alpha1 | the interfaces addons use are listed with a version each; one changes only with a new version, announced a release ahead | [releases](../../docs/releases.md) |

## Trust it

Anyone can see what it does, check it, change it, and count on it staying open. Needed by: [Run it oneself](#run-it-oneself).

- **Expected of it:** [4 expectations](../capabilities/expectations.md#trust-it): 1 partly, 3 not there.
- **Capabilities:** [Releases one can trust](../capabilities/platform.md#releases-one-can-trust) (4).
- **Served by:** no component yet.

| It has to | Quality | Measured by | Today | Target | Says so |
|---|---|---|---|---|---|
| A security hole can be reported in private | security | a policy that says where and how | a security policy in every repository, private reporting on, an answer within 7 days | a security policy in every repository, with private reporting on and an answer within 7 days | — |
| Every image can be traced to the source it was built from | security | signatures, a record of each build, a list of what an image holds | none of the three | every released image signed, with the record of its build and the list of what it holds published | — |
| What the apps send stays with whoever runs the server | security | what leaves the apps for anyone else | nothing to their publisher; an avatar service, a font service and Google Cast are called | nothing but to the server, and to what the person starts themselves, such as casting; avatars and fonts come from the server | [What the apps send](../../docs/releases.md#what-the-apps-send) |
| A stranger can change it and have the change taken in | maintainability | a guide to contributing, and tests that run on every change | tests in the services' repositories; a guide in the operator's alone | a guide to contributing in every repository, and its tests run on every change | — |
<!-- end: by-goal -->

## The files

| File | Written by | Holds |
|---|---|---|
| [goals.csv](./goals.csv) | hand | one row a goal: its kind, the goals it needs, why it is one |
| [qualities.csv](./qualities.csv) | hand | one row a quality: its goal, its kind, what measures it, today, the target and whether it is proposed or approved, where it is said |
| the picture and the tables of this page | `scripts/capabilities.py` | never edited by hand |

An area's goal is in [areas.csv](../capabilities/areas.csv), an expectation's
in [expectations.csv](../capabilities/expectations.csv).
