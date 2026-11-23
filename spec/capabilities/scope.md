# Scope

What becomes of everything zaentrum does not do yet. The
[capability model](./README.md) lists every capability and where it is built;
the [expectations](./expectations.md) list what people look for. This page
answers, for each capability that is not built, the question a builder has to
ask: is it built now, and from what; or is it left out, and why.

> **Written by hand, counted by a program.** What is left out is
> [scope.csv](./scope.csv); what is built is the numbered changes of the
> chapters. The tables on this page are computed from both. A check fails when
> a capability is not built, no numbered change names it, and no row here says
> what becomes of it: nothing is left without an answer.

## How to read it

A capability that is not built has one of these answers:

| Answer | Means |
|---|---|
| a numbered change builds it | a chapter says what is built, as a change with today and the target; the owner approves it by its number |
| to be built, the change still to write | it is meant to be built, and no chapter says how yet: the specification is not ready for it |
| left for later | not built in this round; nothing in the platform rules it out |
| left to an addon | the platform leaves it out on purpose, and an addon can add it through the platform's interfaces ([ADR-0001](../../docs/adr/0001-neutral-core-and-addon-seams.md)) |
| ruled out | the platform will not do it; a decision record says what it does instead |

A row here may stand beside a change: the change builds the capability where it
names an app or a face, and the row says what becomes of the rest, such as the
command line's part.

Every row, every target of a [quality](../goals/README.md) and every new
decision record starts as **proposed**. It counts once the owner approves it,
the same way a numbered change does.

## Is the specification ready to build from

It is ready when nothing is left to write: no capability is “to be built, the
change still to write”, and none is without an answer. What is then built is
what the owner approves: the changes by their numbers, the rows of this page,
the targets, and the decision records the changes rest on.

<!-- generated: ready -->
| Of the capabilities |  |
|---|---|
| Capabilities that are not built | 220 |
| a numbered change builds them | 181 |
| to be built, the change still to write | 0 |
| left for later | 35 |
| left to an addon | 3 |
| ruled out | 1 |
| nothing says | 0 |

| Of the changes |  |
|---|---|
| Numbered changes | 451 |
| proposed | 0 |
| approved | 438 |
| built | 12 |
| verified | 0 |
| withdrawn | 1 |

| Of the proposals |  |
|---|---|
| Rows of scope.csv | 58 |
| proposed | 0 |
| approved | 58 |
| Qualities | 21 |
| with a target | 21 |
| with an approved target | 21 |
| Decision records still proposed | [0012](../../docs/adr/0012-catalog-identity-for-addons.md), [0014](../../docs/adr/0014-subtitles-in-every-language.md) |
<!-- end: ready -->

## Changes that hold a choice

A numbered change whose target starts with “Recommended” holds a choice of the
owner's: the target says what is recommended and what the other choice is.
Approving the change takes the recommendation.

<!-- generated: choices -->
| No. | Change | Where | Status |
|---|---|---|---|
| [2.C10](../chino/frame.md#27-changes) | help in the avatar's menu | Web, Phone app | approved |
| [3.C13](../chino/start.md#37-changes) | No picture in the avatar | Web, Phone app, Android TV | approved |
| [3.C18](../chino/start.md#37-changes) | The apps in their devices' stores (needs the owner) | Phone app, Android TV, Samsung TV | approved |
| [4.C4](../chino/home.md#47-changes) | The hero's line: year, length and genre | Web, Phone app, Android TV, Samsung TV | approved |
| [4.C8](../chino/home.md#47-changes) | Phone app: play alone on the hero | Phone app | approved |
| [4.C11](../chino/home.md#47-changes) | continue watching and next up: stills with the time left | Web, Phone app, Android TV, Samsung TV | approved |
| [4.C12](../chino/home.md#47-changes) | Samsung TV: no genre rows | Samsung TV | approved |
| [4.C15](../chino/home.md#47-changes) | Web: see all as the row's last card alone | Web | approved |
| [5.C1](../chino/browse.md#59-changes) | The filter bar | Web, Phone app, Android TV, Samsung TV | approved |
| [5.C7](../chino/browse.md#59-changes) | The card: the name and the year | Web, Phone app, Android TV, Samsung TV | approved |
| [5.C15](../chino/browse.md#59-changes) | Samsung TV: no load more button | Samsung TV | approved |
| [5.C21](../chino/browse.md#59-changes) | Collections, from movies | Web, Phone app, Android TV, Samsung TV | approved |
| [6.C14](../chino/title-actions.md#69-changes) | No Analyzed fact | Web, Phone app, Samsung TV | approved |
| [6.C16](../chino/title-actions.md#69-changes) | The seasons: specials last, the first numbered season open | Web, Phone app, Android TV | approved |
| [8.C3](../chino/watchlist.md#89-changes) | see all, the row's last card | Web, Phone app, Samsung TV | approved |
| [8.C7](../chino/watchlist.md#89-changes) | The Watchlist keeps its name | Web, Android TV, Samsung TV, the server | approved |
| [9.C1](../chino/search.md#97-changes) | The results in the page, as people type | Web | approved |
| [9.C13](../chino/search.md#97-changes) | The TV's own keyboard beside the results | Android TV, Samsung TV | approved |
| [10.C12](../chino/zap.md#108-changes) | The first card at random | Web, Phone app, Android TV | approved |
| [10.C14](../chino/zap.md#108-changes) | Back from the player returns to the session | Web, Phone app, Samsung TV | approved |
| [11.C12](../chino/playback.md#1116-changes) | Samsung TV: no buttons for 10 seconds back and forward | Samsung TV | approved |
| [11.C20](../chino/playback.md#1116-changes) | Auto-skip counts down, on the episodes in a row | Web, Phone app, Android TV, Samsung TV | approved |
| [11.C27](../chino/playback.md#1116-changes) | No auto-skip of the credits | Android TV, Samsung TV | approved |
| [11.C28](../chino/playback.md#1116-changes) | Nothing starts after a movie | Android TV | approved |
| [11.C42](../chino/playback.md#1116-changes) | A title starting: the loader with its line | Web, Phone app, Android TV, Samsung TV | approved |
| [11.C45](../chino/playback.md#1116-changes) | Couldn't play: one screen, report a bug under details | Web, Phone app, Android TV, Samsung TV | approved |
| [11.C50](../chino/playback.md#1116-changes) | A 5.1 track: where it is listed and where it starts | Phone app (Android), Android TV | approved |
| [11.C53](../chino/playback.md#1116-changes) | A phone's player opens sideways | Phone app | approved |
| [11.C54](../chino/playback.md#1116-changes) | A double tap skips 10 seconds | Web, Phone app | approved |
| [12.C5](../chino/subtitles.md#1212-changes) | iOS: a subtitle it can't draw is left out | Phone app (iOS) | approved |
| [14.C8](../chino/casting.md#147-changes) | The cast button in the iOS app | Phone app (iOS) | approved |
| [14.C9](../chino/casting.md#147-changes) | The cast button on the web | Web, Server | approved |
| [15.C4](../chino/notifications.md#157-changes) | One place per notification | Phone app | approved |
| [16.C9](../chino/settings.md#167-changes) | Web: no reset to defaults | Web | approved |
| [16.C17](../chino/settings.md#167-changes) | delete account only where the server deletes accounts | Web, Phone app, Android TV, Samsung TV, the server | approved |
| [16.C18](../chino/settings.md#167-changes) | The settings' first values | Web, Phone app, Android TV, Samsung TV, the server | approved |
| [17.C2](../chino/errors.md#1715-changes) | The Samsung TV's requests give up | Samsung TV | approved |
| [17.C15](../chino/errors.md#1715-changes) | The web's not-accepted sentence | Web | approved |
| [H.C4](../portal/home.md#changes) | settings in the server's answer | Server, Web | approved |
| [H.C6](../portal/home.md#changes) | settings in three groups | Server, Web | approved |
| [H.C8](../portal/home.md#changes) | catalog admin, a name that fits | Server; catalog management's own heading | approved |
| [H.C9](../portal/home.md#changes) | No badge or square the portal doesn't check | Server, Web | approved |
| [H.C13](../portal/home.md#changes) | An addon joins a space | Server | approved |
| [H.C17](../portal/home.md#changes) | An addon's setup in the settings space | Server, Web | approved |
| [I.C19](../platform/install.md#changes) | A release waits for its operator | Operator, Server, Portal | approved |
| [I.C21](../platform/install.md#changes) | The setting identity.loginTheme goes | Operator, Docs | approved |
| [K.C2](../catalog/console.md#changes) | Two apps, each with its views | Catalog console | approved |
| [K.C18](../catalog/console.md#changes) | extras | Catalog console | approved |
| [K.C24](../catalog/console.md#changes) | settings: one form | Catalog console, Docs | approved |
| [L.C5](../catalog/library.md#changes) | Folders of a library | Server | approved |
| [L.C7](../catalog/library.md#changes) | Scans on a schedule | Server | approved |
| [L.C9](../catalog/library.md#changes) | Details read from the files beside a title | Server | approved |
| [L.C17](../catalog/library.md#changes) | A title as one file | Server | approved |
| [N.C10](../platform/home.md#changes) | The Samsung TV app keeps plain http to home addresses | Samsung TV | approved |
| [N.C12](../platform/home.md#changes) | The one-machine install announces itself | Images | approved |
| [P.C12](../portal/people.md#changes) | A stream needs a session | Server | approved |
| [R.C12](../portal/operations.md#changes) | A backup before an update | Operator | built |
| [R.C13](../portal/operations.md#changes) | A restore brings the identity provider in step | Operator | approved |
| [T.C6](../platform/trust.md#changes) | The addon interfaces, each with a version | Docs | approved |
<!-- end: choices -->

## To be built, the change still to write

<!-- generated: build -->
None.
<!-- end: build -->

## Left for later

<!-- generated: later -->
| What | Key | Area | Why | Status |
|---|---|---|---|---|
| Show new and changed titles without a reload | `refresh-on-library-change` | [Home](./chino.md#home) | the web follows the catalog's changes as they happen; a phone or a TV asks again when a screen opens, which is enough there | approved |
| Choose which cut of a title plays: theatrical, director's, extended | `choose-cut` | [The title page](./chino.md#the-title-page) | a library seldom holds two cuts of one film, and it needs the library to keep several versions playable side by side | approved |
| Watch a title together from different places, in step | `watch-together` | [The player](./chino.md#the-player) | a feature with a design of its own; nothing else waits for it | approved |
| Show broadcast subtitles made as pictures (DVB) on the picture | `show-dvb-subtitles` | [Subtitles](./chino.md#subtitles) | they come with recordings of broadcasts, so they wait for live channels | approved |
| Start chino on a TV on the same network from a phone, playing as the person who sent it (what 14.C5, 14.C6, 14.C7, 14.C8, 14.C9 leave open) | `find-tv-app` | [Casting](./chino.md#casting) | Samsung TVs: their own way to start an app from a phone has to be tried on a real TV before anything is promised | approved |
| Be told on the phone while the app is closed | `get-push-notification` | [Notifications](./chino.md#notifications) | a push to a phone needs keys of the app's publisher, which an open server can't carry: it needs a relay somebody runs, and a decision record of its own | approved |
| Register an app, change it, switch it off, or delete it with its tiles | `register-app` | [Apps, spaces, tiles and extensions](./portal.md#apps-spaces-tiles-and-extensions) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Add, rename, reorder or delete a space of the home page (what H.C4, H.C12 leave open) | `arrange-spaces` | [Apps, spaces, tiles and extensions](./portal.md#apps-spaces-tiles-and-extensions) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Place a tile for an app in a space, with its words, icon, order and how it opens (what H.C7, H.C9, H.C10 leave open) | `place-tiles` | [Apps, spaces, tiles and extensions](./portal.md#apps-spaces-tiles-and-extensions) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Show a space or a tile only to the people who hold given roles | `limit-tile-audience` | [Apps, spaces, tiles and extensions](./portal.md#apps-spaces-tiles-and-extensions) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Edit the buttons addons add to the apps' screens, or add one by hand | `edit-slot-rows` | [Apps, spaces, tiles and extensions](./portal.md#apps-spaces-tiles-and-extensions) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| See an addon's setup checklist and open where each section is configured (what H.C17 leave open) | `check-addon-setup` | [Addons](./portal.md#addons) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Count each addon's notifications, read and unread, never what they say | `count-addon-notifications` | [Addons](./portal.md#addons) | the count is served; no screen needs it until addons send more than a few notifications | approved |
| Look through the addons there are, and install one from the list | `browse-addons` | [Addons](./portal.md#addons) | there are too few addons for a list; one is added by its address or its chart's | approved |
| See everyone who may use the platform, with role, rating cap, status and invite (what P.C3 leave open) | `see-people` | [People and roles](./portal.md#people-and-roles) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Add an account for a person, as a user or as an admin (what P.C3, R.C4 leave open) | `add-person` | [People and roles](./portal.md#people-and-roles) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Give a person an invite link to choose their own password (what P.C3, P.C14, R.C4 leave open) | `invite-person` | [People and roles](./portal.md#people-and-roles) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Change a person's name or role, or switch their account off and on (what P.C2, P.C3, P.C14 leave open) | `change-person` | [People and roles](./portal.md#people-and-roles) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Keep titles rated above an age from a person, on every app (what P.C3, P.C4, P.C16, 3.C16, 3.C17 leave open) | `cap-person-rating` | [People and roles](./portal.md#people-and-roles) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| Delete a person's account, with their data in the apps | `delete-person` | [People and roles](./portal.md#people-and-roles) | the portal has it; the CLI gets it once a script can sign in with a token of its own | approved |
| See what was watched over time: by title, by person, by device | `see-watch-statistics` | [People and roles](./portal.md#people-and-roles) | the apps send how playback went and the server counts it; a page over time comes after the page of who is watching now | approved |
| Watch the event bus: its topics, their consumers and the latest events | `watch-events` | [Running the platform](./portal.md#running-the-platform) | the portal shows the bus; the CLI lists its events, and a live tail there can wait | approved |
| Browse chosen tables of the platform's databases, read-only, secrets masked | `browse-database` | [Running the platform](./portal.md#running-the-platform) | a look into the tables is the portal's; a script reads the APIs | approved |
| Call the platform's APIs from a script with a token of one's own | `use-personal-token` | [Running the platform](./portal.md#running-the-platform) | needs a way to issue and check tokens that every service accepts: a decision record of its own; until then the CLI signs in with a code in a browser | approved |
| Fill titles' details without a key of the admin's own | `enrich-without-own-key` | [The catalog](./catalog.md#the-catalog) | needs a key of the project's in the images, or sources that ask for none: a decision record of its own; until then the first-run checklist asks for a key | approved |
| Retire the originals of chosen titles: a dry run first, then a run of what it found | `retire-list` | [The library and its originals](./catalog.md#the-library-and-its-originals) | whoever runs the platform retires chosen originals through the API; a screen for it comes after the files tab shows what happened to an original | approved |
| Decide whether an original another file replaced may go when it gives up more | `decide-superseded` | [The library and its originals](./catalog.md#the-library-and-its-originals) | whoever runs the platform retires chosen originals through the API; a screen for it comes after the files tab shows what happened to an original | approved |
| Encode queued titles again at a set pace and in set hours | `reencode-queue` | [The library and its originals](./catalog.md#the-library-and-its-originals) | the rules view shows the queue's counts and pace; clearing it stays with the API | approved |
| Keep a title that gets no package playable from its original in the library | `take-in-title` | [The library and its originals](./catalog.md#the-library-and-its-originals) | the platform's own work; the console needs no screen for it beyond what a title's files tab shows | approved |
| Fill in what the catalog records of titles' originals: probe, size and tracks | `backfill-source-facts` | [The library and its originals](./catalog.md#the-library-and-its-originals) | a repair run once through the API; it needs no screen | approved |
| Rebuild the catalog from the library's files after the database is lost | `rebuild-catalog-from-library` | [The library and its originals](./catalog.md#the-library-and-its-originals) | the records the files carry leave out the age rating and what a hand locked; a rebuild from them comes once they are complete | approved |
| Find titles whose files and catalog disagree after a restore, and put them in step | `match-catalog-to-library` | [The library and its originals](./catalog.md#the-library-and-its-originals) | it follows the rebuild of the catalog from the library's files | approved |
| Read a title's chapters from its original, and of titles that miss them at a set pace | `read-chapters` | [Preparing titles to play](./catalog.md#preparing-titles-to-play) | the chapters tab lists a title's chapters; how far the reading is, and settling a title that can't be read, stay with the API | approved |
| Settle titles whose chapters can't be read, or put back chapters a read replaced | `settle-chapter-reads` | [Preparing titles to play](./catalog.md#preparing-titles-to-play) | the chapters tab lists a title's chapters; how far the reading is, and settling a title that can't be read, stay with the API | approved |
| Measure the picture inside a title's frame, and of titles that lack it at a set pace | `measure-picture-area` | [Preparing titles to play](./catalog.md#preparing-titles-to-play) | the platform's own work; the console needs no screen for it beyond what a title's files tab shows | approved |
| Read whether a title's original carries closed captions, at a set pace | `read-closed-captions` | [Preparing titles to play](./catalog.md#preparing-titles-to-play) | the platform's own work; how far the reading is stays with the API, and the console needs no screen for it | approved |
| Encode and package a title's extras on a chain of their own | `package-extras` | [Preparing titles to play](./catalog.md#preparing-titles-to-play) | the platform's own work; the console needs no screen for it beyond what a title's files tab shows | approved |
| Pin the platform to a version, or follow its channel again | `pin-version` | [Installing and configuring](./platform.md#installing-and-configuring) | the CLI and the resource pin any version; the portal offers the update at hand, which is what an admin needs there | approved |
| Publish the bundled identity provider's admin console on the public host | `expose-identity-console` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Serve the platform at its public host, through an Ingress or Routes (what N.C1, N.C11 leave open) | `set-public-host` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Give the library, the database and the event broker their volumes | `configure-storage` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Use the bundled event broker or an external one shared with others | `configure-event-streaming` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Run the live worker for the encodes made while a title plays (what I.C4, I.C6 leave open) | `enable-live-worker` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Give addons a VPN their pods reach the internet through | `connect-vpn` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Provide the platform's secrets yourself instead of generated ones | `bring-own-secrets` | [Installing and configuring](./platform.md#installing-and-configuring) | a choice of whoever installs the platform, made in its resource | approved |
| Watch live channels (what H.C9, H.C10 leave open) | `watch-live-channels` | [Live channels](./platform.md#live-channels) | live channels are a product of their own, designed once watching is complete; the changes named only tidy its tile on the home page | approved |
| Listen to music (what H.C9, H.C10 leave open) | `play-music` | [Music, audiobooks and podcasts](./platform.md#music-audiobooks-and-podcasts) | the listening product is designed once watching is complete; the changes named only tidy its tile on the home page | approved |
| Listen to audiobooks and podcasts | `listen-to-audiobooks` | [Music, audiobooks and podcasts](./platform.md#music-audiobooks-and-podcasts) | with the listening product, which is designed once watching is complete | approved |
| The component an app for Apple TV | `chino-tvos` | [components](../architecture/components.md) | an app for a further TV system is a product of its own; Android TV and Samsung TVs come first | approved |
| The component an app for LG TVs | `chino-webos` | [components](../architecture/components.md) | an app for a further TV system is a product of its own; Android TV and Samsung TVs come first | approved |
| The component an app for Roku players | `chino-roku` | [components](../architecture/components.md) | an app for a further TV system is a product of its own; Android TV and Samsung TVs come first | approved |
| The component push to the apps | `notifications` | [components](../architecture/components.md) | the push service waits for the decision on how a push reaches a phone | approved |
<!-- end: later -->

## Left to an addon

<!-- generated: addon -->
| What | Key | Area | Why | Status |
|---|---|---|---|---|
| Bring people, their watch history and their lists from another media server | `import-people-and-history` | [People and roles](./portal.md#people-and-roles) | an importer reads the other server and writes through the platform's interfaces: the platform stays free of other products' formats | approved |
| Tell another service when something happens: a title added, a title played | `send-webhooks` | [Running the platform](./portal.md#running-the-platform) | events are on the bus for addons; one that calls addresses outside the platform is an addon | approved |
| Reach it from outside the home with no router or DNS setup | `reach-from-outside` | [Installing and configuring](./platform.md#installing-and-configuring) | reaching it from outside without a name of one's own needs a tunnel or a relay somebody runs; an addon brings one, the platform runs no service of its own | approved |
<!-- end: addon -->

## Ruled out

<!-- generated: out -->
| What | Key | Area | Why | Status |
|---|---|---|---|---|
| Find the servers on the home network without typing an address (what N.C12, 3.C14, 3.C15 leave open) | `find-server-on-network` | [Connecting and signing in](./chino.md#connecting-and-signing-in) | the Samsung TV: a web app there can't look for services on the network; it keeps the typed address and the recent ones | approved |
| Update the operator itself, and the one-container install, from the portal or the CLI (what I.C15, I.C16, I.C17, I.C18, I.C19 leave open) | `update-operator` | [Running the platform](./portal.md#running-the-platform) | in a cluster a cluster admin updates the operator, with the release's manifest: the portal and the CLI hold no rights over the cluster | approved |
| Back up the library's files along with the databases | `back-up-library` | [The library and its originals](./catalog.md#the-library-and-its-originals) | the library's files are large and on storage with tools of its own; the platform backs up what only it can restore, and the documentation says what to copy | approved |
<!-- end: out -->
