# Addon charts — addons the platform installs

An addon can ship as a **standard Helm chart** that the platform installs
itself ([ADR-0011](../adr/0011-addon-charts-installed-by-the-operator.md)). An
admin adds it in settings → addons or with `zae addon add`, from a chart
reference and the inputs the chart asks for. The operator renders the chart,
checks it against the guardrails and writes a plan, which settings and `zae`
show; after the admin confirms, it applies the chart into the platform
namespace from one `ZaentrumAddon` resource. Once the addon is Ready,
portal-api installs it from its primary's address like any other addon
([installing](./installing.md)), so its manifest, console, slots and setup
checklist work unchanged. Removing it deletes everything the chart created.

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
    API->>API: create a new values Secret (create only, never read)
    API->>CR: create or update, suspend: true, valuesFrom → that Secret
    CR-->>Admin: generation N
    Op->>Reg: fetch the chart, verify the digest
    Op->>Op: render · validate values · guardrails
    Op->>CR: status.plan for generation N
    Admin->>API: review the plan → install
    API->>CR: suspend: false
    Op->>Op: server-side apply, every object owned by the resource
    Op->>CR: components ready, phase Ready
    API->>API: register from http://<primary> — manifest, app, tiles, rows
```

## 1. The chart

A normal Helm chart: `helm template` and `helm lint` work on it as on any
other. Three conventions make it an addon chart — annotations in `Chart.yaml`,
inputs in `values.schema.json`, and platform facts read from
`.Values.zaentrum` — and the operator renders it in a particular way,
described [below](#how-the-operator-renders).

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

`apiVersion` must be `v2` and `type` `application` (or unset); a chart with a
`crds/` directory is refused.

**The addon's name is the Helm release name, and it must equal the manifest's
`service`.** portal-api registers a Ready chart addon only when the manifest at
its primary names the same service; otherwise the addon runs, stays
unregistered, and says why in `registrationError`. The name is a DNS-1123 label
of at most 40 characters. Settings and `zae` default it to the last segment of
the chart reference without tag, archive extension or trailing `-<version>`,
lower-cased — `example` for both `oci://ghcr.io/example/charts/example` and
`https://example.org/charts/Example-1.2.0.tgz`.

Give the objects fixed names and name the primary Service exactly what
`zaentrum.io/primary` says. The annotation is static, and one namespace holds
one instance of an addon anyway. Names starting with `zaentrum-addon-` are
reserved for addon values and refused.

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
| `"writeOnly": true` on a string | A **secret input**: a password field in settings, a prompt or a file in `zae`. It is stored only in a values Secret and never shown back — a plan says *set* or *missing* |
| `"x-zaentrum-generate": "random-base64-32"` or `"random-hex-32"` | A **generated input**. The first time the operator plans the addon and no value is given, it generates one, stores it in the Secret `zaentrum-addon-<name>-generated` — one key per dotted path — and never regenerates it. Such a property may be `required`: generating happens before validation |
| `title`, `description`, `default`, `enum`, `required` | The install form: labels, help text, prefilled values, a select, required markers. A boolean is a checkbox; a nested object is a group of fields |
| Everything else in draft-07 | Validated by Helm, as with `helm install` |

- Inputs are addressed by **dotted path** — `database.url`, `config.key` —
  in secret keys, generated keys, `zae --set` and `valuesFrom[].targetPath`.
  Keep property names to letters, digits, `_` and `-`, and a secret input's
  path to 250 characters.
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
| `issuerHostAliasIP` | `spec.network.issuerHostAliasIP`: an IP address the platform maps its hostname to (a `hostAliases` entry), so pods validating tokens reach an issuer terminated at the edge from inside the cluster. Empty for none. A chart decides which host it aliases to it — typically the issuer's host |
| `imagePullSecrets` | Pull secret names (`spec.imagePullSecrets`); empty for public images. Pods may use them without the chart rendering them |
| `partOf` | `<platform part-of or namespace>-addons`, the value for `app.kubernetes.io/part-of` |
| `events.brokers` | The Kafka bootstrap address the platform uses — the bundled broker or the shared cluster |
| `events.topicPrefix` | The tenant prefix every topic carries ([events](./events.md)) |
| `events.tlsSecret` | The Secret with `user.crt`, `user.key` and `ca.crt` for mutual TLS to the brokers; empty for plaintext. Pods may mount it without the chart rendering it |
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

The primary is a Deployment named `example` with a ClusterIP Service of the
same name on port 80, serving the manifest, the console and its API. Leave the
`zaentrum.io/*` labels out of templates: the operator sets them
([guardrails](#3-guardrails)).

### How the operator renders

The operator is not `helm install`. It uses Helm's template engine and applies
the result itself, the way it applies the platform:

- **Rendered again and again.** Every reconcile renders the chart anew — when
  the resource, a values Secret it reads or the platform changes, when an
  owned Deployment changes, and at least every five minutes. A template must
  render the same objects from the same values every time.
- **Applied with server-side apply, with force.** The field manager is
  `zaentrum-addon`. Every field the rendered chart sets is taken back from
  whoever changed it, so a hand edit to one lasts until the next reconcile.
- **No cluster, no release.** Rendering happens in memory: `lookup` returns
  nothing, `.Release.IsInstall` is always true and `.Release.IsUpgrade` always
  false, `.Release.Revision` is 1, and `.Capabilities` are Helm's defaults,
  not the cluster's. There is no Helm release, no release history and no
  `helm rollback`.
- **Hooks are plain objects.** Test hooks (`helm.sh/hook: test`) are skipped.
  Every other hook — `pre-install`, `post-upgrade` and the rest — is applied
  as an ordinary object on every reconcile, without hook order, weights or
  delete policies.
- **Jobs stay, and run again when they change.** `ttlSecondsAfterFinished` is
  removed, so a finished Job stays until the chart stops rendering it —
  otherwise the next reconcile would create it and run it again. A Job whose
  pod template changes — a new image, new values — is deleted and created
  anew, which runs it again. Write Jobs that can run more than once.
- **No random values, no lookups for secrets.** `randAlphaNum`, `randBytes`,
  `uuidv4`, `genPrivateKey`, `now` and their kind render a new value every
  time: the Secret holding it changes, the values checksum moves and the pods
  roll, every five minutes. `lookup` finds nothing to keep. A value generated
  once is an `x-zaentrum-generate` input.
- **Errors say where, not what.** A schema error names the property. A
  template error is reported by its location only — `template error at
  example/templates/worker.yaml:12:3` — because its message is the chart's own
  text and could carry a value (Helm's `fail` prints its argument).

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
      name: zaentrum-addon-example-values     # zaentrum-addon-<addon>-…, labelled zaentrum.io/addon: example
      valuesKey: database.url
      targetPath: database.url
  suspend: false
```

| Field | Meaning |
|---|---|
| `spec.chart.ref` | `oci://registry/path/chart` — without a tag or digest — or an `https://` link to a chart archive |
| `spec.chart.version` | The tag, required for an `oci://` chart; an https archive is one version and ignores it |
| `spec.chart.digest` | Optional `sha256:…`; the fetched archive must match it |
| `spec.values` | Non-secret values: a JSON object |
| `spec.valuesFrom[]` | Values from Secrets or ConfigMaps of the addon, applied in order: `kind` (`Secret` or `ConfigMap`), `name`, `valuesKey` (default `values.yaml`, a whole YAML or JSON values document), `targetPath` (set this dotted path to the key's raw string instead), `optional` (tolerate a missing object or key) |
| `spec.suspend` | `true` plans only: fetch, render, validate and report the plan, apply and prune nothing |
| `metadata.annotations["zaentrum.io/keep-values"]` | `"true"` keeps the addon's values Secrets and its generated values when the resource is deleted — see [values Secrets](#values-secrets) |

**A valuesFrom object must belong to the addon:** named
`zaentrum-addon-<addon>-…` *and* labelled `zaentrum.io/addon: <addon>`.
Anything else is refused as a values error without being read — `optional`
included. The operator can read every Secret in the namespace; this keeps an
addon from having it read a platform Secret into chart values.

The status is the plan and the progress:

| Field | Meaning |
|---|---|
| `status.phase` | See below |
| `status.message` | One human line |
| `status.observedGeneration` | The generation the status was written for. A plan is current when it equals `metadata.generation` |
| `status.lastAppliedChart` | `ref`, `version` and `digest` of what actually runs |
| `status.plan.chart` | `name`, `version`, `appVersion`, `description`, `digest` and `annotations` of the fetched chart |
| `status.plan.valuesSchema` | The chart's `values.schema.json` as a string; empty when it has none |
| `status.plan.valuesErrors[]` | Schema and render errors, e.g. a missing required input |
| `status.plan.violations[]` | Guardrail refusals, e.g. `Deployment/example-worker: hostPath volume not allowed` |
| `status.plan.objects[]` | `kind` and `name` of every rendered object |
| `status.plan.workloads[]` | `kind`, `name`, `images[]` and `ports[]` of every Deployment and Job |
| `status.plan.changes` | Against what was last applied: `added[]` and `removed[]` objects, `images[]` changes |
| `status.components[]` | The applied Deployments: `name`, `kind`, `ready`, `desired`, `reason` |
| `status.conditions[]` | `Ready` and `Planned` |

The plan is refreshed on every reconcile, suspended or not.

| Phase | Meaning |
|---|---|
| *(none)* | Not reconciled yet — no phase is written before the first reconcile |
| `Planned` | Suspended, and the plan has no violations or values errors: it can be installed |
| `PlanFailed` | Suspended, and planning found violations or values errors, or the chart could not be fetched or loaded (see `message`) |
| `Installing` | Applied; components not ready yet |
| `Ready` | Every component is ready |
| `Degraded` | Applied, and a component is not ready, or its rollout stalled |
| `Failed` | Not suspended, and planning or applying failed. Also — suspended or not — when the addon's name is invalid, the platform values cannot be derived, or the namespace holds no `Zaentrum` platform or more than one |

An addon's phase never touches the platform's: the addon controller is apart
from the platform reconciler, and a broken addon fails alone.

### Values Secrets

Secret inputs live in Secrets of the addon, and no client ever changes one:

- **Every write makes a new Secret.** portal-api stores the secret inputs a
  request sets in a new Secret, `zaentrum-addon-<addon>-values-<suffix>`,
  labelled `zaentrum.io/addon: <addon>`, and points each input's `valuesFrom`
  entry at it — `valuesKey` and `targetPath` both the dotted path. Inputs set
  earlier keep pointing where they did. So a secret change is a spec change: a
  new generation, and a new plan.
- **The operator cleans up.** It takes ownership of the values Secrets an addon
  reads, so they go with the addon. A values Secret nothing references any more
  is deleted after ten minutes — portal-api creates a Secret before it points
  the addon at it, and must not lose that race — and one belonging to an addon
  that does not exist is deleted after an hour. A Secret labelled
  `zaentrum.io/keep=true` is never touched.
- **Generated values** are in `zaentrum-addon-<addon>-generated`, owned by the
  addon.
- **Keeping values.** With `zaentrum.io/keep-values: "true"` on the resource
  when it is deleted, the operator's finalizer `zaentrum.io/addon-values`
  takes its owner references off the values Secrets and the generated values
  Secret and labels them `zaentrum.io/keep=true`, so they outlive the addon. It
  lets go without keeping them when the namespace is terminating or no platform
  is left.
- **Using kept values.** A new addon of the same name points its inputs at a
  kept Secret with `secretRefs` (settings, the API) or `zae addon add
  --secret-ref`, and finds the kept generated values and uses them instead of
  generating new ones.

## 3. Guardrails

The operator checks the chart and every rendered object before it applies
anything. One refusal is a violation in the plan, and nothing is applied.

| Rule | Refused |
|---|---|
| **Chart** | `apiVersion` other than `v2`; `type` other than `application`; a missing `zaentrum.io/addon: "true"` or `zaentrum.io/primary`; a `crds/` directory |
| **Kinds** | Anything but ServiceAccount, Secret, ConfigMap, PersistentVolumeClaim and Service (`v1`), Deployment (`apps/v1`) and Job (`batch/v1`) — in exactly those API versions. No RBAC, no CRDs, no cluster-scoped objects, no Routes or Ingresses: an addon's UI is reached through the [portal proxy](./console.md) |
| **Objects** | A `metadata.namespace` other than the resource's; the same kind and name rendered twice; a name starting with `zaentrum-addon-`, reserved for addon values; `metadata.ownerReferences` set by the chart; the `kubernetes.io/service-account.name` and `.uid` annotations |
| **Primary** | No Service named by `zaentrum.io/primary`, or one without port 80 |
| **Secrets** | A type other than `Opaque`, `kubernetes.io/tls`, `kubernetes.io/dockerconfigjson`, `kubernetes.io/basic-auth` and `kubernetes.io/ssh-auth` — above all `kubernetes.io/service-account-token` |
| **Services** | A type other than ClusterIP; `externalIPs`, `externalName`, `loadBalancerIP`, `loadBalancerSourceRanges` |
| **PersistentVolumeClaims** | `volumeName`, `dataSource`, `dataSourceRef` — binding or cloning an existing volume |
| **Pods** — in Deployments and Jobs | `hostNetwork`, `hostPID`, `hostIPC`, `hostPort`; privileged containers; `allowPrivilegeEscalation: true`; added capabilities; `runAsUser: 0`; `runAsNonRoot: false`; `procMount: Unmasked`; `seLinuxOptions.type`; `sysctls`; an `Unconfined` AppArmor profile; `windowsOptions.hostProcess`; `priorityClassName`; `nodeName`; a nodeSelector, node affinity or toleration for control-plane nodes, and a toleration matching every taint |
| **Volumes and references** | Volumes other than `configMap`, `secret`, `emptyDir`, `projected`, `downwardAPI` and `persistentVolumeClaim`; a claim other than one the chart renders or `zaentrum.media.claimName`; a Secret or ConfigMap the chart does not render, referenced from a volume, a projected source, `env`, `envFrom` or `imagePullSecrets` — except `zaentrum.events.tlsSecret` and `zaentrum.imagePullSecrets`; a `serviceAccountName` the chart does not render (empty and `default` are allowed) |
| **Ownership** | An object of the same kind and name that exists and is not controlled by this addon — a platform service, another addon's object, something created by hand |

Any image may run. Where a pod spec leaves them unset, the operator sets
`automountServiceAccountToken: false`, `runAsNonRoot: true`, the
`RuntimeDefault` seccomp profile, `allowPrivilegeEscalation: false`, and drops
all capabilities — build images that run as a non-root user.

**Fetching** is guarded too. OCI charts are pulled anonymously. An https
archive is fetched over https only — a redirect to another scheme is refused —
up to 10 MiB, unpacking to at most 20 MiB, within 30 seconds. A `digest` must
match. The fetcher refuses to connect to loopback, link-local and cloud
metadata addresses and to the cluster's own API server, checked after DNS
resolution; private (RFC 1918) addresses stay allowed, for registries on a
private network.

What the operator adds to every object it applies:

- an owner reference to the `ZaentrumAddon` (as controller), so deleting the
  resource deletes the object;
- the labels `zaentrum.io/addon=<name>`, `app.kubernetes.io/managed-by=zaentrum-operator`,
  `app.kubernetes.io/instance=<name>` and `app.kubernetes.io/part-of=<zaentrum.partOf>`;
  Deployments and their pod templates also `zaentrum.io/component=<Deployment name>`;
- on pod templates, the annotation `zaentrum.io/values-checksum` — the SHA-256
  of the merged values — so a values change rolls the pods.

**Prune** deletes what a new render no longer contains, and only objects of
the allowed kinds that carry `zaentrum.io/addon=<name>` *and*
`app.kubernetes.io/managed-by=zaentrum-operator` *and* are controlled by this
very resource. A values Secret labelled for the addon by someone else is never
pruned.

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
# 202 {"name":"example","generation":1,"observedGeneration":0,"chart":{…}}

# the plan — current once observedGeneration reaches the write's generation
curl -H "Authorization: Bearer $TOKEN" https://<instance>/api/portal/addon-charts/example

# install the current plan
curl -X POST -H "Authorization: Bearer $TOKEN" https://<instance>/api/portal/addon-charts/example/install
```

| Call | Does |
|---|---|
| `GET /api/portal/addon-charts` | `available` and a `note` saying why not: outside a cluster, a cluster without the `ZaentrumAddon` resource, or a portal-api Role without it |
| `POST /api/portal/addon-charts` | Body `name` (optional, defaulted from the reference), `chart`, `version`, `digest`, `values`, `secretValues` (`{"dotted.path": "value"}`), `secretRefs` (`{"dotted.path": {"name": "zaentrum-addon-<addon>-…", "key": "…"}}`, the key defaulting to the path). Creates the resource, or updates the one of that name, with `suspend: true`. Values are **replaced**; secret inputs are **added** to those already set, stored in a new values Secret. `409` when the name belongs to an addon installed from an address or to an app registered by hand |
| `GET /api/portal/addon-charts/{name}` | `name`, `chart` (what the resource asks for), `suspended`, `phase`, `message`, `generation`, `observedGeneration`, `plan`, `components`, `lastAppliedChart` (what runs), `values`, `secretKeys` (the paths of the secret inputs that are set, never their values), `secretRefs` (where each is read from), `registered` and `registrationError` |
| `POST /api/portal/addon-charts/{name}/install` | Clears `suspend`. `409` while there is no plan for the current generation, or it has violations or values errors |
| `PATCH /api/portal/addon-charts/{name}` | `version`, `chart`, `digest`, `values`, `secretValues`, `secretRefs`, `clearSecrets` (paths), `suspend`. A new chart, version or digest suspends the addon to plan it first, unless the body says `"suspend": false`; a new chart or version drops the digest unless the body sends one |
| `DELETE /api/portal/addon-charts/{name}?keepValues=true` | Sets `zaentrum.io/keep-values` on the resource to what `keepValues` says, deletes it — and with it everything it applied — and removes the addon's registry rows. Answers `name`, `resource`, `keptValues` and the `removed` rows |

Every write answers `202` with the `generation` it made, `observedGeneration`
and the `chart`; a client waits for the plan of its own write by waiting for
`observedGeneration` to reach that generation. When the instance cannot manage
chart addons at all, the chart endpoints answer `503` with the same note as
`GET /api/portal/addon-charts`.

`GET /api/portal/addons` lists chart addons next to addons installed from an
address, with `chart` (`ref`, `version`, `digest` and `lastApplied`), `phase`,
`suspended`, `registered`, `registrationError` and the components from the
resource's status.

## 5. Installing with zae

[`zae addon`](./cli.md#installing-addons-zae-addon) makes the same calls from
a terminal or a script, waits for the plan of its own write, and prints it
before it installs:

```sh
export ZAE_TOKEN=…   # an admin bearer
zae addon add oci://ghcr.io/example/charts/example --version 1.2.0 \
  --url https://media.example.org --set worker.replicas=2 --set-secret database.url
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
  name: zaentrum-addon-example-values     # must start zaentrum-addon-<addon>-
  namespace: zaentrum
  labels:
    zaentrum.io/addon: example            # must name the addon
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

- The values Secret must be named `zaentrum-addon-<addon>-…` and labelled
  `zaentrum.io/addon: <addon>`, or the operator refuses to read it. The
  operator adopts it, so it goes with the addon; renaming it in the repository
  leaves the old one unreferenced, and the operator deletes that ten minutes
  later.
- Without `suspend`, the operator applies as soon as the plan is clean. To
  read the plan first, commit `suspend: true`, look at
  `kubectl get zaentrumaddon example -o jsonpath='{.status.plan}'`, then commit
  `suspend: false`.
- Commit the Secret the way the repository commits any Secret — encrypted, or
  created by the pipeline — never as plain text.
- portal-api registers every Ready addon it finds, so a committed addon appears
  in settings → addons like one added there; a chart addon whose resource was
  deleted is unregistered.
- To keep the values when deleting the resource, commit
  `zaentrum.io/keep-values: "true"` on it first.
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
- the values Secrets and the generated values — unless the removal keeps them
  (*keep values*, `zae addon remove --keep-values`, or
  `zaentrum.io/keep-values: "true"`). A reinstall without kept values
  generates new ones, so data the addon encrypted with a generated key cannot
  be read afterwards: keep the values when the data outlives the addon.

It keeps what the chart did not create: the media volume, an external
database. The addon's registry rows go with it.

## Checklist

- `Chart.yaml`: `apiVersion: v2`, `type: application`,
  `zaentrum.io/addon: "true"`, and `zaentrum.io/primary` naming the ClusterIP
  Service that serves the manifest on port 80. No `crds/`.
- The chart's name — the addon's name — equals the manifest's `service`.
- Every install input in `values.schema.json`: secrets `writeOnly`, keys the
  operator can make `x-zaentrum-generate`, `minLength: 1` where empty is not an
  answer; no secret or generated input in `values.yaml`.
- Platform facts from `.Values.zaentrum`, never asked for as inputs and never
  hard-coded; no reference to a platform Secret or ConfigMap except the ones
  handed over there.
- Only the allowed kinds, in their API versions; fixed object names, none under
  `zaentrum-addon-`; images that run as non-root, with no host access; volumes
  from the chart's own claims or the media claim.
- Templates that render the same objects every time: no `rand*`, `uuidv4`,
  `genPrivateKey`, `now` or `lookup` for anything kept. Hooks are plain objects;
  Jobs may run again.
- Configuration an admin edits later in the addon's console, not in the chart
  ([configuration](./configuration.md)).
- `helm lint` and `helm template` pass with the values an admin would give.
