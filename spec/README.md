# The specification

The specification says how zaentrum's screens look and behave: what each one
shows, what it says in every state, how it fits a computer, a phone and a TV,
and how today's apps differ from it. It is written for the people who build the
apps, and for the review of every release.

> **What is deployed, and what is the target.** Each chino chapter shows first
> what the apps do today, in screenshots of the deployed web; then the target;
> then every difference between the two as a numbered change with its status.
> Only a change the owner approved is built, one at a time, and anything no
> change names stays as it is deployed. The portal's home page has the same
> form; its settings page shows the target only, and nothing in it is built
> until a change to it is approved.

The [capabilities](./capabilities/README.md) are its first layer: every
capability of the platform, checked against the code, with the chapter that
describes it, or none yet.

The [documentation](../docs/README.md) is the other half: it is for the people
who run zaentrum, extend it with addons, or build on its library format, and it
holds the decision records behind the platform.

| Part | What it specifies |
|---|---|
| [capabilities](./capabilities/README.md) | what the platform does, for whom, where each app and console has it, what serves it, and its settings |
| [chino](./chino/README.md) | the apps for watching: on the web, on a phone or a tablet, on Android TV and on Samsung TVs |
| [portal](./portal/README.md) | the portal: its home page, and its settings and setup |

Both follow the [nalet design system](https://nalet.github.io/design-system/),
which holds the rules every product shares, and don't repeat them. A part
specifies one product: its screens, their states, their words, and its own
decisions.
