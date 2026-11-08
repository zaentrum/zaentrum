# Decisions

The decision records of [docs/adr](../../docs/adr/README.md), with the components
and the capabilities each governs, and how the records change each other, as
each record's status line says, in both directions.

<!-- generated: decisions -->
| Record | Decision | Status | Components | Capabilities | Relations |
|---|---|---|---|---|---|
| [ADR-0001](../../docs/adr/0001-neutral-core-and-addon-seams.md) | Neutral core and addon seams | Accepted | `zaentrum-portal`, `portal-api`, `chino-api`, `katalog-manager`, `kafka`, `sample-addon` | `add-slot-buttons`, `edit-slot-rows`, `hand-over-file`, `open-console-in-portal`, `notify-person`, `count-addon-notifications`, `see-notifications`, `read-portal-notifications` | extended by ADR-0012 |
| [ADR-0002](../../docs/adr/0002-prepackaged-playback.md) | Transcode once at ingest, serve pre-packaged segments | Accepted | `transcoder`, `packager`, `chino-stream`, `media` | `transcode-title`, `package-title`, `package-extras`, `play-title`, `choose-quality` | amended by ADR-0013 |
| [ADR-0003](../../docs/adr/0003-catalog-cqrs-sole-writer.md) | Catalog split into a read service and a sole writer | Accepted | `katalog-manager`, `katalog-api`, `postgres` | `browse-catalog`, `edit-title`, `scan-library`, `change-catalog-settings` | — |
| [ADR-0004](../../docs/adr/0004-per-product-streaming-origins.md) | Streaming is a per-product concern | Accepted | `chino-stream`, `tv-stream`, `musig-stream` | `play-title`, `watch-live-channels`, `play-music` | — |
| [ADR-0005](../../docs/adr/0005-kafka-event-bus-and-schema-contracts.md) | Kafka event bus and schema contracts | Accepted | `kafka`, `schemas`, `katalog-manager`, `analyzer`, `transcoder`, `packager`, `chino-api` | `refresh-on-library-change`, `follow-activity`, `watch-events`, `configure-event-streaming` | extended by ADR-0012 |
| [ADR-0006](../../docs/adr/0006-operator-owned-runtime.md) | Operator-owned runtime on a polyrepo | Accepted | `zaentrum-operator`, `zaentrum`, `zae` | `install-platform`, `update-platform`, `pin-version`, `choose-update-channel` | amended by ADR-0011 |
| [ADR-0007](../../docs/adr/0007-identity-modes.md) | Identity modes — bundled, broker, external | Accepted | `keycloak`, `zaentrum-operator` | `choose-identity`, `sign-in`, `expose-identity-console` | — |
| [ADR-0008](../../docs/adr/0008-single-origin-deployment-profiles.md) | Single-origin deployment profiles | Accepted | `zaentrum-operator`, `keycloak` | `set-public-host`, `provide-certificates` | — |
| [ADR-0009](../../docs/adr/0009-pull-based-addon-installation.md) | Addons are installed by pulling their manifest | Accepted | `zaentrum-operator`, `portal-api` | `add-addon-by-address`, `see-addon-state` | amended by ADR-0010; amended by ADR-0011 |
| [ADR-0010](../../docs/adr/0010-addon-component-groups-and-setup.md) | Addons are component groups that own their configuration | Accepted | `portal-api`, `zaentrum-portal` | `see-addon-state`, `check-addon-setup` | amends ADR-0009; amended by ADR-0011 |
| [ADR-0011](../../docs/adr/0011-addon-charts-installed-by-the-operator.md) | Addons are Helm charts installed by the operator | Accepted | `zaentrum-operator`, `zae`, `portal-api` | `install-addon-chart`, `upgrade-addon`, `remove-addon` | amends ADR-0009; amends ADR-0010; amends ADR-0006 |
| [ADR-0012](../../docs/adr/0012-catalog-identity-for-addons.md) | Addons hand over and look up by identity | Proposed | `katalog-manager`, `katalog-api` | `hand-over-file`, `read-library-holdings` | extends ADR-0001; extends ADR-0005 |
| [ADR-0013](../../docs/adr/0013-live-rungs-safety-net.md) | Live rungs beside the package, as a supervised safety net | Accepted | `live-worker`, `chino-stream` | `encode-while-playing`, `enable-live-worker`, `recover-faltering-stream` | amends ADR-0002 |
| [ADR-0014](../../docs/adr/0014-subtitles-in-every-language.md) | Subtitles in the instance's languages for every title, made on the platform where a title has none | Proposed | `subtitler` | `make-subtitles`, `attach-subtitle` | — |
| [ADR-0015](../../docs/adr/0015-the-package-is-the-master.md) | The package is the master; the original is deleted once its package meets the spec | Accepted | `packager`, `transcoder`, `katalog-manager`, `media` | `retire-originals`, `verify-versions`, `hold-originals`, `package-title`, `reencode-queue` | — |
<!-- end: decisions -->
