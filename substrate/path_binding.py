# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve a module-level name that holds a filesystem path, one hop from its use.

⚑ THE INSERT NAMES A VARIABLE, AND THE VARIABLE IS WHERE THE PATH IS. A reader that
inspects only the call node sees `sys.path.insert(0, HERE)` and finds no literal, so it
reports the site unattributable — 157 of 492 inserts, over two thirds of the population
being ranked. The path is one binding away: `HERE = os.path.dirname(os.path.abspath(
__file__))` at module level, measured at 111 bindings across the tooling trees.

⚑⚑ AND THE READER THIS SERVES ALREADY PAID FOR THIS ONCE, AT THE LITERAL LAYER. Its
`_target` docstring records reporting 291 of 491 unattributable and every candidate as
retiring zero, because the `__file__` idiom carries no string constant — "a fact about
the METHOD presented as a ranking of the SUBSTRATE". Resolving the idiom inline fixed
the direct spelling and left the INDIRECT one, so the same defect survived one layer
out. A resolver that stops at the call node cannot see a name.

⚑⚑⚑ WHAT THIS DELIBERATELY WILL NOT DO IS GUESS. A name bound from a parameter, a
conditional, or another module is NOT resolved and NOT attributed — the caller gets
None and reports the site as unknown, exactly as before. A well-formed wrong
attribution reads as a measurement, which is worse than an admitted gap: the gap is
visible in the count, and the wrong answer is not.
"""

from __future__ import annotations

import ast

# The attribute chains that mean "a directory derived from this file's location".
_LOCATOR_ATTRS = frozenset({"dirname", "abspath", "realpath", "join", "parent"})


def _is_file_derived(node: ast.expr) -> bool:
    """Report whether this expression derives from `__file__`."""
    return any(isinstance(inner, ast.Name) and inner.id == "__file__" for inner in ast.walk(node))


def _dirname_depth(node: ast.expr) -> int:
    """Count how many `dirname`/`parent` steps walk up from the file."""
    return sum(
        1
        for inner in ast.walk(node)
        if isinstance(inner, ast.Attribute) and inner.attr in ("dirname", "parent")
    )


def file_derived_names(tree: ast.Module) -> dict[str, int]:
    """Return `{name: walk-up depth}` for module-level names bound from `__file__`.

    Depth 1 is the file's own directory (`dirname(abspath(__file__))`), 2 its parent,
    and so on. ⚑ ONLY MODULE-LEVEL ASSIGNMENTS ARE READ. A name rebound inside a
    function is not a stable fact about the module, and treating it as one would
    attribute an insert to whichever branch happened to be parsed last.
    """
    out: dict[str, int] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if _is_file_derived(node.value):
            out[target.id] = _dirname_depth(node.value)
        elif isinstance(node.value, ast.Name) and node.value.id in out:
            # `ROOT = HERE` — an alias carries its source's depth.
            out[target.id] = out[node.value.id]
        else:
            # ⚑ `ROOT = HERE.parent` — A WALK OFF AN ALREADY-BOUND NAME, AND MISSING IT
            # LEFT A WHOLE CLUSTER UNATTRIBUTED. The alias branch above accepts only a
            # bare `ast.Name`, so a pathlib walk that climbs from a bound name bound
            # nothing: measured across ~36 `scratch/eliza/tests/*` files spelling
            # `HERE = Path(__file__).resolve().parent` then `ROOT = HERE.parent`, which
            # is roughly half the sites this resolver still could not name. The depth is
            # the source's plus however many steps this expression climbs.
            base = _rooted_in(node.value, out)
            if base is not None:
                out[target.id] = out[base] + _dirname_depth(node.value)
    return out


def _rooted_in(node: ast.expr, known: dict[str, int]) -> str | None:
    """Return the already-bound name this expression walks from, if any.

    ⚑ ONLY A NAME ALREADY PROVEN FILE-DERIVED COUNTS. Walking off an arbitrary name
    would attribute a path built from configuration or an argument as though it were
    relative to this file, which is the well-formed wrong attribution this module
    exists to refuse.
    """
    for inner in ast.walk(node):
        if isinstance(inner, ast.Name) and inner.id in known:
            return inner.id
    return None


def resolve_arg(arg: ast.expr, derived: dict[str, int]) -> int | None:
    """Return the walk-up depth an argument names, or None when it is not resolvable.

    ⚑ A `join(HERE, "..")` RAISES THE DEPTH, and reading it as `HERE` would attribute a
    parent-directory insert to the file's own directory. Those are two different
    directories, and a drain plan built on the wrong one moves the wrong module.
    """
    if isinstance(arg, ast.Name):
        return derived.get(arg.id)
    if not _is_file_derived(arg):
        # A name-bearing expression like `os.path.join(HERE, "..")`.
        names = [n.id for n in ast.walk(arg) if isinstance(n, ast.Name)]
        known = [derived[n] for n in names if n in derived]
        if not known:
            return None
        ups = sum(
            1 for inner in ast.walk(arg) if isinstance(inner, ast.Constant) and inner.value == ".."
        )
        return known[0] + ups
    return _dirname_depth(arg)
