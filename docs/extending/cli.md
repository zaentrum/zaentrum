# The CLI capability contract — extending `zae`

[`zae`](https://github.com/zaentrum/zae) is the zaentrum CLI. Its design rule:
**the binary compiles in no service names.** A static core (doctor, preflight)
works when the platform cannot speak for itself; everything else is a surface
the instance *declares*. Installing an addon extends the CLI on that instance;
uninstalling it leaves no trace.

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
| `workload` | A DNS-1123 label, no dots: the name of the **Deployment and the Service** in the addon's namespace. One workload has one owner — see [installing](./installing.md#what-install-refuses) |
| `role` | `primary` — exactly one; it serves this descriptor, and its `workload` equals the host of the address the addon is installed from. `required` — the addon does not work without it. `optional` — the addon works without it, with less |
| `summary` | Plain text, at most 120 characters |
| `topics` | Event topics this component emits. Top-level `topics[]` stay what the primary emits; list each topic once, under the component that emits it |

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
| `path` | A GET route on the primary, relative: starts with `/`, no `//`, no `..` — spelled out or percent-encoded (`%2e%2e`, `.%2e`) — no encoded `/` or `\`, no scheme or host |
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

Authentication is a stated stopgap until `zae login` ships: a bearer in
`ZAE_TOKEN` (for example an addon service account's client-credentials
token) is sent as-is.

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
| Executing discovered commands + the exit-code contract + `zae require` | ✅ zae v0.2 (`ZAE_TOKEN` for auth until login) |
| `zae login` (device flow) | 🧭 next |
| Registered checks executed by doctor | 🧭 with login (the portal will not expose in-cluster check endpoints unauthenticated) |
