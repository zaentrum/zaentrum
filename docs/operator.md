# Running Zaentrum with the operator

The Zaentrum operator is a Kubernetes controller that turns a single `Zaentrum`
custom resource into the whole platform — the catalog core, the media pipeline,
the per-product streaming backends, the web/mobile/TV clients, the bundled
Postgres/Valkey/Kafka, and OIDC (roughly 16 services). You declare the platform
you want in one CR; the operator reconciles it and reports progress on the CR
status.

## What the operator is, and why

The operator renders the **entire platform from one canonical Helm chart**
(`operator/platform/chart`) that is `go:embed`-ed into the operator image. The
chart values map 1:1 onto the `Zaentrum` CR spec (see the comments in
[`values.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/platform/chart/values.yaml)), so the CR *is* the
values file. On every reconcile the operator:

1. Reads the `Zaentrum` CR (CRD `zaentrums.zaentrum.io`, apiVersion
   `zaentrum.io/v1alpha1`, kind `Zaentrum`, namespace-scoped).
2. Builds chart values from the spec and renders the embedded chart as a pure
   template engine (client-side render — not `helm install`).
3. Applies every rendered object via **server-side apply (SSA)**, so it owns the
   fields it manages and continually corrects drift.
4. Writes back `status` — `phase`, `currentVersion`, `availableUpdate`, and a
   per-Deployment `components[]` list of `ready`/`image` — so you can watch the
   rollout converge.

Because the chart is embedded in the operator image, this is also the **day-2**
control loop: it reconciles on CR changes and on a resync interval, keeps the
declared replica counts (a raw `Deployment` edit is reverted on the next pass),
and — with `spec.update.mode: auto` — tracks the configured release `channel`
and rolls new in-channel image tags itself, surfacing the next version on
`status.availableUpdate` before it applies it.

> **A chart change is not a live change.** The chart ships *inside* the operator
> image. Editing `operator/platform/chart/**` has no effect until the operator
> image is rebuilt and the operator is rolled. See [updating.md](./updating.md).

The same CR is the unit of configuration in every deploy topology — the
all-in-one appliance, self-host on your own cluster (see
[self-hosting.md](./self-hosting.md)), and the reference demo (see
[reference-demo.md](./reference-demo.md)). `/manage` reads and writes this CR
through the operator.

## Install

Installing the operator applies its manifest bundle — the CRD, the cluster
RBAC, and the controller-manager Deployment into the `zaentrum-operator-system`
namespace. This is a one-time, **cluster-admin bootstrap** step (see
[prerequisites.md](./prerequisites.md) for cluster requirements).

```bash
oc apply -f deploy/operator-install.yaml
```

This creates, from [`deploy/operator-install.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/deploy/operator-install.yaml):

| Object | Name | Purpose |
|---|---|---|
| `Namespace` | `zaentrum-operator-system` | Where the controller runs. |
| `CustomResourceDefinition` | `zaentrums.zaentrum.io` | The `Zaentrum` CR type (shortName `stb`). |
| `ServiceAccount` | `zaentrum-operator-controller-manager` | The controller identity. |
| `ClusterRole` / `ClusterRoleBinding` | `zaentrum-operator-manager-role` | Manage namespaces, Deployments, Services, ConfigMaps, Secrets, PVCs, Jobs, Ingresses, OpenShift Routes, Roles/RoleBindings, and `zaentrums`. |
| `ClusterRole` / `ClusterRoleBinding` | `zaentrum-operator-leader-election-role` | Leader-election leases + events. |
| `Deployment` | `zaentrum-operator-controller-manager` | The controller (`/manager --leader-elect`, image `ghcr.io/zaentrum/operator:<tag>`). |

Confirm the controller is running:

```bash
oc -n zaentrum-operator-system rollout status deploy/zaentrum-operator-controller-manager
oc -n zaentrum-operator-system get pods
```

Then create a namespace for the platform and apply a `Zaentrum` CR into it
(examples below). Watch it converge with the printer columns from the CRD:

```bash
kubectl -n zaentrum get zaentrum -w
# NAME       PHASE         VERSION   HOST                AGE
# zaentrum   Reconciling   latest    zaentrum.localhost   30s
# zaentrum   Ready         latest    zaentrum.localhost   3m
```

## Zaentrum CR spec reference

Every field of `spec` (authoritative source:
[`operator/api/v1alpha1/zaentrum_types.go`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/api/v1alpha1/zaentrum_types.go)).
Defaults are the CRD-embedded defaults; a self-host deployment can leave most of
them unset.

### Top level

| Field | Type | Default | Meaning |
|---|---|---|---|
| `spec.version` | string | `latest` | Image tag applied to **every** `ghcr.io/zaentrum/*` image. |
| `spec.channel` | enum `stable` \| `edge` | `stable` | Release train consulted by auto-update. |
| `spec.hostname` | string | `zaentrum.localhost` | The single public host: OIDC issuer host + ingress/route host + Keycloak `KC_HOSTNAME`. |
| `spec.partOf` | string | the namespace | `app.kubernetes.io/part-of` label value on all workloads. |
| `spec.imagePullSecrets` | []string | `[]` | Pull secret names added to every workload (private registries; empty for public ghcr). |
| `spec.replicas` | map[string]int32 | `{}` | Per-Deployment replica overrides by name, e.g. `{"chino-api": 2, "katalog-api": 3}`. Unlisted app services stay at 1. Stateful backers (postgres/valkey/kafka/keycloak) are **not** scalable this way. Set from the portal operator console; the operator reconciles it so the change persists. |

### `spec.identity` — OIDC

| Field | Type | Default | Meaning |
|---|---|---|---|
| `identity.mode` | enum `bundled` \| `external` | `bundled` | `bundled` ships in-cluster Keycloak + the `zaentrum` realm import; `external` federates and does not render Keycloak. |
| `identity.issuer` | string | — | Explicit public issuer URL. Empty in bundled mode → derived as `<scheme>://<hostname>/auth/realms/zaentrum`. |
| `identity.issuerScheme` | enum `http` \| `https` | `http` | Scheme of the derived issuer + Keycloak `KC_HOSTNAME`. Use `https` when TLS is terminated at the edge. |
| `identity.clientId` | string | `chino-web` | Public OIDC client id the web SPA authenticates as. |
| `identity.audience` | string | `chino` | Expected token audience services validate against. |
| `identity.loginTheme` | string | — (Keycloak default) | Bundled Keycloak login theme name (the demo uses `zaentrum`). |

### `spec.features`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `features.kafka` | bool | `true` | Run the bundled single-node KRaft broker (`kafka:9092`, PLAINTEXT). |
| `features.gpu` | bool | `false` | Enable hardware (NVENC) transcoding on the stream plane (needs a GPU node + device plugin). |
| `features.pipeline` | bool | `false` | Enable the media pipeline (analyzer / packager / transcoder / katalog-ingest). |

### `spec.storage`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `storage.mediaSize` | quantity | `50Gi` | Size of the media library PVC. |
| `storage.className` | string | cluster default | Optional StorageClass for platform PVCs. |
| `storage.provisionMedia` | \*bool | `true` | Whether the chart creates the `media` PVC. Set `false` when an external PV backs it (e.g. an NFS export). |
| `storage.kafkaPvc` | string | `""` | Name of a **pre-created** PVC to back the bundled Kafka log dir so **topics survive a pod restart/reschedule**. Empty → ephemeral `emptyDir`. |
| `storage.kafkaNode` | string | `""` | Pin the bundled Kafka broker to a node (`kubernetes.io/hostname`). Required when `kafkaPvc` is a node-local volume. Empty → unpinned. |

> Bundled Kafka defaults to `emptyDir`, so **topics are lost on a broker
> restart** unless `storage.kafkaPvc` is set. Topics auto-create and
> katalog-manager retries transient produce errors, so the pipeline self-heals;
> setting `kafkaPvc` (+ `kafkaNode` for node-local volumes) makes it durable.
> Switching an existing broker from `emptyDir` to a PVC is a known trap — see
> [troubleshooting.md](./troubleshooting.md).

### `spec.network`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `network.issuerHostAliasIP` | string | `""` | Adds a `hostAliases` entry (this IP → the public host) to the OIDC validators so **in-cluster** token validation reaches an edge-terminated HTTPS issuer (split-horizon). Empty → no `hostAliases`. |

### `spec.routing`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `routing.provisionIngress` | \*bool | `true` | Render a plain-Kubernetes `Ingress` (single-origin paths). |
| `routing.provisionRoutes` | \*bool | `false` | Render OpenShift `Route`s (single-origin paths). Enable on OKD/OpenShift. |

### `spec.secrets`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `secrets.external` | bool | `false` | `true` → platform secrets are pre-created (e.g. by CI); the chart does not render them. `false` → bundled dev-default secrets. |

### `spec.databases`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `databases.mode` | string `perApp` \| `single` | `perApp` | `perApp` gives each service its own database; `single` shares one. |
| `databases.chino` | string | `chino` | chino database name. |
| `databases.katalog` | string | `katalog` | katalog database name. |
| `databases.keycloak` | string | `keycloak` | keycloak database name. |
| `databases.portal` | string | `portal` | portal database name. |

### `spec.keycloak`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `keycloak.image` | string | `quay.io/keycloak/keycloak:26.0.7` | Bundled Keycloak container image (bundled identity mode only). |

### `spec.update`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `update.mode` | enum `manual` \| `auto` | `manual` | `manual` never bumps `spec.version` on its own; `auto` lets the reconciler bump to the latest in-`channel` tag. |

### Status (read-only)

`status.phase`, `status.currentVersion`, `status.availableUpdate`,
`status.observedGeneration`, `status.conditions[]` (standard Kubernetes
conditions), and `status.components[]` (`name`, `ready`, `image` per managed
Deployment).

## Example CRs

### Minimal self-host

A single-node self-host on your own cluster: bundled identity, bundled Kafka, a
50 GiB media PVC on the default StorageClass, plain-Kubernetes Ingress, manual
updates. Everything else takes its default.

```yaml
apiVersion: zaentrum.io/v1alpha1
kind: Zaentrum
metadata:
  name: zaentrum
  namespace: zaentrum
spec:
  version: latest
  hostname: zaentrum.example.com      # the one public host — set to your real host
  identity:
    mode: bundled
    clientId: chino-web
    audience: chino
  features:
    kafka: true                     # bundled broker
    gpu: false
    pipeline: true                  # scan → enrich → analyze → transcode → package
  storage:
    mediaSize: 50Gi
    kafkaPvc: kafka-log             # optional: durable topics (pre-create the PVC)
  routing:
    provisionIngress: true
  update:
    mode: manual
```

Set `spec.hostname` to the public host you will reach Zaentrum at. In bundled
mode the operator derives the OIDC issuer, the ingress/route host, and Keycloak's
`KC_HOSTNAME` from that single name. When `status.phase` reaches `Ready`, open
`https://<hostname>` and finish first-run setup at `/manage/setup`.

### Reference-demo profile

The public demo (`zaentrum.demo.nalet.cloud`, namespace `zaentrum-demo`) runs on
an OKD cluster with edge-terminated TLS, an external NFS PV for media, and
CI-created secrets. It corresponds to
[`values-demo.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/platform/chart/values-demo.yaml). Full deploy
mechanics are in [reference-demo.md](./reference-demo.md).

```yaml
apiVersion: zaentrum.io/v1alpha1
kind: Zaentrum
metadata:
  name: zaentrum
  namespace: zaentrum-demo
spec:
  version: latest
  hostname: zaentrum.demo.nalet.cloud
  partOf: zaentrum-demo
  imagePullSecrets: [ghcr-pull, registry-pull]   # names of pre-created pull secrets
  identity:
    mode: bundled
    issuerScheme: https             # TLS terminated at the OpenShift router
    loginTheme: zaentrum
  features:
    kafka: true
    pipeline: true                  # the demo runs the full media pipeline
    gpu: true                       # NVENC on a GPU node
  storage:
    provisionMedia: false           # an external NFS PV backs the media PVC
    kafkaPvc: kafka-log             # node-local PV → durable topics
    kafkaNode: <node>               # pin the broker to the node holding that PV
  network:
    issuerHostAliasIP: "<router-ip>"   # HostNetwork router IP → split-horizon issuer
  routing:
    provisionIngress: false
    provisionRoutes: true           # single-origin OpenShift Routes
  secrets:
    external: true                  # zaentrum-* secrets pre-created by CI
```

The demo deliberately keeps a few things the operator does **not** render: the
media PVC (`storage.provisionMedia: false`), the CI-created secrets
(`secrets.external: true`), and the seed/scan/enqueue/kafka-topics choreography
Jobs. See [reference-demo.md](./reference-demo.md).

## Updating

- **A CR value change** (e.g. bump `spec.version`, change `spec.replicas`): edit
  the CR and re-apply; the operator reconciles it via SSA.
- **An app image change**: push the app repo → GitHub Actions builds
  `ghcr.io/zaentrum/<app>:latest`; roll the app tier to pull it (the demo CI does
  a `rollout restart`, excluding postgres/valkey/kafka).
- **A chart or operator-code change**: rebuild and roll the operator image — the
  embedded chart re-renders only after that. See [updating.md](./updating.md).

For the operator's own auto-update loop (`spec.update.mode: auto` /
`spec.channel`), the reconciler tracks the channel and surfaces the next tag on
`status.availableUpdate` before rolling it.

See also: [prerequisites.md](./prerequisites.md) ·
[self-hosting.md](./self-hosting.md) · [reference-demo.md](./reference-demo.md) ·
[updating.md](./updating.md) · [troubleshooting.md](./troubleshooting.md)
