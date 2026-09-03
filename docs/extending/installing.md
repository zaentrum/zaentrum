# Installing addons — the honest current path

There is no one-command addon install yet. What exists is a **safe place to
stand**: the operator never touches workloads it did not render, so an addon
deployed next to the platform survives every reconcile, is never pruned, and
does not cascade-delete with the CR. Installation itself is plain Kubernetes.

> 🧭 The end state is declarative — an `addons` entry on the `Zaentrum` CR that
> the operator reconciles like everything else, plus platform-provisioned
> [addon identity](./identity.md). Neither is built. This page describes today,
> so nothing here should surprise you at apply time.

## What an addon installation consists of

Using [acquire](https://github.com/laedeli/acquire) as the reference — its
[deploying guide](https://github.com/laedeli/acquire/blob/main/docs/deploying.md)
is the addon-side view of this list:

| Piece | Who provides it | Notes |
|---|---|---|
| Deployment + Service per addon component | the addon's manifests | Plain k8s YAML applied into the platform namespace |
| The addons label | you, via kustomize | See below — it drives the operator console grouping |
| Secrets (DB URL, OIDC client, third-party keys) | you | Addon manifests reference them by name; create them before applying |
| A database/schema, if the addon has state | you | Addons own their schema; the platform DB server may host it |
| OIDC client + addon role | you, by hand today | See [identity — honest status](./identity.md#honest-status-on-a-stock-install) |
| App + tile in the portal | an admin, in settings | Gives the addon its console at `/portal/app/{key}` |
| Slot rows | the addon itself | Self-registered on startup/install once identity exists |
| Media volume mount | you | Required if the addon produces files for [ingest](./ingest.md) |

No Ingress or Route: the [portal proxy](./console.md) is the addon's front
door.

## The label that makes it visible

Stamp every addon object with

```yaml
labels:
  app.kubernetes.io/part-of: <namespace>-addons
```

— from your kustomization, not by hand per file:

```yaml
# kustomization.yaml
namespace: <platform-namespace>
labels:
  - pairs:
      app.kubernetes.io/part-of: <platform-namespace>-addons
    # default includeSelectors: false — selectors are immutable; adding to
    # them would make an already-installed addon fail to apply
resources:
  - my-addon.yaml
```

The portal's operator console groups workloads by this label: platform
services (operator-rendered) in one section, **addons** in their own, and
anything unlabelled under *unclaimed*. An addon that skips the label looks
like something nobody owns.

## Uninstall

Subtraction, in order: delete the addon's k8s objects, delete its registry
rows (`DELETE /api/portal/extensions/{key}` per row, or an admin removes the
app + tile in settings), and drop its database if you are done with the data.
The `addon` column on slot rows exists so this becomes one bulk operation once
self-registration covers apps and tiles too; today it is these steps.
