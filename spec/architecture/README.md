# Architecture

How zaentrum is built: every component of the platform, what runs it, what it
connects to, the decisions behind it, and the capabilities it serves. It is the
second layer of the specification. The [capabilities](../capabilities/README.md)
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
| outside | not the platform's: it calls it |
| demo | in the chart for the reference demo only, behind an option a plain install leaves off |
| beside | part of the project, not of the running platform |
| later | a later product's |
| retired | its repository is archived |

Its **kind** says what it is: an `app` on a device, a `web` app the chart serves,
a `service` that answers requests, a `worker` that does work on its own, from the
bus or a schedule, a `job` that runs and ends, the `operator`, the `cli`, a
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

## The files

| File | Written by | Holds |
|---|---|---|
| [components.csv](./components.csv) | hand | one row a component: layer, kind, status, its code, what of the chart it runs as |
| [connections.csv](./connections.csv) | hand | one row a connection: from, to, kind, on, via |
| [decisions.csv](./decisions.csv) | hand | one row a decision record: the components and the capabilities it governs |
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
- a table on these pages is not what the data says.

## The state of the model

<!-- generated: state -->
| Layer | Components | runs | ships | idle | outside | demo | beside | later | retired |
|---|---|---|---|---|---|---|---|---|---|
| the apps | 4 | 1 | 3 |  |  |  |  |  |  |
| the portal and its consoles | 3 | 3 |  |  |  |  |  |  |  |
| chino's services | 4 | 3 |  | 1 |  |  |  |  |  |
| the catalog | 3 | 3 |  |  |  |  |  |  |  |
| the pipeline | 4 | 3 |  | 1 |  |  |  |  |  |
| bundled services | 5 | 5 |  |  |  |  |  |  |  |
| running the platform | 2 | 1 | 1 |  |  |  |  |  |  |
| outside the platform | 4 |  |  |  | 4 |  |  |  |  |
| the reference demo | 1 |  |  |  |  | 1 |  |  |  |
| beside the platform | 4 |  |  |  |  |  | 4 |  |  |
| later products | 4 |  |  |  |  |  |  | 4 |  |
| retired | 4 |  |  |  |  |  |  |  | 4 |
| all | 42 | 19 | 4 | 2 | 4 | 1 | 4 | 4 | 4 |

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
names. A finding never fails the check: each is for the owner to decide, by a
change to the code, to a decision, or to the model.

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
<!-- end: findings -->

## Pages

| Page | Covers |
|---|---|
| [the map](https://zaentrum.github.io/spec/architecture/map/) | every component as a tile, by layer, and its fact sheet (on the site only) |
| [components](./components.md) | every component, layer by layer |
| [connections](./connections.md) | the requests, the events and the stores |
| [decisions](./decisions.md) | each decision record: what it governs, what it changed |
| [the overview](../../docs/architecture.md) | for the people who run and extend zaentrum: the picture, the routes, the rules |
