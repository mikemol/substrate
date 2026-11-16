# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Resolve the imports that only work under a `sys.path` insert — the antipattern's own edges.

⚑⚑⚑ THE DEPENDENCY GRAPH IS INVISIBLE TO A DOTTED RESOLVER PRECISELY WHERE THE DEBT IS. A file
that does `sys.path.insert(0, ROOT/"scratch")` then `import vfs` depends on `scratch/vfs.py`,
but nothing in the source says `scratch.vfs`, so a resolver keyed on dotted names finds
nothing. MEASURED before this existed: 257 blockers yielded ONE in-population edge, and the
decomposition ordering reported every file startable — honest for the graph it was handed, and
badly misread as "these files are independent".

⚑⚑ SO THE TRACKER MUST MODEL THE ANTIPATTERN IT IS DRAINING. The insert says WHICH directory a
bare name resolves against; the bare import says WHICH name. Composing them recovers the edge
the language never records. A tracker that refused to model this would stay blind exactly on
the population it exists to order — and would keep reporting a nearly-empty DAG as a fact about
the tree.

⚑ AN EDGE IS EVIDENCE OF THE DEBT, NOT OF GOOD STRUCTURE. Every edge here exists BECAUSE of a
path insert, so draining the insert makes the edge either disappear (the import becomes dotted
and the dotted reader sees it) or become impossible (the name was never reachable). The graph
is therefore a MOVING TARGET whose shrinking is the drain's own progress measure.

⚑⚑ AND A BARE NAME MAY RESOLVE IN SEVERAL INSERTED DIRECTORIES. Python takes the FIRST on
`sys.path`, and insert order is a runtime fact this reader cannot replay — so an ambiguous name
yields every candidate, and the caller decides. Silently picking one would fabricate a specific
dependency out of a genuine ambiguity, which is worse than reporting both.

⚑ AN UNRESOLVED INSERT TARGET CONTRIBUTES NOTHING. When the inserted directory is computed at
runtime, no static reader can say what a bare name under it resolves to; naming a plausible
directory would invent an edge. The count of such sites is `insert_read`'s to report.
"""

from __future__ import annotations

import ast

from substrate import corpus, insert_read

# ⚑ THE REPO'S OWN TOOL DIRECTORIES. An insert naming something else — a vendored tree, an
# absolute path outside the checkout — cannot produce an edge between files this repo orders.
_INSIDE = ("scratch", "scripts", "substrate", "jea", "catalog", "tests")


def inserted_dirs(tree: ast.Module, label: str) -> tuple[str, ...]:
    """Return the repo-relative directories `label` puts on `sys.path`.

    ⚑ THE TARGET IS THE EXISTING READER'S ANSWER, never re-derived. Which directory an insert
    names is a question with one authority, and a second implementation here would disagree
    with the census that reports the same sites.

    ⚑ THE RESULT KEEPS INSERT ORDER, deduplicated by hand. That order is the closest static
    stand-in for the `sys.path` order a real resolution would follow.
    """
    out: list[str] = []
    for site in insert_read.inserts(tree, label):
        if site.target == insert_read.UNKNOWN:
            continue
        named = ""
        for top in _INSIDE:
            if site.target == top or site.target.endswith(f"/{top}"):
                named = top
                break
        if not named and (corpus.ROOT / site.target).is_dir():
            named = site.target
        if named and named not in out:
            out.append(named)
    return tuple(out)


def resolve_bare(name: str, dirs: tuple[str, ...]) -> tuple[str, ...]:
    """Return every repo file `name` could bind to, given the inserted `dirs`.

    ⚑ EVERY CANDIDATE, NOT THE FIRST. Python resolves by `sys.path` order, which depends on
    the order the inserts ran — a runtime fact this reader cannot replay. Reporting one would
    fabricate a specific dependency out of a real ambiguity.
    """
    found: list[str] = []
    for directory in dirs:
        for candidate in (f"{directory}/{name}.py", f"{directory}/{name}/__init__.py"):
            if (corpus.ROOT / candidate).is_file():
                found.append(candidate)
                break
    return tuple(found)


def edges_of(path: str) -> set[str]:
    """Return the repo files `path` reaches by bare import under its own inserts.

    ⚑ THE FILE'S OWN INSERTS, not a global path. A bare name in one file resolves against the
    directories THAT FILE added; using a union over the repo would report edges that only
    exist when some other module happens to have been imported first.
    """
    try:
        tree = ast.parse((corpus.ROOT / path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    dirs = inserted_dirs(tree, path)
    if not dirs:
        return set()
    out: set[str] = set()
    for name in insert_read.bare_names(tree):
        out.update(p for p in resolve_bare(name, dirs) if p != path)
    return out


def graph(paths: list[str]) -> dict[str, set[str]]:
    """Return the bare-import graph over `paths`, restricted to that population."""
    inside = set(paths)
    return {p: {d for d in edges_of(p) if d in inside} for p in paths}


def merged(paths: list[str], dotted: dict[str, set[str]]) -> dict[str, set[str]]:
    """Return the union of a dotted graph and the bare-import graph.

    ⚑⚑ BOTH READINGS ARE REAL DEPENDENCIES AND NEITHER SUBSUMES THE OTHER. A packaged module
    imported dotted is invisible to the bare reader; a sibling imported bare is invisible to
    the dotted one. An ordering built on either alone is blind on half its population, and
    this repo measured that half at 256 of 257 files.
    """
    bare = graph(paths)
    return {p: dotted.get(p, set()) | bare.get(p, set()) for p in paths}
