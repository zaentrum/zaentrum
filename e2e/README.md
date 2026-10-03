# End-to-end tests

Playwright tests that use a running zaentrum instance the way a person does:
they sign in through its own Keycloak login page, browse the web client
(chino), open titles in the catalog console, and call chino-api with the token
the signed-in web client holds. They run against the public demo,
**`https://zaentrum.demo.nalet.cloud`**, by default — and against any instance
that holds the same open-licensed titles.

They exist so a UI change can be built on the demo and checked there: the
baseline says nothing else broke, a spec per planned change says when the
change is done, and every run's report is a gallery of each page as it looked.

**The tests never change the instance they run against.** Every browser
context goes through a guard ([`support/readonly.ts`](support/readonly.ts))
that lets reads through and, of the writes, only those that change nothing:
the Keycloak login form, the OIDC token exchange, the short-lived artwork token
chino-api mints, and GraphQL *queries*. Anything else — marking a title
watched, adding it to a list, a bug report the app would file on its own, a
console mutation, signing out of the shared session — is aborted in the browser
and listed on the test as a `blocked write`. The console tests only ever click
a title and a tab.

## Running them

You need Node 20 or newer and two accounts on the instance (below).

```bash
cd e2e
npm ci
npx playwright install chromium     # once: the browser Playwright 1.63 drives

set -a; . ./e2e.env; set +a          # or: export the variables one by one
npm test                             # the baseline
npm run report                       # the HTML report: results and screenshots
```

`e2e.env` is a plain `KEY=VALUE` file that never belongs in git (`*.env` and
`.env` are ignored here). Instead of sourcing it you can point the suite at it
— `E2E_ENV_FILE=/path/to/e2e.env npm test` — or keep it as `e2e/.env`, which is
read when present. A variable set in the environment wins over the file.

Credentials are read from the environment only. The suite never prints them,
and the login form gets them through a page binding rather than as arguments of
Playwright calls, because those are written into the report's steps.

| Variable | What it is |
|---|---|
| `E2E_BASE_URL` | Origin of the instance. Default `https://zaentrum.demo.nalet.cloud`. |
| `E2E_USER`, `E2E_PASSWORD` | An ordinary account — a viewer, without the admin role. |
| `E2E_ADMIN_USER`, `E2E_ADMIN_PASSWORD` | An administrator. The catalog console and launchpad tests run as this account. |
| `E2E_ENV_FILE` | A `KEY=VALUE` file to read the variables from. |
| `E2E_CHINO_PATH` | Where the web client is mounted. Default `/chino/`. |
| `E2E_CONSOLE_PATH` | Where the catalog console (browse mode) is mounted. Default `/katalog/`. |
| `E2E_PORTAL_PATH` | Where the portal launchpad is mounted. Default `/portal/`. |
| `E2E_WORKERS` | Parallel workers. Default `2` — the demo is a small cluster. |
| `E2E_RETRIES` | Retries per test. Default `0`: a test that needs one is reported, not hidden. |
| `E2E_NEXT` | `1` includes the `@next` tests. |
| `E2E_FIXME` | `run` runs the assertions of the UI-change specs instead of stopping before them. |

The issuer and the OIDC client ids are not configured here: the suite reads
them from the instance's `GET /api/config`, as every client does. Both accounts
have to be able to sign in without a pending required action (a temporary
password, a profile to complete): the setup project names the one Keycloak asks
for and stops, since completing it would change the account.

## What runs

| Project | Account | What it covers |
|---|---|---|
| `setup` | both | Signs each account in once through the Keycloak login page and saves the signed-in browser state to `e2e/.auth/` (ignored by git, readable by you only). Every other project depends on it. |
| `chino` | viewer | The web client: home and the movies page with posters, a movie's and a series' detail page with their credits, seasons and episodes, the person page, search for titles and for people. |
| `api` | viewer | chino-api as the pages call it: cast entries, episodes, people search and person pages, posters; the data set; that the viewer is no administrator. |
| `console` | admin | The catalog console: find a title, open it, read its cast tab, its poster loads; a person's record lists their credits, each linking back; the launchpad links the apps where the suite expects them; the operator console shows the platform's last check of itself, passed. |
| `ui-changes` | viewer, admin | One spec per UI change: built ones guard the change, planned ones stop at `notYet()` (below). |

`npx playwright test --project=chino` runs one project, `npx playwright test
tests/chino/search.spec.ts` one file, `--grep "person page"` the tests whose
title matches.

**`@next`** marks the contract of a backend round that is not deployed yet: the
default run leaves such tests out, `npm run test:next` runs them (and the setup
they depend on), and once the round is live they lose the tag and join the
default run — as the credits and people contract did
([`tests/api/credits-people.spec.ts`](tests/api/credits-people.spec.ts)).
None is tagged today.

**A known product bug** goes into the baseline as an expected failure,
`test.fail()` with the reason, so the run stays green while the bug stands and
turns red once it is fixed, until the marker is removed. None is marked today:
the last one (a cast name on a detail page linked outside the app's mount
path) was fixed in chino-web e153a47.

## The report as a gallery

Every UI test attaches a full-page screenshot of the moment it checks — inner
scroll containers included, so a whole page shows, not one screen of it — and
the API tests attach the responses they checked. Run the suite before a change and
after it, keep both reports (`npx playwright show-report <folder>`), and the two
show the change page by page. The signed-in account's name is masked in every
capture. Nothing compares pixels: the data on a live instance moves.

## The data set

[`data/catalog.ts`](data/catalog.ts) holds the titles and people the tests rely
on — Sintel, Tears of Steel, Spring, HERO, Agent 327, the series Pioneer One;
the director Colin Levy, the actor Thom Hoffman — with what TMDB publishes
about them. It holds names, not ids: tests look titles and people up at run
time, so the suite works against any catalog with the same titles.
[`tests/api/catalog-data.spec.ts`](tests/api/catalog-data.spec.ts) checks the
data set against the instance; when a UI test fails on a missing title, read
that one first.

## Implementing a UI change

[`tests/ui-changes.spec.ts`](tests/ui-changes.spec.ts) holds one spec per
planned change, each titled with what it will check and holding the assertion
already. Each opens its page, attaches a screenshot, and stops at `notYet(…)`
(from [`support/fixtures.ts`](support/fixtures.ts)) — a runtime `test.fixme()` —
so a default run reports it as skipped and still shows the page as it is today.
The first fourteen, the web client's and the console's credits and people, are
built and guard their changes now; a new planned change starts there again.

1. Run the suite before the change and keep the report: the "before" pictures.
2. Build the change and deploy it to the instance the usual way (nothing in
   this suite deploys anything).
3. `npm run test:ui-changes` runs the assertions of every UI-change spec;
   iterate until the one for your change passes.
4. Delete its `notYet(…)` line. From then on it runs in the default run and
   keeps the change from regressing; move it next to the other tests of its
   page if you like.
5. `npm test`: the baseline still passes, and the report has the "after"
   pictures. Commit.

A new test uses `test` and `expect` from
[`support/fixtures.ts`](support/fixtures.ts), not from `@playwright/test`, so
the read-only guard applies. It opens a page with `open(app, path)` (which makes
sure the session is live first), finds the titles it needs with
`findTitle(api, SINTEL)` and the people with `findPerson(api, name)`, calls
`snap(name)` at the moment worth looking at, and adds any new fact it relies on
to `data/catalog.ts`.

## In CI

[`.github/workflows/e2e.yml`](../.github/workflows/e2e.yml) is started by hand
(Actions → e2e → Run workflow) and asks which set to run: the baseline, the
`@next` contract, or the UI-change specs' assertions. It reads the repository
secrets `E2E_USER`, `E2E_PASSWORD`, `E2E_ADMIN_USER` and `E2E_ADMIN_PASSWORD`
and the repository variable `E2E_BASE_URL` (unset: the public demo); without
the secrets it skips with a notice. It uploads the HTML report as an artifact.
A report from CI keeps no traces, which carry bearer tokens, and no page
snapshot of a failure, which carries the text on screen.

## When it fails before testing anything

- *Keycloak refused the viewer account* — the credentials are wrong.
- *Keycloak asks the … account for a required action* — sign in by hand once
  and complete it.
- *… sent the browser to the Keycloak login form* — the session the setup saved
  has ended; run again.
- *… is not in the catalog of …* — the library changed; see the data set tests.
