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
| **[Configuration](./configuration.md)** | Settings the addon owns and edits in its console, with a setup checklist in settings → addons that links there | `components` and `setup` in the descriptor, plus a status endpoint |
| **[Addon charts](./charts.md)** | The platform deploys the addon itself: a plan to confirm, an install form from the chart's schema, removal that deletes what it created | A Helm chart with `zaentrum.io` annotations and `values.schema.json`, installed through one `ZaentrumAddon` resource |

Four properties make this composition honest:

- **The operator never prunes what it did not render.** The reconciler applies
  only its own objects; a workload you add to the namespace survives every
  reconcile and does not cascade-delete with the CR. Your addon is safe next to
  the platform.
- **Installation is pull.** The addon declares what it contributes in one
  manifest; the platform reads it when an admin adds the addon and creates
  the app, tile and slot rows itself, owned by the addon's key. The addon
  holds no credential and writes nothing.
- **An addon is a group of containers that owns its configuration.** The
  manifest declares the addon's components and where its setup state is
  reported; the platform shows whether they run and whether the addon is
  configured, and links to the addon's console where settings are edited. It
  never stores a configuration value. The containers are deployed by the
  operator from the addon's Helm chart after an admin confirms the plan — or,
  for an addon installed from an address, by the installer's own channel.
- **Uninstall is subtraction.** UI contributions live in registry rows keyed by
  `addon`; zero rows means zero UI. Remove the addon in settings — a chart
  addon takes its workloads with it; for one installed from an address, delete
  them too — and the core looks as if it never existed.

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
| Component groups and the setup checklist in settings → addons | ✅ shipped — see [installing](./installing.md) and [configuration](./configuration.md) |
| Addons installed from a Helm chart by the operator — one `ZaentrumAddon` per addon, plan before install, settings and `zae addon` | 🔶 decided in [ADR-0011](../adr/0011-addon-charts-installed-by-the-operator.md), being built — see [addon charts](./charts.md) |
| Addon service-account role in the bundled realm | ✅ defined; clients are created by hand — see [identity](./identity.md) |
| Platform-provisioned addon identity | 🧭 roadmap |
| Declarative install: a committed `ZaentrumAddon` and its values Secret | 🔶 arrives with addon charts — see [GitOps](./charts.md#6-gitops-committing-the-resource) |
| CLI capability discovery + a worked descriptor | ✅ shipped — see [the CLI contract](./cli.md) |

## Installing an addon

An addon that ships a Helm chart is added in settings → addons → **+** or
with `zae addon add`: the operator deploys it once you confirm its plan
([addon charts](./charts.md)). Any other addon is deployed next to the
platform through your own channel, then added in the portal's settings by its
in-cluster address. [Installing addons](./installing.md) describes both, what
the platform creates from the manifest, and how upgrade and uninstall work.
