# Troubleshooting

A symptom → cause → fix runbook for the traps that actually bite when deploying
and operating zaentrum. Each section is a single trap: the **symptom** (the log
line or error you see), the **cause**, and the **fix** (the commands).

The platform is operator-managed — one [operator](./operator.md) renders the whole
stack from a single `Zaentrum` custom resource. Most fixes below are day-2
operations against a running install; the reference demo details are in
[self-hosting.md](./self-hosting.md).

| # | Symptom | Cause |
|---|---------|-------|
| 1 | Deploy job fails pre-flight `ns zaentrum-demo missing` | Expired `OC_TOKEN`, or deployer SA missing the cluster get-namespaces / get-crd grants |
| 2 | Operator reconcile error `may not specify more than 1 volume type` | Kafka `Deployment` being switched `emptyDir`→PVC in place |
| 3 | Every transcode aborts `Driver does not support the required nvenc API version` | ffmpeg NVENC build newer than the GPU node's Nvidia driver |
| 4 | Pods stuck `ContainerCreating`, only a `Scheduled` event | Same NFS export mounted twice in one pod → kubelet hang |
| 5 | In-cluster login / OIDC issuer errors | Split-horizon DNS: public issuer host not resolvable from inside the cluster |
| 6 | A fresh scan's first item never advances / topics gone after a Kafka restart | Bundled Kafka on `emptyDir` lost its topics |
| 7 | Admin login demands a password change | Fresh Keycloak realm import forces `UPDATE_PASSWORD` |

---

## 1. Deploy job fails pre-flight: `ns zaentrum-demo missing`

**Symptom** — the `deploy:zaentrum-demo` CI job fails at its pre-flight guard:

```
ns zaentrum-demo missing — run 'oc apply -f zaentrum-demo/bootstrap.yaml' as cluster-admin first
```

(or the sibling guard `Zaentrum CRD missing — install the operator first`).

**Cause** — the guard is a plain `kubectl get ns zaentrum-demo` / `kubectl get crd
zaentrums.zaentrum.io` run with the group-level `OC_TOKEN`. If the namespace and
CRD *do* exist, the guard only fails for one of two reasons:

1. **`OC_TOKEN` has expired.** It is a deployer `ServiceAccount` token; if it was
   minted short-lived it will silently lapse and every `kubectl` call under it
   returns unauthorized, which the guard surfaces as "missing."
2. **The deployer SA lacks the cluster-scoped reads.** Both guards are
   *cluster-scoped gets* that the namespace-admin `RoleBinding` does not grant.
   They are covered by the `resourceNames`-scoped `ClusterRole`
   **`zaentrum-demo-ns-get`** in `zaentrum-demo/bootstrap.yaml`, which grants
   exactly `get namespaces/zaentrum-demo` and
   `get customresourcedefinitions/zaentrums.zaentrum.io`. If bootstrap was never
   applied (or was applied without that block), the guard fails even with a valid
   token.

**Fix** — mint a long-lived deployer token and update the group CI variable:

```bash
# Long-lived deployer token. The deployer SA lives in your deploy namespace.
oc create token <deploy-sa> -n <deploy-namespace> --duration=<long>

# Push it to the group-level CI variable so every deploy uses it.
glab api --method PUT \
  "groups/zaentrum/variables/OC_TOKEN" \
  -f "value=$(oc create token <deploy-sa> -n <deploy-namespace> --duration=<long>)"
```

If the grant is missing rather than the token, (re-)apply the bootstrap as
cluster-admin — this is a one-time cluster-scoped bootstrap, **not** something CI
can do:

```bash
oc apply -f zaentrum-demo/bootstrap.yaml
```

> **Caveat — false positive when testing an SA token locally.** `oc --token=""`
> (empty or unset) does **not** fail; `oc` silently falls back to your **admin
> kubeconfig**, so the guard passes and the token looks fine. Always test the
> actual token value explicitly, e.g.:
>
> ```bash
> oc get ns zaentrum-demo --token="$OC_TOKEN" --server="$OC_SERVER" \
>   --insecure-skip-tls-verify=true
> ```

---

## 2. Kafka won't switch to a PVC: `may not specify more than 1 volume type`

**Symptom** — after setting `storage.kafkaPvc` (see [trap 6](#6-a-fresh-scans-first-item-never-advances--topics-gone-after-a-kafka-restart)),
the operator's server-side apply on the Kafka `Deployment` fails:

```
Deployment.apps "kafka" is invalid: spec.template.spec.volumes[…]:
Forbidden: may not specify more than 1 volume type
```

**Cause** — the existing Kafka `Deployment` already carries an `emptyDir` volume
for the log dir. Server-side apply cannot cleanly transform that same volume into
a `persistentVolumeClaim` in place — the merge leaves both volume types on one
volume entry, which the API server rejects.

**Fix** — delete the Kafka `Deployment` once so the operator recreates it clean
from the chart with the PVC-backed volume:

```bash
oc delete deploy kafka -n zaentrum-demo
```

The operator re-renders it on the next reconcile. This is safe for the config
switch itself; be aware it restarts the broker (see [trap 6](#6-a-fresh-scans-first-item-never-advances--topics-gone-after-a-kafka-restart)
for what survives).

---

## 3. Every transcode fails: `Driver does not support the required nvenc API version`

**Symptom** — every transcode job aborts. In the transcoder logs:

```
Driver does not support the required nvenc API version. Required: 13.1 Found: 13.0
```

or, on a mismatched older ffmpeg:

```
Unrecognized option 'spatial_aq'
```

**Cause** — the transcoder's bundled ffmpeg NVENC build does not match the GPU
node's Nvidia driver. The image ships a **prebuilt NVENC-enabled ffmpeg static
build**, pinned in `transcoder/Dockerfile` via `FFMPEG_BUILD_URL`. Tracking
`master-latest` drifts to bleeding-edge NVENC SDKs: a mid-2026 master build began
requiring nvenc API 13.1 (driver ≥ 610) and aborted every encode on nodes running
driver 580 / nvenc 13.0 (RTX 3090). A build that is *too new* for the driver
fails with the "required nvenc API version" error; a mismatched build can also
reject encoder flags (`spatial_aq`).

**Fix** — pin `FFMPEG_BUILD_URL` to a **release branch**, never `master-latest`.
The default in `transcoder/Dockerfile` is the ffmpeg 7.1 release branch:

```dockerfile
ARG FFMPEG_BUILD_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-latest-linux64-gpl-7.1.tar.xz
```

The `n7.1` branch links an NVENC SDK compatible with driver ≥ ~550 and takes only
bugfix backports, so it never bumps the driver floor out from under the cluster.
Override for a mirror or a different pin with a build arg:

```bash
docker build --build-arg FFMPEG_BUILD_URL=<release-branch-tarball-url> .
```

Bump to a newer branch **only** after verifying the GPU nodes' driver is new
enough (`nvidia-smi` on the GPU node) and re-validating an encode.

---

## 4. Pods stuck `ContainerCreating` with only a `Scheduled` event

**Symptom** — one or more pods sit in `ContainerCreating` indefinitely. `oc
describe pod` shows *only* a `Scheduled` event and nothing after it — no
`Pulling`, no `FailedMount`, no progress. The node's kubelet is effectively hung.

**Cause** — the **same NFS export is mounted twice inside one pod**. Mounting one
NFS export at two paths in a single pod hangs the kubelet's mount operation, which
stalls the pod at `ContainerCreating` with no further events.

**Fix** — mount the export **once** at a single parent path and reference
sub-paths beneath it, rather than mounting the same export at multiple mount
points. In this platform the media library is a single parent-mount at
`/var/lib/katalog`; consumers use sub-paths of that one mount instead of adding a
second volume for the same export. Fix the offending workload's volume/mount spec
(or the CR/chart values that generate it) so the export appears exactly once, then
delete the stuck pod so it reschedules:

```bash
oc delete pod <stuck-pod> -n zaentrum-demo
```

---

## 5. In-cluster login / OIDC issuer errors

**Symptom** — login fails, or services log OIDC issuer-validation errors when
talking to the identity provider from inside the cluster (issuer URL unreachable,
or the discovered issuer does not match).

**Cause** — **split-horizon DNS.** The public HTTPS issuer host (e.g. the
`hostname` on the CR) resolves to a public/edge address that in-cluster pods
cannot route to, or that does not point back at the cluster's router. Token
issuer validation requires that the *same public host* resolve to the OKD router
**from inside the cluster**.

**Fix** — set **`network.issuerHostAliasIP`** on the `Zaentrum` CR. The operator
injects a matching `hostAliases` entry into the workloads so the public issuer
host resolves to the router IP from inside the cluster, satisfying issuer
validation without changing the public URL. Example CR fragment:

```yaml
spec:
  network:
    issuerHostAliasIP: <router-ip>
```

Apply the CR change (via CI for the demo) and let the operator reconcile; the
affected pods pick up the `hostAliases` on their next roll.

---

## 6. A fresh scan's first item never advances / topics gone after a Kafka restart

**Symptom** — after a Kafka pod restart (including the deliberate delete in
[trap 2](#2-kafka-wont-switch-to-a-pvc-may-not-specify-more-than-1-volume-type)),
a fresh scan's first item never advances through the pipeline, or expected topics
are missing.

**Cause** — the media pipeline is **pure event-driven**: stage handoffs are Kafka
events keyed by `item_id`
(`scan → stube.catalog.item.discovered → enrich → …enriched → analyze →
…analyzed → transcode → …transcoded → package`). The bundled single-node KRaft
broker defaults to an **`emptyDir`** log dir, so a pod restart/reschedule wipes
its topics and consumer offsets — in-flight handoffs for the affected keys are
lost.

**Fix** — back the broker's log dir with a PVC so topics survive a restart. Set
**`storage.kafkaPvc`** (and pin the pod to a node with **`storage.kafkaNode`**,
since the PVC is node-local) on the `Zaentrum` CR:

```yaml
spec:
  storage:
    kafkaPvc: <pvc-name>       # e.g. kafka-data — empty => ephemeral emptyDir
    kafkaNode: <node-hostname> # pin the broker to the node holding the PV
```

For the demo, the node-local PV and its pre-created host dir are established by
`zaentrum-demo/bootstrap.yaml` (a `pv-...-kafka` PersistentVolume, a host dir on
the node, and the `<node>` the broker is pinned to).

> **Self-heals otherwise.** Even on `emptyDir`, the platform recovers on its own:
> topics **auto-create** on first produce, and `katalog-manager` **retries**
> transient produce errors. So a lost topic reappears and the pipeline resumes —
> `kafkaPvc` just makes it durable instead of relying on recovery.

---

## 7. Admin login demands a password change

**Symptom** — logging into the bundled Keycloak admin (realm `zaentrum`) on a
fresh deploy immediately forces a password change (`UPDATE_PASSWORD` required
action) instead of signing you in.

**Cause** — this is a **fresh realm import**, not an error. On first import the
realm seeds the admin with a temporary password and the `UPDATE_PASSWORD`
required action. Existing realms are **not** re-imported, so this only happens on
a genuinely fresh identity store.

**Fix** — complete the forced password change with the seeded credentials, then
sign in normally. The initial admin password comes from the demo's
`zaentrum-keycloak-admin` secret (`DEMO_KC_ADMIN_PW` / `DEMO_REALM_ADMIN_PW` CI
variables). Nothing needs to be "repaired" — it is expected first-login behavior.
