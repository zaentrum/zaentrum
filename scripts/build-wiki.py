#!/usr/bin/env python3
"""Generate the GitHub Wiki from the repo's docs/ (single source of truth).

Usage: build-wiki.py <src-docs-dir> <dst-wiki-dir>

The wiki is a *mirror* of docs/: edit the markdown in docs/, never the wiki
directly. This script is run locally for the first push and by the
wiki-sync GitHub Action on every change to docs/.

Transform rules
  - docs/README.md            -> Home.md            (the wiki landing page)
  - docs/<name>.md            -> <name>.md          (page slug == <name>)
  - docs/<dir>/README.md      -> <dir>.md           (a section's landing page)
  - docs/<dir>/<name>.md      -> <dir>-<name>.md    (wiki pages are FLAT — a
    GitHub wiki has no directories, so one level of docs/ nesting is folded
    into the slug)
  - relative links  ](./x.md#anchor) / ](x.md) / ](../x.md) / ](dir/x.md)
    -> ](slug#anchor), resolved against the *linking file's* directory, with
    README -> the section slug; http(s)/mailto/pure-#anchor links are left
    as-is; links inside fenced code blocks are never rewritten.
  - a curated _Sidebar.md nav and a _Footer.md "generated" note are written.
"""
import os
import posixpath
import re
import sys

# Reading order for the sidebar: (section, [(page-slug, label), ...]).
# "Home" is implicit first. A page missing from NAV still syncs — it is just
# not in the sidebar — so forgetting to add one here loses navigation, not
# content.
NAV = [
    ("Run it", [
        ("prerequisites", "Prerequisites"),
        ("self-hosting", "Self-hosting"),
        ("operator", "Operator & CR reference"),
        ("reference-demo", "Reference demo"),
        ("updating", "Updating"),
        ("troubleshooting", "Troubleshooting"),
    ]),
    ("Extend it", [
        ("extending", "Addons — overview"),
        ("extending-slots", "UI slots"),
        ("extending-console", "Hosted consoles"),
        ("extending-ingest", "Catalog ingest"),
        ("extending-events", "Event bus"),
        ("extending-identity", "Addon identity"),
        ("extending-installing", "Installing addons"),
    ]),
    ("Understand it", [
        ("architecture", "Architecture"),
        ("adr", "Decision records (ADRs)"),
    ]),
]

SOURCE_TREE = "https://github.com/zaentrum/zaentrum/tree/main/docs"
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def slug_for(rel_path):
    """docs-relative path (extending/slots.md, README.md) -> wiki page slug."""
    rel = rel_path[:-3] if rel_path.endswith(".md") else rel_path
    parts = rel.split("/")
    if parts[-1] == "README":
        parts = parts[:-1] or ["Home"]
    if parts == ["Home"] or parts == []:
        return "Home"
    return "-".join(parts)


def transform_target(target, src_rel_dir):
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return target
    path, sep, anchor = target.partition("#")
    if not path.endswith(".md"):
        return target  # not a doc link (an asset, or a bare anchor)
    # Resolve against the linking file's directory so ../ and dir/ links from
    # nested pages land on the right flat slug.
    resolved = posixpath.normpath(posixpath.join(src_rel_dir, path))
    if resolved.startswith(".."):
        return target  # points outside docs/ — leave it alone
    slug = slug_for(resolved)
    return slug + (("#" + anchor) if sep else "")


def transform_markdown(text, src_rel_dir):
    out, in_fence = [], False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        out.append(LINK_RE.sub(
            lambda m: "](" + transform_target(m.group(1), src_rel_dir) + ")", line))
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def build_sidebar():
    lines = ["### Zaentrum docs", "", "- [Home](Home)", ""]
    for section, pages in NAV:
        lines.append(f"**{section}**")
        lines += [f"- [{label}]({slug})" for slug, label in pages]
        lines.append("")
    lines += [
        "---",
        f"_Generated from [`docs/`]({SOURCE_TREE}) — edit there, not here._",
        "",
    ]
    return "\n".join(lines)


def build_footer():
    return (
        f"_These pages are generated from [`docs/`]({SOURCE_TREE}) in the main "
        "repo. Edit the docs there; a GitHub Action syncs the wiki automatically._\n"
    )


def walk_docs(src):
    """Yield docs-relative paths of every .md, one directory level deep."""
    for name in sorted(os.listdir(src)):
        full = os.path.join(src, name)
        if os.path.isfile(full) and name.endswith(".md"):
            yield name
        elif os.path.isdir(full):
            for sub in sorted(os.listdir(full)):
                if sub.endswith(".md"):
                    yield f"{name}/{sub}"


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build-wiki.py <src-docs-dir> <dst-wiki-dir>")
    src, dst = sys.argv[1], sys.argv[2]

    # Clear previously-generated markdown (keep .git and any non-.md assets).
    for name in os.listdir(dst):
        if name.endswith(".md") and name != ".git":
            os.remove(os.path.join(dst, name))

    slugs = set()
    for rel in walk_docs(src):
        with open(os.path.join(src, rel), encoding="utf-8") as fh:
            text = fh.read()
        slug = slug_for(rel)
        if slug in slugs:
            sys.exit(f"slug collision: {rel} -> {slug} already written; rename one source file")
        slugs.add(slug)
        out_name = f"{slug}.md"
        with open(os.path.join(dst, out_name), "w", encoding="utf-8") as fh:
            fh.write(transform_markdown(text, posixpath.dirname(rel)))
        print(f"  {rel} -> {out_name}")

    missing = [s for _, pages in NAV for s, _ in pages if s not in slugs]
    if missing:
        sys.exit(f"sidebar links pages that do not exist: {missing}")

    with open(os.path.join(dst, "_Sidebar.md"), "w", encoding="utf-8") as fh:
        fh.write(build_sidebar())
    with open(os.path.join(dst, "_Footer.md"), "w", encoding="utf-8") as fh:
        fh.write(build_footer())
    print("  + _Sidebar.md, _Footer.md")


if __name__ == "__main__":
    main()
