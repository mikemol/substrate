#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Tell a RELATION arm from an arm that merely bundles independent claims.

⚑⚑⚑ WHY THIS EXISTS (gate-G36). `arm_claims` reports the multi-claim arms and the bijection
target says each should assert one claim. Reading the three heaviest arms of the heaviest suite
showed that premise does not hold uniformly: all three are positive-plus-control structures whose
claim IS the relation between their outcomes.

  * `the_three_refusals_are_never_collapsed` — UNSAFE, UNKNOWN and CLEAN must carry DIFFERENT
    messages. Split into three, each message is checked and the distinctness is asserted by nobody.
  * `only_a_real_main_guard_is_recognised` — one positive against four planted negatives, and its
    own docstring says a predicate that always said yes would pass every other dispatch arm.
  * `a_stranded_import_may_vanish_but_a_body_line_may_not` — an ASYMMETRY, where each half passes
    trivially alone.

⚑⚑ SO SPLITTING IS RIGHT FOR INDEPENDENT FACTS AND DESTRUCTIVE FOR A RELATION, and a census that
cannot separate them turns a paydown into a content loss. `arm_claims` counts `out.append` sites,
which is what it says it does — the separation is a different question and belongs here.

⚑⚑⚑ THE DISCRIMINATOR IS WHICH PREDICATE THE GUARDS CALL, AND IT IS A PROXY. Sibling claims that
probe the SAME predicate against different inputs are one relation under test; claims that probe
DIFFERENT predicates are independent facts that happen to share an arm. That is readable from the
call names in the guard conditions, and it is not a proof: an arm could relate two outcomes of two
different functions, and this reader would call it independent.

⚑ SO IT REPORTS UNDECIDED RATHER THAN GUESSING, and the undecided column is printed even at zero.
A reader that silently classified what it could not read would license exactly the mechanical
split this exists to prevent — the census-green shape, one level up from the census it corrects.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass

from substrate import arm_claims, corpus

# How many rows to spell out before summarising. The counts are always stated.
SAMPLE = 12

# Below this many claims an arm is not worth classifying — one claim is already the target.
_MULTI = 2


@dataclass(frozen=True, slots=True)
class Arm:
    """One multi-claim arm, and whether its claims relate or merely coexist."""

    suite: str
    name: str
    claims: int
    verdict: str
    probes: tuple[str, ...]

    @property
    def relation(self) -> bool:
        """Whether this arm's claims probe one predicate — splitting would destroy it."""
        return self.verdict == "relation"

    @property
    def undecided(self) -> bool:
        """Whether this reader could not classify the arm — a fact about the reader."""
        return self.verdict == "undecided"


def _is_append(call: ast.Call) -> bool:
    """Whether this call is the `out.append(...)` that marks a claim."""
    return isinstance(call.func, ast.Attribute) and call.func.attr == "append"


def _bindings(func: ast.FunctionDef) -> dict[str, str]:
    """Return `local name -> predicate it was last assigned from`, for calls only.

    ⚑⚑ THIS IS THE WIDENING THE FIRST CUT NEEDED, AND THE UNREAD ARMS NAMED IT THEMSELVES. The
    dominant undecided shape is assign-then-compare: `got = _kinds(...)` followed by
    `if got != [...]`, twice, over different fixtures. `assert_census_selftest`'s two arms both
    say in their own docstrings that the discriminator IS the pair — so they are relations, and a
    reader that stopped at the bare `Name` in the comparison called them undecided.

    ⚑ LAST ASSIGNMENT WINS, deliberately. These arms REBIND one name across successive probes
    (`got = ...` then `got = ...`), so a first-wins rule would read the second guard against the
    first fixture's call. Both bind the same predicate here, which is exactly why the arm is a
    relation — but the rule has to be stated rather than fall out of dict ordering.

    ⚑⚑ AND A BINDING RESOLVES THROUGH A TRANSPARENT BUILTIN TOO, or the two routes to a probe
    disagree. `text = str(exc)` bound to `str` while a guard calling `str(exc)` inline resolved
    to `exc` — one arm, two spellings of one fact, which is the shape this repo files against.
    The map is threaded in so `str(exc)` reaches whatever `exc` was bound from.
    """
    out: dict[str, str] = {}
    # ⚑⚑⚑ AN `except ... as exc` BINDS A NAME AND IS NOT AN ASSIGN, and missing it made the
    #   builtin-transparency fix REGRESS a verified relation. `an_unknown_target_is_refused_by_name`
    #   binds `text = str(exc)`, so resolving `str` through to `exc` found no binding at all and
    #   the arm went from a wrongly-reasoned RELATION to UNDECIDED. The handler binds the
    #   exception RAISED BY the call under test, so the probe is that call.
    for node in ast.walk(func):
        if not isinstance(node, ast.Try):
            continue
        raised = next(
            (
                _called(s.value, out)
                for s in node.body
                if isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
            ),
            "",
        )
        for handler in node.handlers:
            if handler.name and raised:
                out[handler.name] = raised
    # ⚑⚑⚑ CALL IDENTITY WAS TRIED AS THE DISCRIMINATOR AND REFUTED (gate-G44). Tagging each
    #   binding with its call site made two fields of ONE result read as a relation — correct for
    #   `_verdict@106.refuses` beside `_verdict@106.state` — and made `Bucket` constructed twice
    #   read as INDEPENDENT, which is wrong: that arm's docstring says the populated and empty
    #   buckets are ONE LAW AT TWO POINTS, DELIBERATELY LEFT FUSED. Both shapes occur in both
    #   meanings, so the syntax does not decide it and the experiment is recorded rather than kept.
    for node in ast.walk(func):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        called = _called(node.value, out)
        if not called:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out[target.id] = called
    return out


# ⚑⚑⚑ ARGUMENT-AGNOSTIC BUILTINS ARE NOT PREDICATES, AND KEYING ON THEM FUSES UNRELATED GUARDS.
# `len(a) != len(b)` and `len(c) == 3` both record `len`, so two guards inspecting entirely
# different objects read as one relation — a false positive in the FREEZING direction, which
# marks a splittable arm as destructive-to-split. MEASURED: `a_conflict_is_reported_once` and
# `an_unknown_target_is_refused_by_name` are both genuine relations that this reader reached for
# the wrong reason, so the verdicts were right and the evidence was not.
# ⚑ SO A BUILTIN RESOLVES THROUGH TO ITS ARGUMENT, naming what is actually being examined. It is
# a wrapper on the probe, not the probe.
_TRANSPARENT: frozenset[str] = frozenset(
    {
        "len",
        "str",
        "set",
        "list",
        "tuple",
        "sorted",
        "bool",
        "int",
        "repr",
        "frozenset",
    }
)


def _direct(node: ast.expr) -> str:
    """Return the predicate a call expression names, or the empty string.

    ⚑ THE ATTRIBUTE'S LEAF IS THE NAME, so `module_trim.conserved(...)` reads as `conserved`.
    A module-qualified call and a bare one probe the same predicate, and keying on the whole
    dotted path would report them as two — the two-spelling shape this repo files against.
    """
    if not isinstance(node, ast.Call):
        return ""
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _compared(node: ast.Compare, bound: dict[str, str]) -> str:
    """Return the predicate a comparison probes, from whichever side carries it.

    ⚑⚑⚑ A MEMBERSHIP TEST PUTS THE PROBE ON THE RIGHT, AND TAKING `.left` UNCONDITIONALLY WAS THE
    DEFECT. `"35 provider(s)" not in got.shape` has a string LITERAL on the left, so the first cut
    resolved to nothing and reported a real relation arm undecided. That prediction failed twice —
    once against the arm and once against a BoolOp widening built on the same wrong model — before
    this function was READ rather than inferred.

    ⚑ THE LEFT SIDE WINS WHEN BOTH RESOLVE, because `got != expected` is the dominant shape and
    its probe is the left operand. A literal contributes nothing either way.
    """
    left = _called(node.left, bound)
    if left:
        return left
    for other in node.comparators:
        got = _called(other, bound)
        if got:
            return got
    return ""


def _called(node: ast.expr, bound: dict[str, str]) -> str:
    """Return the predicate a test expression probes, resolving locals through `bound`."""
    if isinstance(node, ast.UnaryOp):
        return _called(node.operand, bound)
    if isinstance(node, ast.Compare):
        return _compared(node, bound)
    # ⚑⚑ A BOOLOP RESOLVES ONLY WHEN ITS OPERANDS AGREE, and that unanimity IS the claim. The
    #   measured instance is `"35 provider(s)" not in got.shape or "X x21" not in got.shape` —
    #   two membership tests over ONE field, asserting one property of one probe. Operands that
    #   disagree are two questions joined by an operator, and folding them to whichever came
    #   first would name a predicate the guard does not single out.
    # ⚑ AND AN AGREED-EMPTY BOOLOP STAYS EMPTY BY CONSTRUCTION, not by the accident that popping
    #   a one-element set of "" happens to yield "". Operands this reader cannot name are still
    #   unread however many of them agree on being unreadable.
    if isinstance(node, ast.BoolOp):
        seen = {_called(v, bound) for v in node.values}
        return seen.pop() if len(seen) == 1 and "" not in seen else ""
    # ⚑⚑ AN ATTRIBUTE OF A BOUND LOCAL PROBES THAT FIELD OF THAT TYPE, and the field is part of
    #   the probe rather than noise. `ban_witness_selftest` constructs a `Bucket` twice and reads
    #   `got.n` in one arm and `got.shape` in another — same constructor, genuinely different
    #   questions — so keying on the constructor alone would fuse two arms that do not relate.
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        base = bound.get(node.value.id, "")
        return f"{base}.{node.attr}" if base else ""
    # ⚑ A BARE NAME RESOLVES THROUGH ITS BINDING, which is what makes assign-then-compare
    #   readable. A name never assigned from a call stays empty, so the arm reports UNDECIDED
    #   rather than being classified on a guess.
    if isinstance(node, ast.Name):
        return bound.get(node.id, "")
    return _invoked(node, bound)


def _invoked(node: ast.expr, bound: dict[str, str]) -> str:
    """Return the predicate a call names, resolving through argument-agnostic builtins.

    ⚑ A TRANSPARENT BUILTIN IS A WRAPPER, SO IT RESOLVES THROUGH to whatever it examines. An empty
    result means the argument itself is unread, and the arm reports UNDECIDED rather than being
    classified on the wrapper's name — which every guard using that builtin would share.
    """
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _TRANSPARENT
        and node.args
    ):
        return _called(node.args[0], bound)
    return _direct(node)


def _probes(func: ast.FunctionDef) -> tuple[str, ...]:
    """Return the predicate each claim-bearing guard probes, in order.

    ⚑ ONLY GUARDS THAT CARRY A CLAIM COUNT. An `if` whose body appends nothing is plumbing —
    a fixture check or an early return — and folding it in would let unrelated setup decide
    whether the arm's real claims relate.
    """
    bound = _bindings(func)
    out: list[str] = []
    for node in ast.walk(func):
        if not isinstance(node, ast.If):
            continue
        if not any(
            isinstance(inner, ast.Call) and _is_append(inner)
            for stmt in node.body
            for inner in ast.walk(stmt)
        ):
            continue
        out.append(_called(node.test, bound))
    return tuple(out)


def classify(func: ast.FunctionDef) -> tuple[str, tuple[str, ...]]:
    """Return `(verdict, probes)` for one multi-claim arm.

    ⚑⚑ ONE DISTINCT PREDICATE ACROSS SEVERAL CLAIMS IS A RELATION. The arm is asking the same
    question of different inputs, which is what a positive-and-its-controls looks like, and the
    several-claim count IS the relation being tested.

    ⚑ AN ARM WHOSE GUARDS THIS READER COULD NOT NAME IS UNDECIDED, never independent. A guard
    that inlines its test, compares two locals, or calls nothing yields an empty probe name, and
    treating an unread guard as evidence of independence would license the destructive split.
    """
    probes = _probes(func)
    if len(probes) < _MULTI or any(p == "" for p in probes):
        return "undecided", probes
    # ⚑⚑⚑ AND KEYING ON THE CALL RATHER THAN THE FIELD WAS TRIED AND REFUTED — see gate-G44 and
    #   the note in `_bindings`. It fixed the field-pair arms and broke the two-construction arms,
    #   because BOTH shapes occur in BOTH meanings. The verdict therefore stays on the whole
    #   probe, and the INDEPENDENT column stays untrusted until a reader can tell them apart.
    return ("relation" if len(set(probes)) == 1 else "independent"), probes


def read(path: str, multi: dict[str, int]) -> tuple[Arm, ...]:
    """Return a classification for every multi-claim arm in one suite."""
    try:
        tree = ast.parse((corpus.ROOT / "substrate" / path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()
    out: list[Arm] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        claims = multi.get(node.name, 0)
        if claims < _MULTI:
            continue
        verdict, probes = classify(node)
        out.append(Arm(path, node.name, claims, verdict, probes))
    return tuple(out)


def census() -> tuple[Arm, ...]:
    """Return a classification for every multi-claim arm the authority reports.

    ⚑ THE POPULATION COMES FROM `arm_claims`, never from a second walk. A reader that decided
    for itself which arms are multi-claim would be a rival authority for a question that one
    already answers, and the two would drift.
    """
    by_suite: dict[str, dict[str, int]] = {}
    for claim in arm_claims.census():
        if claim.count is not None and claim.count >= _MULTI:
            by_suite.setdefault(claim.suite, {})[claim.name] = claim.count
    out: list[Arm] = []
    for suite in sorted(by_suite):
        out.extend(read(suite, by_suite[suite]))
    return tuple(out)


def relations(found: tuple[Arm, ...]) -> tuple[Arm, ...]:
    """Return only the arms a split would destroy."""
    return tuple(a for a in found if a.relation)


def render(found: tuple[Arm, ...]) -> str:
    """Render the split: which multi-claim arms may be split and which must not be."""
    if not found:
        return "relation-arm: no multi-claim arms read — a fact about the WALK\n"

    relation = relations(found)
    unread = [a for a in found if a.undecided]
    independent = len(found) - len(relation) - len(unread)

    out = [
        f"  {len(found)} multi-claim arm(s) across {len({a.suite for a in found})} suite(s)",
        f"    INDEPENDENT — splitting is a paydown  : {independent}",
        f"    ⚑ RELATION — splitting DESTROYS it    : {len(relation)}",
        f"    UNDECIDED (a fact about this reader)  : {len(unread)}",
    ]
    out.extend(
        f"      relation  {a.suite}::{a.name}  ({a.claims} claims, all {a.probes[0]})"
        for a in relation[:SAMPLE]
    )
    if len(relation) > SAMPLE:
        out.append(f"      … and {len(relation) - SAMPLE} more relation arm(s)")
    return "\n".join(out) + "\n"


def named(found: tuple[Arm, ...], want: str) -> str:
    """Render the verdict for arms whose name contains `want`.

    ⚑⚑ THIS MODE EXISTS BECAUSE AUDITING A WIDENING NEEDED IT AND THE TOOL COULD NOT ANSWER.
    `render` prints a population and a truncated sample, so after a widening moved the counts I
    could not ask what verdict ONE arm received — and reaching for a shell pipe to filter the
    output is the judgement-in-the-turn shape the standing rule forbids. A reader that reports
    only aggregates cannot be audited against a case.

    ⚑ AN EMPTY RESULT NAMES THE SPELLING, never the substrate. No arm matching a substring is a
    fact about the query, and a caller must be able to tell that from a classified-clean arm.
    """
    hits = [a for a in found if want in a.name]
    if not hits:
        return f"relation-arm: no arm's name contains {want!r} — a fact about the SPELLING\n"
    return (
        "\n".join(
            f"  {a.verdict:<12} {a.suite}::{a.name}  ({a.claims} claims, probes {a.probes})"
            for a in hits
        )
        + "\n"
    )


def splittable(found: tuple[Arm, ...]) -> tuple[Arm, ...]:
    """Return the arms a split would pay down rather than destroy."""
    return tuple(a for a in found if a.verdict == "independent")


def render_splittable(found: tuple[Arm, ...]) -> str:
    """Render every splittable arm, so the paydown is a WORKLIST rather than a count.

    ⚑⚑ THE CENSUS SPELLS OUT ONLY RELATIONS, so the population this reader exists to make
    actionable was the one it would not name. That is `gate-G39`'s aggregate-vs-case gap arriving
    in the other column: a count tells you how much work there is and never which work to start.

    ⚑ THE PROBES RIDE ALONG, because an INDEPENDENT verdict means the guards probe DIFFERENT
    predicates and those names are the split's seam — one arm per predicate. A caller reading only
    the name would have to re-derive what this reader already knows.
    """
    rows = splittable(found)
    if not rows:
        return "relation-arm: no splittable arms — a fact about the READER, not the tree\n"
    out = [f"  {len(rows)} splittable arm(s) across {len({a.suite for a in rows})} suite(s)"]
    out.extend(
        f"      {a.suite}::{a.name}  ({a.claims} claims, probes {' '.join(a.probes)})" for a in rows
    )
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """Print which multi-claim arms are relations rather than bundles."""
    if not argv:
        sys.stdout.write(render(census()))
        return 0
    if argv == ["--splittable"]:
        sys.stdout.write(render_splittable(census()))
        return 0
    if len(argv) == 2 and argv[0] == "--named":  # noqa: PLR2004 — flag plus its operand
        sys.stdout.write(named(census(), argv[1]))
        return 0
    sys.stderr.write("usage: relation_arm.py [--splittable | --named <substring>]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
