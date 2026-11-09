# Releases

A release of Zaentrum is one version, `vX.Y.Z`, tagged in every repository of
the platform at once. Each repository builds what it publishes from that tag —
its images, and for some a GitHub release — and when every build has passed,
the `stable` channel moves to the release. Between releases, `main` keeps
publishing `latest`, which the `edge` channel serves.

This page is what a release publishes, how the channels decide what an install
runs, how a release is cut, and how to try one before production runs it.

## The channels

The operator reads one channel document,
[`releases.json`](https://github.com/zaentrum/zaentrum/blob/main/releases.json) in
this repository (`https://raw.githubusercontent.com/zaentrum/zaentrum/main/releases.json`;
the operator's `RELEASES_URL` environment variable points it elsewhere, for a
mirror). It names a tag per channel:

| Channel | Serves | Moves when |
|---|---|---|
| **`stable`** (the default) | the newest release, `vX.Y.Z` | a release is finished (`releases.json` changes) |
| **`edge`** | `latest`, the newest build of `main` | every push to `main` of any repository |

What an install runs follows from three fields of its `Zaentrum`:

| `spec.version` | `spec.channel` | `spec.update.mode` | It runs | When the channel moves |
|---|---|---|---|---|
| `vX.Y.Z` | — | — | that release | nothing: a pinned version never looks at a channel, and makes no outbound call for it |
| `latest` (the default) | `stable` | `manual` (the default) | a new install: the release `stable` names; after that, the version it runs | `status.availableUpdate` names the new release; applying it (the portal's operator console, `zae platform update --apply`) pins `spec.version` to it |
| `latest` | `stable` | `auto` | the release `stable` names | it moves to the new release on its own |
| `latest` | `edge` | either | `latest` | every push to `main` rolls the components whose image changed |

The tag an install renders is applied to every `ghcr.io/zaentrum/*` image, and
the operator resolves each one to the digest that tag points at, on every
reconcile. A release's tag never moves, so a push to `main` moves nothing in an
install on a release; it moves exactly the installs that render `latest`.

Two more cases:

- **The channel document cannot be read** — no network, or GitHub is down: an
  install keeps running what it runs. A new install renders `latest` until it
  can read the document.
- **An install that ran `latest` before `stable` named a release** (every
  install did, before the first release) stays on `latest` in manual mode and
  reports the release in `status.availableUpdate`. Apply it to move to the
  release, or set `spec.channel: edge` to keep following `main` and stop being
  told.

Moving between channels is a CR change: `spec.channel`, or `zae platform update
--channel`. In manual mode an install keeps what it runs until you apply what
the channel offers; `edge` is followed in both modes, as there is no release on
it to hold an install at.

### The operator and the release go together

The platform is rendered from the chart the operator embeds, so an install on
`stable` should run that release's operator: install it from the release's
manifest, or run the release's appliance (below). The install manifest on the
operator repository's `main`, pinned to an `operator:sha-<commit>`, goes with
`edge`. The operator's own version is reported in `status.controller`, and
updated by whatever installed it — see
[updating the operator](./updating-the-operator.md).

## What a release publishes

| From | At the tag `vX.Y.Z` |
|---|---|
| every service repository (`chino-*`, `katalog-*`, `zaentrum-portal`, the pipeline's `analyzer`, `transcoder`, `packager`, `sample-addon`) | its images, `ghcr.io/zaentrum/<image>:vX.Y.Z` and `:X.Y` |
| [`zaentrum-operator`](https://github.com/zaentrum/zaentrum-operator) | `operator`, `admin` and `keycloak` images; the GitHub release with `operator-install.yaml` (the CRDs, the cluster RBAC and the controller on `operator:vX.Y.Z`); the appliance `appliance:vX.Y.Z`, which bakes `operator:vX.Y.Z` and a `Zaentrum` pinned to `vX.Y.Z`; the OLM `operator-bundle:vX.Y.Z` (`zaentrum-operator.vX.Y.Z`) and `operator-catalog:vX.Y.Z`, which serves it on its `stable` channel |
| [`zae`](https://github.com/zaentrum/zae) | the CLI for Linux, macOS and Windows on amd64 and arm64, with `checksums.txt`, on its GitHub release; the image `zae:vX.Y.Z`, which the platform's own check runs |
| this repository | the tag, on the commit that moves `stable` to the release |

`:X.Y` is the newest patch of a minor version: `0.4` is `v0.4.2` once `v0.4.2`
is out. A pre-release (`vX.Y.Z-rc.1`) publishes its full tag only, and never
moves `stable`. No release publishes `latest`: that tag is `main`'s alone.

Installing a release:

```sh
# the appliance, the whole platform in one container, on the release
docker run -d --privileged --restart unless-stopped -p 80:80 --name zaentrum \
  ghcr.io/zaentrum/appliance:vX.Y.Z

# a cluster: the release's operator, then a Zaentrum on stable (the default)
kubectl apply -f https://github.com/zaentrum/zaentrum-operator/releases/download/vX.Y.Z/operator-install.yaml
#   (…/releases/latest/download/operator-install.yaml is always the newest release)

# OLM: a CatalogSource on ghcr.io/zaentrum/operator-catalog:vX.Y.Z, channel stable

# the CLI
curl -fsSL https://raw.githubusercontent.com/zaentrum/zae/main/install.sh | sh
```

## Cutting a release

[`scripts/release.py`](https://github.com/zaentrum/zaentrum/blob/main/scripts/release.py) does every step from a directory
holding a `git clone` of each repository side by side (`--root`; by default the
directory that holds this repository). Each step checks before it acts, prints
exactly what it will push, and pushes nothing without `--push`; `--dry-run`
changes nothing at all.

**1. Pick the version.** It must be newer than every tag in every repository —
the same tag goes everywhere. `check` names the smallest version that is, when
the one asked for is taken somewhere.

**2. Check.** Every repository on `main`, clean, in step with `origin/main`,
its CI green at that commit, and its release workflows on `main`:

```sh
scripts/release.py check vX.Y.Z
```

**3. Tag.** Annotated tags on each repository's `main` — the services, `zae`,
`sample-addon` and the operator; this repository is tagged last, by `finish`:

```sh
scripts/release.py tag vX.Y.Z           # makes the tags, prints the pushes
scripts/release.py tag vX.Y.Z --push    # …and pushes them: the release builds start
```

On the tag, each repository's workflows build the release:

| Repository | Runs on the tag |
|---|---|
| each service, `sample-addon` | `image` (`zaentrum-portal`: `image` and `image-api`) |
| `zae` | `image`, and `release` (GoReleaser: the binaries, `checksums.txt` and the GitHub release) |
| `zaentrum-operator` | `build-images`; `operator-bundle` (stamps the release into the CSV, then the bundle and the catalog); `all-in-one` (the appliance, then boots it once every image of the release is published, and waits for the platform to pass its own verification); `release` (once `operator:vX.Y.Z` exists, the GitHub release with `operator-install.yaml`) |

A commit whose message says `[skip ci]` builds nothing on its tag either:
GitHub applies the skip to the tag's push. `tag --push` starts such a
repository's release workflows on the tag by hand (`gh workflow run`), and
`finish` counts those runs like the others.

**4. Finish.** Wait for every one of those builds, check that every image and
release asset is published, then move `stable`: commit `releases.json` here
with `stable` on the release, tag that commit, and draft the release notes —
per repository, from its commits since its previous release (the pre-releases
on the way are left out; a summary for its first), and one for the platform:

```sh
scripts/release.py finish vX.Y.Z                    # waits, checks, commits, tags, drafts
scripts/release.py finish vX.Y.Z --push             # …and pushes main and the tag: stable moves
scripts/release.py finish vX.Y.Z --publish-notes    # …and drafts the GitHub releases with the notes
```

From the push on, every install on `stable` sees the release: a new one starts
on it, a manual one reports it, an auto one moves to it.

**When a build fails**, nothing has moved: `stable` stays where it was, and
`finish` stops before it changes anything. Re-run the failed run once the cause
is fixed, if it was outside the code (`gh run rerun <id> --failed`), and run
`finish` again. A fix in the code is a new patch release. Never move a pushed
tag: an image built from it may already be pulled somewhere.

## Trying a release before production

A pre-release, `vX.Y.Z-rc.N`, is cut like a release — `check`, `tag --push`,
`finish` — and is one in everything but `stable`: every repository is tagged,
every image is built at the tag, and no install that follows a channel moves.
To try a release on an install of its own before production runs it:

1. **Pin a trial install to the pre-release**: `spec.version: vX.Y.Z-rc.N`. A
   pinned version never reads a channel, so nothing else reaches that install
   until its pin changes. Give it data like production's, and the same identity
   and addons.
2. **Try it**: its own verification (`status.verification`, `zae platform
   status`), signing in and playing on each kind of device you use, and what
   the release changes. A fix lands on `main` and goes out as the next
   pre-release, `-rc.N+1`, tried the same way.
3. **Release what you tried.** `main` has usually moved on by then. Tag the
   release where the pre-release is, so it holds exactly the commits you tried:

   ```sh
   scripts/release.py check  vX.Y.Z --from vX.Y.Z-rc.N
   scripts/release.py tag    vX.Y.Z --from vX.Y.Z-rc.N --push
   scripts/release.py finish vX.Y.Z --push
   ```

   The release's images are built again from its tags, so their digests are
   new; their code is the pre-release's.
4. **Pin production to the release**: `spec.version: vX.Y.Z`. It rolls once,
   to the code you tried. Moving the trial install to the release as well keeps
   the two alike until the next pre-release.

**One operator renders every install in a cluster.** The chart is the
operator's own: it renders each install, at that install's version, from the
chart it embeds. Installing a new operator therefore changes every install in
the cluster at once, whatever each one pins — install the release's operator
together with the release, and check every install right after. Trying a new
operator first takes a cluster of its own, or the pre-release's appliance
(`ghcr.io/zaentrum/appliance:vX.Y.Z-rc.N`).

## The apps

The TV, phone and tablet apps (`chino-androidtv`, `chino-mobile`,
`chino-tizen`) ship through their stores, on their own versions, and are not
part of a platform release yet.

### App identity

A published build carries the project's identity, not an installation's: the
reverse-DNS name of the project's GitHub Pages site. The phone and tablet app
(Android, iOS) and the Android TV app are `io.github.zaentrum.chino`; debug
builds add `.debug`, so they install beside a release. The Samsung TV app is
package `zaentrumio`, application `zaentrumio.Chino` (`config.xml`).

A store never lets a published id change, so a fork publishes under its own:
`-PchinoAppId` (Android), `CHINO_BUNDLE_ID` in `iosApp/Configuration/` (iOS),
the ids in `config.xml` (Samsung). Two identifiers don't follow the app id: the
code's Kotlin namespace, and the phone app's OAuth redirect URI, which identity
providers register exactly as written ([chino-mobile, redirect URI](https://github.com/zaentrum/chino-mobile#redirect-uri)).
A new redirect URI breaks sign-in wherever it isn't registered yet: it goes
into the operator's realm, and is announced for external providers, one release
before a build uses it.

### Publishing the apps

- **Google Play.** The two Android apps share one app id, so they are one Play
  entry: sign both bundles with the same upload key. Play gives each device the
  bundle whose manifest fits it (the TV app requires leanback). Their version
  codes never meet: the phone app's is set at release, above Play's last; the
  TV app's is the build's run number plus 2,000,000. A new personal Play
  developer account runs a closed test with at least 12 testers for 14 days
  before it may publish to production.
- **App Store.** iOS is built and signed on a Mac with Xcode. The app keeps its
  settings in user defaults, so the bundle needs a privacy manifest that
  declares that, and an export-compliance answer.
- **Samsung.** The `.wgt` is signed with Samsung author and distributor
  certificates. A TV in developer mode installs it only when its DUID is in
  that distributor certificate. The TV emulator runs x86 images and needs an
  x86-64 machine with hardware virtualisation. Publishing goes through
  Samsung's seller portal.
- **Every store.** Check playback on a real device, not only an emulator. Fill
  in the content rating, and give the listing a privacy policy and a page that
  says how to delete an account (the app's **Delete Account**, or the people
  who run the server). Screenshots show only openly licensed titles, such as
  the reference demo's, and the listing names no other media product and no
  server.

### What the apps send

What a store's data-safety form asks, as the apps are built today:

- The apps talk only to the server the person adds and to the outside services
  below; nothing goes to whoever published them. There is no analytics or
  crash-reporting SDK.
- Sign-in runs at that server's identity provider. The tokens stay on the
  device: encrypted on Android TV; in the phone app's own storage, with
  encryption on its roadmap.
- The server keeps progress, watched marks, likes, lists and history.
- App events go to the server's event log, which records each with the
  account. The phone and Android TV apps add the device's model, maker, system
  version, the app's version and the account's id to theirs; their playback
  quality reports and the web's events carry no device details.
- Bug reports go only where the server takes them ([bug reports from the
  apps](./self-hosting.md#bug-reports-from-the-apps-optional)). They hold the
  person's words, the same app and device details, the account's username,
  which the server adds, and on the web and the phone a screenshot the person
  can leave out. The Android phone app's own report of a playback failure
  includes a screenshot of the app. Reports go to the tracker the server's
  operators chose, and stay there when the account is deleted.
- Offline titles on Android stay in the app's own storage; nothing of the
  Android apps goes into a device backup.
- The phone and Android TV apps fetch an avatar from an outside avatar service
  by a hash of the account's email (change 3.C13 of the
  [specification](../spec/chino/start.md) proposes dropping it). The web and
  Samsung TV apps load their typefaces from a public font service. The Android
  phone app casts with Google Cast. A trailer that is only online opens outside
  the app.
- **Delete Account**, in every app, deletes the account and what the server
  keeps of it.

See also: [updating](./updating.md) · [updating the operator](./updating-the-operator.md) ·
[the operator & CR reference](./operator.md)
