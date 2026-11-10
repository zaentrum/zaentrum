# Zaentrum architecture

## What Zaentrum is

A neutral, self-hostable media platform for a library **you own and are entitled
to stream**: a catalog core, an event-driven processing pipeline, per-product
streaming backends, clean clients, and a portal that fronts the whole thing. It
is content-neutral: you bring files you already have, and Zaentrum catalogs,
processes (transcode/package) and streams them. It never acquires content.

The picture is drawn from the [architecture](../spec/architecture/README.md), the
specification's model of every component: what the operator's chart runs or what
ships, and how each reaches the others. Sign-in is left out, as every app and
service signs in at keycloak, and so are the browser's links and the demo's jobs.
An arrow from a lane is every component's in it; a dotted one carries events.

<!-- generated: diagram -->
```mermaid
flowchart LR
  subgraph apps["the apps"]
    chino_web["chino-web"]; chino_mobile["chino-mobile"]; chino_androidtv["chino-androidtv"]; chino_tizen["chino-tizen"]
  end
  subgraph portal["the portal and its consoles"]
    zaentrum_portal["zaentrum-portal"]; portal_api["portal-api"]; katalog_manager_ui["katalog-manager-ui"]
  end
  subgraph chino["chino's services"]
    chino_api["chino-api"]; chino_stream["chino-stream"]; live_worker["live-worker"]
  end
  subgraph catalog["the catalog"]
    katalog_api["katalog-api"]; katalog_manager["katalog-manager"]; katalog_ingest["katalog-ingest"]
  end
  subgraph pipeline["the pipeline"]
    analyzer["analyzer"]; transcoder["transcoder"]; packager["packager"]
  end
  subgraph bundled["bundled services"]
    postgres["postgres"]; valkey["valkey"]; kafka["kafka"]; keycloak["keycloak"]; media["media"]
  end
  subgraph runtime["running the platform"]
    zaentrum_operator["zaentrum-operator"]; zae["zae"]; appliance["appliance"]
  end
  apps --> chino_api
  portal --> chino_api
  pipeline -.-> kafka
  pipeline --> katalog_manager
  pipeline --> media
  zaentrum_portal --> portal_api
  katalog_manager_ui --> katalog_manager
  portal_api --> postgres
  portal_api --> keycloak
  portal_api -.-> kafka
  portal_api --> katalog_manager
  chino_api --> katalog_api
  chino_api --> katalog_manager
  chino_api --> chino_stream
  chino_api --> portal_api
  chino_api --> postgres
  chino_api -.-> kafka
  chino_stream --> katalog_api
  chino_stream --> live_worker
  chino_stream --> media
  live_worker --> media
  katalog_api --> postgres
  katalog_manager --> postgres
  katalog_manager --> media
  katalog_manager -.-> kafka
  katalog_ingest --> katalog_api
  katalog_ingest --> katalog_manager
  katalog_ingest -.-> kafka
  keycloak --> postgres
  zae --> keycloak
```
<!-- end: diagram -->

## The repo model — a repository a service, one release

Zaentrum is a polyrepo: every service is its own repository in the
[`zaentrum` org](https://github.com/zaentrum) and builds its image,
`ghcr.io/zaentrum/<service>`. The portal's repository builds two, the shell and
`portal-api`, from its `server/`. Two repos are special:

- **[`zaentrum/zaentrum`](https://github.com/zaentrum/zaentrum)** (this repo) —
  the front door: the install docs, the product page, `releases.json` and the
  end-to-end tests. It **builds no service code** — and while no release is
  tagged, it pins no image tags either.
- **[`zaentrum/zaentrum-operator`](https://github.com/zaentrum/zaentrum-operator)**
  — the runtime owner: the `Zaentrum` CRD, the controller, the platform chart it
  renders, and the all-in-one appliance image, `ghcr.io/zaentrum/appliance`. A
  cluster declares one CR; the operator reconciles the platform from published
  images.

Addons live in their own repos under their own owners (the worked example is
[laedeli/acquire](https://github.com/laedeli/acquire)) and are never merged in.
The reasoning is recorded in [ADR-0006](./adr/0006-operator-owned-runtime.md).

## Front door and route map

One host fronts the product; the portal is the landing surface. The operator
renders this Ingress (single-origin profile — subdomain routing is a CR option),
listed from the chart a plain install renders:

<!-- generated: routes -->
| Path | Workload | What it is |
|---|---|---|
| `/` | `zaentrum-portal` | the portal: its launchpad, its settings and the consoles of addons |
| `/api` | `chino-api` | chino's API, for every app |
| `/api/manage` | `katalog-manager-api` (`katalog-manager`) | the catalog's only writer: scan, ingest, enrichment, the management API |
| `/api/portal` | `portal-api` | the portal's API: the registry, people, addons, running the platform |
| `/auth/callback` | `chino-web` | the web app |
| `/auth/realms` | `keycloak` | the bundled identity provider, and the job that sets up its realm |
| `/auth/resources` | `keycloak` | the bundled identity provider, and the job that sets up its realm |
| `/chino` | `chino-web` | the web app |
| `/katalog` | `katalog-manager-ui` | the catalog console |
| `/katalog-manage` | `katalog-manage-ui` (`katalog-manager-ui`) | the catalog console |
| `/portal` | `zaentrum-portal` | the portal: its launchpad, its settings and the consoles of addons |
<!-- end: routes -->

With `identity.exposeAdminConsole`, `/auth` goes to keycloak whole, its admin
console and admin API with it; without it the console answers through a
port-forward only. The [`/api/ingest`](./extending/ingest.md) of
`katalog-manager` answers in the cluster, not on the public host.

## Scope — the neutral line {#scope}

Zaentrum ships **only** the neutral platform. The hard boundary: anything that
knows *how content was acquired* lives outside the platform's repos, as an
addon.

| In the platform (neutral) | Never in the platform |
|---|---|
| clients, `chino-api`, `chino-stream`, the portal | any tool that fetches or downloads content |
| `katalog-api` (read), `katalog-manager` (write/ingest) | any control plane that decides what to go and get |
| analyzer, transcoder, packager; enrichment in `katalog-manager` | anything that reaches out to indexers or trackers |

The catalog write path is the neutral `katalog-manager`: it registers and
manages library entries for files that are **already on disk**. How those files
got there is not Zaentrum's concern.

This isn't cosmetic. A media client/server is distributable on app stores
precisely *because* it is content-neutral. Bundling acquisition would re-import
the IP problem and is against store and host policy. The boundary is enforced
by CI (a neutrality gate greps for internal hostnames and acquisition
vocabulary), not just by review.

## Extending — code plugs into seams {#extending}

The neutral line does **not** mean Zaentrum can't grow capability. It means
capability beyond the neutral core arrives as an **addon**: out-of-tree code
that plugs into seams the core exposes — UI slots, notices to one person,
portal-hosted consoles, the neutral ingest API, the event bus. The core never
learns an addon's name; uninstalling one leaves no trace.

**[Extending zaentrum](./extending/README.md)** documents every seam and its
honest implementation status. The design rationale is
[ADR-0001](./adr/0001-neutral-core-and-addon-seams.md).

Operator-specific *configuration* remains data — your issuer, your library
path, your storage classes, supplied via the CR — never patches to platform
code. A private deployment consumes public releases read-only and layers its
config (and its addons) on top.

## The pipeline is event-driven

Stage handoffs are Kafka events (`catalog.item.*` under a tenant prefix);
database rows record *state* while events drive the *handoff*. The
[event bus page](./extending/events.md) documents the topics — they are a
public integration surface, not an internal detail. Rationale:
[ADR-0005](./adr/0005-kafka-event-bus-and-schema-contracts.md).

## License {#license}

**[MPL-2.0](https://github.com/zaentrum/zaentrum-operator/blob/main/LICENSE).**
The clients ship to mobile app stores, which constrained the choice: strong
copyleft (GPL/AGPL family) conflicts with store distribution terms, and
permissive licenses give the platform no protection. MPL-2.0 — file-level
copyleft — is the middle ground: it protects the platform while keeping the
clients store-distributable. Applies across the platform's repos.

## Decision records

Durable decisions and their reasoning live in [docs/adr/](./adr/README.md) —
start with the [index](./adr/README.md).
