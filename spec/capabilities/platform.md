# The platform

The capabilities of installing and configuring the platform through the
operator's resources, and the products that are only registered, or only
[expected](./expectations.md). The resources'
fields are in [the operator's reference](../../docs/operator.md). The columns are
explained in [how to read it](./README.md#how-to-read-it); every row comes from
[capabilities.csv](./capabilities.csv).

<!-- generated: areas -->
## Installing and configuring

The platform as an operator installs it: identity, storage, addresses, certificates, backups, updates. Not specified yet. Depth: working. For the goal [Run it oneself](../goals/README.md#run-it-oneself).

| Capability | Who | Portal | CLI | Resource | Spec |
|---|---|---|---|---|---|
| Pin the platform to a version, or follow its channel again | operator | partial | built | built | [operator](../../docs/operator.md), [updating](../../docs/updating.md), [releases](../../docs/releases.md), [cli](../../docs/extending/cli.md) |
| Turn the media pipeline on or off | operator | built | built | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [architecture](../../docs/architecture.md) |
| Install the whole platform from one resource in a namespace | operator | — | — | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [prerequisites](../../docs/prerequisites.md), [architecture](../../docs/architecture.md), [0006 operator owned runtime](../../docs/adr/0006-operator-owned-runtime.md) |
| Sign people in through the bundled identity provider or an external one | operator | partial | no | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [prerequisites](../../docs/prerequisites.md), [0007 identity modes](../../docs/adr/0007-identity-modes.md) |
| Publish the bundled identity provider's admin console on the public host | operator | no | no | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [troubleshooting](../../docs/troubleshooting.md) |
| Serve the platform at its public host, through an Ingress or Routes | operator | partial | no | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [prerequisites](../../docs/prerequisites.md), [0008 single origin deployment profiles](../../docs/adr/0008-single-origin-deployment-profiles.md) |
| Serve the platform over https with a certificate of its own | operator | partial | no | built | [prerequisites](../../docs/prerequisites.md), [self hosting](../../docs/self-hosting.md) |
| Give the library, the database and the event broker their volumes | operator | partial | no | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [prerequisites](../../docs/prerequisites.md), [troubleshooting](../../docs/troubleshooting.md) |
| Keep the databases on the bundled Postgres or on an external one | operator | no | no | partial | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md) |
| Use the bundled event broker or an external one shared with others | operator | no | no | built | [operator](../../docs/operator.md), [events](../../docs/extending/events.md), [0005 kafka event bus and schema contracts](../../docs/adr/0005-kafka-event-bus-and-schema-contracts.md) |
| Encode titles on an NVIDIA GPU or on the CPU | operator | no | no | built | [prerequisites](../../docs/prerequisites.md), [troubleshooting](../../docs/troubleshooting.md) |
| Choose the renditions, segments, audio and subtitles the packages get | operator | no | no | built | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md), [versions](../../docs/library/versions.md), [extras](../../docs/extending/extras.md) |
| Run the live worker for the encodes made while a title plays | operator | no | no | built | [0013 live rungs safety net](../../docs/adr/0013-live-rungs-safety-net.md) |
| Back up the bundled databases on a schedule, keeping the newest dumps | operator | no | no | built | — |
| Restore the bundled databases from one of their dumps | operator | no | no | built | — |
| Choose the release channel, and whether its updates apply themselves | operator | built | built | built | [operator](../../docs/operator.md), [updating](../../docs/updating.md), [releases](../../docs/releases.md) |
| Give addons a VPN their pods reach the internet through | operator | no | no | built | — |
| Provide the platform's secrets yourself instead of generated ones | operator | no | no | built | [operator](../../docs/operator.md), [self hosting](../../docs/self-hosting.md), [reference demo](../../docs/reference-demo.md) |
| Install the whole platform on one machine as a single container | operator | — | — | built | [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance), [Appliance](../../docs/prerequisites.md#appliance), [0006 operator owned runtime](../../docs/adr/0006-operator-owned-runtime.md) |
| Reach it from the home's phones and TVs with no name or certificate of one's own | operator | no | no | no | [0008 single origin deployment profiles](../../docs/adr/0008-single-origin-deployment-profiles.md), [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance) |
| Reach it from outside the home with no router or DNS setup | operator | no | no | no | — |
| Run the platform on an ARM machine | operator | — | — | no | [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance) |
| Encode on an Intel or AMD graphics chip, or a Mac's | operator | no | no | no | [GPU (NVENC)](../../docs/prerequisites.md#gpu-nvenc) |
| Move the platform to another machine with its people, settings, history and library | operator | — | no | no | — |

- Pin the platform to a version, or follow its channel again: A tag pins every image; latest follows the channel. Portal shows the version and pins only the offered update
- Turn the media pipeline on or off: Starts or stops analyzer, transcoder, packager and katalog-ingest; off, files stream as they are
- Install the whole platform from one resource in a namespace: The operator renders its embedded chart, about 16 services, with server-side apply and reverts edits to what it manages
- Sign people in through the bundled identity provider or an external one: Portal: the setup checklist shows the mode and the issuer, changes neither. identity.loginTheme is read by no template
- Publish the bundled identity provider's admin console on the public host: Off: only /auth/realms and /auth/resources are public; the console answers through a port-forward
- Serve the platform at its public host, through an Ingress or Routes: Path-routed on one host; subdomains adds chino's own. Portal: the setup checklist shows the origin, changes nothing
- Serve the platform over https with a certificate of its own: A Secret or a cert-manager issuer; Routes carry it inline. Portal shows only whether it is https. No docs page names spec.tls
- Give the library, the database and the event broker their volumes: Postgres leaves an emptyDir only with storage.postgres.migrate. Portal: the setup checklist shows the library's claim only
- Keep the databases on the bundled Postgres or on an external one: single renders exactly as perApp: no template reads it. external: the databases are made beforehand
- Use the bundled event broker or an external one shared with others: External: a bootstrap list, an mTLS Secret, a topic prefix and a consumer-group prefix per instance
- Encode titles on an NVIDIA GPU or on the CPU: gpu: NVENC on a node offering nvidia.com/gpu; cpu: x264/x265 anywhere. The setup checklist reads features.gpu instead
- Choose the renditions, segments, audio and subtitles the packages get: Empty fields keep each worker's own default; a change reaches new packages only. Of these fields the docs name only surroundAudio
- Run the live worker for the encodes made while a title plays: Mode off, shadow or on; GPU or CPU slots. Without it chino-stream encodes itself, on the CPU; features.gpu changes nothing
- Back up the bundled databases on a schedule, keeping the newest dumps: Bundled Postgres only; on by default where it is on a claim. Each dump carries its checksums; status.backup lists them
- Restore the bundled databases from one of their dumps: Asked with the annotation zaentrum.io/restore-request naming a dump: clients stop, it is checked, restored, restarted
- Choose the release channel, and whether its updates apply themselves: stable: the newest release; edge: latest. manual reports status.availableUpdate; auto rolls to it
- Give addons a VPN their pods reach the internet through: Pods labelled zaentrum.io/vpn reach only the cluster networks directly; addons get the proxy in their values. No platform pod uses it
- Provide the platform's secrets yourself instead of generated ones: Off: the operator generates each Secret once and never rotates it; on: it makes, reads and reports none
- Install the whole platform on one machine as a single container: a cluster of its own in one privileged container; amd64; answers on the machine it runs on alone
- Reach it from the home's phones and TVs with no name or certificate of one's own: sign-in needs https on every name but localhost, and the Android apps refuse plain http
- Run the platform on an ARM machine: every image is built for amd64 alone
- Encode on an Intel or AMD graphics chip, or a Mac's: the encoders are NVIDIA's and the CPU's
- Move the platform to another machine with its people, settings, history and library: a dump restores into the install that made it; nothing carries an install over

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `pin-version` | — | `Zaentrum.spec.version`, `zaentrum-portal GET /api/portal/operator`, `platform update` and 1 more | `platform-version`, `digest-pinning`, `platform-wait-timeout` |
| `enable-pipeline` | — | `Zaentrum.spec.features.pipeline`, `zaentrum-portal PATCH /api/portal/operator`, `setup pipeline` and 1 more | `service-clients`, `event-topics`, `pipeline-switch` |
| `install-platform` | — | `Zaentrum.spec.partOf`, `Zaentrum.spec.imagePullSecrets`, `Zaentrum.spec.replicas` | `part-of-label`, `image-pull-secrets`, `replica-counts`, `service-addresses`, `listen-ports`, `web-app-paths`, `kubernetes-api`, `portal-cluster-scope`, `operator-api-names`, `outside-service-keys`, `bug-report-target`, `tool-paths`, `image-version-stamp` |
| `choose-identity` | — | `Zaentrum.spec.identity.mode`, `Zaentrum.spec.identity.issuer`, `Zaentrum.spec.identity.issuerScheme` and 8 more | `identity-mode`, `oidc-issuer`, `issuer-scheme`, `token-audience`, `sign-in-clients`, `service-clients`, `people-admin-client`, `role-names`, `token-checks`, `login-theme`, `keycloak-image`, `issuer-host-alias`, `password-policy-hint`, `public-host` |
| `expose-identity-console` | — | `Zaentrum.spec.identity.exposeAdminConsole` | `identity-console` |
| `set-public-host` | — | `Zaentrum.spec.hostname`, `Zaentrum.spec.routing.mode`, `Zaentrum.spec.routing.hosts.chino` and 4 more | `issuer-host-alias`, `public-host`, `chino-host`, `ingress-switch`, `routes-switch` |
| `provide-certificates` | — | `Zaentrum.spec.tls.secretName`, `Zaentrum.spec.tls.issuerRef.name`, `Zaentrum.spec.tls.issuerRef.kind` and 3 more | `issuer-scheme`, `routes-switch`, `tls-secret`, `tls-issuer` |
| `configure-storage` | — | `Zaentrum.spec.storage.*`, `zaentrum-portal GET /api/portal/setup` | `media-size`, `media-access-mode`, `media-claim-provision`, `storage-class`, `database-volume-size`, `database-volume-class`, `database-claim`, `database-migrate`, `broker-claim`, `broker-node`, `media-paths` |
| `choose-databases` | — | `Zaentrum.spec.databases.*` | `database-mode`, `database-connection` |
| `configure-event-streaming` | — | `Zaentrum.spec.eventStreaming.*`, `Zaentrum.spec.features.kafka` | `broker-claim`, `broker-node`, `event-broker-mode`, `bundled-broker`, `kafka-brokers`, `kafka-tls`, `event-topics`, `consumer-groups` |
| `choose-encoder` | — | `Zaentrum.spec.pipeline.encoder` | `encoder`, `nvenc-quality` |
| `configure-pipeline` | — | `Zaentrum.spec.pipeline.ladder`, `Zaentrum.spec.pipeline.extraLadder`, `Zaentrum.spec.pipeline.segmentSeconds` and 3 more | `rendition-ladder`, `extras-ladder`, `segment-length`, `surround-audio`, `playlist-subtitles`, `default-audio-language`, `speech-recognition`, `chapters-lookup` |
| `enable-live-worker` | — | `Zaentrum.spec.liveWorker.*` | `nvenc-quality`, `live-worker-switch`, `live-worker-mode`, `live-worker-slots`, `live-worker-gpu`, `live-worker-placement`, `live-worker-resources`, `stream-encoder`, `stream-gpu`, `service-tokens`, `live-worker-wiring` |
| `schedule-backups` | — | `Zaentrum.spec.backup.*` | `backup-switch`, `backup-schedule`, `backup-retention`, `backup-volume-size`, `backup-volume-class`, `backup-claim` |
| `restore-backup` | — | `Zaentrum.spec.backup.claimName` | `backup-claim` |
| `choose-update-channel` | — | `Zaentrum.spec.channel`, `Zaentrum.spec.update.mode`, `zaentrum-portal PATCH /api/portal/operator` and 1 more | `release-channel`, `update-mode`, `releases-url`, `digest-pinning` |
| `connect-vpn` | — | `Zaentrum.spec.vpn.proxy`, `Zaentrum.spec.vpn.clusterCIDRs` | `vpn-proxy`, `vpn-cluster-networks` |
| `bring-own-secrets` | — | `Zaentrum.spec.secrets.external` | `external-secrets`, `service-tokens` |
| `install-on-one-machine` | — | — | — |
| `reach-on-home-network` | — | — | — |
| `reach-from-outside` | — | — | — |
| `run-on-arm` | — | — | — |
| `encode-on-other-gpus` | — | — | — |
| `move-platform` | — | — | — |

## Live channels

A product for live channels: registered, not built. Not specified yet. Depth: stub. For the goal [Watch live channels](../goals/README.md#watch-live-channels).

| Capability | Who | Portal | Spec |
|---|---|---|---|
| Watch live channels | person | no | [As deployed](../portal/home.md#as-deployed), [Spaces](../portal/home.md#spaces) |

- Watch live channels: registered only: a seeded app and tile, switched off, badged soon; nothing behind them

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `watch-live-channels` | H.C9, H.C10 | — | `registry-seed` |

## Music

A product for music: registered, not built. Not specified yet. Depth: stub. For the goal [Listen to music](../goals/README.md#listen-to-music).

| Capability | Who | Portal | Spec |
|---|---|---|---|
| Listen to music | person | no | [As deployed](../portal/home.md#as-deployed), [Spaces](../portal/home.md#spaces) |

- Listen to music: registered only: a seeded app and tile, switched off, badged soon; nothing behind them

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `play-music` | H.C9, H.C10 | `katalog-api GET /albums` | `registry-seed` |

## Photos and home videos

What a household keeps beside its films: expected, neither registered nor built. Not specified yet. Depth: stub. For the goal [Look at photos and home videos](../goals/README.md#look-at-photos-and-home-videos).

| Capability | Who | Portal | Spec |
|---|---|---|---|
| Look through photos and home videos | person | no | — |

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `look-at-photos` | — | — | — |

## Audiobooks, podcasts and books

Listening and reading: expected, neither registered nor built. Not specified yet. Depth: stub. For the goal [Listen to books and podcasts](../goals/README.md#listen-to-books-and-podcasts).

| Capability | Who | Portal | Spec |
|---|---|---|---|
| Listen to audiobooks and podcasts, and read books | person | no | — |

| Key | Changes | Served by | Settings |
|---|---|---|---|
| `listen-to-books` | — | — | — |
<!-- end: areas -->
