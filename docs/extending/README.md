# Extending zaentrum with addons

zaentrum's core is deliberately small and **content-neutral**: it catalogs,
processes and streams a library you already own, and it refuses to grow
features beyond that. Everything else — request flows, download orchestration,
anything opinionated — is an **addon**: a separate service, in its own repo,
built and deployed on its own cadence, that plugs into seams the core exposes.

The principle throughout: **the core ships the socket, the addon ships the
plug.** The core never learns an addon's name. Installed, an addon surfaces
real UI and drives real work; uninstalled, the core shows no trace of it.

Two worked examples: the [sample addon](https://github.com/zaentrum/sample-addon)
is the smallest thing that plugs into every seam, written to be copied;
[acquire](https://github.com/laedeli/acquire) — the requests + downloads
addon — is the full-size one. Their docs describe the addon side of
everything on this page.

## The extension surfaces

| Surface | What it gives an addon | Contract |
|---|---|---|
| **[UI slots](./slots.md)** | A native button inside a product app (e.g. "Request this" on an empty search) | `ui_extensions` registry in portal-api |
| **[Hosted console](./console.md)** | A full admin UI inside the portal shell — no own origin, route, or session | Module federation, attached at runtime |
| **[Catalog ingest](./ingest.md)** | "This file on disk is now a library item" — the pipeline takes it from there | `POST /api/ingest` on katalog-manager |
| **[Event bus](./events.md)** | React to pipeline stages; publish your own domain events | Kafka topics under the tenant prefix |
| **[Identity](./identity.md)** | A service account for calling platform APIs (ingest, events) — not needed to install | OIDC client-credentials + the addon role |
| **[CLI capability](./cli.md)** | Commands and checks in the [`zae`](https://github.com/zaentrum/zae) CLI on any instance running the addon | A descriptor at `/.well-known/zaentrum-capability.json` |

Two properties make this composition honest:

- **The operator never prunes what it did not render.** The reconciler applies
  only its own objects; a workload you add to the namespace survives every
  reconcile and does not cascade-delete with the CR. Your addon is safe next to
  the platform.
- **Installation is pull.** The addon declares what it contributes in one
  manifest; the platform reads it when an admin adds the addon and creates
  the app, tile and slot rows itself, owned by the addon's key. The addon
  holds no credential and writes nothing.
- **Uninstall is subtraction.** UI contributions live in registry rows keyed by
  `addon`; zero rows means zero UI. Remove the addon in settings and its
  workload, and the core looks as if it never existed.

## Honest status

These docs describe only what a **stock install** does. Where the design is
ahead of the shipped platform, it is marked, not asserted:

| Capability | Status |
|---|---|
| UI slot registry + per-slot read API | ✅ shipped |
| Slots rendered in product apps | 🔶 one slot today (`search.empty`) — see [slots](./slots.md) |
| Portal-hosted console via runtime federation | ✅ shipped |
| Neutral catalog ingest | ✅ shipped |
| Event bus with tenant-prefixed topics | ✅ shipped |
| Install from settings by pulling the addon's manifest (app + tile + slot rows, removable by key) | ✅ shipped — see [installing](./installing.md) |
| Addon service-account role in the bundled realm | ✅ defined; clients are created by hand — see [identity](./identity.md) |
| Platform-provisioned addon identity | 🧭 roadmap |
| Declarative install (`spec.addons[]` on the CR) | 🧭 roadmap — see [installing](./installing.md) |
| CLI capability discovery + a worked descriptor | ✅ shipped — see [the CLI contract](./cli.md) |

## Installing an addon

Deploy the workload next to the platform, then add it in the portal's
settings by its in-cluster address. [Installing addons](./installing.md)
describes both steps, what the platform creates from the manifest, and how
upgrade and uninstall work.
