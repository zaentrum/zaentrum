# Components

Every component of zaentrum, layer by layer: what it is, its code, what the
operator's chart runs it as, and how many capabilities and settings are its. A
component's capabilities are those whose screens or interfaces are in its code;
its settings, those whose variables, fields or constants are. How to read the
columns is on the [front page](./README.md#how-to-read-it).

<!-- generated: components -->
## The apps

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `chino-web` | the web app | web | runs | [chino-web](https://github.com/zaentrum/chino-web) | `chino-web` | 88 | 24 | — |
| `chino-mobile` | the phone and tablet app | app | ships | [chino-mobile](https://github.com/zaentrum/chino-mobile) | — | 100 | 25 | — |
| `chino-androidtv` | the Android TV app | app | ships | [chino-androidtv](https://github.com/zaentrum/chino-androidtv) | — | 87 | 21 | — |
| `chino-tizen` | the Samsung TV app | app | ships | [chino-tizen](https://github.com/zaentrum/chino-tizen) | — | 74 | 20 | — |
| `chino-tvos` | an app for Apple TV | app | missing | — | — | — | — | — |
| `chino-webos` | an app for LG TVs | app | missing | — | — | — | — | — |
| `chino-roku` | an app for Roku players | app | missing | — | — | — | — | — |

- `chino-web`: Served at /chino, signed in at /auth/callback
- `chino-mobile`: For Android and iOS, at the server address a person gives it
- `chino-tvos`: Expected of a media server; not begun
- `chino-webos`: Expected of a media server; not begun
- `chino-roku`: Expected of a media server; not begun

## The portal and its consoles

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `zaentrum-portal` | the portal: its launchpad, its settings and the consoles of addons | web | runs | [zaentrum-portal](https://github.com/zaentrum/zaentrum-portal) | `zaentrum-portal` | 42 | 9 | ADR-0001, ADR-0010 |
| `portal-api` | the portal's API: the registry, people, addons, running the platform | service | runs | [zaentrum-portal/server/](https://github.com/zaentrum/zaentrum-portal/tree/main/server) | `portal-api` | 51 | 46 | ADR-0001, ADR-0009, ADR-0010, ADR-0011 |
| `katalog-manager-ui` | the catalog console | web | runs | [katalog-manager-ui](https://github.com/zaentrum/katalog-manager-ui) | `katalog-manager-ui`, `katalog-manage-ui` | 21 | 4 | — |

- `portal-api`: Built from the portal's repository, its server/, as an image of its own
- `katalog-manager-ui`: One image, run twice: at /katalog and at /katalog-manage

## Chino's services

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `chino-api` | chino's API, for every app | service | runs | [chino-api](https://github.com/zaentrum/chino-api) | `chino-api` | 88 | 24 | ADR-0001, ADR-0005 |
| `chino-stream` | the stream origin: packages and the renditions made while playing | service | runs | [chino-stream](https://github.com/zaentrum/chino-stream) | `chino-stream` | 12 | 15 | ADR-0002, ADR-0004, ADR-0013 |
| `live-worker` | warm GPU workers for the renditions made while playing | service | runs | [live-worker](https://github.com/zaentrum/live-worker) | `live-worker` | 2 | 15 | ADR-0013 |
| `notifications` | push to the apps | service | idle | [notifications](https://github.com/zaentrum/notifications) | — | — | — | — |

- `live-worker`: With liveWorker.enabled (ADR-0013)
- `notifications`: A scaffold: built once the phone apps take pushes

## The catalog

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `katalog-api` | the catalog's read side | service | runs | [katalog-api](https://github.com/zaentrum/katalog-api) | `katalog-api` | 32 | 8 | ADR-0003, ADR-0012 |
| `katalog-manager` | the catalog's only writer: scan, ingest, enrichment, the management API | service | runs | [katalog-manager](https://github.com/zaentrum/katalog-manager) | `katalog-manager-api` | 37 | 75 | ADR-0001, ADR-0003, ADR-0005, ADR-0012, ADR-0015 |
| `katalog-ingest` | the ingest scheduler | worker | runs | [katalog-ingest](https://github.com/zaentrum/katalog-ingest) | `katalog-ingest` | 1 | 3 | — |

- `katalog-manager`: Runs as katalog-manager-api, the name of the service it replaced
- `katalog-ingest`: With features.pipeline

## The pipeline

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `analyzer` | analysis: intro and credits, chapters, the picture area | worker | runs | [analyzer](https://github.com/zaentrum/analyzer) | `analyzer` | — | 24 | ADR-0005 |
| `transcoder` | the transcode to the package's rules | worker | runs | [transcoder](https://github.com/zaentrum/transcoder) | `transcoder` | — | 22 | ADR-0002, ADR-0005, ADR-0015 |
| `packager` | HLS and CMAF packaging | worker | runs | [packager](https://github.com/zaentrum/packager) | `packager` | — | 21 | ADR-0002, ADR-0005, ADR-0015 |
| `subtitler` | subtitles where a title has none | worker | idle | [subtitler](https://github.com/zaentrum/subtitler) | — | — | 6 | ADR-0014 |

- `analyzer`: With features.pipeline
- `transcoder`: With features.pipeline
- `packager`: With features.pipeline
- `subtitler`: Run by hand on a GPU beside live playback; the chart doesn't run it yet (ADR-0014)

## Bundled services

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `postgres` | the bundled database server: chino, katalog, keycloak, portal | database | runs | — | `postgres`, `zaentrum-backup`, `postgres-data`, `backups` | — | — | ADR-0003 |
| `valkey` | the bundled cache | cache | runs | — | `valkey` | — | — | — |
| `kafka` | the bundled event broker | broker | runs | — | `kafka` | — | — | ADR-0001, ADR-0005 |
| `keycloak` | the bundled identity provider, and the job that sets up its realm | identity | runs | — | `keycloak`, `zaentrum-realm` | — | — | ADR-0007, ADR-0008 |
| `media` | the media volume: originals and packages | volume | runs | — | `media` | — | — | ADR-0002, ADR-0015 |

- `postgres`: Not with databases.mode external; its databases are dumped every day
- `kafka`: Not with eventStreaming.mode external
- `keycloak`: Not with identity.mode external
- `media`: A claim the chart makes, or a volume of your own

## Running the platform

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `zaentrum-operator` | the operator: the Zaentrum resource, the platform chart, addons | operator | runs | [zaentrum-operator](https://github.com/zaentrum/zaentrum-operator) | — | 23 | 70 | ADR-0006, ADR-0007, ADR-0008, ADR-0009, ADR-0011 |
| `zae` | the zae CLI; the platform's self-test runs it | cli | ships | [zae](https://github.com/zaentrum/zae) | `zaentrum-verify` | 23 | 9 | ADR-0006, ADR-0011 |
| `appliance` | the one-container install: a cluster of its own, the operator and a resource | appliance | ships | — | — | — | — | ADR-0006, ADR-0008 |

- `zaentrum-operator`: Installed on its own, it runs what the chart holds
- `appliance`: Built from zaentrum-operator's deploy/allinone; amd64; plain http, on the machine it runs on alone

## Outside the platform

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `kubernetes` | the Kubernetes API of the cluster | service | outside | — | — | — | — | — |
| `issue-tracker` | an issue tracker for bug reports | service | outside | — | — | — | — | — |
| `metadata-service` | an outside metadata service | service | outside | — | — | — | — | — |
| `chapters-service` | an outside database of chapter names | service | outside | — | — | — | — | — |

- `issue-tracker`: Optional: OpenProject, when the secret zaentrum-feedback names one
- `metadata-service`: TMDB, with the key the secret katalog-tmdb holds
- `chapters-service`: ChaptersDB, when CHAPTERSDB_ENABLED is on: the chart has it off

## The reference demo

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `demo-seed` | the reference demo's content: fetched, scanned and queued | job | demo | — | `seed-demo-content`, `scan-catalog`, `enqueue-processing` | — | — | — |

- `demo-seed`: Only with jobs.seed, which the reference demo sets: a plain install runs none of it

## Beside the platform

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `zaentrum` | the front door: the docs, the specification, the releases | docs | beside | [zaentrum](https://github.com/zaentrum/zaentrum) | — | — | — | ADR-0006 |
| `zaentrum-site` | the site: the product page, the docs and the specification | docs | beside | [zaentrum.github.io](https://github.com/zaentrum/zaentrum.github.io) | — | — | — | — |
| `schemas` | the event contracts | contracts | beside | [schemas](https://github.com/zaentrum/schemas) | — | — | — | ADR-0005 |
| `sample-addon` | the reference addon | addon | beside | [sample-addon](https://github.com/zaentrum/sample-addon) | — | — | — | ADR-0001 |

- `schemas`: Records of an earlier design: the item events are JSON today (ADR-0005)

## Later products

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `tv-api` | the tv product's API | service | later | [tv-api](https://github.com/zaentrum/tv-api) | — | — | — | — |
| `tv-stream` | the tv product's stream origin | service | later | [tv-stream](https://github.com/zaentrum/tv-stream) | — | — | — | ADR-0004 |
| `musig-api` | the music product's API | service | later | [musig-api](https://github.com/zaentrum/musig-api) | — | — | — | — |
| `musig-stream` | the music product's stream origin | service | later | [musig-stream](https://github.com/zaentrum/musig-stream) | — | — | — | ADR-0004 |

## Retired

| Component | Is | Kind | Status | Code | Runs as | Capabilities | Settings | Decisions |
|---|---|---|---|---|---|---|---|---|
| `api-gateway` | an edge gateway | service | retired | [api-gateway](https://github.com/zaentrum/api-gateway) | — | — | — | — |
| `artwork` | an image service | service | retired | [artwork](https://github.com/zaentrum/artwork) | — | — | — | — |
| `katalog-manager-api` | the catalog's writer before katalog-manager | service | retired | [katalog-manager-api](https://github.com/zaentrum/katalog-manager-api) | — | — | — | — |
| `metadata-enricher` | metadata enrichment | worker | retired | [metadata-enricher](https://github.com/zaentrum/metadata-enricher) | — | — | — | — |

- `artwork`: katalog-manager serves the pictures now
- `katalog-manager-api`: Its successor's workload kept the name
- `metadata-enricher`: katalog-manager enriches now
<!-- end: components -->
