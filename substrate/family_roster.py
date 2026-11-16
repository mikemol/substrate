#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read every declared witness FAMILY in `substrate/` as ONE SET.

⚑⚑⚑ `witness_family` BUILT TWO READERS FOR DRIFT AND LEFT THEM UNASKABLE. `Family.unsplit()` is
the n-split work list and `Family.dangling_premises()` is what makes a positive control's edge
checkable — and both can only be asked ONE FILE AT A TIME, by a reader who already knows which
files declare a family. That is the same defect as a census with no denominator: the instrument
exists, nothing points it at the population, so its zero is a fact about who opened which file.

⚑⚑ AND THE DECLARED-BUT-UNRUN CHECK IS THE POINT, NOT A BONUS ROW.
`edge_witness_selftest.every_declared_member_is_a_real_arm` argues it for ONE family: a family
naming a member nothing runs *"reads as MORE rigorous than an undeclared suite while being less"*.
That arm can only ever cover the family whose suite carries it — so the property holds exactly
where someone remembered to write the arm, which is the population that needs it least. Corpus-wide
it is a census, and the families with no such arm are precisely the ones it can find something in.

⚑⚑⚑ `ast`, NOT IMPORT — THE SAME ARGUMENT `import_edges` RECORDS. Several modules in this corpus
execute work at import (one rewrites files from module scope), so discovering families by importing
candidate modules to read `__dict__` would FIRE that work, once per module, in-process — and a
roster is exactly the reader that must sweep every file, so it would fire the most. The `of(...)`
call and its `Member(...)` arguments are LITERAL in every declaration measured, so the shape is
statically evaluable; this evaluates that shape and refuses anything else.

⚑⚑ A DECLARATION THIS CANNOT EVALUATE IS REPORTED, NEVER SKIPPED. A computed roster — a
comprehension, a name, a splat — is a family the reader has no reading of, and dropping it silently
would let a family leave the census by becoming cleverer. `case_count` records the same rule for
its own literal-sum parse: an unreadable total is UNREADABLE, not zero. The alternative is the
false-zero this module exists to make impossible.

⚑⚑⚑ AND `cases` IS EVALUATED OVER A NAMED FIXTURE LIST, WHICH IS A DELIBERATE WIDENING WITH A
STATED FLOOR. Two declarations spelled `cases=len(_KEEP) + len(_DROP)`, and this reader refused
them — correctly, under the rule above, but the refusal pointed at the BETTER shape. A count
written `len(<fixture>)` TRACKS its data: add a path to `_DROP` and the member's count grows with
the assertions the arm actually makes, where a literal `9` silently under-reports from the moment
the fixture moves. Demanding a literal in order to be readable would make the census REWARD the
shape that drifts, which inverts what it is for.

⚑⚑ SO THE EVALUATOR IS BOUNDED BY ENUMERATION, NOT BY TASTE, AND HERE IS EXACTLY WHERE IT STOPS.
It resolves a bare NAME bound once at MODULE SCOPE to a literal tuple/list display, takes `len` of
it, and folds `+` over integers. Nothing else: no call but `len`, no attribute, no subscript, no
comprehension, no operator but `+`, no name bound inside a function or bound twice. A form outside
that set is UNREADABLE exactly as before — the refusal is NARROWED, never removed, and the row it
produces still carries its reason.

⚑ THE FLOOR IS WHAT KEEPS THIS FROM BECOMING A SECOND PYTHON. Every admitted form is decidable
from one module's own syntax tree, with no environment and no execution — the same property that
made the `of(...)` literal readable in the first place. The moment a `cases` needs a VALUE not
derivable that way, the answer is a row saying so; the alternative is a reader that evaluates
arbitrary expressions and is wrong somewhere no case will look.

⚑ WHAT IT STILL CANNOT SEE, STATED RATHER THAN LEFT TO BE DISCOVERED. A family assembled at
runtime, or bound to a name other than `FAMILY`, is invisible here — this reports the boundary of
the DECLARATION convention, and must not be read as reporting the boundary of families.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import witness_family

from substrate import case_count, corpus

if TYPE_CHECKING:
    from pathlib import Path

# The module-level name a family is declared under. ⚑ ONE SPELLING, READ FROM HERE. A roster
# keyed on a name typed at several sites is the census-keyed-on-one-spelling shape inside the
# census built to find it.
FAMILY_NAME = "FAMILY"

# The constructor and member spellings this reader evaluates. ⚑ MATCHED ON THE ATTRIBUTE, not the
# module alias, so a declaration importing `witness_family` under any name is still read.
_OF = "of"
_MEMBER = "Member"

# The ONE call this reader evaluates inside a `cases=` expression. ⚑ A BARE NAME ONLY — an
# attribute spelled `x.len` is a method on a value this reader knows nothing about, and admitting
# it would make the grammar depend on a VALUE rather than on the syntax, which is precisely the
# line between a bounded reader and a second Python.
_LEN = "len"

# The suffix that makes a module a suite. ⚑ THE ARM-ROSTER NAME COMES FROM `case_count`, which owns
# that reading; a second parse of the same convention here is the drift that reader exists to stop.
_SUITE_SUFFIX = "_selftest.py"

# ⚑ A TYPED STAND-IN FOR AN ABSENT ARGUMENT, so a missing keyword takes exactly the same path as a
# present-but-unevaluable one. `None` is not an `ast.expr`, and widening every field reader to
# accept it would put an "absent" branch into six readers instead of one constant here — six places
# for the two cases to be told apart differently. Every reader below returns None for it.
_MISSING: ast.expr = ast.Constant(value=None)


@dataclass(frozen=True, slots=True)
class Declared:
    """One module's `FAMILY`, as read — or the reason it could not be read.

    ⚑ THE UNREADABLE CASE IS A ROW, NOT AN ABSENCE. A module that declares a family this reader
    cannot evaluate must appear in the census carrying WHY, because the alternative is a
    denominator that shrinks silently when a declaration gets cleverer.
    """

    path: str
    family: witness_family.Family | None
    reason: str

    @property
    def readable(self) -> bool:
        """Report whether the declaration evaluated to a family."""
        return self.family is not None


@dataclass(frozen=True, slots=True)
class Unrun:
    """A member a family declares that the owning suite does not run as an arm."""

    path: str
    key: str
    member: str

    @property
    def route(self) -> str:
        """Return the repair a reader should make."""
        return f"add an arm named {self.member}, or drop the member from {self.key}"


@dataclass(frozen=True, slots=True)
class Dangling:
    """A premise naming a member its own family does not hold."""

    path: str
    key: str
    member: str
    premise: str


@dataclass(frozen=True, slots=True)
class Unsplit:
    """A member asserting several facts under one name — the split work list."""

    path: str
    key: str
    member: str
    cases: int


def _str_of(node: ast.expr) -> str | None:
    """Return a string built from literals and implicit concatenation, or None.

    ⚑ THE PROSE IS WRITTEN AS ADJACENT STRING LITERALS across several lines, which the parser
    folds into one `Constant` — but a claim assembled with `+` is a `BinOp`, and evaluating it
    as anything other than a string would put a wrong value into the census. Refused instead.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _str_of(node.left), _str_of(node.right)
        if left is None or right is None:
            return None
        return left + right
    return None


def _strs_of(node: ast.expr) -> tuple[str, ...] | None:
    """Return a literal sequence of strings, or None when it is not one."""
    if not isinstance(node, (ast.Tuple, ast.List)):
        return None
    out: list[str] = []
    for elt in node.elts:
        text = _str_of(elt)
        if text is None:
            return None
        out.append(text)
    return tuple(out)


def lengths(tree: ast.Module) -> dict[str, int]:
    """Return each module-scope name bound ONCE to a literal tuple/list, mapped to its length.

    ⚑⚑ BOUND ONCE IS PART OF THE CONTRACT, NOT AN IMPLEMENTATION DETAIL. A name rebound later has
    two lengths and no reading; taking the first would report a count off a fixture the declaration
    does not use — a wrong number wearing a readable shape, which is worse than a refusal. A
    rebound name is dropped, so its `len()` stays UNREADABLE rather than becoming plausible.

    ⚑ MODULE SCOPE ONLY. A name bound inside a function is not in scope at the declaration, and
    resolving it would be this reader inventing an environment that Python does not have there.
    """
    seen: dict[str, int] = {}
    rebound: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id in seen:
                rebound.add(target.id)
            elif isinstance(node.value, (ast.Tuple, ast.List)):
                seen[target.id] = len(node.value.elts)
    return {name: n for name, n in seen.items() if name not in rebound}


def _len_arg(node: ast.expr) -> str | None:
    """Return the name `node` takes the length of, when it is exactly `len(<name>)`.

    ⚑ SPELLED AS NESTED NARROWINGS RATHER THAN ONE CHAINED CONDITION, and the shape is doing the
    same work as the check. A chain reads an attribute off a node the narrowing has not yet fixed,
    which types as `Any` — an unchecked value walking into the census the module exists to keep
    honest.
    """
    if not isinstance(node, ast.Call) or node.keywords or len(node.args) != 1:
        return None
    func = node.func
    if not isinstance(func, ast.Name) or func.id != _LEN:
        return None
    arg = node.args[0]
    return arg.id if isinstance(arg, ast.Name) else None


def _int_of(node: ast.expr, sizes: dict[str, int]) -> int | None:
    """Return `cases` as an integer, over the bounded fixture-length grammar.

    ⚑ THREE FORMS, ENUMERATED, AND NOTHING ELSE. An integer literal; `len(<name>)` for a name
    `lengths()` resolved; and `+` folded over those. No other call, operator, attribute, subscript
    or comprehension — each admitted form is decidable from one module's own syntax tree with no
    environment and no execution, the same property that made the `of(...)` literal readable.

    ⚑ A `len()` OF AN UNRESOLVED NAME RETURNS None, WHICH LEAVES THE REFUSAL PATH INTACT. That is
    where the widening declines to guess: the count exists, this reader cannot see it, and a row
    saying so is the honest report — the rule the module docstring records for a computed roster.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _int_of(node.left, sizes), _int_of(node.right, sizes)
        if left is None or right is None:
            return None
        return left + right
    name = _len_arg(node)
    return None if name is None else sizes.get(name)


def _attr_is(node: ast.expr, name: str) -> bool:
    """Report whether `node` is a call target spelled `<anything>.name` or bare `name`."""
    if isinstance(node, ast.Attribute):
        return node.attr == name
    return isinstance(node, ast.Name) and node.id == name


def _kwargs(call: ast.Call) -> dict[str, ast.expr] | None:
    """Return a call's keyword arguments, or None when it uses positional args or a splat.

    ⚑ POSITIONAL IS REFUSED RATHER THAN POSITIONALLY DECODED. Mapping argument ORDER to field
    names here would be a second authority on `witness_family`'s signature, and it would keep
    reading successfully — with the fields swapped — the day that signature changes.
    """
    if call.args:
        return None
    out: dict[str, ast.expr] = {}
    for kw in call.keywords:
        if kw.arg is None:
            return None
        out[kw.arg] = kw.value
    return out


def _member(node: ast.expr, sizes: dict[str, int]) -> witness_family.Member | None:
    """Return one `Member(...)` literal as a member, or None when it is not one.

    ⚑ A NESTED `family=` IS REFUSED, NOT READ AS A LEAF. A split member read as `cases=1` would
    report a total BELOW the family's own — the invariance that makes an n-split auditable, broken
    by the READER rather than by the split, and therefore invisible to the split's own audit.
    """
    if not isinstance(node, ast.Call) or not _attr_is(node.func, _MEMBER):
        return None
    kw = _kwargs(node)
    if kw is None or "family" in kw:
        return None
    name = _str_of(kw.get("name", _MISSING))
    claim = _str_of(kw.get("claim", _MISSING))
    cases = _int_of(kw["cases"], sizes) if "cases" in kw else 1
    premises = _strs_of(kw["premises"]) if "premises" in kw else ()
    if name is None or claim is None or cases is None or premises is None:
        return None
    return witness_family.Member(name=name, claim=claim, cases=cases, premises=premises)


def _members(node: ast.expr, sizes: dict[str, int]) -> tuple[witness_family.Member, ...] | None:
    """Return a literal roster of members, or None when any element is unevaluable."""
    if not isinstance(node, (ast.Tuple, ast.List)):
        return None
    out: list[witness_family.Member] = []
    for elt in node.elts:
        got = _member(elt, sizes)
        if got is None:
            return None
        out.append(got)
    return tuple(out)


def _family(node: ast.expr, sizes: dict[str, int]) -> tuple[witness_family.Family | None, str]:
    """Return the family a `witness_family.of(...)` call declares, with a reason on failure."""
    if not isinstance(node, ast.Call) or not _attr_is(node.func, _OF):
        return None, "the value is not a witness_family.of(...) call"
    kw = _kwargs(node)
    if kw is None:
        return None, "the of(...) call uses positional or splatted arguments"

    key = _str_of(kw.get("key", _MISSING))
    apex = _str_of(kw.get("apex", _MISSING))
    subject = _str_of(kw.get("subject", _MISSING))
    if key is None or apex is None or subject is None:
        return None, "key, apex or subject is not a literal string"

    roster = _members(kw.get("members", _MISSING), sizes)
    if roster is None:
        return None, (
            "the member roster is not a literal sequence of Member(...) literals, or a "
            "cases= is outside the literal/len(fixture)/+ grammar this reader evaluates"
        )

    # ⚑ BUILT THROUGH `of()`, NOT `Family(...)`. The duplicate-name refusal and the
    # family-and-cases refusal are the constructor's, and a roster that bypassed them would
    # report a population the real declaration cannot construct.
    try:
        return witness_family.of(key=key, apex=apex, subject=subject, members=roster), ""
    except ValueError as exc:
        return None, str(exc)


def read(path: Path) -> Declared | None:
    """Return one file's declared family, or None when it declares none.

    ⚑ THE FIXTURE LENGTHS COME FROM THE SAME TREE THE DECLARATION IS IN, which is what makes a
    `len(<name>)` in `cases=` a reading rather than a lookup in someone else's namespace.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None

    sizes = lengths(tree)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == FAMILY_NAME for t in node.targets):
            continue
        family, reason = _family(node.value, sizes)
        return Declared(path=path.name, family=family, reason=reason)
    return None


def census(root: Path | None = None) -> tuple[Declared, ...]:
    """Return every declared family in `substrate/`, readable or not."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    found = [read(path) for path in sorted(where.glob("*.py"))]
    return tuple(got for got in found if got is not None)


def suite_of(declared: Declared, root: Path | None = None) -> Path:
    """Return the path of the suite that would run a declaring module's arms.

    ⚑ THE CONVENTION IS `<module>_selftest.py` AND IT IS DERIVED, NOT SEARCHED. A search that
    guessed the owning suite could attach a family's members to the wrong roster and report the
    unrun set of a different module — a false zero with a plausible shape.
    """
    base = (root if root is not None else corpus.ROOT) / "substrate"
    stem = declared.path.removesuffix(".py")
    if stem.endswith("_selftest"):
        return base / f"{stem}.py"
    return base / f"{stem}{_SUITE_SUFFIX}"


def arms(path: Path) -> tuple[str, ...] | None:
    """Return the arm names a suite's `_ARMS` roster dispatches, or None when unreadable.

    ⚑⚑ NONE MEANS "NO READING", NEVER "NO ARMS", and the two must not collapse. A missing suite
    and a suite whose roster this cannot parse both yield no names — and reporting either as an
    empty arm set would declare EVERY member of that family unrun, which is a loud false positive
    that trains a reader to ignore the row.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == case_count.ARMS_NAME for t in node.targets):
            continue
        if not isinstance(node.value, (ast.Tuple, ast.List)):
            return None
        names = [e.id for e in node.value.elts if isinstance(e, ast.Name)]
        if len(names) != len(node.value.elts):
            return None
        return tuple(names)
    return None


def unrun(rows: tuple[Declared, ...], root: Path | None = None) -> tuple[Unrun, ...]:
    """Return every declared member no arm in the owning suite runs.

    ⚑⚑⚑ THE CORPUS-WIDE FORM OF THE ONE ARM THAT EXISTS. A family naming a member nothing runs
    reads as more rigorous than an undeclared suite while being less — and the per-suite arm can
    only ever assert this for the family whose author already thought of it.
    """
    out: list[Unrun] = []
    for row in rows:
        if row.family is None:
            continue
        got = arms(suite_of(row, root))
        if got is None:
            continue
        known = set(got)
        out.extend(
            Unrun(path=row.path, key=row.family.key, member=name)
            for name in row.family.names
            if name not in known
        )
    return tuple(out)


def dangling(rows: tuple[Declared, ...]) -> tuple[Dangling, ...]:
    """Return every premise naming a member its own family does not hold."""
    return tuple(
        Dangling(path=row.path, key=row.family.key, member=member, premise=premise)
        for row in rows
        if row.family is not None
        for member, premise in row.family.dangling_premises()
    )


def unsplit(rows: tuple[Declared, ...]) -> tuple[Unsplit, ...]:
    """Return every member asserting several facts under one name — the split work list."""
    return tuple(
        Unsplit(path=row.path, key=row.family.key, member=member, cases=cases)
        for row in rows
        if row.family is not None
        for member, cases in row.family.unsplit()
    )


def totals(rows: tuple[Declared, ...]) -> tuple[int, int, int]:
    """Return `(families, members, cases)` over the readable declarations.

    ⚑ THE READABLE ONES ONLY, AND THE UNREADABLE COUNT IS RENDERED BESIDE IT rather than folded
    in. A total that silently included an unevaluable declaration as zero would report the census
    growing cleaner as declarations grew harder to read.
    """
    good = tuple(r.family for r in rows if r.family is not None)
    return len(good), sum(len(f.members) for f in good), sum(f.count for f in good)


def render(rows: tuple[Declared, ...], root: Path | None = None) -> str:
    """Return the corpus-wide roster as text, defects first.

    ⚑ THE TOTALS COME LAST BECAUSE THEY ARE THE DENOMINATOR, not the finding. A reader scanning
    for work wants the three lists; the counts are what make a zero in them readable.
    """
    if not rows:
        return "  no module declares a FAMILY\n"

    lines: list[str] = []
    lines.extend(
        f"  ⚑ UNREADABLE: {r.path} declares {FAMILY_NAME} but {r.reason}"
        for r in rows
        if r.family is None
    )
    lines.extend(
        f"  ⚑ DECLARED BUT UNRUN: {u.path} {u.key}.{u.member} — {u.route}"
        for u in unrun(rows, root)
    )
    lines.extend(
        f"  ⚑ DANGLING PREMISE: {d.path} {d.key}.{d.member} rests on {d.premise}, "
        f"which is not a member"
        for d in dangling(rows)
    )
    lines.extend(
        f"  unsplit: {u.path} {u.key}.{u.member} asserts {u.cases} facts under one name"
        for u in unsplit(rows)
    )
    families, members, cases = totals(rows)
    lines.append(f"  {families} famil(ies), {members} member(s), {cases} case(s)")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(census()))
    sys.exit(0)
