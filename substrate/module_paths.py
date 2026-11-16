# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve dotted module names to the repo files that define them, and back.

⚑⚑⚑ A DEPENDENCY ORDER OVER FILES NEEDS NAMES RESOLVED TO PATHS, AND THE TRUNCATED FORM
MANUFACTURES CYCLES. `import_edges.module_level` returns top-level names, so every file in a
package reports importing the package — and a reader mapping that to "the package directory"
makes every intra-package pair mutually dependent. A cycle detector fed that data reports the
whole package as one unbreakable knot, which is a fact about the truncation rather than the
tree. The dotted reading exists for exactly this, and its own docstring says so.

⚑⚑ A DOTTED NAME IS A CANDIDATE, NOT A MODULE. `import_edges` says this plainly: `from x
import y` yields both `x.y` and `x`, and only one may be a module — the other is an attribute.
Resolving means TESTING which candidates correspond to files that exist, so a name with no
file is dropped rather than mapped to something plausible.

⚑ AND A NAME OUTSIDE THE REPO RESOLVES TO NOTHING, DELIBERATELY. `os`, `ast`, a third-party
package — none is a file this repo can decompose, so an edge to one is not a blocker and must
not appear. Reporting them would inflate every dependency set with work nobody can do.

⚑ BOTH LAYOUTS ARE TRIED because the repo has both: `substrate/foo.py` for `substrate.foo`,
and `pkg/__init__.py` for `pkg`. Checking only the first would silently drop every package
import; checking only the second would drop every module.
"""

from __future__ import annotations

from mikemol.corpus import import_edges

from substrate import corpus


def path_of(dotted: str) -> str | None:
    """Return the repo-relative file defining `dotted`, or None when none does.

    ⚑ THE MODULE FILE WINS OVER THE PACKAGE FILE. If both `pkg/foo.py` and `pkg/foo/__init__`
    somehow exist, the flat module is what a plain import binds; preferring the package would
    attribute an edge to the wrong file and misplace it in the ordering.
    """
    rel = dotted.replace(".", "/")
    for candidate in (f"{rel}.py", f"{rel}/__init__.py"):
        if (corpus.ROOT / candidate).is_file():
            return candidate
    return None


def imports_of(path: str) -> set[str]:
    """Return the repo files `path` imports at module scope.

    ⚑ MODULE SCOPE ONLY. A deferred import fires when called, so it does not constrain the
    order in which files can be decomposed — folding the two together would over-report
    blocking and stall an ordering that had work available.
    """
    out: set[str] = set()
    for dotted in import_edges.module_level_dotted(str(corpus.ROOT / path)):
        resolved = path_of(dotted)
        if resolved is not None and resolved != path:
            out.add(resolved)
    return out


def graph(paths: list[str]) -> dict[str, set[str]]:
    """Return the module-scope import graph over `paths`, restricted to those paths.

    ⚑⚑ RESTRICTED TO THE POPULATION, because an edge to a file nobody is cleaning is not a
    wait. A graph carrying every resolvable import would make the ordering depend on files
    outside the question being asked, and the answer would change when an unrelated file was
    added to the tree.
    """
    inside = set(paths)
    return {p: {d for d in imports_of(p) if d in inside} for p in paths}
