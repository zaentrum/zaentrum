# Releases one can trust

This page specifies what an open product owes the people who run it, check it
and build on it: a way to report a security hole in private, images that can be
traced to their source, apps that call nobody but the server, a guide for
whoever wants to change it, and interfaces for addons that stay as they are.

The section As built describes what the platform does today. The sections after it are
the target, and the section Changes lists every difference between the two as a numbered
change. Only a change the owner has approved is built, one change at a time; anything no
change names stays as it is built.

## Purpose

zaentrum is open: anyone can run it, look into it, change it and add to it.
That is worth little if nobody can tell where an image comes from, or where to
turn with a hole they found. This page serves the goals
[Trust it](../goals/README.md#trust-it) and
[Make it one's own](../goals/README.md#make-it-ones-own), and four of their
qualities: a security hole can be reported in private, every image can be
traced to the source it was built from, what the apps send stays with whoever
runs the server, a stranger can change it and have the change taken in, and
what an addon builds on stays as it is.

Nothing here adds a screen. Three of the five changes are about the
repositories and how they build, so they come before the other changes are
built: they are what lets a change by anyone, a person or an agent, be checked.

## As built

As of 18 November 2026, from the main branch of the organisation's
repositories.

- **Reporting a hole.** One security policy, in the organisation's shared
  repository, shows in every repository. It says what a report can be about
  and what happens to one. Private reporting is switched on in all 28
  repositories.
- **Changing it.** One guide to contributing is in the organisation's shared
  repository, and every repository has its own `AGENTS.md`, which says, for a
  person or an agent, how it is built, tested and run and what its tests leave
  unchecked. Every repository runs a workflow on every pull request that
  builds it and runs its tests; the six that hold a service and had no test
  have one that builds them and starts them. Every repository calls the
  organisation's one neutrality check, with one set of rules: other media
  products, download tools and the vocabulary of acquiring content. It does
  not read for the names of any one installation. Three repositories also
  still run an older copy of their own beside it.
- **Where an image comes from.** The image workflows of fifteen repositories
  sign what they push, with the build system's own identity, and attach the
  build's record and a list of what the image holds; the operator's workflows
  no longer switch the record off. [Releases](../../docs/releases.md) says in
  one command each how to check a signature and read the record and the list.
  The four scaffolds of the later products build images that are not signed.
- **What the apps call.** The web, the Samsung TV app, the portal and the
  catalog console load their two typefaces from a public font service, in
  their page's head. The phone and Android TV apps fetch an avatar from an
  outside avatar service by a hash of the account's e-mail address
  (change 3.C13 of [chino, chapter 3](../chino/start.md) takes that out).
  Nothing else leaves the apps but to the server, and to what a person starts:
  a cast, a trailer that is only online
  ([what the apps send](../../docs/releases.md#what-the-apps-send)).
- **What an addon builds on.** The documentation's
  [extending](../../docs/extending/README.md) pages describe the interfaces: the
  buttons an addon adds to the apps, notices, a console hosted in the portal,
  handing files over, extras, what the library holds, the event bus, an
  addon's identity, installing by address or by chart, its configuration, and
  the command line's contract. None says which version it is, what may change,
  or how a change is announced. The platform is at version 0 and its resources
  at `v1alpha1`.

## Reporting a security hole

Every repository of the organisation has the same security policy, kept once,
in the organisation's repository for the files every repository shares, so
that one text holds everywhere. It says:

- **Where.** Through the repository's own private reporting, which is switched
  on in every repository: the report is seen by the maintainers alone until a
  fix is out. Never in a public issue.
- **What is in scope.** The platform's code, its images and its documentation.
  An installation somebody runs is that person's, and a report about one goes
  to them.
- **What happens.** An answer within 7 days that says whether it is taken as
  a hole. A fix goes out in a release, and the release's notes name it and
  thank whoever reported it, unless they ask not to be named.

## Changing it

The organisation has one guide to contributing, in the same shared place. It
says how a change is proposed: for anything a person sees, the specification
first, as a numbered change, then the code
([building from the specification](../../AGENTS.md)); a branch and a pull
request for each change; what a pull request has to pass; and what never
belongs in a public repository.

Each repository says for itself, in a file `AGENTS.md` at its root that a
person reads as well as an agent: what the repository is, the command that
builds it, the command that runs its tests, the command that runs it against
the reference demo or recorded answers, and what its tests leave unchecked.

Every repository's workflow runs its build and its tests on every pull request
and on the main branch. A repository without a test gets one that at least
builds it and starts it.

What never belongs in a public repository is checked, not only read for. One
check, kept in the organisation's shared repository, runs in every repository's
workflow on every pull request and on the main branch. It reads every tracked
text file, hidden ones included, for the names of other media products and of
download tools and, in code and configuration, for the vocabulary of acquiring
content. Its rules name nothing of any one installation: a rule that did would
publish what it guards, so whoever runs an installation keeps its names out of
what they publish by their own means. A repository names the paths the check
leaves out in its own workflow, each with its reason beside it. The check's log
names the file, the line and the rule, never the line's text. The check carries
its own test cases and fails when one of them no longer trips.

## Where an image comes from

Every image and every file a release publishes can be traced to the source it
was built from:

- **Signed.** Each image is signed by the workflow that builds it, with the
  build system's own identity for that repository and that workflow. There is
  no key to keep, and so none to lose.
- **With the record of its build.** The build's own record is attached to the
  image: which repository, which commit, which workflow built it.
- **With a list of what it holds.** The packages inside the image, attached
  the same way.
- **Checked.** The release check fails for a release that holds an image
  without these three. The documentation says, in one command for each, how
  anyone checks an image's signature, reads its record and its list. The
  updater of a one-machine install checks the signature before it starts a new
  version ([installing and updating](./install.md)).

## What the apps call

The typefaces are part of each app: their files are in the app's own bundle,
and no page asks a font service for them. With change 3.C13 built as well, an
app calls the server it was given, and nothing else unless the person starts
it.

## What an addon builds on

The documentation lists every interface an addon builds on, in one table: its
name, its version, and whether it is settled or may still change. Three rules
hold for an interface that is settled:

1. It changes in a way that breaks an addon only with a new version of that
   interface.
2. The version before stays served for at least one further release of the
   platform.
3. The release notes announce the change one release ahead.

An interface that may still change says so in the table, and an addon that
builds on it takes that risk knowingly. Which interfaces are settled today is
the owner's to say; the table starts with the event bus's schemas and the
library format, which are published contracts already.

## Changes

| No. | Change | Where | Today | Target | Status |
|---|---|---|---|---|---|
| T.C1 | A security policy in every repository | Docs | no repository has one, and nothing says where a report goes | the section Reporting a security hole: one policy in the organisation's shared repository, so every repository shows it; private reporting switched on in every repository; in scope the platform's code, images and documentation; an answer within 7 days; the fix named in the release's notes. Needs the owner: switching private reporting on is the organisation's setting | built |
| T.C2 | A guide to contributing, and each repository's own | Docs | a guide in the operator's repository alone; no repository says how it is built and tested | the section Changing it: one guide in the organisation's shared repository (the specification first, a branch and a pull request for each change, what it has to pass, what never belongs in a public repository); in every repository an `AGENTS.md` with what it is, how it is built, how its tests run, how it runs against the reference demo or recorded answers, and what its tests leave unchecked | built |
| T.C3 | Every repository's tests on every change | Images | all but one of the service and app repositories run a workflow on pull requests; the catalog console's builds its image on the main branch only; six repositories that hold a service have no test | the section Changing it: each repository's workflow builds it and runs its tests on every pull request and on the main branch; the catalog console gets the workflow the portal has; a repository without a test gets one that builds it and starts it | built |
| T.C4 | Images signed, with the record of their build and a list of what they hold | Images, Docs | no workflow signs an image or publishes what it holds; the operator's workflows switch the build's record off | the section Where an image comes from: every image and file a release publishes is signed by its workflow with the build system's own identity, carries the build's record and the list of its packages; the release check fails without them; [releases](../../docs/releases.md) says in one command each how to check a signature and read the record and the list | approved |
| T.C5 | The typefaces in the apps' own bundles | Web, Samsung TV, Portal, Catalog console | each loads its two typefaces from a public font service in its page's head | the section What the apps call: the font files are in each app's bundle and its page asks no other host for them; [what the apps send](../../docs/releases.md#what-the-apps-send) no longer names a font service | approved |
| T.C6 | The addon interfaces, each with a version | Docs | the pages under extending describe the interfaces; none has a version, and nothing says what may change | Recommended: the section What an addon builds on: one table in [extending](../../docs/extending/README.md) with each interface's name, version and whether it is settled; for a settled one the three rules (a breaking change takes a new version, the version before is served one further release, the notes announce it a release ahead); the other choice is to promise nothing until version 1 of the platform | approved |
| T.C7 | The neutrality check in every repository | Images | seven repositories check it in their own workflows, each with its own copy of the rules, two of them reading only some kinds of file; nineteen have no check, while [architecture](../../docs/architecture.md) says the boundary is enforced by CI | the section Changing it: one check in the organisation's shared repository, called by every repository's workflow on every pull request and on the main branch; every tracked text file, hidden ones included, read for other media products, download tools and the vocabulary of acquiring content, and for nothing of any one installation; a repository's exceptions named in its own workflow, each with its reason; a log that names file, line and rule, never the text; the check's own test cases run with it | approved |

## States

Nothing on this page has a screen.

## Words

| Where | Text |
|---|---|
| The security policy, its first line | Report a security hole in private: use “Report a vulnerability” on this repository's Security tab. Don't open a public issue. |
| The security policy, what follows | You get an answer within 7 days. |
