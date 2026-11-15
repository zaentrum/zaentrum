# The platform

The platform is what runs zaentrum: the operator that installs it and keeps it
running, in a cluster or on one machine, and what makes it reachable. This part
specifies what a household needs of it that is not there yet, and what an
open product owes the people who run and check it. It is for the goals
[Run it oneself](../goals/README.md#run-it-oneself) and
[Trust it](../goals/README.md#trust-it).

Each page has the form of the [chino chapters](../chino/README.md): first what
is built today, from the code and the [documentation](../../docs/README.md),
then the target, then every difference between the two as a numbered change.
Only a change the owner has approved is built, one change at a time; anything
no change names stays as it is built.

What the platform's resource takes today is in the documentation's
[operator reference](../../docs/operator.md); every setting, with who changes it
and where, is in [configuration](../capabilities/configuration.md). Running the
platform from the portal, with mail, alerts and backups, is specified with
[the portal](../portal/operations.md).

## Pages

| Page | What it covers |
|---|---|
| [Reaching it at home](./home.md) | a phone and a TV on the home network reach the platform and sign in with no name and no certificate of one's own; the apps find it by themselves |
| [Installing and updating](./install.md) | the processors and encoders it runs on, the smallest machine, the first administrator, and updating an install on one machine |
| [Releases one can trust](./trust.md) | a security policy, a guide to contributing, tests on every change, signed images with the record of their build, typefaces in the apps' own bundles, and addon interfaces with a version |
