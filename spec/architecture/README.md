# Architecture

How zaentrum is built: every component of the platform, what runs it, what it
connects to, the decisions behind it, the capabilities it serves, and what it
cannot do yet. It is the second layer of the specification. The [capabilities](../capabilities/README.md)
say what the platform does and for whom; this layer says which part of it does
it, and how the parts reach each other.

On the site the layer is also a [map](https://zaentrum.github.io/spec/architecture/map/):
a lane for each layer, a tile for each component, coloured by its status, the
capabilities it serves, the requirements open on them, its settings fixed in the
code, or the decisions that govern it. Choosing a tile lights what it connects to;
opening it shows the component's fact sheet: what it is and runs as, its
connections both ways, the capabilities it serves, what it offers in the code,
its settings and its decisions.

> **A model, checked against the code.** The components, their connections and
> the decisions are data, written by hand. What the operator's chart runs and how
> it sets each part up is listed by a program, from the chart's main branch
> rendered with helm, and so are the organisation's repositories. A check fails
> when the chart runs something no component claims, when it wires one part to
> another and no connection says so, when a connection names nothing in the code,
> or when one decision record changes another and the other doesn't say so. The
> numbers here are computed, never typed.

## The product, not an instance

This layer is the product: what the repositories of
[github.com/zaentrum](https://github.com/zaentrum) hold, and what the operator's
chart installs, rendered with the chart's own defaults and then with every option
on. No running instance is read for it. An instance, the reference demo or anyone's
own, is the product with its own values: its routing, its storage, its databases and
broker when they are someone else's. Those values aren't modelled here.

Where the product still carries a deployment, the model shows it rather than taking
it for the product: the jobs the chart runs only for the reference demo are a lane
of their own, and a name of the demo in what every install runs is a finding.

## How to read it

A **component** is a part of zaentrum you can point at: an app, a service, a
worker, a job, the operator, the CLI, or a service the chart runs from someone
else's image, such as the database server. A repository holds the code of one
component, or of two, as the portal's does; a workload of the chart runs one.

The **layers** are the map's lanes:

| Layer | Holds |
|---|---|
| the apps | the chino apps: the web, the phone and tablet, Android TV, Samsung TV |
| the portal and its consoles | the portal, its API, the catalog console |
| chino's services | chino's API, its stream origin, the live worker |
| the catalog | the catalog's read side, its only writer, the ingest scheduler |
| the pipeline | the workers that analyse, transcode, package and make subtitles |
| bundled services | what the chart runs from others' images: the database server, the cache, the broker, the identity provider, and the media volume |
| running the platform | the operator, the CLI, the demo's jobs |
| outside the platform | what the platform calls and doesn't run: the cluster's API, outside services |
| the reference demo | what the chart runs only for the reference demo: its content, fetched, scanned and queued |
| beside the platform | the docs, the site, the event contracts, the reference addon |
| later products | products that are only registered |
| retired | archived repositories, and what replaced them |

A component's **status**:

| Status | Means |
|---|---|
| runs | the operator's chart runs it, or it is the operator |
| ships | published for people to install: the phone and TV apps, the CLI |
| idle | built, and nothing runs it yet |
| missing | not built: named because an [expectation](../capabilities/expectations.md) looks for it |
| outside | not the platform's: it calls it |
| demo | in the chart for the reference demo only, behind an option a plain install leaves off |
| beside | part of the project, not of the running platform |
| later | a later product's |
| retired | its repository is archived |

Its **kind** says what it is: an `app` on a device, a `web` app the chart serves,
a `service` that answers requests, a `worker` that does work on its own, from the
bus or a schedule, a `job` that runs and ends, the `operator`, the `cli`, the
`appliance` (one container that holds a cluster, the operator and a resource), a
`database`, a `cache`, a `broker`, an `identity` provider, a `volume`, `docs`,
`contracts`, an `addon`.

A **connection** says that one component reaches another:

| Kind | Means |
|---|---|
| calls | it sends requests to the other |
| signs in | it takes its tokens from the identity provider, or checks them against it |
| manages | it changes what the other holds: the cluster's resources, the realm's people |
| links | its page leads the browser to the other |
| publishes | it puts events on the broker's topics |
| consumes | it reads events from the broker's topics |
| writes | it changes what a store holds |
| reads | it reads a store and changes nothing |

**On** names what a connection is on: a path, a database, the topics. **Via**
names what in the code makes it: the chart's wiring (a variable the chart gives a
workload, or a claim it mounts), a variable the code reads, a path of the
Ingress, a command of the CLI.

A **decision** is a record of [docs/adr](../../docs/adr/README.md).
[decisions.csv](./decisions.csv) names the components and the capabilities each
governs; what one record amends, supersedes or extends comes from its status line.

A **limit** is something the architecture, as it is built, cannot do or does at a
cost: “Every image is built for amd64 alone”. [limits.csv](./limits.csv) names
the components it is of, the capabilities it holds back, and where the
documentation or a decision record says so. A limit is no fault: it is a fact
the next decision has to start from.

## The files

| File | Written by | Holds |
|---|---|---|
| [components.csv](./components.csv) | hand | one row a component: layer, kind, status, its code, what of the chart it runs as |
| [connections.csv](./connections.csv) | hand | one row a connection: from, to, kind, on, via |
| [decisions.csv](./decisions.csv) | hand | one row a decision record: the components and the capabilities it governs |
| [limits.csv](./limits.csv) | hand | one row a limit: its components, the capabilities it holds back, where it is said |
| [inventory.csv](../capabilities/inventory.csv) | `scripts/inventory.py` | what the code offers, and what the chart runs: workloads, services, the Ingress's paths, volumes, wires; and the repositories |
| the tables of these pages, the picture and the routes of [the overview](../../docs/architecture.md) | `scripts/capabilities.py` | never edited by hand |

To change the model, edit the CSV files and run `python3 scripts/capabilities.py`:
the same program checks the capabilities and the architecture, and writes the
tables of both. To list the code and the chart again, run
`python3 scripts/inventory.py --src <a folder of clones> --fetch`; it needs helm
to render the chart.

## What is checked

`scripts/capabilities.py --check` runs in docs-check and fails when:

- a repository of the organisation is no component's code, or a component's
  status says retired and its repository isn't archived, or the other way round;
- a workload or a volume of the chart is no component's, or more than one's;
- a wire of the chart leads to another component, by a service's name, a path of
  the public host or a claim it mounts, and no connection between the two names
  it; or it names a topic no connection of its component is on;
- a variable of the code whose name ends in `_URL`, `_URI`, `_BROKERS`,
  `_ISSUER` or `_SERVICE_HOST`, other than a component's own `BASE_URL` or
  `PUBLIC_BASE_URL`, is no connection's via;
- a via is not in the inventory, is not its connection's, or a path it names
  leads elsewhere; a connection names no via;
- a decision record has no row, or names a component or a capability that
  doesn't exist; or one record amends, supersedes or extends another, and the
  other's status line doesn't say so;
- a limit names no component, or one or a capability that doesn't exist, or
  doesn't say where it is written: a page or a heading of the documentation or
  the specification, or a page of one of the organisation's repositories;
- a table on these pages is not what the data says.

## The state of the model

<!-- generated: state -->
| Layer | Components | runs | ships | idle | missing | outside | demo | beside | later | retired |
|---|---|---|---|---|---|---|---|---|---|---|
| the apps | 7 | 1 | 3 |  | 3 |  |  |  |  |  |
| the portal and its consoles | 3 | 3 |  |  |  |  |  |  |  |  |
| chino's services | 4 | 3 |  | 1 |  |  |  |  |  |  |
| the catalog | 3 | 3 |  |  |  |  |  |  |  |  |
| the pipeline | 4 | 3 |  | 1 |  |  |  |  |  |  |
| bundled services | 5 | 5 |  |  |  |  |  |  |  |  |
| running the platform | 3 | 1 | 2 |  |  |  |  |  |  |  |
| outside the platform | 4 |  |  |  |  | 4 |  |  |  |  |
| the reference demo | 1 |  |  |  |  |  | 1 |  |  |  |
| beside the platform | 4 |  |  |  |  |  |  | 4 |  |  |
| later products | 4 |  |  |  |  |  |  |  | 4 |  |
| retired | 4 |  |  |  |  |  |  |  |  | 4 |
| all | 46 | 19 | 5 | 2 | 3 | 4 | 1 | 4 | 4 | 4 |

| Connections | Rows | Made by the chart's wiring | Only in the code |
|---|---|---|---|
| calls | 28 | 23 | 5 |
| signs in | 15 | 14 | 1 |
| manages | 5 | 2 | 3 |
| links | 2 | 0 | 2 |
| publishes | 4 | 4 | 0 |
| consumes | 6 | 6 | 0 |
| writes | 10 | 10 | 0 |
| reads | 3 | 3 | 0 |
| all | 73 | 62 | 11 |

| What the chart runs, and the code | Rows | Claimed by |
|---|---|---|
| workloads | 24 | a component |
| volumes | 3 | a component |
| services | 18 | listed: each leads to a workload |
| paths of the Ingress | 11 | listed: each leads to a workload |
| wires | 242 | 44 lead to another component, each a connection's via |
| repositories of the organisation | 31 | a component: 27 active, 4 archived |

| Decision records | Accepted | Proposed |
|---|---|---|
| 15 | 13 | 2 |
<!-- end: state -->

## What the model finds

What the model shows the code doing, against a decision or against its own
names, and a decision record that is accepted while nothing serves a capability
it governs. A finding never fails the check: each is for the owner to decide, by
a change to the code, to a decision, or to the model.

<!-- generated: findings -->
| Finding | Components | What the model shows | In the code |
|---|---|---|---|
| two writers | `katalog-manager`, `demo-seed`, `postgres` | the database katalog is written by katalog-manager and demo-seed (the reference demo's); each database is one service's | `katalog-manager-api SPRING_DATASOURCE_URL`, `DATABASE_URL` and 2 more |
| unconnected | `valkey` | valkey runs, and no component connects to it | `valkey` |
| unread topic | `katalog-ingest` | katalog-ingest publishes processing.task.*, and no component consumes it | `katalog-ingest KAFKA_BROKERS`, `KAFKA_BROKERS` |
| named for another | `chino-api`, `katalog-manager` | chino-api's ARTWORK_BASE_URL is named for artwork (retired), and leads to katalog-manager | `chino-api ARTWORK_BASE_URL` |
| named for another | `chino-api`, `katalog-manager` | chino-api's ANALYZER_BASE_URL is named for analyzer, and leads to katalog-manager | `ANALYZER_BASE_URL` |
| named for another | `analyzer`, `katalog-manager` | analyzer's KATALOG_API_URL is named for katalog-api, and leads to katalog-manager | `analyzer KATALOG_API_URL` |
| named for another | `transcoder`, `katalog-manager` | transcoder's KATALOG_API_URL is named for katalog-api, and leads to katalog-manager | `transcoder KATALOG_API_URL` |
| named for another | `packager`, `katalog-manager` | packager's KATALOG_API_URL is named for katalog-api, and leads to katalog-manager | `packager KATALOG_API_URL` |
| outside default | `katalog-ingest` | katalog-ingest's KAFKA_BROKERS defaults to a service in another namespace of one cluster, not to one the platform runs | `KAFKA_BROKERS` |
| the demo in the product | `katalog-ingest` | katalog-ingest's KAFKA_GROUP_ID is zaentrum-demo: a name of the reference demo, set by the chart every install uses | `katalog-ingest KAFKA_GROUP_ID` |
| the demo in the product | `katalog-manager` | katalog-manager's KAFKA_GROUP_ID is zaentrum-demo: a name of the reference demo, set by the chart every install uses | `katalog-manager-api KAFKA_GROUP_ID` |
| the demo in the product | `keycloak` | keycloak's DEMO_USER_PASSWORD comes from the secret zaentrum-demo-user: a name of the reference demo, set by the chart every install uses | `keycloak DEMO_USER_PASSWORD` |
| decided, not built | `zaentrum-operator`, `keycloak`, `appliance` | ADR-0008 is accepted, and nothing serves reach-on-home-network, which it governs | — |
<!-- end: findings -->

## What the architecture cannot do yet

The limits of the platform as it is built: what it cannot do, or does at a cost,
whatever an install sets. Each names the components it is of, the capabilities
it holds back, and where the documentation or a decision record says it. The
[expectations](../capabilities/expectations.md) say what people look for; a
limit says why the platform, as built, doesn't give it. Limits are written by
hand, and a component's fact sheet lists its own beside what the model finds.

<!-- generated: limits -->
| Limit | Components | Holds back | Says so |
|---|---|---|---|
| Signing in from another device takes https on a name of one's own; plain http signs in on the machine itself alone. ADR-0008's profiles for a home network are accepted and cannot sign in, as its own status says | `keycloak`, `appliance`, `chino-mobile`, `chino-androidtv` | `reach-on-home-network`, `install-on-one-machine` | [0008 single origin deployment profiles](../../docs/adr/0008-single-origin-deployment-profiles.md), [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance), [DNS + TLS](../../docs/prerequisites.md#dns--tls) |
| Every install is a Kubernetes cluster; the one-container install runs one of its own in a privileged container. The profiles without a cluster of one's own, a script and Compose, are not supported today | `zaentrum-operator`, `appliance`, `kubernetes` | `install-on-one-machine` | [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance), [D. k3s and Compose profiles](../../docs/self-hosting.md#d-k3s-and-compose-profiles), [0006 operator owned runtime](../../docs/adr/0006-operator-owned-runtime.md) |
| Every image is built for amd64 alone | `appliance`, `zaentrum-operator` | `run-on-arm` | [A. One-command appliance](../../docs/self-hosting.md#a-one-command-appliance), [Appliance](../../docs/prerequisites.md#appliance) |
| Titles are encoded on an NVIDIA GPU or on the CPU, before they play and while they do | `transcoder`, `live-worker`, `chino-stream` | `encode-on-other-gpus`, `choose-encoder` | [GPU (NVENC)](../../docs/prerequisites.md#gpu-nvenc) |
| A plain install runs a database server, a cache, an event broker and an identity provider beside its own services, one of each. The documentation names no smallest machine | `postgres`, `valkey`, `kafka`, `keycloak` | — | [Appliance](../../docs/prerequisites.md#appliance), [Keycloak / Replicas / Update](../../docs/self-hosting.md#keycloak--replicas--update) |
| By default the event broker keeps its log on a volume that goes with its pod: a restart loses topics and offsets. Producers and the pipeline retry; a claim of one's own keeps the log | `kafka` | — | [Storage](../../docs/prerequisites.md#storage), [3. Enable the media pipeline and GPU (optional)](../../docs/self-hosting.md#3-enable-the-media-pipeline-and-gpu-optional) |
| Storage, certificates, backups, databases, the encoder and identity are set in the cluster's resource alone. The portal and the CLI offer updates, the pipeline's switch, scaling and restarts | `zaentrum-operator`, `zaentrum-portal`, `zae` | `configure-storage`, `provide-certificates`, `schedule-backups`, `restore-backup`, `choose-databases`, `choose-encoder`, `choose-identity` | [Zaentrum CR spec reference](../../docs/operator.md#zaentrum-cr-spec-reference) |
| The product never updates its operator: a cluster admin applies each new one, and the one-container install is replaced | `zaentrum-operator`, `appliance`, `portal-api` | `update-operator` | [Why the product will not do it for you](../../docs/updating-the-operator.md#why-the-product-will-not-do-it-for-you), [3. The appliance](../../docs/updating-the-operator.md#3-the-appliance) |
| One operator renders every install of a cluster from the chart it embeds: a new operator changes them all at once | `zaentrum-operator` | — | [Trying a release before production](../../docs/releases.md#trying-a-release-before-production) |
| The one-container install, started as documented first, loses the platform when its container is replaced. On a named volume under a fixed host name a new container finds its cluster again | `appliance` | `move-platform` | [Persistence](../../docs/self-hosting.md#persistence) |
| Backups are dumps of the bundled databases onto a claim; the library and an external database are left to their storage. The documentation of this repository does not describe backups | `postgres`, `media`, `zaentrum-operator` | `back-up-library`, `move-platform`, `schedule-backups`, `restore-backup` | [zaentrum-operator, README.md](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/README.md#backups-of-the-bundled-postgres-specbackup) |
| The platform sends nothing to a person or an admin outside its apps: no mail, no push. An invite link is handed over by hand; a password is reset by an admin, in the identity provider's console | `portal-api`, `keycloak`, `notifications` | `mail-person`, `alert-admins`, `reset-own-password`, `get-push-notification` | [First run](../../docs/self-hosting.md#first-run) |
| The catalog scans one folder of one volume, when it is told to | `katalog-manager`, `media` | `add-library-folder`, `keep-several-libraries`, `scan-by-itself` | [Getting content in](../../docs/self-hosting.md#getting-content-in) |
| Titles' details come from one outside service, with a key of the admin's own | `katalog-manager`, `metadata-service` | `enrich-without-own-key`, `read-local-metadata`, `choose-artwork` | [First run](../../docs/self-hosting.md#first-run), [Network egress](../../docs/prerequisites.md#network-egress) |
| Where originals are retired a title is its package alone: renditions in segments, stereo and HDR10, and deleting is final. Originals are kept unless an admin sets them to go once packaged | `packager`, `katalog-manager`, `media` | `export-title`, `play-surround` | [0015 the package is the master](../../docs/adr/0015-the-package-is-the-master.md) |
| The apps are for the web, Android and iOS phones and tablets, Android TV and Samsung TVs, none from a public store yet | `chino-web`, `chino-mobile`, `chino-androidtv`, `chino-tizen`, `chino-tvos`, `chino-webos`, `chino-roku` | `get-app-from-store` | [The apps](../../docs/releases.md#the-apps) |
<!-- end: limits -->

## Pages

| Page | Covers |
|---|---|
| [the map](https://zaentrum.github.io/spec/architecture/map/) | every component as a tile, by layer, and its fact sheet (on the site only) |
| [components](./components.md) | every component, layer by layer |
| [connections](./connections.md) | the requests, the events and the stores |
| [decisions](./decisions.md) | each decision record: what it governs, what it changed |
| [the overview](../../docs/architecture.md) | for the people who run and extend zaentrum: the picture, the routes, the rules |
