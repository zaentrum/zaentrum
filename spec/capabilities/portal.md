# The portal

The capabilities of the portal: its home page, the registry admins edit, addons,
people and roles, and running the platform. Most of them have no chapter yet; the
[portal's pages](../portal/README.md) cover the home page and part of settings.
The columns are explained in [how to read it](./README.md#how-to-read-it); every
row comes from [capabilities.csv](./capabilities.csv).

<!-- generated: areas -->
## The portal's home

Where everyone signs in: the spaces, their tiles, the search across them, an app opened in place. Specified in [portal home](../portal/home.md). Depth: deep.

| Capability | Who | Portal | Spec |
|---|---|---|---|
| Sign in to the portal once, stay signed in, and sign out | person | built | [As deployed](../portal/home.md#as-deployed), [States](../portal/home.md#states) |
| Open an app one may use from its tile on the home page | person | partial | [As deployed](../portal/home.md#as-deployed), [What an admin sees](../portal/home.md#what-an-admin-sees), [Spaces](../portal/home.md#spaces), [States](../portal/home.md#states) |
| Move between spaces in a bar, each space at an address of its own | person | no | [Spaces](../portal/home.md#spaces), [The home page on a computer](../portal/home.md#the-home-page-on-a-computer), [The home page on a phone](../portal/home.md#the-home-page-on-a-phone), [For the keyboard and screen readers](../portal/home.md#for-the-keyboard-and-screen-readers) |
| Find a tile by its name or description across every space | person | no | [Search across spaces](../portal/home.md#search-across-spaces) |
| Use an app's console inside the portal, on the portal's sign-in | person | built | [As deployed](../portal/home.md#as-deployed), [console](../../docs/extending/console.md) |
| Read the notifications addons sent in the portal's bell, mark them read, delete them | person | built | [As deployed](../portal/home.md#as-deployed), [The home page on a computer](../portal/home.md#the-home-page-on-a-computer), [notices](../../docs/extending/notices.md) |

- Sign in to the portal once, stay signed in, and sign out: OIDC code flow with PKCE, back where one was going; apps on this origin share the session; admin role via another client opens no console
- Open an app one may use from its tile on the home page: in place or in a new tab, as the tile says; admins get 7 console tiles too; an account with no tile gets a blank window (H.C16)
- Move between spaces in a bar, each space at an address of its own: today one page holds every space, one under the other, at /portal/
- Find a tile by its name or description across every space: the home page has no search today
- Use an app's console inside the portal, on the portal's sign-in: an app with a proxy address; its bundle under /embed/ is open, the rest needs a signed-in person, whose bearer goes on to the app
- Read the notifications addons sent in the portal's bell, mark them read, delete them: on every page of the portal; a link is followed only on this instance; chino's apps read the same ones through chino-api

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `sign-in-portal` | H.C2 | `zaentrum-portal GET /api/portal/me`, `chino-api GET /api/config` | — |
| `open-app-from-tile` | H.C1, H.C4, H.C5, H.C6, H.C7, H.C8, H.C9, H.C10, H.C14, H.C15, H.C16 | `zaentrum-portal GET /api/portal/launchpad` | `app-entry`, `space-entry`, `tile-entry`, `registry-seed` |
| `switch-space` | H.C3 | — | `space-entry` |
| `search-tiles` | H.C2, H.C11 | — | `tile-entry` |
| `open-console-in-portal` | — | `zaentrum-portal ANY /api/portal/apps/{key}/*` | `app-entry`, `app-proxy-timeout` |
| `read-portal-notifications` | — | `zaentrum-portal GET /api/portal/me/notices`, `zaentrum-portal POST /api/portal/me/notices/{id}/read`, `zaentrum-portal POST /api/portal/me/notices/read-all` and 1 more | `notification-retention`, `notifications-kept`, `portal-bell-refresh` |

## Apps, spaces, tiles and extensions

What the home page shows and where: the registry admins edit. Specified in [portal settings](../portal/settings.md). Depth: deep.

| Capability | Who | Portal | CLI | Spec |
|---|---|---|---|---|
| Register an app, change it, switch it off, or delete it with its tiles | admin | built | no | [portal settings](../portal/settings.md) |
| Add, rename, reorder or delete a space of the home page | admin | built | no | [Spaces](../portal/home.md#spaces), [portal settings](../portal/settings.md) |
| Place a tile for an app in a space, with its words, icon, order and how it opens | admin | built | no | [Spaces](../portal/home.md#spaces), [portal settings](../portal/settings.md) |
| Show a space or a tile only to the people who hold given roles | admin | built | no | [As deployed](../portal/home.md#as-deployed), [Spaces](../portal/home.md#spaces) |
| Edit the buttons addons add to the apps' screens, or add one by hand | admin | built | no | [slots](../../docs/extending/slots.md) |

- Register an app, change it, switch it off, or delete it with its tiles: a core app (chino) can be switched off, never deleted; a proxy address makes an app open inside the portal
- Add, rename, reorder or delete a space of the home page: a deleted space takes its tiles; apps and manage are core, never deleted; any number of spaces, any name (H.C12: five)
- Place a tile for an app in a space, with its words, icon, order and how it opens: badges and status squares are stored words, never checked; a deleted seed tile comes back at the next start
- Show a space or a tile only to the people who hold given roles: everyone signed in, admins, or named realm roles; the server leaves out what one may not see, and a space left empty
- Edit the buttons addons add to the apps' screens, or add one by hand: a row that breaks the slot rules is refused; an addon writes its own rows through the same routes

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `register-app` | — | `zaentrum-portal GET /api/portal/apps`, `zaentrum-portal POST /api/portal/apps`, `zaentrum-portal PATCH /api/portal/apps/{key}` and 1 more | `app-entry`, `registry-seed` |
| `arrange-spaces` | H.C4, H.C12 | `zaentrum-portal GET /api/portal/spaces`, `zaentrum-portal POST /api/portal/spaces`, `zaentrum-portal PATCH /api/portal/spaces/{key}` and 1 more | `space-entry`, `registry-seed` |
| `place-tiles` | H.C7, H.C9, H.C10 | `zaentrum-portal GET /api/portal/tiles`, `zaentrum-portal POST /api/portal/tiles`, `zaentrum-portal PATCH /api/portal/tiles/{key}` and 1 more | `tile-entry`, `registry-seed` |
| `limit-tile-audience` | — | `zaentrum-portal GET /api/portal/launchpad`, `zaentrum-portal POST /api/portal/spaces`, `zaentrum-portal PATCH /api/portal/spaces/{key}` and 2 more | `space-entry`, `tile-entry` |
| `edit-slot-rows` | — | `zaentrum-portal GET /api/portal/extensions`, `zaentrum-portal POST /api/portal/extensions`, `zaentrum-portal PATCH /api/portal/extensions/{key}` and 1 more | `slot-row` |

## Addons

Adding, installing, setting up and removing addons, and what an addon may add to the platform. Specified in [portal settings](../portal/settings.md). Depth: deep.

| Capability | Who | Web | Phone | Android TV | Samsung TV | Portal | CLI | Resource | Spec |
|---|---|---|---|---|---|---|---|---|---|
| Add an addon deployed elsewhere by its address, or refresh it after a redeploy | admin | — | — | — | — | built | built | — | [Spaces](../portal/home.md#spaces), [0009 pull based addon installation](../../docs/adr/0009-pull-based-addon-installation.md), [installing](../../docs/extending/installing.md) |
| Install an addon from its chart, after reviewing the operator's plan | admin | — | — | — | — | built | built | built | [portal settings](../portal/settings.md), [0011 addon charts installed by the operator](../../docs/adr/0011-addon-charts-installed-by-the-operator.md), [charts](../../docs/extending/charts.md), [installing](../../docs/extending/installing.md), [Settings and setup](../portal/settings.md) |
| Upgrade an addon's chart or change its values, planned before anything applies | admin | — | — | — | — | built | built | built | [portal settings](../portal/settings.md), [charts](../../docs/extending/charts.md) |
| Remove an addon and what the platform made for it, keeping its secrets if wanted | admin | — | — | — | — | built | built | built | [installing](../../docs/extending/installing.md), [charts](../../docs/extending/charts.md) |
| See each addon's parts and their state, its version and whether a refresh waits | admin | — | — | — | — | built | built | built | [An addon's setup checklist](../portal/settings.md#an-addons-setup-checklist), [0010 addon component groups and setup](../../docs/adr/0010-addon-component-groups-and-setup.md), [installing](../../docs/extending/installing.md) |
| See an addon's setup checklist and open where each section is configured | admin | — | — | — | — | built | partial | — | [An addon's setup checklist](../portal/settings.md#an-addons-setup-checklist), [Spaces](../portal/home.md#spaces), [0010 addon component groups and setup](../../docs/adr/0010-addon-component-groups-and-setup.md), [configuration](../../docs/extending/configuration.md) |
| Add an addon's buttons to the apps' screens, as where a search found nothing | addon | built | built | built | built | built | — | — | [9.2.5](../chino/search.md#925-feature-by-feature), [9.8](../chino/search.md#98-states), [slots](../../docs/extending/slots.md) |
| Use the commands services and addons declare, from the CLI | operator | — | — | — | — | — | built | — | [cli](../../docs/extending/cli.md) |
| Tell one person something, shown in the bell of every app they use | addon | built | built | built | built | built | — | — | [chapter 15](../chino/notifications.md), [notices](../../docs/extending/notices.md) |
| Count each addon's notifications, read and unread, never what they say | admin | — | — | — | — | partial | no | — | [notices](../../docs/extending/notices.md) |
| Look through the addons there are, and install one from the list | admin | — | — | — | — | no | no | — | — |

- Add an addon deployed elsewhere by its address, or refresh it after a redeploy: checked first: app, tiles, slot rows and CLI commands from its manifest; moving it to another address needs consent
- Install an addon from its chart, after reviewing the operator's plan: planned suspended, installed once the plan is clean, registered from its primary Service when Ready; a committed resource works too
- Upgrade an addon's chart or change its values, planned before anything applies: secret inputs are write-only, never shown again; putting a plan back restores chart and values, not secret inputs
- Remove an addon and what the platform made for it, keeping its secrets if wanted: a chart addon's parts and data go with it; an address addon's containers keep running; its notifications go too
- See each addon's parts and their state, its version and whether a refresh waits: a chart addon's phase, plan and running chart too; the operator console groups addon parts apart from the platform's
- See an addon's setup checklist and open where each section is configured: asked of the addon each time, with the admin's sign-in; only in registry → addons; zae shows it for an address addon only
- Add an addon's buttons to the apps' screens, as where a search found nothing: one slot today, search.empty; rows from the manifest or the addon's service account; a TV shows a link's address instead of opening it
- Use the commands services and addons declare, from the CLI: zae discover lists them, zae require asserts one, zae <service> <command> runs it with one's bearer; none compiled in
- Tell one person something, shown in the bell of every app they use: its service account posts to anyone; its console posts to its own person with their bearer; plain text; TVs follow no link
- Count each addon's notifications, read and unread, never what they say: GET /api/portal/notices answers it; no screen or command shows it
- Look through the addons there are, and install one from the list: an addon is added by its address or its chart's; there is no list

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `add-addon-by-address` | H.C13 | `zaentrum-portal POST /api/portal/addons`, `addon add`, `addon refresh` | — |
| `install-addon-chart` | H.C13 | `zaentrum-portal GET /api/portal/addon-charts`, `zaentrum-portal POST /api/portal/addon-charts`, `zaentrum-portal GET /api/portal/addon-charts/{name}` and 9 more | `addon-name-length`, `values-path-length`, `chart-registration-pace`, `addon-wait-timeout`, `kubernetes-api`, `operator-api-names`, `addon-chart`, `addon-values`, `addon-plan-only` |
| `upgrade-addon` | — | `zaentrum-portal GET /api/portal/addon-charts/{name}`, `zaentrum-portal PATCH /api/portal/addon-charts/{name}`, `zaentrum-portal POST /api/portal/addon-charts/{name}/install` and 7 more | `values-path-length`, `addon-wait-timeout` |
| `remove-addon` | — | `zaentrum-portal DELETE /api/portal/addons/{key}`, `zaentrum-portal DELETE /api/portal/addon-charts/{name}`, `addon remove` | — |
| `see-addon-state` | — | `zaentrum-portal GET /api/portal/addons`, `zaentrum-portal GET /api/portal/addons/{key}`, `zaentrum-portal GET /api/portal/addon-charts/{name}` and 3 more | `parts-selector`, `operator-console-refresh` |
| `check-addon-setup` | H.C17 | `zaentrum-portal ANY /api/portal/apps/{key}/*`, `addon status` | `app-proxy-timeout` |
| `add-slot-buttons` | 9.C7 | `zaentrum-portal GET /api/portal/slots/{slot}`, `chino-api GET /api/v1/extensions`, `zaentrum-portal POST /api/portal/addons` and 5 more | `slot-row`, `addon-role` |
| `run-declared-commands` | — | `zaentrum-portal GET /api/portal/cli/discovery`, `discover`, `require` and 1 more | `discovery-cache-age`, `parts-selector` |
| `notify-person` | — | `zaentrum-portal POST /api/portal/notices`, `zaentrum-portal POST /api/portal/me/notices` | `notification-title-length`, `notification-body-length`, `notification-post-rate`, `notification-retention`, `notifications-kept`, `addon-role` |
| `count-addon-notifications` | — | `zaentrum-portal GET /api/portal/notices` | `notification-retention`, `notifications-kept` |
| `browse-addons` | — | — | — |

## People and roles

Who may use the platform: people, their roles, invites. Not specified yet. Depth: deep.

| Capability | Who | Web | Phone | Android TV | Samsung TV | Portal | CLI | Spec |
|---|---|---|---|---|---|---|---|---|
| See everyone who may use the platform, with role, rating cap, status and invite | admin | — | — | — | — | built | no | [portal settings](../portal/settings.md) |
| Add an account for a person, as a user or as an admin | admin | — | — | — | — | built | no | [portal settings](../portal/settings.md) |
| Give a person an invite link to choose their own password | admin | — | — | — | — | built | no | — |
| Choose one's password from an invite link, then sign in on every app | person | — | — | — | — | built | — | — |
| Change a person's name or role, or switch their account off and on | admin | — | — | — | — | built | no | [portal settings](../portal/settings.md) |
| Keep titles rated above an age from a person, on every app | admin | built | built | built | built | built | no | — |
| Delete a person's account, with their data in the apps | admin | — | — | — | — | built | no | [portal settings](../portal/settings.md) |
| Say what each person may do: which libraries, downloads, quality, casting | admin | — | — | — | — | no | no | — |
| Limit how many streams a person plays at once, and their bit rate | admin | — | — | — | — | no | no | — |
| See who is watching what right now, and stop a stream | admin | — | — | — | — | no | no | — |
| See what was watched over time: by title, by person, by device | admin | — | — | — | — | no | — | — |
| Send a person a mail: an invite, a reset link, a notice | system | — | — | — | — | no | — | [First run](../../docs/self-hosting.md#first-run) |
| Bring people, their watch history and their lists from another media server | admin | — | — | — | — | no | no | — |

- See everyone who may use the platform, with role, rating cap, status and invite: with bundled identity; with an outside identity provider the page says so and links to it; the platform's own accounts left out
- Add an account for a person, as a user or as an admin: enabled, with no password; the answer holds their first invite link, shown once
- Give a person an invite link to choose their own password: a new link stops the older ones; shown once, to copy; switching the account off revokes it
- Choose one's password from an invite link, then sign in on every app: no sign-in needed; works once; every dead link gets the same answer; limited per address and per link
- Change a person's name or role, or switch their account off and on: the last enabled admin stays one; nobody changes their own role or switches themselves off; an identity provider admin is changed there
- Keep titles rated above an age from a person, on every app: an age on the account, carried in the person's token to chino-api, which serves no title above it; an admin has none
- Delete a person's account, with their data in the apps: their app data first, then the account, its invites and notifications; without the deletion token the app data stays
- Say what each person may do: which libraries, downloads, quality, casting: a person has a role and a rating cap, nothing finer
- See what was watched over time: by title, by person, by device: the apps send how playback went; no page shows it
- Send a person a mail: an invite, a reset link, a notice: the platform sends no mail; an invite link is handed over by hand

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `see-people` | — | `zaentrum-portal GET /api/portal/people` | `hidden-accounts`, `people-list-limit`, `invite-record-kept` |
| `add-person` | — | `zaentrum-portal POST /api/portal/people` | `user-role`, `username-length`, `person-name-length` |
| `invite-person` | — | `zaentrum-portal POST /api/portal/people/{id}/invite`, `zaentrum-portal POST /api/portal/people` | `invite-lifetime`, `invite-record-kept` |
| `accept-invite` | — | `zaentrum-portal GET /api/portal/invites/{token}`, `zaentrum-portal POST /api/portal/invites/{token}` | `invite-lifetime` |
| `change-person` | — | `zaentrum-portal PATCH /api/portal/people/{id}` | `user-role`, `person-name-length` |
| `cap-person-rating` | — | `zaentrum-portal POST /api/portal/people`, `zaentrum-portal PATCH /api/portal/people/{id}` | `rating-cap-range`, `unrated-for-capped` |
| `delete-person` | — | `zaentrum-portal DELETE /api/portal/people/{id}`, `chino-api DELETE /api/v1/admin/accounts/{sub}/data` | `admin-subjects` |
| `set-person-rights` | — | — | — |
| `limit-streams` | — | — | — |
| `see-who-is-watching` | — | — | — |
| `see-watch-statistics` | — | — | — |
| `mail-person` | — | — | — |
| `import-people-and-history` | — | — | — |

## Running the platform

Keeping it running: its parts, updates, checks, logs, events, its database, a support bundle, the first-run checklist. Not specified yet. Depth: deep.

| Capability | Who | Portal | CLI | Resource | Spec |
|---|---|---|---|---|---|
| See the platform's parts, their versions and readiness, and why one is unhealthy | admin | built | built | built | [cli](../../docs/extending/cli.md), [operator](../../docs/operator.md), [updating the operator](../../docs/updating-the-operator.md) |
| Scale a part of the platform up or down | admin | built | built | built | [cli](../../docs/extending/cli.md) |
| Restart a part of the platform | admin | built | built | — | [cli](../../docs/extending/cli.md) |
| Update the platform to the version its channel offers, by hand or by itself | admin | built | built | built | [operator](../../docs/operator.md), [cli](../../docs/extending/cli.md) |
| Have the platform verify itself, after each update or on request, and see its checks | admin | built | built | built | — |
| Check an instance from outside: its certificate, routes, sign-in, image pulls, commands | operator | — | built | — | — |
| Read a part's logs, credentials scrubbed, as they come or as a download | admin | built | built | — | — |
| Watch the event bus: its topics, their consumers and the latest events | admin | built | partial | — | — |
| Browse chosen tables of the platform's databases, read-only, secrets masked | admin | built | no | — | — |
| Download a support bundle for a bug report, credentials scrubbed | admin | built | built | — | — |
| Set up a fresh platform through a first-run checklist, and mark it done | admin | built | built | — | [First run](../portal/settings.md#first-run), [What an admin sees](../portal/home.md#what-an-admin-sees), [self hosting](../../docs/self-hosting.md) |
| Sign in with the CLI by a code in any browser, see who one is, sign out | operator | — | built | — | [cli](../../docs/extending/cli.md) |
| Report each service's liveness, readiness and metrics, and the API's description | system | — | — | — | — |
| Tell the admins when a part fails, a volume fills or a certificate nears its end | system | no | — | — | — |
| See how much room the library, its packages and the databases take, and what is free | admin | no | no | — | — |
| Choose the first administrator's name and password in the browser | admin | no | — | — | [First run](../../docs/self-hosting.md#first-run) |
| Update the operator itself, and the one-container install, from the portal or the CLI | admin | no | no | — | [updating the operator](../../docs/updating-the-operator.md) |
| Call the platform's APIs from a script with a token of one's own | admin | no | no | — | — |
| Tell another service when something happens: a title added, a title played | admin | no | — | — | [events](../../docs/extending/events.md) |

- See the platform's parts, their versions and readiness, and why one is unhealthy: the platform's, the addons' and unclaimed parts; the operator's controller shown, never updated; direct mode without operator
- Scale a part of the platform up or down: asked first; protected parts refused, the console's own keep one; a part the operator owns is scaled in spec.replicas
- Restart a part of the platform: asked first; refused for protected parts and console parts whose old pod stops first; pulls an always-pulled image again
- Update the platform to the version its channel offers, by hand or by itself: channel stable or edge, updates manual or auto; applying names the offered version and is refused if it changed
- Have the platform verify itself, after each update or on request, and see its checks: the operator runs zae doctor --sign-in as a test account and records each check; a waiting request is joined, not doubled
- Check an instance from outside: its certificate, routes, sign-in, image pulls, commands: each check ends in a fix line; --sign-in goes on as a person, read-only; --report writes one line of JSON
- Read a part's logs, credentials scrubbed, as they come or as a download: a pod and a container, a filter, live or downloaded; zae merges a workload's pods and follows them
- Watch the event bus: its topics, their consumers and the latest events: what passed since portal-api started, never a topic's history, scrubbed; zae lists events, no consumers, no live tail
- Browse chosen tables of the platform's databases, read-only, secrets masked: 7 tables: the catalog's items, status, steps and playback assets, the registry's apps, spaces and tiles
- Download a support bundle for a bug report, credentials scrubbed: logs, parts and operator state, the bus, the registry, settings; any section left out; the portal adds the browser's
- Set up a fresh platform through a first-run checklist, and mark it done: metadata key, library and a scan, media pipeline, https for devices, people; shown to admins until marked done; settings reopens it
- Sign in with the CLI by a code in any browser, see who one is, sign out: device grant with PKCE; a session per instance, renewed by itself; logout revokes it at the issuer; ZAE_TOKEN for scripts
- Report each service's liveness, readiness and metrics, and the API's description: for probes and scrapers; portal-api's own /healthz and /actuator/health/* are not in the inventory
- Tell the admins when a part fails, a volume fills or a certificate nears its end: the portal shows a part's state to whoever looks; nothing is sent
- Choose the first administrator's name and password in the browser: the first sign-in is admin, with a one-time password read from a secret of the cluster
- Update the operator itself, and the one-container install, from the portal or the CLI: a cluster admin applies each release's manifest; the one-container install is replaced
- Call the platform's APIs from a script with a token of one's own: the CLI signs in by a code in a browser; no token is issued to keep
- Tell another service when something happens: a title added, a title played: events are on the bus for addons; nothing calls an address outside

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `see-platform-parts` | — | `zaentrum-portal GET /api/portal/operator`, `platform`, `platform status` and 1 more | `parts-selector`, `operator-console-refresh`, `protected-parts`, `console-stack` |
| `scale-part` | — | `zaentrum-portal POST /api/portal/operator/instances/{name}/scale`, `platform scale`, `Zaentrum.spec.replicas` | `protected-parts`, `console-stack`, `replica-limit`, `platform-wait-timeout` |
| `restart-part` | — | `zaentrum-portal POST /api/portal/operator/instances/{name}/restart`, `platform restart` | `protected-parts`, `console-stack`, `platform-wait-timeout` |
| `update-platform` | — | `zaentrum-portal GET /api/portal/operator`, `zaentrum-portal PATCH /api/portal/operator`, `zaentrum-portal POST /api/portal/operator/apply-update` and 4 more | `platform-wait-timeout` |
| `verify-platform` | — | `zaentrum-portal POST /api/portal/operator/verify`, `zaentrum-portal GET /api/portal/operator`, `platform verify` and 2 more | `platform-wait-timeout`, `verification-switch`, `verification-account` |
| `check-instance-outside` | — | `doctor` | — |
| `read-logs` | — | `zaentrum-portal GET /api/portal/debug/pods`, `zaentrum-portal GET /api/portal/debug/logs`, `debug` and 1 more | `log-tail-lines`, `log-live-refresh` |
| `watch-events` | — | `zaentrum-portal GET /api/portal/debug/kafka/topology`, `zaentrum-portal GET /api/portal/debug/kafka/events`, `debug events` | `event-tail-size`, `event-live-refresh`, `event-payload-cap` |
| `browse-database` | — | `zaentrum-portal GET /api/portal/debug/db/tables`, `zaentrum-portal GET /api/portal/debug/db/rows` | `db-page-size`, `db-cell-length`, `db-query-timeout` |
| `download-support-bundle` | — | `zaentrum-portal GET /api/portal/debug/support-bundle`, `debug bundle` | `bundle-timeout` |
| `set-up-platform` | — | `zaentrum-portal GET /api/portal/setup`, `zaentrum-portal GET /api/portal/setup/complete`, `zaentrum-portal POST /api/portal/setup/complete` and 8 more | `stale-scan-age` |
| `sign-in-cli` | — | `login`, `logout`, `whoami` and 2 more | `cli-config-folder` |
| `report-health` | — | `* GET /healthz`, `* GET /readyz`, `* GET /metrics` and 4 more | — |
| `alert-admins` | — | — | — |
| `see-storage-use` | — | — | — |
| `create-first-admin` | — | — | — |
| `update-operator` | — | — | — |
| `use-personal-token` | — | — | — |
| `send-webhooks` | — | — | — |
<!-- end: areas -->
