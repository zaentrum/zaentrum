# Connections

How the components reach each other: the requests one makes of another, the
events on the bus, and the stores. Each is a row of
[connections.csv](./connections.csv), with what in the code makes it.

<!-- generated: connections -->
## Requests

| From | Kind | To | On | Note |
|---|---|---|---|---|
| `chino-androidtv` | calls | `chino-api` | /api | — |
| `chino-androidtv` | signs in | `keycloak` | — | The device grant: a code, entered on another device |
| `chino-mobile` | calls | `chino-api` | /api | At the address a person gives it |
| `chino-mobile` | signs in | `keycloak` | — | The authorization code with PKCE, in the system's browser |
| `chino-tizen` | calls | `chino-api` | /api | — |
| `chino-tizen` | signs in | `keycloak` | — | The device grant: a code, entered on another device |
| `chino-web` | calls | `chino-api` | /api | — |
| `chino-web` | signs in | `keycloak` | — | — |
| `katalog-manager-ui` | calls | `chino-api` | /api/config | The client to sign in with |
| `katalog-manager-ui` | calls | `katalog-manager` | /api/manage | GraphQL, and the streams of its previews |
| `katalog-manager-ui` | signs in | `keycloak` | — | — |
| `portal-api` | calls | `chino-api` | a person's data | Deletes the data of someone an admin deletes |
| `portal-api` | calls | `katalog-manager` | setting up | The library's volume and its scan, while the platform is set up |
| `portal-api` | signs in | `keycloak` | — | — |
| `portal-api` | manages | `keycloak` | people | Adds, changes and deletes people in the bundled realm |
| `portal-api` | manages | `kubernetes` | the platform's parts | Its parts, the Zaentrum resource, addons |
| `portal-api` | links | `chino-web` | /chino | The launchpad's tile for chino |
| `portal-api` | links | `keycloak` | where people are managed | The identity provider's own console, when people aren't the portal's to manage |
| `zaentrum-portal` | calls | `chino-api` | /api/config | The client to sign in with |
| `zaentrum-portal` | calls | `portal-api` | /api/portal | — |
| `zaentrum-portal` | signs in | `keycloak` | — | — |
| `chino-api` | calls | `chino-stream` | — | — |
| `chino-api` | calls | `issue-tracker` | bug reports | When the secret zaentrum-feedback names one |
| `chino-api` | calls | `katalog-api` | — | With the viewer's bearer and their max_rating |
| `chino-api` | calls | `katalog-manager` | admin actions, pictures | ANALYZER_BASE_URL is an older name of KATALOG_MANAGER_URL |
| `chino-api` | calls | `portal-api` | slots, account deletion | — |
| `chino-api` | signs in | `keycloak` | — | — |
| `chino-stream` | calls | `katalog-api` | — | The playback lookups take no bearer: in-cluster only |
| `chino-stream` | calls | `live-worker` | — | As far as LIVE_WORKER_MODE says: off, shadow or on |
| `chino-stream` | signs in | `keycloak` | — | — |
| `katalog-api` | signs in | `keycloak` | — | — |
| `katalog-ingest` | calls | `katalog-api` | — | — |
| `katalog-ingest` | calls | `katalog-manager` | — | — |
| `katalog-manager` | calls | `chapters-service` | chapter names | Off in the chart |
| `katalog-manager` | calls | `metadata-service` | metadata | With a key |
| `katalog-manager` | signs in | `keycloak` | — | — |
| `analyzer` | calls | `katalog-manager` | claims and results | — |
| `analyzer` | signs in | `keycloak` | a service's token | — |
| `packager` | calls | `katalog-manager` | packaging complete | It publishes nothing: katalog-manager announces the package |
| `packager` | signs in | `keycloak` | a service's token | — |
| `subtitler` | calls | `katalog-manager` | the attach endpoint | — |
| `subtitler` | calls | `live-worker` | its metrics | Leaves the GPU to live playback |
| `transcoder` | calls | `katalog-manager` | claims and results | — |
| `transcoder` | signs in | `keycloak` | a service's token | — |
| `zae` | signs in | `keycloak` | — | — |
| `zae` | manages | `keycloak` | the self-test's account | — |
| `zae` | manages | `kubernetes` | the platform | — |
| `zaentrum-operator` | calls | `zaentrum` | releases.json | The versions it may update to |
| `zaentrum-operator` | manages | `kubernetes` | the platform | The chart's parts, addons' charts |
| `demo-seed` | calls | `katalog-manager` | a scan | — |

## Events

| Topic, after the prefix | Published by | Consumed by |
|---|---|---|
| `catalog.extra.packaged` | `katalog-manager` | `chino-api` |
| `catalog.extra.queued` | `katalog-manager` | `transcoder` |
| `catalog.extra.transcoded` | `transcoder` | `packager` |
| `catalog.item.analyzed` | `analyzer` | `chino-api`, `transcoder` |
| `catalog.item.discovered` | `katalog-manager` | `chino-api`, `katalog-manager` |
| `catalog.item.enriched` | `katalog-manager` | `analyzer`, `chino-api` |
| `catalog.item.packaged` | `katalog-manager` | `chino-api` |
| `catalog.item.removed` | `katalog-manager` | `chino-api` |
| `catalog.item.transcoded` | `transcoder` | `chino-api`, `packager` |
| `processing.task.*` | `katalog-ingest` | — |

`portal-api` reads every topic.
Every topic carries the instance's prefix, `stube.` unless the resource says another.

## Stores

| Store | On | Written by | Read by |
|---|---|---|---|
| `media` | — | `analyzer`, `demo-seed`, `katalog-manager`, `packager`, `transcoder` | `chino-stream`, `live-worker` |
| `postgres` | chino | `chino-api` | — |
| `postgres` | katalog | `demo-seed`, `katalog-manager` | `katalog-api` |
| `postgres` | keycloak | `keycloak` | — |
| `postgres` | portal | `portal-api` | — |
<!-- end: connections -->
