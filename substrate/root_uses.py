# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What each `corpus.ROOT` use REACHES FOR — the census that decides where the decomposition starts.

    python -m substrate.root_uses FILE_OR_DIR...           # by joined path segment
    python -m substrate.root_uses --bare FILE_OR_DIR...    # the BARE uses, by context

⚑ WHY (2026-09-24). `corpus.ROOT` is read ~330 times across ~150 modules, and the operator read the
count correctly: *"it's not correctly broken down into submodules and a dag of packages."* A module
that joins `ROOT / "scripts" / "x_baseline.txt"` is doing its own I/O on a repo-relative path; the
fix is to split it into a pure core and an edge that reads, one CLUSTER at a time. The cluster is
named by what the use reaches for, so the default mode reports, per use, the FIRST path segment
joined onto ROOT (`"scripts"`, `"agda"`, …) — or `(bare)` when ROOT is passed on unjoined.

⚑ `--bare` EXISTS BECAUSE THE BARE CASE DOMINATED (102 files, measured) and is the layering fault
itself: an interior module choosing the tree. It reports each bare use by CONTEXT — `relative_to`
base, `cwd=` keyword, positional argument of a named call, assignment, return — because each
context names a different repair (a display path, a subprocess boundary, a walker call, a
module-level alias).

⚑ STRUCTURAL, NOT TEXTUAL: `ast` finds `corpus.ROOT` as an Attribute on the name `corpus`. A
segment or callee that is not a plain name/literal is reported as `(computed)` rather than guessed.
"""

from __future__ import annotations

import ast
import collections
import sys
from pathlib import Path

USAGE = "usage: python -m substrate.root_uses [--bare] [--list LABEL] FILE_OR_DIR...\n"
_BARE = "(bare)"
_COMPUTED = "(computed)"
_SUITE = "_selftest.py"

#: Parent node types whose context label does not depend on the node's fields.
_PLAIN: dict[type[ast.AST], str] = {
    ast.Assign: "assigned to a name",
    ast.AnnAssign: "assigned to a name",
    ast.Return: "returned",
}


def _is_root(node: ast.AST) -> bool:
    """Report whether `node` is the expression `corpus.ROOT`."""
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "ROOT"
        and isinstance(node.value, ast.Name)
        and node.value.id == "corpus"
    )


def _segment(parent: ast.AST | None, child: ast.AST) -> str:
    """Return the first path segment joined onto ROOT, when `child` is ROOT's `/` left operand."""
    if not (
        isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div) and parent.left is child
    ):
        return _BARE
    right = parent.right
    if isinstance(right, ast.Constant) and isinstance(right.value, str):
        return right.value.split("/", 1)[0] or _COMPUTED
    return _COMPUTED


def _callee(func: ast.expr) -> str:
    """Return a call's name as written (`f`, `mod.f`, or `.f` for a method), else computed."""
    if isinstance(func, ast.Name):
        return func.id
    if not isinstance(func, ast.Attribute):
        return _COMPUTED
    owner = func.value.id if isinstance(func.value, ast.Name) else ""
    return f"{owner}.{func.attr}"


def _call_context(call: ast.Call) -> str:
    """Name the context of a bare ROOT passed positionally to a call."""
    if isinstance(call.func, ast.Attribute) and call.func.attr == "relative_to":
        return "relative_to(ROOT)"
    return f"arg of {_callee(call.func)}()"


def _context(parent: ast.AST | None, child: ast.AST) -> str:
    """Name the context a BARE `corpus.ROOT` sits in."""
    if isinstance(parent, ast.Call):
        return _call_context(parent)
    if isinstance(parent, ast.keyword):
        return f"{parent.arg}=ROOT"
    if isinstance(parent, ast.BinOp):
        return "ROOT / <computed>" if parent.left is child else "<x> / ROOT"
    if isinstance(parent, ast.Attribute):
        return f"ROOT.{parent.attr}"
    if parent is None:
        return "(module)"
    return _PLAIN.get(type(parent), type(parent).__name__)


def _roots(path: Path) -> list[tuple[ast.AST | None, ast.AST]]:
    """Return `(parent, node)` for every `corpus.ROOT` in `path`; [] when unparseable."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return [(parents.get(node), node) for node in ast.walk(tree) if _is_root(node)]


def uses(path: Path) -> list[str]:
    """Return the segment each `corpus.ROOT` use in `path` reaches for."""
    return [_segment(parent, node) for parent, node in _roots(path)]


def bare_uses(path: Path) -> list[str]:
    """Return the context of each BARE `corpus.ROOT` use in `path`."""
    return [
        _context(parent, node) for parent, node in _roots(path) if _segment(parent, node) == _BARE
    ]


def _files(paths: list[Path]) -> list[Path]:
    """Expand directories to their `.py` files."""
    out: list[Path] = []
    for p in paths:
        out.extend(sorted(p.rglob("*.py")) if p.is_dir() else [p])
    return out


def census(paths: list[Path], *, bare: bool = False) -> dict[str, dict[str, int]]:
    """Return `label -> {file: count}` over every `.py` under `paths`."""
    out: dict[str, dict[str, int]] = collections.defaultdict(dict)
    for f in _files(paths):
        labels = bare_uses(f) if bare else uses(f)
        for label, n in collections.Counter(labels).items():
            out[label][str(f)] = n
    return out


def render(got: dict[str, dict[str, int]]) -> list[str]:
    """Render labels by how many FILES carry each, largest first, suites counted apart."""
    lines: list[str] = []
    # ⚑ sorted on (negated file count, label) tuples: no key lambda, so no inferred `Any`.
    for _neg, label in sorted((-len(files), label) for label, files in got.items()):
        files = got[label]
        suites = sum(1 for f in files if f.endswith(_SUITE))
        lines.append(
            f"{label:<34} {len(files):4d} file(s)  ({suites} suite)  {sum(files.values())} use(s)"
        )
    total = {f for files in got.values() for f in files}
    lines.append(f"\n{len(total)} file(s) in this census")
    return lines


def listing(got: dict[str, dict[str, int]], label: str) -> list[str]:
    """Return the files carrying `label`, with their use counts, largest first."""
    files = got.get(label, {})
    lines = [f"  {n:3d}  {f}" for _neg, f, n in sorted((-n, f, n) for f, n in files.items())]
    lines.append(f"{len(files)} file(s) carry {label!r}")
    return lines


def main(argv: list[str]) -> int:
    """Parse `[--bare] [--list LABEL] PATH...` and print the census or one label's files."""
    args = list(argv)
    label: str | None = None
    if "--list" in args:
        at = args.index("--list")
        if at + 1 >= len(args):
            sys.stderr.write(USAGE)
            return 2
        label = args[at + 1]
        del args[at : at + 2]
    bare = "--bare" in args
    paths = [Path(a) for a in args if a != "--bare"]
    if not paths or not all(p.exists() for p in paths):
        sys.stderr.write(USAGE)
        return 2
    got = census(paths, bare=bare)
    sys.stdout.write("\n".join(listing(got, label) if label else render(got)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
