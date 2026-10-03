# Zaentrum

**A neutral, self-hosted media platform for a library you own and are entitled to stream.**
Bring your own files — Zaentrum catalogs, processes, and streams them to clean clients on the
web, your phone/tablet, and your TV.

This repo is the **front door**: how to install, the release channels, and pointers to the
rest of the project.

**Product page → [zaentrum.github.io/zaentrum](https://zaentrum.github.io/zaentrum/)** ·
**Docs → [the wiki](https://github.com/zaentrum/zaentrum/wiki)**

> **Status: pre-release.** No release has been tagged yet: every image is published from `main`
> as `latest` (and `sha-<commit>`), and both release channels in
> [`releases.json`](./releases.json) point at `latest`. The commands below are the ones that
> work today.

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
other name, no other port. Keep the container — replacing it starts an empty platform — and
know that the bundled Postgres keeps its data only as long as its pod
([persistence](docs/self-hosting.md#persistence)).

There is **no setup wizard**. The first run is three steps
([self-hosting → first run](docs/self-hosting.md#first-run)): sign in as `admin` with the first
admin password, which the platform generates at install; add a TMDB key under **Catalog
Management → settings** (the images carry none); then copy your files into the library and
trigger a scan.

## Reaching it from your phone / TV

Sign-in needs **https** everywhere except on the machine itself. Keycloak marks its login
cookies `Secure`, and a browser keeps those over plain http for `localhost` names only — over
`http://<lan-ip>` or `http://<name>.local`, Keycloak answers the login form with "Cookie not
found" and nobody signs in. The Android phone and TV apps go further: they refuse plain http
altogether, and trust public certificate authorities only.

So the appliance, which serves plain http at `zaentrum.localhost`, is for the machine it runs
on. To reach Zaentrum from other devices, run it under a real hostname with TLS: the operator on
a cluster whose ingress terminates https with a certificate the devices trust (`spec.hostname`
and `identity.issuerScheme: https` — see
[self-hosting](docs/self-hosting.md#b-self-host-with-the-operator)). Clients use **Add Server**
with that address. LAN deployment profiles — the server's IP, a wildcard DNS name, mDNS — are
designed ([ADR-0008](docs/adr/0008-single-origin-deployment-profiles.md)) but not built, and as
designed they serve plain http, which cannot sign in.

## Identity

Out of the box Zaentrum runs its **own bundled Keycloak** (realm `zaentrum`); you manage users
in Keycloak's admin console for that realm, at `/auth/admin/zaentrum/console/`. On a cluster you
can instead **use your own OIDC provider directly**: `identity.mode: external` on the `Zaentrum`
CR, with your provider's issuer and client, and no Keycloak is rendered. Those are the two modes
the CRD accepts. **Federating** your provider through the bundled Keycloak (`broker`,
[ADR-0007](docs/adr/0007-identity-modes.md)) is designed, not built.

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

There are two release channels, `stable` and `edge` ([`releases.json`](./releases.json); by
default the operator reads its own copy, in the operator repository). **Today both point at
`latest`**: no tagged release has been cut, so choosing a channel, or `spec.update.mode: auto`,
changes nothing yet. An install on `spec.version: latest` — the default — follows every newly
published image anyway: the operator resolves each `ghcr.io/zaentrum/*` image to its current
digest on every reconcile, and rolls the components whose image changed.

## Repository layout

| Repo | What it is |
|---|---|
| **`zaentrum/zaentrum`** *(this)* | install, releases, instructions, the product page and the end-to-end tests — the front door |
| [`zaentrum/zaentrum-operator`](https://github.com/zaentrum/zaentrum-operator) | the Kubernetes operator — controller + CRD + deploy templates + OLM bundle, and the appliance image |
| `zaentrum/<service>` | per-service repos (catalog, playback, web/mobile/TV clients, …) |

## License

[MPL-2.0](./LICENSE).
