#!/usr/bin/env python3
"""Validate docs/ and spec/ before they ship: every relative link must point at a
file that exists, and every #anchor into a page must match a heading there.

This exists because the docs have already lied twice in ways a reader paid
for: a section described a setup API that no service implements, and a schema
comment promised a capability the API forbids. A link checker cannot catch
prose, but it catches the structural half — links to pages that were renamed,
removed, or never written.

Run: scripts/check-docs.py   (from anywhere; exits non-zero on failure)
"""
import os
import posixpath
import re
import sys
import unicodedata

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
# the documentation and the specification; spec/ is checked once it exists
TREES = [t for t in (os.path.join(REPO, "docs"), os.path.join(REPO, "spec")) if os.path.isdir(t)]
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*(?:\{#([^}]+)\})?\s*$")


def slug(text):
    """A heading's anchor as GitHub and the docs site make it: lowercase, keep
    letters, numbers, marks, "_", "-" and spaces, then each space becomes "-".
    Nothing is trimmed, so "Field ⚠️" is "field-" plus the emoji's variation
    selector, and a link to "#field" is broken on both."""
    kept = "".join(ch for ch in text.lower()
                   if ch in " -" or unicodedata.category(ch)[0] in "LMN"
                   or unicodedata.category(ch) == "Pc")
    return kept.replace(" ", "-")


def anchors_of(path):
    """GitHub-style anchors for every heading in a markdown file."""
    out = set()
    in_fence = False
    for line in open(path, encoding="utf-8"):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        if m.group(2):  # explicit {#anchor}
            out.add(m.group(2))
        out.add(slug(m.group(1)))
    return out


def md_files():
    for dirpath, _, names in (w for tree in TREES for w in os.walk(tree)):
        for n in names:
            if n.endswith(".md"):
                yield os.path.join(dirpath, n)


def main():
    fail = 0
    anchor_cache = {}
    for f in md_files():
        here = os.path.dirname(f)
        in_fence = False
        for lineno, line in enumerate(open(f, encoding="utf-8"), 1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK_RE.findall(line):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                path, _, anchor = target.partition("#")
                if not path:  # pure in-page anchor
                    continue
                resolved = os.path.normpath(os.path.join(here, path))
                if not os.path.exists(resolved):
                    print(f"BROKEN {os.path.relpath(f, REPO)}:{lineno} -> {target}")
                    fail = 1
                    continue
                if anchor and resolved.endswith(".md"):
                    if resolved not in anchor_cache:
                        anchor_cache[resolved] = anchors_of(resolved)
                    if anchor not in anchor_cache[resolved]:
                        print(f"BAD ANCHOR {os.path.relpath(f, REPO)}:{lineno} -> {target}")
                        fail = 1
    print("docs links: " + ("FAILED" if fail else "clean"))
    sys.exit(fail)


if __name__ == "__main__":
    main()
