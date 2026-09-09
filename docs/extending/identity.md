# Addon identity — when an addon needs to authenticate

**Installing an addon needs no identity.** The platform pulls the addon's
manifest and creates its UI itself — see [installing](./installing.md). An
addon that only contributes UI, a console and CLI commands never holds a
credential.

Identity enters when the addon **calls** platform APIs on its own behalf:
[`POST /api/ingest`](./ingest.md), publishing on the [event bus](./events.md),
or changing its slot rows while running. For those it acts as a **service
account**: an OIDC confidential client on the instance's realm, using the
client-credentials grant.

Users never authenticate *to* an addon — the portal proxy forwards the
signed-in user's bearer to the addon's own API, and the addon validates it
against the same issuer as every other service.

## The design

- The addon has a confidential client (service accounts enabled) on the
  instance's identity provider.
- The realm role **`zaentrum-addon`** marks addon service accounts. portal-api
  reads the role name from `PORTAL_ADDON_ROLE` (default `zaentrum-addon`) and
  accepts it, alongside the admin role, on the
  [`/api/portal/extensions` write API](./slots.md#the-api).
- The addon mints a token with `grant_type=client_credentials` and uses it for
  platform calls.

## Honest status on a stock install

The bundled realm defines the `zaentrum-addon` role. **The operator does not
create addon clients.** An addon that needs a service account gets one by
hand today:

1. Create a confidential client for the addon in the realm
   (service accounts enabled).
2. Assign the realm role `zaentrum-addon` to that client's service account.
3. Provide the client id + secret to the addon (a Secret its Deployment
   mounts).

🧭 Platform-provisioned addon identity (a client per installed addon, issued
at install) is roadmap, alongside [declarative install](./installing.md).

## Validating users inside your addon

Your addon's API receives the user's bearer via the portal proxy. Validate it
as an OIDC resource server against the instance's issuer (discovery), and key
authorization on `(iss, sub)` — never on email. The issuer is whatever the CR's
identity mode yields; your addon should take it from configuration, not assume
a mode. The [sample addon](https://github.com/zaentrum/sample-addon) shows
the lazy, retrying verifier this needs: an addon must not refuse to boot
because the identity provider was slow to come up alongside it.
