#!/usr/bin/env python3
"""Validate docs/ before it ships: every relative link must point at a file
that exists, and every #anchor into a doc must match a heading there.

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

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs"))
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*(?:\{#([^}]+)\})?\s*$")


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
        text = m.group(1)
        slug = re.sub(r"[^\w\- ]", "", text.lower()).strip().replace(" ", "-")
        out.add(slug)
    return out


def md_files():
    for dirpath, _, names in os.walk(ROOT):
        for n in names:
            if n.endswith(".md"):
                yield os.path.join(dirpath, n)


def main():
    fail = 0
    anchor_cache = {}
    for f in md_files():
        rel_dir = os.path.dirname(os.path.relpath(f, ROOT))
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
                resolved = os.path.normpath(os.path.join(ROOT, rel_dir, path))
                if not os.path.exists(resolved):
                    print(f"BROKEN {os.path.relpath(f, ROOT)}:{lineno} -> {target}")
                    fail = 1
                    continue
                if anchor and resolved.endswith(".md"):
                    if resolved not in anchor_cache:
                        anchor_cache[resolved] = anchors_of(resolved)
                    if anchor not in anchor_cache[resolved]:
                        print(f"BAD ANCHOR {os.path.relpath(f, ROOT)}:{lineno} -> {target}")
                        fail = 1
    print("docs links: " + ("FAILED" if fail else "clean"))
    sys.exit(fail)


if __name__ == "__main__":
    main()
