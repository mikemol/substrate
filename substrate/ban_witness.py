#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The A5 family — one body over the ban ratchet's directive buckets, plus the reach of their fix.

⚑⚑⚑ FIVE BIB ENTRIES OVER ONE BODY, WHICH IS WHAT MAKES THIS A FAMILY RATHER THAN FIVE
WITNESSES. `A5-as`, `A5-using` and `A5-renaming` are one parameterized reading of one census at
three values of one field; `A5` is the AGGREGATE that also asks whether those three COVER it; and
`A5-as-reach` asks whether the tool that would pay the `as` bucket down can be reached at all.

⚑⚑⚑ MEASURED BEFORE PORTING, BECAUSE THE LAST WITNESS EXTRACTED THIS WAY TURNED OUT VACUOUS.
`T28_EDGES`'s question could only ever report zero and was retired. This one CANNOT: measured on
the live tree at extraction, `check_ban_ratchet` holds **7411 keys, 375 of them added over
baseline** — `as` x187 over 35 providers, `using` x131 over 71, `renaming` x57 over 19. Every
member of this family discriminates today, and the predicate has room to fail in both directions.

⚑⚑ THE COVERAGE CHECK IS THE AGGREGATE'S OWN CLAIM, AND IT IS NOT VACUOUS EITHER. The ban skill
names FOUR directives — `using`/`renaming`/`hiding`/`as` — while only three have buckets. Today
`hiding` measures ZERO, so the three buckets sum to exactly the census; that is a MEASUREMENT, not
a construction, and the moment a `hiding` key or a malformed one appears the aggregate reports a
kind no sub-item names while all three sub-items still read clean. **A sum of sub-items is not a
proof that the parts cover the whole**, so the whole is checked here rather than asserted.

⚑⚑ WHAT DELIBERATELY DID NOT COME ACROSS: THE DAG-CONE PROSE. The original body decorated its
verdict with `kind_cone`, `kind_cone_exclusive`, `route_cones`, `cone_containment` and
`kind_providers` — five figures that exist ONLY in `catalog/library/figures.py`, which is dirty and
cannot be edited. `substrate.dagcone` is the clean cone AUTHORITY, but it takes the caller's edge
relation as a parameter and the Agda import-DAG reader for it has not been extracted yet.
Re-deriving those five here would mint a second authority for a relation this repo already owns —
the `agda_files()` shape. So the cone figures are a NAMED GAP, not a silent omission: this witness
reports the census, its partition and its concentration, and says nothing about cones.

⚑ CONCENTRATION IS CARRIED, THOUGH, BECAUSE IT IS THE HALF THAT CHANGES THE ROUTE. 187 keys over
35 providers is 35 decisions; 187 over 187 is 187 hand-edits, and the count alone says they are the
same work. `kind_partition.concentration` already owns that read.

⚑⚑ `A5-as-reach` IS REWRITTEN, NOT TRANSCRIBED, AND THE MOVE IS WHY. The original asked
`hasattr(scope_fix, "fix_qualified")` and then `inspect.getsource(scope_fix)`. `fix_qualified` has
since MOVED to `scratch/scope_alias.py`; `scope_fix` re-exports it, so `hasattr` still passes and
`getsource` still finds the caller — **the probe reads the right answer off the wrong file, by
luck of a re-export.** A definition that moves out from under a source probe is exactly the
stale-target shape, so this reads the DEFINITION SITE and the CALL SITE separately.

⚑ AND IT READS THEM STATICALLY, NEVER BY IMPORT. A promoted module may not acquire a runtime
dependency on `scratch/` (`substrate.dagcone` records the rule and the sanctioned resolution).
`ast` over the file answers the same question without importing a tree of Agda rewriters — and it
is the stronger reading anyway, since the question is about a call site's GUARD, which an import
cannot see.

⚑⚑ THE FIGURE COMES FROM `warrant_records` AND THE EXCEPTION FROM `warrant_bib` (gate-G209). The
engine half — `records` / `claim_of` / `tag` — imports paperkit at module scope and lives in its
own module; `WarrantError` stays with the config half precisely so a caller catching it need not
import the engine to name the exception it is catching. ⚑ `_anchor` IS WHERE BOTH MEET, which is
why the repoint is two lines in a 475-line file: the call moves and the `except` does not.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), on `ratchet_census`,
`kind_partition`, `warrant_bib`, `witness_row` and `witness_family`.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import witness_family, witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import (
    corpus,
    kind_partition,
    ratchet_census,
    warrant_records,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

# The gate whose census this family reads, named the way `gate_module` resolves gates.
#
# ⚑⚑⚑ BARE, NOT `scripts.<gate>`, AND THE PREFIX WORKED HERE BY LUCK RATHER THAN BY
# CONSTRUCTION (gate-G359). `gate_module` runs a SIBLING FINDER scoped to `scripts/` so a gate
# importing its siblings by bare name resolves — but only on its `_by_location` fallback, which a
# DOTTED name never reaches, because ordinary package import succeeds first. This gate happens to
# spell its own import `from scripts.ratchet import …`, so it resolved either way and the defect
# was invisible: `ratchet_census_show` reads OVER under BOTH spellings today.
#
# ⚑⚑ WHICH IS EXACTLY WHY IT WAS WORTH PAYING WHILE CHEAP. The day `check_ban_ratchet` spells
# that import bare — as most of its siblings do — this witness goes UNMEASURABLE, and an
# unmeasurable census reads as *not clean* rather than as a defect in the caller. The failure
# would arrive attributed to the gate.
#
# ⚑ THE HOUSE SPELLING IS BARE: `ratchet_family` reads 7 of 7 measurable with every gate named
# bare, and `ratchet_witness` was corrected to bare for this reason.
GATE = "check_ban_ratchet"

# ⚑ THE FOUR DIRECTIVES THE BAN NAMES, NOT THE THREE THAT HAVE BUCKETS. Deriving this roster from
# the buckets would make the coverage check compare the partition against itself — the shape that
# turns a census into a tautology. `hiding` measures zero today and is listed anyway, because a
# kind that appears tomorrow must read as UNCOVERED rather than as absent.
DIRECTIVES = ("as", "using", "renaming", "hiding")

# The buckets this family declares a member for. ⚑ A SUBSET OF `DIRECTIVES` BY CONSTRUCTION, and
# the difference is exactly what the aggregate's coverage member exists to notice.
BUCKETS = ("as", "using", "renaming")

# The rewriter `A5-as-reach` asks about, and where its definition and its caller now live.
REWRITER = "fix_qualified"
REWRITER_DEF = "scratch/scope_alias.py"
REWRITER_CALLER = "scratch/scope_fix.py"

# ⚑ THE GUARD THAT MAKES THE CALLER ERROR-DRIVEN. `scope_fix`'s loop matches a compiler
# `[NotInScope]` and passes its suggestion group down; a call whose arguments include that group is
# reachable only from a build error. A5-as's aliases COMPILE — that is what makes them ban debt
# rather than build errors — so such a call can never fire for them.
ERROR_GUARD = "sugg"

# The separator a ban census key uses, and how many fields it carries.
_SEP = "::"

# How many added keys to name in a verdict sentence before the partition speaks for the rest.
_SAMPLE = 4


@dataclass(frozen=True, slots=True)
class Bucket:
    """One directive bucket's live reading: its size, and how concentrated it is."""

    kind: str
    keys: tuple[str, ...]
    providers: int
    top: str

    @property
    def n(self) -> int:
        """Return how many keys this bucket holds over baseline."""
        return len(self.keys)

    @property
    def shape(self) -> str:
        """Return the concentration clause — the half that decides sweep versus grind.

        ⚑ A COUNT IS NOT A DECISION COUNT. 187 keys over 35 providers is 35 decisions and one
        sweep; 187 over 187 is 187 hand-edits. Reporting only the count says those are the same
        work, which is the reflex this clause replaces with a measurement.
        """
        if not self.providers:
            return ""
        return f" over {self.providers} provider(s), top {self.top}"


def route(kind: str) -> str:
    """Return the command that enumerates this bucket, for a reader to act on.

    ⚑ THE GATE'S OWN LISTING, NOT PROSE. Every ratchet gate grew a `--list` mode precisely so a
    census could be ENUMERATED; naming it on each row makes the row actionable rather than
    descriptive.
    """
    return f"python3 scripts/check_ban_ratchet.py --list  # kind={kind}"


# ⚑⚑ THE FAMILY, DECLARED. The apex states what having the family establishes — which is the thing
# no single member says. `subject` names what it is parameterized over, so a fourth directive
# growing a bucket adds a member without changing the body.
#
# ⚑ THE MEMBERS ARE THE PROPERTIES, NOT THE BUCKETS. A roster of one member per directive would
# make this a copy of `BUCKETS` and the apex a count. What the family CLAIMS is these facts about
# every bucket, plus the two that only the aggregate and the reach probe can state.
FAMILY = witness_family.of(
    key="A5",
    apex="the ban additions are paid down, bucket by directive — and the buckets COVER the "
    "census, so no kind can be clean in every sub-item while the whole refuses",
    subject="directive kinds in the ban ratchet's added-key census",
    members=[
        # ⚑⚑ LEFT FUSED ON A SECOND READING, AND THE SPLIT WORK LIST IS WHERE THAT VERDICT BELONGS
        # RATHER THAN IN A PLAN. Both assertions under this name are `n == len(keys)`, once at a
        # populated bucket and once at an empty one — and the empty bucket is exactly the instance
        # a hardcoded non-zero `n` would fail, so it is a SECOND POINT on one law, not a second
        # law. Compare the two splits this same suite DID perform: the reach arm's pair asserted
        # opposite DIRECTIONS of one predicate (a probe that never fires is permanently
        # pessimistic, one that never clears permanently quiet), and the roster arm shed a claim
        # about the family's BOUNDARY. Neither shape is present here — neither branch guards the
        # other, so there is no premise edge to declare, and neither carries prose the other does
        # not already state. Splitting would produce two paragraphs restating one fact, which is a
        # worse arm than the one it replaced.
        witness_family.Member(
            name="each_bucket_reports_its_own_added_keys",
            claim="a bucket's verdict is its OWN added keys, partitioned out of the shared "
            "census — so three sub-items read one gate rather than three gates drifting; "
            "asserted at a populated AND an empty bucket, which is one law at two points",
            cases=2,
        ),
        witness_family.Member(
            name="a_bucket_reports_where_its_decisions_concentrate",
            claim="the provider count rides with the key count, because 187 keys over 35 "
            "providers is 35 decisions and 187 over 187 is 187 hand-edits — and the count "
            "alone says those are the same work",
        ),
        witness_family.Member(
            name="a_kind_no_bucket_names_is_reported_by_the_aggregate",
            claim="the ban names FOUR directives and three have buckets, so a `hiding` or "
            "malformed key would read clean in every sub-item while the census refuses; "
            "the aggregate is the only place that would notice",
            premises=("each_bucket_reports_its_own_added_keys",),
        ),
        witness_family.Member(
            name="an_unmeasurable_census_is_open_not_clean",
            claim="a gate that cannot be read has an UNKNOWN state, and reporting it at baseline "
            "would bank a green verdict nothing measured",
            premises=("each_bucket_reports_its_own_added_keys",),
        ),
        # ⚑⚑ THE REACH CLAIM IS TWO MEMBERS, NOT ONE WITH `cases=2`. The verdict has to separate
        # THREE states — absent, defined-but-unreachable, reachable — so it must both FIRE on an
        # all-guarded caller and CLEAR when a free one appears. A probe that only fired would be
        # permanently pessimistic and a probe that only cleared permanently quiet; each direction
        # is a distinct way to be wrong, and under one name the report could not say which.
        witness_family.Member(
            name="an_all_guarded_caller_reads_as_unreachable",
            claim="`fix_qualified` is built and its only caller is gated on a `[NotInScope]` "
            "suggestion; A5-as's aliases COMPILE, so nothing produces the error that "
            "reaches the fix — a capability with no entry point, not a missing capability",
        ),
        witness_family.Member(
            name="a_census_driven_caller_clears_unreachable",
            claim="adding an entry point that does not need a compiler error CLOSES the item — "
            "so the verdict tracks the fix rather than staying open on a file that still "
            "contains a guarded call",
            premises=("an_all_guarded_caller_reads_as_unreachable",),
        ),
    ],
)


def bucket(kind: str) -> tuple[Bucket | None, str | None]:
    """Return one directive bucket's live reading, or say why it is unmeasurable.

    ⚑ THE KEYS THEMSELVES, NOT A COUNT. The ordering ranks an item by a population it must be able
    to SEE; the prior body side-channelled a scalar and emitted no parts, so every one of these
    items was a size with nothing under it.
    """
    census, why = ratchet_census.census(GATE)
    if census is None:
        return None, why

    rows, why2 = kind_partition.kinds(GATE)
    if rows is None:
        return None, why2

    keys = tuple(k for k in census.added if k.rsplit(_SEP, 1)[-1] == kind)
    conc, _w = kind_partition.concentration(GATE, kind)
    found = conc or []
    top = f"{found[0].label} x{found[0].n}" if found else "-"
    return Bucket(kind=kind, keys=keys, providers=len(found), top=top), None


def uncovered() -> tuple[tuple[str, int], ...] | None:
    """Return `(kind, n)` for every added key of a kind NO bucket names, or None if unmeasurable.

    ⚑⚑ THE COVERAGE IS CHECKED, NOT ASSERTED, AND THAT IS THE AGGREGATE'S WHOLE REASON TO EXIST.
    Writing *"the three buckets cover the census"* in prose and not testing it is the same shape as
    a gate that verifies presence rather than behaviour. `kind_partition` already buckets malformed
    keys under their own label, so a key that does not parse for this gate's schema surfaces here
    too rather than vanishing.
    """
    rows, _why = kind_partition.kinds(GATE)
    if rows is None:
        return None
    return tuple((row.label, row.n) for row in rows if row.label not in BUCKETS)


def _callee(node: ast.Call) -> str | None:
    """Return the bare name a call invokes, whether attribute or plain."""
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def calls_guarded_by(tree: ast.Module, callee: str, guard: str) -> tuple[int, int]:
    """Return `(total calls, calls whose arguments mention `guard`)` for `callee` in `tree`.

    ⚑⚑ THE GUARD IS READ OFF THE CALL'S OWN ARGUMENTS, NOT OFF THE FILE. The original probe asked
    whether the STRING `m.group("sugg")` appears anywhere in the module — which is true of a file
    that also grew an unguarded caller, so it would keep reporting the item open after the very fix
    that closes it. Per-call is the reading the claim actually needs.

    ⚑ A BARE NAME COUNTS, NOT ONLY `m.group("sugg")`. The guard reaches the call as whatever the
    loop bound it to, so matching one spelling would be the census-keyed-on-one-spelling defect —
    an attribute, a keyword and a plain identifier all mean the same thing here.
    """
    total = driven = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _callee(node) != callee:
            continue
        total += 1
        args = [*node.args, *(kw.value for kw in node.keywords)]
        if any(guard in ast.dump(arg) for arg in args):
            driven += 1
    return total, driven


def parse(rel: str) -> ast.Module | None:
    """Parse one repo-relative source file, or None when it cannot be read.

    ⚑ STATIC, NEVER AN IMPORT. Importing `scratch/scope_alias` would give a promoted module a
    runtime dependency on `scratch/`, and it would answer a weaker question besides: a call site's
    GUARD is not visible to an import.
    """
    try:
        return ast.parse((corpus.ROOT / rel).read_text(encoding="utf-8"), filename=rel)
    except (OSError, SyntaxError):
        return None


@dataclass(frozen=True, slots=True)
class Reach:
    """Whether the `as` rewriter has a caller that a census — not a compiler error — can drive."""

    defined: bool
    calls: int
    driven: int

    @property
    def unreachable(self) -> bool:
        """Report whether every existing caller is gated on a compiler error.

        ⚑ DEFINED-BUT-ALL-DRIVEN IS THE OPEN STATE, and it is NOT the same as absent. A census
        that saw the function defined would report this clean — the *presence, never behaviour*
        shape — while a report of "absent" would say the plan's *not yet built* reading was right,
        which it is not. The two must stay distinguishable.
        """
        return self.defined and self.calls > 0 and self.driven == self.calls


def rewriter_reach() -> Reach:
    """Return whether `fix_qualified` can be driven without a compiler error.

    ⚑⚑ THE DEFINITION AND THE CALL SITE ARE READ FROM DIFFERENT FILES, DELIBERATELY. They live in
    different modules today and `scope_fix` re-exports the name, so a single-file probe reads a
    true answer off a file that no longer owns the definition. Naming both is what keeps the next
    move from making the probe silently wrong.
    """
    defined = False
    definition = parse(REWRITER_DEF)
    if definition is not None:
        defined = any(
            isinstance(node, ast.FunctionDef) and node.name == REWRITER
            for node in ast.walk(definition)
        )

    caller = parse(REWRITER_CALLER)
    if caller is None:
        return Reach(defined=defined, calls=0, driven=0)
    calls, driven = calls_guarded_by(caller, REWRITER, ERROR_GUARD)
    return Reach(defined=defined, calls=calls, driven=driven)


def _anchor(key: str, figure: str) -> tuple[int | None, str | None]:
    """Return the claim's own `[figure=N]`, or say why it could not be read."""
    try:
        return warrant_records.tag(key, figure), None
    except WarrantError as exc:
        return None, f"the claim carries no [{figure}=N] tag: {exc}"


def witness_bucket(
    key: str, kind: str, figure: str
) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield one part per added key of `kind`, then the bucket's verdict."""
    got, why = bucket(kind)
    if got is None:
        yield witness_row.opened(
            key,
            f"CANNOT MEASURE the ban census ({why}) — an unmeasurable census is not a clean one",
        )
        return

    want, unanchored = _anchor(key, figure)
    if want is None:
        yield witness_row.opened(key, unanchored or "unanchored")
        return

    for added in got.keys:
        yield witness_row.part(key, added, route=route(kind))

    sample = ", ".join(got.keys[:_SAMPLE]) or "none"
    if got.n != want:
        yield witness_row.opened(
            key, f"claim says {want}; the tree says {got.n} `{kind}` key(s){got.shape} ({sample})"
        )
        return
    if got.n:
        yield witness_row.opened(
            key, f"{got.n} `{kind}` key(s) still added over baseline{got.shape}: {sample}"
        )
        return
    yield witness_row.closed(key, f"no `{kind}` key is added over baseline")


def witness_aggregate(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the whole census's added keys, then the aggregate verdict INCLUDING coverage.

    ⚑⚑ THE COVERAGE FAILURE OUTRANKS THE COUNT, because it is the one thing no sub-item can
    report. A kind no bucket names leaves all three sub-items reading clean while the census
    refuses, so this branch is checked before the ordinary paydown comparison.
    """
    census, why = ratchet_census.census(GATE)
    if census is None:
        yield witness_row.opened(
            key,
            f"CANNOT MEASURE the ban census ({why}) — an unmeasurable census is not a clean one",
        )
        return

    want, unanchored = _anchor(key, figure)
    if want is None:
        yield witness_row.opened(key, unanchored or "unanchored")
        return

    for added in census.added:
        yield witness_row.part(key, added, route=route("*"))

    orphans = uncovered()
    if orphans:
        total = sum(n for _k, n in orphans)
        named = ", ".join(f"{k} x{n}" for k, n in orphans)
        yield witness_row.opened(
            key,
            f"{total} key(s) of a kind NO BUCKET NAMES: {named} — the sub-items cannot "
            f"cover this and would each read clean while the census refuses",
        )
        return

    rows, _why = kind_partition.kinds(GATE)
    shape = f" — {kind_partition.render(rows)}" if rows else ""
    sample = ", ".join(census.added[:_SAMPLE]) or "none"

    if census.over != want:
        yield witness_row.opened(
            key,
            f"claim says {want} added; the tree holds {census.over} of {census.held}"
            f"{shape} ({sample})",
        )
        return
    if census.over:
        yield witness_row.opened(
            key, f"{census.over} key(s) still added over baseline{shape}: {sample}"
        )
        return
    yield witness_row.closed(key, f"the ban census is at baseline ({census.held} held)")


def witness_reach(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the reach verdict for the `as` rewriter's entry point.

    ⚑ MEASURED BEHAVIOURALLY, BECAUSE PRESENCE IS EXACTLY WHAT IS NOT IN QUESTION. A census that
    saw `fix_qualified` defined would report this clean — and the function IS defined, and better
    than the plan credited. What is missing is a caller a census can drive.
    """
    want, unanchored = _anchor(key, figure)
    if want is None:
        yield witness_row.opened(key, unanchored or "unanchored")
        return

    got = rewriter_reach()
    if not got.defined:
        yield witness_row.opened(
            key,
            f"{REWRITER} is absent from {REWRITER_DEF} — the plan's 'not yet built' reading "
            f"would be correct, and this item would be the wrong one",
        )
        return
    if not got.calls:
        yield witness_row.opened(
            key,
            f"{REWRITER} is defined but {REWRITER_CALLER} calls it nowhere — a rewriter with "
            f"no caller at all, which is neither reachable nor error-driven",
        )
        return
    if got.unreachable:
        yield witness_row.opened(
            key,
            f"{REWRITER} is defined ({got.calls} call site(s) in {REWRITER_CALLER}) and "
            f"every one is gated on a compiler [NotInScope] `{ERROR_GUARD}`; the A5-as "
            f"aliases compile, so it can never fire for them",
        )
        return
    free = got.calls - got.driven
    yield witness_row.closed(
        key,
        f"{REWRITER} has {free} caller(s) not gated on a compiler error — a census-driven "
        f"entry point exists",
    )


def members() -> tuple[str, ...]:
    """Return every bib key this family answers for, in roster order."""
    return ("A5", *(f"A5-{kind}" for kind in BUCKETS), "A5-as-reach")


def witness(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Dispatch one family member by its bib key — the roster's single entry point.

    ⚑ KEYED DISPATCH, NOT FIVE EXPORTED WITNESSES, because the family IS one body at five values.
    A roster that named five functions would let one drift from the others, which is the drift the
    parameterization exists to make impossible.
    """
    if key == "A5":
        yield from witness_aggregate(key, figure)
        return
    if key == "A5-as-reach":
        yield from witness_reach(key, figure)
        return
    kind = key.removeprefix("A5-")
    if kind not in BUCKETS:
        yield witness_row.opened(
            key, f"{key} is not a member of this family — the roster holds {', '.join(members())}"
        )
        return
    yield from witness_bucket(key, kind, figure)
