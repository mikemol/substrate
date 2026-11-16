#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ban_witness` — the A5 family, and the false greens it prevents.

⚑⚑⚑ THE GUARD CASE IS THE SUBJECT. `A5-as-reach` asks whether the `as` rewriter can be driven
WITHOUT a compiler error, and the original probe answered it by asking whether the string
`m.group("sugg")` appears ANYWHERE in the caller's file. That predicate stays true of a file that
has also grown an unguarded caller — so it would keep reporting the item OPEN after the very fix
that closes it, and nothing would say why. The reading has to be per-call.

⚑⚑ AND THE OPPOSITE FALSE GREEN IS CASED TOO. Reading only "is `fix_qualified` defined" reports
this item CLEAN, because the function IS defined — the *a census verifies presence, never
behaviour* shape. Both directions need a case, because a probe that is wrong in one direction is
usually right in the other and reads as working.

⚑⚑ THE FIXTURES ARE WRITTEN HERE, NOT READ FROM THE LIVE CENSUS. Measured at extraction, the ban
gate holds 7411 keys with 375 added — so a live-census case would pin today's numbers and go green
or red the moment someone pays down an unrelated bucket. What the live tree IS good for is the
vacuity question, and that was asked once, before the module was written: the predicate can still
fail, which is why this family was ported rather than retired.

⚑ THE COVERAGE CASE ASSERTS A CONTAINMENT, NOT A COUNT. `BUCKETS` must be a proper subset of
`DIRECTIVES` — if someone "fixes" the aggregate by deriving its roster from the buckets, the
coverage check compares the partition against itself and can never fire again.

⚑⚑⚑ TWO ARMS HERE WERE UNSPLIT FAMILIES, AND THE SPLITS ARE DIFFERENT SHAPES. The reach arm
asserted a FIRES and a CLEARS over one predicate, and those are two ways to be wrong — a probe
that never fires is permanently pessimistic, one that never clears permanently quiet — so they are
now two arms with the clear resting on the fire. The roster arm asserted a count and five
memberships over the SAME roster, which is one claim through several comparisons and is left
fused; what came off it is the REFUSAL of an unowned key, which is a claim about the family's
boundary rather than about its contents.

⚑⚑⚑ AND ONE ARM EXISTS BECAUSE ITS SUBJECT PASSED IDENTICALLY WRONG. `GATE` carried a
`scripts.` prefix for the life of this module while every case here stayed green — the suite had
no arm that read the constant at all. See
`the_gate_is_named_the_way_gate_module_resolves_gates`: a suite that cannot distinguish two
spellings is what lets the wrong one survive, and the evidence for the defect lived on a
different gate entirely (gate-G359).
"""

from __future__ import annotations

import ast
import sys

from mikemol.witness import witness_row

from substrate import ban_witness, gate_module, ratchet_census

# A caller in which EVERY call to the rewriter is gated on the compiler's suggestion group — the
# live shape, and the one that makes the item open.
_ALL_DRIVEN = """
def loop(m, path):
    if fix_demand(name, path, dry):
        return
    if '.' in name and fix_qualified(name, path, dry, m.group('sugg'), alias_owner):
        return
"""

# The same file after the fix this item asks for: a census-driven caller beside the error-driven
# one. ⚑ THE OLD PROBE PASSES ITS OWN TEST HERE — the `sugg` string is still present — which is
# exactly the false OPEN this suite exists to catch.
_ONE_FREE = """
def loop(m, path):
    if '.' in name and fix_qualified(name, path, dry, m.group('sugg'), alias_owner):
        return

def from_census(rows):
    for name, path in rows:
        fix_qualified(name, path, dry=False)
"""

# A caller that names the rewriter nowhere — distinct from one whose calls are all guarded.
_NO_CALLS = """
def loop(m, path):
    fix_demand(name, path, dry)
"""

# A guard reaching the call as a BARE NAME rather than as `m.group('sugg')`. ⚑ THE SECOND
# SPELLING, because a census keyed on one spelling reports the method as the substrate.
_BARE_GUARD = """
def loop(sugg, path):
    fix_qualified(name, path, dry, sugg, alias_owner)
"""

# How many bib keys this family answers for.
_EXPECTED_MEMBERS = 5

# The bib keys the roster must name, one per entry in the warrants bib.
_BIB_KEYS = ("A5", "A5-as", "A5-using", "A5-renaming", "A5-as-reach")


def _guarded(text: str) -> tuple[int, int]:
    """Run the guard reader over a fixture."""
    return ban_witness.calls_guarded_by(
        ast.parse(text), ban_witness.REWRITER, ban_witness.ERROR_GUARD
    )


def an_error_driven_caller_is_reported_as_driven(out: list[str]) -> int:
    """Check a call carrying the compiler's suggestion group counts as error-driven.

    ⚑ THE LIVE SHAPE. `scope_fix`'s only call site passes `m.group('sugg')`, so the item is open
    for the reason its claim states — not because the function is missing.
    """
    calls, driven = _guarded(_ALL_DRIVEN)
    if (calls, driven) != (1, 1):
        out.append(f"selftest: the error-driven fixture read {calls} call(s), {driven} driven")
        return 1
    return 0


def a_census_driven_caller_beside_a_guarded_one_is_seen(out: list[str]) -> int:
    """Check an UNGUARDED caller is found even when a guarded one remains.

    ⚑⚑⚑ THE CASE THIS MODULE EXISTS FOR, AND THE ONE THE ORIGINAL PROBE FAILS. It asked whether
    `m.group('sugg')` appears anywhere in the file; here it does, and there is ALSO a
    census-driven entry point — so the old reading reports the item still open after the fix that
    closes it. Per-call is what tells the two files apart.
    """
    want_calls, want_driven = 2, 1
    calls, driven = _guarded(_ONE_FREE)
    if (calls, driven) != (want_calls, want_driven):
        out.append(
            f"selftest: the mixed fixture read {calls} call(s), {driven} driven — the "
            f"census-driven caller was not distinguished"
        )
        return 1
    return 0


def a_bare_name_guard_counts_as_a_guard(out: list[str]) -> int:
    """Check the guard is matched however it reaches the call, not by one spelling.

    ⚑ A CENSUS KEYED ON ONE SPELLING REPORTS THE METHOD AS THE SUBSTRATE. The loop may bind the
    suggestion to a local and pass it bare; reading only `m.group('sugg')` would call that caller
    free and close the item on a rewrite that changed nothing.
    """
    calls, driven = _guarded(_BARE_GUARD)
    if (calls, driven) != (1, 1):
        out.append(f"selftest: a bare-name guard read {calls} call(s), {driven} driven")
        return 1
    return 0


def a_caller_with_no_call_is_not_a_guarded_caller(out: list[str]) -> int:
    """Check zero calls is distinguished from all-calls-guarded.

    ⚑ THE POSITIVE CONTROL FOR THE COUNTER. Without it a reader that matched nothing would look
    identical to one whose every match was guarded, and both would report the item open — for
    opposite reasons, one of which is a broken probe.
    """
    calls, driven = _guarded(_NO_CALLS)
    if (calls, driven) != (0, 0):
        out.append(f"selftest: the no-call fixture read {calls} call(s), {driven} driven")
        return 1
    return 0


def an_all_guarded_caller_reads_as_unreachable(out: list[str]) -> int:
    """Check `unreachable` FIRES when every call to the rewriter is compiler-driven.

    ⚑⚑ DEFINED-BUT-UNREACHABLE IS A THIRD STATE, and collapsing it into either neighbour loses the
    item. Absent would mean the plan's *not yet built* reading was right; reachable would mean the
    work is done. This is the arm that says the middle state is expressible at all.
    """
    stuck = ban_witness.Reach(defined=True, calls=1, driven=1)
    if not stuck.unreachable:
        out.append("selftest: an all-guarded caller did not read as unreachable")
        return 1
    return 0


def a_census_driven_caller_clears_unreachable(out: list[str]) -> int:
    """Check `unreachable` CLEARS once a call that needs no compiler error exists.

    ⚑⚑ A VERDICT THAT ONLY EVER FIRES IS PERMANENTLY PESSIMISTIC, AND THAT IS INDISTINGUISHABLE
    FROM A CORRECT ONE while the item is open. The fire direction alone would keep reporting the
    item after the fix that closes it — which is the SAME defect the original string probe had,
    reintroduced one layer up in the verdict rather than in the reader.

    ⚑ IT RESTS ON THE FIRE ARM. A `Reach` whose `unreachable` is always False clears here
    trivially, so this claim only distinguishes anything where its sibling holds.
    """
    freed = ban_witness.Reach(defined=True, calls=2, driven=1)
    if freed.unreachable:
        out.append("selftest: a census-driven caller still read as unreachable")
        return 1
    return 0


def an_absent_rewriter_is_not_reported_as_unreachable(out: list[str]) -> int:
    """Check a missing definition reads as absent rather than as merely unreachable.

    ⚑ THE TWO DEMAND DIFFERENT WORK. Absent means build the rewriter; unreachable means give the
    built one an entry point — and the plan already recorded a built tool as unbuilt once, which
    is the confusion this separation exists to prevent.
    """
    if ban_witness.Reach(defined=False, calls=0, driven=0).unreachable:
        out.append("selftest: an absent rewriter read as unreachable")
        return 1
    return 0


def each_bucket_reports_its_own_added_keys(out: list[str]) -> int:
    """Check a bucket's size is its key count, and that the keys are carried, not summarised.

    ⚑⚑ THE ROWS WERE IN HAND ALL ALONG AND THE PRIOR BODY THREW THEM AWAY. Every one of these
    items shipped as a `size` with NO parts, so the ordering could rank them only by a number
    whose population it could not see. `n` deriving from the keys is what keeps a size and its
    rows from becoming two authorities.

    ⚑ THE POPULATED AND EMPTY BUCKETS ARE ONE LAW AT TWO POINTS, DELIBERATELY LEFT FUSED. Both
    assert `n == len(keys)`; the empty bucket is the instance that a hardcoded non-zero `n` would
    fail, so it is a SECOND POINT on one claim rather than a second claim. Neither guards the
    other, so there is no premise edge to declare either.
    """
    bad = 0
    got = ban_witness.Bucket(kind="as", keys=("a::b::as", "c::d::as"), providers=1, top="d x2")
    if got.n != len(got.keys):
        out.append(f"selftest: a bucket's n is {got.n} over {len(got.keys)} key(s)")
        bad += 1
    empty = ban_witness.Bucket(kind="hiding", keys=(), providers=0, top="-")
    if empty.n:
        out.append(f"selftest: an empty bucket reports n={empty.n}")
        bad += 1
    return bad


def a_bucket_reports_where_its_decisions_concentrate(out: list[str]) -> int:
    """Check the provider count rides with the key count in the verdict clause.

    ⚑⚑ A COUNT IS NOT A DECISION COUNT. 187 keys over 35 providers is 35 decisions and one sweep;
    187 over 187 is 187 hand-edits. A verdict carrying only the count says those are the same
    work, which is the reflex this clause replaces — and a bucket with no measured providers must
    say NOTHING rather than claim zero.
    """
    bad = 0
    got = ban_witness.Bucket(kind="as", keys=("a::b::as",), providers=35, top="X x21")
    if "35 provider(s)" not in got.shape or "X x21" not in got.shape:
        out.append(f"selftest: the concentration clause is {got.shape!r}")
        bad += 1
    blind = ban_witness.Bucket(kind="as", keys=("a::b::as",), providers=0, top="-")
    if blind.shape:
        out.append(f"selftest: an unmeasured concentration still spoke: {blind.shape!r}")
        bad += 1
    return bad


def a_kind_no_bucket_names_is_reported_by_the_aggregate(out: list[str]) -> int:
    """Check the declared buckets are a PROPER subset of the directives the ban names.

    ⚑⚑⚑ THE COVERAGE CHECK IS ONLY MEANINGFUL WHILE THIS HOLDS. If the bucket roster were derived
    from the partition — or widened to every directive — the aggregate would compare the census
    against itself and could never report an uncovered kind again. That is a census turned into a
    tautology, and nothing about the code would look different.

    ⚑ AND `hiding` IS THE WITNESS THAT THE GAP IS REAL. The ban skill's directive list has four
    entries and three have buckets; `hiding` measures zero today, so the sums agree BY
    MEASUREMENT rather than by construction.
    """
    bad = 0
    missing = [d for d in ban_witness.BUCKETS if d not in ban_witness.DIRECTIVES]
    if missing:
        out.append(f"selftest: bucket(s) that are not declared directives: {missing!r}")
        bad += 1
    if not [d for d in ban_witness.DIRECTIVES if d not in ban_witness.BUCKETS]:
        out.append(
            "selftest: every directive has a bucket, so the aggregate's coverage check "
            "compares the partition against itself and can never fire"
        )
        bad += 1
    return bad


def an_unmeasurable_census_is_open_not_clean(out: list[str]) -> int:
    """Check a bucket read that measures nothing still yields exactly one verdict naming why.

    ⚑⚑ A GATE THAT CANNOT BE READ HAS AN UNKNOWN STATE. Reporting it at baseline banks a green
    verdict nothing measured — the `census-green-is-a-fact-about-the-census` shape, and the reason
    every failure path in this family carries a REASON rather than a bare None.
    """
    rows = list(ban_witness.witness_bucket("A5-as", "no-such-kind-at-all", "ban-as"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    if len(verdicts) != 1:
        out.append(f"selftest: {len(verdicts)} verdict(s) for a bucket that measures nothing")
        return 1
    return 0


def every_declared_member_is_a_real_arm(out: list[str]) -> int:
    """Check the family's declared members are arms this suite actually runs.

    ⚑⚑⚑ A FAMILY NAMING A MEMBER NOBODY RUNS IS THE FALSE-PROTECTION DEFECT THE SHAPE EXISTS TO
    CATCH, turned on the shape itself. The declaration is prose plus a name; nothing about writing
    it forces the named arm to exist, so a renamed or deleted arm leaves the family claiming
    coverage it does not have — and reading as MORE rigorous than an undeclared suite while being
    less.
    """
    arms = {arm.__name__ for arm in _ARMS}
    missing = [name for name in ban_witness.FAMILY.names if name not in arms]
    if missing:
        out.append(f"selftest: the family declares members with no arm: {missing!r}")
        return 1
    return 0


def the_familys_premises_all_resolve(out: list[str]) -> int:
    """Check no declared premise names a member the family does not hold.

    ⚑ A DANGLING PREMISE READS AS PROTECTED AND IS NOT. `witness_family` computes this; asserting
    it here is what makes the computation load-bearing for THIS family rather than merely
    available.
    """
    got = ban_witness.FAMILY.dangling_premises()
    if got != ():
        out.append(f"selftest: the family carries a dangling premise: {got!r}")
        return 1
    return 0


def the_roster_answers_for_every_bib_key(out: list[str]) -> int:
    """Check the dispatch names all five bib entries this family owns.

    ⚑⚑ FIVE ENTRIES OVER ONE BODY IS THE WHOLE CLAIM, so a roster that silently dropped one would
    leave a bib key with no witness — and the worklist gate would report it as a missing item
    rather than as a family that shrank.

    ⚑ THE COUNT AND THE MEMBERSHIPS ARE ONE CLAIM, NOT SIX, AND ARE DELIBERATELY LEFT TOGETHER.
    They are two comparisons over the SAME subject — the roster — neither guarding the other, and
    each unreadable without its partner: the memberships alone admit a roster carrying extras, and
    the count alone admits a roster of the right size holding the wrong keys. Splitting them would
    produce two paragraphs restating one fact.
    """
    bad = 0
    roster = ban_witness.members()
    if len(roster) != _EXPECTED_MEMBERS:
        out.append(f"selftest: the roster holds {len(roster)}: {roster!r}")
        bad += 1
    for key in _BIB_KEYS:
        if key not in roster:
            out.append(f"selftest: {key} is not in the roster")
            bad += 1
    return bad


def a_key_this_family_does_not_own_is_refused(out: list[str]) -> int:
    """Check that dispatching an unowned bib key yields one OPEN verdict, not an answer.

    ⚑ ANSWERING FOR A KEY YOU DO NOT OWN IS THE SILENT-WRONG-TARGET SHAPE. The dispatch reads a
    bucket off a prefix strip, so a near-miss key (`A5-hiding` against the `ban-hiding` kind) is
    exactly the input a prefix-shaped implementation would answer CONFIDENTLY and wrongly. Refusal
    has to be observable as a verdict, since a caller cannot tell a wrong bucket from a right one
    by looking at the row.

    ⚑⚑ AND IT IS THE POSITIVE CONTROL FOR THE ROSTER CLAIM ABOVE. A dispatch that answered every
    key it was handed would satisfy every membership check in the roster arm while owning nothing
    — the roster would read complete because the boundary had dissolved.
    """
    rows = list(ban_witness.witness("A5-hiding", "ban-hiding"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    if len(verdicts) != 1 or not verdicts[0].is_open:
        out.append(f"selftest: an unowned key was not refused: {rows!r}")
        return 1
    return 0


def the_gate_is_named_the_way_gate_module_resolves_gates(out: list[str]) -> int:
    """Check `GATE` is spelled bare, and that the spelling actually censuses.

    ⚑⚑⚑ THIS ARM EXISTS BECAUSE ITS SUBJECT PASSED IDENTICALLY WRONG. `GATE` read
    `scripts.check_ban_ratchet` for the life of this module and every case here was green, because
    `check_ban_ratchet` happens to spell its own import `from scripts.ratchet import …` and so
    resolves under ordinary package import. **The suite could not tell the two spellings apart**,
    which is what let the prefix survive — and gate-G359's evidence for the defect lived on a
    DIFFERENT gate entirely.

    ⚑⚑ THE PREFIX IS THE FAILING DIRECTION AND IT IS SILENT. `gate_module` runs a sibling finder
    scoped to `scripts/` so a gate importing its siblings by bare name resolves — but only on its
    `_by_location` fallback, which a DOTTED name never reaches. The day this gate spells that
    import bare, as most of its siblings do, the census returns a REASON instead of a reading and
    the family reports UNMEASURABLE — which is *not clean* rather than a defect in the caller, so
    the failure would arrive attributed to the gate.

    ⚑ BOTH HALVES ARE ASSERTED, because either alone is satisfiable by the wrong thing. A string
    check alone passes against a name that is bare and does not exist; a census check alone passes
    against the prefixed spelling today, since both resolve for THIS gate right now. Together they
    say: named the house way, and that naming reaches a real census.
    """
    bad = 0
    if ban_witness.GATE.startswith(f"{gate_module.GATE_DIR}."):
        out.append(
            f"selftest: GATE carries a {gate_module.GATE_DIR}. prefix, which bypasses the "
            f"sibling finder: {ban_witness.GATE!r}"
        )
        bad += 1
    census, why = ratchet_census.census(ban_witness.GATE)
    if census is None:
        out.append(f"selftest: GATE {ban_witness.GATE!r} does not census: {why}")
        bad += 1
    return bad


_ARMS = (
    an_error_driven_caller_is_reported_as_driven,
    a_census_driven_caller_beside_a_guarded_one_is_seen,
    a_bare_name_guard_counts_as_a_guard,
    a_caller_with_no_call_is_not_a_guarded_caller,
    an_all_guarded_caller_reads_as_unreachable,
    a_census_driven_caller_clears_unreachable,
    an_absent_rewriter_is_not_reported_as_unreachable,
    each_bucket_reports_its_own_added_keys,
    a_bucket_reports_where_its_decisions_concentrate,
    a_kind_no_bucket_names_is_reported_by_the_aggregate,
    an_unmeasurable_census_is_open_not_clean,
    every_declared_member_is_a_real_arm,
    the_familys_premises_all_resolve,
    the_roster_answers_for_every_bib_key,
    a_key_this_family_does_not_own_is_refused,
    the_gate_is_named_the_way_gate_module_resolves_gates,
)

# ⚑ HAND-SUMMED, AND THAT IS THE SAME OPEN ITEM `edge_witness_selftest` RECORDS (⟡case-count-
# derived). `witness_family.Family.count` derives a total from a ROSTER; this suite's `_ARMS` are
# FUNCTIONS and the family's members are DECLARATIONS, joined only by the case above. Writing the
# derived number here would fake the reconciliation rather than perform it.
#
# ⚑⚑ TWO SPLITS, TOTAL UNCHANGED. The reach arm's 2 became 1 + 1 and the roster arm's 7 became
# 6 + 1 — both faithful, so the population is the same assertions under better names.
_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 2 + 2 + 1 + 1 + 1 + 6 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"ban-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"ban-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
