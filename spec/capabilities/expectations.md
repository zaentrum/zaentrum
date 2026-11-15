# Expectations

What people expect of a media server they run themselves, and what of it
zaentrum does today. The [capability model](./README.md) is complete against the
code: a program lists what the code offers, and the check fails when no
capability claims it. The code cannot say what is not there. This list does:
each row is one expectation, with the capabilities and components that meet it,
under the [goal](../goals/README.md) it is for.

> **Written by hand, counted by a program.** The expectations are
> [expectations.csv](./expectations.csv); the state of each is computed from the
> capabilities and components it names, never typed. An expectation is no
> requirement: it says what people look for, not what zaentrum will build. What
> is built is decided change by change in the chapters, and what is ruled out, by
> a decision record.

## How to read it

**State** is what the model says of an expectation as a whole:

| State | Means |
|---|---|
| there | every capability and component it names is built |
| partly | some of what it names is built, or it is built on some apps and faces only |
| not there | nothing it names is built: no app or face has it |
| not checked | nobody has looked yet |
| decided otherwise | a decision record rules it out, and says what the platform does instead |

**Met by** names each capability with its own state over every app and face
meant to have it (built, partial, no, not checked), each component with its
status, and the decision record where one decides it. A capability's key leads
to its area's table; the [map](https://zaentrum.github.io/spec/capabilities/map/)
shows the same capabilities as tiles.

**Next** says what becomes of a row that is not there, or only partly: **build**
where numbered changes of a chapter build what is missing; **later**, **an
addon's** or **ruled out** where [scope](./scope.md) leaves it out, with the
reason there. Where the capabilities of one row have different answers, the
first word is the answer for most of it, and the others name their
capabilities. Every answer is a proposal until the owner approves it. What
stands in a row's way in the platform as it is built is in
[the architecture's limits](../architecture/README.md#what-the-architecture-cannot-do-yet).

<!-- generated: expectations -->
## Watch films and shows

For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Get the apps from each device's store | not there | build | [`get-app-from-store`](./chino.md#connecting-and-signing-in) no | — |
| An app for the TV or the box a household owns | partly | later | [`chino-androidtv`](../architecture/components.md#the-apps) ships, [`chino-tizen`](../architecture/components.md#the-apps) ships, [`chino-tvos`](../architecture/components.md#the-apps) missing, [`chino-webos`](../architecture/components.md#the-apps) missing, [`chino-roku`](../architecture/components.md#the-apps) missing | — |
| Browse, search, resume, the next episode, a watchlist, a history | partly | build | [`browse-library`](./chino.md#movies-and-shows) built, [`search-titles`](./chino.md#search) built, [`resume-title`](./chino.md#the-player) partial, [`see-next-up`](./chino.md#home) built, [`keep-on-watchlist`](./chino.md#watchlist-and-lists) built, [`see-watch-history`](./chino.md#watchlist-and-lists) partial | — |
| Choose between the cuts of a title | not there | later | [`choose-cut`](./chino.md#the-title-page) no | — |
| Trailers and extras | partly | build | [`play-trailer`](./chino.md#the-title-page) built, [`manage-extras`](./catalog.md#the-catalog) partial | — |
| Subtitles of every kind show | partly | build; later: `show-dvb-subtitles` | [`choose-subtitles`](./chino.md#subtitles) built, [`show-pgs-subtitles`](./chino.md#subtitles) partial, [`show-vobsub-subtitles`](./chino.md#subtitles) no, [`show-dvb-subtitles`](./chino.md#subtitles) no, [`show-styled-subtitles`](./chino.md#subtitles) no | — |
| Surround sound where the room has it | not checked | build | [`play-surround`](./chino.md#the-player) not checked | — |
| Skip the intro, set the speed, picture in picture, a still while seeking | partly | build | [`skip-intro`](./chino.md#the-player) built, [`set-volume-speed`](./chino.md#the-player) partial, [`play-in-background`](./chino.md#the-player) partial, [`seek-title`](./chino.md#the-player) partial | — |
| Download to watch without a connection | partly | build | [`download-titles`](./chino.md#downloads-and-offline) partial, [`play-downloads-offline`](./chino.md#downloads-and-offline) partial | — |
| Play on a TV from a phone or a computer | partly | build | [`cast-title`](./chino.md#casting) partial, [`control-cast`](./chino.md#casting) partial, [`find-tv-app`](./chino.md#casting) no | — |
| Watch together from different places | not there | later | [`watch-together`](./chino.md#the-player) no | — |
| The interface in one's own language | not there | build | [`choose-interface-language`](./chino.md#settings-and-account) no | — |
| Usable with a screen reader and the device's accessibility settings | partly | build | [`use-with-screen-reader`](./chino.md#the-frame) not checked, [`hear-result-count`](./chino.md#search) no, [`follow-caption-preferences`](./chino.md#subtitles) partial | — |
| Suggestions of what to watch | partly | build | [`see-similar-titles`](./chino.md#the-title-page) built, [`see-top-rated`](./chino.md#home) built, [`zap-through-titles`](./chino.md#zap) partial | — |

## Listen to music, audiobooks and podcasts

For the goal [Listen to music, audiobooks and podcasts](../goals/README.md#listen-to-music-audiobooks-and-podcasts).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Music | not there | build | [`play-music`](./platform.md#music-audiobooks-and-podcasts) no | — |
| Audiobooks and podcasts | not there | later | [`listen-to-audiobooks`](./platform.md#music-audiobooks-and-podcasts) no | — |

## Watch live channels

For the goal [Watch live channels](../goals/README.md#watch-live-channels).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Live channels and recordings | not there | build | [`watch-live-channels`](./platform.md#live-channels) no | — |

## Keep the library

For the goal [Keep the library](../goals/README.md#keep-the-library).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Use the folders that already hold the library | partly | build; later: `configure-storage` | [`add-library-folder`](./catalog.md#the-catalog) no, [`configure-storage`](./platform.md#installing-and-configuring) partial, [`scan-library`](./catalog.md#the-catalog) partial | Files stay where they are unless an admin moves the platform to the library layout |
| Keep several libraries, each with its folders and its audience | not there | build | [`keep-several-libraries`](./catalog.md#the-catalog) no | — |
| New files appear by themselves | partly | build | [`scan-by-itself`](./catalog.md#the-catalog) no, [`scan-library`](./catalog.md#the-catalog) partial | — |
| Titles get their details with no account elsewhere | partly | build; later: `enrich-without-own-key` | [`enrich-without-own-key`](./catalog.md#the-catalog) no, [`enrich-titles`](./catalog.md#the-catalog) partial, [`set-metadata-key`](./catalog.md#the-catalog) built | — |
| Details and artwork kept beside the files are used | not there | build | [`read-local-metadata`](./catalog.md#the-catalog) no | — |
| Correct a title's match, details and artwork by hand | partly | build | [`match-title`](./catalog.md#the-catalog) built, [`edit-title`](./catalog.md#the-catalog) partial, [`choose-artwork`](./catalog.md#the-catalog) no | — |
| Collections everyone sees: a film series, a theme | not there | build | [`see-collections`](./chino.md#movies-and-shows) no, [`curate-collections`](./catalog.md#the-catalog) no | — |
| Any file plays right away, whatever its format | there | — | [`play-title`](./chino.md#the-player) built, [`encode-while-playing`](./catalog.md#preparing-titles-to-play) built | — |
| Get a title back as an ordinary file once its original is gone | not there | build | [`export-title`](./catalog.md#the-library-and-its-originals) no | Originals are kept unless an admin sets them to go once packaged |
| See how much room the library takes and what is free | not there | build | [`see-storage-use`](./portal.md#running-the-platform) no | — |
| A title that lacks subtitles gets them | partly | build | [`make-subtitles`](./catalog.md#preparing-titles-to-play) partial, [`attach-subtitle`](./catalog.md#preparing-titles-to-play) built, [`add-own-subtitle`](./catalog.md#the-catalog) no | — |
| Lossless sound and Dolby Vision as the original has them | decided otherwise | ruled out | [ADR-0015](../../docs/adr/0015-the-package-is-the-master.md) | The master is stereo, 5.1 where turned on, and HDR10; an instance may keep its originals |

## Share it with a household

For the goal [Share it with a household](../goals/README.md#share-it-with-a-household).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Invite people | partly | build | [`invite-person`](./portal.md#people-and-roles) partial, [`accept-invite`](./portal.md#people-and-roles) built | — |
| Rights for each person: which libraries, downloads, quality | partly | build | [`set-person-rights`](./portal.md#people-and-roles) no, [`cap-person-rating`](./portal.md#people-and-roles) partial, [`limit-to-age-cap`](./chino.md#the-title-page) built | — |
| Lock a profile on a shared TV | not there | build | [`lock-account`](./chino.md#connecting-and-signing-in) no | — |
| Reset a forgotten password by oneself | not there | build | [`reset-own-password`](./chino.md#connecting-and-signing-in) no | — |
| A second factor at sign-in | not there | build | [`use-second-factor`](./chino.md#connecting-and-signing-in) no | — |
| See one's devices and sign one out | not there | build | [`see-own-devices`](./chino.md#settings-and-account) no | — |
| Limit streams or bandwidth for a person | not there | build | [`limit-streams`](./portal.md#people-and-roles) no | — |
| See who is watching now, and what was watched over time | partly | build; later: `see-watch-statistics` | [`see-who-is-watching`](./portal.md#people-and-roles) no, [`see-watch-statistics`](./portal.md#people-and-roles) no, [`report-playback-quality`](./chino.md#the-player) partial | — |
| Sign in with an identity provider one already runs | partly | build | [`choose-identity`](./platform.md#installing-and-configuring) partial | — |
| Delete one's account and what the server keeps of it | there | — | [`delete-account`](./chino.md#settings-and-account) built | — |
| Reach people outside the app: a push, a mail | partly | build; later: `get-push-notification`, `notifications` | [`get-push-notification`](./chino.md#notifications) no, [`mail-person`](./portal.md#people-and-roles) no, [`notify-person`](./portal.md#addons) built, [`notifications`](../architecture/components.md#chinos-services) idle | — |

## Run it oneself

For the goal [Run it oneself](../goals/README.md#run-it-oneself).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Install it on one machine with one command | there | — | [`install-on-one-machine`](./platform.md#installing-and-configuring) built, [`install-platform`](./platform.md#installing-and-configuring) built | — |
| Run it on the machine a household has | partly | build | [`run-on-arm`](./platform.md#installing-and-configuring) no, [`encode-on-other-gpus`](./platform.md#installing-and-configuring) no, [`choose-encoder`](./platform.md#installing-and-configuring) partial | The documentation names no smallest machine |
| Reach it from a phone or a TV at home right after installing | partly | build | [`reach-on-home-network`](./platform.md#installing-and-configuring) no, [`set-public-host`](./platform.md#installing-and-configuring) partial, [`provide-certificates`](./platform.md#installing-and-configuring) partial | Today with a name and an https certificate of one's own |
| The apps find the server by themselves | not there | build | [`find-server-on-network`](./chino.md#connecting-and-signing-in) no | — |
| Reach it from outside the home with no network setup | not there | an addon's | [`reach-from-outside`](./platform.md#installing-and-configuring) no | — |
| Set up the first administrator in the browser | partly | build | [`create-first-admin`](./portal.md#running-the-platform) no, [`set-up-platform`](./portal.md#running-the-platform) built | — |
| Update with one click, or by itself | partly | build | [`update-platform`](./portal.md#running-the-platform) built, [`choose-update-channel`](./platform.md#installing-and-configuring) built, [`update-operator`](./portal.md#running-the-platform) no | — |
| Back up and restore everything | partly | build; later: `rebuild-catalog-from-library`, `match-catalog-to-library`; ruled out: `back-up-library` | [`schedule-backups`](./platform.md#installing-and-configuring) partial, [`restore-backup`](./platform.md#installing-and-configuring) partial, [`back-up-library`](./catalog.md#the-library-and-its-originals) no, [`rebuild-catalog-from-library`](./catalog.md#the-library-and-its-originals) no, [`match-catalog-to-library`](./catalog.md#the-library-and-its-originals) no | — |
| Move the server to another machine | not there | build | [`move-platform`](./platform.md#installing-and-configuring) no | — |
| Be told when something is wrong | partly | build | [`alert-admins`](./portal.md#running-the-platform) no, [`verify-platform`](./portal.md#running-the-platform) built, [`see-platform-parts`](./portal.md#running-the-platform) built | — |
| A first-run checklist, logs, a self-check, a support bundle | there | — | [`set-up-platform`](./portal.md#running-the-platform) built, [`read-logs`](./portal.md#running-the-platform) built, [`verify-platform`](./portal.md#running-the-platform) built, [`download-support-bundle`](./portal.md#running-the-platform) built | — |
| Bring people and their watch history from another media server | not there | an addon's | [`import-people-and-history`](./portal.md#people-and-roles) no | — |

## Make it one's own

For the goal [Make it one's own](../goals/README.md#make-it-ones-own).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Extend it with addons | there | — | [`install-addon-chart`](./portal.md#addons) built, [`add-slot-buttons`](./portal.md#addons) built, [`notify-person`](./portal.md#addons) built | — |
| Browse the addons there are | not there | later | [`browse-addons`](./portal.md#addons) no | — |
| Scripts and other tools: a token, a webhook | partly | later; an addon's: `send-webhooks` | [`sign-in-cli`](./portal.md#running-the-platform) built, [`run-declared-commands`](./portal.md#addons) built, [`use-personal-token`](./portal.md#running-the-platform) no, [`send-webhooks`](./portal.md#running-the-platform) no | — |
| Ask for a title the library lacks | there | — | [`act-on-empty-search`](./chino.md#search) built | The asking is an addon's |
| Interfaces for addons that stay as they are | not there | build | [`rely-on-addon-interfaces`](./portal.md#addons) no | — |

## Trust it

For the goal [Trust it](../goals/README.md#trust-it).

| Expected | State | Next | Met by | Note |
|---|---|---|---|---|
| Report a security hole in private | there | — | [`report-security-hole`](./platform.md#releases-one-can-trust) built | — |
| Check where an image comes from and what it holds | not there | build | [`trace-image-to-source`](./platform.md#releases-one-can-trust) no | — |
| The apps send nothing to anyone but the server | partly | build | [`call-only-the-server`](./platform.md#releases-one-can-trust) partial | — |
| Change it and have the change taken in | not there | build | [`contribute-change`](./platform.md#releases-one-can-trust) no | — |
<!-- end: expectations -->
