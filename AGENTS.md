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
