# Extending zaentrum with addons

zaentrum's core is deliberately small and **content-neutral**: it catalogs,
processes and streams a library you already own, and it refuses to grow
features beyond that. Everything else — request flows, download orchestration,
anything opinionated — is an **addon**: a separate service, in its own repo,
built and deployed on its own cadence, that plugs into seams the core exposes.

The principle throughout: **the core ships the socket, the addon ships the
plug.** The core never learns an addon's name. Installed, an addon surfaces
real UI and drives real work; uninstalled, the core shows no trace of it.

The worked example is [acquire](https://github.com/laedeli/acquire) — the
requests + downloads addon. Its docs describe the addon side of everything on
this page.

## The extension surfaces

| Surface | What it gives an addon | Contract |
|---|---|---|
| **[UI slots](./slots.md)** | A native button inside a product app (e.g. "Request this" on an empty search) | `ui_extensions` registry in portal-api |
| **[Hosted console](./console.md)** | A full admin UI inside the portal shell — no own origin, route, or session | Module federation, attached at runtime |
| **[Catalog ingest](./ingest.md)** | "This file on disk is now a library item" — the pipeline takes it from there | `POST /api/ingest` on katalog-manager |
| **[Event bus](./events.md)** | React to pipeline stages; publish your own domain events | Kafka topics under the tenant prefix |
| **[Identity](./identity.md)** | A service account that may self-register its UI contributions | OIDC client-credentials + the addon role |

Two properties make this composition honest:

- **The operator never prunes what it did not render.** The reconciler applies
  only its own objects; a workload you add to the namespace survives every
  reconcile and does not cascade-delete with the CR. Your addon is safe next to
  the platform.
- **Uninstall is subtraction.** UI contributions live in registry rows keyed by
  `addon`; zero rows means zero UI. Remove the workload and its rows and the
  core looks as if the addon never existed.

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
| Addon service-account role in the bundled realm | 🧭 roadmap — see [identity](./identity.md) |
| Addon self-registering its **app/tile** (not just slot rows) | 🧭 roadmap (admin registers them today) |
| Declarative install (`spec.addons[]` on the CR) | 🧭 roadmap — see [installing](./installing.md) |

## Installing an addon today

There is no one-command install yet. [Installing addons](./installing.md)
describes the honest current path — plain Kubernetes manifests applied next to
the platform — and what the operator does and does not take care of.
