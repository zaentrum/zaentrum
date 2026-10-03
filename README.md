# Zaentrum

**A neutral, self-hosted media platform for a library you own and are entitled to stream.**
Bring your own files — Zaentrum catalogs, processes, and streams them to clean clients on the
web, your phone/tablet, and your TV.

This repo is the **front door**: how to install, the release channels, and pointers to the
rest of the project.

**Product page → [zaentrum.github.io/zaentrum](https://zaentrum.github.io/zaentrum/)** ·
**Docs → [the wiki](https://github.com/zaentrum/zaentrum/wiki)**

> **Status: pre-release.** Container images are published as releases are cut — see
> [`releases.json`](./releases.json). The commands below describe the intended install flow.

---

## Install in one command

```bash
docker run -d --privileged --restart unless-stopped -p 80:80 --name zaentrum \
  ghcr.io/zaentrum/appliance:latest
open http://zaentrum.localhost
```

That single container runs the **whole platform**: a full Kubernetes (k3s) in-process, the
**operator**, and everything the operator brings up — the portal, the web app, the catalog and
its consoles, streaming, and bundled **Keycloak**, **Postgres**, **Valkey** and **Kafka**. One
image, one port, nothing else to install; the first boot pulls the platform's images from
`ghcr.io` and takes a few minutes. The image is **linux/amd64** only, and it needs host port
**80**: the platform's ingress and its sign-in are bound to `http://zaentrum.localhost` — no
other name, no other port.

There is **no setup wizard**. The first run is three steps
([self-hosting → first run](docs/self-hosting.md#first-run)): sign in as `admin` with the first
admin password, which the platform generates at install; add a TMDB key under **Catalog
Management → settings** (the images carry none); then copy your files into the library and
trigger a scan.

## Reaching it from your phone / TV

`*.localhost` only resolves on the host machine. To reach Zaentrum from other devices on your
LAN, pick a profile in the setup wizard (it wires the ingress **and** the login issuer
together):

| Profile | How devices reach it | DNS |
|---|---|---|
| This machine only | `*.localhost` (host browser only) | none |
| **LAN, single origin (recommended)** | the server's LAN IP, path-routed (`/`, `/api`, `/auth`) | none |
| LAN, magic wildcard | `zaentrum.<lan-ip>.nip.io` | none (needs internet) |
| mDNS | `zaentrum.local` | none |
| Real domain | your domain + wildcard + TLS | yes |

Clients use **Add Server** — point them at the IP / `.local` / domain.

## Identity

Out of the box Zaentrum runs its **own bundled Keycloak** and you manage users in the admin
UI. You can instead **federate your existing identity provider** (broker) or **delegate
directly** to an external OIDC provider — chosen in the setup wizard.

## Scale out / production

The same platform runs on any Kubernetes cluster via the **operator**, which reconciles the
whole stack from a single custom resource. Install it once, as cluster-admin, from its pinned
install manifest — the CRDs, the cluster RBAC and the controller, pinned to one immutable
`operator:sha-<commit>` image — then apply a `Zaentrum` CR:

```bash
kubectl apply -f https://raw.githubusercontent.com/zaentrum/zaentrum-operator/main/deploy/operator-install.yaml
kubectl create namespace zaentrum
kubectl apply -f zaentrum.yaml     # your Zaentrum CR — see docs/self-hosting.md
# or install the OLM bundle on OpenShift — see the operator repo's operator/bundle
```

## Documentation

Full deployment & operations docs live in **[`docs/`](docs/README.md)** — start there. It routes
by audience and covers every path:

- **[docs/README.md](docs/README.md)** — index + the four-layer deploy model
- **[Prerequisites](docs/prerequisites.md)** — cluster + external dependencies
- **[Self-hosting](docs/self-hosting.md)** — appliance · your-own-k8s · helm (+ values reference; the old k3s/Compose profiles are unsupported)
- **[Operator & CR reference](docs/operator.md)** — the operator + the complete `Zaentrum` CR spec
- **[Reference demo](docs/reference-demo.md)** — a worked operator + CI GitOps deploy
- **[Updating](docs/updating.md)** — day-2: app image · chart/operator roll · CR change
- **[Troubleshooting](docs/troubleshooting.md)** — symptom → cause → fix
- **[Architecture](docs/architecture.md)** — how it fits together

## Releases

Channels are tracked in [`releases.json`](./releases.json): `stable` and `edge`. The bundled
operator auto-updates against the channel you pin.

## Repository layout

| Repo | What it is |
|---|---|
| **`zaentrum/zaentrum`** *(this)* | install, releases, instructions — the front door |
| [`zaentrum/zaentrum-operator`](https://github.com/zaentrum/zaentrum-operator) | the Kubernetes operator — controller + CRD + deploy templates + OLM bundle |
| `zaentrum/<service>` | per-service repos (catalog, playback, web/mobile/TV clients, …) |

## License

[MPL-2.0](./LICENSE).
