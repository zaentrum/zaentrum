# Prerequisites

What you need to have in place **before** you deploy zaentrum. Requirements vary by topology, so
this page is split by audience. Read the row that matches how you intend to run the platform, then
follow the linked deployment guide.

The three topologies:

| Topology | What it is | Guide |
|---|---|---|
| **Appliance** | One container — `docker run --privileged -p 80:80 ghcr.io/zaentrum/appliance:latest` boots an in-process single-node k3s that installs the operator, which brings up the platform from a baked-in `Zaentrum` resource. linux/amd64. Zero-clone. | [self-hosting.md](./self-hosting.md#a-one-command-appliance) |
| **Self-host on k8s** | Install the operator once, then apply a `Zaentrum` CR; or `helm install` the chart (`operator/platform/chart`) directly. The `deploy/k3s` (`up.sh`) and `deploy/compose` profiles in the operator repo are **not supported today**. | [self-hosting.md](./self-hosting.md), [operator.md](./operator.md) |
| **Reference demo** | The public demo at `https://zaentrum.demo.nalet.cloud` on an OKD cluster, deployed by CI from a deploy-only repo. | [reference-demo.md](./reference-demo.md) |

## At a glance

| Requirement | Appliance | Self-host on k8s | Reference demo |
|---|:---:|:---:|:---:|
| Container runtime (Docker/Podman) | required | — | — |
| A Kubernetes / OKD cluster | bundled (k3s) | required | required (OKD) |
| Media library storage (NFS or a StorageClass) | the container's volume (lost on replacement) | required | NFS (`<nfs-server>:/media-demo`) |
| A claim for the bundled Postgres (a StorageClass, or a pre-bound PV) | the container's volume (lost on replacement) | required, unless `databases.mode: external` | — (its Postgres still runs on an `emptyDir`) |
| Node-local storage for the bundled Kafka PV (topic persistence) | — | optional | required |
| GPU node + matching Nvidia driver (`features.gpu`) | not supported | optional (if pipeline) | required (pipeline) |
| Public DNS + TLS for the hostname (sign-in needs https on any name but `localhost`) | none — `zaentrum.localhost`, this machine only | required | OKD edge TLS |
| Split-horizon issuer resolution (in-cluster) | auto (CoreDNS rewrite) | required with HTTPS | `network.issuerHostAliasIP` |
| Egress to `ghcr.io` | required | required | required |
| Egress to TMDB (metadata enrichment) | if enriching | if enriching | required |
| Egress to seed content hosts | — | — | required |

Everything runs as a container at `ghcr.io/zaentrum/<service>` (public GitHub Container Registry).
The platform is operator-managed: the `zaentrum-operator` renders all ~16 services from ONE canonical
Helm chart (`operator/platform/chart`, `go:embed`-ed into the operator image) driven by a single
`Zaentrum` custom resource (`zaentrums.zaentrum.io`, `apiVersion zaentrum.io/v1alpha1`). Chart values
map 1:1 onto the CR spec — the field names below are those shared keys.

---

## Appliance

The appliance needs **almost nothing**. It ships a full single-node k3s in-process and the operator,
which brings up the portal, the web app, the catalog, streaming, and bundled Keycloak, Postgres,
Valkey, and Kafka.

- **A container runtime** that can run a privileged container — Docker or Podman — on a
  **linux/amd64** host (no arm64 image is published yet), with **host port 80** free: the platform's
  ingress and sign-in are bound to `http://zaentrum.localhost` on port 80.

  ```bash
  docker run -d --privileged --restart unless-stopped -p 80:80 --name zaentrum \
    ghcr.io/zaentrum/appliance:latest
  open http://zaentrum.localhost
  ```

- **Network egress to `ghcr.io`** to pull the appliance image, and on first boot every platform image.
- **The machine it runs on.** `http://zaentrum.localhost` resolves to `127.0.0.1` in modern
  browsers with no `/etc/hosts` edit, and it is the one address the appliance answers and signs in
  at. Phones, TVs and other computers need https, which the appliance does not serve: over plain
  http only a `localhost` name can sign in (see
  [self-hosting.md](./self-hosting.md#a-one-command-appliance)).

Optional:

- **Egress to TMDB, and a TMDB key of your own,** if you want metadata enrichment — the published
  images carry no key (see [Network egress](#network-egress)).

Not used by the appliance:

- **Storage of your own.** The library and the bundled Postgres's databases live on claims in
  the container's own volume, for as long as the container does — see
  [persistence](./self-hosting.md#persistence).
- **A GPU.** The appliance transcodes in software; hardware transcoding (`features.gpu`) needs a
  cluster with a GPU node — see [GPU](#gpu-nvenc).

Split-horizon issuer resolution is handled for you: the all-in-one wires a CoreDNS rewrite (driven by
the `STUBE_ISSUER_HOST` env) so pods resolve the issuer host to the appliance's own ingress, as the
browser does. There is no TLS.

---

## Self-host on your own k8s

You bring the cluster and its supporting infrastructure; the operator renders the platform into it.

### A cluster

- A **Kubernetes or OKD cluster** you can create a namespace and a `Zaentrum` CR in, and a
  cluster-admin once, to install the operator from its pinned install manifest — no OLM needed (see
  [operator.md](./operator.md#install)). Where OLM runs (OpenShift), the operator's OLM bundle is the
  alternative. Without Kubernetes, run the [appliance](#appliance): the `deploy/k3s/up.sh` and
  `deploy/compose` profiles are not supported today (see
  [self-hosting.md](./self-hosting.md#d-k3s-and-compose-profiles)).

### Storage

- **Media library storage.** The chart provisions a `media` PVC of `storage.mediaSize` (default `50Gi`)
  from `storage.className` (default: the cluster's default StorageClass). Use an **RWX** class (NFS,
  CephFS, etc.) if more than one media-plane pod must read the library concurrently; RWO works for a
  single-node library. To back it with a pre-created PV instead (e.g. an existing NFS export), set
  `storage.provisionMedia: false` and bind your own PV to the `media` claim.

  > Trap: never mount the **same** NFS export twice in one pod — it hangs the kubelet. Use a single
  > parent-mount at `/var/lib/katalog`. See [troubleshooting.md](./troubleshooting.md).

- **A claim for the bundled Postgres.** A new install keeps its databases on a `postgres-data`
  claim: `ReadWriteOnce`, `storage.postgres.size` (default `10Gi`), from
  `storage.postgres.className`, else `storage.className`, else the cluster's default
  StorageClass. Where nothing provisions one, bind a PersistentVolume to a claim of your own and
  name it in `storage.postgres.claimName`. With `databases.mode: external` there is none (see
  [self-hosting.md](./self-hosting.md#b-self-host-with-the-operator)).

- **Node-local storage for the bundled Kafka PV (optional but recommended).** The bundled broker's log
  dir is an `emptyDir` by default, so **topics and consumer offsets are lost on a broker restart**. To
  make them survive, set `storage.kafkaPvc` to a pre-created PVC and `storage.kafkaNode` to the
  `kubernetes.io/hostname` the PVC is pinned to (a node-local PV must be pinned to its node):

  ```yaml
  storage:
    kafkaPvc: kafka-data
    kafkaNode: <node>
  ```

  If you point the platform at an **external** Kafka cluster instead (`features.kafka: false`, brokers
  via `KAFKA_BROKERS`), this doesn't apply.

### GPU (only if you run the pipeline with NVENC)

Required only when `features.pipeline: true` **and** `features.gpu: true`. See [GPU](#gpu-nvenc) below —
the ffmpeg-nvenc ↔ driver version coupling applies to you.

### DNS + TLS

- A **public hostname** (`hostname`) that both the browser and in-cluster validation use as the OIDC
  issuer host. Point DNS at your ingress/router and terminate TLS there.
- **TLS is not optional** for any hostname but a `localhost` name. Keycloak marks its login cookies
  `Secure` (`SameSite=None`), and a browser stores and sends those over https only, or to `localhost`
  — over plain http, sign-in fails with "Cookie not found". The Android phone and TV apps refuse plain
  http and trust public certificate authorities only, so give them a certificate from one. The
  chart's `Ingress` has no TLS section: terminate TLS at your ingress controller (its default
  certificate) or a proxy in front of it, and set `identity.issuerScheme: https`.
- Set `routing.provisionIngress: true` for a plain-k8s `Ingress` (single-origin paths), or
  `routing.provisionRoutes: true` on OpenShift.
- If you terminate TLS at the edge (`identity.issuerScheme: https`), you need **split-horizon issuer
  resolution** — see [Split-horizon issuer resolution](#split-horizon-issuer-resolution).

### Identity

- With `identity.mode: bundled` (default), the chart ships Keycloak (realm `zaentrum`); nothing to
  provide up front. With `identity.mode: external`, register a public OIDC client at your own provider
  and set `identity.issuer` / `identity.clientId` / `identity.audience` (see the operator contract in
  [self-hosting.md](./self-hosting.md#b-self-host-with-the-operator)).

### Network egress

- **`ghcr.io`** — mandatory, to pull every image. **Do not attach a pull secret for it**: the images
  are public, and GHCR answers a dead or expired credential with `403` instead of falling back to
  anonymous — an attached credential that later expires makes public images unpullable. Add
  `imagePullSecrets` only if you mirror behind a private registry. This applies to the operator's
  own ServiceAccount too; the deploy pipeline's preflight checks for exactly this.
- **TMDB** — only if you enrich metadata (see [Network egress](#network-egress)).

---

## Reference demo (OKD)

The public demo is deployed by CI from your deploy repo (a private, deploy-only repo)
into namespace `zaentrum-demo` on an OKD cluster. It runs the **full media pipeline** with GPU NVENC.
Most of the setup is one-time cluster-admin bootstrap; the rest is CI. Full walkthrough:
[reference-demo.md](./reference-demo.md).

### Cluster + one-time cluster-admin bootstrap

An OKD cluster, plus a cluster-admin who runs these **once** (CI cannot — it can only touch the namespace):

1. **Install the operator** (cluster-scoped CRD + ClusterRoles + controller-manager in
   `zaentrum-operator-system`):

   ```bash
   oc apply -f https://raw.githubusercontent.com/zaentrum/zaentrum-operator/main/deploy/operator-install.yaml
   ```

2. **Apply the demo bootstrap** — Namespace, the NFS PV for media, the node-local PV for Kafka, deployer
   RBAC, and the Kafka `anyuid` SCC:

   ```bash
   oc apply -f zaentrum-demo/bootstrap.yaml
   ```

3. **Pre-create the Kafka PV host dir** on the pinned node (the demo pins Kafka to a `<node>`):

   ```bash
   oc debug node/<node>
   # mkdir -p /host/var/local-storage/a/pv/zaentrum-demo-kafka && chmod 0777 ...
   ```

4. **Set CI variables** (see below).

The deploy ServiceAccount (`<deploy-namespace>:<deploy-sa>`) is namespace-scoped and needs two cluster-scoped **reads**
for the deploy job's pre-flight guards — `get namespaces/zaentrum-demo` and
`get customresourcedefinitions/zaentrums.zaentrum.io` — granted by the `resourceNames`-scoped
`zaentrum-demo-ns-get` ClusterRole in `bootstrap.yaml`.

### Storage

- **Media**: an **NFS server** exporting the demo library. The bootstrap PV binds `<nfs-server>:/media-demo`
  (RWX, `Retain`) to the `media` claim; the CR keeps `storage.provisionMedia: false` so the operator
  consumes it. The demo must serve only distributable content (Creative Commons / public domain).
- **Kafka**: a **node-local PV** for topic persistence — `storage.kafkaPvc: kafka-data`,
  `storage.kafkaNode: <node>`, backed by the node-local `zaentrum-demo-kafka` PV in
  `bootstrap.yaml`, with the host dir from step 3.

### GPU

The demo runs `features.pipeline: true` with NVENC, so it needs a **GPU node with a matching Nvidia
driver** — see [GPU](#gpu-nvenc).

### DNS + TLS + split-horizon

- Host `zaentrum.demo.nalet.cloud`, TLS terminated at the **OKD edge router**
  (`identity.issuerScheme: https`, `routing.provisionRoutes: true`).
- **Split-horizon**: `network.issuerHostAliasIP: "<router-ip>"` points the in-cluster OIDC validators
  at the router node so token validation reaches the edge-terminated TLS. See
  [Split-horizon issuer resolution](#split-horizon-issuer-resolution).

### CI variables

The demo keeps a few things external to the operator: the `media` PVC (`storage.provisionMedia: false`),
the CI-created secrets (`secrets.external: true`), and the seed/scan/enqueue/kafka-topics Jobs (demo
choreography — the operator forces `jobs.seed: false`).

| Scope | Variable | What it is |
|---|---|---|
| Group | `OC_SERVER`, `OC_TOKEN` | OKD API URL + a long-lived deployer SA token (`oc create token <deploy-sa> -n <deploy-namespace> --duration=<long>`). |
| Project | `DEMO_DB_PW`, `DEMO_MANAGER_SECRET`, `DEMO_KC_ADMIN_PW`, `DEMO_REALM_ADMIN_PW`, `DEMO_USER_PW` | Secrets CI creates as the `zaentrum-*` secrets. |
| Group | `GHCR_PULL_TOKEN`, `GHCR_PULL_USER` | **Optional — only for a private mirror.** Leave unset for public `ghcr.io/zaentrum/*`; when unset the deploy removes any stale `ghcr-pull` secret it finds. |

> Trap: an expired `OC_TOKEN` fails the deploy pre-flight with "namespace missing" — refresh with a new
> long-lived token. See [troubleshooting.md](./troubleshooting.md).

### Network egress

The demo needs egress to **`ghcr.io`** (images), **TMDB** (metadata enrichment), and the **seed content
hosts** — `download.blender.org`, `upload.wikimedia.org`, and `archive.org` (the seed Job pulls
Creative-Commons / public-domain movies from these).

---

## Cross-cutting requirements

### GPU (NVENC)

Needed only when the pipeline transcodes with hardware acceleration — `features.pipeline: true` **and**
`features.gpu: true` (the demo; optional for self-host; software ffmpeg otherwise). You need:

- A **GPU node** with an Nvidia GPU and the Nvidia device plugin installed so pods can request
  `nvidia.com/gpu`.
- A **host Nvidia driver whose version matches the transcoder's bundled ffmpeg**.

**The ffmpeg-nvenc ↔ driver coupling is load-bearing.** The transcoder image ships a **prebuilt
NVENC-enabled ffmpeg static build**, pinned to the **ffmpeg 7.1 release branch** — not `master-latest`.
`master` drifts to bleeding-edge NVENC SDKs: a mid-2026 `master` build began requiring nvenc API 13.1
(Nvidia driver ≥ 610) and aborted every encode with:

```
Driver does not support the required nvenc API version. Required: 13.1 Found: 13.0
```

on GPU nodes running driver 580 / nvenc 13.0. The `n7.1` branch links an NVENC SDK compatible with
driver ≥ ~550 and only takes bugfix backports, so it never bumps the driver floor out from under the
cluster. Verify your node's driver with `nvidia-smi` and only bump `FFMPEG_BUILD_URL` to a newer branch
after the node driver is confirmed new enough and the encode re-validated. Details and the fix live in
[troubleshooting.md](./troubleshooting.md).

### Split-horizon issuer resolution

Every service runs OIDC discovery + token validation against the issuer URL, which must **equal** both
the discovery document's `issuer` and the token's `iss` — so the same public hostname is used from the
browser and from inside the cluster. When TLS is terminated at the edge (`identity.issuerScheme: https`),
the in-cluster validators must be able to reach the **public HTTPS issuer**, which means the public host
has to resolve to the ingress/router **from inside the cluster**:

- **Self-host / demo**: set `network.issuerHostAliasIP` to the ingress/router IP. The operator adds
  `hostAliases` (that IP → `hostname`) to the OIDC validators so in-cluster validation reaches the public
  issuer.
- **Appliance**: handled automatically — a CoreDNS rewrite resolves the issuer host to the
  appliance's own ingress, which a browser on the machine reaches at `127.0.0.1`.

### Network egress

| Destination | Why | Who needs it |
|---|---|---|
| `ghcr.io` | Pull every `ghcr.io/zaentrum/*` image. | all topologies |
| TMDB (`api.themoviedb.org`) | Metadata enrichment — with your own key: the **TMDB api key** setting in Catalog Management, or `TMDB_API_KEY` from the optional `katalog-tmdb` secret. The published images carry none. | any topology that enriches |
| `download.blender.org`, `upload.wikimedia.org`, `archive.org` | The demo seed Job pulls Creative-Commons / public-domain movies. | reference demo |

---

## Next steps

- Appliance / self-host: [self-hosting.md](./self-hosting.md)
- Operator install + the `Zaentrum` CR: [operator.md](./operator.md)
- The public demo end-to-end: [reference-demo.md](./reference-demo.md)
- Applying updates: [updating.md](./updating.md)
- When something breaks: [troubleshooting.md](./troubleshooting.md)
