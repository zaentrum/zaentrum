# chino

The capabilities of the apps for watching, one area a chapter of the
[chino specification](../chino/README.md). The columns are explained in
[how to read it](./README.md#how-to-read-it); every row comes from
[capabilities.csv](./capabilities.csv).

<!-- generated: areas -->
## Connecting and signing in

Reaching a server, signing in on each kind of device, keeping several accounts on one. Specified in [chapter 3](../chino/start.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Portal | Spec |
|---|---|---|---|---|---|---|---|
| Connect to a server by its address | person | — | built | built | built | — | [3.3](../chino/start.md#33-connect-to-a-server) |
| Connect again to a server used before, from a list of recent ones | person | — | built | built | no | — | [3.3.1](../chino/start.md#331-on-a-phone-held-upright) |
| Sign in on the server's own sign-in page | person | built | built | — | — | — | [3.4.1](../chino/start.md#341-on-a-phone-held-upright), [3.4.4](../chino/start.md#344-on-the-web) |
| Sign in on a TV with a code entered on a phone or a computer | person | — | — | built | partial | — | [3.4.3](../chino/start.md#343-on-a-tv) |
| Stay signed in while the sign-in renews itself | system | built | built | built | partial | — | [3.4.4](../chino/start.md#344-on-the-web), [17.11](../chino/errors.md#1711-a-sign-in-that-expired) |
| Come back to the page a link named, once signed in | person | partial | — | — | — | — | [3.4.4](../chino/start.md#344-on-the-web) |
| Choose who's watching as the app starts on a shared device | person | — | built | built | no | — | [3.5](../chino/start.md#35-whos-watching) |
| Switch to another account on this device | person | — | built | built | partial | — | [3.5](../chino/start.md#35-whos-watching), [16.5](../chino/settings.md#165-the-account) |
| Add another account to this device | person | — | built | built | no | — | [3.5](../chino/start.md#35-whos-watching) |
| Remove an account from this device | person | — | built | built | no | — | [3.5](../chino/start.md#35-whos-watching), [16.5.5](../chino/settings.md#1655-sign-out-remove-account-and-change-server) |
| Sign out of this server | person | built | built | no | built | — | [16.5.5](../chino/settings.md#1655-sign-out-remove-account-and-change-server), [2.3](../chino/frame.md#23-the-frame-on-a-computer) |
| Change to another server | person | — | built | built | partial | — | [3.3.1](../chino/start.md#331-on-a-phone-held-upright), [16.4.4](../chino/settings.md#1644-server), [16.5.5](../chino/settings.md#1655-sign-out-remove-account-and-change-server) |
| Add the web app to a phone's home screen | person | built | — | — | — | — | — |
| Find the servers on the home network without typing an address | person | — | no | no | no | — | — |
| Get the app from the device's own store | person | — | no | no | no | — | [Publishing the apps](../../docs/releases.md#publishing-the-apps) |
| Reset a forgotten password by oneself | person | no | no | — | — | no | [First run](../../docs/self-hosting.md#first-run) |
| Sign in with a second factor | person | no | no | — | — | no | [First run](../../docs/self-hosting.md#first-run) |
| Lock an account on a shared device behind a code | person | — | no | no | no | — | — |

- Connect to a server by its address: checks it is chino and its sign-in answers, on a TV also sign-in by code; the web comes from its own server
- Connect again to a server used before, from a list of recent ones: up to five, newest first; Samsung keeps no list, so it never shows
- Sign in on the server's own sign-in page: the web in its tab, the phone in the browser; a failure says why by kind on the web, in the sign-in service's words on the phone
- Sign in on a TV with a code entered on a phone or a computer: Samsung shows no picture code to scan; neither TV offers change server there
- Stay signed in while the sign-in renews itself: Samsung renews ahead but not when a request is refused, and shows “chino-api 401”
- Come back to the page a link named, once signed in: the first sign-in opens home, a title's link too; only a sign-in refused later returns to its page
- Choose who's watching as the app starts on a shared device: with two accounts or more; Samsung opens the active one's home, its who's watching in the code but never opened
- Switch to another account on this device: from settings to who's watching, on Android TV from the avatar too; Samsung: a list over settings, its add account adds none
- Add another account to this device: the phone in the browser, Android TV with a code; Samsung's add account goes to home without signing in
- Remove an account from this device: phone: the ✕, Android TV: holding OK, both asking first; Samsung can only sign the active account out
- Sign out of this server: web at the sign-in service too; the phone asks where downloads go or a cast stops; Samsung asks nothing; Android TV has none
- Change to another server: signs every account out; the phone asks first where downloads go; Samsung signs out before an address is typed, without cancel
- Add the web app to a phone's home screen: a hint where the browser offers no install of its own; once closed it stays away
- Find the servers on the home network without typing an address: every app asks for an address; nothing announces a server on the network
- Get the app from the device's own store: no app is in a public store yet; each is built from its repository
- Reset a forgotten password by oneself: the sign-in page offers it; the bundled identity provider has no mail server to send the link with
- Sign in with a second factor: left to the identity provider's console; no app or console of the platform offers it
- Lock an account on a shared device behind a code: switching accounts asks for nothing, so a rating cap ends at the account chooser

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `connect-server` | 3.C1, 3.C2, 3.C3, 3.C4 | `chino-api GET /api/config` | `server-check-timeout` |
| `reconnect-recent-server` | 3.C5 | — | — |
| `sign-in` | 3.C6, 3.C8 | `chino-api GET /api/config` | `server-check-timeout` |
| `sign-in-with-code` | 3.C7, 3.C8 | `chino-api GET /api/config` | `server-check-timeout` |
| `stay-signed-in` | 17.C11 | — | — |
| `return-after-sign-in` | 3.C9 | — | — |
| `choose-account-at-start` | 3.C4, 3.C10, 3.C11 | — | — |
| `switch-account` | 3.C11, 16.C12, 16.C13 | — | — |
| `add-account` | 3.C10, 3.C11 | — | — |
| `remove-account` | 3.C10, 16.C14 | — | — |
| `sign-out` | 2.C1, 16.C12, 16.C13, 16.C14 | — | — |
| `change-server` | 16.C6, 16.C14 | `chino-api GET /api/config` | — |
| `install-web-app` | — | — | — |
| `find-server-on-network` | — | — | — |
| `get-app-from-store` | — | — | — |
| `reset-own-password` | — | — | — |
| `use-second-factor` | — | — | — |
| `lock-account` | — | — | — |

## The frame

What is around every screen: the rail or tab bar, the top bar, going back. Specified in [chapter 2](../chino/frame.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Move between home, movies, shows, watchlist, zap and settings | person | built | built | built | built | [2.3](../chino/frame.md#23-the-frame-on-a-computer), [2.4](../chino/frame.md#24-the-frame-on-a-phone), [2.5](../chino/frame.md#25-the-frame-on-a-tv) |
| Open a view, a title or a list again from a link, a reload or the browser's back | person | partial | — | — | — | [2.3](../chino/frame.md#23-the-frame-on-a-computer), [5.7.3](../chino/browse.md#573-where-the-view-starts), [8.6](../chino/watchlist.md#86-a-list) |
| Go back to the screen before, as it was left | person | partial | built | built | partial | [2.1](../chino/frame.md#21-purpose), [4.5](../chino/home.md#45-home-on-a-tv), [5.7.3](../chino/browse.md#573-where-the-view-starts), [6.3.5](../chino/title-actions.md#635-on-a-tv) |
| See which account is signed in | person | built | built | built | built | [2.3](../chino/frame.md#23-the-frame-on-a-computer), [3.5.4](../chino/start.md#354-the-avatar), [16.5](../chino/settings.md#165-the-account) |
| Keep what matters inside a TV's safe area | system | — | — | partial | no | [2.5](../chino/frame.md#25-the-frame-on-a-tv) |
| Get the web app's new version with one reload | person | built | — | — | — | [17.7](../chino/errors.md#177-the-causes) |
| Use every screen with a screen reader | person | ? | ? | ? | ? | — |

- Move between home, movies, shows, watchlist, zap and settings: web: a rail, tabs below 768 px; phone: tabs, a rail from 600 dp, downloads on Android; TVs: a rail of icons that never opens
- Open a view, a title or a list again from a link, a reload or the browser's back: titles, people, the watchlist, search and the account have addresses; movies, shows, zap, settings and an opened list don't
- Go back to the screen before, as it was left: web: back from a title's page lands on home, not on movies, shows or a list; Samsung: home, the views and title pages load anew
- See which account is signed in: initials in the avatar, name and email on the account page; phone and Android TV fetch a picture from an outside service
- Keep what matters inside a TV's safe area: Android TV keeps it in the player and zap only; the frame starts at the screen's edge
- Get the web app's new version with one reload: a toast offers reload once a new version is waiting
- Use every screen with a screen reader: not checked on any app; search is known not to say its result count

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `switch-view` | 2.C2, 2.C3, 2.C4, 2.C5, 2.C7, 4.C16, 6.C1, 7.C1 | — | — |
| `open-view-by-address` | 2.C6, 5.C12, 8.C14 | — | — |
| `go-back` | 4.C18, 5.C12, 6.C23, 8.C14 | — | — |
| `see-who-is-signed-in` | 2.C1, 2.C9, 3.C12, 3.C13, 16.C12 | `chino-api GET /api/v1/me` | — |
| `keep-tv-safe-area` | 2.C8 | — | — |
| `reload-new-web-version` | 17.C15 | — | — |
| `use-with-screen-reader` | — | — | — |

## Home

The first screen: the hero and the rows. Specified in [chapter 4](../chino/home.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Start a featured title, or open it, from the hero | person | built | partial | built | built | [4.3](../chino/home.md#43-home-on-a-computer), [4.6.1](../chino/home.md#461-the-hero) |
| Watch the featured title's trailer from the hero | person | built | built | no | no | [4.3](../chino/home.md#43-home-on-a-computer) |
| Pick up the titles one is in the middle of | person | built | built | built | built | [4.6.2](../chino/home.md#462-the-rows), [11.7](../chino/playback.md#117-play-resume-and-a-finished-title) |
| Take a title off continue watching without changing what was watched | person | built | built | built | no | [4.6.2](../chino/home.md#462-the-rows), [11.7](../chino/playback.md#117-play-resume-and-a-finished-title) |
| See the next episode of each show whose last episode was finished | person | built | built | built | built | [4.6.2](../chino/home.md#462-the-rows) |
| See the movies and shows added last that are not watched yet | person | built | built | built | built | [4.6.2](../chino/home.md#462-the-rows) |
| See the highest rated movies that are not watched yet | person | built | built | built | built | [4.6.2](../chino/home.md#462-the-rows) |
| See rows of a genre's titles on home | person | no | no | no | built | [4.2.4](../chino/home.md#424-samsung-tv) |
| Open a row's titles in full, from see all | person | built | built | built | no | [4.6.2](../chino/home.md#462-the-rows), [5.7.3](../chino/browse.md#573-where-the-view-starts) |
| See how much is left of a title or an episode begun | person | partial | partial | partial | no | [4.6.2](../chino/home.md#462-the-rows), [6.7.2](../chino/title-actions.md#672-the-episode-row) |
| Show new and changed titles without a reload | system | built | no | no | no | — |

- Start a featured title, or open it, from the hero: web and phone pick titles with a trailer, the TVs movies rated 7 or more; the phone has no hero when no title has a trailer
- Watch the featured title's trailer from the hero: one the server holds plays in the player; one only online opens outside the app
- Pick up the titles one is in the middle of: titles past 30 s and not finished, the last watched first; a finished movie leaves, an episode makes way for the next
- Take a title off continue watching without changing what was watched: in the card's menu; the title stays unwatched; Samsung's cards have no menu
- See the next episode of each show whose last episode was finished: the server puts the next episode in once one is finished
- See the movies and shows added last that are not watched yet: two rows, recently added movies and shows, newest first
- See the highest rated movies that are not watched yet: rated 8 or more, the highest first
- See rows of a genre's titles on home: up to three, after top rated; recommended to go
- Open a row's titles in full, from see all: the last three rows; it opens movies or shows by title, not in the row's order
- See how much is left of a title or an episode begun: only an episode row says it, “Resume · 30m left”, no card does; Samsung's rows show neither the bar nor the time
- Show new and changed titles without a reload: the web follows the catalog's changes as they happen; the apps ask again only when a screen loads

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `start-featured-title` | 4.C1, 4.C2, 4.C3, 4.C4, 4.C5, 4.C6, 4.C7, 4.C8, 4.C9, 4.C17 | `chino-api GET /api/v1/items`, `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/items/{id}/backdrop` and 2 more | `hero-pool-size`, `hero-candidates`, `hero-rotation`, `hero-refresh` |
| `play-hero-trailer` | 4.C6, 4.C7 | `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/items/{id}/extras/*` | `hero-trailer-autoplay` |
| `continue-watching` | 4.C10, 4.C11 | `chino-api GET /api/v1/me/continue-watching` | `resume-floor`, `watched-rule` |
| `remove-from-continue-watching` | 4.C13 | `chino-api POST /api/v1/items/{id}/progress` | — |
| `see-next-up` | 4.C10, 4.C11 | `chino-api GET /api/v1/me/continue-watching` | — |
| `see-new-titles` | 4.C10, 4.C19, 4.C20, 4.C21, 4.C22 | `chino-api GET /api/v1/items`, `katalog-api GET /movies`, `katalog-api GET /series` | `home-row-size` |
| `see-top-rated` | 4.C10 | `chino-api GET /api/v1/items`, `katalog-api GET /movies` | `home-row-size`, `top-rated-floor` |
| `see-genre-rows` | 4.C12 | `chino-api GET /api/v1/items` | `genre-rows` |
| `open-row-in-full` | 4.C13, 4.C14, 4.C15 | — | — |
| `see-time-left` | 4.C11, 6.C18 | `chino-api GET /api/v1/items/{id}/progress`, `chino-api GET /api/v1/me/continue-watching` | `resume-floor` |
| `refresh-on-library-change` | — | `chino-api GET /api/v1/events` | — |

## Movies and shows

Every movie and every show, filtered and sorted. Specified in [chapter 5](../chino/browse.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Look through every movie, or every show | person | built | built | built | built | [chapter 5](../chino/browse.md) |
| Narrow movies or shows to a genre | person | built | built | built | built | [5.7.1](../chino/browse.md#571-the-filters) |
| Narrow movies or shows to a decade | person | built | built | built | no | [5.7.1](../chino/browse.md#571-the-filters) |
| Narrow movies or shows to a rating and above | person | built | built | built | no | [5.7.1](../chino/browse.md#571-the-filters) |
| Put movies or shows in order: title, newest added, rating or year | person | built | built | built | partial | [5.7.2](../chino/browse.md#572-the-sort) |
| Clear every filter at once | person | built | built | built | no | [5.7.1](../chino/browse.md#571-the-filters) |
| Narrow movies or shows by a name typed in the view | person | no | no | — | — | [5.7.1](../chino/browse.md#571-the-filters) |
| See how many titles the view holds, and how many fit the filters | person | partial | partial | partial | partial | [5.8](../chino/browse.md#58-the-grid) |
| Find movies or shows as they were left: filters, sort and place | person | no | built | partial | partial | [5.7.3](../chino/browse.md#573-where-the-view-starts) |
| Play or resume a title from its card, without opening its page | person | partial | partial | partial | no | [5.8](../chino/browse.md#58-the-grid), [6.5.4](../chino/title-actions.md#654-nothing-on-artwork) |
| See the collections everyone shares: a film series, a theme | person | no | no | no | no | — |

- Look through every movie, or every show: more load as the end nears; Samsung loads 60 at a time with a load more button, and names shows “Series”
- Narrow movies or shows to a genre: one genre at a time, from one list for both kinds, so some lead to nothing; the target ticks several
- Narrow movies or shows to a decade: “Older” is 1900 to 1979; no choice for all, a second press takes a decade off
- Narrow movies or shows to a rating and above: 8.0+, 7.0+, 6.0+; the target drops it for the sort by rating
- Put movies or shows in order: title, newest added, rating or year: Samsung: by rating first, newest and A–Z, no year
- Clear every filter at once: today it sets the sort back too; the target leaves the sort
- Narrow movies or shows by a name typed in the view: the target's filter bar search; on a TV the rail's search finds names
- See how many titles the view holds, and how many fit the filters: a total under the grid once all of it is in, “26 movies in all.”; nothing counts what the filters keep
- Find movies or shows as they were left: filters, sort and place: web starts over on leaving; Android TV keeps them for a title's page only; Samsung only between movies and shows
- Play or resume a title from its card, without opening its page: the card's menu; a grid's plays, never resumes; Android TV only a movie's; list cards in the apps and Samsung's have none
- See the collections everyone shares: a film series, a theme: lists are each person's own; the catalog keeps no collection

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `browse-library` | 5.C6, 5.C7, 5.C10, 5.C11, 5.C14, 5.C15, 5.C16, 5.C17, 5.C18, 5.C19 | `chino-api GET /api/v1/items`, `chino-api GET /api/v1/items/{id}/poster`, `katalog-api GET /movies` and 1 more | `browse-page-size` |
| `filter-by-genre` | 5.C1, 5.C3 | `chino-api GET /api/v1/genres`, `katalog-api GET /genres`, `chino-api GET /api/v1/items` | — |
| `filter-by-decade` | 5.C1, 5.C2, 5.C5 | `chino-api GET /api/v1/items` | — |
| `filter-by-rating` | 5.C1 | `chino-api GET /api/v1/items` | — |
| `sort-titles` | 5.C1, 5.C5 | `chino-api GET /api/v1/items` | — |
| `clear-filters` | 5.C4, 5.C5, 5.C16 | — | — |
| `search-in-view` | 5.C1 | — | — |
| `see-filter-count` | 5.C20 | — | — |
| `keep-view-state` | 5.C12, 5.C13 | — | — |
| `play-from-card` | 4.C13, 5.C9, 8.C13 | — | — |
| `see-collections` | — | — | — |

## The title page

A movie's or a show's page: what it is, its seasons and episodes, its extras, what can be done with it. Specified in [chapter 6](../chino/title-actions.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| See what a title is: its picture, facts, genres and description | person | built | built | built | built | [6.3](../chino/title-actions.md#63-a-movies-page), [6.8.1](../chino/title-actions.md#681-the-facts) |
| See a title's age rating | person | built | no | no | no | [6.8.1](../chino/title-actions.md#681-the-facts) |
| Play a show from the episode it has come to | person | built | built | built | built | [6.6](../chino/title-actions.md#66-play-on-a-show) |
| Watch a title's trailer | person | built | built | built | built | [6.5.1](../chino/title-actions.md#651-the-row), [11.7](../chino/playback.md#117-play-resume-and-a-finished-title) |
| Go through a show's seasons and play an episode | person | partial | built | built | partial | [6.4](../chino/title-actions.md#64-a-shows-page), [6.7](../chino/title-actions.md#67-seasons-and-episodes) |
| Open an episode on its show's page, at its row | person | built | built | built | no | [6.7.4](../chino/title-actions.md#674-opened-on-an-episode) |
| See which parts of a title the server found: intro, credits, recap | person | built | built | no | built | [6.2.5](../chino/title-actions.md#625-feature-by-feature) |
| See titles like this one | person | built | built | built | built | [6.8.3](../chino/title-actions.md#683-more-like-this) |
| Like a title | person | built | built | built | no | [6.5.3](../chino/title-actions.md#653-on-and-off) |
| Show a viewer capped at an age rating only the titles the cap allows | system | built | built | built | built | — |
| Choose which cut of a title plays: theatrical, director's, extended | person | no | no | no | no | [versions](../../docs/library/versions.md) |

- See what a title is: its picture, facts, genres and description: with its tagline and subtitle languages; Android TV cuts the description at four lines
- See a title's age rating: a badge in the board's words, “FSK 12”, “PG-13”, “16+”
- Play a show from the episode it has come to: the first button names it, “resume S01E03”, “play S01E02”; Android TV asks the server for the next episode
- Watch a title's trailer: one the server holds plays in the player and keeps no place; one only online opens outside the app
- Go through a show's seasons and play an episode: web hides the specials while there are numbered seasons; Samsung lists a file of several episodes as a row for each
- Open an episode on its show's page, at its row: from continue watching, next up or a notification; Samsung opens a page of the episode alone, without seasons
- See which parts of a title the server found: intro, credits, recap: “Analyzed” on the title page; recommended to go, as the player shows the parts on its seek bar
- See titles like this one: titles that share genres and people, as the server ranks them
- Like a title: the heart on the title page; the server keeps it, no screen lists what was liked
- Show a viewer capped at an age rating only the titles the cap allows: the server holds every route to the cap; a title past it answers as one not there, and lists leave it out
- Choose which cut of a title plays: theatrical, director's, extended: the library format records a version's cut; the apps play the current version

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `see-title-details` | 6.C1, 6.C2, 6.C3, 6.C4, 6.C5, 6.C6, 6.C11, 6.C12, 6.C24 | `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/items/{id}/poster`, `chino-api GET /api/v1/items/{id}/backdrop` and 1 more | — |
| `see-age-rating` | 6.C6 | `chino-api GET /api/v1/items/{id}`, `katalog-api GET /items/{id}` | — |
| `play-show-episode` | 6.C9, 6.C21 | `chino-api GET /api/v1/me/continue-watching`, `chino-api GET /api/v1/series/{id}/next-episode`, `chino-api GET /api/v1/series/{id}/episodes` | — |
| `play-trailer` | 6.C7, 6.C9 | `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/items/{id}/extras/*`, `katalog-api GET /api/v1/extras/{extraId}/playback` and 9 more | — |
| `browse-episodes` | 6.C15, 6.C16, 6.C18, 6.C19, 6.C20, 6.C25 | `chino-api GET /api/v1/series/{id}/episodes`, `katalog-api GET /series/{id}/episodes` | — |
| `open-episode-in-show` | 6.C21, 6.C22, 8.C12 | `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/series/{id}/episodes` | — |
| `see-analyzed-parts` | 6.C14 | `chino-api GET /api/v1/items/{id}`, `katalog-api GET /items/{id}` | — |
| `see-similar-titles` | 6.C17 | `chino-api GET /api/v1/items/{id}/similar`, `katalog-api GET /items/{id}/similar` | `similar-size` |
| `like-title` | 6.C9 | `chino-api PUT /api/v1/me/likes/{id}`, `chino-api DELETE /api/v1/me/likes/{id}`, `chino-api GET /api/v1/me/likes` | — |
| `limit-to-age-cap` | 6.C24, 7.C10 | `katalog-api GET /api/v1/visible` | `unrated-for-capped` |
| `choose-cut` | — | — | — |

## People

Cast and crew: a person's page and what they were in. Specified in [chapter 7](../chino/person.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| See who someone is and what of theirs the library holds | person | built | built | built | built | [chapter 7](../chino/person.md) |
| See who is in a title and who made it, and open their pages | person | built | built | partial | partial | [6.8.2](../chino/title-actions.md#682-the-people) |

- See who someone is and what of theirs the library holds: photo or initials, known for, born, the biography in full, and their titles with their roles
- See who is in a title and who made it, and open their pages: on a title's page; the TVs show every actor as a card of initials, never a photo

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `see-person` | 7.C1, 7.C2, 7.C3, 7.C4, 7.C5, 7.C6, 7.C7, 7.C8, 7.C9, 7.C10, 7.C11 | `chino-api GET /api/v1/people/{id}`, `chino-api GET /api/v1/people/{id}/profile`, `katalog-api GET /people/{id}` | `person-titles-limit` |
| `see-cast-and-crew` | 6.C12, 6.C13 | `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/people/{id}/profile`, `katalog-api GET /items/{id}` | `cast-preview`, `credits-cap` |

## Watchlist and lists

What a person keeps to watch, in lists of their own, and what they watched. Specified in [chapter 8](../chino/watchlist.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Put a title on the Watchlist, or take it off | person | built | built | built | built | [6.5.2](../chino/title-actions.md#652-add-to-list), [8.1](../chino/watchlist.md#81-purpose) |
| See the Watchlist and one's own lists, and open one with all its titles | person | built | built | built | built | [8.3](../chino/watchlist.md#83-the-watchlist-on-a-computer), [8.6](../chino/watchlist.md#86-a-list), [8.8](../chino/watchlist.md#88-what-a-list-holds) |
| Put a title in one's own lists, or take it out of them | person | built | built | built | no | [6.5.2](../chino/title-actions.md#652-add-to-list) |
| Create a list of one's own | person | built | built | built | built | [8.7.1](../chino/watchlist.md#871-creating-a-list), [8.7.4](../chino/watchlist.md#874-names-and-limits) |
| Start a new list from a title's page, with the title in it | person | built | built | built | no | [6.5.2](../chino/title-actions.md#652-add-to-list), [8.7.1](../chino/watchlist.md#871-creating-a-list) |
| Rename a list | person | built | built | built | built | [8.7.2](../chino/watchlist.md#872-renaming-a-list) |
| Delete a list of one's own | person | built | built | built | partial | [8.7.3](../chino/watchlist.md#873-deleting-a-list) |
| Mark a title or an episode as watched, or take the mark off | person | built | built | built | built | [6.5.3](../chino/title-actions.md#653-on-and-off), [5.8](../chino/browse.md#58-the-grid) |
| Count a title as watched once it is played into its credits or its end | system | built | built | built | built | [11.7](../chino/playback.md#117-play-resume-and-a-finished-title) |
| See what was watched, newest first | person | built | built | built | no | [16.5](../chino/settings.md#165-the-account) |
| See on a poster whether a title is on the Watchlist, watched or begun | person | partial | partial | partial | partial | [6.5.3](../chino/title-actions.md#653-on-and-off), [6.5.4](../chino/title-actions.md#654-nothing-on-artwork), [5.8](../chino/browse.md#58-the-grid) |

- Put a title on the Watchlist, or take it off: the bookmark on a title's page and its episode rows; Samsung: a “+” for the default list, none on episodes Zap saves to it too.
- See the Watchlist and one's own lists, and open one with all its titles: a row each, the Watchlist first, then by creation; the same lists in every app
- Put a title in one's own lists, or take it out of them: the list picker beside the bookmark; Samsung has none
- Create a list of one's own: a name unique in the account; the web shows a refusal as “request failed (409)”, Android TV drops it silently
- Start a new list from a title's page, with the title in it: “new list…” in the list picker; Samsung has no picker
- Rename a list: web and both TVs rename the Watchlist too, which the target keeps fixed; the phone only the person's own lists
- Delete a list of one's own: its titles stay in the library and the other lists; Samsung deletes at once, without asking
- Mark a title or an episode as watched, or take the mark off: on the title page and its episode rows, and in a card's menu where it has one; Samsung's is an eye
- Count a title as watched once it is played into its credits or its end: each player marks it in the credits or past 95 %; the server also counts a place saved in the last 5 % or 2 min
- See what was watched, newest first: on the account page; web and phone take a title off with its watched mark; Android TV opens the title
- See on a poster whether a title is on the Watchlist, watched or begun: the bar shows only in continue watching; the phone's more like this has no marks; Samsung shows the watched check alone

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `keep-on-watchlist` | 6.C8, 6.C9, 6.C20 | `chino-api PUT /api/v1/me/watchlist/{id}`, `chino-api DELETE /api/v1/me/watchlist/{id}`, `chino-api GET /api/v1/me/watchlist` and 2 more | — |
| `see-lists` | 8.C1, 8.C2, 8.C3, 8.C9, 8.C10, 8.C11, 8.C12, 8.C15, 8.C16 | `chino-api GET /api/v1/me/watchlists`, `chino-api GET /api/v1/me/watchlists/{listId}` | `watchlist-shelf-size` |
| `put-title-in-lists` | 6.C8, 6.C9, 6.C10 | `chino-api PUT /api/v1/me/watchlists/{listId}/items/{itemId}`, `chino-api DELETE /api/v1/me/watchlists/{listId}/items/{itemId}`, `chino-api GET /api/v1/me/watchlists/memberships` | — |
| `create-list` | 8.C4, 8.C5, 8.C17 | `chino-api POST /api/v1/me/watchlists` | `list-name-length`, `lists-per-account` |
| `create-list-from-title` | 6.C10 | `chino-api POST /api/v1/me/watchlists`, `chino-api PUT /api/v1/me/watchlists/{listId}/items/{itemId}` | `list-name-length`, `lists-per-account` |
| `rename-list` | 8.C5, 8.C6, 8.C7, 8.C9, 8.C17 | `chino-api PATCH /api/v1/me/watchlists/{listId}` | `list-name-length` |
| `delete-list` | 8.C8, 8.C9 | `chino-api DELETE /api/v1/me/watchlists/{listId}` | — |
| `mark-watched` | 5.C9, 6.C9, 6.C19, 6.C20, 8.C13 | `chino-api POST /api/v1/me/items/{id}/watched`, `chino-api DELETE /api/v1/me/items/{id}/watched` | `watched-rule` |
| `count-as-watched` | 11.C39 | `chino-api POST /api/v1/me/items/{id}/watched`, `chino-api POST /api/v1/items/{id}/progress` | `watched-rule` |
| `see-watch-history` | 16.C12, 16.C13, 16.C19 | `chino-api GET /api/v1/me/watched` | `watch-history-size` |
| `see-title-marks` | 4.C13, 5.C8, 6.C17 | `chino-api GET /api/v1/me/watchlists/memberships`, `chino-api GET /api/v1/me/watchlist` | — |

## Search

Finding a title or a person by name. Specified in [chapter 9](../chino/search.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Find a movie or a show by its name | person | built | built | built | built | [9.6.1](../chino/search.md#961-matching-and-order) |
| Find a person by name | person | built | built | built | built | [9.6.1](../chino/search.md#961-matching-and-order) |
| Find an episode by its name | person | no | no | no | no | [9.6.1](../chino/search.md#961-matching-and-order) |
| See the results change while typing | person | partial | built | built | partial | [9.6.1](../chino/search.md#961-matching-and-order), [9.5](../chino/search.md#95-search-on-a-tv) |
| Come back to the results as they were after opening one | person | built | partial | partial | no | [9.6.2](../chino/search.md#962-opening-a-result-and-leaving) |
| Hear how many results there are with a screen reader | person | no | no | no | no | [9.6.1](../chino/search.md#961-matching-and-order) |
| Use what an addon offers when a search finds nothing | person | built | built | built | built | [9.8](../chino/search.md#98-states) |

- Find a movie or a show by its name: from the top bar of every view; one list for both kinds, ranked by how well the name matches, close spellings too
- Find a person by name: cast & crew over the titles; the web's list under the field leaves people out
- Find an episode by its name: the server finds episodes; every app asks for movies and shows only
- See the results change while typing: web: eight titles under the field, the results page only on Enter; Samsung's keyboard covers the results
- Come back to the results as they were after opening one: the phone runs the search again; Android TV keeps them but focuses the field; Samsung forgets the words
- Use what an addon offers when a search finds nothing: the search.empty slot's buttons, with the words typed; nothing shows on a server without such an addon

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `search-titles` | 2.C12, 9.C2, 9.C4, 9.C7, 9.C8, 9.C9, 9.C10, 9.C15 | `chino-api GET /api/v1/search`, `chino-api GET /api/v1/items`, `katalog-api GET /search` and 1 more | `search-result-limits`, `search-spelling-tolerance` |
| `search-people` | 9.C2, 9.C3 | `chino-api GET /api/v1/search`, `chino-api GET /api/v1/people`, `katalog-api GET /search` and 1 more | `search-result-limits`, `search-spelling-tolerance` |
| `search-episodes` | 9.C5 | `chino-api GET /api/v1/search`, `katalog-api GET /search` | — |
| `search-as-you-type` | 9.C1, 9.C6, 9.C11, 9.C13 | `chino-api GET /api/v1/search` | `search-debounce` |
| `return-to-results` | 9.C12 | — | — |
| `hear-result-count` | 9.C14 | — | — |
| `act-on-empty-search` | 9.C7 | `chino-api GET /api/v1/extensions` | — |

## Zap

Titles one after the other, playing from their middle, to find something to watch. Specified in [chapter 10](../chino/zap.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Zap through titles, each card playing a scene with its sound | person | built | partial | built | built | [10.3](../chino/zap.md#103-zap-on-a-computer), [10.4](../chino/zap.md#104-zap-on-a-phone), [10.5](../chino/zap.md#105-zap-on-a-tv), [10.7](../chino/zap.md#107-the-light), [10.9](../chino/zap.md#109-states) |
| Pick only the unwatched, ready-made movies and episodes for zap | system | partial | partial | partial | partial | [10.6.1](../chino/zap.md#1061-the-titles), [0002 prepackaged playback](../../docs/adr/0002-prepackaged-playback.md) |
| Start each card at a random scene between the intro and the credits | system | partial | partial | partial | partial | [10.6.2](../chino/zap.md#1062-the-scene), [10.6.1](../chino/zap.md#1061-the-titles) |
| Pick the next cards by what the person saves, watches or passes | system | partial | partial | partial | no | [10.6.1](../chino/zap.md#1061-the-titles) |
| Watch a zapped title in the player from the second its scene reached | person | built | built | built | built | [10.3](../chino/zap.md#103-zap-on-a-computer), [10.5](../chino/zap.md#105-zap-on-a-tv), [10.6.3](../chino/zap.md#1063-what-zap-leaves-alone) |
| Come back from the player to the same zap session and card | person | no | no | built | no | [10.6.3](../chino/zap.md#1063-what-zap-leaves-alone) |
| Go back to the card before, its scene again from where the card began | person | no | partial | built | built | [10.3](../chino/zap.md#103-zap-on-a-computer), [10.5](../chino/zap.md#105-zap-on-a-tv), [10.6.2](../chino/zap.md#1062-the-scene) |
| Turn zap's sound off and on from the remote | person | — | — | built | partial | [10.5](../chino/zap.md#105-zap-on-a-tv) |
| Skip a title that can't be played, at most six in a row | system | — | — | built | no | [10.5](../chino/zap.md#105-zap-on-a-tv), [10.9](../chino/zap.md#109-states) |

- Zap through titles, each card playing a scene with its sound: iOS shows a black box in place of every clip; save and watch on every card; the TVs show the info at the foot for a minute
- Pick only the unwatched, ready-made movies and episodes for zap: web: the ready pool's later cards not checked for watched; phone, Android TV: movies only; Samsung: shows too, ready-made or not
- Start each card at a random scene between the intro and the credits: the phone, the TVs and the web's ready pool pick from the length alone, which no change names for the pool; first card at 35 %
- Pick the next cards by what the person saves, watches or passes: web, phone, Android TV learn kind, genres and cast but pick by kind alone, the web's pool cards not at all; Samsung shuffles
- Watch a zapped title in the player from the second its scene reached: a click or a tap anywhere on the card, OK on a TV; zapping itself never counts as watched or moves the resume point
- Come back from the player to the same zap session and card: the web loads zap anew with new cards; the phone app and Samsung start a new session
- Go back to the card before, its scene again from where the card began: the web drops a card once it is left; the phone app goes on where the card was paused
- Turn zap's sound off and on from the remote: Samsung mutes the TV's own sound and leaves it muted after zap; a computer or a phone uses its own volume
- Skip a title that can't be played, at most six in a row: Samsung means to skip but stays on the poster until down is pressed; on a computer or a phone the card stays

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `zap-through-titles` | 10.C1, 10.C2, 10.C3, 10.C4, 10.C6, 10.C7, 10.C15, 10.C16, 10.C17, 10.C18, 10.C19, 10.C20, 10.C21, 17.C9 | `chino-api GET /api/v1/play/zap-feed`, `chino-stream GET /api/play/zap-feed`, `chino-api POST /api/v1/items/{id}/play/prewarm` and 4 more | `zap-ready-pool`, `zap-warm-slots`, `zap-info-linger` |
| `pick-zap-titles` | 10.C8, 10.C9, 10.C10 | `chino-api GET /api/v1/items`, `chino-api GET /api/v1/me/watched`, `chino-api GET /api/v1/play/packaged-ids` and 6 more | `zap-list-size`, `zap-watched-check`, `zap-ready-pool` |
| `pick-zap-scene` | 10.C10, 10.C11, 10.C12 | `chino-api GET /api/v1/items/{id}/segments`, `katalog-api GET /items/{id}/segments`, `chino-api GET /api/v1/play/zap-feed` | `zap-scene-window`, `zap-first-card` |
| `learn-from-zapping` | 10.C13 | — | `zap-dwell`, `zap-exploration`, `zap-weights` |
| `watch-from-zap` | 10.C6, 10.C14 | — | — |
| `return-to-zap-session` | 10.C14 | — | — |
| `go-back-zap-card` | 10.C5 | — | — |
| `mute-zap` | 10.C18 | — | — |
| `skip-unplayable-channel` | 10.C18 | — | `zap-dead-channels` |

## The player

Playing a title: resume, quality, audio, skipping, the next episode, the picture. Specified in [chapter 11](../chino/playback.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Play a movie or an episode | person | built | built | built | built | [11.3](../chino/playback.md#113-the-player-on-a-computer), [11.4](../chino/playback.md#114-the-player-on-a-phone), [11.5](../chino/playback.md#115-the-player-on-a-tv), [11.6](../chino/playback.md#116-showing-and-hiding-the-controls), [11.17](../chino/playback.md#1117-states), [0002 prepackaged playback](../../docs/adr/0002-prepackaged-playback.md), [0013 live rungs safety net](../../docs/adr/0013-live-rungs-safety-net.md) |
| Resume a title where it stopped, or start it over | person | partial | built | partial | partial | [11.7](../chino/playback.md#117-play-resume-and-a-finished-title) |
| Seek within a title, with a still of the moment and its marked parts | person | built | partial | partial | partial | [11.3](../chino/playback.md#113-the-player-on-a-computer), [11.4.2](../chino/playback.md#1142-held-sideways), [11.5](../chino/playback.md#115-the-player-on-a-tv) |
| Skip the intro, a recap or the credits with one press | person | built | built | built | built | [11.8.1](../chino/playback.md#1181-skip-intro-skip-recap-and-skip-credits) |
| Skip intros and recaps by themselves on episodes watched in a row | system | partial | no | partial | partial | [11.8.2](../chino/playback.md#1182-auto-skip), [16.4.2](../chino/settings.md#1642-binge-watching) |
| Go on to the next episode with up next | person | built | partial | partial | partial | [11.8.3](../chino/playback.md#1183-up-next), [11.8.4](../chino/playback.md#1184-going-on-to-the-next-episode) |
| Go to the previous or the next episode from the player | person | built | built | partial | partial | [11.3](../chino/playback.md#113-the-player-on-a-computer) |
| Choose the picture's quality, or Auto | person | built | partial | built | partial | [11.9](../chino/playback.md#119-quality-names), [11.10](../chino/playback.md#1110-the-players-menus) |
| Keep a title playing when the stream falters, stepping down and saying why | system | built | built | partial | partial | [11.13](../chino/playback.md#1113-when-the-quality-changes-by-itself), [11.13.1](../chino/playback.md#11131-when-the-stream-falters) |
| Set the volume and the playback speed in the player | person | built | built | built | no | [11.3](../chino/playback.md#113-the-player-on-a-computer), [11.5](../chino/playback.md#115-the-player-on-a-tv), [11.10](../chino/playback.md#1110-the-players-menus) |
| Fit the picture without its baked-in black bars, or fill the screen | person | built | built | — | — | [11.11](../chino/playback.md#1111-the-picture) |
| Keep a title playing in picture in picture, with controls on the lock screen | person | built | partial | — | — | [11.12](../chino/playback.md#1112-picture-in-picture-airplay-and-the-lock-screen) |
| Keep the screen on and the screen saver away while a title plays | system | — | built | built | no | [11.12](../chino/playback.md#1112-picture-in-picture-airplay-and-the-lock-screen) |
| See how a title plays and reaches the screen | person | built | partial | partial | no | [11.15](../chino/playback.md#1115-playback-info) |
| Say why a title couldn't play, also when no picture comes within 20 seconds | system | built | partial | partial | partial | [11.17](../chino/playback.md#1117-states), [17.7](../chino/errors.md#177-the-causes), [17.9](../chino/errors.md#179-a-removed-title-or-person) |
| File a bug report by itself when a title won't play, showing its number | system | built | partial | partial | no | [11.17](../chino/playback.md#1117-states) |
| Send how playback went to the server, for the people who run it | system | built | built | built | no | — |
| Control the player with the keyboard or the remote's keys | person | built | — | built | partial | [11.3](../chino/playback.md#113-the-player-on-a-computer), [11.5](../chino/playback.md#115-the-player-on-a-tv) |
| Choose the audio track a title plays in | person | built | built | built | built | [12.3](../chino/subtitles.md#123-the-panel-on-a-computer), [12.6](../chino/subtitles.md#126-the-audio-column), [11.14](../chino/playback.md#1114-the-audio-setting) |
| Watch a title together from different places, in step | person | no | no | no | no | — |
| Hear a title in surround where the device and the room play it | person | ? | ? | ? | ? | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |

- Play a movie or an episode: the package, or a version converted as it plays; Samsung has no top and no home; what a start shows differs per app
- Resume a title where it stopped, or start it over: saved every 10 s; the web saves no more, Samsung not on pause, Android TV even before a resume landed; the phone keeps it offline
- Seek within a title, with a still of the moment and its marked parts: the apps show the still for ready-made titles only, Samsung without the time; Samsung's seek bar takes no focus
- Skip the intro, a recap or the credits with one press: the web offers skip credits only without a next episode; Samsung offers a skip for any part, a chapter too
- Skip intros and recaps by themselves on episodes watched in a row: the web skips the intro only; the phone app's player reads no setting; the TVs skip on every episode, the first too, and credits
- Go on to the next episode with up next: phone: up next only with auto-play on, without the name; Android TV: a note without buttons; Samsung: no card
- Go to the previous or the next episode from the player: Android TV shows both on every episode, doing nothing at a season's ends; Samsung has next episode only
- Choose the picture's quality, or Auto: the phone app has no Auto; Samsung's Auto doesn't name the quality playing; the apps reload the stream on a pick
- Keep a title playing when the stream falters, stepping down and saying why: Android TV doesn't ask again after a long pause; Samsung: its engine's own recovery, none on the TV's player, no notices
- Set the volume and the playback speed in the player: Android TV: the volume is one focus stop, up and down 5 % a press; Samsung has neither
- Fit the picture without its baked-in black bars, or fill the screen: Android: a pinch fills any title; iOS and the TVs fit the whole frame, as the spec has it
- Keep a title playing in picture in picture, with controls on the lock screen: the web: the browser's own picture in picture; iOS has it, with AirPlay; the Android app has none
- Keep the screen on and the screen saver away while a title plays: Samsung: not found in its code
- See how a title plays and reaches the screen: for the people who fix things; the phone's dialog lacks the quality changes; Android TV's card closes after 8 s
- Say why a title couldn't play, also when no picture comes within 20 seconds: iOS gives up after 20 s too, Android never; Android TV shows the raw error without try again; Samsung the error's text
- File a bug report by itself when a title won't play, showing its number: the phone app files one for each failure shown, Android TV one for every player error; neither shows the number
- Send how playback went to the server, for the people who run it: events batched about every 30 s and on leaving; the server logs them and counts startup, stalls and bandwidth
- Control the player with the keyboard or the remote's keys: Samsung: fast forward and rewind 30 s, no subtitles or audio key, down with the controls hidden does nothing
- Choose the audio track a title plays in: no app marks the original or a described track: the catalog keeps no original language; the phone greys one it can't play
- Hear a title in surround where the device and the room play it: a 5.1 track only where an instance turns it on; which apps play it is not checked

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `play-title` | 11.C1, 11.C7, 11.C8, 11.C9, 11.C11, 11.C14, 11.C42, 11.C43 | `chino-api POST /api/v1/me/stream-token`, `chino-api GET /api/v1/items/{id}`, `chino-api GET /api/v1/items/{id}/play/info` and 17 more | `stream-token-lifetime`, `controls-hide` |
| `resume-title` | 11.C39, 11.C40 | `chino-api GET /api/v1/items/{id}/progress`, `chino-api POST /api/v1/items/{id}/progress` | `progress-save-interval`, `restart-near-end`, `resume-floor`, `watched-rule` |
| `seek-title` | 11.C15, 11.C16, 11.C17, 11.C18 | `chino-api GET /api/v1/items/{id}/play/trickplay/*`, `chino-stream GET /trickplay/*`, `chino-api GET /api/v1/items/{id}/segments` and 1 more | `seek-step` |
| `skip-intro` | 11.C19 | `chino-api GET /api/v1/items/{id}/segments`, `katalog-api GET /items/{id}/segments` | — |
| `auto-skip-intro` | 11.C20, 11.C21, 11.C27 | `chino-api GET /api/v1/items/{id}/segments`, `katalog-api GET /items/{id}/segments` | `auto-skip-intros`, `binge-countdown`, `binge-window`, `auto-skip-credits` |
| `play-next-episode` | 11.C22, 11.C23, 11.C24, 11.C25, 11.C26, 11.C28 | `chino-api GET /api/v1/series/{id}/next-episode`, `katalog-api GET /series/{id}/episodes`, `chino-api GET /api/v1/items/{id}/segments` and 3 more | `auto-play-next`, `binge-countdown`, `up-next-trigger`, `next-episode-guard`, `next-episode-warm`, `zap-warm-slots` |
| `step-episodes` | 11.C5, 11.C11 | `chino-api GET /api/v1/series/{id}/episodes`, `chino-api GET /api/v1/series/{id}/next-episode` | — |
| `choose-quality` | 11.C3, 11.C29, 11.C31, 11.C32 | `chino-api GET /api/v1/items/{id}/play/info`, `chino-api GET /api/v1/items/{id}/play/master.m3u8`, `chino-api GET /api/v1/items/{id}/play/{quality}/*` | — |
| `recover-faltering-stream` | 11.C34, 11.C35, 11.C36, 11.C43 | `chino-api POST /api/v1/me/stream-token`, `chino-api GET /api/v1/items/{id}/play/master.m3u8` | `stall-recovery`, `stream-token-lifetime` |
| `set-volume-speed` | 11.C6, 11.C11, 11.C29 | — | — |
| `fit-picture` | — | `chino-api GET /api/v1/items/{id}/play/info` | `fill-carry-limit` |
| `play-in-background` | 11.C10, 11.C37 | — | — |
| `keep-screen-awake` | 11.C38 | — | — |
| `show-playback-info` | 11.C48 | `chino-api GET /api/v1/items/{id}/play/info` | — |
| `explain-playback-failure` | 11.C44, 11.C45, 11.C47 | — | `startup-deadline` |
| `report-playback-failure` | 11.C46 | `chino-api POST /api/v1/feedback` | `auto-report-limit`, `report-dedup-window`, `report-rate-limit` |
| `report-playback-quality` | — | `chino-api POST /api/v1/play/events` | — |
| `use-player-keys` | 11.C12, 11.C13 | — | `seek-step` |
| `choose-audio` | 11.C2, 11.C4, 11.C30, 12.C1, 12.C10 | `chino-api GET /api/v1/items/{id}/play/info`, `chino-api GET /api/v1/items/{id}/play/audio/*`, `chino-stream GET /audio/*` and 2 more | `audio-language` |
| `watch-together` | — | — | — |
| `play-surround` | — | — | `surround-audio` |

## Subtitles

Choosing subtitles and how they look, in every kind of subtitle the library holds. Specified in [chapter 12](../chino/subtitles.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| Choose a title's subtitles, or turn them off | person | built | built | built | built | [12.3](../chino/subtitles.md#123-the-panel-on-a-computer), [12.4](../chino/subtitles.md#124-the-panel-on-a-phone), [12.5](../chino/subtitles.md#125-the-panel-on-a-tv), [12.7](../chino/subtitles.md#127-the-subtitles-column) |
| Turn subtitles on by themselves when the audio isn't in the person's language | system | built | built | built | built | [12.9](../chino/subtitles.md#129-what-switches-on-by-itself), [12.10](../chino/subtitles.md#1210-the-setting) |
| Show Blu-ray subtitles made as pictures (PGS) on the picture | person | built | partial | built | partial | [12.7](../chino/subtitles.md#127-the-subtitles-column), [12.8](../chino/subtitles.md#128-the-look), [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Show DVD subtitles made as pictures (VobSub) on the picture | person | no | no | no | no | [12.7](../chino/subtitles.md#127-the-subtitles-column), [12.8](../chino/subtitles.md#128-the-look), [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Show broadcast subtitles made as pictures (DVB) on the picture | person | no | no | no | no | — |
| Show styled subtitles (ASS) as they were made, with the title's fonts | person | no | no | no | no | [12.8](../chino/subtitles.md#128-the-look), [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| Show text subtitles in one readable look, sized by the picture, clear of the controls | system | built | built | built | partial | [12.8](../chino/subtitles.md#128-the-look), [11.10](../chino/playback.md#1110-the-players-menus) |
| Follow the caption preferences set on the device | system | — | partial | built | no | [12.8](../chino/subtitles.md#128-the-look) |
| Move the subtitles earlier or later while a title plays | person | built | no | no | no | [11.10](../chino/playback.md#1110-the-players-menus) |

- Choose a title's subtitles, or turn them off: a menu of its own in each app today; iOS lists every track as it comes; Samsung numbers two that read the same
- Turn subtitles on by themselves when the audio isn't in the person's language: else the foreign-language parts in the audio's language; every app lists those parts as rows, and off turns them off
- Show Blu-ray subtitles made as pictures (PGS) on the picture: Android and Android TV draw them with a reader of their own, in testing; iOS greys them; Samsung only on its fallback engine
- Show DVD subtitles made as pictures (VobSub) on the picture: the web and Samsung leave them out; Android and Android TV list them and show nothing; iOS greys them
- Show broadcast subtitles made as pictures (DVB) on the picture: the server hands them out by their format; no app draws them, and the spec names only PGS and VobSub
- Show styled subtitles (ASS) as they were made, with the title's fonts: every app shows the plain copy the package keeps beside them, in the one look
- Show text subtitles in one readable look, sized by the picture, clear of the controls: Samsung: a dark box at one size, italics dropped; an open menu covers the line on the web, the phone and Samsung
- Follow the caption preferences set on the device: a web page can't read them; iOS draws its own overlay without them; Samsung: not found in its code
- Move the subtitles earlier or later while a title plays: the web, in its subtitles menu, for subtitles made as text

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `choose-subtitles` | 11.C2, 11.C4, 11.C41, 12.C1, 12.C2, 12.C3, 12.C5 | `chino-api GET /api/v1/items/{id}/subtitles`, `chino-api GET /api/v1/play/subs/{id}.vtt`, `chino-api GET /api/v1/items/{id}/play/subtitles/{streamIndex}.vtt` and 6 more | `subtitle-language` |
| `switch-on-subtitles` | 12.C4 | `chino-api GET /api/v1/items/{id}/subtitles` | `subtitle-language` |
| `show-pgs-subtitles` | 12.C7 | `chino-api GET /api/v1/play/subs/{id}.vtt`, `chino-stream GET /api/play/subs/{subID}.sup`, `katalog-api GET /api/v1/subtitles/{id}/asset` | — |
| `show-vobsub-subtitles` | 12.C9 | `chino-stream GET /api/play/subs/{subID}.idx`, `chino-stream GET /api/play/subs/{subID}.sub`, `katalog-api GET /api/v1/subtitles/{id}/asset` | — |
| `show-dvb-subtitles` | — | `chino-stream GET /api/play/subs/{subID}.dvb` | — |
| `show-styled-subtitles` | 12.C8 | `chino-api GET /api/v1/play/subs/{id}.ass`, `chino-api GET /api/v1/play/fonts/{id}.`, `chino-stream GET /api/play/subs/{subID}.ass` and 2 more | — |
| `keep-subtitles-readable` | 12.C6, 11.C33 | — | `subtitle-look` |
| `follow-caption-preferences` | 12.C6 | — | — |
| `time-subtitles` | 11.C3 | — | `subtitle-timing-step` |

## Downloads and offline

Keeping a title on a phone to watch without a connection. Specified in [chapter 13](../chino/downloads.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Phone | Spec |
|---|---|---|---|
| Download a title or a season's episodes to watch without a connection | person | partial | [13.3](../chino/downloads.md#133-the-download-control), [13.3.1](../chino/downloads.md#1331-on-a-show), [13.3.2](../chino/downloads.md#1332-while-downloads-run), [13.7](../chino/downloads.md#137-settings) |
| See the downloads and the room they take, and delete them | person | partial | [13.4](../chino/downloads.md#134-the-downloads-screen), [13.4.4](../chino/downloads.md#1344-deleting) |
| Play downloads while the server can't be reached, their progress sent later | person | partial | [13.6](../chino/downloads.md#136-when-the-server-cant-be-reached), [13.6.1](../chino/downloads.md#1361-the-downloads-screen), [13.6.2](../chino/downloads.md#1362-a-titles-page-from-the-phone), [13.6.3](../chino/downloads.md#1363-a-download-that-waits-for-its-check), [13.6.4](../chino/downloads.md#1364-the-rest-of-the-app), [14.4.6](../chino/casting.md#1446-downloads-without-the-server) |
| Keep each account's downloads to itself, deleting them when it leaves the phone | system | partial | [13.5](../chino/downloads.md#135-whose-downloads-they-are), [16.5.5](../chino/settings.md#1655-sign-out-remove-account-and-change-server) |
| Delete downloads the account may no longer watch, and say so once | system | partial | [13.5](../chino/downloads.md#135-whose-downloads-they-are), [13.6.3](../chino/downloads.md#1363-a-download-that-waits-for-its-check) |

- Download a title or a season's episodes to watch without a connection: the Android app only; offered where the server offers downloads; a notification shows the progress
- See the downloads and the room they take, and delete them: the Android app only; deleting one asks nothing, delete all asks first
- Play downloads while the server can't be reached, their progress sent later: the Android app only; it opens on downloads under a banner; a download plays on the phone even while a TV is connected
- Keep each account's downloads to itself, deleting them when it leaves the phone: the Android app only; two accounts share one copy; sign out, remove account and change server ask first
- Delete downloads the account may no longer watch, and say so once: the Android app only; after two answers at least an hour apart, a day where an answer leaves out every title

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `download-titles` | 13.C1, 13.C2, 13.C6, 16.C5 | `chino-api GET /api/config`, `chino-api POST /api/v1/me/stream-token`, `chino-api GET /api/v1/items/{id}/play/info` and 5 more | `downloads-switch`, `download-quality`, `download-wifi-only`, `stream-token-lifetime` |
| `manage-downloads` | 13.C2, 13.C3, 13.C6 | — | — |
| `play-downloads-offline` | 10.C21, 13.C4, 13.C6 | `chino-api POST /api/v1/items/{id}/progress` | `download-check-age`, `server-recheck` |
| `keep-downloads-per-account` | 13.C5, 16.C14 | — | — |
| `remove-unavailable-downloads` | — | `chino-api POST /api/v1/me/available`, `katalog-api GET /api/v1/visible` | `download-removal-gap`, `download-check-age` |

## Casting

Playing on a TV from a phone or a computer. Specified in [chapter 14](../chino/casting.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Phone | Spec |
|---|---|---|---|
| Cast a title to a TV on the network, going on where the phone was | person | partial | [14.3](../chino/casting.md#143-the-cast-button), [14.4.4](../chino/casting.md#1444-handing-over), [11.12](../chino/playback.md#1112-picture-in-picture-airplay-and-the-lock-screen) |
| Control the TV from the phone while casting, also from the lock screen | person | partial | [14.4.1](../chino/casting.md#1441-the-bar), [14.4.2](../chino/casting.md#1442-the-full-controls), [14.4.3](../chino/casting.md#1443-outside-the-app) |
| Show the title's subtitles on the TV while casting, every kind | system | partial | [14.4.2](../chino/casting.md#1442-the-full-controls) |
| Say when the TV can't play a title, after one more try where that can help | system | partial | [14.5](../chino/casting.md#145-when-the-tv-cant-play-a-title) |
| Stop casting when the account signs out or changes, keeping its place | system | partial | [14.4.5](../chino/casting.md#1445-changing-accounts) |

- Cast a title to a TV on the network, going on where the phone was: the Android app with Google Cast, not yet tried on a real Cast device; iOS sends to a screen with AirPlay from the player
- Control the TV from the phone while casting, also from the lock screen: the Android app only: the bar, the full controls, the notification; the TV's audio tracks by the stream's names
- Show the title's subtitles on the TV while casting, every kind: text subtitles only, as WebVTT: picture subtitles are left out, and a styled one goes as its plain copy
- Say when the TV can't play a title, after one more try where that can help: the Android app only; a warning in the bar's place, with details; casting stops, the title stays paused on the phone
- Stop casting when the account signs out or changes, keeping its place: the Android app only; the questions before signing out say casting stops; a switch says so after, in a toast

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `cast-title` | 11.C10, 14.C1 | `chino-api POST /api/v1/me/stream-token`, `chino-api GET /api/v1/items/{id}/play/master.m3u8`, `chino-api GET /api/v1/items/{id}/play/{rendId:[va][0-9]+}/*` and 1 more | `stream-token-lifetime` |
| `control-cast` | 14.C2 | `chino-api POST /api/v1/items/{id}/progress` | `progress-save-interval`, `seek-step` |
| `show-cast-subtitles` | 14.C4 | `chino-api GET /api/v1/play/subs/{id}.vtt` | — |
| `report-cast-failure` | 14.C3 | — | — |
| `stop-cast-on-account-change` | 13.C5, 16.C14 | `chino-api POST /api/v1/items/{id}/progress` | — |

## Notifications

What the server tells a person, in the bell. Specified in [chapter 15](../chino/notifications.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Spec |
|---|---|---|---|---|---|---|
| See the notifications addons left, with the number unread | person | built | built | built | built | [15.3](../chino/notifications.md#153-notifications-on-a-computer), [15.4](../chino/notifications.md#154-notifications-on-a-phone), [15.5](../chino/notifications.md#155-notifications-on-a-tv), [15.6.1](../chino/notifications.md#1561-what-a-notification-says), [15.6.3](../chino/notifications.md#1563-asking-the-server), [15.8](../chino/notifications.md#158-states) |
| Open the title a notification is about, marking it read | person | built | built | built | partial | [15.6.2](../chino/notifications.md#1562-where-it-leads) |
| Follow a notification's link where it stays on this server | person | built | built | — | — | [15.6.2](../chino/notifications.md#1562-where-it-leads) |
| Mark every notification read, or delete one | person | built | built | built | built | [15.6.3](../chino/notifications.md#1563-asking-the-server) |
| Be told on the phone while the app is closed | person | — | no | — | — | — |

- See the notifications addons left, with the number unread: no bell where the server offers none; the phone hides it offline; Android TV's screen shows the bell's last answer
- Open the title a notification is about, marking it read: Samsung opens an episode's own page, not its show's at that episode
- Follow a notification's link where it stays on this server: the web in the same tab, the phone in its browser, offered beside the title too; a TV follows no link
- Mark every notification read, or delete one: shown at once, the list read again where the server refuses; Android TV shows a change only once the server made it
- Be told on the phone while the app is closed: the bell fills while the app is open; the push service is a scaffold nothing runs

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `see-notifications` | 15.C1, 15.C2, 15.C3, 15.C5, 15.C6, 15.C7, 15.C8, 15.C9, 15.C10, 15.C13 | `chino-api GET /api/v1/notices`, `zaentrum-portal GET /api/portal/me/notices` | `notice-poll` |
| `open-notification` | 15.C4, 15.C11, 15.C12 | `chino-api POST /api/v1/notices/{noticeId}/read`, `zaentrum-portal POST /api/portal/me/notices/{id}/read` | — |
| `follow-notification-link` | 15.C4 | — | — |
| `clear-notifications` | 15.C3, 15.C8, 15.C11 | `chino-api POST /api/v1/notices/read-all`, `chino-api DELETE /api/v1/notices/{noticeId}`, `zaentrum-portal POST /api/portal/me/notices/read-all` and 1 more | — |
| `get-push-notification` | — | — | — |

## Settings and account

A person's settings, reporting a problem, and the account itself. Specified in [chapter 16](../chino/settings.md). Depth: deep. For the goal [Watch films and shows](../goals/README.md#watch-films-and-shows).

| Capability | Who | Web | Phone | Android TV | Samsung TV | Portal | Catalog console | Spec |
|---|---|---|---|---|---|---|---|---|
| Set the audio and subtitle languages titles start in | person | built | built | built | partial | — | — | [16.4.1](../chino/settings.md#1641-language), [11.14](../chino/playback.md#1114-the-audio-setting), [12.10](../chino/subtitles.md#1210-the-setting) |
| Set how episodes follow one another: auto-skip, auto-play next, the countdown | person | built | partial | built | built | — | — | [16.4.2](../chino/settings.md#1642-binge-watching) |
| Set every setting back to its first value at once | person | built | — | — | — | — | — | [16.2.1](../chino/settings.md#1621-the-web) |
| See the app's version, to tell the people who run the server | person | no | no | no | no | — | — | [16.4.6](../chino/settings.md#1646-about) |
| Report a bug to the people who run the server | person | built | built | built | partial | — | — | [16.4.5](../chino/settings.md#1645-report-a-bug), [17.13](../chino/errors.md#1713-when-an-action-fails) |
| Report a bug from the player's error, with what the player knows of it | person | built | built | built | no | — | — | [11.17](../chino/playback.md#1117-states), [16.4.5](../chino/settings.md#1645-report-a-bug) |
| File a bug report by itself when the app crashes | system | built | partial | built | built | — | — | [16.4.5](../chino/settings.md#1645-report-a-bug) |
| Delete one's account and what the server keeps of it | person | built | built | built | built | — | — | [16.5.6](../chino/settings.md#1656-delete-account) |
| Use the apps and the consoles in one's own language | person | no | no | no | no | no | no | — |
| See the devices one is signed in on, and sign one out from afar | person | no | no | no | no | — | — | — |

- Set the audio and subtitle languages titles start in: Samsung: Original and eight fixed languages with texts of its own, not the server's subtitle languages
- Set how episodes follow one another: auto-skip, auto-play next, the countdown: the phone app has no countdown, and its player reads only auto-play next; the phone and the TVs add auto-skip credits
- Set every setting back to its first value at once: the web only, without asking; the spec recommends leaving it out
- See the app's version, to tell the people who run the server: no app shows its version
- Report a bug to the people who run the server: only where the server takes reports, but Samsung offers it always; the TVs pick one of six choices instead of typing
- Report a bug from the player's error, with what the player knows of it: Android TV: report this problem, with its list of choices; Samsung's failure screen offers no report
- File a bug report by itself when the app crashes: iOS files none
- Delete one's account and what the server keeps of it: offered on every server, also one that deletes none; the web asks to type DELETE; the TVs show a screen of their own
- Use the apps and the consoles in one's own language: every app and console is in English alone
- See the devices one is signed in on, and sign one out from afar: signing out is done on the device itself

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `set-play-languages` | 12.C10, 16.C1, 16.C2, 16.C3, 16.C18, 16.C19 | `chino-api GET /api/v1/subtitles/languages` | `audio-language`, `subtitle-language` |
| `set-binge-watching` | 16.C1, 16.C4 | — | `auto-skip-intros`, `auto-skip-credits`, `auto-play-next`, `binge-countdown` |
| `reset-settings` | 16.C9 | — | — |
| `see-app-version` | 16.C8 | — | — |
| `report-bug` | 16.C7, 16.C10, 16.C11, 17.C14 | `chino-api POST /api/v1/feedback`, `chino-api GET /api/config` | `report-rate-limit`, `report-dedup-window`, `bug-report-target` |
| `report-playback-bug` | 11.C45, 16.C10 | `chino-api POST /api/v1/feedback` | `report-rate-limit`, `report-dedup-window`, `bug-report-target` |
| `report-crash` | — | `chino-api POST /api/v1/feedback` | `auto-report-limit`, `report-dedup-window`, `bug-report-target` |
| `delete-account` | 16.C15, 16.C16, 16.C17 | `chino-api DELETE /api/v1/me`, `zaentrum-portal DELETE /api/portal/me` | — |
| `choose-interface-language` | — | — | — |
| `see-own-devices` | — | — | — |
<!-- end: areas -->
