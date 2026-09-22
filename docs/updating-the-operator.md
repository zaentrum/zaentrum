# Updating the operator

The platform updates its own images. The **operator's controller does not** —
it is installed and upgraded outside the product, through whichever of three
channels installed it. This page is what each of those looks like, how to see
what you are running, and why the product shows you the version instead of
offering a button.

For the platform's own updates — a new app image, a chart change, a CR value —
see [updating.md](./updating.md). This page is only about the controller that
reconciles your `Zaentrum` CR.

## What "the controller" means here

Installing the operator creates, in its own namespace `zaentrum-operator-system`:
the `Zaentrum` and `ZaentrumAddon` CRDs, the cluster RBAC, and one Deployment —
`zaentrum-operator-controller-manager`, running `ghcr.io/zaentrum/operator:<tag>`.
That Deployment is *the controller*. It watches your CR and renders the whole
platform from the Helm chart embedded in its own image
(see [operator.md](./operator.md#install)).

Two consequences follow, and they are the whole subject of this page:

- **The chart ships inside the controller image.** A chart change is a
  controller change — the new templates take effect only once the controller
  runs a new image ([updating.md flow B](./updating.md#flow-b--chart--operator-change)).
- **The controller is not one of the workloads it manages.** It runs in another
  namespace, under cluster-scoped permissions, and nothing inside the platform
  namespace can write to it.

## See what you run

The operator reports itself on the CR, under `status.controller`:

| Field | Is |
|---|---|
| `image` | what the controller pod runs, tag or digest |
| `version` | the tag, else the short digest, else `unknown` |
| `source` | how it was installed: `olm`, `manifest`, `appliance` or `unknown` |
| `availableUpdate` | a newer version found on the channel; `""` when there is none, or nothing looks |
| `observedAt` | when the operator last looked |

Three ways to read it, in rising order of how much access they need.

**1. The CLI**, through the portal — no cluster access at all:

```sh
zae platform controller --url https://media.example.org
```

```
https://media.example.org — the operator's controller
  version      v0.4.1
  image        ghcr.io/zaentrum/operator:v0.4.1
  installed    OLM — a subscription the cluster manages
  update       v0.5.0 available
  observed     2026-09-22T08:00:00Z
Updated outside the platform: approve the update in its OLM subscription.
```

`zae platform status` ends with the same section, and `--json` on either prints
what the portal reported, for a script. An instance whose operator predates the
field says so and `zae platform controller` exits `3` — *not offered by this
instance* — so a check can branch on it. See
[the CLI contract](./extending/cli.md#the-operators-own-controller).

**2. The portal.** The operator console (`/portal/operator`, admin-only) shows
an **operator controller** card with the same facts and the same one line
naming the path. There is no button on it, for the reasons
[below](#why-the-product-will-not-do-it-for-you).

**3. The cluster**, if you have access to it:

```sh
kubectl -n zaentrum get zaentrum -o jsonpath='{.items[0].status.controller}' | jq
kubectl -n zaentrum-operator-system get deploy zaentrum-operator-controller-manager \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

## The three channels

### 1. OLM — a subscription the cluster manages

On OpenShift or any OLM cluster the operator is installed from its bundle
(package `zaentrum-operator`, channel `stable` — see
[the bundle](https://github.com/zaentrum/zaentrum-operator/tree/main/operator/bundle)).
OLM then owns the lifecycle: it watches the catalog and creates an
`InstallPlan` for each new version in the channel.

The bundle supports `OwnNamespace`, `SingleNamespace` and `AllNamespaces`, so
the `Subscription`'s name and namespace are whatever the install chose — find
it first:

```sh
oc get subscription -A | grep zaentrum-operator
oc -n <ns> get subscription <name> -o jsonpath='{.spec.installPlanApproval}{"\n"}'  # Automatic | Manual
oc -n <ns> get installplan
oc -n <ns> patch installplan <plan> --type merge -p '{"spec":{"approved":true}}'    # approve a Manual plan
oc -n <ns> get csv                                       # Succeeded once it has rolled
```

- `installPlanApproval: Automatic` — the cluster rolls new versions on its own;
  there is nothing to do, and `availableUpdate` is a heads-up, not a task.
- `installPlanApproval: Manual` — **approve the install plan.** This is the
  path the product names for `source: olm`.

Changing the channel (`spec.channel` on the `Subscription`) is the same act one
level up, and also belongs to whoever owns the cluster's operators.

### 2. The pinned install manifest

Without OLM the operator is installed by applying one manifest —
[`deploy/operator-install.yaml`](https://github.com/zaentrum/zaentrum-operator/blob/main/deploy/operator-install.yaml),
which carries the namespace, both CRDs, the cluster RBAC and the controller
Deployment, with the controller image pinned to an immutable `:sha-<gitsha>`.

Updating means bumping that pin and applying it again — **as cluster-admin, and
normally through the deployment repository that holds the manifest**, so the
record of what is installed stays the record:

```sh
# in the repository that holds your copy of the manifest
sed -i 's|ghcr.io/zaentrum/operator:.*|ghcr.io/zaentrum/operator:sha-<newsha>|' \
  deploy/operator-install.yaml
git commit -am "operator: roll the controller to sha-<newsha>" && git push
# …your pipeline applies it, or, by hand:
oc apply -f deploy/operator-install.yaml
oc -n zaentrum-operator-system rollout status deploy/zaentrum-operator-controller-manager
```

Pinning a digest or an immutable SHA tag rather than a floating one is what
makes the roll deterministic and reversible: rolling back is applying the
previous manifest. The reference demo does exactly this — see
[reference-demo.md](./reference-demo.md) and
[updating.md flow B](./updating.md#flow-b--chart--operator-change).

### 3. The appliance

The [appliance](./self-hosting.md#a-one-command-appliance) bakes the operator
install into its image and k3s applies it on boot, so the controller version is
a property of the appliance image. Its update *is* the controller's update:

```sh
docker pull ghcr.io/zaentrum/appliance:latest
docker rm -f zaentrum
docker run -d --privileged --name zaentrum -p 8080:80 \
  -v zaentrum-data:/var/lib/rancher/k3s/storage \
  ghcr.io/zaentrum/appliance:latest
```

Keep the storage volume across the replacement (as above) and the platform's
data survives; the new container brings a new controller with it. There is
nothing separate to update inside it.

## What a controller update carries with it

Not only a new binary:

- **the embedded platform chart** — the templates every platform workload is
  rendered from. Expect a reconcile after the roll, and expect workloads whose
  rendered spec changed to restart;
- **the CRD schema** — a new field is only usable once the CRD that validates it
  is installed. Applying a CR that uses a field the running CRD does not know is
  rejected by the apiserver, not ignored
  ([adding a new CR spec field](./updating.md#adding-a-new-cr-spec-field));
- **the cluster RBAC** — what the controller, and the permissions it hands to
  the platform's own components, are allowed to do.

What it does **not** carry: your CR, your data, and the platform version you are
pinned to. `spec.version` stays where you put it; a new controller re-renders
the same platform unless the chart changed.

## Why the product will not do it for you

Four reasons, in the order they bite:

1. **Permissions.** `portal-api` is scoped to the platform's namespace. The
   controller lives in another one, and its install also carries cluster-scoped
   objects — CRDs, ClusterRoles, ClusterRoleBindings. Granting the portal enough
   to replace them would make every admin of the platform an effective
   cluster-admin, which is a much larger change than an update button.
2. **Self-surgery.** The thing that would perform the update is the thing being
   replaced. A controller that rolls its own Deployment is terminated
   mid-reconcile by the rollout it started; if the new image is wrong, the
   component that could roll it back is the one that is now failing.
3. **The record.** On OLM the cluster owns the operator's lifecycle, and on a
   pinned manifest the manifest in your repository *is* the record of what is
   installed. A button in the product would change the cluster without changing
   either, and the next pipeline run would quietly undo it.
4. **It is the ordinary shape.** A cluster operator updates the workloads it
   manages; it is itself updated through whatever installed it. Keeping that
   boundary is what makes the platform's own updates safe to hand to a
   non-cluster-admin at all.

So the product does the half it can do honestly: it shows the version in charge,
says whether something newer exists, and names the path. The portal's operator
console and
[`zae platform controller`](./extending/cli.md#the-operators-own-controller)
both stop exactly there.

## After the roll

```sh
oc -n zaentrum-operator-system rollout status deploy/zaentrum-operator-controller-manager
oc -n zaentrum-operator-system logs deploy/zaentrum-operator-controller-manager --tail=50
kubectl -n zaentrum get zaentrum                     # PHASE back to Ready
zae platform controller --url https://media.example.org   # the version you expect
zae platform status --url https://media.example.org       # every workload ready again
```

A platform that does not return to `Ready`, or workloads that do not come back,
are in [troubleshooting.md](./troubleshooting.md). A controller that reports no
version at all is simply older than this field — update it by the channel that
installed it, and it will start reporting.

See also: [operator.md](./operator.md) ·
[updating.md](./updating.md) · [self-hosting.md](./self-hosting.md) ·
[the CLI contract](./extending/cli.md) ·
[troubleshooting.md](./troubleshooting.md)
