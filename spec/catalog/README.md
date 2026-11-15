# The catalog

The catalog is what zaentrum knows of a household's library: its films and
shows, where their files are, and what was made of them to play. This part
specifies how the library is kept and the console an admin looks after it in.
It is for the goal [Keep the library](../goals/README.md#keep-the-library).

Each page has the form of the [chino chapters](../chino/README.md): first what
is built today, from the code, then the target, then every difference between
the two as a numbered change. Only a change the owner has approved is built,
one change at a time; anything no change names stays as it is built. These
pages draw no figures yet: a screen is described by the design system's page
layouts and components, and by its exact words.

The catalog console's screens follow the
[nalet design system](https://nalet.github.io/design-system/), and this part
doesn't repeat its rules. How a title is made ready to play, and what a package
keeps of its original, is decided in
[ADR-0015](../../docs/adr/0015-the-package-is-the-master.md) and described in
the [library format](../../docs/library/README.md).

## Pages

| Page | What it covers |
|---|---|
| [The library](./library.md) | libraries and their folders, scans that run by themselves, details and artwork kept beside the files, collections, and getting a title back as one file |
| [The catalog console](./console.md) | the console's screens: titles and a title's page, collections, libraries, scans, settings |
