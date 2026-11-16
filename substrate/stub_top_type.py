#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read which bare `object` annotations in a `.pyi` are DEBT and which are DECISIONS.

⚑⚑⚑ A DECISION AND AN INABILITY LOOK IDENTICAL WHEN BOTH ARE SPELLED `object`, and that
collision is the whole subject of this module. `stubs/agda_lex.pyi` declares
`HEADER: _HeaderLike` — a two-member Protocol — because the runtime value is a duck-typed
stand-in whose `.search` does not return a `re.Match`. That is a genuine boundary, and it is
LEGIBLE only because its author declined the lazy spelling. Four slots in the same file were
spelled `object` while their assignments were `re.compile(<str>)`, which states the type as
plainly as a literal does. Nothing in the text distinguished the judgement from the shrug.

⚑⚑⚑ AND `object` IS THE TOP TYPE, SO `stubtest` CANNOT CONTRADICT IT. Every runtime value
inhabits `object`, so the gate's green on such a slot is a fact about what `object` ADMITS —
`census-green-is-a-fact-about-the-census`, one annotation wide. Strengthening a slot is the
first moment it becomes capable of being wrong, which is what makes it worth checking; a slot
that cannot fail is not being verified by the thing that passes it.

⚑⚑⚑ THE DISCRIMINATOR IS NOT A KEYWORD, A MARKER, OR A LINE COUNT — IT IS WHETHER THE
ASSIGNMENT BOTTOMS OUT. `substrate.iface_construct` evaluates a module-level assignment's own
constructor and reports each slot as COMPUTED (with a `file:line` witness) or UNRESOLVED. Run
against `scratch/agda_lex.py` it computes sixteen assignments and leaves exactly one
unresolved: `HEADER`. **The author's refusal of the top type and the reader's inability to
resolve the slot pick out the same name, independently.** So the rule does not need a new
declaration for authors to maintain — the evidence is already in the source.

⚑⚑ WHICH IS WHY THIS DOES NOT ADD A `⟡` MARKER, AND THE TEMPTATION TO WAS THE FIRST DESIGN.
A candidate rule ran: *a bare `object` must carry a stated reason.* That makes every honest
slot pay a documentation tax, and — worse — it is satisfiable by writing prose, so the check
becomes "did someone type a sentence" rather than "is this derivable". A marker is the right
mechanism for a DECLINED SURFACE (`stub_declines`, where the fact is editorial and nothing can
compute it) and the wrong one here, where the fact is mechanical.

⚑⚑ THE VERDICT IS THEREFORE ONE-SIDED, AND THE DIRECTION IS THE CLAIM. A COMPUTED slot spelled
`object` is DEBT — the derivation is available and the stub declined to state it, and reporting
it costs a reader nothing to check. An UNRESOLVED slot spelled `object` is UNDERIVABLE and is
NOT reported: the reader could not settle it, and a reader's stopping point is a fact about the
READER, never proof the slot has no type. Asserting the converse would turn every gap in
`iface_construct` into a false accusation against a stub.

⚑ SO THIS ANSWERS A NARROWER QUESTION THAN "IS THIS `object` DELIBERATE", AND SAYS SO. It
cannot read intent. It reports the slots where intent is not needed, because the source already
states the answer — which is exactly the population a gate may act on.

⚑⚑ AND IT DELIBERATELY DOES NOT REACH FUNCTION RETURNS, THOUGH THE SAME ARGUMENT APPLIES
THERE. `iface_construct` covers module-level ASSIGNMENTS only; the function-slot reader is
`iface_dataflow`, which on one live module in this tree EXITS 124 at 600s. A check that
sometimes times out reports a machine fact as a stub fact, which is the collapse
`check_stub_authority.classify` exists to refuse. Returns are owed work, named here rather than
half-covered: `tsdbprobe.query` and its three siblings are one-line passthroughs of a
`json.loads` body, so they are honestly `object` and would need no repair anyway.

⚑ WIDENING IS NOT DEBT, AND A DERIVATION IS NOT AUTOMATICALLY THE CONTRACT. `tsdbprobe`'s
`KNOWN_PRODUCERS` derives as a POSITIONAL `tuple[tuple[str, str], tuple[str, str],
tuple[str, str]]` — three entries, because the literal holds three today — while the stub
states the variadic `tuple[tuple[str, str], ...]`. The stub is BETTER: arity is not part of
that constant's contract, every consumer iterates it, and matching the derivation would break
on the next producer added. This module reports only the TOP TYPE, so a deliberate widening is
outside its subject by construction rather than by an exemption someone has to maintain.

⚑⚑ THIS IS A READER, NOT A WIRED GATE, AND THAT IS DELIBERATE. The pre-commit hook is red
tree-wide, and adding a gate to a red surface makes a new finding indistinguishable from the
standing ones — the operator's call, not this module's. `--check` gives the exit code a gate
would use, so wiring it later is one line in the hook rather than a rewrite here.

Usage: stub_top_type.py <stub.pyi> <module.py> [--check] | --selftest
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import iface_construct

# ⚑ THE SPELLINGS OF THE TOP TYPE. `builtins.object` is the qualified form a stub may use when
# it imports `builtins`; both denote the same type, and a check that saw only the bare name
# would report a fact about its own pattern. `typing.Any` is NOT here — it is a different
# claim (unchecked, not "some value"), it is already refused tree-wide by
# `disallow_any_explicit`, and conflating the two would duplicate a flag that already fires.
_TOP = frozenset({"object", "builtins.object"})

# ⚑ THE STATUS `iface_construct` PRINTS FOR A SLOT IT SETTLED. Read from its own vocabulary
# rather than restated as a bare string at each use, so a rename there is one edit here.
_COMPUTED = "COMPUTED"


@dataclass(frozen=True, slots=True)
class Slot:
    """One module-level name a stub annotates, and how the stub spelled it."""

    name: str
    annotation: str
    lineno: int

    @property
    def is_top(self) -> bool:
        """True when this slot is spelled with the top type and asserts nothing."""
        return self.annotation in _TOP


@dataclass(frozen=True, slots=True)
class Finding:
    """One `object` slot the module's own source already determines.

    ⚑ `witness` IS A `file:line`, NOT A VERDICT. The whole argument for calling this debt is
    that a reader can go and look; a finding that says "derivable" without saying WHERE is
    asking to be trusted, which is what the top type was already doing.
    """

    name: str
    stub_line: int
    derived: str
    witness: str


def _annotation_text(node: ast.expr) -> str:
    """Return the source spelling of an annotation expression."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_annotation_text(node.value)}.{node.attr}"
    return ast.unparse(node)


def slots(src: str) -> tuple[Slot, ...]:
    """Return the module-level annotated names a stub declares.

    ⚑ MODULE LEVEL ONLY, MATCHING THE EVIDENCE. `iface_construct` reads module-level
    assignments; a class attribute has no corresponding derivation here, so including one would
    produce a slot this module can never resolve and must always stay silent about — an entry
    that looks like coverage and is not.
    """
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return ()
    return tuple(
        Slot(node.target.id, _annotation_text(node.annotation), node.lineno)
        for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    )


def top_slots(src: str) -> tuple[Slot, ...]:
    """Return only the slots a stub spelled with the top type."""
    return tuple(s for s in slots(src) if s.is_top)


def findings(stub_src: str, derived: dict[str, tuple[str, str]]) -> tuple[Finding, ...]:
    """Return the `object` slots whose type the module's source already determines.

    `derived` maps a name to its `(type, witness)` as COMPUTED by `iface_construct`. A name
    ABSENT from that mapping did not bottom out and is deliberately not reported — see this
    module's docstring for why the verdict is one-sided.
    """
    return tuple(
        Finding(s.name, s.lineno, got[0], got[1])
        for s in top_slots(stub_src)
        if (got := derived.get(s.name)) is not None
    )


def derived_of(module_path: str) -> dict[str, tuple[str, str]]:
    """Return `{name: (type, witness)}` for every assignment `iface_construct` COMPUTED.

    ⚑ ONLY THE COMPUTED ROWS ENTER THE MAPPING, and that filter IS the one-sided verdict. An
    UNRESOLVED row is dropped here rather than carried with an empty type, so a caller cannot
    accidentally read "did not bottom out" as "derives to nothing".
    """
    try:
        src = Path(module_path).read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=module_path)
    except (OSError, SyntaxError, ValueError):
        return {}
    out: dict[str, tuple[str, str]] = {}
    for r in iface_construct.resolve_module(tree, module_path):
        if r.status == _COMPUTED and r.witness is not None:
            out[r.name] = (r.type_name, r.witness.where)
    return out


def _render(found: tuple[Finding, ...], stub_path: str, module_path: str) -> None:
    """Print the derivable-`object` findings for one stub, or say the stub is clean."""
    if not found:
        sys.stdout.write(
            f"stub-top-type: clean — no derivable `object` in {stub_path}.\n"
            "  ⚑ This is one-sided: an `object` whose assignment did NOT bottom out is "
            "UNDERIVABLE\n  and is not reported. Silence here is not a claim that every "
            "`object` was deliberate.\n"
        )
        return
    sys.stdout.write(
        f"stub-top-type: {len(found)} slot(s) in {stub_path} spell the TOP TYPE where "
        f"{module_path}\n  already determines the answer. `object` admits every value, so "
        "`stubtest` cannot\n  contradict these — a green verdict on them is a fact about what "
        "`object` admits:\n"
    )
    for f in found:
        sys.stdout.write(
            f"    · {f.name} (stub line {f.stub_line}) -> {f.derived}   [{f.witness}]\n"
        )
    sys.stdout.write(
        "  NEXT: state the derived type. A type read off an assignment's own constructor is\n"
        "  correct BY CONSTRUCTION — that it cannot be falsified is not a reason to withhold\n"
        "  it. If a slot is a deliberate refusal, give it a NAMED type (a Protocol, an alias)\n"
        "  so the judgement is legible: see `HEADER: _HeaderLike` in stubs/agda_lex.pyi.\n"
    )


def main(argv: list[str]) -> int:
    """Report one stub's derivable `object` slots; with `--check`, exit 1 when any exist."""
    rest = [a for a in argv[1:] if not a.startswith("-")]
    expected = 2
    if len(rest) != expected:
        sys.stdout.write(__doc__ or "")
        return 2
    stub_path, module_path = rest
    try:
        stub_src = Path(stub_path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        sys.stdout.write(f"stub-top-type: could not read {stub_path}: {e}\n")
        return 2
    found = findings(stub_src, derived_of(module_path))
    _render(found, stub_path, module_path)
    return 1 if found and "--check" in argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
