# ADR-0007: Identity modes — bundled, broker, external

**Status:** Accepted · recorded retrospectively (decision from 2026-06)

> **Status — partly ahead of the code.** Built: the `bundled` and `external` modes, and the
> CRD accepts no other value — **`broker` is not built**. In `bundled` mode the portal's
> People page manages the realm's people — add, invite, rename, change the role, give a
> rating cap, switch off, delete — through a client whose service account may only view,
> query and manage users. Not built: passwords and second factors set from the platform,
> per-library access; for `external`, the directory, the claim-to-role editor, per-principal
> grants and connection health; the setup question, SCIM, and the emergency admin. The
> clients are one per app — the web app, the portal and its consoles, the phone, the TV, the
> command line — not one unified client
> ([sign-in redirects](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/README.md#sign-in-redirects-and-the-realm-job)).
> And an empty issuer in `external` mode is not yet an error: it is derived from
> `spec.hostname`, as in `bundled` mode.

## Context

Zaentrum deployments span two populations that want opposite things from identity.
A household appliance must boot with working login and zero identity homework.
An operator who already runs an identity provider refuses — rightly — to maintain
a second user store just for a media platform.

Both populations share the same clients: one unified public OIDC client used by
the web app (authorization code + PKCE), mobile (AppAuth), and TV (device grant,
RFC 8628). All of them are public clients; exact redirect registration and
audience scoping are the real controls, not secrets.

And both trip over the same failure. The single most common self-host boot
failure in this class of software is the **issuer trap**: the identity provider
mints tokens for one hostname while services validate them against another —
an internal service address, `localhost`, or a stale name. Every service then
boots with OIDC broken and the operator sees an empty, unauthenticated app.
Whatever identity design we pick has to solve that trap once, centrally, not
once per service.

## Decision

One field on the platform custom resource decides who owns users:

```yaml
spec:
  hostname: media.example.org   # the ONE access host
  identity:
    mode: bundled               # bundled | broker | external
```

```mermaid
flowchart TB
  subgraph BUN["bundled (default)"]
    bw["clients"] --> bk["bundled Keycloak\n(owns users)"]
  end
  subgraph BRK["broker"]
    rw["clients"] --> rk["bundled Keycloak\n(local issuer, linked accounts)"]
    rk -. "federates, server-to-server" .-> up["upstream IdP\n(owns credentials)"]
  end
  subgraph EXT["external"]
    ew["clients"] --> ei["remote IdP\n(owns users + issuer)"]
  end
```

- **`bundled`** (default) — the operator renders a headless Keycloak as the sole
  user store. The management UI has full user CRUD: create, delete, passwords,
  MFA reset, roles, per-library access. The issuer is **derived from
  `spec.hostname`** (`https://<hostname>/auth/realms/…`) and pinned strictly, so
  it can never be taken from a spoofable Host header.
- **`broker`** — the bundled Keycloak stays, and additionally **federates an
  upstream IdP**. On first login it links a local account (explicit
  confirm-link flow; email trust is off by default because silent auto-link is
  an account-takeover hole), maps upstream claims to platform roles, and mints
  its **own locally signed token**. Clients never see the upstream IdP. The TV
  device flow keeps working even when the upstream does not support it, because
  it runs against the local Keycloak. Ownership is hybrid: the upstream owns
  credentials and MFA; the platform owns the linked record, roles, and a local
  break-glass admin. Brokering adds one registration upstream: the bundled
  realm's broker endpoint, `https://<hostname>/auth/realms/<realm>/broker/<alias>/endpoint`,
  must be an allowed redirect URI of the client the upstream IdP issues for the
  platform.
- **`external`** — no bundled Keycloak is rendered at all. The platform is a
  pure OIDC relying party: it validates tokens directly against the remote
  issuer's discovery document and JWKS. Users live entirely upstream; the
  platform keeps only a thin authorization table. The management UI loses user
  CRUD and shows instead a read-only directory of principals it has actually
  seen, a claim-to-role mapping editor, per-principal grants, and connection
  health checks.

**The invariant that makes this safe:** in `bundled` *and* `broker`, every
client validates the **same stable local issuer**. The issuer trap is solved
exactly once, in the operator, keyed on `spec.hostname` — and turning on
external SSO via `broker` changes **zero** client configuration. This is why
`broker`, not `external`, is the recommended mode for anyone bringing their own
IdP.

In `external` mode the issuer is fixed by the remote IdP, independent of
`spec.hostname`. The operator never rewrites it from the hostname; the trap
moves to the one place it can live — **redirect-URI registration** on the
upstream client — and the operator validates that registration instead. Setting
`mode: external` or `broker` with an empty issuer is a hard reconcile error,
never a silent default.

**Authorization is keyed on `(iss, sub)` — never on email or username.** Those
are mutable; the issuer/subject pair is the only stable identity across all
three modes. The IdP owns authentication (credentials, MFA, sessions); the
platform owns app-level authorization (roles, per-library access). On every
login a deterministic claim-to-role resolution runs, with a fail-safe default
when nothing matches (plain user, no library access). Authentication failure is
a 401 at the IdP boundary; authorization failure is a 403 at the platform's
policy layer. Provisioning defaults to JIT-on-first-login; SCIM 2.0 sits behind
a flag for organizations that need pre-provisioning and automated offboarding.

Mode changes follow the same asymmetry: `bundled → broker` is additive and
allowed live; switching between `bundled` and `external` is a migration of a
populated user store and is gated behind an explicit destructive-switch flag.

## Consequences

- Setup asks one question. The default steers households to `bundled` and
  BYO-IdP operators to `broker`; `external` is a deliberate opt-in for someone
  running a mature IdP that supports every grant the clients need — including
  the device grant for TV.
- Renaming a user or changing their email never breaks their grants, in any
  mode, because nothing is keyed on either.
- Claims are a snapshot at token-issue time: a group change upstream applies on
  the next login or refresh, so access-token TTLs stay short.
- `external` trades away the local escape hatch: with no bundled Keycloak
  there is no local break-glass admin, so a misconfigured claim mapping can
  lock everyone out of administration. The CR therefore accepts an emergency
  admin pinned by `(iss, sub)` even in external mode.
- The management UI must show provenance per principal (local vs. federated),
  so an admin never believes they can reset a federated user's password here.
- What sign-in depends on differs by mode. `bundled` depends on the in-cluster
  Keycloak alone. `broker` depends on the upstream IdP for federated sign-ins
  only: local accounts, the break-glass admin among them, still sign in while it
  is down. `external` depends on the remote IdP for every sign-in.

### The fields, sketched (not built)

How the parts of this decision that aren't built would sit on the resource;
nothing here is in the CRD yet, and secrets stay references, never values:

```yaml
spec:
  identity:
    mode: broker                       # bundled | broker | external
    roleMapping:                       # deterministic claim-to-role resolution
      claim: realm_access.roles        # a dotted path into the token
      adminValues: [zaentrum-admin]
      userValues: [zaentrum-user]
      onNoMatch: user-no-library       # user-no-library (the fail-safe default) | deny
    broker:                            # an upstream IdP federated through the bundled realm
      alias: upstream
      issuer: https://login.example.org/realms/example
      clientId: zaentrum-broker
      clientSecretRef: { name: zaentrum-broker-idp, key: client-secret }
      claimToRole:
        - { claim: groups, value: media-admins, role: zaentrum-admin }
        - { claim: groups, value: "*", role: zaentrum-user }
      trustEmail: false                # never link on an unverified email
      firstLoginFlow: confirm-link     # confirm-link | verify-email; never a silent link
    allowDestructiveSwitch: false      # true lets a switch drop a populated bundled realm
```

### What this rules out

- **Per-service identity configuration.** One deployment has one identity mode
  and one issuer; no service carries its own OIDC settings.
- **Auto-linking accounts by email.** Linking a federated login to an existing
  account requires an explicit confirmation flow, always.
- **Writing into someone else's directory.** In `external` mode the platform
  never creates, deletes, or modifies users upstream unless the operator
  explicitly grants an admin client for that purpose.
- **Deriving the external issuer from the access hostname.** The old
  localhost-issuer guessing is gone; a missing issuer fails loudly.
- **Inline secrets in the CR.** Client secrets and admin passwords live only in
  Secret references; rotation is a planned restart, not an edit.
