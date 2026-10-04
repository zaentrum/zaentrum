# Self-hosting Zaentrum

Zaentrum is a neutral self-host media platform — a catalog, a media pipeline, and clean
web/mobile/TV clients for a library **you own and are entitled to stream**. It ships no
content and no downloaders: you point it at files that are already on disk.

The platform is one canonical Helm chart (`operator/platform/chart`) that is `go:embed`-ed
into the operator image and driven by a single `Zaentrum` custom resource. Everything is a
container at `ghcr.io/zaentrum/<service>` on the public GitHub Container Registry. This page
covers the three supported ways to run it, and two profiles that are not supported today:

| Path | Audience | Section |
|---|---|---|
| One-command appliance | Fastest start, single box | [A](#a-one-command-appliance) |
| Operator on your own Kubernetes | You run k8s; want day-2 management | [B](#b-self-host-with-the-operator) |
| `helm install` the chart directly | You run k8s; don't want the operator | [C](#c-helm-install-the-chart) |
| k3s (`up.sh`) profile | **Not supported today** | [D](#d-k3s-and-compose-profiles) |
| Docker Compose profile | **Not supported today** | [D](#d-k3s-and-compose-profiles) |

Before you start, read [prerequisites.md](./prerequisites.md) for identity (OIDC), DNS, and
TLS. For the full `Zaentrum` CR contract see [operator.md](./operator.md); the public
reference deployment is documented in [reference-demo.md](./reference-demo.md).

---

## A. One-command appliance

The whole platform in **one container**. The image bundles a single-node
[k3s](https://k3s.io), the operator's install manifest and a `Zaentrum` resource; k3s applies
them on boot, and the operator brings up the platform from that resource as it would on any
cluster. Zero-clone — nothing to check out.

```bash
docker run -d --privileged --restart unless-stopped --name zaentrum -p 80:80 \
  ghcr.io/zaentrum/appliance:latest
```

Then open <http://zaentrum.localhost> — modern browsers resolve `*.localhost` to `127.0.0.1`
with no `/etc/hosts` edit. First boot pulls the application images and runs the database
migrations, so give it a few minutes; `--restart unless-stopped` brings the container back
after a reboot or a Docker restart.

**Port 80, and that one name.** The resource the appliance boots sets
`hostname: zaentrum.localhost`, and the platform binds both its ingress and its sign-in to it:
the ingress answers that host only, and Keycloak issues its tokens for, and redirects every
sign-in to, `http://zaentrum.localhost` on port 80. Publish the container on another host port
(`-p 8080:80`) or open it by another name (`http://localhost`, the machine's IP) and the pages
answer 404, or the sign-in redirects to a port nothing listens on.

**linux/amd64 only.** No arm64 image is published yet.

**This machine only.** The appliance serves plain http, and sign-in works over plain http on
`localhost` names alone: Keycloak marks its login cookies `Secure`, which a browser keeps over
http only for `localhost`. A phone, a TV or another computer cannot sign in to it — and the
Android phone and TV apps refuse plain http outright. For other devices, run the
[operator](#b-self-host-with-the-operator) under a real hostname with https.

**Why `--privileged`?** The container runs k3s, which needs to mount filesystems, manage
cgroups, and run an embedded containerd for the app pods. `--privileged` is the supported
default; hardened setups can pass the narrower capability/mount set k3s documents instead.

### First run

There is **no setup wizard**. The wizard at `/manage/setup` and its `/api/manage/setup` API went
away when the catalog manager was rewritten, and nothing replaces them yet. A fresh appliance
comes up already configured — for `http://zaentrum.localhost`, with the bundled Keycloak (realm
`zaentrum`) and an empty library — and three steps make it yours:

1. **Sign in.** Open <http://zaentrum.localhost>: the portal, whose launchpad opens the video
   app and, for an admin, the catalog consoles. Sign in as `admin` with the **one-time
   password** the operator generated for this install, and Keycloak then has you choose a
   password of your own. The one-time password is in Secret `zaentrum-keycloak-admin`, key
   `realm-admin-password`:

   ```bash
   docker exec zaentrum kubectl -n zaentrum get secret zaentrum-keycloak-admin \
     -o jsonpath='{.data.realm-admin-password}' | base64 -d; echo
   ```

   On a cluster it is the same command without `docker exec zaentrum`, in the platform's
   namespace, and the CR's `SecretsGenerated` condition names the Secret too
   ([operator.md](./operator.md#minimal-self-host)). Further accounts are made in
   Keycloak's admin console, which is not on the public host — see
   [the admin console](#the-admin-console).
2. **Add a TMDB key — before the first scan.** Titles, posters and plots come from TMDB, and
   the published images carry no key of their own. In **Catalog Management** on the launchpad
   (`/katalog-manage/`), open **settings** and enter a TMDB v4 read access token as **TMDB api
   key**; it applies from the next lookup, no restart. A file scanned without a key is listed by
   its file name; its page in the **Catalog** can look it up again once there is one.
3. **Fill the library, then scan.** The catalog reads `/var/lib/katalog/media` — the `media/`
   folder of the platform's `media` volume. On the appliance that volume is a directory under
   k3s's storage path inside the container. Copy your files there, then press **trigger scan**
   in Catalog Management:

   ```bash
   lib=$(docker exec zaentrum sh -c 'echo /var/lib/rancher/k3s/storage/pvc-*_zaentrum_media')/media
   docker exec zaentrum mkdir -p "$lib"
   docker cp ./my-library/. zaentrum:"$lib/"
   ```

   A file under a `series/`, `tv/` or `shows/` folder, or named with `S01E02`, becomes an
   episode; every other video file becomes a movie.

### The admin console

Keycloak's admin console — where further accounts are made — and its admin API are **not on the
public host**: the ingress sends Keycloak only `/auth/realms` (the login and account pages, the
OIDC endpoints) and `/auth/resources`, so <http://zaentrum.localhost/auth/admin/> answers 404.
The console answers through a port-forward on local port 8080, where its own links point
(`http://localhost:8080/auth`), signed in as the master realm's bootstrap admin: `admin`, with
the `password` of Secret `zaentrum-keycloak-admin` — a machine credential beside the first
administrator's, which the operator's own Jobs sign in with too. In the master realm's console
the realm `zaentrum`, its users and its clients, is one switch away in the realm list; the
realm's own console, `/auth/admin/zaentrum/console/`, signs in on the public host and does not
work through the port-forward.

On the appliance the port-forward runs inside the container, which needs that port published
when it starts:

```bash
docker run -d --privileged --restart unless-stopped --name zaentrum \
  -p 80:80 -p 127.0.0.1:8080:8080 ghcr.io/zaentrum/appliance:latest
docker exec -d zaentrum kubectl -n zaentrum port-forward --address 0.0.0.0 svc/keycloak 8080:80
docker exec zaentrum kubectl -n zaentrum get secret zaentrum-keycloak-admin \
  -o jsonpath='{.data.password}' | base64 -d; echo
open http://localhost:8080/auth/admin/    # as admin, with that password
```

A running container gains no port, and replacing one started with the command above starts an
empty platform ([persistence](#persistence)). Without the port, publish the console on the
appliance's own port instead, knowing that it then answers anyone who can reach this machine's
port 80 and asks for `zaentrum.localhost`:

```bash
docker exec zaentrum kubectl -n zaentrum patch zaentrum zaentrum --type merge \
  -p '{"spec":{"identity":{"exposeAdminConsole":true}}}'
```

The console is then at <http://zaentrum.localhost/auth/admin/>, and the realm's own at
`/auth/admin/zaentrum/console/`, where the first administrator signs in.

On a cluster it is the same port-forward, from your machine — or `identity.exposeAdminConsole:
true` on the CR, which publishes `/auth` whole on the public host:

```bash
kubectl -n zaentrum port-forward svc/keycloak 8080:80
kubectl -n zaentrum get secret zaentrum-keycloak-admin -o jsonpath='{.data.username}' | base64 -d; echo
kubectl -n zaentrum get secret zaentrum-keycloak-admin -o jsonpath='{.data.password}' | base64 -d; echo
open http://localhost:8080/auth/admin/
```

### Persistence

A fresh appliance keeps the platform's data on two claims, which k3s's `local-path`
StorageClass keeps under `/var/lib/rancher/k3s/storage`, inside the Docker volume the image
declares for `/var/lib/rancher/k3s`: `media`, the library — your files and, with the pipeline
on, their packaged streams — and `postgres-data`, the bundled Postgres's: the catalog,
Keycloak's accounts and the portal's settings. Both outlive their pods. Kafka and the HLS cache
run on `emptyDir`s.

- **A restart keeps the platform.** `docker stop` / `docker start`, a Docker restart, or a reboot
  with `--restart unless-stopped` bring back the same cluster, pods and claims, data included.
- **An appliance from an older image keeps its Postgres on an `emptyDir`,** as the chart ran it
  before it had a claim, and whatever recreates that pod — deleting it, say — empties its
  databases. The operator keeps it there, as it never moves a running database by itself — a
  Postgres started on a new volume starts empty — and the `DatabasePersistent` condition says
  `EmptyDir`. The copy that moves it, `storage.postgres.migrate`
  ([B](#b-self-host-with-the-operator)), is a field newer than the CRDs such an appliance was
  built with ([updating the operator](./updating-the-operator.md#3-the-appliance)).
- **Replacing the container starts a new, empty platform.** `docker rm` and a new `docker run`
  of the command above start a new cluster whose claims get new directories — `local-path`
  names each one after its claim's UID — so even a volume mounted at k3s's storage path keeps
  the old files without attaching them.

To be able to replace the container — for a newer appliance image, or to publish another
port — start it with the whole k3s state on a named volume and a fixed host name. A container
re-created on that volume, under that name, finds the same cluster and its node — k3s names the
node after the host, and a `local-path` volume belongs to the node it was made on — so every
claim keeps its directory
([deploy/allinone](https://github.com/zaentrum/zaentrum-operator/blob/main/deploy/allinone/README.md#persistence)):

```bash
docker run -d --privileged --restart unless-stopped --name zaentrum -h zaentrum -p 80:80 \
  -v zaentrum:/var/lib/rancher/k3s ghcr.io/zaentrum/appliance:latest
```

The volume also keeps the operator install that first container brought, its CRDs included,
until a newer one is copied into it
([updating the operator](./updating-the-operator.md#3-the-appliance)).

Inspect it like any cluster — the k3s image ships `kubectl` itself:

```bash
docker exec zaentrum kubectl -n zaentrum get zaentrum      # PHASE Ready once it is up
docker exec zaentrum kubectl -n zaentrum get pods
docker exec zaentrum kubectl -n zaentrum logs deploy/katalog-manager-api
```

How the image is built lives with it, in
[`deploy/allinone`](https://github.com/zaentrum/zaentrum-operator/tree/main/deploy/allinone) in the
operator repo. For split-horizon issuer resolution see [prerequisites.md](./prerequisites.md).

---

## B. Self-host with the operator

Recommended for anyone who already runs Kubernetes and wants day-2 management (scaling,
updates, the portal's operator console). Install the operator once (cluster-admin), then apply a
`Zaentrum` CR per instance. The operator renders the embedded chart and reconciles it via
server-side apply.

### 1. Install the operator (once, cluster-admin)

```bash
kubectl apply -f https://raw.githubusercontent.com/zaentrum/zaentrum-operator/main/deploy/operator-install.yaml
```

This is the supported cluster install: one pinned manifest that creates the
`zaentrums.zaentrum.io` and `zaentrumaddons.zaentrum.io` CRDs, the operator's ClusterRoles, and
the `controller-manager` Deployment in namespace `zaentrum-operator-system`, its image pinned to
an immutable `ghcr.io/zaentrum/operator:sha-<commit>`. On OpenShift or any OLM cluster you can
instead install the OLM bundle — see
[the bundle](https://github.com/zaentrum/zaentrum-operator/tree/main/operator/bundle) in the
operator repo. What is in the manifest, object by object: [operator.md](./operator.md#install).

### 2. Apply a minimal `Zaentrum` CR

```yaml
apiVersion: zaentrum.io/v1alpha1
kind: Zaentrum
metadata:
  name: zaentrum
  namespace: zaentrum
spec:
  version: latest
  hostname: media.example.com
  identity:
    mode: bundled          # ship Keycloak; "external" uses your own OIDC provider instead
    issuerScheme: https    # TLS terminated in front of the Ingress — sign-in needs https
    clientId: chino-web
    audience: chino
  storage:
    mediaSize: 500Gi       # size the media PVC to your library
```

**https is required** on any hostname but a `localhost` name: Keycloak marks its login cookies
`Secure`, which browsers send only over https or to `localhost`, and the Android phone and TV
apps refuse plain http and trust public certificate authorities only. The chart's Ingress
carries no TLS section, so terminate TLS in front of it — your ingress controller's default
certificate, or a proxy — with a certificate your devices trust, and set
`network.issuerHostAliasIP` so in-cluster token validation reaches the https issuer (see
[prerequisites.md](./prerequisites.md#split-horizon-issuer-resolution)).

```bash
kubectl create namespace zaentrum
kubectl apply -f zaentrum.yaml
kubectl -n zaentrum get zaentrum   # Phase / Version / Host columns
```

The operator reconciles the whole platform into namespace `zaentrum`: catalog, per-product
streaming backends, bundled Postgres/Valkey/Kafka, and (in `bundled` mode) Keycloak with the
`zaentrum` realm. Chart values map 1:1 onto CR spec fields — see the
[reference table](#e-values--cr-field-reference). When the CR's `PHASE` is `Ready`, the first run
is the appliance's [three steps](#first-run) at your hostname; the library is the `media/`
folder of the `media` PVC, or of the volume you bind to it (`storage.provisionMedia: false`).

**The bundled Postgres keeps its data on a claim.** A new install puts the catalog, Keycloak's
accounts and the portal's settings on `postgres-data`, a `ReadWriteOnce` claim of
`storage.postgres.size` (default `10Gi`) from `storage.postgres.className`, else
`storage.className`, else the cluster's default StorageClass, so they outlive the pod. Where
nothing provisions such a claim, bind a PersistentVolume to a claim of your own and name it in
`storage.postgres.claimName`; the chart then makes none.

An install made before that, upgraded in place, keeps its Postgres where it runs — on an
`emptyDir`, which a reschedule, a drain or a deleted pod empties — because a Postgres started
on a new volume starts empty; the `DatabasePersistent` condition then says `EmptyDir`. Setting
`storage.postgres.migrate: true` moves it: a Job copies every database onto the claim while
Postgres keeps serving, and once the copy has succeeded the operator switches Postgres over
(`DatabasePersistent`: `Migrating` → `Migrated` → `OnClaim`; a failed copy is
`MigrationFailed`, and Postgres stays). Writes made while it copies, until the switch, are not
carried across, so do it when the platform is quiet — see
[the bundled Postgres](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/README.md#the-bundled-postgres-keeps-its-data-specstoragepostgres)
in the operator's README. A Postgres of your own is the other way: `databases.mode: external`
with `databases.external.host`, the databases created in advance (the chart then renders no
Postgres; see the `databases` comments in
[`values.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/platform/chart/values.yaml)).

### 3. Enable the media pipeline and GPU (optional)

By default the platform catalogs and streams files as-is. To run the full event-driven
pipeline (scan → enrich → analyze → transcode → package) turn on `features.pipeline`; add
`features.gpu` for NVENC hardware transcoding on a GPU node:

```yaml
spec:
  version: latest
  hostname: media.example.com
  features:
    kafka: true            # bundled single-node KRaft broker (default true)
    pipeline: true         # analyzer/packager/transcoder/katalog-ingest
    gpu: true              # NVENC on the stream/transcoder plane
  storage:
    mediaSize: 2Ti
    kafkaPvc: kafka-log    # pre-created PVC so Kafka topics survive a broker restart
    kafkaNode: <node>      # pin Kafka to the node holding a node-local kafkaPvc
```

The pipeline is pure event-driven: stage handoffs are Kafka events keyed by `item_id`
(`stube.catalog.item.discovered → .enriched → .analyzed → .transcoded`, then package to HLS).
The bundled broker (`kafka:9092`, PLAINTEXT) carries it; production can point at an external
cluster. GPU needs the NVIDIA device plugin on the GPU node.

> **Kafka durability.** With `storage.kafkaPvc` empty (the default) the broker's log dir is
> an ephemeral `emptyDir`, so topics are lost on a restart (they auto-recreate and producers
> retry, so it self-heals). Set `storage.kafkaPvc` (+ `storage.kafkaNode` for a node-local
> volume) to make topics survive restarts.

For identity, DNS, TLS, and split-horizon issuer resolution
(`network.issuerHostAliasIP`), see [prerequisites.md](./prerequisites.md). For updates and
channels, see [updating.md](./updating.md).

---

## C. `helm install` the chart

If you don't want the operator, install the same canonical chart directly, from a checkout of
the operator repo. You lose the operator's day-2 logic (scaling from the portal's operator
console, rolling each newly published image, CR reconciliation), but you get the identical
platform objects.

```bash
helm install zaentrum ./operator/platform/chart \
  --namespace zaentrum --create-namespace \
  --set global.hostname=media.example.com \
  --set identity.issuerScheme=https \
  --set features.pipeline=true \
  --set storage.mediaSize=500Gi
```

Or with a values file:

```yaml
# my-values.yaml
global:
  hostname: media.example.com
identity:
  mode: bundled
  issuerScheme: https      # TLS in front of the Ingress; plain http signs in on localhost only
features:
  kafka: true
  pipeline: true
  gpu: false
storage:
  mediaSize: 500Gi
```

```bash
helm install zaentrum ./operator/platform/chart -n zaentrum --create-namespace -f my-values.yaml
```

Chart values are grouped exactly like the CR spec (`global`, `identity`, `features`,
`storage`, `network`, `routing`, `secrets`, `databases`). The chart defaults reproduce a
plain single-node self-host; see [`values.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/platform/chart/values.yaml) and
the [reference table](#e-values--cr-field-reference). The demo profile
([`values-demo.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/platform/chart/values-demo.yaml)) shows a real override set
(HTTPS at the edge, OpenShift Routes, external secrets, external NFS media PV).

A new release puts the bundled Postgres on its `postgres-data` claim, as the operator does. An
upgrade looks at the running Postgres and keeps it where it is, so a release from before the
chart gave it a claim stays on its `emptyDir` and moves in two upgrades: one with
`storage.postgres.migrate=true`, whose post-upgrade hook copies the databases while Postgres
stays, then, once that copy has succeeded, one with `storage.postgres.current=postgres-data`
and `storage.postgres.migrate=false`, which switches it.

---

## D. k3s and Compose profiles

**Not supported today — use the [appliance](#a-one-command-appliance) for a single box, or the
[operator](#b-self-host-with-the-operator) on a cluster.**

The operator repo still carries two older profiles: `deploy/k3s/up.sh`, which creates a k3d
cluster and applies `deploy/base`, and `deploy/compose`, a Docker Compose stack behind Caddy.
Neither brings up a working platform. Both configure the catalog manager with variables the
current, Go `katalog-manager` does not read — `PG_URL`, `ADDR`, `DB_USER` / `DB_PASSWORD`,
where it reads `SPRING_DATASOURCE_*` (or `DATABASE_*`) and `SERVER_PORT` — so it gets no
database. Neither runs the portal or the catalog consoles the platform is reached through, and
the Compose stack has no identity provider at all: it leaves `OIDC_ISSUER` blank for a first-run
setup that no longer exists. They are kept only until they are brought back in line or removed.

---

## E. Values / CR-field reference

Every chart value maps 1:1 onto a `Zaentrum` CR spec field (the operator builds chart values
from the CR). The table lists both. Fields marked **CR-only** are honored by the operator's
CR but not surfaced in the chart's default `values.yaml`; the one marked **chart-only**,
`storage.postgres.current`, has no CR field, as the operator decides it from the running
Postgres.

### Global

| Chart value | CR spec | Default | Meaning |
|---|---|---|---|
| `global.version` | `spec.version` | `latest` | Image tag applied to every `ghcr.io/zaentrum/*` image. |
| `global.hostname` | `spec.hostname` | `zaentrum.localhost` | Public host: OIDC issuer host + ingress host + `KC_HOSTNAME`. |
| `global.partOf` | `spec.partOf` | `zaentrum` | `app.kubernetes.io/part-of` label value. |
| `global.imagePullSecrets` | `spec.imagePullSecrets` | `[]` | Pull secrets added to every workload (empty for public ghcr). |
| — | `spec.channel` | `stable` | **CR-only.** Release train consulted by auto-update (`stable`\|`edge`). Both point at `latest` today. |

### Identity (`identity.*` → `spec.identity`)

| Chart value | Default | Meaning |
|---|---|---|
| `mode` | `bundled` | `bundled` (ship Keycloak) or `external` (services validate tokens from your own OIDC provider; no Keycloak). The only two values — `broker` ([ADR-0007](./adr/0007-identity-modes.md)) is not built. |
| `issuer` | `""` | Explicit issuer URL; empty → derived from `issuerScheme` + `hostname` (`<scheme>://<hostname>/auth/realms/zaentrum`). |
| `issuerScheme` | `http` | `http` \| `https`. Use `https` when TLS is terminated at the edge — and serve TLS for any hostname but a `localhost` name: over plain http, sign-in fails. |
| `clientId` | `chino-web` | Public OIDC client id the web SPA authenticates as. |
| `audience` | `chino` | Expected token audience services validate against. |
| `loginTheme` | `""` | Bundled Keycloak login theme name (empty = Keycloak default). |

### Features (`features.*` → `spec.features`)

| Chart value | Default | Meaning |
|---|---|---|
| `kafka` | `true` | Bundled single-node KRaft broker for the event stream. |
| `gpu` | `false` | NVENC hardware transcoding on the stream/transcoder plane. |
| `pipeline` | `false` | Media pipeline (analyzer / packager / transcoder / katalog-ingest). |

### Storage (`storage.*` → `spec.storage`)

| Chart value | Default | Meaning |
|---|---|---|
| `mediaSize` | `50Gi` | Size of the media library PVC. |
| `className` | `""` | Optional StorageClass for platform PVCs. |
| `provisionMedia` | `true` | `false` → an external PV backs the `media` PVC (chart skips the PVC). |
| `kafkaPvc` | `""` | Name of a pre-created PVC for Kafka's log dir (topics survive restart); `""` → `emptyDir`. |
| `kafkaNode` | `""` | `kubernetes.io/hostname` to pin Kafka to (needed for a node-local `kafkaPvc`); `""` → unpinned. |
| `postgres.size` | `10Gi` | Size of the claim made for the bundled Postgres, `postgres-data` (`ReadWriteOnce`). |
| `postgres.className` | `""` | StorageClass of that claim; `""` → `className`, else the cluster's default. |
| `postgres.claimName` | `""` | An existing claim to keep the data on instead; the chart then makes none. |
| `postgres.migrate` | `false` | Copy a database that runs elsewhere — an `emptyDir`, another claim — onto the claim; the Postgres stays where it is until it is switched. |
| `postgres.current` | `""` | **Chart-only** (the operator sets it itself). Where the running Postgres's data is while it is not on the claim: `emptyDir` or a claim's name. `""` → Helm looks at the running Postgres and keeps it where it is; a new install starts on the claim. |

### Network / Routing / Secrets

| Chart value | CR spec | Default | Meaning |
|---|---|---|---|
| `network.issuerHostAliasIP` | `spec.network.issuerHostAliasIP` | `""` | Split-horizon: adds `hostAliases` (this IP → `hostname`) to OIDC validators so in-cluster token validation reaches an edge-terminated HTTPS issuer. |
| `routing.provisionIngress` | `spec.routing.provisionIngress` | `true` | Render a plain-Kubernetes Ingress (single-origin paths). |
| `routing.provisionRoutes` | `spec.routing.provisionRoutes` | `false` | Render OpenShift Routes. |
| `secrets.external` | `spec.secrets.external` | `false` | `true` → the platform's Secrets are pre-created (CI/demo) and left alone. `false` → the operator generates each one once, from `crypto/rand`, and never rotates it — the first administrator's one-time password among them; a plain `helm install` renders random ones and reads them back on every upgrade. |

### Databases (`databases.*` → `spec.databases`)

| Chart value | Default | Meaning |
|---|---|---|
| `mode` | `perApp` | `perApp` (a DB per service) or `single`, both on the bundled Postgres — on its claim (`storage.postgres`) — or `external` (your own Postgres at `databases.external.host`; the chart renders none). |
| `chino` | `chino` | Chino database name. |
| `katalog` | `katalog` | Katalog database name. |
| `keycloak` | `keycloak` | Keycloak database name. |
| `portal` | `portal` | Portal database name. |

### Keycloak / Replicas / Update

| Chart value | CR spec | Default | Meaning |
|---|---|---|---|
| `keycloak.image` | `spec.keycloak.image` | `quay.io/keycloak/keycloak:26.0.7` | Bundled Keycloak container image. |
| `services.<name>.replicas` | `spec.replicas.<name>` | `1` (chart ships `packager: 2`) | Per-service replica override by Deployment name. Stateful backers (postgres/valkey/kafka/keycloak) are **not** scalable this way. |
| — | `spec.update.mode` | `manual` | **CR-only.** `manual` (never bump `version`) or `auto` (let the reconciler track the channel) — no difference while both channels are `latest`. |

> `jobs.seed` (chart value, default `false`) enables the demo's self-populate
> scan/enqueue/topics Jobs. It is demo choreography, not part of the CR spec — leave it off
> for a real library.

---

## Getting content in

Zaentrum catalogs the `media/` folder of the platform's `media` volume, which the catalog sees
as `/var/lib/katalog/media`. Put files you own there and trigger a scan in Catalog Management
([first run](#first-run)), or register a staged file through the neutral
[ingest API](./extending/ingest.md). `katalog-manager-api` registers and manages those entries,
enriches them from TMDB once a key is set, and — with `features.pipeline` on — hands them to the
transcode/package pipeline for adaptive streaming.

> Zaentrum intentionally has **no** built-in downloaders or indexer integrations. It catalogs
> and streams files that are already on disk. How they got there is out of scope.

## Next steps

- [prerequisites.md](./prerequisites.md) — identity (OIDC), DNS, and TLS setup.
- [operator.md](./operator.md) — the full `Zaentrum` CR contract and the operator install.
- [updating.md](./updating.md) — image tags, channels, and rollouts.
- [troubleshooting.md](./troubleshooting.md) — known traps (Kafka volume switch, NVENC/driver
  mismatch, split-horizon issuer, first-login password change, sign-in over plain http, the
  admin console's 404).
- [reference-demo.md](./reference-demo.md) — the public reference deployment.
