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
| [0014](./0014-subtitles-in-every-language.md) | Subtitles in the instance's languages for every title: where the source brings none in a language, the platform converts the script, translates the best subtitle the title has, or transcribes the audio first — marked as made, never replacing the source's own; proposed, measured by a spike first |
| [0015](./0015-the-package-is-the-master.md) | The package is the master for every title, made to the pipeline's rules (HEVC within a cap, bit depth and HDR10 kept, AAC stereo, every subtitle as it is); an original is deleted once its package lacks nothing but what the spec drops (surround, lossless audio, Dolby Vision kept as HDR10, 3D) — the players draw every subtitle format, ASS and VobSub everywhere and PGS on iOS and Cast still ahead of the code |
| [0016](./0016-reaching-it-at-home.md) | At home the platform is reached over plain http at the machine's address, with no name and no certificate of one's own, and announces itself so the apps find it; plain http is refused everywhere else — accepted 2026-11-15, a trial comes first, nothing built |
| [0017](./0017-the-household-machine.md) | Images for amd64 and arm64, encoders for NVIDIA, Intel and AMD chips or the processor, a smallest machine that is named and tested, the first administrator made in the browser with a setup code, and an updater outside the container that goes back when an update fails — accepted 2026-11-15, nothing built |
| [0018](./0018-people-rights-and-safety.md) | One account per person; what a person may do travels in their token as the rating cap does; a code guards an account on a shared device; passwords, a second factor and devices stay with the identity provider; a play session for every stream shows who is watching and holds a limit — accepted 2026-11-15, nothing built |
| [0019](./0019-mail-and-alerts.md) | Mail, through a server the admin names, is the platform's one way out: invites, the password reset and five alerts to the admins, raised by portal-api and shown in the bell; no push and no webhooks in the core — accepted 2026-11-15, nothing built |
| [0020](./0020-backup-restore-and-moving.md) | A backup is one set of the bundled databases that says what made it and restores into any install of its version or a newer one, which is how a platform moves; the library's files stay with their storage — accepted 2026-11-15, nothing built |
| [0021](./0021-libraries-folders-and-scans.md) | Several libraries with folders of their own, scans that run by themselves, details and pictures read from beside a title, collections kept by the catalog, and a title given back as one file — accepted 2026-11-15, nothing built |
| [0022](./0022-casting-starts-the-tv-app.md) | A cast starts chino on the TV through the TV's own system and plays as the person who sent the title, for that cast only, with a pass that is used once — accepted 2026-11-15, nothing built |
| [0023](./0023-languages-and-accessibility.md) | Every text from one message catalogue in the specification's repository, in the person's language (the device's, or a choice kept with the account); a server sends a code and values, never a sentence; every screen to WCAG 2.2 AA, checked by a program on every web page and by a walk with the device's screen reader — accepted 2026-11-15, nothing built |
| [0024](./0024-one-product-for-listening.md) | musig is the one product for listening: music, audiobooks and podcasts in one app; books to read and a household's own photos and videos are not goals — accepted, the product's design left for later |

## Adding one

New ADRs take the next number and the same skeleton. Two rules carried over
from hard experience: state only what is *shipped* as fact — design that is
ahead of the code is marked as such, because docs that describe an unshipped
platform cost more than no docs; and never name internal infrastructure or
acquisition tooling (CI enforces this).
