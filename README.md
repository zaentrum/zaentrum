# Zaentrum

**A neutral, self-hosted media platform for a library you own and are entitled to stream.**
Bring your own files — Zaentrum catalogs, processes, and streams them to clean clients on the
web, your phone/tablet, and your TV.

This repo is the **front door**: how to install, the release channels, and pointers to the
rest of the project.

> **Status: pre-release.** Container images are published as releases are cut — see
> [`releases.json`](./releases.json). The commands below describe the intended install flow.

---

## Install in one command

```bash
docker run -d --privileged -p 80:80 --name zaentrum ghcr.io/zaentrum/zaentrum:latest
open http://zaentrum.localhost
```

That single container runs the **whole platform** — a full Kubernetes (k3s) in-process with
the web app, admin UI, catalog, transcode/package and streaming, plus bundled **Postgres**,
**Valkey** and **Kafka**. One image, one port, no external dependencies. The first-run wizard
at **`/manage/setup`** walks you through naming it, choosing identity, and pointing it at your
library.

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
whole stack from a single custom resource:

```bash
kubectl apply -k 'github.com/zaentrum/zaentrum-operator/config'
# or install the OLM bundle on OpenShift — see the operator repo
```

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
