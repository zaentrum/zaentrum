# Decision records

Why the platform is shaped the way it is — the decisions that would cost the
most to rediscover. Several are recorded retrospectively from earlier internal
records; the dates in each Status line are the decision dates, not the
publication dates.

The format is deliberately small: Context (the forces), Decision (what and
why), Consequences (what got better, what it costs, and **what it rules out**
— the section that saves the next person from re-proposing a rejected path).

| ADR | Decision |
|---|---|
| [0001](./0001-neutral-core-and-addon-seams.md) | The core stays content-neutral; capability beyond it plugs into seams as out-of-tree addons — UI slots and ingest, and since 2026-10 notices |
| [0002](./0002-prepackaged-playback.md) | Transcode once at ingest; serve pre-packaged HLS/CMAF — no per-session runtime transcoding |
| [0003](./0003-catalog-cqrs-sole-writer.md) | One catalog writer (katalog-manager); scalable read side (katalog-api); nobody else touches the DB |
| [0004](./0004-per-product-streaming-origins.md) | Streaming origins are per-product, not one shared streamer |
| [0005](./0005-kafka-event-bus-and-schema-contracts.md) | Stage handoffs are Kafka events under a tenant prefix; schemas are published contracts |
| [0006](./0006-operator-owned-runtime.md) | Polyrepo + a front-door repo that pins releases + an operator that owns the runtime |
| [0007](./0007-identity-modes.md) | Three identity modes on one CR field: bundled, broker, external — `broker` is not built yet |
| [0008](./0008-single-origin-deployment-profiles.md) | Deployment profiles set routing and the OIDC issuer together; single-origin path routing is the LAN default — not built, and its plain-http profiles cannot sign in |
| [0009](./0009-pull-based-addon-installation.md) | Addons are installed by pulling their manifest; the platform creates their UI, owned by key — no addon identity needed to appear |
| [0010](./0010-addon-component-groups-and-setup.md) | An addon is a group of components with one primary; it owns its configuration, the platform shows component and setup state and links to where it is edited |
| [0011](./0011-addon-charts-installed-by-the-operator.md) | Addons are standard Helm charts the operator installs from one `ZaentrumAddon` per addon, planned and checked against guardrails before anything applies — no package format of our own, no GitOps controller required |
| [0012](./0012-catalog-identity-for-addons.md) | Addons hand over and look up by identity: ingest takes a series' or movie's identity, the read side answers what the library holds by identity, and an addon's topics come from its manifest — proposed, not built |
| [0013](./0013-live-rungs-safety-net.md) | Live rungs beside the package: lower SDR renditions made segment by segment by a supervised pool of warm GPU workers, offered in the same master playlist so the player switches without a reload — the encoder leaves the stream origin; accepted after a spike (the warm worker 2–4× faster than a command per segment for HDR, every crash recovered within one segment) |

## Adding one

New ADRs take the next number and the same skeleton. Two rules carried over
from hard experience: state only what is *shipped* as fact — design that is
ahead of the code is marked as such, because docs that describe an unshipped
platform cost more than no docs; and never name internal infrastructure or
acquisition tooling (CI enforces this).
