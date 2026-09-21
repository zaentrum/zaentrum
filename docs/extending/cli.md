# The CLI capability contract — extending `zae`

[`zae`](https://github.com/zaentrum/zae) is the zaentrum CLI. Its design rule:
**the binary compiles in no service names.** A static core (doctor, preflight,
[installing addons](#installing-addons-zae-addon),
[driving the platform](#driving-the-platform-zae-platform)) works when the
platform cannot speak for itself; everything else is a surface the instance
*declares*. Installing an addon extends the CLI on that instance; uninstalling
it leaves no trace.

## How discovery works

1. Any service or addon MAY serve a **capability descriptor** at
   `/.well-known/zaentrum-capability.json` on its own origin. It is metadata,
   served unauthenticated (like `/healthz`), versioned with the service image —
   a deployed service declares its own surface, so the CLI can never describe
   an unshipped platform.
2. portal-api aggregates: `GET /api/portal/cli/discovery` fans out to every
   workload the platform knows — the operator console's instance list
   (platform services) and the app registry's proxy URLs (addons) — and
   returns one document. **Installing an addon is what registers its CLI
   surface** — the install creates the app with its proxy URL. Candidates
   never come from the request, which is what keeps a fanning-out endpoint
   SSRF-proof.
3. `zae discover --url https://…` renders the document; `zae doctor` reports
   how many services declare capabilities.

The aggregate document also says **where a CLI signs in**, because a CLI
cannot guess it:

```json
{
  "capabilityVersion": 1,
  "auth": {
    "issuer": "https://media.example.org/auth/realms/zaentrum",
    "clientId": "zae"
  },
  "services": [ … ]
}
```

- `auth.issuer` — the issuer this instance validates bearers against.
- `auth.clientId` — the OIDC client a CLI should sign in as. portal-api reads
  it from `PORTAL_CLI_CLIENT_ID` (default `zae`), so an operator who registered
  the client under another name points that at it.

`auth` is absent when there is nothing to sign in to: no issuer configured, or
auth disabled. That is also what an instance that predates the field looks
like, and `zae login` says so and asks for `--issuer` and `--client-id`
instead. `capabilityVersion` stays `1`: nothing a v1 client already reads
changed shape, and a client that does not know `auth` ignores it.

## Descriptor schema (v1)

```json
{
  "service": "acquire",
  "kind": "addon",
  "version": "1.2.3",
  "commands": [
    { "name": "wanted", "summary": "list requests and their state",
      "method": "GET", "path": "/api/wanted", "role": "user" }
  ],
  "checks": [
    { "name": "system", "path": "/api/health/system" }
  ],
  "topics": ["download.client.completed"],
  "ui": {
    "app": { "title": "acquire", "description": "requests and downloads", "icon": "download" },
    "console": true,
    "space": { "key": "acquire", "title": "acquire", "ord": 30 },
    "tiles": [
      { "key": "requests", "title": "requests", "description": "who asked for what",
        "icon": "download", "target": "#/requests", "ord": 10 }
    ],
    "slots": [
      { "key": "search-request", "slot": "search.empty", "kind": "link",
        "label": "Request this", "icon": "download",
        "url": "/portal/app/acquire?q={q}#/discover", "ord": 10 }
    ]
  }
}
```

- `service` — required; a descriptor that cannot name itself is dropped.
- `kind` — `platform` or `addon`.
- `proxyKey` — optional; the app-registry key the service is reached under
  through the portal proxy, when it differs from `service` (see
  [below](#reaching-a-command-from-outside)).
- `commands[]` — a curated surface, not a route dump. `path` is
  **service-relative**; `role` lets the CLI hide or fail early, but the API
  enforces authorization regardless of what the descriptor claims.
- `checks[]` — GET endpoints returning structured check results, for
  `doctor`. Prefer making these unauthenticated the way acquire's
  `/api/health/system` is: a health surface that needs working auth is useless
  exactly when auth is what broke.
- `topics[]` — event topics the service emits (logical names; the tenant
  prefix is instance configuration).
- `ui` — optional; what the addon contributes to the portal and product apps.
  The CLI ignores it. The platform reads it when an admin
  [installs the addon](./installing.md): `app` names the portal app,
  `console: true` places a tile for the [hosted console](./console.md),
  `space` and `tiles[]` place a curated set of entry points instead,
  `slots[]` become [slot rows](./slots.md). One manifest declares the whole
  addon.
- `components[]` and `setup` — optional; the containers the addon consists of
  and where its configuration state is reported. The CLI ignores both; the
  platform reads them on install. See
  [components and setup](#components-and-setup).

**Descriptors are data, never code.** Nothing an instance serves executes in
anyone's terminal. The worst a descriptor can do is describe an HTTP call the
CLI then makes with the caller's own token against the instance's own APIs —
no new surface beyond what those APIs already gate.

## Components and setup

An addon is usually more than one container: the service that serves this
descriptor and the console, plus workers or gateways next to it. It is also
rarely useful the moment it starts — it needs configuration an admin enters
afterwards. Two optional sections say both, so the platform can show whether
an addon is *running* and whether it is *configured* without learning
anything else about it ([ADR-0010](../adr/0010-addon-component-groups-and-setup.md)).

```json
{
  "service": "example",
  "kind": "addon",
  "version": "0.4.0",
  "commands": [
    { "name": "setup", "summary": "what still needs configuring",
      "method": "GET", "path": "/api/setup", "role": "admin" }
  ],
  "topics": ["example.job.scheduled"],
  "components": [
    { "name": "example", "workload": "example", "role": "primary",
      "summary": "console, API and setup" },
    { "name": "worker", "workload": "example-worker", "role": "required",
      "summary": "runs jobs against the external service",
      "topics": ["example.job.finished"] }
  ],
  "setup": {
    "path": "/api/setup",
    "sections": [
      { "key": "connection", "title": "connection",
        "description": "the external service the worker calls",
        "required": true, "target": "#/settings/connection", "ord": 10 },
      { "key": "schedule", "title": "schedule",
        "description": "when jobs run",
        "required": false, "target": "#/settings/schedule", "ord": 20 }
    ]
  },
  "ui": { "app": { "title": "example" }, "console": true }
}
```

`components[]` — at most 16:

| Field | Rule |
|---|---|
| `name` | A DNS-1123 label (lowercase letters, digits and `-`), unique in the manifest |
| `workload` | A DNS-1123 label, no dots: the name of the **Deployment and the Service** in the addon's namespace, unique in the manifest. One workload has one owner — see [installing](./installing.md#what-install-refuses) |
| `role` | `primary` — exactly one; it serves this descriptor, and its `workload` equals the host of the address the addon is installed from. `required` — the addon does not work without it. `optional` — the addon works without it, with less |
| `summary` | Plain text, at most 120 characters |
| `topics` | Event topics this component emits, each under the component that emits it. Top-level `topics[]` stay what the primary emits, so the primary's `topics` may repeat them |

A manifest without `components` is a group of one:
`[{"name": <service>, "workload": <install host>, "role": "primary"}]`.
Nothing changes for an addon that is a single container. That implicit
component follows the same rules as a declared one, so `service` must then be
a DNS-1123 label. Either way the install address names the primary's Service:
its host is a DNS-1123 label (or starts with one, as in
`example.ns.svc.cluster.local`), never an IP address.

`setup` — optional; at most 16 sections:

| Field | Rule |
|---|---|
| `path` | A GET route on the primary, relative: starts with `/`, no `//`, no `..` — spelled out or percent-encoded (`%2e%2e`, `.%2e`) — no `\` or encoded `/` or `\`, no scheme or host, no `#` fragment, spaces or control characters. A query is allowed |
| `sections[].key` | A DNS-1123 label; the status document reports the section under this key |
| `sections[].title` | At most 60 characters |
| `sections[].description` | One line saying what the section covers |
| `sections[].required` | Whether the section counts toward the addon's overall state |
| `sections[].target` | Where **configure** opens the addon's console — the same rule as a [tile target](./installing.md#declaring-a-layout-not-just-a-console): a hash route or path inside the console, never another origin |
| `sections[].ord` | Order in the checklist |

Install refuses a manifest that breaks these rules and says which one.

### The setup status document

`GET {setup.path}` answers with the state of each declared section. The
portal calls it from the admin's browser, through the
[portal proxy](#reaching-a-command-from-outside), with the admin's own bearer:

```json
{
  "state": "needs-setup",
  "sections": [
    { "key": "connection", "state": "needs-setup", "summary": "no external service configured yet" },
    { "key": "schedule",   "state": "ready",       "summary": "every 30 minutes" }
  ]
}
```

- A section's `state` is one of `ready` (nothing to do), `degraded`
  (configured, but not working as configured — unreachable, rejected, not
  applied yet) and `needs-setup` (not configured enough to work).
- The top-level `state` is the worst state among the **required** sections, in
  the order `ready` < `degraded` < `needs-setup`. Optional sections are shown
  and never lower it.
- Report every section the manifest declares, under its `key`.
- `summary` is plain text of at most 200 characters, rendered as text. Say
  what is configured and what is wrong — *2 endpoints, 1 unreachable* — never a
  value: no credential, no URL that carries one.
- Gate the route on the admin role; a checklist names what is missing, which
  is not every user's business. Answer fast — the portal asks whenever an
  admin looks at settings → addons — so bound slow checks with short
  timeouts.
- When the call fails, is refused or returns something else, the portal shows
  the checklist as **unknown**. It never infers a state.

Declaring the same path as a command, as above, lets `zae` show the checklist
too. What an addon behind a `setup` section should look like — write-only
secrets, encryption at rest, the endpoint itself — is
[configuration](./configuration.md).

## Reaching a command from outside

Descriptor paths are service-relative. From outside the cluster, `zae` reaches
them through the portal's app proxy: `/api/portal/apps/<key>/<path>`, where
`<key>` is the service's app-registry key — by default its `service` name; a
descriptor may set `proxyKey` when they differ. So an addon that wants CLI
commands needs to be [installed](./installing.md) — which registers its app
with a `proxyUrl` — and nothing else: no route, no origin.

## Signing in — `zae login`

```sh
zae login --url https://media.example.org
```

The grant is the **OAuth 2.0 Device Authorization Grant**
([RFC 8628](https://www.rfc-editor.org/rfc/rfc8628)) with
[PKCE](https://www.rfc-editor.org/rfc/rfc7636). A CLI is a public client: it
cannot keep a secret, and it cannot receive a browser redirect. The device
grant is the one flow designed for exactly that — the terminal prints a URL
and a user code, and a browser, which need not be on the same machine, does
the signing in. That is what makes it work over ssh, in a container and on a
server with no desktop.

What happens, in order:

1. `zae` fetches `/api/portal/cli/discovery` and takes `auth.issuer` and
   `auth.clientId` from it ([above](#how-discovery-works)). `--issuer` and
   `--client-id` override them, and are required against an instance that
   advertises neither.
2. It reads the issuer's `/.well-known/openid-configuration` for
   `device_authorization_endpoint` and `token_endpoint`. **Endpoints are read,
   never built**: a realm may be served under a path prefix, and its endpoints
   are wherever that document says. An issuer that advertises no device
   endpoint fails with exit `3`, naming what an operator must enable.
3. It posts `client_id`, `scope`, and a **PKCE** `code_challenge` with
   `code_challenge_method=S256` to the device endpoint, prints the
   verification URL and the user code — `verification_uri_complete` when the
   provider offers one, since it already carries the code — and opens a
   browser unless `--no-browser` is given. A missing opener never fails a
   login; the URL is on the screen either way.
4. It polls the token endpoint with `grant_type=urn:ietf:params:oauth:grant-type:device_code`,
   the device code and the PKCE `code_verifier`, at the interval the provider
   set, honouring `slow_down` (add five seconds and keep it),
   `authorization_pending`, `expired_token` and `access_denied`. Ctrl-C stops
   the poll where it stands and stores nothing.
5. It stores the session and prints who you are — and whether your token
   carries the admin role. A login that succeeds *without* the role says so
   there, rather than three commands later.

The PKCE challenge goes out on every device request. An identity provider
whose client requires S256 refuses a request without it; one that does not
require it is unharmed by receiving it.

| command | does |
|---|---|
| `zae login --url …` | signs in and stores the session. `--no-browser`, `--issuer`, `--client-id`, `--scope` (default `openid`) |
| `zae logout --url …` | forgets that instance's session; `--all` removes the file |
| `zae whoami --url …` | subject, username, and whether the token carries the platform's admin role (`--role` names another) — never the token itself |

### What is stored, and where

`~/.config/zae/credentials.json` — `$XDG_CONFIG_HOME/zae/credentials.json`
when that is set — mode `0600` inside a `0700` directory, written through a
temporary file in the same directory so a crash mid-write cannot leave a
half-parsed file where credentials were.

It is keyed by **instance URL**: a session at one instance is worthless at
another and must never travel there. Each entry holds the access token, the
refresh token, the expiry, the issuer and the client id.

Which bearer a command sends, in order:

1. **`ZAE_TOKEN`**, when set — a bearer minted elsewhere (a service account's
   client-credentials token, a CI secret). It wins on purpose: a script that
   sets it is naming the identity it means, and a developer's own login must
   not quietly override it.
2. The **stored session** for that instance, renewed with its refresh token
   when it has expired and written back — so one expiry costs one extra round
   trip, not one per command.

A renewal that fails is a session that ended: `zae` says *session expired —
run: zae login --url …* and exits `5` rather than sending a token it knows is
dead. A token that is real and still refused gets different words, because it
needs a different fix — signing in again with the same account does nothing
about a missing role.

**Tokens are never printed** — not by `login`, not by `whoami`, not in an
error message. It is the one rule that keeps them out of scrollback, CI logs
and pasted bug reports.

### What an operator must configure

The platform does not create the CLI's client. One public client on the
instance's realm, which every CLI user on that instance shares:

```json
{
  "clientId": "zae",
  "name": "zae CLI",
  "description": "The zaentrum CLI — device grant, public client",
  "protocol": "openid-connect",
  "enabled": true,
  "publicClient": true,
  "standardFlowEnabled": true,
  "implicitFlowEnabled": false,
  "directAccessGrantsEnabled": false,
  "serviceAccountsEnabled": false,
  "fullScopeAllowed": true,
  "attributes": {
    "oauth2.device.authorization.grant.enabled": "true",
    "pkce.code.challenge.method": "S256"
  },
  "redirectUris": [
    "http://localhost/*",
    "http://127.0.0.1/*"
  ],
  "webOrigins": []
}
```

Why each line is there:

- **`publicClient: true`** — a CLI on someone's laptop cannot hold a secret.
  A confidential client would put one in every user's shell history.
- **`oauth2.device.authorization.grant.enabled`** — the flow itself. Without
  it the realm advertises no `device_authorization_endpoint`, and `zae login`
  exits `3` saying so.
- **`pkce.code.challenge.method: "S256"`** — proof of possession for a client
  with no secret. `zae` always sends the challenge, so requiring it costs
  nothing and closes the gap for anything else using this client.
- **`fullScopeAllowed: true`** — the point of the whole exercise: the access
  token must carry the user's **realm roles** in `realm_access.roles`, or the
  platform admin role never reaches portal-api and every admin command answers
  `403`. (The `roles` client scope, assigned by default, is what puts them
  there; full scope is what stops them being filtered out.)
- **`standardFlowEnabled` with loopback `redirectUris`** — not used today:
  `zae` speaks only the device grant. They are here so a browser-redirect
  fallback can be added later without an operator touching the realm again.
  Loopback addresses only, never a public origin.
- **`serviceAccountsEnabled: false`** — this client is how *people* sign in.
  An addon that needs to act on its own behalf gets a confidential client
  instead; see [addon identity](./identity.md).

Then, per person: the platform admin role — `zaentrum-admin` by default,
`PORTAL_ADMIN_ROLE` on portal-api — assigned to the users who administer the
instance. `zae whoami --url …` shows whether it reached the token.

To use another client id, set `PORTAL_CLI_CLIENT_ID` on portal-api (it is what
the discovery document advertises) or pass `--client-id` per command.

## Exit codes — the scripting contract

A dynamic surface creates a failure mode static CLIs never had: a command can
vanish between two runs of the same script because the **instance** changed.
`zae` therefore distinguishes, by exit code, "the invocation is malformed",
"this instance definitively does not offer that", and "zae could not find
out" — the last two demand opposite reactions from a script. These are
stable and part of this contract:

| exit | meaning |
|---|---|
| `0` | ran |
| `1` | ran; the instance returned an error |
| `2` | usage — malformed invocation, missing `--url`, a placeholder not supplied |
| `3` | **not offered** — discovery answered and the instance declares no such service or command |
| `4` | **undetermined** — discovery unreachable, or the instance predates it; do **not** conclude the command is gone |
| `5` | declared, but the instance refused the caller (401/403) |
| `6` | the instance speaks a newer capability schema than the binary |

`zae require <service>[.<command>] --url …` answers with `0`/`3`/`4`/`6` and
prints nothing on stdout, so scripts assert prerequisites before doing work.
A `404` during execution triggers one re-discovery and is reclassified as `3`
if the command is now absent.

Authentication is [`zae login`](#signing-in--zae-login). A bearer in
`ZAE_TOKEN` (for example an addon service account's client-credentials token)
is still sent as-is, and still wins over a stored session.

## Installing addons: `zae addon`

Installing is how an addon reaches an instance, so no addon can declare the
command that does it: `zae addon` is part of the static core. It drives
portal-api's [chart API](./charts.md#4-installing-from-settings) with the
caller's admin bearer — from [`zae login`](#signing-in--zae-login) or
`ZAE_TOKEN` — waits for the plan the operator made for its own write, and
prints that plan before anything is installed ([addon charts](./charts.md)).

```sh
zae login --url https://media.example.org
zae addon add oci://ghcr.io/example/charts/example --version 1.2.0 \
  --url https://media.example.org --set worker.replicas=2 --set-secret database.url
```

| Command | Does |
|---|---|
| `zae addon add <chart> --url …` | Creates the addon suspended, waits for the plan of that write and prints it — chart, workloads with images and ports, objects, violations, values errors, and the inputs: secret ones only as *set* or *missing*, generated ones as *generated* — asks, installs |
| `zae addon list --url …` | Every installed addon, from a chart or from an address: source, the version asked for next to the one running, phase, ready components |
| `zae addon status <name> --url …` | Phase, the chart asked for and the one running, registration, components and the current plan |
| `zae addon upgrade <name> --url …` | Changes the chart (`--version`, `--chart`, `--digest`), values (`--set` over the current values, `--values` in their place) or secret inputs (the secret flags below, `--clear-secret`). It always plans first, prints the changes, asks, installs |
| `zae addon remove <name> --url …` | Deletes the addon and everything its chart applied; `--keep-values` keeps its values Secrets and its generated values for a later install |

| Flag | Meaning |
|---|---|
| `<chart>` | `oci://registry/path/chart` with `--version` or a `:tag`, or an `https://` link to a chart archive. A digest belongs in `--digest`, not in the reference |
| `--name` | The addon's name (`add`) — it must be the manifest's `service`. By default the reference's last segment without tag, extension or `-<version>`, lower-cased, exactly as the portal derives it |
| `--version`, `--digest` | The chart's tag; the `sha256:` the chart archive must match |
| `--values FILE`, `--values -` | One JSON object of values, from a file or from stdin |
| `--set path=value` | One value at a dotted path. JSON when it parses as JSON — `2`, `true`, `["a"]` — and the text as a string otherwise; quoting forces a string: `--set 'image.tag="1.10"'` |
| `--set-secret path` | A secret input, asked for on the terminal without echo |
| `--set-secret-file path=FILE` | A secret input read from a file, one trailing newline trimmed |
| `--secret-values FILE`, `--secret-values -` | Secret inputs as one JSON object of dotted path to string |
| `--set-secret path=value` | A secret input given on the command line — visible to other local users in the process list, and kept in shell history |
| `--secret-ref path=name[/key]` | A secret input read from a values Secret the addon kept (`add`); the key defaults to the path |
| `--clear-secret path` | Remove a secret input (`upgrade`) |
| `--yes` | Do it without asking |
| `--wait`, `--timeout` | Follow the install until the addon is Ready and registered; each wait — for the plan, for Ready — lasts at most `--timeout`, default `5m` |
| `--json` | Print the portal's answer as JSON (`list`, `status`) |

Secret inputs are stored in a values Secret and never shown again. They are
added to the ones already set; a path longer than 250 characters, or an empty
value, is refused.

What makes it safe to script:

- **A blocked plan is never installed.** Violations or values errors exit `1`,
  with `--yes` too, and the plan names the required inputs still missing.
- **The plan is the one for zae's write.** Every write answers with a
  generation; zae waits until the operator has planned exactly that one, and
  stops with `1` when someone else changes the addon meanwhile.
- **zae asks only a person.** `add`, `upgrade` and `remove` ask on stdin, and so
  does `--set-secret path`. Without a terminal there they need `--yes` (and a
  secret from a file). Stdin cannot carry a document and an answer, or two
  documents. Each of these exits `2` before anything is written.
- **An upgrade puts back what it does not install.** Refused, declined, no plan
  in time, Ctrl-C or SIGTERM: zae re-reads the addon and restores the chart
  reference, version, digest, values and suspension it read before writing —
  unless someone else changed the addon since. Secret inputs cannot be put
  back, since zae never reads them; it names the ones that stay as written.
- **Values are JSON.** `zae` uses only the standard library and does not parse
  YAML: a partial parser would disagree with Helm about what `yes`, `on` or
  `0755` mean. JSON is valid YAML, so the same file works with Helm; convert a
  YAML file first, for example with `yq -o=json values.yaml`.
- **Exit codes** are the contract above: `0` done; `1` refused, failed,
  declined, changed by someone else, or not Ready and registered within
  `--timeout`; `2` usage; `3` no such addon, or an instance that cannot install
  addons from charts — a portal-api without the API, a cluster without the
  `ZaentrumAddon` resource; `4` the instance could not be reached; `5` the
  bearer is missing or lacks the admin role; `130` or `143` interrupted.

## Driving the platform: `zae platform`

The platform's own version is what every declared command runs on top of, so
no declared command can change it: `zae platform` is part of the static core
too. It drives the portal's **operator console** — the admin API behind
settings → instances — with the caller's admin bearer, and it changes exactly
what the console changes: the operator's own resource, and the replica count
or rollout of one workload.

```sh
zae login --url https://media.example.org
zae platform status --url https://media.example.org
zae platform update --apply --wait --url https://media.example.org
```

```
$ zae platform status --url https://media.example.org
https://media.example.org — the platform
  version      1.4.0 — pinned
  channel      stable
  update mode  manual — an update is applied when someone asks for it
  phase        Ready
  running      1.4.0
  update       1.5.0 available — apply it with: zae platform update --apply --url https://media.example.org
  host         media.example.org

NAME            GROUP          IMAGE                READY  PHASE     REASON
chino-api       platform       1.4.0                2/2    ready     -
katalog-api     platform       sha256:aaaaaaaaaaaa  0/1    degraded  ImagePullBackOff
postgres        platform       16                   1/1    ready     -
example-worker  addon:example  2.0.0                1/1    ready     -
leftover        other          latest               1/1    ready     -

Not covered here: the operator's own controller image. …

$ zae platform update --apply --wait --url https://media.example.org
https://media.example.org — the platform
  version      1.4.0 → 1.5.0
  rolls        3 workloads the operator manages
apply this to https://media.example.org? [y/N] y
waiting for the platform to report 1.5.0, and every workload the operator manages to be ready (timeout 10m)
  Reconciling  1.4.0 · 2/3 ready — the operator has not reconciled this change yet (at 7, waiting for 8); waiting for 1.5.0
  Reconciling  1.5.0 · 2/3 ready — katalog-api 0/1 progressing
  Ready        1.5.0 · 3/3 ready
the platform reports 1.5.0, and every workload the operator manages is ready
```

| Command | Does |
|---|---|
| `zae platform status --url …` | The version the platform is pinned to — or that nothing is pinned and it follows a channel — the channel, the update mode, the phase, the version it reports running, and whether an update is offered; then every workload it can see, grouped: what the operator renders first, addons after them, and whatever neither claims last |
| `zae platform update --url …` | Changes what the platform asks for: `--version V` pins an image tag (`--version latest` follows the channel again), `--channel C` picks the release train, `--mode auto\|manual` decides whether the operator applies in-channel updates by itself, `--apply` pins the update it has already discovered |
| `zae platform restart <workload> --url …` | Rolls one workload |
| `zae platform scale <workload> <replicas> --url …` | Sets one workload's replica count |

| Flag | Meaning |
|---|---|
| `--version`, `--channel`, `--mode` | What the operator's resource should say. Only what is passed is sent; `--version ""` takes the pin off |
| `--apply` | Pin the platform to the update the operator discovered — `status.availableUpdate`. It takes no version of its own |
| `--yes` | Do it without asking |
| `--wait`, `--timeout` | Follow the rollout; each wait lasts at most `--timeout`, default `10m` |
| `--json` | Print the portal's own answer, unchanged (`status`) |

The three columns of the workload table that are not obvious: **GROUP** is how
an administrator has to reason about the workload — `platform` (the operator
renders it, so a platform update rolls it), `addon:<key>` (its own repo, its
own lifecycle, its own version) and `other` (running here, claimed by neither,
which is exactly why it is worth seeing); **IMAGE** is the tag, or the head of
the digest when the reference is pinned by digest; **REASON** is the cluster's
own words for why a workload is not healthy, because "degraded" is not
actionable and *cannot pull the image* is.

### How a wait is exact

A restart on the demo once reported *ready* eight seconds after it was asked
for, while the pod that was ready was the one from **before** it. Nothing was
lying: `readyReplicas`, `updatedReplicas` and `availableReplicas` describe
whatever pods exist, and for the first seconds of a rollout those are the
previous ones — every field true, the conclusion false. It is the same
mechanism that hid a 36-hour outage behind a green *ready* badge, one layer
down.

So the console reports, and every write returns, what Kubernetes itself uses
to answer the question:

| Field | On | Means |
|---|---|---|
| `generation` | each workload, and the operator's resource | how many times the spec has changed |
| `observedGeneration` | the same two | which of those the controller has acted on |
| `restartedAt` | each workload | the rollout-restart stamp, `""` when there is none |

`POST …/instances/{name}/{scale,restart}` answers `200` with
`{"name", "generation", "restartedAt"}`, and `PATCH /operator` and
`POST /operator/apply-update` answer `200` with `{"version", "generation"}` —
the generation *that write* produced. `zae platform … --wait` then waits until:

- **restart** — the workload's `observedGeneration` has reached that
  generation, its `restartedAt` has moved off the one from before, and then
  `updatedReplicas == desiredReplicas` with ready and available at or above it;
- **scale** — the same gate, plus the replica count that was asked for;
- **update** — the operator has reconciled the resource generation the write
  made, reports the new version as `currentVersion`, and every workload it
  manages has settled the same way.

Two further contract points, both about telling states apart that used to look
alike. A workload the namespace does not run answers `404`, not `400`: absent
and refused need opposite reactions, and only one of them means *fix the name*
(a protected workload keeps its `400` and its reason). And `apply-update`
accepts an optional `{"version": "…"}` — the update the caller decided on — and
answers `409` when the operator has discovered another one since, naming what
is on the shelf now.

Against a portal-api that predates these fields, `zae` keeps working: the wait
falls back to the readiness gate it had before, and says so in one line. That
line matters more than the fallback — a wait that quietly gets weaker is how
the original bug stayed invisible.

### What `zae platform` does not cover

**The operator's own controller image.** The controller runs in
`zaentrum-operator-system`, outside the namespace the portal administers and
outside its permissions, so `zae` can neither read nor change the version of
the controller itself. Updating the controller means applying its install
bundle — or going through OLM, on a cluster that installs it that way; see
[running with the operator](../operator.md#updating-from-the-command-line).
`zae platform` updates the platform that controller *deploys*, which is the
other half of the same job and the half that happens far more often.

What makes it safe to script:

- **The change is printed before it is made,** and `update`, `restart` and
  `scale` ask on stdin. Without a terminal there they need `--yes` and exit
  `2` before anything is written.
- **`--apply` refuses to race a channel change.** The update on the shelf was
  discovered on the channel the platform follows *now*, so `--apply --channel C`
  is a usage error, and so is `--apply --version V`: pinning what was found and
  pinning what you name are two different instructions. When nothing has been
  discovered, `--apply` says so and writes nothing. The request also carries
  the version zae showed you, so an update that moved in between is refused by
  the platform (`409` → exit `1`) rather than applied.
- **Protected workloads are refused by the platform.** The stateful services it
  keeps out of reach are refused by the API, in the API's own words, and zae
  prints that reason and exits `1`. The rule lives on one side only.
- **`--wait` follows the rollout the write produced,** and exits `1` on timeout
  naming what was still not ready. See
  [how a wait is exact](#how-a-wait-is-exact).
- **Exit codes** are the contract above: `0` done; `1` the platform refused it,
  the change was declined, or it was not ready within `--timeout`; `2` usage;
  `3` this instance has no operator console — portal-api is not running where
  it can manage workloads, or there is no operator resource — or no workload
  has that name; `4` the instance could not be reached; `5` the bearer is
  missing or lacks the admin role.

## Rules for a good descriptor

- **Declare only what is routed.** Put the drift-killer in your tests:
  acquire's `capability_test.go` walks its router and fails the build if the
  descriptor names a command the router does not serve, with the declared
  method. Copy that pattern; it is the whole reason this system can be
  trusted.
- The same test holds `setup` honest: `setup.path` is a GET route the router
  serves, every section `target` is a view the console has, and component
  names and workloads are unique with exactly one primary.
- Curate. Ten commands an operator actually reaches for beat eighty generated
  ones.
- Keep the schema boring. If a command needs conditionals or loops to
  describe, the service should expose one endpoint that does the thing.

## Honest status

| | |
|---|---|
| Aggregation endpoint (`/api/portal/cli/discovery`) | ✅ shipped in portal-api |
| A worked descriptor | ✅ [acquire](https://github.com/laedeli/acquire) declares 10 commands, 1 check, 4 topics; the [sample addon](https://github.com/zaentrum/sample-addon) declares 2 commands, 1 check and a full `ui` section |
| `components[]` and `setup` read on install; containers and setup checklist in settings → addons | ✅ shipped in portal-api — see [installing](./installing.md#what-settings--addons-shows) |
| `zae discover` / doctor integration | ✅ shipped in zae v0.1 |
| Executing discovered commands + the exit-code contract + `zae require` | ✅ zae v0.2 |
| `zae addon add`, `list`, `status`, `upgrade`, `remove` | 🔶 built in zae against the [addon chart](./charts.md) API; needs a portal-api and operator that ship it |
| `zae platform status`, `update`, `restart`, `scale` | 🔶 built in zae against the portal's operator console; needs an operator-managed instance. The controller's own image stays out of scope — that is its [install bundle](../operator.md#install) |
| `auth` in the discovery document (`PORTAL_CLI_CLIENT_ID`) | ✅ shipped in portal-api |
| `zae login`, `logout`, `whoami` (device grant with PKCE, refresh, per-instance sessions) | 🔶 built in zae; needs a portal-api that advertises `auth` and the [operator-created client](#what-an-operator-must-configure) |
| Registered checks executed by doctor | 🧭 next, now that login exists (the portal will not expose in-cluster check endpoints unauthenticated) |
