#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Infer a module's typing interface FROM ITS SOURCE — the engine three readers sit on.

⚑⚑⚑ A `.pyi` IN THIS TREE IS AUTHORED, AND THAT IS THE DEFECT CLASS. Someone reads a module
and writes a claim about it, so the claim can contradict its subject. Both instances are
recorded in this repo rather than hypothesised: the FIRST stub written here declared
`main(argv: list[str]) -> int` for a `main()` taking no parameters, and `stubs/panflute`
declared `load`'s parameter `source` where the runtime spells it `input_stream` — a live
latent break that type-checked clean and would have raised `TypeError` on any keyword call.

⚑⚑ A DERIVED INTERFACE CANNOT CONTRADICT WHAT IT WAS DERIVED FROM. That is the whole
reframing: for a repo-local module the `.pyi` becomes a GENERATED VIEW with a drift gate —
`agda/Flat.mk` and the sql census already have this shape — and the authored remainder shrinks
to what a generator provably cannot state.

⚑⚑⚑ THE GENERATOR IS `stubgen`, WHICH SHIPS WITH MYPY AND IS ALREADY A DEPENDENCY. This
module does NOT reimplement it, and the reuse-search that established that is the point: a
second stub generator would be exactly the reinvention this repo's standing rule exists to
stop. What is measured and kept below is the part `stubgen` does NOT answer — *what did the
source actually state, symbol by symbol* — because that residue is the statistic all three
readers are computed from, and no `.pyi` (generated or authored) can carry it: a stub records
the type it landed on, never whether that type was READ or INVENTED.

⚑⚑ INFERENCE HAS A FLOOR AND THIS MODULE STATES IT RATHER THAN PAPERING OVER IT. An
unannotated parameter is unannotated in the derived stub too — `stubgen` emits `Incomplete`
(an alias for `Any`), which under this repo's `disallow_any_expr` bar is the weakest possible
claim. Inference PROPAGATES the types a source states; it does not MANUFACTURE types the
source never stated. So a derived stub is exactly as strong as its module's annotations and no
stronger.

⚑⚑⚑ AND THAT FLOOR IS NOT A LIMITATION TO APOLOGISE FOR — IT IS THE THIRD READER. The gap
between what inference CAN state and what the source DOES state is the under-annotation
census, which is precisely the half `check_stub_authority`'s own docstring says `stubtest` can
never verify: *"it cannot verify a type the source never states."* Measuring the floor is what
turns it from an excuse into a work queue. A module at 100% annotation derives a stub with no
`Incomplete` in it at all, and for that module the authored remainder is empty.

⚑ SYMBOL-LEVEL, NOT FILE-LEVEL, BECAUSE A FILE-LEVEL RATIO CANNOT BE ACTED ON. "This module is
60% annotated" names no work; "these four parameters are unannotated, at these lines" is a
paydown list. The per-file ratio is a derived view of the symbol rows, never the primary datum.

⚑ WHAT THIS READS AND WHAT IT DELIBERATELY DOES NOT. It reads annotations AS WRITTEN, via
`ast` — the same thing a checker starts from — and does NOT run mypy's inference engine over
bodies. That is a deliberate scope: a body-inferred return type is a fact about the current
implementation, not a declared contract, and promoting one into a published interface would
manufacture exactly the claim this module exists to stop manufacturing. `stubgen --no-import`
makes the same choice for the same reason.

⚑ AN UNANNOTATED `self`/`cls` IS NOT A FINDING. It is never annotated by anyone, so counting
it would inflate every class's debt by its method count and make the ranking a proxy for class
size. Excluded structurally, not by a threshold.

Usage: iface_infer.py [--selftest]
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# ⚑ THE NAMES A GENERATOR EMITS WHEN IT HAS NOTHING TO SAY. `stubgen` writes `Incomplete`
# (imported from `_typeshed`); mypy spells the same hole `Any`. Both mean "no claim", and a
# reader that knew only one spelling would report a fully-hollow stub as fully typed — the
# census-keyed-on-one-spelling defect this repo has already recorded twice.
HOLLOW = frozenset({"Incomplete", "Any"})

# ⚑ Never a finding: no one annotates these, so counting them makes debt track class size.
IMPLICIT = frozenset({"self", "cls"})


@dataclass(frozen=True, slots=True)
class Param:
    """One parameter of one function, and whether the source stated its type."""

    name: str
    annotation: str | None

    @property
    def stated(self) -> bool:
        """Report whether the source states a type inference could propagate."""
        return self.annotation is not None and self.annotation not in HOLLOW


@dataclass(frozen=True, slots=True)
class Symbol:
    """One inferable symbol: what the source states about it, and where it is.

    ⚑ `returns` IS `None` FOR A NON-FUNCTION, which is why `stated_slots` counts it only
    when the symbol is a function. Collapsing "has no return" into "return unannotated"
    would make every module constant read as debt.
    """

    name: str
    kind: str
    lineno: int
    params: tuple[Param, ...]
    returns: str | None
    is_function: bool

    @property
    def slots(self) -> int:
        """Return how many annotation slots this symbol has."""
        return len(self.params) + (1 if self.is_function else 0)

    @property
    def stated_slots(self) -> int:
        """Return how many of those slots the source actually states."""
        got = sum(1 for p in self.params if p.stated)
        if self.is_function and self.returns is not None and self.returns not in HOLLOW:
            got += 1
        return got

    @property
    def complete(self) -> bool:
        """Report whether inference can state this symbol's whole interface.

        ⚑ A ZERO-SLOT SYMBOL IS COMPLETE, NOT UNKNOWN. `def f(): ...` with a stated return
        has nothing left to state; a bare class likewise. Reporting it as incomplete would
        make the census fire on symbols with no work available.
        """
        return self.stated_slots == self.slots


@dataclass(frozen=True, slots=True)
class Interface:
    """A module's inferred interface: every public symbol, and the floor beneath it."""

    module: str
    symbols: tuple[Symbol, ...]

    @property
    def slots(self) -> int:
        """Return the module's total annotation slots."""
        return sum(s.slots for s in self.symbols)

    @property
    def stated(self) -> int:
        """Return how many slots the source states."""
        return sum(s.stated_slots for s in self.symbols)

    @property
    def hollow(self) -> tuple[Symbol, ...]:
        """Return the symbols a derived stub could not fully state — the floor, itemized."""
        return tuple(s for s in self.symbols if not s.complete)

    @property
    def ratio(self) -> float:
        """Return the stated fraction; 1.0 for a module with no slots at all.

        ⚑ AN EMPTY MODULE IS NOT 0% ANNOTATED. Dividing by zero slots and reporting 0.0
        would rank every trivial module as maximally indebted, which is the ranking
        inverted. No slots means no debt.
        """
        return 1.0 if self.slots == 0 else self.stated / self.slots


def _annotation(node: ast.expr | None) -> str | None:
    """Render an annotation as source text, or None when there is none."""
    return None if node is None else ast.unparse(node)


def _params(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[Param, ...]:
    """Collect every parameter of a function, in declaration order.

    ⚑ EVERY ARITY KIND, NOT JUST `args`. Positional-only, keyword-only, `*args` and
    `**kwargs` each carry their own annotation slot, and a reader that walked only
    `node.args.args` would silently under-count a module using modern signatures —
    reporting it as better annotated than it is, which is the dangerous direction.
    """
    a = fn.args
    named = [
        Param(arg.arg, _annotation(arg.annotation))
        for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs]
        if arg.arg not in IMPLICIT
    ]
    stars = [
        Param(star.arg, _annotation(star.annotation))
        for star in (a.vararg, a.kwarg)
        if star is not None
    ]
    return tuple(named + stars)


def _public(name: str) -> bool:
    """Report whether a name is part of the interface a stub would declare.

    ⚑ A DUNDER IS INTERFACE, A SINGLE UNDERSCORE IS NOT. `__init__`'s signature is exactly
    what a caller writes against, so excluding every underscore name would drop the one
    method most worth typing.
    """
    return not name.startswith("_") or (name.startswith("__") and name.endswith("__"))


def _class_symbols(node: ast.ClassDef) -> list[Symbol]:
    """Return a public class and each public method it declares."""
    out = [Symbol(node.name, "class", node.lineno, (), None, is_function=False)]
    out += [
        Symbol(
            f"{node.name}.{sub.name}",
            "method",
            sub.lineno,
            _params(sub),
            _annotation(sub.returns),
            is_function=True,
        )
        for sub in node.body
        if isinstance(sub, ast.FunctionDef | ast.AsyncFunctionDef) and _public(sub.name)
    ]
    return out


def _assign_symbols(node: ast.Assign) -> list[Symbol]:
    """Return a symbol for each public bare-assignment target."""
    return [
        Symbol(t.id, "assign", node.lineno, (), None, is_function=False)
        for t in node.targets
        if isinstance(t, ast.Name) and _public(t.id)
    ]


def symbols_of(src: str) -> tuple[Symbol, ...]:
    """Infer every public symbol of a module from its source text.

    ⚑ TOP-LEVEL AND ONE CLASS LEVEL DOWN, WHICH IS WHAT A STUB DECLARES. A nested function
    is not interface — it cannot be imported or called — so including it would count debt
    against symbols no derived stub would ever carry.
    """
    out: list[Symbol] = []
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and _public(node.name):
            out.append(
                Symbol(
                    node.name,
                    "function",
                    node.lineno,
                    _params(node),
                    _annotation(node.returns),
                    is_function=True,
                )
            )
        elif isinstance(node, ast.ClassDef) and _public(node.name):
            out += _class_symbols(node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if _public(node.target.id):
                out.append(
                    Symbol(
                        node.target.id,
                        "assign",
                        node.lineno,
                        (),
                        _annotation(node.annotation),
                        is_function=False,
                    )
                )
        elif isinstance(node, ast.Assign):
            out += _assign_symbols(node)
    return tuple(out)


def interface_of_src(src: str, module: str = "<src>") -> Interface:
    """Infer an interface from source TEXT — the pure core `interface_of` wraps."""
    return Interface(module, symbols_of(src))


def interface_of(path: Path) -> Interface | None:
    """Infer one module's interface, or None when it cannot be parsed.

    ⚑ UNPARSEABLE IS `None`, NEVER AN EMPTY INTERFACE. A file the reader could not read and
    a file with no public symbols are opposite facts, and rendering them identically is the
    `census-green-is-a-fact-about-the-census` shape: an empty result would enter the census
    as a fully-annotated module and IMPROVE the score.
    """
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        return interface_of_src(src, path.stem)
    except SyntaxError:
        return None


def declared_names(stub_src: str) -> frozenset[str]:
    """Return the names a `.pyi` declares — the narrowing's numerator.

    ⚑ THIS IS HOW A NARROWING IS MEASURED, and it is a SET question rather than a count.
    Our stub over an already-typed upstream states a subset of that upstream's surface; the
    cost of the narrowing is exactly the names the upstream has and ours does not, which a
    count cannot name and therefore cannot pay down.
    """
    return frozenset(s.name.split(".")[0] for s in symbols_of(stub_src))


def narrowing(upstream_src: str, stub_src: str) -> tuple[str, ...]:
    """Return the upstream names our stub does not declare, sorted.

    ⚑ THE DELTA IS THE FIGURE THE networkx RETREAT WAS DECIDED WITHOUT. "This repo never
    uses them" is a claim about today's call sites; the names below are what a caller
    CANNOT reach while the narrowing stands. That turns a hunch into a measured cost.
    """
    return tuple(sorted(declared_names(upstream_src) - declared_names(stub_src)))
