#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Attribute reads `<Recv>.<leaf>`, with the RECEIVER resolved through the file's own imports.

⚑⚑⚑ THE ORIGIN'S DOTTED FORM WAS DOCUMENTED AND NEVER IMPLEMENTED, AND IT RETURNED A CLEAN ZERO
(Ⓝ68b ⟡attr-misses-the-alias). `scratch/pycodemod.py --attr ratchet_flags.selftest` reports
`0 attribute read(s) in 0 of 1142 file(s)` while the site exists. The origin special-cases only
the `<Recv>.*` spelling; anything else dotted falls through to the LEAF branch and is compared
against `node.attr.value`, which no attribute name can ever equal — `"ratchet_flags.selftest"` is
not an identifier. So the mode does not over- or under-report the dotted question: it cannot ask
it, and says zero instead of saying so.

⚑⚑ A FALSE ZERO GETS BANKED WHERE A FALSE FINDING GETS ARGUED WITH, and this toolkit DELETES on
its censuses (`--dead`). A fact about the METHOD reported as a fact about the SUBSTRATE is the
recurring defect here: `--calls emit` reporting one OTLP emitter while the second was spelled
`_emit_one`; `--importers corpus` reporting zero for a module with twenty-six importers. This is
the third instance of the same shape and the second in the same toolkit.

⚑ THE RECEIVER IS RESOLVED, NOT MATCHED AS TEXT, and that is the difference from `scan()`'s dotted
target. `scan` documents itself as SYNTACTIC — `--calls store.connect` answers "spelled this way",
so `import store as _store` is deliberately a different key. That is right for a receiver which
may be any expression. Here the operand names a MODULE, so the binding forms are enumerable and
the resolution is exact: `import pkg.mod`, `import pkg.mod as m`, `from pkg import mod`,
`from pkg import mod as m` and `from . import mod` all put the module under a local name, and
every one of those names is read off the file's own import statements. The query therefore answers
"reaches THIS module", not "is spelled this way".

⚑ THE LEAF-ONLY FORM IS UNCHANGED AND STAYS RECEIVER-BLIND. `--attr waiting` asks which sites read
a FIELD, whose receiver is an arbitrary expression and is not decidable. The origin's docstring is
right that the honest move there is to over-report with context rather than filter by a guess. The
dotted form is a different question, not a tightening of that one.

⚑⚑ WHAT REMAINS INVISIBLE IS NAMED RATHER THAN COUNTED AS ZERO. Three shapes cannot be resolved
from one file's syntax, and `unresolved` reports each as itself:

  * a RE-EXPORT CHAIN. `ratchet.py` does `from ratchet_flags import *`; a consumer then reads
    `ratchet.selftest` and no import statement in that consumer names `ratchet_flags` at all.
    This reader attributes the site to `ratchet`, which is what the consumer actually wrote, and
    cannot follow the chain to the module that defines the name.
  * a DYNAMIC import. `importlib.import_module(name)` binds at runtime; the name may not be a
    literal, and no static reader can resolve it.
  * a RELATIVE import of an unknown package. `from . import mod` binds `mod` locally, so a query
    for the BARE receiver `mod` resolves; a query for the DOTTED `pkg.mod` cannot confirm that
    this file's package is `pkg`.

A caller that gets zero and a non-empty `unresolved` list has been told the difference between
"none" and "could not see" — which is the whole defect being repaired, and reintroducing it one
layer down would be the same error wearing the fix's clothes.

⚑ PROMOTED AS A READER, NOT AS A PATCH TO THE ORIGIN (⟡promote-pycodemod, the route
`module_importers` already took for the `--importers` half of this same defect). The origin file
carries ~2145 ruff findings and the per-file gate has no partial-credit path, so no edit to it can
land; the gate's own refusal text names extraction as the move. The walk here is `ast`, the
population is `substrate.corpus`, and nothing here holds state.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Iterable

# How the receiver came to be bound in the file that reads off it. ⚑ NAMED ONCE: the resolver, the
# render and the cases cite these rather than respelling the strings.
PLAIN, ALIAS, FROM, FROM_AS, RELATIVE, UNBOUND = (
    "import",
    "import-as",
    "from",
    "from-as",
    "relative",
    "unbound",
)

# The binding forms this reader resolves, in the order the module docstring names them. ⚑ THE
# ROSTER IS DATA so a case can pin the PROPERTY — *every documented form resolves* — rather than a
# named victim file, which expires the moment the tree moves.
BINDING_FORMS = (PLAIN, ALIAS, FROM, FROM_AS, RELATIVE)

# Shapes no single-file static read can resolve; reported as themselves, never folded into a zero.
CHAIN, DYNAMIC, RELATIVE_PKG = "re-export-chain", "dynamic-import", "relative-package"


class Read(NamedTuple):
    """One attribute read, and how its receiver came to be bound."""

    path: str
    line: int
    recv: str
    attr: str
    form: str

    @property
    def text(self) -> str:
        """Return the read as it is written at the site."""
        return f"{self.recv}.{self.attr}"


class Query(NamedTuple):
    """A parsed `--attr` operand: which receiver, which leaf.

    ⚑ THE THREE FORMS ARE ONE PREDICATE, and keeping them as three branches is how the dotted one
    went missing. `leaf is None` means `<Recv>.*` (every attribute off the receiver); `recv is
    None` means the receiver-blind leaf query; both set is the dotted form that returned zero.
    """

    recv: str | None
    leaf: str | None

    @property
    def wants_receiver(self) -> bool:
        """Return whether this query constrains the receiver."""
        return self.recv is not None


def parse(operand: str) -> Query:
    """Return the `Query` an `--attr` operand denotes.

    ⚑ `Recv.*` AND `Recv.leaf` DIFFER ONLY IN THE LEAF, which is why one `rsplit` serves both. The
    origin tested `endswith(".*")` and had no branch at all for the other dotted spelling.
    """
    if "." not in operand:
        return Query(recv=None, leaf=operand)
    recv, leaf = operand.rsplit(".", 1)
    return Query(recv=recv, leaf=None if leaf == "*" else leaf)


def _plain_binds(node: ast.Import, module: str) -> list[tuple[str, str]]:
    """Return `(local name, form)` for each `import <module>` / `import <module> as m`."""
    return [
        ((a.asname, ALIAS) if a.asname else (a.name, PLAIN)) for a in node.names if a.name == module
    ]


def _from_binds(node: ast.ImportFrom, module: str, package: str | None) -> list[tuple[str, str]]:
    """Return `(local name, form)` for each `from … import <module>` binding.

    ⚑ `from pkg.mod import leaf` BINDS THE LEAF, NOT THE MODULE, so it yields no receiver — the
    consumer never writes `mod.leaf` and reporting one would be a false finding.
    """
    short = module.rsplit(".", 1)[-1]
    if node.level:
        # ⚑ `from . import mod` BINDS `mod` LOCALLY even though the package is unknown, so the
        # BARE receiver resolves here. Only the dotted query needs the package, and that case is
        # reported by `unresolved` rather than guessed.
        return [(a.asname or a.name, RELATIVE) for a in node.names if a.name == short]
    if node.module in (package, module.rsplit(".", 1)[0]):
        return [
            (a.asname or a.name, FROM_AS if a.asname else FROM)
            for a in node.names
            if a.name == short
        ]
    return []


def _module_names(node: ast.AST, module: str, package: str | None) -> list[tuple[str, str]]:
    """Return `(local name, form)` for every binding of `module` this node creates."""
    if isinstance(node, ast.Import):
        return _plain_binds(node, module)
    if isinstance(node, ast.ImportFrom):
        return _from_binds(node, module, package)
    return []


def binds(tree: ast.AST, recv: str) -> dict[str, str]:
    """Return `{local name: binding form}` for every name in `tree` that refers to `recv`.

    ⚑ THE BARE RECEIVER ALWAYS BINDS ITSELF. A receiver naming no importable module — `self`, a
    `Row` class, a local variable — must still match its own spelling, or widening the dotted form
    into a resolver would DELETE the answers the origin's `Recv.*` already gave correctly.
    """
    package = recv.rsplit(".", 1)[0] if "." in recv else None
    found = {
        name: form for node in ast.walk(tree) for name, form in _module_names(node, recv, package)
    }
    # `import pkg.mod` leaves the file writing `pkg.mod.leaf`, whose receiver is itself a dotted
    # path; `_recv_text` renders it, so the spelling must be a key here too.
    found.setdefault(recv, UNBOUND)
    return found


def _recv_text(node: ast.expr) -> str | None:
    """Return the receiver's dotted source text, or None if it is not a plain name path.

    ⚑ AN ARBITRARY RECEIVER EXPRESSION IS NOT A NAME, and returning something for `f(x).leaf`
    would put back the guess that the leaf-only form deliberately refuses to make.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        inner = _recv_text(node.value)
        return f"{inner}.{node.attr}" if inner is not None else None
    return None


def reads(query: Query, tree: ast.AST, label: str) -> list[Read]:
    """Return every attribute read in `tree` matching `query`."""
    known = binds(tree, query.recv) if query.recv is not None else {}
    out: list[Read] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if query.leaf is not None and node.attr != query.leaf:
            continue
        text = _recv_text(node.value)
        if query.recv is None:
            # The receiver-blind leaf form: report the read with whatever receiver it has.
            out.append(
                Read(
                    path=label,
                    line=node.lineno,
                    recv=text or "<expr>",
                    attr=node.attr,
                    form=UNBOUND,
                )
            )
        elif text is not None and text in known:
            out.append(
                Read(path=label, line=node.lineno, recv=text, attr=node.attr, form=known[text])
            )
    return out


def _parsed(files: Iterable[tuple[Path, str]]) -> list[tuple[str, ast.AST]]:
    """Return `(label, tree)` for every file that parses.

    ⚑ ONE UNPARSEABLE FILE MUST NOT TAKE THE CENSUS DOWN — it would report nothing about the
    thousand that parse, a far larger error than the one file it skips.
    """
    out: list[tuple[str, ast.AST]] = []
    for path, label in files:
        try:
            out.append(
                (
                    label,
                    ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=label),
                )
            )
        except (OSError, SyntaxError, ValueError):
            continue
    return out


def sites(operand: str, files: Iterable[tuple[Path, str]]) -> tuple[Read, ...]:
    """Return every attribute read matching `operand` across `files`."""
    query = parse(operand)
    return tuple(sorted(r for label, tree in _parsed(files) for r in reads(query, tree, label)))


def _blind_shapes(node: ast.AST, label: str, query: Query) -> list[str]:
    """Return the unresolvable shapes this node exhibits, as reader-facing lines."""
    recv = query.recv or ""
    short = recv.rsplit(".", 1)[-1]
    out: list[str] = []
    if isinstance(node, ast.ImportFrom):
        if node.level and "." in recv and any(a.name == short for a in node.names):
            out.append(
                f"{RELATIVE_PKG}: {label}:{node.lineno} binds `{short}` from an unknown package"
            )
        if (
            any(a.name == "*" for a in node.names)
            and (node.module or "").rsplit(".", 1)[-1] == short
        ):
            out.append(
                f"{CHAIN}: {label}:{node.lineno} re-exports `{short}` with a star; "
                f"consumers reach it under THIS module's name"
            )
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "import_module"
    ):
        out.append(f"{DYNAMIC}: {label}:{node.lineno} binds a module at runtime")
    return out


def unresolved(operand: str, files: Iterable[tuple[Path, str]]) -> tuple[str, ...]:
    """Return the shapes in `files` that could hide a read this reader cannot resolve.

    ⚑⚑ THIS IS THE HALF THAT MAKES A ZERO HONEST. A count alone cannot distinguish *none* from
    *could not see*, and that collapse IS the defect this module repairs — so re-introducing it
    one layer down would be the same error wearing the fix's clothes. Each shape is named with the
    file that carries it, so a reader gets a lead rather than a caveat.
    """
    query = parse(operand)
    if query.recv is None:
        return ()
    return tuple(
        sorted(
            {
                line
                for label, tree in _parsed(files)
                for node in ast.walk(tree)
                for line in _blind_shapes(node, label, query)
            }
        )
    )


def render(operand: str, found: tuple[Read, ...], scanned: int, blind: tuple[str, ...] = ()) -> str:
    """Return the census — one line per read, the denominator, and what stayed invisible.

    ⚑⚑ THE DENOMINATOR IS PRINTED EVEN WHEN THE ANSWER IS ZERO. `0 reads` and `0 reads of 1144
    files scanned` are the same finding; only the second lets a reader see the scan HAPPENED.
    """
    lines = [f"  {r.form:<9} {r.path}:{r.line}  {r.text}" for r in found]
    hit = len({r.path for r in found})
    lines.append(f"{operand}: {len(found)} attribute read(s) in {hit} of {scanned} file(s)")
    if blind:
        lines.append(
            f"   ⚑ {len(blind)} shape(s) this reader CANNOT resolve — a zero above is "
            f"not yet an absence:"
        )
        lines.extend(f"     {b}" for b in blind)
    return "\n".join(lines) + "\n"


def population(root: Path | None = None) -> tuple[tuple[Path, str], ...]:
    """Return the corpus to scan, as `(path, best-effort relative label)` pairs.

    ⚑⚑⚑ THE LABEL IS BEST-EFFORT BECAUSE THE WALK AND THE ROOT CAN LEGITIMATELY DIVERGE
    (gate-G245, reported by summit-74 from a borrowing checkout). `corpus.resolve_root` resolves
    CWD FIRST — deliberately, because this tooling is symlinked into other trees and a peer once
    nearly recorded substrate's census as their own. So from another repo the walk correctly
    yields THAT repo's files, and computing `relative_to` against substrate's root then raised
    `ValueError` and killed the run.

    ⚑⚑ BOTH FUNCTIONS WERE RIGHT AND THEIR COMPOSITION WAS NOT, which is why the fix is here
    rather than in either of them. Narrowing `resolve_root` would reintroduce the wrong-repo
    answer it exists to prevent; forcing the walk back under substrate's root would make the tool
    unable to answer about a borrower's own tree at all.

    ⚑ A PATH OUTSIDE THE ROOT KEEPS ITS ABSOLUTE FORM rather than being dropped. Dropping it
    would silently shrink the population — the census-green shape — and an absolute label is
    longer but never wrong.
    """
    where = root if root is not None else corpus.ROOT
    return tuple((Path(p), _label(Path(p), where)) for p in corpus.py_files(root=where))


def _label(path: Path, root: Path) -> str:
    """Return `path` relative to `root`, or its absolute form when it lies outside."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main(argv: list[str]) -> int:
    """Print the attribute reads matching the operand named on the command line."""
    if len(argv) != 1:
        sys.stderr.write("usage: attr_reads.py <leaf>|<Recv>.<leaf>|<Recv>.*\n")
        return 2
    files = population()
    sys.stdout.write(render(argv[0], sites(argv[0], files), len(files), unresolved(argv[0], files)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
