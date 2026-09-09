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
  `slots[]` become [slot rows](./slots.md). One manifest declares the whole
  addon.

**Descriptors are data, never code.** Nothing an instance serves executes in
anyone's terminal. The worst a descriptor can do is describe an HTTP call the
CLI then makes with the caller's own token against the instance's own APIs —
no new surface beyond what those APIs already gate.

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
- Curate. Ten commands an operator actually reaches for beat eighty generated
  ones.
- Keep the schema boring. If a command needs conditionals or loops to
  describe, the service should expose one endpoint that does the thing.

## Honest status

| | |
|---|---|
| Aggregation endpoint (`/api/portal/cli/discovery`) | ✅ shipped in portal-api |
| A worked descriptor | ✅ [acquire](https://github.com/laedeli/acquire) declares 10 commands, 1 check, 4 topics; the [sample addon](https://github.com/zaentrum/sample-addon) declares 2 commands, 1 check and a full `ui` section |
| `zae discover` / doctor integration | ✅ shipped in zae v0.1 |
| Executing discovered commands + the exit-code contract + `zae require` | ✅ zae v0.2 (`ZAE_TOKEN` for auth until login) |
| `zae login` (device flow) | 🧭 next |
| Registered checks executed by doctor | 🧭 with login (the portal will not expose in-cluster check endpoints unauthenticated) |
