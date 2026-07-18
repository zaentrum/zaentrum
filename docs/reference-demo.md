# Reference demo: how a public demo is deployed

This page is a **generic worked example** of a real GitOps deploy of an
operator-managed Zaentrum platform — how an entire ~16-service platform is
rendered from a single `Zaentrum` CR and rolled out by a CI job. It is a
companion to the more general [self-hosting.md](./self-hosting.md) and
[operator.md](./operator.md).

> The full cluster-specific runbook (our exact hostnames, nodes, CI variables, and
> cluster-admin steps) is maintained internally for maintainers. This page uses
> `<placeholders>` throughout so it reads as a reusable pattern rather than one
> cluster's configuration.

A working instance of this exact deploy is browsable at the public demo,
**`https://zaentrum.demo.nalet.cloud`**.

The demo runs in a dedicated namespace (`<deploy-namespace>`) on an OKD cluster.
The whole ~16-service platform is rendered by the
[zaentrum-operator](./operator.md) from a single `Zaentrum` CR out of its embedded
canonical Helm chart. Deploys are driven by a **CI job** in a deploy-only
repository — the manifests referenced throughout live in your deploy repo (a
private, deploy-only repo) under a `demo/` overlay. This operator repo is the
public source-of-truth for the operator and chart; the deploy manifests are kept
in a separate deploy-only repo because they are deploy-only.

The deploy is best understood as four layers, from the outside in:

| Layer | What | Who / when |
|---|---|---|
| 0 | External, pre-existing infrastructure | Not managed here |
| 1 | One-time cluster-admin bootstrap | Cluster-admin, run once |
| 2 | The repeatable CI deploy | CI, every deploy |
| 3 | Verify | Read-only checks, after every deploy |

---

## Layer 0 — External / pre-existing

These exist independently of the demo and are not created by the deploy:

| Thing | Detail |
|---|---|
| OKD cluster | Edge-terminated TLS at the router; the public host (`<cluster-domain>`) already routes to the edge load balancer. |
| Media NFS export | `<nfs-server>:/media-demo`, exported RWX with permissive squash (the seed Job writes as an arbitrary UID). **Creative-Commons / own content ONLY** — never point the demo at production media. |
| Split-horizon DNS | In-cluster, the demo hostname must resolve to the OKD router IP so the in-cluster OIDC validators can reach the edge-terminated issuer TLS. The CR pins this via `network.issuerHostAliasIP` (see [Layer 2](#the-cr)). |
| Container images | `ghcr.io/zaentrum/*:latest` on the public GitHub Container Registry, built by GitHub Actions from the app repos. |
| GHCR pull credentials | A GitHub PAT with `read:packages`, supplied to CI (see [CI variables](#ci-variables)). |
| A registry pull secret | The demo CI can copy an existing image-pull secret out of another namespace on the same cluster into the demo namespace (optional, cluster-dependent). |

---

## Layer 1 — One-time cluster-admin bootstrap

The CI deploy token is a namespace-scoped ServiceAccount and **cannot** create
cluster-scoped resources (CRDs, `Namespace`, `PersistentVolume`) or bind a cluster
SCC. So a cluster-admin runs these steps once, out of band from CI. Source: the
`demo/bootstrap.yaml` in the deploy repo and the operator install manifest in this
repo.

### 1a. Install the operator (CRD + ClusterRoles + controller)

```bash
oc apply -f https://raw.githubusercontent.com/zaentrum/zaentrum-operator/main/deploy/operator-install.yaml
oc -n zaentrum-operator-system rollout status deploy/zaentrum-operator-controller-manager
```

This installs the `zaentrums.zaentrum.io` CRD, the operator ClusterRoles, and the
controller-manager in namespace `zaentrum-operator-system`.

### 1b. Bootstrap the namespace (`bootstrap.yaml`)

```bash
oc apply -f demo/bootstrap.yaml
```

This single file creates everything cluster-scoped or privileged that the
namespaced CI deployer cannot:

| Resource | Purpose |
|---|---|
| `Namespace/<deploy-namespace>` | The target namespace. |
| `PersistentVolume` (media NFS) | Static NFS PV → `<nfs-server>:/media-demo` (200Gi, RWX, `Retain`), `claimRef` pinned to the `media` PVC. |
| `PersistentVolume` (Kafka log dir) | Node-local PV (20Gi, RWO, local-storage class) for the bundled Kafka log dir, `nodeAffinity` pinned to `<node>`, `claimRef` to the `kafka-data` PVC. Backs persistent Kafka so **topics + consumer offsets survive a broker restart**. |
| `RoleBinding/deployer-admin` | Grants the `<deploy-sa>` SA the `admin` ClusterRole on the demo namespace. |
| `Role`+`RoleBinding/zaentrum-deployer` | Grants the deployer explicit `zaentrums` rights (the built-in `admin` role does not cover custom resources) so CI can apply the CR. |
| `RoleBinding/kafka-anyuid` | Grants the bundled `kafka` SA the `anyuid` SCC (apache/kafka writes config as uid 1000). |
| `ClusterRole`+`ClusterRoleBinding` (ns-get) | Grants the deployer two cluster-scoped reads — `get` on the demo `Namespace` and on `customresourcedefinitions/zaentrums.zaentrum.io`, both `resourceNames`-scoped — for the deploy job's pre-flight guards. |

### 1c. Create the Kafka PV host directory

The node-local Kafka PV points at a host path that must exist and be writable
before the PVC can bind. On the pinned node:

```bash
oc debug node/<node>
# in the debug shell:
chroot /host mkdir -p /var/local-storage/a/pv/zaentrum-demo-kafka
chroot /host chmod 0777 /var/local-storage/a/pv/zaentrum-demo-kafka   # kafka runs as uid 1000
```

### CI variables

Set once, in your CI. Group-level variables are shared across the deploy group;
project-level variables live on the deploy project.

| Scope | Variable | What it is |
|---|---|---|
| Group | `OC_SERVER` | OKD API server URL. |
| Group | `OC_TOKEN` | A **long-lived deployer SA token** (see the mint recipe below). |
| Project | `DEMO_DB_PW` | Bundled Postgres password (throwaway). |
| Project | `DEMO_MANAGER_SECRET` | Keycloak client secret for the manager/pipeline client. |
| Project | `DEMO_KC_ADMIN_PW` | Bundled Keycloak admin password. |
| Project | `DEMO_REALM_ADMIN_PW` | `zaentrum` realm admin password. |
| Project | `DEMO_USER_PW` | Optional demo end-user password (seeds the realm `demo` user on a fresh import only). |
| Project | `GHCR_PULL_TOKEN` | GitHub PAT with `read:packages` for `ghcr.io/zaentrum/*` pulls. |
| Project | `GHCR_PULL_USER` | GitHub username for the GHCR pull secret (defaults to `zaentrum`). |
| Group / project | `CI_ENABLED` | Must be `"true"` or the whole pipeline stays dormant. |

Mint the deployer token as a cluster-admin and set it as `OC_TOKEN`:

```bash
oc create token <deploy-sa> -n <deploy-namespace> --duration=<long>
```

> **Trap:** if `OC_TOKEN` expires the deploy fails pre-flight with `ns
> <deploy-namespace> missing`. Refresh it with a new long-lived deployer token. See
> [troubleshooting.md](./troubleshooting.md).

---

## Layer 2 — The repeatable deploy

Everything namespaced is applied by the CI deploy job (source: the pipeline
definition in the deploy repo). It is **main-only**, **manual**, and gated on
`CI_ENABLED == "true"`. It runs a public `origin-cli` image and authenticates as
the deployer SA from the group `OC_SERVER` / `OC_TOKEN`.

### The CR

The platform is one `Zaentrum` custom resource (`apiVersion:
zaentrum.io/v1alpha1`). The demo profile maps 1:1 onto the chart's
`values-demo.yaml`. Key fields:

```yaml
apiVersion: zaentrum.io/v1alpha1
kind: Zaentrum
metadata:
  name: zaentrum
  namespace: <deploy-namespace>
spec:
  version: latest                       # every ghcr.io/zaentrum/* image tracks :latest
  hostname: <hostname>                  # OIDC issuer host + Route host + KC_HOSTNAME
  partOf: zaentrum-demo
  imagePullSecrets: [ghcr-pull, gitlab-registry]
  identity:
    issuerScheme: https                 # TLS terminates at the OKD router
    loginTheme: zaentrum
  features:
    kafka: true
    pipeline: true                      # full media pipeline: analyzer/packager/transcoder/katalog-ingest
  storage:
    provisionMedia: false               # the external media PVC is applied by CI, not the operator
    kafkaPvc: kafka-data                # persistent Kafka log dir → node-local PV
    kafkaNode: <node>
  network:
    issuerHostAliasIP: "<router-ip>"    # in-cluster split-horizon to the router for OIDC validation
  routing:
    provisionIngress: false
    provisionRoutes: true               # single-origin OpenShift Routes
  secrets:
    external: true                      # zaentrum-* secrets are pre-created by CI
  databases:
    mode: perApp
```

### What the operator does NOT render

The demo deliberately keeps a few resources outside the operator; the CI overlay
(`kustomization.yaml`) carries them alongside the CR:

| Kept out | CR flag | Why |
|---|---|---|
| The `media` PVC | `storage.provisionMedia: false` | The operator consumes the existing PVC bound to the NFS PV. |
| The `zaentrum-*` secrets | `secrets.external: true` | CI creates them from the `DEMO_*` variables (the only secret path allowed from CI). |
| The `kafka-data` PVC | `storage.kafkaPvc: kafka-data` | Binds the node-local Kafka PV from bootstrap. |
| The seed / scan / enqueue / kafka-topics Jobs | operator forces `jobs.seed=false` | Demo choreography (populate + drive the pipeline), never rendered by the operator. |

### Job steps

The deploy job script, in order:

1. **Pre-flight guards.** Require the `DEMO_*` + `OC_SERVER` + `OC_TOKEN`
   variables; then `kubectl get ns <deploy-namespace>` and `kubectl get crd
   zaentrums.zaentrum.io` — both fail with a clear message pointing at the Layer 1
   bootstrap if missing.
2. **Create the demo secrets** with `kubectl create secret --dry-run=client -o
   yaml | kubectl apply -f -`: `zaentrum-db`, `zaentrum-stream-signing` (random
   32-byte key), `zaentrum-keycloak`, `zaentrum-keycloak-admin`, and optionally
   `zaentrum-demo-user`.
3. **Copy an image-pull secret** from another namespace on the cluster into the
   demo namespace (optional, cluster-dependent).
4. **Create the `ghcr-pull` secret** from `GHCR_PULL_TOKEN` / `GHCR_PULL_USER`
   (if set) and add it to the `default` SA's `imagePullSecrets`. If unset, an
   existing in-namespace `ghcr-pull` from a prior deploy persists.
5. **Delete the finished choreography Jobs** (`kafka-topics`, `seed-demo-content`,
   `scan-catalog`, `enqueue-processing`) so `apply -k` recreates them fresh — Jobs
   are immutable.
6. **`kubectl apply -k demo`** — applies the CR, the two external PVCs, and the
   choreography Jobs. The operator picks up the CR and reconciles the platform via
   server-side apply (async).
7. **Wait for the operator to render** — poll up to ~2 min for
   `deploy/zaentrum-portal` to appear.
8. **Rollout-restart the app tiers** to pick up config, **excluding** the stateful
   backers (`postgres` / `valkey` / `kafka` — restarting them would wipe DB / topic
   / session state), then `rollout status deploy/keycloak`.
9. **Print CR status + workloads** (`kubectl get zaentrum,pods,routes`).

The choreography Jobs recreated by step 6 run once the platform is up:

| Job | Does |
|---|---|
| `kafka-topics` | Creates the pipeline topics with deterministic partitions/retention: `stube.catalog.item.discovered/enriched/analyzed/transcoded` (idempotent, `--if-not-exists`). |
| `seed-demo-content` | Downloads Creative-Commons / public-domain titles to `/var/lib/katalog/media` on the NFS export (skip-if-present, tolerant of dead links). |
| `scan-catalog` | Mints a client-credentials token from bundled Keycloak and triggers the filesystem scan; the scan emits `stube.catalog.item.discovered` and the event-driven pipeline (enrich → analyze → transcode → package) takes over. |
| `enqueue-processing` | Harmless backfill for items that predate the event flow. |

### Trigger the deploy

The job is manual, so trigger a pipeline on `main` and then play the manual job:

```bash
glab ci run -b main -R <deploy-repo>
# then, in the CI UI or CLI, play the manual demo deploy job
```

---

## Layer 3 — Verify

Read-only checks after the deploy (no cluster mutation needed):

```bash
# 1. The operator reports the platform Ready.
oc -n <deploy-namespace> get zaentrum
#   → PHASE should be Ready; status.components all ready.

# 2. All pods up (postgres → keycloak → services).
oc -n <deploy-namespace> get pods

# 3. Pipeline topics exist.
oc -n <deploy-namespace> exec deploy/kafka -- \
  /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list | grep '^stube.catalog.item.'

# 4. Seed landed the CC titles.
oc -n <deploy-namespace> logs job/seed-demo-content

# 5. Issuer resolves (confirms split-horizon DNS).
curl -s https://<hostname>/auth/realms/zaentrum/.well-known/openid-configuration
```

Then in a browser: open the demo hostname, log in with the bundled Keycloak admin
(a **fresh realm import forces an `UPDATE_PASSWORD` on first login**), browse the
catalog, and play a title.

---

## Update flows

| Change | Path |
|---|---|
| **An app change** | Push the app's GitHub repo → GitHub Actions builds `ghcr.io/zaentrum/<app>:latest` (+ `:sha-<gitsha>`) → run the CI deploy; step 8 `rollout restart`s the app tiers to pull `:latest`. |
| **A chart / operator change** | Push `zaentrum-operator` → the build-images workflow builds `ghcr.io/zaentrum/operator:latest` (+ `:sha-<gitsha>`) → bump the image in `deploy/operator-install.yaml` to that sha → cluster-admin `oc apply -f operator-install.yaml` to roll the operator (its embedded chart re-renders). |
| **A CR value change** | Edit the `Zaentrum` CR → run the CI deploy. |

See [updating.md](./updating.md) for the full update model and channels, and
[troubleshooting.md](./troubleshooting.md) for known traps (OC_TOKEN expiry, the
Kafka `emptyDir`→PVC volume-type conflict, NVENC/driver mismatch, in-cluster OIDC
split-horizon, and the fresh-realm password change).
