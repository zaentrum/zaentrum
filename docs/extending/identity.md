# Addon identity — how an addon authenticates

An addon talks to platform APIs (registering slot rows, calling ingest) as a
**service account**: an OIDC confidential client on the instance's realm,
using the client-credentials grant. Users never authenticate *to* an addon —
the portal proxy forwards the signed-in user's bearer to the addon's own API,
and the addon validates it against the same issuer as every other service.

## The design

- The addon has a confidential client (service account enabled) on the
  instance's identity provider.
- The realm role **`zaentrum-addon`** marks addon service accounts. portal-api
  reads the role name from `PORTAL_ADDON_ROLE` (default `zaentrum-addon`) and
  accepts it, alongside the admin role, on the
  [`/api/portal/extensions` write API](./slots.md#the-api).
- The addon mints a token with `grant_type=client_credentials` and uses it for
  self-registration and for platform calls such as
  [`POST /api/ingest`](./ingest.md).

## Honest status on a stock install

**The bundled realm does not yet define the `zaentrum-addon` role, and the
operator does not create addon clients.** This section is design plus a manual
procedure, not a shipped flow. Until the platform provisions addon identity,
an operator installing an addon must, by hand:

1. Create a confidential client for the addon in the realm
   (service accounts enabled).
2. Create the realm role `zaentrum-addon` and assign it to that client's
   service account.
3. Provide the client id + secret to the addon (a Secret its Deployment
   mounts).

With that in place, addon self-registration of **slot rows** works. Registering
the addon's **app and tile** (its console entry in the launchpad) is admin-only
today — an admin adds them in the portal's settings console. Making the addon
role sufficient for an addon to register *itself* — app, tile, and rows, keyed
to an `addon` owner for one-step uninstall — is roadmap, tracked alongside
[declarative install](./installing.md).

## Validating users inside your addon

Your addon's API receives the user's bearer via the portal proxy. Validate it
as an OIDC resource server against the instance's issuer (discovery), and key
authorization on `(iss, sub)` — never on email. The issuer is whatever the CR's
identity mode yields; your addon should take it from configuration, not assume
a mode.
