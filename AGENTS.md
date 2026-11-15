# Building zaentrum from its specification

For whoever builds a change, a person or an agent. This repository holds the
specification ([spec/](./spec/README.md)) and the documentation
([docs/](./docs/README.md)); the code is in the other repositories of the
organisation, one for each component
([components](./spec/architecture/components.md)).

## What may be built

- **Only a change the owner has approved.** Every difference between what is
  built and the target is a numbered change in a chapter's Changes table
  (`11.C30`, `H.C8`, `P.C4`). Its status says where it stands: proposed,
  approved, built, verified, withdrawn. Build a change only when its status
  is `approved`.
- **One change at a time**, as its row says. Anything no change names stays
  as it is built. Do not improve what you pass on the way.
- **In the order of the packages.** [Work packages](./spec/capabilities/packages.md)
  says which package comes after which. Take a package whose earlier
  packages are built; inside it, the changes in the order of their numbers,
  the server's part of a change before the apps'.
- **What is left out is left out.** [Scope](./spec/capabilities/scope.md) lists
  what is for later, an addon's, or ruled out. Do not build it on the side.

## What a change asks for

Read, in this order: the change's row (Today and Target), the section and the
figures its Target names, the chapter's States and its Words, and the
decision record the chapter names, if any. Then:

- Build what the Target says, in every app and component the row names.
- Use the words of the Words section exactly: every label and every sentence.
- Follow the [design system](https://nalet.github.io/design-system/) for
  everything the chapter does not say.
- If the Target is unclear, contradicts another chapter, or cannot be built as
  written, stop and say so. Do not decide it yourself: the specification is
  changed first, then the code.

## When a change is done

1. Every app and component its row names does what the Target says, in each
   state the chapter lists.
2. Each repository you changed has a test that failed before and passes now,
   with the change's number in its name (`11.C30`), and all of its tests pass.
3. For a screen: a picture of each state at each size the chapter draws, to
   compare with its figures.
4. This repository says what is true now: the capability's row in
   [capabilities.csv](./spec/capabilities/capabilities.csv) (where it is built),
   the inventory (`python3 scripts/inventory.py --src <a folder of clones> --fetch`),
   and the change's status,
   `built`. `python3 scripts/capabilities.py --check`,
   `python3 scripts/check-spec.py` and `python3 scripts/check-docs.py` pass.
5. The change is `verified` once the owner, or whoever reviews for the owner,
   has seen it in a released build. Do not set that status yourself.

## Never

- Write into a public repository, a commit message, a test or a page: a
  hostname, an address, a path or a name of a real installation; the name of
  a private person; an e-mail address; a password, a token or a key; the name
  of another media product; real commercial film or show titles (the
  reference demo's open-licensed titles are fine).
- Write a sentence for a screen that is not true on every installation.
- Change a generated table by hand: the text between `<!-- generated: … -->`
  and `<!-- end: … -->` is written by `scripts/capabilities.py`.
- Push to a main branch. A change is a branch and a pull request named by its
  number; it is merged when its checks pass and it has been reviewed.
- Change a running installation.

## This repository

This repository holds the specification (`spec/`), the documentation
(`docs/`), the scripts that check them and write their generated tables
(`scripts/`), the release script, and end-to-end tests that use a running
instance (`e2e/`). The [site](https://github.com/zaentrum/zaentrum.github.io)
builds the docs and the specification into its pages.

### Build

Nothing is compiled. What is generated is written by a script and committed:

```sh
python3 scripts/capabilities.py      # the tables between <!-- generated: … --> and <!-- end: … -->
python3 scripts/inventory.py --src <a folder of clones> --fetch   # spec/capabilities/inventory.csv
npx -p playwright@1.63.0 node scripts/render-mockups.mjs chino    # a section's drawings, as PNGs
```

`inventory.py` reads every repository's main and renders the operator's chart
with `helm template`, so it needs `helm` on the PATH and the network.
`render-mockups.mjs` needs Playwright's Chromium and the network.

### Test

What `docs-check.yml` runs on every pull request and on main:

```sh
python3 scripts/check-docs.py              # every relative link and every anchor resolves
python3 scripts/check-spec.py              # the chapters' numbers, captions and legends
python3 scripts/capabilities.py --check    # the model, and its tables as written
```

It also builds the site from the pull request's `docs/` and `spec/`, which
fails on a link or a heading that leads nowhere.

### Run it

The end-to-end tests sign in to an instance as a person does and change
nothing on it. They run against the reference demo
([how it is deployed](./docs/reference-demo.md)) or any instance with the same
open-licensed titles, with one ordinary account and one administrator.
[e2e/README.md](./e2e/README.md) names the variables:

```sh
cd e2e && npm ci && npx playwright install chromium
E2E_ENV_FILE=/path/to/e2e.env npm test
```

`e2e.yml` runs them on request, from the Actions tab, with the repository's
variables and secrets.

### What the checks leave unchecked

- Whether the text is true of the code. The checks hold the structure and the
  model together; the model meets the code only through the inventory, which
  is refreshed by hand.
- The end-to-end tests run only on request, against a live instance.
- The drawings are not compared with the screens that are built.
- `release.py` talks to GitHub and the registry only when a release is cut.
