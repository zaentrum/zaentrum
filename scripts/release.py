#!/usr/bin/env python3
"""Cut a release of the Zaentrum platform: one tag, vX.Y.Z, in every repository.

    scripts/release.py check  v0.4.0           is every repository ready to be tagged?
    scripts/release.py tag    v0.4.0 [--push]  tag the component repositories, and push the tags
    scripts/release.py finish v0.4.0 [--push]  wait for the tags' builds, point stable at the
                                               release, tag this repository, draft the notes

Each step checks before it acts and prints exactly what it will push. Nothing
leaves this machine without --push. --dry-run runs every check, prints every
step and changes nothing: no tag, no commit, no push (it fetches main, unless
--no-fetch; the drafted notes go to a temporary directory).

The repositories are `git clone`s of github.com/zaentrum/<name>, side by side in
one directory: --root, by default the directory that holds this repository.
docs/releases.md is the whole process: what a release publishes, the
channels, and the order of the steps.

A component repository is ready to be tagged when it is on main, clean, in step
with origin/main, its CI is green at that commit, the workflows that build its
release run on the tag, and the version is newer than every tag it has.
"""
import argparse
import datetime
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ORG = "zaentrum"
FRONT_DOOR = "zaentrum"
GUIDE = "https://github.com/zaentrum/zaentrum/blob/main/docs/releases.md"


class Component:
    """A repository tagged in a release: the images its tag publishes, the
    workflows that must build on the tag, and the GitHub release assets they
    attach ({v} is the version without its v)."""

    def __init__(self, name, images, workflows, assets=()):
        self.name, self.images, self.workflows, self.assets = name, images, workflows, list(assets)


ZAE_ASSETS = ["checksums.txt"] + [
    f"zae_{{v}}_{goos}_{arch}.{'zip' if goos == 'windows' else 'tar.gz'}"
    for goos in ("linux", "darwin", "windows") for arch in ("amd64", "arm64")
]

COMPONENTS = [
    Component("katalog-manager", ["katalog-manager"], ["image.yml"]),
    Component("katalog-manager-ui", ["katalog-manager-ui"], ["image.yml"]),
    Component("katalog-api", ["katalog-api"], ["image.yml"]),
    Component("katalog-ingest", ["katalog-ingest"], ["image.yml"]),
    Component("chino-api", ["chino-api"], ["image.yml"]),
    Component("chino-stream", ["chino-stream"], ["image.yml"]),
    Component("chino-web", ["chino-web"], ["image.yml"]),
    Component("zaentrum-portal", ["zaentrum-portal", "portal-api"], ["image.yml", "image-api.yml"]),
    Component("analyzer", ["analyzer"], ["image.yml"]),
    Component("transcoder", ["transcoder"], ["image.yml"]),
    Component("packager", ["packager"], ["image.yml"]),
    Component("zae", ["zae"], ["image.yml", "release.yml"], ZAE_ASSETS),
    Component("sample-addon", ["sample-addon"], ["image.yml"]),
    Component(
        "zaentrum-operator",
        ["operator", "admin", "keycloak", "appliance", "operator-bundle", "operator-catalog"],
        ["build-images.yml", "operator-bundle.yml", "all-in-one.yml", "release.yml"],
        ["operator-install.yaml"],
    ),
]


class Failure(Exception):
    pass


# ── versions ──────────────────────────────────────────────────────────────────

SEMVER = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")


def version_key(tag):
    """Sort key of a vX.Y.Z[-pre] tag; a pre-release sorts before its release."""
    m = SEMVER.match(tag)
    if not m:
        raise ValueError(tag)
    major, minor, patch, pre = int(m[1]), int(m[2]), int(m[3]), m[4]
    if pre is None:
        return (major, minor, patch, 1, ())
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return (major, minor, patch, 0, parts)


def is_prerelease(tag):
    return SEMVER.match(tag)[4] is not None


def minor_of(tag):
    m = SEMVER.match(tag)
    return f"{m[1]}.{m[2]}"


def next_minor(tags):
    newest = max(tags, key=version_key)
    m = SEMVER.match(newest)
    return f"v{m[1]}.{int(m[2]) + 1}.0"


# ── git / gh ──────────────────────────────────────────────────────────────────

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise Failure(f"{' '.join(cmd)}: {(r.stderr or r.stdout).strip()}")
    return r


def git(path, *args, check=True):
    return run(["git", "-C", path, *args], check=check).stdout.strip()


def gh_json(*args):
    out = run(["gh", *args]).stdout
    return json.loads(out) if out.strip() else []


def remote_tags(path):
    """origin's tags as name -> the commit each points at (peeled)."""
    tags = {}
    for line in git(path, "ls-remote", "--tags", "origin").splitlines():
        sha, ref = line.split("\t")
        name = ref[len("refs/tags/"):]
        if name.endswith("^{}"):
            tags[name[:-3]] = sha
        else:
            tags.setdefault(name, sha)
    return tags


def local_tag(path, tag):
    r = run(["git", "-C", path, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}"], check=False)
    return r.stdout.strip() if r.returncode == 0 else ""


def push_tag_patterns(text):
    """The tag filters of a workflow's push trigger: on.push.tags, inline or as
    a block list. A light reading of the YAML, enough for these workflows."""
    lines = text.splitlines()
    pats = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)push:\s*$", line)
        if not m:
            continue
        indent = len(m[1])
        j = i + 1
        while j < len(lines):
            cur = lines[j]
            if not cur.strip() or cur.lstrip().startswith("#"):
                j += 1
                continue
            if len(cur) - len(cur.lstrip()) <= indent:
                break
            t = re.match(r"^(\s*)tags:\s*(.*?)\s*$", cur)
            if t:
                rest = t[2]
                if rest.startswith("["):
                    pats += [p.strip().strip("'\"") for p in rest.strip("[]").split(",") if p.strip()]
                else:
                    k = j + 1
                    while k < len(lines) and re.match(r"^\s*-\s", lines[k]):
                        pats.append(lines[k].split("-", 1)[1].strip().strip("'\""))
                        k += 1
            j += 1
    return pats


def workflow_name(text, fallback):
    m = re.search(r"^name:\s*(.+?)\s*$", text, re.M)
    return m[1].strip("'\"") if m else fallback


# ── the registry ──────────────────────────────────────────────────────────────

ACCEPT = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])


def image_published(image, tag):
    """Whether ghcr.io holds ghcr.io/zaentrum/<image>:<tag>, asked as an
    anonymous pull would ask (the images are public)."""
    try:
        url = f"https://ghcr.io/token?scope=repository:{ORG}/{image}:pull"
        with urllib.request.urlopen(url, timeout=20) as r:
            token = json.load(r).get("token", "")
        req = urllib.request.Request(
            f"https://ghcr.io/v2/{ORG}/{image}/manifests/{tag}", method="HEAD",
            headers={"Authorization": f"Bearer {token}", "Accept": ACCEPT})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except (urllib.error.URLError, ValueError, OSError):
        return False


# ── one repository's state ────────────────────────────────────────────────────

class State:
    def __init__(self, comp, path):
        self.comp, self.path = comp, path
        self.sha = self.subject = ""
        self.tagged = ""     # "", "local" (made, not pushed) or "pushed"
        self.ci = ""
        self.errors, self.notes = [], []

    def error(self, msg):
        self.errors.append(msg)

    def note(self, msg):
        self.notes.append(msg)


def ci_state(st):
    """green / pending / red / unverified at the checkout's HEAD, and why."""
    runs = gh_json("run", "list", "-R", f"{ORG}/{st.comp.name}", "--commit", st.sha, "-L", "100",
                   "--json", "workflowName,status,conclusion,createdAt,url")
    latest = {}
    for r in runs:
        if r["workflowName"] not in latest or r["createdAt"] > latest[r["workflowName"]]["createdAt"]:
            latest[r["workflowName"]] = r
    if latest:
        pending = sorted(w for w, r in latest.items() if r["status"] != "completed")
        red = sorted(w for w, r in latest.items()
                     if r["status"] == "completed" and r["conclusion"] not in ("success", "skipped", "neutral"))
        if red:
            return "red", "failed at HEAD: " + ", ".join(f"{w} ({latest[w]['url']})" for w in red)
        if pending:
            return "pending", "still running at HEAD: " + ", ".join(pending)
        return "green", ", ".join(sorted(latest))
    # Nothing ran at HEAD: path filters left the commit out, or the runs were
    # made for commits history no longer has. Green only if each workflow HEAD
    # defines passed its last run on main, on a commit HEAD contains.
    defined = set()
    for f in git(st.path, "ls-tree", "--name-only", "HEAD", ".github/workflows/").splitlines():
        if f.endswith((".yml", ".yaml")):
            defined.add(workflow_name(git(st.path, "show", f"HEAD:{f}"), os.path.basename(f)))
    runs = gh_json("run", "list", "-R", f"{ORG}/{st.comp.name}", "--branch", "main", "--event", "push",
                   "-L", "100", "--json", "workflowName,status,conclusion,createdAt,headSha")
    latest = {}
    for r in runs:
        if r["workflowName"] not in defined:
            continue
        if r["workflowName"] not in latest or r["createdAt"] > latest[r["workflowName"]]["createdAt"]:
            latest[r["workflowName"]] = r
    if not latest:
        return "unverified", "no CI run on main at all"
    for w, r in sorted(latest.items()):
        contained = run(["git", "-C", st.path, "merge-base", "--is-ancestor", r["headSha"], st.sha],
                        check=False).returncode == 0
        if r["conclusion"] != "success" or not contained:
            why = "is not in HEAD's history" if not contained else f"ended {r['conclusion'] or r['status']}"
            return "unverified", f"no run at HEAD, and {w}'s last run on main ({r['headSha'][:8]}) {why}"
    return "green", "no run at HEAD (path filters); each workflow's last run on main passed"


def inspect(root, comp, version, fetch):
    st = State(comp, os.path.join(root, comp.name))
    if not os.path.exists(os.path.join(st.path, ".git")):
        st.error(f"no checkout at {st.path}")
        return st
    try:
        origin = git(st.path, "remote", "get-url", "origin")
        if not re.search(rf"[:/]{ORG}/{re.escape(comp.name)}(\.git)?$", origin):
            st.error(f"origin is {origin}, not {ORG}/{comp.name}")
        if fetch:
            git(st.path, "fetch", "--quiet", "origin", "main")
        branch = git(st.path, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        if branch != "main":
            st.error(f"on {branch or 'a detached HEAD'}, not main")
        changed = git(st.path, "status", "--porcelain", "--untracked-files=no")
        if changed:
            st.error(f"uncommitted changes ({len(changed.splitlines())} files)")
        untracked = [l for l in git(st.path, "status", "--porcelain").splitlines() if l.startswith("??")]
        if untracked:
            st.note(f"{len(untracked)} untracked paths (not part of the tag)")
        st.sha = git(st.path, "rev-parse", "HEAD")
        st.subject = git(st.path, "log", "-1", "--format=%s")
        upstream = git(st.path, "rev-parse", "origin/main")
        if st.sha != upstream:
            ahead, behind = git(st.path, "rev-list", "--left-right", "--count", f"HEAD...origin/main").split()
            st.error(f"not origin/main: {ahead} ahead, {behind} behind — the tag must be on a pushed commit of main")

        remote = remote_tags(st.path)
        local = local_tag(st.path, version)
        if version in remote:
            if remote[version] == st.sha:
                st.tagged = "pushed"
            else:
                st.error(f"{version} already exists on origin, at {remote[version][:8]} — not HEAD")
        elif local:
            if local == st.sha:
                st.tagged = "local"
            else:
                st.error(f"a local {version} exists at {local[:8]}, not HEAD (git tag -d {version} if it is stale)")
        known = set(remote) | set(git(st.path, "tag", "-l", "v*").split())
        newer = sorted((t for t in known if SEMVER.match(t) and t != version
                        and version_key(t) >= version_key(version)), key=version_key)
        if newer:
            st.error(f"{version} is not newer than the repository's {newer[-1]}")

        for wf in comp.workflows:
            show = run(["git", "-C", st.path, "show", f"HEAD:.github/workflows/{wf}"], check=False)
            if show.returncode != 0:
                st.error(f".github/workflows/{wf} is not on main")
                continue
            pats = push_tag_patterns(show.stdout)
            if not any(fnmatch.fnmatchcase(version, p) for p in pats):
                st.error(f"{wf} does not build on the tag {version} (its push tags: {', '.join(pats) or 'none'}) — "
                         "merge the release pipeline first")
        st.ci, why = ci_state(st)
        if st.ci != "green":
            st.error(f"CI {st.ci}: {why}")
    except Failure as e:
        st.error(str(e))
    return st


def report(states, version):
    print(f"\nZaentrum {version} — {len(states)} repositories\n")
    width = max(len(s.comp.name) for s in states)
    for s in states:
        mark = "ok " if not s.errors else "!! "
        tagged = {"pushed": "tag pushed", "local": "tag made"}.get(s.tagged, "")
        print(f"  {mark}{s.comp.name:<{width}}  {s.sha[:8] or '-':<8}  {s.ci or '-':<10}  {tagged:<10}  {s.subject[:70]}")
    problems = [(s, e) for s in states for e in s.errors]
    notes = [(s, n) for s in states for n in s.notes]
    if notes:
        print("\nnotes:")
        for s, n in notes:
            print(f"  {s.comp.name}: {n}")
    if problems:
        print("\nnot ready:")
        for s, e in problems:
            print(f"  {s.comp.name}: {e}")
        taken = sorted({e.split("repository's ")[-1] for _, e in problems if "is not newer than" in e}, key=version_key)
        if taken:
            print(f"\n  {version} is taken or behind in some repositories. Every repository must take the same, "
                  f"newer tag: the smallest that is newer than all of them is {next_minor(taken)}.")
    return not problems


# ── check / tag ───────────────────────────────────────────────────────────────

def components(args):
    if not args.only:
        return COMPONENTS
    wanted = set(args.only.split(","))
    unknown = wanted - {c.name for c in COMPONENTS}
    if unknown:
        raise Failure(f"--only names no such repository: {', '.join(sorted(unknown))}")
    return [c for c in COMPONENTS if c.name in wanted]


def front_door_note(args):
    """This repository is tagged last, by finish; say now what finish will need."""
    front = os.path.join(args.root, FRONT_DOOR)
    if not os.path.exists(os.path.join(front, ".git")):
        print(f"\n{FRONT_DOOR}: no checkout at {front} — finish needs one")
        return
    try:
        problems = front_door_problems(front, args)
    except Failure as e:
        problems = [str(e)]
    if problems:
        print(f"\n{FRONT_DOOR} (tagged by finish, after the builds): " + "; ".join(problems))
    else:
        print(f"\n{FRONT_DOOR} (tagged by finish, after the builds): ready")


def cmd_check(args):
    states = [inspect(args.root, c, args.version, not args.no_fetch) for c in components(args)]
    ready = report(states, args.version)
    front_door_note(args)
    print("\nready to tag." if ready else "")
    return 0 if ready else 1


def cmd_tag(args):
    states = [inspect(args.root, c, args.version, not args.no_fetch) for c in components(args)]
    ready = report(states, args.version)
    front_door_note(args)
    if not ready:
        print("\nnothing tagged." + (" (dry run)" if args.dry_run else ""))
        return 1
    message = (f"{{repo}} {args.version}\n\nPart of the Zaentrum {args.version} release, tagged in every "
               f"repository of the platform at once: {GUIDE}")
    print()
    for s in states:
        if s.tagged:
            print(f"  {s.comp.name}: {args.version} already {'pushed' if s.tagged == 'pushed' else 'made'} at {s.sha[:8]}")
            continue
        if args.dry_run:
            print(f"  {s.comp.name}: would tag {s.sha[:8]} as {args.version} (annotated)")
        else:
            git(s.path, "tag", "-a", args.version, "-m", message.format(repo=s.comp.name), s.sha)
            s.tagged = "local"
            print(f"  {s.comp.name}: tagged {s.sha[:8]} as {args.version}")
    pushes = [s for s in states if s.tagged != "pushed"]
    if not pushes:
        print("\nevery tag is on origin already: run `finish`.")
        return 0
    print("\nto push — this starts every release build:")
    for s in pushes:
        print(f"  git -C {s.path} push origin refs/tags/{args.version}")
    if args.push and not args.dry_run:
        print()
        for s in pushes:
            git(s.path, "push", "--quiet", "origin", f"refs/tags/{args.version}")
            print(f"  pushed {s.comp.name} {args.version}")
        print(f"\nthen: scripts/release.py finish {args.version}")
    elif not args.dry_run:
        print("\nnot pushed (no --push).")
    else:
        print("\n(dry run: nothing tagged, nothing pushed)")
    return 0


# ── finish ────────────────────────────────────────────────────────────────────

def release_commit(path, version, dry_run):
    """The commit the release tag names: the pushed tag's, or for a dry run
    before tagging, HEAD."""
    sha = local_tag(path, version)
    if sha:
        return sha, True
    remote = remote_tags(path).get(version, "")
    if remote:
        return remote, True
    if dry_run:
        return git(path, "rev-parse", "HEAD"), False
    raise Failure(f"{os.path.basename(path)} has no tag {version}: run `tag` first")


def build_states(comp, path, version):
    """Each expected workflow's latest run for the tag: (name, status, conclusion, url)."""
    out = []
    for wf in comp.workflows:
        text = git(path, "show", f"{version}:.github/workflows/{wf}", check=False) or ""
        name = workflow_name(text, wf)
        runs = gh_json("run", "list", "-R", f"{ORG}/{comp.name}", "--workflow", wf, "--branch", version,
                       "-L", "20", "--json", "status,conclusion,createdAt,url,event")
        runs = [r for r in runs if r.get("event") == "push"]
        if not runs:
            out.append((name, "missing", "", ""))
            continue
        r = max(runs, key=lambda r: r["createdAt"])
        out.append((name, r["status"], r["conclusion"] or "", r["url"]))
    return out


def wait_for_builds(root, version, comps, timeout_min, interval=60):
    deadline = time.time() + timeout_min * 60
    last = None
    while True:
        rows, done, failed = [], True, []
        for c in comps:
            for name, status, conclusion, url in build_states(c, os.path.join(root, c.name), version):
                state = conclusion if status == "completed" else status
                rows.append(f"{c.name}/{name}: {state}")
                if status != "completed":
                    done = False
                elif conclusion != "success":
                    failed.append(f"{c.name}/{name} {conclusion}: {url}")
        snapshot = "\n".join(rows)
        if snapshot != last:
            print(f"\n{time.strftime('%H:%M:%S')} the {version} builds:")
            for r in rows:
                print(f"  {r}")
            last = snapshot
        if failed:
            raise Failure("a release build failed — fix it, re-run it (gh run rerun), then finish again:\n  "
                          + "\n  ".join(failed))
        if done:
            return
        if time.time() > deadline:
            raise Failure(f"the {version} builds did not finish in {timeout_min} minutes")
        time.sleep(interval)


def verify_artifacts(version, comps):
    """Every image at the release's tags, and every release asset. Returns the
    problems."""
    problems = []
    tags = [version] if is_prerelease(version) else [version, minor_of(version)]
    for c in comps:
        for image in c.images:
            for tag in tags:
                if not image_published(image, tag):
                    problems.append(f"ghcr.io/{ORG}/{image}:{tag} is not published")
        if c.assets:
            try:
                rel = gh_json("release", "view", version, "-R", f"{ORG}/{c.name}", "--json", "assets,isDraft")
                have = {a["name"] for a in rel.get("assets", [])}
            except Failure:
                have = set()
                problems.append(f"{c.name} has no GitHub release {version}")
                continue
            for asset in c.assets:
                name = asset.format(v=version[1:])
                if name not in have:
                    problems.append(f"{c.name}'s release {version} has no {name}")
    return problems


def releases_document(path, version):
    """releases.json with stable on the release, and the release recorded."""
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    channels = doc.setdefault("channels", {})
    channels["stable"] = version
    channels.setdefault("edge", "latest")
    versions = doc.setdefault("versions", {})
    versions[version] = {
        "released": datetime.date.today().isoformat(),
        "notes": f"Zaentrum {version}: every image, the operator, its install, the appliance and the zae CLI, "
                 f"tagged together. https://github.com/{ORG}/{FRONT_DOOR}/releases/tag/{version}",
    }
    versions["latest"] = {"notes": "Rolling: the newest build of main, which edge serves. Every push to main moves it."}
    return doc


def render_releases(doc):
    """The document in the file's own layout: the channels on one line, the
    newest release first, latest last."""
    channels = ", ".join(f"{json.dumps(k)}: {json.dumps(v)}" for k, v in doc["channels"].items())
    names = sorted((v for v in doc["versions"] if SEMVER.match(v)), key=version_key, reverse=True)
    names += [v for v in doc["versions"] if not SEMVER.match(v)]
    entries = []
    for name in names:
        fields = ",\n".join(f"      {json.dumps(k)}: {json.dumps(v)}" for k, v in doc["versions"][name].items())
        entries.append(f"    {json.dumps(name)}: {{\n{fields}\n    }}")
    return ("{\n"
            f"  \"channels\": {{ {channels} }},\n"
            "  \"versions\": {\n" + ",\n".join(entries) + "\n  }\n}\n")


AREA = re.compile(r"^([A-Za-z][\w ./()&+-]{0,40}?):\s+(.+)$")

# The public repositories' neutrality rules, for notes made of commit subjects:
# no internal hostnames, no other media products, no acquisition tools or
# vocabulary. Put together from pieces, as the repositories' own gates are, so
# this file does not name what it looks for.
_HOSTS = "|".join(re.escape(a + "." + b) for a, b in (("nalet", "cloud"), ("implentic", "com")))
_WORDS = "|".join([
    "jelly" "fin", "pl" "ex", "em" "by", "ko" "di",
    "nz" "bget", "qbit" "tor" "rent", "jdown" "loader", "odown" "loader", "so" "narr", "ra" "darr",
    "prow" "larr", "jack" "ett", "trans" "mission", "del" "uge", "download[-_]?gate" "way",
    "use" "net", "nz" "b", "tor" "rent", "trac" "ker", "index" "er", "scrap" "er",
])
UNNEUTRAL = re.compile(rf"({_HOSTS})|(^|[^0-9A-Za-z])({_WORDS})([^0-9A-Za-z]|$)", re.I)


def unneutral_lines(text):
    return [line for line in text.splitlines() if UNNEUTRAL.search(line)]


def commits(path, rng):
    out = git(path, "log", "--no-merges", "--format=%h%x1f%as%x1f%s", *rng)
    return [line.split("\x1f") for line in out.splitlines() if line]


def notes_for(comp, path, version, ref, tagged):
    """A repository's notes: its changes since its previous tag, or for its
    first release, a summary of what it holds."""
    prev = sorted((t for t in git(path, "tag", "--merged", ref, "-l", "v*").split()
                   if SEMVER.match(t) and t != version and version_key(t) < version_key(version)),
                  key=version_key)
    prev = prev[-1] if prev else ""
    log = commits(path, [f"{prev}..{ref}"] if prev else [ref])
    groups = {}
    for sha, day, subject in log:
        m = AREA.match(subject)
        area, text = (m[1].lower(), m[2]) if m else ("other", subject)
        groups.setdefault(area, []).append((sha, day, text))
    title = f"## {comp.name} {version}" + ("" if tagged else " (preview: not tagged yet)")
    lines = [title, ""]
    tags = [version] if is_prerelease(version) else [version, minor_of(version)]
    if comp.images:
        lines.append("Images: " + ", ".join(f"`ghcr.io/{ORG}/{i}:{t}`" for i in comp.images for t in tags) + ".")
        lines.append("")
    if prev:
        lines.append(f"{len(log)} commits since {prev} "
                     f"([compare](https://github.com/{ORG}/{comp.name}/compare/{prev}...{version})):")
        lines.append("")
        for area in sorted(groups, key=lambda a: (-len(groups[a]), a)):
            for sha, _, text in groups[area]:
                lines.append(f"- **{area}**: {text} ({sha})")
    else:
        first, last = (log[-1][1], log[0][1]) if log else ("", "")
        lines.append(f"The first tagged release of {comp.name}: {len(log)} commits, {first} to {last}. "
                     "By area, with the latest changes in each:")
        lines.append("")
        for area in sorted(groups, key=lambda a: (-len(groups[a]), a)):
            items = groups[area]
            recent = "; ".join(text for _, _, text in items[:3])
            lines.append(f"- **{area}** ({len(items)}): {recent}")
    lines.append("")
    return "\n".join(lines), len(log), prev


def platform_notes(version, rows, per_repo):
    tags = f"`{version}`" + ("" if is_prerelease(version) else f" (and `{minor_of(version)}`, its newest patch)")
    out = [
        f"# Zaentrum {version}", "",
        f"The platform at {version}: every image, the operator and its install, the appliance and the "
        f"`zae` CLI, tagged together. Every `ghcr.io/{ORG}` image is published as {tags}. "
        f"The `stable` channel names {version}; `edge` stays on `latest`.", "",
        "## Install", "",
        "```sh",
        "# the appliance: the whole platform in one container, pinned to this release",
        f"docker run -d --privileged --restart unless-stopped -p 80:80 --name zaentrum ghcr.io/{ORG}/appliance:{version}",
        "",
        "# a cluster: the operator, its CRDs and RBAC, then a Zaentrum on the stable channel",
        f"kubectl apply -f https://github.com/{ORG}/zaentrum-operator/releases/download/{version}/operator-install.yaml",
        "```", "",
        f"OLM: the catalog `ghcr.io/{ORG}/operator-catalog:{version}` serves `zaentrum-operator.{version}` on "
        f"`stable`. The CLI: [zae {version}](https://github.com/{ORG}/zae/releases/tag/{version}). "
        f"How releases and channels work: [the releases guide]({GUIDE}).", "",
        "## What is in it", "",
        "| Repository | Commit | Changes |",
        "|---|---|---|",
    ]
    for name, sha, count, prev in rows:
        since = f"{count} since {prev}" if prev else f"first release, {count} commits"
        out.append(f"| [{name}](https://github.com/{ORG}/{name}/tree/{version}) | `{sha[:8]}` | {since} |")
    out += ["", "## By repository", ""]
    for text in per_repo:
        out.append(text.replace("\n## ", "\n### ").replace("## ", "### ", 1))
    return "\n".join(out) + "\n"


def cmd_finish(args):
    comps = components(args)
    front = os.path.join(args.root, FRONT_DOOR)
    version = args.version

    # 1. every tag is on origin, where it was made
    print(f"\nZaentrum {version}: finishing")
    refs, missing = {}, []
    for c in comps:
        path = os.path.join(args.root, c.name)
        sha, tagged = release_commit(path, version, args.dry_run)
        pushed = remote_tags(path).get(version, "")
        if not pushed:
            missing.append(c.name)
        elif sha != pushed:
            raise Failure(f"{c.name}: origin's {version} is {pushed[:8]}, the local one {sha[:8]}")
        refs[c.name] = (sha, tagged)
    if missing:
        if not args.dry_run:
            raise Failure(f"not pushed yet: {', '.join(missing)} — `tag {version} --push` first")
        print(f"  (dry run) not pushed yet: {', '.join(missing)}")

    # 2. their builds
    if args.dry_run or args.no_wait:
        print("  not waiting for the builds" + (" (dry run)" if args.dry_run else ""))
    else:
        wait_for_builds(args.root, version, comps, args.timeout)

    # 3. what they published
    problems = verify_artifacts(version, comps)
    if problems:
        print("\nnot published:" if not args.dry_run else "\nnot published yet (expected before the tags are pushed):")
        for p in problems:
            print(f"  {p}")
        if not args.dry_run:
            raise Failure("the release is incomplete: stable stays where it is")
    else:
        print("\nevery image and release asset is published.")

    # 4. stable -> the release, in this repository, tagged. A pre-release is
    # published, never served: stable stays, and this repository stays untagged.
    if is_prerelease(version):
        print(f"\n{version} is a pre-release: stable stays where it is, and {FRONT_DOOR} is not tagged.")
    else:
        publish_stable(front, version, args)

    # 5. the notes
    notes_dir = args.notes_dir or tempfile.mkdtemp(prefix=f"zaentrum-{version}-notes-")
    os.makedirs(notes_dir, exist_ok=True)
    rows, per_repo = [], []
    for c in comps:
        sha, tagged = refs[c.name]
        text, count, prev = notes_for(c, os.path.join(args.root, c.name), version, sha, tagged)
        with open(os.path.join(notes_dir, f"{c.name}.md"), "w", encoding="utf-8") as f:
            f.write(text)
        rows.append((c.name, sha, count, prev))
        per_repo.append(text)
    with open(os.path.join(notes_dir, f"{FRONT_DOOR}.md"), "w", encoding="utf-8") as f:
        f.write(platform_notes(version, rows, per_repo))
    print(f"\nrelease notes drafted in {notes_dir}: {FRONT_DOOR}.md (the platform) and one per repository")
    for name in [c.name for c in comps] + [FRONT_DOOR]:
        with open(os.path.join(notes_dir, f"{name}.md"), encoding="utf-8") as f:
            for line in unneutral_lines(f.read()):
                print(f"  review {name}.md — a public release must not carry this: {line[:120]}")

    # 6. push, and the draft releases
    if not is_prerelease(version):
        print("\nto push — stable moves for every install that follows it:")
        print(f"  git -C {front} push origin main")
        print(f"  git -C {front} push origin refs/tags/{version}")
        if args.push and not args.dry_run:
            git(front, "push", "--quiet", "origin", "main")
            git(front, "push", "--quiet", "origin", f"refs/tags/{version}")
            print(f"  pushed: stable is {version}")
        elif not args.dry_run:
            print("  not pushed (no --push).")
    draft_releases(args, comps, notes_dir)
    if args.dry_run:
        print("\n(dry run: nothing committed, tagged or pushed)")
    return 0


def publish_stable(front, version, args):
    """Commit releases.json with stable on the release, and tag that commit."""
    for problem in front_door_problems(front, args):
        if not args.dry_run:
            raise Failure(f"{FRONT_DOOR}: {problem}")
        print(f"  (dry run) {FRONT_DOOR}: {problem}")
    path = os.path.join(front, "releases.json")
    with open(path, encoding="utf-8") as f:
        before = f.read()
    after = render_releases(releases_document(path, version))
    if before == after:
        print(f"\nreleases.json already names {version} on stable.")
    else:
        print("\nreleases.json, after:\n" + "\n".join(f"  {l}" for l in after.splitlines()))
        if not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.write(after)
            git(front, "add", "releases.json")
            git(front, "commit", "--quiet", "-m", f"releases: stable is {version}",
                "-m", f"Every repository of the platform is tagged {version} and its builds are published. "
                      f"The operator's stable channel now names {version}; edge stays on latest.")
            print(f"  committed: {git(front, 'log', '-1', '--format=%h %s')}")
    if local_tag(front, version):
        print(f"  {FRONT_DOOR} is tagged {version} already")
    elif args.dry_run:
        print(f"  would tag {FRONT_DOOR}'s commit with stable on {version} as {version}")
    else:
        git(front, "tag", "-a", version, "-m", f"Zaentrum {version}\n\nstable names {version}: {GUIDE}")
        print(f"  tagged {FRONT_DOOR} {version}")


def front_door_problems(front, args):
    problems = []
    if not args.no_fetch:
        git(front, "fetch", "--quiet", "origin", "main")
    if git(front, "symbolic-ref", "--quiet", "--short", "HEAD", check=False) != "main":
        problems.append("not on main")
    if git(front, "status", "--porcelain", "--untracked-files=no"):
        problems.append("uncommitted changes")
    if run(["git", "-C", front, "merge-base", "--is-ancestor", "origin/main", "HEAD"], check=False).returncode:
        problems.append("main does not contain origin/main: pull first")
    if run(["git", "-C", front, "cat-file", "-e", "HEAD:docs/releases.md"], check=False).returncode:
        problems.append("docs/releases.md is not on main: merge the release branch first")
    return problems


def draft_releases(args, comps, notes_dir):
    """Draft GitHub releases with the notes, where none exists. zae's and the
    operator's are made by their tag builds; this one only drafts."""
    version = args.version
    built = {c.name for c in comps if c.assets}  # their tag builds make their releases
    names = [c.name for c in comps] + ([] if is_prerelease(version) else [FRONT_DOOR])
    plan = []
    for name in names:
        exists = run(["gh", "release", "view", version, "-R", f"{ORG}/{name}"], check=False).returncode == 0
        notes = os.path.join(notes_dir, f"{name}.md")
        if exists or name in built:
            edit = shlex.join(["gh", "release", "edit", version, "-R", f"{ORG}/{name}", "--notes-file", notes])
            made = "made by its tag build" + ("" if exists else ", not there yet")
            plan.append((name, None, f"{made}; to replace its notes: {edit}"))
        else:
            plan.append((name, ["gh", "release", "create", version, "-R", f"{ORG}/{name}", "--draft", "--verify-tag",
                                "--title", f"{name} {version}" if name != FRONT_DOOR else f"Zaentrum {version}",
                                "--notes-file", notes], None))
    print("\nGitHub releases" + (" (--publish-notes makes the drafts):" if not args.publish_notes else ":"))
    for name, create, hint in plan:
        if create and args.publish_notes and not args.dry_run:
            path = os.path.join(args.root, name)
            with open(os.path.join(notes_dir, f"{name}.md"), encoding="utf-8") as f:
                if unneutral_lines(f.read()):
                    print(f"  {name}: not drafted — its notes name what a public release must not; edit "
                          f"them, then: {shlex.join(create)}")
                    continue
            if version not in remote_tags(path):
                print(f"  {name}: {version} is not on origin yet — push it, then: {shlex.join(create)}")
                continue
            try:
                run(create)
                print(f"  {name}: drafted — publish it with gh release edit {version} -R {ORG}/{name} --draft=false")
            except Failure as e:
                print(f"  {name}: could not draft its release: {e}")
        elif create:
            print(f"  {shlex.join(create)}")
        else:
            print(f"  {name}: {hint}")


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=GUIDE)
    p.add_argument("step", choices=["check", "tag", "finish"])
    p.add_argument("version", help="the release, vX.Y.Z (or vX.Y.Z-rc.N)")
    p.add_argument("--root", default=os.path.dirname(os.path.dirname(here)),
                   help="the directory holding the repositories (default: %(default)s)")
    p.add_argument("--push", action="store_true", help="push what the step made (tags; main and its tag)")
    p.add_argument("--dry-run", action="store_true", help="check and print every step, change nothing")
    p.add_argument("--no-fetch", action="store_true", help="do not fetch origin's main first")
    p.add_argument("--only", help="a comma-separated subset of the component repositories")
    p.add_argument("--no-wait", action="store_true", help="finish: do not wait for the builds, only check them")
    p.add_argument("--timeout", type=int, default=150, help="finish: minutes to wait for the builds (default 150)")
    p.add_argument("--notes-dir", help="finish: where to draft the notes (default: a new temporary directory)")
    p.add_argument("--publish-notes", action="store_true",
                   help="finish: draft GitHub releases with the notes where none exists")
    args = p.parse_args(argv)
    args.root = os.path.abspath(args.root)
    if not SEMVER.match(args.version):
        p.error(f"{args.version} is not vX.Y.Z or vX.Y.Z-pre")
    if args.only and args.step == "finish":
        p.error("finish takes the whole release, not --only")
    try:
        run(["gh", "auth", "status"])
        return {"check": cmd_check, "tag": cmd_tag, "finish": cmd_finish}[args.step](args)
    except Failure as e:
        print(f"\nrelease.py: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
