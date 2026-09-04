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
   returns one document. **Registering an addon's app is what registers its
   CLI surface.** Candidates never come from the request, which is what keeps
   a fanning-out endpoint SSRF-proof.
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
  "topics": ["download.client.completed"]
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

**Descriptors are data, never code.** Nothing an instance serves executes in
anyone's terminal. The worst a descriptor can do is describe an HTTP call the
CLI then makes with the caller's own token against the instance's own APIs —
no new surface beyond what those APIs already gate.

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
| A worked descriptor | ✅ [acquire](https://github.com/laedeli/acquire) declares 10 commands, 1 check, 4 topics |
| `zae discover` / doctor integration | ✅ shipped in zae v0.1 |
| `zae login` (device flow) + executing role-gated commands | 🧭 next — until then the discovered surface is browsable, not yet invokable |
| Registered checks executed by doctor | 🧭 with login (the portal will not expose in-cluster check endpoints unauthenticated) |
