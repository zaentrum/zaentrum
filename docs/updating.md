# Updating — day-2 operations

How to ship a change to a running Zaentrum platform. Which steps you run depends on
**what** changed. There are three flows:

| # | What changed | Rebuilds | Needs an operator roll? | How it lands |
|---|---|---|---|---|
| **A** | App code / image (a service under `github.com/zaentrum/<app>`) | `ghcr.io/zaentrum/<app>` | No | Push the app repo → GitHub Actions builds `:latest` → the demo CI deploy `rollout restart`s the app tiers to pull `:latest` |
| **B** | Chart / operator (templates, CR schema, chart values) | `ghcr.io/zaentrum/operator` | **Yes** | Push `zaentrum-operator` → its `build-images` workflow builds the operator image → bump the ref in `deploy/operator-install.yaml` → cluster-admin `oc apply` to roll the operator → CI deploy |
| **C** | A CR value (features / replicas / storage / hostname / …) | nothing | No | Edit the CR (`okd/zaentrum.yaml`) → CI deploy |

The platform is operator-managed: the operator renders all ~16 services from ONE
canonical Helm chart (`operator/platform/chart`) that is `go:embed`-ed into the
operator image, driven by a single `Zaentrum` CR. So a **chart change is an operator
change** — the new templates only take effect once the operator image is rebuilt and
the operator is rolled (flow B). A CR-only change needs no new image at all (flow C).

## Image tag scheme

Every image publishes two tags. The app polyrepos and this monorepo's
`build-images` workflow both use the same scheme (see
[`.github/workflows/build-images.yml`](https://github.com/zaentrum/zaentrum-operator/blob/main/.github/workflows/build-images.yml),
`docker/metadata-action`):

```yaml
tags: |
  type=raw,value=latest,enable={{is_default_branch}}
  type=sha,format=long
```

| Tag | When | Example |
|---|---|---|
| `:latest` | Pushes to the **default branch** (`main`) only. PRs build to validate but never push. | `ghcr.io/zaentrum/chino-web:latest` |
| `:sha-<gitsha>` | Every pushed build (`type=sha,format=long` → the **full** commit SHA). | `ghcr.io/zaentrum/operator:sha-cb96f3dc3d592a42e0399c58d24f8cf0379b76d9` |

The reference demo tracks `:latest` (CR `spec.version: latest`), so an app deploy just
re-pulls `:latest`. The operator is pinned to an **immutable `:sha-<gitsha>`** in
`deploy/operator-install.yaml` so a roll is deterministic and reversible.

---

## Flow A — app code / image change

A change to a service that has its own polyrepo (`chino-web`, `chino-api`,
`chino-stream`, `katalog-api`, `katalog-manager`, …). No operator or chart change.

1. **Push the app's GitHub repo.** Merge to `main` on `github.com/zaentrum/<app>`.
2. **GitHub Actions builds the image.** That repo's own workflow builds and pushes
   `ghcr.io/zaentrum/<app>:latest` (+ `:sha-<gitsha>`). This monorepo does **not**
   rebuild the polyrepo images — its `build-images` workflow only builds `admin`,
   `keycloak`, and `operator` (see the header comment in `build-images.yml`).
3. **Run the demo CI deploy** (see [Running a CI deploy](#running-a-ci-deploy)).
   The job’s tail re-pulls `:latest` by rolling the app tiers:

   ```bash
   # from deploy/.gitlab-ci.yml (deploy:zaentrum-demo)
   app=$(kubectl -n "$NS" get deploy -o name | grep -vE '/(postgres|valkey|kafka)$')
   echo "$app" | xargs -r -n1 kubectl -n "$NS" rollout restart
   ```

   The stateful backers (`postgres`, `valkey`, `kafka`) are **excluded** —
   restarting `postgres` wipes the demo DB; `kafka`/`valkey` hold topic/session
   state.

No operator roll is involved: the chart still references the same flat
`ghcr.io/zaentrum/<svc>` image, only the bytes behind `:latest` changed.

---

## Flow B — chart / operator change

A change to the embedded Helm chart (templates or `values.yaml`), the CR schema
(`api/v1alpha1/zaentrum_types.go`), or the controller logic. The chart ships **inside**
the operator image (`go:embed`, see [`operator/Dockerfile`](https://github.com/zaentrum/zaentrum-operator/blob/main/operator/Dockerfile)),
so it only takes effect after the operator is rebuilt and rolled.

1. **Push `zaentrum-operator`.** Merge to `main`.
2. **`build-images` builds the operator image.** On `main` it builds
   `ghcr.io/zaentrum/operator:latest` **and** `:sha-<full gitsha>`
   (`operator` context; see `build-images.yml`). Note the full SHA.
3. **Bump the image ref** in
   [`deploy/operator-install.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/deploy/operator-install.yaml) to that SHA:

   ```yaml
   # spec.template.spec.containers[].image (controller-manager Deployment)
   image: ghcr.io/zaentrum/operator:sha-<full-gitsha>
   ```

4. **Roll the operator (cluster-admin).** Applying the install manifest updates the
   controller-manager in `zaentrum-operator-system`, so it restarts with the new
   embedded chart:

   ```bash
   oc apply -f deploy/operator-install.yaml
   ```

   > `operator-install.yaml` also carries the CRD, ClusterRoles/Bindings, and the
   > controller-manager Deployment — re-applying it is the whole operator install.

5. **Run a CI deploy** (flow’s tail below / [Running a CI deploy](#running-a-ci-deploy))
   so the operator re-renders the platform from the new chart and rolls the affected
   tiers. The operator reconciles via server-side apply; give it up to ~2 min to
   converge (`kubectl -n <deploy-namespace> get zaentrum,pods`).

### Adding a new CR spec field ⚠️

The CRD (the OpenAPI schema the API server validates against) is stored in **three
copies**. If you add a field to `api/v1alpha1/zaentrum_types.go`, it must be present
in the schema of **all three** or the API server **prunes** the value on apply (the
CR looks accepted but the field silently vanishes):

| Copy | Consumed by |
|---|---|
| `operator/config/crd/zaentrum.io_zaentrums.yaml` | the operator’s own CRD source |
| `operator/bundle/manifests/zaentrum.io_zaentrums.yaml` | the OLM bundle (OperatorHub install) |
| `deploy/operator-install.yaml` | the direct `oc apply` install (embeds the CRD inline) |

Regenerate/mirror the field into all three, then follow the flow B steps above so the
API server sees the new schema before any CR references the field.

---

## Flow C — CR value change

A change to *configuration* only — enable a feature, change replicas, resize storage,
point at external identity, etc. No image is rebuilt and the operator is **not** rolled;
the same operator reconciles the edited CR.

1. **Edit the CR.** For the reference demo that is
   [`deploy/zaentrum-demo/okd/zaentrum.yaml`](https://github.com/zaentrum/zaentrum-operator)
   in your deploy repo (a private, deploy-only repo). Spec fields map 1:1 onto the chart values
   (see the field table in [operator.md](./operator.md) and the `values.yaml`
   comments). For example, to make the bundled Kafka log persist across restarts:

   ```yaml
   spec:
     storage:
       kafkaPvc: kafka-data              # empty => ephemeral emptyDir (topics lost on restart)
       kafkaNode: <node>
   ```

2. **Run a CI deploy** ([Running a CI deploy](#running-a-ci-deploy)). CI applies the
   overlay; the operator picks up the changed CR and reconciles.

> Switching `kafka`’s volume from `emptyDir` to a PVC fails the operator’s server-side
> apply (`may not specify more than 1 volume type`) — see
> [troubleshooting.md](./troubleshooting.md) for the one-time
> `oc delete deploy kafka` fix.

---

## Running a CI deploy

Flows A, B, and C all finish with the same GitLab CI job. It is defined in
[`deploy/.gitlab-ci.yml`](https://github.com/zaentrum/zaentrum-operator) in
your deploy repo (a private, deploy-only repo) as `deploy:zaentrum-demo`:

- **`main`-only** and **manual**, gated on `CI_ENABLED=true`
  (`workflow.rules`). Pipelines stay dormant otherwise.
- It creates the demo secrets from the `DEMO_*` CI variables, copies the registry
  pull secrets, `kubectl apply -k zaentrum-demo`, waits for the operator to render
  the platform, then rolls the app tiers.

Trigger it from the repo, then play the manual job:

```bash
glab ci run -b main -R <deploy-repo>
# then play the manual `deploy:zaentrum-demo` job in the pipeline UI (or `glab ci`)
```

The demo keeps a few things the operator does **not** render (they’re applied by CI /
bootstrap, not the chart): the media PVC (`storage.provisionMedia: false`), the
`zaentrum-*` secrets (`secrets.external: true`), and the seed/scan/enqueue/kafka-topics
Jobs (demo choreography). See [reference-demo.md](./reference-demo.md) for the full
bootstrap and CI-variable list.

---

## When do I roll the operator vs. just rollout?

- **Rollout only** (flow A / C): the running operator and its embedded chart are
  unchanged. New app bytes (A) or new CR values (C) are picked up by a normal
  `rollout restart` / reconcile. This is what a routine deploy does.
- **Roll the operator** (flow B): the *chart* or *controller* changed, and the chart
  lives inside the operator image. You must rebuild the operator image, pin it in
  `operator-install.yaml`, and `oc apply` it (cluster-admin) so the new templates are
  loaded — then deploy so the operator re-renders.

If a deploy fails a pre-flight guard (`ns … missing`, CRD missing), an OIDC / issuer
mismatch, a stalled pipeline stage, or a Kafka volume/type error, see
[troubleshooting.md](./troubleshooting.md).
