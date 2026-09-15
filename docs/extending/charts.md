# Addon charts — addons the platform installs

An addon can ship as a **standard Helm chart** that the platform installs
itself ([ADR-0011](../adr/0011-addon-charts-installed-by-the-operator.md)). An
admin adds it in settings → addons or with `zae addon add`, from a chart
reference and the inputs the chart asks for. The operator renders the chart,
checks it against the guardrails and writes a plan, which settings and `zae`
show; after the admin confirms, it applies the chart into the platform
namespace from one `ZaentrumAddon` resource. Once the addon is Ready, portal-api installs it from its primary's
address like any other addon ([installing](./installing.md)), so its manifest,
console, slots and setup checklist work unchanged. Removing it deletes
everything the chart created.

> **Status — design ahead of the release.** This page is the contract that the
> operator's addon controller, portal-api's chart API and `zae addon` are built
> against. Until a platform release ships them, deploy an addon through your
> own channel and install it from its address, as [installing](./installing.md)
> describes.

```mermaid
sequenceDiagram
    participant Admin as admin (settings or zae)
    participant API as portal-api
    participant CR as ZaentrumAddon
    participant Op as operator
    participant Reg as chart registry
    Admin->>API: chart reference · values · secret inputs
    API->>API: create / patch the values Secret (never read)
    API->>CR: create, suspend: true
    Op->>Reg: fetch the chart, verify the digest
    Op->>Op: render · validate values · guardrails
    Op->>CR: status.plan, phase Planned
    Admin->>API: review the plan → install
    API->>CR: suspend: false
    Op->>Op: server-side apply, every object owned by the resource
    Op->>CR: components ready, phase Ready
    API->>API: install from http://<primary> — manifest, app, tiles, rows
```

## 1. The chart

A normal Helm chart: `helm template` and `helm lint` work on it as on any
other. Three conventions make it an addon chart — annotations in `Chart.yaml`,
inputs in `values.schema.json`, and platform facts read from
`.Values.zaentrum`.

### Chart.yaml

```yaml
apiVersion: v2
name: example
description: An example addon with a worker
type: application
version: 1.2.0
appVersion: "4.1.0"
annotations:
  zaentrum.io/addon: "true"            # required: charts without it are refused
  zaentrum.io/primary: example         # required: the Service that serves the manifest
  zaentrum.io/title: example           # optional display metadata
  zaentrum.io/description: An example addon with a worker
  zaentrum.io/icon: puzzle
```

| Annotation | Rule |
|---|---|
| `zaentrum.io/addon` | `"true"`. A chart without it is refused |
| `zaentrum.io/primary` | The name of the Service, on port 80, that serves `/.well-known/zaentrum-capability.json` — the addon's [manifest](./cli.md#descriptor-schema-v1). portal-api registers the addon from `http://<primary>` |
| `zaentrum.io/title`, `zaentrum.io/description`, `zaentrum.io/icon` | Optional display metadata, carried in the plan's chart annotations. The addon's app, tiles and rows still come from its manifest |

The addon's name is the Helm release name: a DNS-1123 label of at most 40
characters. Settings and `zae` default it to the last segment of the chart
reference without version or extension — `example` for both
`oci://ghcr.io/example/charts/example` and
`https://example.org/charts/example-1.2.0.tgz`.

Give the objects fixed names, and name the primary Service exactly what
`zaentrum.io/primary` says. The annotation is static, and one namespace holds
one instance of an addon anyway — the manifest's `service` is its key there.

### values.schema.json

The schema declares the install inputs. Helm validates the merged values
against it (JSON Schema draft-07), settings renders the install form from it,
and `zae` prints the inputs from it.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["database", "config"],
  "properties": {
    "database": {
      "type": "object",
      "title": "Database",
      "required": ["url"],
      "properties": {
        "url": {
          "type": "string",
          "title": "Connection URL",
          "description": "postgres://user:password@host:5432/example",
          "minLength": 1,
          "writeOnly": true
        }
      }
    },
    "config": {
      "type": "object",
      "required": ["key"],
      "properties": {
        "key": {
          "type": "string",
          "title": "Settings encryption key",
          "writeOnly": true,
          "x-zaentrum-generate": "random-base64-32"
        }
      }
    },
    "worker": {
      "type": "object",
      "title": "Worker",
      "properties": {
        "replicas": { "type": "integer", "title": "Replicas", "default": 1, "minimum": 0, "maximum": 4 },
        "logLevel": { "type": "string", "title": "Log level", "enum": ["debug", "info", "warn"], "default": "info" }
      }
    }
  }
}
```

| Keyword | Meaning |
|---|---|
| `"writeOnly": true` on a string | A **secret input**: a password field in settings, `--set-secret` in `zae`. It is stored only in the addon's values Secret and never shown back — a plan says *set* or *missing* |
| `"x-zaentrum-generate": "random-base64-32"` or `"random-hex-32"` | A **generated input**. The first time the operator plans the addon and no value is given, it generates one, stores it in the Secret `zaentrum-addon-<name>-generated` — one key per dotted path — and never regenerates it. Such a property may be `required`: generating happens before validation |
| `title`, `description`, `default`, `enum`, `required` | The install form: labels, help text, prefilled values, a select, required markers. A boolean is a checkbox; a nested object is a group of fields |
| Everything else in draft-07 | Validated by Helm, as with `helm install` |

- Inputs are addressed by **dotted path** — `database.url`, `config.key` —
  in secret keys, generated keys, `zae --set` and `valuesFrom[].targetPath`.
  Keep property names to letters, digits, `_` and `-`.
- `required` asks only that a key exists. A chart whose `values.yaml` carries
  the key with an empty string passes it; add `"minLength": 1` to a string
  that must be given.
- Leave secret and generated inputs out of `values.yaml`. A secret default is
  the same secret on every instance, and a generated input needs no default.
- Declare install inputs, not configuration. What an admin changes while the
  addon runs belongs in its console ([configuration](./configuration.md)).

### Platform values

The operator sets the top-level key `zaentrum` last, over anything the chart's
defaults or an admin put there. Charts read platform facts only from it:

```yaml
zaentrum:
  namespace: zaentrum
  hostname: media.example.org
  issuer: https://media.example.org/auth/realms/zaentrum
  issuerHostAliasIP: ""
  imagePullSecrets: []
  partOf: zaentrum-addons
  events:
    brokers: kafka:9092
    topicPrefix: stube.
    tlsSecret: ""
  media:
    claimName: media
```

| Key | Value |
|---|---|
| `namespace` | The platform namespace, which is the addon's namespace |
| `hostname` | The platform's public hostname (`spec.hostname`) |
| `issuer` | The OIDC issuer the platform services use — the one tokens reaching the addon are issued by |
| `issuerHostAliasIP` | `spec.network.issuerHostAliasIP`: an IP for a `hostAliases` entry that lets a pod validating tokens reach an edge-terminated issuer from inside the cluster; empty for none |
| `imagePullSecrets` | Pull secret names (`spec.imagePullSecrets`); empty for public images |
| `partOf` | `<platform part-of or namespace>-addons`, the value for `app.kubernetes.io/part-of` |
| `events.brokers` | The Kafka bootstrap address the platform uses — the bundled broker or the shared cluster |
| `events.topicPrefix` | The tenant prefix every topic carries ([events](./events.md)) |
| `events.tlsSecret` | The Secret with `user.crt`, `user.key` and `ca.crt` for mutual TLS to the brokers; empty for plaintext |
| `media.claimName` | The platform's media PersistentVolumeClaim, for an addon that writes files for [ingest](./ingest.md) |

**Precedence**, lowest first: the chart's `values.yaml`, generated values,
`spec.values`, each `spec.valuesFrom` entry in order, and `zaentrum`.

### Templates

Templates are ordinary Helm templates. A worker that reads its inputs and the
platform's facts:

```yaml
# templates/worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-worker
spec:
  replicas: {{ .Values.worker.replicas }}
  selector:
    matchLabels:
      app: example-worker
  template:
    metadata:
      labels:
        app: example-worker
    spec:
      {{- with .Values.zaentrum.imagePullSecrets }}
      imagePullSecrets:
        {{- range . }}
        - name: {{ . }}
        {{- end }}
      {{- end }}
      securityContext:
        runAsNonRoot: true
      containers:
        - name: worker
          image: ghcr.io/example/example-worker:{{ .Chart.AppVersion }}
          env:
            - name: OIDC_ISSUER
              value: {{ .Values.zaentrum.issuer | quote }}
            - name: KAFKA_BROKERS
              value: {{ .Values.zaentrum.events.brokers | quote }}
            - name: TOPIC_PREFIX
              value: {{ .Values.zaentrum.events.topicPrefix | quote }}
            - name: LOG_LEVEL
              value: {{ .Values.worker.logLevel | quote }}
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: example-env, key: database-url }
            - name: EXAMPLE_CONFIG_KEY
              valueFrom:
                secretKeyRef: { name: example-env, key: config-key }
          volumeMounts:
            - { name: media, mountPath: /media }
      volumes:
        - name: media
          persistentVolumeClaim:
            claimName: {{ .Values.zaentrum.media.claimName }}
---
# templates/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: example-env
type: Opaque
stringData:
  database-url: {{ .Values.database.url | quote }}
  config-key: {{ .Values.config.key | quote }}
```

The primary is a Deployment named `example` with a Service of the same name on
port 80, serving the manifest, the console and its API. Leave the
`zaentrum.io/*` labels out of templates: the operator sets them
([guardrails](#3-guardrails)).

## 2. The `ZaentrumAddon` resource

Group `zaentrum.io`, version `v1alpha1`, namespaced, short name `zaddon`. One
per addon, in the platform's namespace; its name is the addon's name.

```yaml
apiVersion: zaentrum.io/v1alpha1
kind: ZaentrumAddon
metadata:
  name: example
  namespace: zaentrum
spec:
  chart:
    ref: oci://ghcr.io/example/charts/example
    version: 1.2.0
    digest: sha256:…
  values:
    worker:
      replicas: 2
  valuesFrom:
    - kind: Secret
      name: zaentrum-addon-example-values
      valuesKey: database.url
      targetPath: database.url
  suspend: false
```

| Field | Meaning |
|---|---|
| `spec.chart.ref` | `oci://registry/path/chart`, or an `https://` link to a chart archive |
| `spec.chart.version` | The tag, required for an `oci://` chart; an https archive is one version and ignores it |
| `spec.chart.digest` | Optional `sha256:…`; the fetched archive must match it |
| `spec.values` | Non-secret values, any shape |
| `spec.valuesFrom[]` | Values from Secrets or ConfigMaps in the namespace, applied in order: `kind` (`Secret` or `ConfigMap`), `name`, `valuesKey` (default `values.yaml`, a whole YAML or JSON values document), `targetPath` (set this dotted path to the key's raw string instead), `optional` |
| `spec.suspend` | `true` plans only: fetch, render, validate and report the plan, apply and prune nothing |

The status is the plan and the progress:

| Field | Meaning |
|---|---|
| `status.phase` | See below |
| `status.message` | One human line |
| `status.observedGeneration` | The generation the status was written for |
| `status.lastAppliedChart` | `ref`, `version` and `digest` of what actually runs |
| `status.plan.chart` | `name`, `version`, `appVersion`, `description`, `digest` and `annotations` of the fetched chart |
| `status.plan.valuesSchema` | The chart's `values.schema.json` as a string; empty when it has none |
| `status.plan.valuesErrors[]` | Schema and render errors, e.g. a missing required input |
| `status.plan.violations[]` | Guardrail refusals, e.g. `Deployment/example-worker: hostPath volume not allowed` |
| `status.plan.objects[]` | `kind` and `name` of every rendered object |
| `status.plan.workloads[]` | `kind`, `name`, `images[]` and `ports[]` of every workload |
| `status.plan.changes` | Against what was last applied: `added[]` and `removed[]` objects, `images[]` changes |
| `status.components[]` | The applied workloads: `name`, `kind`, `ready`, `desired`, `reason` |
| `status.conditions[]` | `Ready` and `Planned` |

The plan is refreshed on every reconcile, suspended or not.

| Phase | Meaning |
|---|---|
| `Pending` | Not planned yet |
| `Planned` | Suspended, and the plan has no violations or values errors: it can be installed |
| `PlanFailed` | Suspended, and planning found violations or values errors, or could not finish (see `message`) |
| `Installing` | Applied; components not ready yet |
| `Ready` | Every component is ready |
| `Degraded` | Applied, and a component is not ready |
| `Failed` | Not suspended, and planning or applying failed. Also the phase when the namespace holds no `Zaentrum` platform — the resource needs exactly one |

An addon's phase never touches the platform's: the addon controller is apart
from the platform reconciler, and a broken addon fails alone.

## 3. Guardrails

The operator checks every rendered object before it applies any. One refusal
is a violation in the plan, and nothing is applied.

| Rule | Refused |
|---|---|
| **Kinds** | Anything but Deployment, Service, ConfigMap, Secret, ServiceAccount, Job and PersistentVolumeClaim. No RBAC, no CRDs, no cluster-scoped objects, no Routes or Ingresses — an addon's UI is reached through the [portal proxy](./console.md) |
| **Namespace** | A `metadata.namespace` other than the resource's |
| **Pods** | `hostPath` volumes; `hostNetwork`, `hostPID`, `hostIPC`; privileged containers; `allowPrivilegeEscalation: true`; added capabilities; `runAsUser: 0` |
| **Volumes** | Anything but `configMap`, `secret`, `emptyDir`, `projected`, `downwardAPI` and `persistentVolumeClaim` — a claim the chart renders, or `zaentrum.media.claimName` |
| **Service accounts** | A `serviceAccountName` the chart does not render (empty and `default` are allowed) |
| **Ownership** | An object of the same kind and name that exists and is not owned by this addon — a platform service, another addon's object, something created by hand |

Any image may run. Where a pod spec leaves them unset, the operator sets
`runAsNonRoot: true`, the `RuntimeDefault` seccomp profile,
`allowPrivilegeEscalation: false` and drops all capabilities — build images
that run as a non-root user.

Fetching is guarded too: OCI charts are pulled anonymously, and https archives
are fetched over https only, up to 10 MiB, within 30 seconds, without
redirects to another scheme. A `digest` must match.

What the operator adds to every object it applies, with the field manager
`zaentrum-addon`:

- an owner reference to the `ZaentrumAddon`, so deleting the resource deletes
  the object;
- the labels `zaentrum.io/addon=<name>`, `app.kubernetes.io/managed-by=zaentrum-operator`,
  `app.kubernetes.io/instance=<name>` and `app.kubernetes.io/part-of=<zaentrum.partOf>`;
  Deployments and their pod templates also `zaentrum.io/component=<Deployment name>`;
- on pod templates, the annotation `zaentrum.io/values-checksum` — the SHA-256
  of the merged values — so a values change rolls the pods.

Objects labelled with the addon that a new render no longer contains are
pruned. A values Secret or ConfigMap referenced from `valuesFrom` and labelled
`zaentrum.io/addon=<name>` is owned by the resource too, unless it is labelled
`zaentrum.io/keep=true`.

## 4. Installing from settings

Settings → **addons** → **+**:

1. **Chart.** A chart reference with an optional version and digest — or a
   pasted values JSON together with the reference.
2. **Plan.** The chart's name, version and description; every workload with
   its images and ports; the objects; violations and values errors, either of
   which blocks installing. Below it, the install form generated from
   `values.schema.json`: a password field for a secret input, required
   markers, defaults, a select for an `enum`, a checkbox for a boolean, groups
   for nested objects, and *generated* for a generated input. Changing an input
   plans again.
3. **Install.** Progress, component by component, until the addon is Ready and
   registered.

A chart addon's row has **upgrade** (a new version, planned with its changes,
then applied), **values** (edit non-secret values, set or clear secret inputs)
and **remove** (with *keep values*). An addon that was only ever planned can be
cancelled, which deletes it.

Scripted, with an admin bearer — the settings page makes the same calls:

```sh
# create the addon suspended, with its inputs; the operator plans it
curl -X POST https://<instance>/api/portal/addon-charts \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"chart":"oci://ghcr.io/example/charts/example","version":"1.2.0",
       "values":{"worker":{"replicas":2}},
       "secretValues":{"database.url":"postgres://…"}}'
# 202 {"name":"example"}

# the plan, and later the progress
curl -H "Authorization: Bearer $TOKEN" https://<instance>/api/portal/addon-charts/example

# install the current plan
curl -X POST -H "Authorization: Bearer $TOKEN" https://<instance>/api/portal/addon-charts/example/install
```

| Call | Does |
|---|---|
| `POST /api/portal/addon-charts` | Body `name` (optional, defaulted from the reference), `chart`, `version`, `digest`, `values`, `secretValues` (`{"dotted.path": "value"}`). Writes the Secret `zaentrum-addon-<name>-values`, one key per secret path, without reading it; creates or updates the resource with `suspend: true`, the values and one `valuesFrom` entry per secret key. Answers `202` with the name |
| `GET /api/portal/addon-charts/{name}` | `name`, `suspended`, `phase`, `message`, `plan`, `components`, `lastAppliedChart`, `values` and `secretKeys` — the dotted paths of the secret inputs that are set, never their values |
| `POST /api/portal/addon-charts/{name}/install` | Clears `suspend`. `409` when there is no plan for the current generation yet, or it has violations or values errors |
| `PATCH /api/portal/addon-charts/{name}` | `version`, `chart`, `digest`, `values`, `secretValues`, `clearSecrets` (paths), `suspend`. Changing the chart or its version suspends the addon to plan it first, unless the body says `"suspend": false` |
| `DELETE /api/portal/addon-charts/{name}?keepValues=true` | Deletes the resource — and with it everything it applied — and the addon's registry rows. `keepValues=true` labels the values Secret `zaentrum.io/keep=true` first |

`GET /api/portal/addons` lists chart addons next to addons installed from an
address, with `chart` (`ref`, `version`), `phase`, `suspended` and the
components from the resource's status.

## 5. Installing with zae

[`zae addon`](./cli.md#installing-addons-zae-addon) makes the same calls from
a terminal or a script, and prints the plan before it installs:

```sh
export ZAE_TOKEN=…   # an admin bearer
zae addon add oci://ghcr.io/example/charts/example --version 1.2.0 \
  --url https://media.example.org --set worker.replicas=2 --set-secret database.url="$DATABASE_URL"
zae addon status example --url https://media.example.org
zae addon upgrade example --version 1.3.0 --url https://media.example.org --wait
zae addon remove example --url https://media.example.org --keep-values
```

## 6. GitOps: committing the resource

Committing a `ZaentrumAddon` and its values Secret to a deployment repository
installs the addon just as settings does; the review is the pull request
instead of the plan screen.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: zaentrum-addon-example-values
  namespace: zaentrum
  labels:
    zaentrum.io/addon: example        # owned by the addon, removed with it
type: Opaque
stringData:
  database.url: postgres://example:…@postgres:5432/example
---
apiVersion: zaentrum.io/v1alpha1
kind: ZaentrumAddon
metadata:
  name: example
  namespace: zaentrum
spec:
  chart:
    ref: oci://ghcr.io/example/charts/example
    version: 1.2.0
  values:
    worker:
      replicas: 2
  valuesFrom:
    - kind: Secret
      name: zaentrum-addon-example-values
      valuesKey: database.url
      targetPath: database.url
```

- Without `suspend`, the operator applies as soon as the plan is clean. To
  read the plan first, commit `suspend: true`, look at
  `kubectl get zaentrumaddon example -o jsonpath='{.status.plan}'`, then commit
  `suspend: false`.
- Commit the Secret the way the repository commits any Secret — encrypted, or
  created by the pipeline — never as plain text.
- portal-api registers every Ready addon it finds, so a committed addon appears
  in settings → addons like one added there.
- Give each addon one owner. A pipeline that re-applies the committed resource
  reverts what settings or `zae` change on it.

## 7. Upgrades and removal

**Upgrade** from settings, with `zae addon upgrade`, or with a commit that
changes `version`. Settings and `zae` plan first: changing the chart suspends
the addon until the new plan is installed, while what runs keeps running, and
the plan lists the changes — objects added and removed, images replaced. A
values change rolls the pods through the values checksum.

**Remove** from settings, with `zae addon remove`, or by deleting the resource.
Garbage collection deletes:

- every object the chart applied — including a PersistentVolumeClaim it
  rendered, and with it, depending on the storage class, its data;
- the values Secret, unless it is kept;
- the generated values. A reinstall generates new ones, so data the addon
  encrypted with a generated key cannot be read afterwards. When that data
  outlives the addon — a database the chart does not create — give the key as a
  secret input and keep the values instead.

It keeps what the chart did not create: the media volume, an external
database. Settings and `zae` also remove the addon's registry rows.

## Checklist

- `Chart.yaml`: `apiVersion: v2`, `type: application`,
  `zaentrum.io/addon: "true"`, and `zaentrum.io/primary` naming the Service
  that serves the manifest on port 80.
- Every install input in `values.schema.json`: secrets `writeOnly`, keys the
  operator can make `x-zaentrum-generate`, `minLength: 1` where empty is not an
  answer; no secret or generated input in `values.yaml`.
- Platform facts from `.Values.zaentrum`, never asked for as inputs and never
  hard-coded.
- Only the allowed kinds; fixed object names; images that run as non-root, with
  no host access; volumes from the chart's own claims or the media claim.
- Configuration an admin edits later in the addon's console, not in the chart
  ([configuration](./configuration.md)).
- `helm lint` and `helm template` pass with the values an admin would give.
