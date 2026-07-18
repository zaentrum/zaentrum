#!/usr/bin/env python3
"""Generate the GitHub Wiki from the repo's docs/ (single source of truth).

Usage: build-wiki.py <src-docs-dir> <dst-wiki-dir>

The wiki is a *mirror* of docs/: edit the markdown in docs/, never the wiki
directly. This script is run locally for the first push and by the
wiki-sync GitHub Action on every change to docs/.

Transform rules
  - docs/README.md            -> Home.md          (the wiki landing page)
  - docs/<name>.md            -> <name>.md        (page slug == <name>)
  - relative links  ](./x.md#anchor) / ](x.md)    -> ](x#anchor) / ](x)
    with README -> Home; http(s)/mailto/pure-#anchor links are left as-is;
    links inside fenced code blocks are never rewritten.
  - a curated _Sidebar.md nav and a _Footer.md "generated" note are written.
"""
import os
import re
import sys

# Reading order for the sidebar; (page-slug, label). "Home" is implicit first.
NAV = [
    ("Home", "Home"),
    ("prerequisites", "Prerequisites"),
    ("self-hosting", "Self-hosting"),
    ("operator", "Operator & CR reference"),
    ("reference-demo", "Reference demo"),
    ("updating", "Updating"),
    ("troubleshooting", "Troubleshooting"),
    ("architecture", "Architecture"),
]

SOURCE_TREE = "https://github.com/zaentrum/zaentrum/tree/main/docs"
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def page_for(md_filename):
    """docs filename (README.md / self-hosting.md) -> wiki page slug."""
    base = md_filename[:-3] if md_filename.endswith(".md") else md_filename
    return "Home" if base == "README" else base


def transform_target(target):
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return target
    t = target[2:] if target.startswith("./") else target
    path, sep, anchor = t.partition("#")
    if not path.endswith(".md"):
        return target  # not a doc link (e.g. bare anchor already handled)
    slug = page_for(path)
    return slug + (("#" + anchor) if sep else "")


def transform_markdown(text):
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
        out.append(LINK_RE.sub(lambda m: "](" + transform_target(m.group(1)) + ")", line))
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def build_sidebar():
    lines = ["### Zaentrum docs", ""]
    lines += [f"- [{label}]({slug})" for slug, label in NAV]
    lines += [
        "",
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


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build-wiki.py <src-docs-dir> <dst-wiki-dir>")
    src, dst = sys.argv[1], sys.argv[2]

    # Clear previously-generated markdown (keep .git and any non-.md assets).
    for name in os.listdir(dst):
        if name.endswith(".md") and name != ".git":
            os.remove(os.path.join(dst, name))

    for name in sorted(os.listdir(src)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(src, name), encoding="utf-8") as fh:
            text = fh.read()
        out_name = f"{page_for(name)}.md"
        with open(os.path.join(dst, out_name), "w", encoding="utf-8") as fh:
            fh.write(transform_markdown(text))
        print(f"  {name} -> {out_name}")

    with open(os.path.join(dst, "_Sidebar.md"), "w", encoding="utf-8") as fh:
        fh.write(build_sidebar())
    with open(os.path.join(dst, "_Footer.md"), "w", encoding="utf-8") as fh:
        fh.write(build_footer())
    print("  + _Sidebar.md, _Footer.md")


if __name__ == "__main__":
    main()
