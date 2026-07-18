# Self-hosting Zaentrum

Zaentrum is a neutral self-host media platform — a catalog, a media pipeline, and clean
web/mobile/TV clients for a library **you own and are entitled to stream**. It ships no
content and no downloaders: you point it at files that are already on disk.

The platform is one canonical Helm chart (`operator/platform/chart`) that is `go:embed`-ed
into the operator image and driven by a single `Zaentrum` custom resource. Everything is a
container at `ghcr.io/zaentrum/<service>` on the public GitHub Container Registry. This page
covers the five ways to run it:

| Path | Audience | Section |
|---|---|---|
| One-command appliance | Fastest start, single box | [A](#a-one-command-appliance) |
| Operator on your own Kubernetes | You run k8s; want day-2 management | [B](#b-self-host-with-the-operator) |
| `helm install` the chart directly | You run k8s; don't want the operator | [C](#c-helm-install-the-chart) |
| k3s (`up.sh`) profile | Local single-node k8s, non-appliance | [D](#d-k3s-and-compose-profiles) |
| Docker Compose profile | NAS / single box, no Kubernetes | [D](#d-k3s-and-compose-profiles) |

Before you start, read [prerequisites.md](./prerequisites.md) for identity (OIDC), DNS, and
TLS. For the full `Zaentrum` CR contract see [operator.md](./operator.md); the public
reference deployment is documented in [reference-demo.md](./reference-demo.md).

---

## A. One-command appliance

The whole platform in **one container**. The image bundles a single-node
[k3s](https://k3s.io) and the rendered `deploy/base` manifests; k3s auto-applies them on
boot. Zero-clone — nothing to check out.

```bash
docker run -d --privileged --name zaentrum -p 8080:80 ghcr.io/zaentrum/appliance:latest
```

Then open <http://localhost:8080> (or map `-p 80:80` and use <http://zaentrum.localhost> —
modern browsers resolve `*.localhost` to `127.0.0.1` with no `/etc/hosts` edit). First boot
pulls the application images and runs the database migrations, so give it a minute.

**Why `--privileged`?** The container runs k3s, which needs to mount filesystems, manage
cgroups, and run an embedded containerd for the app pods. `--privileged` is the supported
default; hardened setups can pass the narrower capability/mount set k3s documents instead.

### First-run wizard

Sign-in uses the **bundled Keycloak** (realm `zaentrum`): log in with its admin account
(`admin` / `dev` by default), which forces a password change on first login. On first boot
nothing is configured, so the app routes you to the setup wizard at **`/manage/setup`**
(served by the admin UI, backed by `katalog-manager-api`). The flow is driven by one status
endpoint:

```
GET /api/manage/setup/status
    -> { configured: false, checks: { database: true, kafka: true, library: false } }
```

While `configured` is `false`, visitors are routed to the wizard, which submits:

```
POST /api/manage/setup
     { "displayName": "My Library",
       "oidcIssuer":  "https://auth.example.com/realms/zaentrum",
       "oidcClientId":"chino",
       "libraryPath": "/var/lib/zaentrum/media" }
```

If you don't supply a `streamSigningKey`, one is generated so playback works immediately.
Revisit settings any time under `/manage` (`GET`/`PUT /api/manage/config`).

### Persistence

Everything (Postgres, the Kafka log, the media library, the HLS cache) lives on PVCs backed
by k3s's `local-path` StorageClass, i.e. inside the container's writable layer. To keep data
across `docker rm`, mount a host directory at k3s's storage path:

```bash
docker run -d --privileged --name zaentrum -p 8080:80 \
  -v zaentrum-data:/var/lib/rancher/k3s/storage \
  ghcr.io/zaentrum/appliance:latest
```

Inspect it like any cluster:

```bash
docker exec -it zaentrum k3s kubectl -n zaentrum get pods
docker exec -it zaentrum k3s kubectl -n zaentrum logs deploy/katalog-manager-api
```

For running under a non-localhost name, airgap, and build details see
[`deploy/allinone/README.md`](https://github.com/zaentrum/zaentrum-operator/blob/main/deploy/allinone/README.md). For split-horizon issuer
resolution see [prerequisites.md](./prerequisites.md).

---

## B. Self-host with the operator

Recommended for anyone who already runs Kubernetes and wants day-2 management (scaling,
channel updates, `/manage`). Install the operator once (cluster-admin), then apply a
`Zaentrum` CR per instance. The operator renders the embedded chart and reconciles it via
server-side apply.

### 1. Install the operator (once, cluster-admin)

```bash
kubectl apply -f deploy/operator-install.yaml
```

This creates the `zaentrums.zaentrum.io` CRD, the operator's ClusterRoles, and the
`controller-manager` Deployment in namespace `zaentrum-operator-system`. On OpenShift or any
OLM cluster you can instead install the OLM bundle — see [operator.md](./operator.md).

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
    mode: bundled          # ship Keycloak; use "external" to federate your IdP
    clientId: chino-web
    audience: chino
  storage:
    mediaSize: 500Gi       # size the media PVC to your library
```

```bash
kubectl create namespace zaentrum
kubectl apply -f zaentrum.yaml
kubectl -n zaentrum get zaentrum   # Phase / Version / Host columns
```

The operator reconciles the whole platform into namespace `zaentrum`: catalog, per-product
streaming backends, bundled Postgres/Valkey/Kafka, and (in `bundled` mode) Keycloak with the
`zaentrum` realm. Chart values map 1:1 onto CR spec fields — see the
[reference table](#e-values--cr-field-reference).

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

If you don't want the operator, install the same canonical chart directly. You lose the
operator's day-2 logic (`/manage`-driven scaling, channel auto-update, CR reconciliation),
but you get the identical platform objects.

```bash
helm install zaentrum ./operator/platform/chart \
  --namespace zaentrum --create-namespace \
  --set global.hostname=media.example.com \
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

---

## D. k3s and Compose profiles

Two profiles for people who don't want to install the operator or `helm install` a full
cluster. Both use the same `ghcr.io/zaentrum/*` images.

### k3s (`deploy/k3s/up.sh`)

A local single-node cluster via [k3d](https://k3d.io) (k3s in Docker) that applies
`deploy/base`. This is for hacking on the manifests; for a turnkey box prefer the
[appliance](#a-one-command-appliance).

```bash
./deploy/k3s/up.sh          # create k3d cluster + apply deploy/base
./deploy/k3s/up.sh down     # tear the cluster down
```

Requires `docker`, `k3d`, and `kubectl`. It maps the cluster ingress to `localhost:8080`
(`8080:80@loadbalancer`), so open <http://zaentrum.localhost:8080>. For a LAN name set the
host consistently in `deploy/base/ingress.yaml`, `OIDC_ISSUER`, and `KC_HOSTNAME`.

### Docker Compose (`deploy/compose`)

A lighter front door for a NAS / single box — no Kubernetes. A single **Caddy** reverse proxy
on `:8080` fronts everything, mirroring the k8s route map:

| Path | Service |
|---|---|
| `/api/manage` | `katalog-manager-api` (neutral write API) |
| `/manage` | `admin` (management UI, SPA; first run opens `/manage/setup`) |
| `/api` | `chino-api` (product BFF) |
| `/` | `chino-web` (the main app, static SPA) |

```bash
cd deploy/compose
STUBE_MEDIA=/path/to/your/library docker compose up -d
```

Point `STUBE_MEDIA` at a directory of media you own; it is mounted read-only into
`chino-stream` at `/media`. Software transcode by default (no GPU) — for hardware transcode
use the appliance + GPU, or add an NVIDIA device reservation. The stack bundles
`postgres:16-alpine`, `valkey/valkey:8-alpine`, and a single-node KRaft
`apache/kafka:3.8.0` broker (`kafka:9092`). Set `OIDC_ISSUER` in the compose file to your
provider, or leave it blank for first-run setup.

> The Compose defaults use `-dev-change-me` passwords and a dev stream-signing key. Change
> them (Postgres credentials, `STREAM_SIGNING_KEY` shared by `chino-api` and `chino-stream`)
> before exposing the stack.

---

## E. Values / CR-field reference

Every chart value maps 1:1 onto a `Zaentrum` CR spec field (the operator builds chart values
from the CR). The table lists both. Fields marked **CR-only** are honored by the operator's
CR but not surfaced in the chart's default `values.yaml`.

### Global

| Chart value | CR spec | Default | Meaning |
|---|---|---|---|
| `global.version` | `spec.version` | `latest` | Image tag applied to every `ghcr.io/zaentrum/*` image. |
| `global.hostname` | `spec.hostname` | `zaentrum.localhost` | Public host: OIDC issuer host + ingress host + `KC_HOSTNAME`. |
| `global.partOf` | `spec.partOf` | `zaentrum` | `app.kubernetes.io/part-of` label value. |
| `global.imagePullSecrets` | `spec.imagePullSecrets` | `[]` | Pull secrets added to every workload (empty for public ghcr). |
| — | `spec.channel` | `stable` | **CR-only.** Release train consulted by auto-update (`stable`\|`edge`). |

### Identity (`identity.*` → `spec.identity`)

| Chart value | Default | Meaning |
|---|---|---|
| `mode` | `bundled` | `bundled` (ship Keycloak) or `external` (federate an existing IdP). |
| `issuer` | `""` | Explicit issuer URL; empty → derived from `issuerScheme` + `hostname` (`<scheme>://<hostname>/auth/realms/zaentrum`). |
| `issuerScheme` | `http` | `http` \| `https`. Use `https` when TLS is terminated at the edge. |
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

### Network / Routing / Secrets

| Chart value | CR spec | Default | Meaning |
|---|---|---|---|
| `network.issuerHostAliasIP` | `spec.network.issuerHostAliasIP` | `""` | Split-horizon: adds `hostAliases` (this IP → `hostname`) to OIDC validators so in-cluster token validation reaches an edge-terminated HTTPS issuer. |
| `routing.provisionIngress` | `spec.routing.provisionIngress` | `true` | Render a plain-Kubernetes Ingress (single-origin paths). |
| `routing.provisionRoutes` | `spec.routing.provisionRoutes` | `false` | Render OpenShift Routes. |
| `secrets.external` | `spec.secrets.external` | `false` | `true` → secrets are pre-created (CI/demo); chart skips rendering them. |

### Databases (`databases.*` → `spec.databases`)

| Chart value | Default | Meaning |
|---|---|---|
| `mode` | `perApp` | `perApp` (a DB per service) or `single`. |
| `chino` | `chino` | Chino database name. |
| `katalog` | `katalog` | Katalog database name. |
| `keycloak` | `keycloak` | Keycloak database name. |
| `portal` | `portal` | Portal database name. |

### Keycloak / Replicas / Update

| Chart value | CR spec | Default | Meaning |
|---|---|---|---|
| `keycloak.image` | `spec.keycloak.image` | `quay.io/keycloak/keycloak:26.0.7` | Bundled Keycloak container image. |
| `services.<name>.replicas` | `spec.replicas.<name>` | `1` (chart ships `packager: 2`) | Per-service replica override by Deployment name. Stateful backers (postgres/valkey/kafka/keycloak) are **not** scalable this way. |
| — | `spec.update.mode` | `manual` | **CR-only.** `manual` (never bump `version`) or `auto` (let the reconciler track the channel). |

> `jobs.seed` (chart value, default `false`) enables the demo's self-populate
> scan/enqueue/topics Jobs. It is demo choreography, not part of the CR spec — leave it off
> for a real library.

---

## Getting content in

Point Zaentrum at a directory of media you own. `katalog-manager-api` registers and manages
those entries; the catalog core enriches metadata and (optionally) transcodes/packages for
adaptive streaming.

> Zaentrum intentionally has **no** built-in downloaders or indexer integrations. It catalogs
> and streams files that are already on disk. How they got there is out of scope.

## Next steps

- [prerequisites.md](./prerequisites.md) — identity (OIDC), DNS, and TLS setup.
- [operator.md](./operator.md) — the full `Zaentrum` CR contract and OLM install.
- [updating.md](./updating.md) — image tags, channels, and rollouts.
- [troubleshooting.md](./troubleshooting.md) — known traps (Kafka volume switch, NVENC/driver
  mismatch, split-horizon issuer, first-login password change).
- [reference-demo.md](./reference-demo.md) — the public reference deployment.
