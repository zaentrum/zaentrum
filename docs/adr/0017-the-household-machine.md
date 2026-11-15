# ADR-0017: zaentrum fits the machine a household has, and one machine is updated from outside its container

**Status:** Proposed · 2026-11-15, for the owner's review. Design ahead of the code: nothing of it is built.

## Context

zaentrum is installed in a cluster through its operator, or on one machine as one container that holds a cluster of its own, the one-machine install. A household's machine is often not what the platform needs today. The facts, as the code at each repository's main branch has them on 15 November 2026:

- **One processor.** Every image the platform runs is built for amd64 alone. Small home servers and many boards have ARM processors. What the images are built on, the media programs included, exists for arm64.
- **One maker's graphics.** A title is encoded on an NVIDIA GPU or on the CPU, before it plays and while it does. Many of the small machines a household runs a server on have the graphics chip of Intel or AMD, and no NVIDIA GPU. The one-machine install hands no graphics device to its workers at all, an NVIDIA GPU included.
- **No smallest machine.** With the one-machine install's own settings, the chart's workloads ask for 2.27 cores and 5.1 GiB of memory, and may take up to 19.9 cores and 24.4 GiB. The image's README says the machine wants four cores and 8 GiB. This repository's documentation names no machine, and no check holds the platform to one.
- **A password read from the cluster.** The first administrator is an account `admin` with a one-time password the operator generates. Whoever installs reads it out of the cluster with a second command. The first page a browser opens is a sign-in page that says nothing of either.
- **An update by hand, with no way back.** The one-machine install is updated by replacing its container. A release's install never hears of a newer release, because its version is pinned. The platform checks itself after an update, and nothing undoes an update whose check failed.
- **Settings that do nothing.** `databases.mode: single`, `identity.loginTheme` and `features.gpu` are read by no template. The reference of the resource has no section for `spec.pipeline`.

Older records set the frame.

- [ADR-0006](./0006-operator-owned-runtime.md) made the operator the owner of what runs, and called a release of the one-machine image a lockfile whose way back is the pin before. This record says how that way back is walked on one machine, and adds a second actor there, on the machine itself.
- [ADR-0008](./0008-single-origin-deployment-profiles.md) names a first-run wizard that was never built. This record gives the first run its first page. Where the machine is reached is ADR-0016's.
- [ADR-0013](./0013-live-rungs-safety-net.md) has a pool of GPU workers make the live rungs, and no encoder in the stream origin. This record adds a second kind of graphics chip to that pool.
- [ADR-0015](./0015-the-package-is-the-master.md) says what a master is. An encoder on another chip has to make the same master.

Two things do not move. Every install is a Kubernetes cluster, so the one-machine install stays k3s in a privileged container. And in Kubernetes a pod reaches a device only when its node hands it over.

The chapter that sets all of this out is [Installing and updating](../../spec/platform/install.md).

## Decision

1. **One tag, two processors.** Every image the platform publishes is one tag for amd64 and arm64. A Go program is compiled for the target's processor on the build's own. A web app is built once. A worker with media programs is built on a runner of each processor, with the media programs of that processor from the same pinned releases. A release is finished only when every image holds both. On arm64 the workers encode on the CPU.

2. **One encoder setting, four values, and two who look.** `spec.pipeline.encoder` takes `auto`, `nvenc`, `vaapi` and `cpu`; `gpu`, its name today, is read as `nvenc`. The default becomes `auto`.
   - **The operator looks first.** A worker cannot look for a device its pod was not given, and a pod that asks for a device no node offers never starts. So the operator reads what the nodes offer and gives the transcoder and the live worker the first device there is: an NVIDIA GPU, else a render device, else none.
   - **The worker looks again.** It takes the first encoder that opens: NVENC, then VA-API, then the CPU's. It says which, and why not another.
   - **VA-API makes the same master.** In the transcoder it is the CPU's path with the encoder as its last step, at a constant quality under the title's cap. Where a chip's driver cannot do that for a codec, the CPU encodes that codec.
   - **The stream origin gets nothing new.** Its own encoder goes as ADR-0013 lands.
   - **On one machine the devices come through.** The one-machine install hands an NVIDIA GPU and the machine's render devices to its workers through device plugins, each device offered 4 times so that the workers share it.

3. **A smallest machine, named and checked.** 4 cores, 8 GB of memory, 40 GB of free disk beside the library, amd64 or arm64. On it the platform runs idle and plays one packaged title, and every release is checked for exactly that, on both processors, with the container held to that memory. Nothing is cut to make it fit: if the check does not pass, the machine named becomes larger.

4. **The first administrator is made on the first page, with a code.** The operator generates a setup code. The install command prints it. The first page a browser opens asks for the code, a name and a password, makes the administrator, signs the person in and opens the setup checklist. The page works once. A new realm holds no account for a person before that. The code is what keeps a stranger on the network from claiming the install.

5. **One machine is updated from outside its container.** A command installs the one-machine install: it checks the machine, starts the container, and leaves an updater on the machine, a service of the machine's own with a timer.
   - **The portal asks, the updater acts.** The portal's operator console asks for a release, or an admin turns updates by themselves on. The updater fetches the release's image, checks its signature where releases are signed, copies the records an update may rewrite, starts the new image and waits for the platform to be ready and to pass its own check.
   - **A failed check goes back.** The updater puts the records back, starts the image before, and the portal says what failed.
   - **The platform asks for one thing.** The updater takes a release's version from the platform and nothing else: no image name, no command.
   - **The image keeps the install's own settings.** At a start it brings its operator and sets the version, and leaves every other field of the platform's resource as an admin left it.
   - **A cluster keeps its way.** Its operator is updated outside the platform, by the cluster's operator lifecycle manager or by a cluster admin who applies the release's manifest. One rule is added there: an operator that is a release does not move the platform to a release newer than itself.

6. **Settings that do nothing go.** `single` goes from the database modes and `identity.loginTheme` from the resource. The setup checklist reads the encoder the platform reports. The documentation names every field of `spec.pipeline`, and stops naming `features.gpu` for NVENC.

## Consequences

- A household with an ARM machine can run the platform. One whose machine has an Intel or AMD chip no longer waits hours for the CPU to encode a title.
- The documentation can say what machine is enough, and a release that outgrows it is caught before it is published.
- Nobody reads a password out of a cluster to sign in for the first time, and the first administrator is a person like any other on the People page.
- An update on one machine either passes the platform's own check or is undone. A household does not wake up to a broken platform.
- A resource that names no encoder no longer leaves its transcoder waiting for a GPU that is not there.

What it costs:

- Every image is built twice, and five of them on two kinds of runner. Every release is checked on two processors.
- A program on the machine, with the rights of root, that the project has to keep safe. It reads one value from the platform, and that value is checked.
- The one-machine image grows: NVIDIA's runtime, two device plugins, the list of its images, the CLI.
- Two more encoders to keep the master's rules with, on drivers the project does not control.
- The one-machine install stays a privileged container. This record does not change that.
- The first administrator no longer holds the identity provider's own admin role. Its console is reached with the identity provider's own first account, as the documentation says today.

What it rules out:

- **The container runtime's socket inside the platform**, and a container that watches the others and replaces them, which needs the same socket. A service that holds the socket can start any container with any right. It would hand the machine to that service and to whoever breaks into it.
- **The operator replacing its own image.** What does the replacing would be what is replaced. In a cluster the reasons of [updating the operator](../updating-the-operator.md#why-the-product-will-not-do-it-for-you) stand.
- **A Mac's graphics chip.** On a Mac a container runs in a Linux virtual machine, and the container runtime hands that machine no encoder of the Mac's.
- **A worker's pod with all of its node's rights**, to reach a device without a device plugin. The transcoder reads files nobody has vetted.
- **A promise of a smaller footprint.** No profile without the bundled services, no lower limits, until someone has measured what the platform takes.
- **A known first password, or no code at all.** The first would be the same on every install; the second gives the install to whoever opens it first.
- **Signing the first administrator in from the server.** Every client of the realm has the password grant switched off, and portal-api may manage people and nothing else. Both stay so. The page completes the sign-in in the browser, as a person would.
- **An `auto` that changes its device while an encode runs.** The operator waits 10 minutes before it believes a device has gone or come.
- **32-bit ARM.** The bundled identity provider and the event broker are not published for it.
- **The encoders of ARM boards**, in this record. They are reached through other interfaces than NVENC and VA-API.

## To prove first

Four parts of the decision are not certain. Each needs a short trial before the changes that depend on it are built.

- **VA-API makes a master** (changes I.C5 and I.C6). On a machine with a current Intel chip and on one with an AMD chip: the worker's image opens the device; `hevc_vaapi` and `h264_vaapi` encode, in 10 bits too; the driver offers a constant quality under a maximum rate; the result passes the transcoder's own checks and looks like the CPU's at the same cap; a live rung's segment is made in less time than it plays. The trial sets the quality number. If a driver offers no such rate control, VA-API is used for the live rungs alone, which have a fixed bit rate, and masters stay with NVENC and the CPU. If the images' base holds no driver new enough for current chips, the base moves first.
- **A graphics device reaches a worker of the one-machine install** (change I.C7). With an NVIDIA GPU, and with a render device: a pod inside the container's own cluster is given the device by a device plugin and encodes on it, and two pods share it. k3s's documentation, and the guide of k3d, the tool that runs k3s in containers, describe the way for NVIDIA; nobody has walked it with this image. If the image has to change its base for NVIDIA's runtime and that costs machines without a GPU anything, NVIDIA stays a cluster's, and the one-machine install hands on render devices alone.
- **The smallest machine is enough** (change I.C11). The release check passes on both processors with the container held to 4 CPUs and 7 GiB. Nobody has measured what the platform takes when idle. If it does not pass, the machine named becomes larger, 16 GB of memory being the next common size, and the documentation says so; the platform is not cut.
- **Going back works across a Kubernetes version** (change I.C16). An update from one image to another with a newer k3s is made to fail its check on purpose, and the updater goes back: the platform is ready on the old version, with its accounts, its catalog and its library as before. The trial shows which records have to be copied. If no such list makes it reliable, a release that moves to a newer Kubernetes is marked in the channel document, is never taken by itself, and its dialog says that it cannot be undone.

One smaller point is tried with its change, not before it. The first-run page completes the sign-in in the browser (change I.C14); where that fails, the page opens the ordinary sign-in page with the username filled in, and the change is still done.
