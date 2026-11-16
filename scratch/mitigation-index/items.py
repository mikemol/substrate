#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The mitigation EDGE SET — `(site, remedy, witness)` — and its two projections.

⚑⚑⚑ THIS IS ONE RELATION, NOT TWO CROSS-LINKED TABLES.  The framing that
commissioned this project asked for "remedy rows cross-linked to arc rows"; the
operator collapsed it:

    "'refusal specifies the successor' … that's an EDGE IN A GRAPH.  And,
     honestly, an INDEX IS A COVERING WITNESS TO THE EDGES THAT EXIST."

A refusal is that edge QUERIED AT A POINT (given this defect here, what is the
remedy).  An index is the SAME EDGE SET ENUMERATED (given this remedy, what does
it cover).  So `--remedies` and `--arcs` below are PROJECTIONS of `EDGES`, not
two rosters that point at each other.  Two projections of one relation cannot
disagree; two cross-linked tables can, and that derived-view duplication is what
this repo keeps paying for.

⚑⚑ THE COVERING-WITNESS PROPERTY IS WHAT MAKES THIS FALSIFIABLE, and it can be
wrong in TWO directions — both findings:

  · an edge asserted by a refusal but ABSENT here      -> the index does not cover
  · an edge here with NO refusal implementing it       -> the UNREACHABLE REMEDY

`--cover` reports both.  The second is the one the operator most wants to see: a
remedy nothing routes to is a capability that exists and is functionally absent.

⚑ WHY THE EDGE SET IS STORED AT ALL, rather than recomputed per run.  This is the
argument `gate_census.py --successors` makes against itself in its own blind-spot
list:

    "a gate whose refusal is CORRECTLY TERMINAL — nothing populates it, so naming
     a successor would be a fabrication; THIS MODE CANNOT DISTINGUISH THAT FROM AN
     OMISSION."

A per-run census cannot tell "no successor exists" from "no successor found".  A
stored edge set can, because absence becomes a RECORDED CLAIM (`terminal=True`,
with the reason) rather than a silent gap.  That is a stronger argument for this
artefact than the review-surface argument, and it is why `terminal` is a field.

⚑ THE GATE ARM IS READ, NOT RE-IMPLEMENTED.  `gate_census.py --successors`
already extracts 35 rows of `(gate, kind, hint, witness)` and stores nothing.
`--successors-drift` SHELLS OUT to it and diffs its live rows against the
`GATE_ARM` edges recorded here, so this file cannot silently diverge from the
extractor it subsumes.  Do not re-derive its parse.

    items.py --remedies        # projection: remedy -> every site it covers
    items.py --arcs            # projection: arc -> its edges
    items.py --residue         # projection: the corruption arm — (damage, tool, cleaned?)
    items.py --overlap         # remedies ranked by shared sites (genericization candidates)
    items.py --cover           # the covering-witness audit, BOTH directions
    items.py --successors-drift# GATE_ARM vs `gate_census.py --successors`, live
    items.py <KEY>             # one edge's witness — the paperkit `check` target
    items.py --items [<KEY>]   # the witness ROSTER — what `bibstruct --add` resolves
    items.py --sibling <path>  # READ ⟡remedy-sweep's corpus — never re-sweep it
    items.py --list            # every edge's witness verdict
    items.py --selftest

⚑ NAMED `items.py` BECAUSE `bibstruct --add` RESOLVES `item:<KEY>` AGAINST
`findings.py` OR `items.py` BESIDE THE BIB, falling back to
`catalog/library/items.py`. A runner under any other name has every entry refused
against a project the filer is not using — measured here on the first `--add`.

Every mode reports `n of m`.
"""

import subprocess
import sys
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PY = os.path.join(REPO, ".venv", "bin", "python3")

# ⚑ `.venv/bin/python3` AND NOT `/usr/bin/python3`, WHICH IS 3.14 AND MAKES
# `pycodemod` REPORT `AttributeError — unparseable` ON EVERY FILE as a bare
# `0 definition(s)` WITH NO WARNING.  A witness that shells out to the wrong
# interpreter reports every edge as uncovered and looks like a real finding.
# This is why PY is absolute and never the ambient `python3`.


def _run(args, timeout=110):
    """Run a repo tool; return (rc, stdout).  A TIMEOUT IS REPORTED AS A TIMEOUT.

    ⚑ `check_divergence_ratchet --list` exited 137 (membudget cap) and
    `prose_apex --corpora` ran past 120s during this project's construction.
    Collapsing either into "empty" would report a fact about the MACHINE as a
    fact about the SUBSTRATE — the exact shape this index exists to make visible.
    """
    try:
        p = subprocess.run([PY] + args, cwd=REPO, capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after %ds — a fact about the run, NOT an empty result" % timeout


def _calls(name):
    """(rc, n_call_sites) for `pycodemod --calls <name>`.

    ⚑ NAME-SCOPED, NOT CAPABILITY-SCOPED, and every consumer of this must carry
    that limit.  `--calls emit` once returned "1 def, 1 call" and was written up
    as "there is exactly one OTLP emitter"; the second one is spelled `_emit_one`
    and was invisible to the query.  Measured again HERE while building this
    file: `--calls guard` returns 57 calls, but the population includes
    `sequitur.py`'s and `eliza`'s unrelated `guard` — so the count is an UPPER
    BOUND on the remedy's reach, never the reach itself.  Edges whose site count
    comes from this route carry `scoped="name"`.
    """
    rc, out = _run([os.path.join("scratch", "pycodemod.py"), "--calls", name])
    if rc != 0:
        return rc, None
    # Summary line: `<name>: 1 def(s), 40 call(s), 33 ref(s)` — the COUNT is the
    # token BEFORE `call(s)`, not a prefix of it.
    # ⚑ THE FIRST CUT SPLIT `call(s),` ITSELF and raised ValueError on the empty
    # stem. It crashed loudly, which is the only reason it was caught in one run
    # — a parse that had silently returned 0 would have banked every remedy as an
    # UNREACHABLE REMEDY, i.e. as this project's headline finding.
    for line in out.splitlines():
        if line.startswith(name + ":"):
            toks = line.split()
            for i, part in enumerate(toks):
                if part.startswith("call(s)") and i:
                    try:
                        return 0, int(toks[i - 1])
                    except ValueError:
                        return 2, None
    # ⚑ A PARSE MISS IS NOT A ZERO.  Returning 0 here would bank a false green.
    return 2, None


def _residue_verdict(edge):
    """THE THIRD FIELD, DECIDED — never asserted.  Returns (rc, verdict, why).

    ⚑⚑⚑ THE PREDICATE IS `agda_defs.py --stranded-residue`, WHICH IS READ AND
    NEVER RE-IMPLEMENTED.  It is the sibling's mode; it landed while this arm was
    being built.  This function SHELLS OUT to it and matches on the residue file
    path — exactly as `--successors-drift` shells out to `gate_census` rather than
    re-deriving its parse.

    ⚑⚑ AND THE FIRST CUT OF THIS FUNCTION DID RE-IMPLEMENT IT, WRONGLY, IN BOTH
    DIRECTIONS.  That is recorded here rather than deleted, because it is the
    argument for the delegation:

      · It asked `agda_defs.py <name>` — the TREE-WIDE definition index — and read
        R1 as `re-homed` because `Word` / `normalize` / `Canonical` happen to be
        bound as unrelated definitions elsewhere (`normalize` at nine modules).
        True, and not the fact the row needs.  The real mode checks binding
        against the SIBLING SET ONLY, and its own comment records that its first
        cut made this identical mistake and falsely retired `Word` on a
        coincidental global match.
      · It read R2 as `unused residue` — nothing binds `N-Carrier` / `G-N`
        tree-wide — while WithAction.agda:20-25 re-declares all of them as its own
        module parameters, i.e. REPAIRED.  `agda_defs` does not index module
        parameters, and `--telescope` reports `0 provider(s)` over
        Substrate.Groups.Coxeter regardless.

    ⚑ SAME HAND-ROLLED PREDICATE, OPPOSITE ERRORS: a common name read repaired
    when it was never checked, a distinctive one read unused when it was repaired.
    The second direction is the dangerous one — it would have shipped R2 as a file
    safe to delete, when deleting it loses the only record of a telescope its
    leaves depend on.

    ⚑ IT ALSO MISSED NAMES.  The hand roster for R2 was read off the residue by
    eye as four names; the real mode reports SIX, having caught `_≈N_` and `_≈H_`.
    A roster typed from a file is the same stored-cursor defect as a typed
    verdict, one level down — which is why `residue_names` below is documentation
    only and the VERDICT never consults it.

    Verdicts are the mode's own vocabulary, three-valued plus an honest fourth:
    `re-homed`, `live-damage`, `unused`, and `no-binders` (a residue that records
    a bare fixity or pragma and so binds nothing to re-home — reported rather than
    skipped, so "not this question" and "nothing to do" do not render alike).
    """
    art = edge.get("artifact")
    rc, out = _run([os.path.join("scratch", "agda_defs.py"), "--stranded-residue"])
    if rc == 124:
        return 2, "UNDECIDED", "TIMEOUT running agda_defs --stranded-residue"
    if rc != 0:
        return 2, "UNDECIDED", (
            "agda_defs --stranded-residue did not run — an unreadable census is "
            "not a clean one, so no verdict is reported")
    # Locate this artifact's block and collect the verdict tokens under it.
    lines = out.splitlines()
    where = [i for i, l in enumerate(lines) if l.strip() == art]
    if not where:
        # ⚑ ABSENT IS NOT CLEAN. The mode censuses every RESIDUE.md it finds; a
        # row missing from it means the FILE is gone (someone acted) or the mode
        # no longer sees it. Either way this index must not read that as repaired.
        return 2, "UNDECIDED", (
            "%s does not appear in the --stranded-residue census — the file may "
            "have been retired, or the mode no longer covers it. NOT read as "
            "re-homed." % art)
    seen = {}
    for l in lines[where[0] + 1:]:
        if not l.startswith("      "):
            break
        tok = l.split()
        if tok and tok[0] in ("re-homed", "live-damage", "unused", "no-binders"):
            seen.setdefault(tok[0], []).append(" ".join(tok[1:]) or "(no name)")
    if not seen:
        return 2, "UNDECIDED", "no verdict rows parsed under %s — refusing to guess" % art
    # ⚑ WORST-VERDICT-WINS, and the order is not arbitrary: a file with ONE
    # live-damage name is damaged whatever else it holds. Summing or majority-
    # voting would let two repaired names outvote one broken consumer.
    for v, rc_v in (("live-damage", 1), ("unused", 1), ("no-binders", 2), ("re-homed", 0)):
        if v in seen:
            others = ", ".join("%d %s" % (len(seen[k]), k) for k in seen if k != v)
            return rc_v, v, ("%d name(s): %s%s"
                             % (len(seen[v]), "; ".join(seen[v]),
                                (" [also %s]" % others) if others else ""))
    return 2, "UNDECIDED", "unrecognised verdict vocabulary in --stranded-residue"


# ── THE EDGE SET ────────────────────────────────────────────────────────────
#
# Each edge: the DEFECT SHAPE it answers, the REMEDY that answers it, the SITES
# the remedy reaches, the ARC that produced it, and a WITNESS that re-derives the
# edge.  `terminal` records a DELIBERATE absence (see the module docstring): a
# remedy with no refusal routing to it, where that is correct rather than an
# omission.
#
# ⚑ `sites` IS NEVER A FROZEN NUMBER.  It names the QUERY that recomputes it.
# A literal count here would be the restated-constant defect this repo has
# measured five times over (MEM_CAP as 128m at its authority and 256m in four
# other files, one of them the ratchet ENFORCING the cap).

# ⚑⚑⚑ TWO EDGE KINDS IN ONE LIST, AND THE SECOND IS A RELATION OVER TIME.
#
# A REMEDY edge (`kind="remedy"`, E1–E10) is a function of the tree's PRESENT
# SHAPE: given this defect shape, what answers it.  A RESIDUE edge
# (`kind="residue"`, R1–R4) is not — it is
#
#     (damage_instance, tool_that_now_prevents_it, cleaned?)
#
# and THE THIRD FIELD IS NOT DERIVABLE FROM THE FIRST TWO.  The proof is on disk
# and is the reason this kind exists at all:
#
#   `Groups/Coxeter/Core/IdemInequality/` and `Algebra/Quotient/Surreal/` have
#   IDENTICAL (a) — a split dropped a `module … (X : …) where` telescope, both
#   written by the SAME `split_lemmas.write_residue` — and IDENTICAL (b), and
#   OPPOSITE (c).  IdemInequality/Idem.agda:16 re-declares the whole telescope as
#   its own parameters (`split_telescoped` carried it).  Surreal/SurrealQuotient
#   .agda:29,32-33 USES `≤ⁿ-refl` / `≤ⁿ-trans` and binds neither, and
#   `agda_defs.py ≤ⁿ-refl` reports NO DEFINER in agda/Substrate.
#
# Any model keyed on the residue's SHAPE collapses those two: the residue TEXT is
# the same class of thing in both.  The discriminator is the RELATION between the
# artifact and its repair — the memory-mesh shape
# `the-fact-may-be-an-edge-not-a-property`, where a per-item predicate cannot
# express the distinction because the fact is an edge.
#
# ⚑⚑ SO WHY THE SAME LIST RATHER THAN A SECOND `RESIDUE_EDGES`.  Three consumers
# already close over `EDGES` — `--cover`, `--list`, and the `items-covers-edges`
# selftest that asserts `set(ITEMS) == set(_BY_KEY)`.  A parallel list needs its
# own roster, its own cover pass and its own selftest, which is three more places
# the two can disagree — the cross-linked-tables shape this whole artefact was
# collapsed out of.  A `kind` discriminator keeps ONE relation and makes
# `--residue` a THIRD PROJECTION alongside `--remedies` and `--arcs`.  Projections
# of one relation cannot disagree.
#
# ⚑ AND THE VERDICT IS RE-DERIVED, NEVER STORED.  A hand-typed `cleaned=True`
# would be a STORED CURSOR — a second write that must be made atomic with the work
# it describes, the defect this repo retired by name.  `_residue_verdict` below
# resolves the residue's bound names against the leaves ON EVERY RUN, exactly as
# E1-E6 re-derive a site count.

EDGES = [
    dict(
        key="E1-unstated-intent-argv",
        shape="unrecognised argument accepted, silently changes nothing",
        remedy="ratchet.check_argv",
        arc="argv-contract",
        sites=lambda: _calls("check_argv"),
        scoped="name",
        witness="scripts/ratchet.py:525 def; 40 call sites incl. 20 gate scripts",
        note="Refuses an argv token no mode claims. The site population is "
             "dominated by scripts/check_*.py, i.e. the gate roster.",
    ),
    dict(
        key="E2-guard-runs-too-late",
        shape="the guard is correct where it runs and runs too late",
        remedy="edit_snapshot.require_at_entry",
        arc="mutation-intent",
        sites=lambda: _calls("require_at_entry"),
        scoped="name",
        witness="scratch/edit_snapshot.py:1089 def; 35 call sites, all scratch/ writers",
        note="Paired with `pycodemod --unbound-snapshot`, which reports PLACEMENT "
             "and explicitly not NECESSITY — it has no read-path exemption.",
    ),
    dict(
        key="E3-silent-default-tenant",
        shape="a silent default answers a question the caller never stated",
        remedy="store.tenant",
        arc="wrong-tenant-read",
        sites=lambda: _calls("tenant"),
        scoped="name",
        witness="jea/metalanguage/store.py:370 def; 14 call sites",
        note="The recorded incident is that a per-dispatch --sandbox drifts so "
             "READ modes ignore it SILENTLY. One resolver; name the tenant in output.",
    ),
    dict(
        key="E4-defined-never-dispatched",
        shape="a capability defined and never dispatched",
        remedy="pycodemod --dead / --calls / --forwards",
        arc="dead-capability",
        sites=None,
        scoped="mode",
        terminal=("A MODE, NOT A FUNCTION — nothing CALLS it, so a call census is "
                  "the wrong instrument and would report 0 as if that were a "
                  "finding. Verified to RUN: `--dead scratch/vfs.py` returns "
                  "1 def with no caller, and self-reports SCOPED-RUN blindness."),
        witness="pycodemod.py --dead, exercised; mode present in the toolmodes census",
        note="The motivating incident is split_pipeline.rewire_only(): written, "
             "documented with a 354-consumer justification, ZERO callers.",
    ),
    dict(
        key="E5-census-counted-the-string",
        shape="the census counted the flag STRING, not the behaviour",
        remedy="pycodemod --calls/--rivals over --literal",
        arc="census-spelling",
        sites=None,
        scoped="mode",
        terminal=("A MODE. Its own failure case is recorded in this file's "
                  "`_calls` docstring: --calls is name-scoped, so it is BOTH the "
                  "remedy for --literal's substring defect AND subject to a "
                  "spelling defect of its own."),
        witness="pycodemod.py --calls, exercised on 6 names during construction",
        note="`--sql node` returns 82 sites almost all of which are node_child / "
             "obs_node / orbit_node — discarding those by eye is the judgement "
             "that belongs in a program.",
    ),
    dict(
        key="E6-positional-intent",
        shape="intent stated positionally, two propositions one spelling",
        remedy="check_snapshot_guard.intent_census",
        arc="mutation-intent",
        sites=lambda: _calls("intent_census"),
        scoped="name",
        witness="scripts/check_snapshot_guard.py:528 def; 2 call sites, both in-file",
        note="⚑ THE NARROWEST REMEDY IN THE SET — 1 def, 2 calls, no external "
             "caller. That is the overlap finding, not a defect: see --overlap.",
    ),
    # ── GATE_ARM: read from `gate_census.py --successors`, not re-derived ──
    dict(
        key="E7-gate-refusal-names-successor",
        shape="a refusal that does not say what to do next",
        remedy="ratchet.set_ratchet(refuse_hint=...)",
        arc="refusal-names-successor",
        sites=None,
        scoped="gate-arm",
        witness="gate_census.py --successors: 14 ratchet gates forward refuse_hint",
        note="The shared refusal. One authority, forwarded — the consolidated "
             "form of what 11 hand-rolled gates each spell separately.",
    ),
    dict(
        key="E8-hand-rolled-successor",
        shape="a refusal that does not say what to do next",
        remedy="per-gate hand-rolled successor token",
        arc="refusal-names-successor",
        sites=None,
        scoped="gate-arm",
        witness="gate_census.py --successors: 11 hand-rolled gates name a successor",
        note="⚑ THE GENERICIZATION CANDIDATE IN THE GATE ARM: 11 sites hand-roll "
             "what E7's refuse_hint does once. Presented as a candidate; whether "
             "they should consolidate is the operator's call.",
    ),
    dict(
        key="E9-successor-not-found",
        shape="a refusal that does not say what to do next",
        remedy=None,
        arc="refusal-names-successor",
        sites=None,
        scoped="gate-arm",
        terminal=("⚑ THE HONEST HOLE. 6 gates have a refusal path and name NO "
                  "successor. `--successors` CANNOT distinguish a correctly-"
                  "terminal refusal (nothing populates it) from an omission — "
                  "which is precisely why this edge set stores the row instead "
                  "of recomputing it. Recorded as a claim, not a silent gap."),
        witness="gate_census.py --successors: 6 'not found' rows",
        note="jea_metalanguage_gate (3 sites), check_feature_coverage (2), "
             "decl_shape_tag (1), law_motif_apex (1), reuse_sweep (2), "
             "set1_ratchet_cores (calls set_ratchet WITHOUT refuse_hint).",
    ),
    dict(
        key="E10-textual-guard-refuses-derived-roster",
        shape="a guard with a TEXTUAL predicate refuses the derived form of what it guards",
        remedy="items.py --items (dict-membership resolution)",
        arc="witness-roster",
        sites=None,
        scoped="mode",
        terminal=("FOUND BY BUILDING THIS PROJECT, not by sweeping. bibstruct's "
                  "`item:` resolver is a REGEX for a line-initial `\"<key>\": "
                  "lambda`, so the comprehension form — the one that CANNOT drift "
                  "from its authority — is invisible to it and every entry files "
                  "as unresolvable. The guard's own comment already records the "
                  "sharper half: `def D0_KERNEL(` existed while `--items D0-kernel` "
                  "still said unknown, because REGISTRATION is the real predicate "
                  "and the textual check is the weaker one. So the tool knows its "
                  "predicate is a proxy and still enforces the proxy."),
        witness="bibstruct --add refused a comprehension-registered witness, 2026-08-26",
        note="⚑ THE COST IS AN INVARIANT DOWNGRADE, and it should be visible to "
             "whoever decides whether to fix bibstruct: the roster moves from "
             "'cannot drift by construction' to 'cannot drift undetected' (the "
             "items-covers-edges selftest). The precedent registry carries 30 rows "
             "of exactly this drift, which is what the downgrade risks.",
    ),
    # ── RESIDUE ARM: (damage_instance, successor_tool, cleaned?) ─────────────
    #
    # ⚑ FOUR `RESIDUE.md` ON DISK, UNTRACKED, READ BACK BY NOTHING. All four were
    # written by `split_lemmas.write_residue`, all four are `??` to git, and no
    # pre-commit gate reads them — so the population is invisible to every
    # instrument this repo has. `write_residue`'s own docstring names the unmade
    # decision: "Re-home them deliberately, or delete them deliberately — but do
    # it as a decision, not as a side effect." NOTHING HAS EVER ASKED. These rows
    # are the asking; they still do not DECIDE, which stays the operator's call.
    dict(
        key="R1-residue-idem-inequality",
        kind="residue",
        shape="a split dropped a module telescope and recorded it as residue",
        remedy="agda_defs --repair-telescopes (restores a dropped telescope)",
        arc="dropped-telescope",
        sites=None,
        scoped="residue",
        artifact="agda/Substrate/Groups/Coxeter/Core/IdemInequality/RESIDUE.md",
        residue_names=["Word", "Canonical", "normalize",
                       "normalize-canonical", "canonical-is-fixed"],
        leaf_refs={},
        witness="agda_defs --stranded-residue: 5 re-homed, bound in .Idem and .Op",
        note="⚑ THE (a)-AND-(b)-IDENTICAL HALF OF THE DISCRIMINATING PAIR. Same "
             "damage class and same successor tool as R3, OPPOSITE verdict. "
             "IdemInequality/Idem.agda:16 re-declares the entire telescope as its "
             "own module parameters, and its header comment credits "
             "`split_telescoped`. ⚑ The parent IdemInequality.agda ALSO still "
             "exists, unlike R2/R3/R4 whose monoliths are gone — a difference the "
             "residue TEXT does not record and only a tree query can see.",
    ),
    dict(
        key="R2-residue-semidirect-product",
        kind="residue",
        shape="a split dropped a module telescope and recorded it as residue",
        remedy="agda_defs --repair-telescopes / --at <rev> for manual recovery",
        arc="dropped-telescope",
        sites=None,
        scoped="residue",
        artifact="agda/Substrate/Groups/Coxeter/SemidirectProductGroup/RESIDUE.md",
        residue_names=["N-Carrier", "_≈N_", "G-N", "H-Carrier", "_≈H_", "G-H"],
        leaf_refs={},
        witness="agda_defs --stranded-residue: 6 re-homed, bound in .Private and .WithAction",
        note="⚑ THE BRIEF FILED THIS UNDER `Algebra/Quotient/SemidirectProductGroup/` "
             "AND IT IS NOT THERE — the path on disk is Groups/Coxeter/. Corrected "
             "here rather than carried. ⚑⚑ THE REPAIR IS SELF-DOCUMENTING, which is "
             "rare and worth the row: WithAction.agda:11-14 records that it named "
             "N-Carrier/H-Carrier/_≈N_/_≈H_ throughout and BOUND NONE, was recovered "
             "from `--at 771283c8^`, and was then APPLIED to the sibling `Private`. "
             "That comment is the successor-tool half of this edge stated by the "
             "artifact itself. ⚑⚑⚑ AND THIS ROW IS WHY THE PREDICATE IS "
             "DELEGATED: a hand-rolled tree-wide-definition check read it "
             "`unused residue` — safe to delete — because nothing DEFINES "
             "`N-Carrier` anywhere, while the leaves bind all six as module "
             "PARAMETERS. It also missed `_≈N_` and `_≈H_`, which a roster read "
             "off the file by eye does not see. Six names, not four.",
    ),
    dict(
        key="R3-residue-surreal",
        kind="residue",
        shape="a split dropped a module telescope and recorded it as residue",
        remedy=None,
        arc="dropped-telescope",
        sites=None,
        scoped="residue",
        artifact="agda/Substrate/Algebra/Quotient/Surreal/RESIDUE.md",
        residue_names=["≤ⁿ-refl", "≤ⁿ-trans"],
        # ⚑ THE LEAF REFERENCES ARE RECORDED AS LOCATIONS, NOT AS A BOOLEAN. A
        # `referenced=True` bit would be the stored cursor again; a file:line is
        # a claim the reader can open. The BINDING half is still re-derived.
        leaf_refs={
            "≤ⁿ-refl": "Surreal/SurrealQuotient.agda:29",
            "≤ⁿ-trans": "Surreal/SurrealQuotient.agda:32-33",
        },
        terminal=("⚑ NO SUCCESSOR IS NAMED, DELIBERATELY. `--repair-telescopes` "
                  "would restore the dropped parameters, but SurrealQuotient.agda"
                  ":36-45 records these two as the Conway-induction witnesses "
                  "DEFERRED to Conway.OrderTrans / Conway.OrderLaws — so the "
                  "repair may be to complete those and IMPORT a proof rather than "
                  "to re-home a parameter. Naming a tool here would present a "
                  "guess as a route. The decision is the operator's."),
        witness="agda_defs --stranded-residue: live-damage on ≤ⁿ-refl and ≤ⁿ-trans, used by SurrealQuotient",
        note="⚑⚑⚑ THE LIVE-DAMAGE MEMBER, and the proof that (c) is not a function "
             "of (a) and (b). Identical damage class and successor tool to R1, "
             "opposite verdict. ⚑ NO REMEDY IS NAMED — deliberately: the dropped "
             "parameters are the Conway-induction witnesses that "
             "SurrealQuotient.agda:36-45 says are DEFERRED to Conway.OrderTrans / "
             "Conway.OrderLaws, so re-homing the telescope is not obviously the "
             "right repair and this index does not decide it. ⚑⚑ `--applied-args` "
             "IS BLIND TO THIS ROW and that is the argument for storing it: that "
             "mode reads `open import M x` where x is unbound, and this leaf "
             "references BARE names with no applied import at all. Live tree-wide "
             "count is 2 rows, neither of them this one.",
    ),
    dict(
        key="R4-residue-f2-fixity",
        kind="residue",
        shape="a split left a FIXITY declaration behind its operator",
        # ⚑ NO SUCCESSOR TOOL IS NAMED, and that is the row's second finding.
        # `--stranded-residue` DETECTS this class (`no-binders`) and nothing
        # REPAIRS it: `--stale-sections` is the nearest census and answers a
        # different question (a section spelling left by a rename, where nothing
        # was displaced). Naming it here would be the stale-deferral-comment
        # defect — a pointer that reads as a provider.
        remedy=None,
        arc="dropped-telescope",
        sites=None,
        scoped="residue",
        artifact="agda/Substrate/Algebra/F2/RESIDUE.md",
        residue_names=[],
        leaf_refs={},
        terminal=("⚑ A FIXITY DECLARATION BINDS NOTHING — it decorates an operator "
                  "defined elsewhere — so the three verdicts that decide R1-R3 all "
                  "presuppose a subject this row does not have. The mode does NOT "
                  "force it into one: `no-binders` is its own fourth verdict, "
                  "reported rather than skipped, so 'not this question' and "
                  "'nothing to do' do not render alike."),
        witness="agda_defs --stranded-residue: no-binders (not a telescope — a fixity line)",
        note="⚑ THE FOURTH VERDICT WAS THE SIBLING'S, NOT MINE, and finding it "
             "already there is the finding. This arm was designed three-valued on "
             "the brief's instruction and this row would not fit; the honest move "
             "was to record a gap. `--stranded-residue` had already named the "
             "class. ⚑⚑ WHAT REMAINS UNMEASURED, and no verdict covers it: `-_` is "
             "alive at Substrate.Algebra.F2.Op2, so the operator was re-homed "
             "across a 369-module subtree and only its `infix 8` was left behind. "
             "A lost fixity is a PRECEDENCE change — it typechecks silently, and "
             "`no-binders` correctly declines to call that either repaired or "
             "damaged.",
    ),
    # ── TRANSCRIPT-SOURCED MEMBERS OF THE CLASS ──────────────────────────────
    #
    # ⚑ FOUR WERE OFFERED BY THE MINER AND ONLY TWO ARE FILED. The other two are
    # recorded in R5's and R6's notes as REFUSED, with the reason, rather than
    # filed with a weak check — this project's whole claim is that a row is
    # CERTIFIED rather than asserted, and a row whose check cannot re-derive its
    # third field would be the `standing`-kind vacuity the design excludes.
    dict(
        key="R5-snapshot-arming-per-call",
        kind="damage",
        shape="a guard is armed per-call, so the SECOND write in a scope is unguarded",
        remedy="pycodemod --placement",
        arc="dropped-telescope",
        sites=None,
        scoped="mode",
        artifact="scratch/edit_snapshot.py (_snapshot_once arming)",
        successor_check=("toolmodes.py", "placement"),
        residue_names=[],
        leaf_refs={},
        terminal=("⚑ THE ARMING BUG IS SEPARATELY WITNESSED AND THE ATTRIBUTION IS "
                  "NOT. The transcript pairs it with `split_upstream` destroying a "
                  "monolith before its snapshot armed; the BUG is real and has its "
                  "own witness, the CAUSAL claim about that destruction does not. "
                  "So this row certifies the mechanism and explicitly declines the "
                  "incident: `--placement` re-derives WHEN a guard fires, which is "
                  "the arming question, and says nothing about what was lost."),
        witness="pycodemod --placement, the declared owner of guard-firing placement",
        note="⚑⚑ THE REFUSED HALF, RECORDED RATHER THAN DROPPED: "
             "`split_upstream destroyed a monolith before its snapshot armed` is "
             "UNCONFIRMED and is NOT filed as an instance. Filing it would take an "
             "unestablished cause from the transcript and give it a check that "
             "witnesses the MECHANISM while appearing to witness the INCIDENT — "
             "the shape where a datum verified makes the model around it feel "
             "audited.",
    ),
    dict(
        key="R6-sed-truncation-emptied-modules",
        kind="damage",
        shape="a textual rewrite truncated files to empty",
        remedy="edit_snapshot.guard (per-file recovery command)",
        arc="dropped-telescope",
        sites=None,
        scoped="mode",
        artifact="three modules emptied by sed-truncation (cleanup CONFIRMED 3x)",
        successor_check=("toolmodes.py", "unbound-snapshot"),
        residue_names=[],
        leaf_refs={},
        terminal=("⚑ THE ONLY TRANSCRIPT MEMBER WHOSE (c) IS CONFIRMED — cleanup "
                  "witnessed three times — and it is filed for exactly that "
                  "reason: it is the class's POSITIVE CONTROL, the instance where "
                  "the third field is `cleaned` and independently corroborated. "
                  "Without a confirmed-clean member, a census reporting 1 "
                  "live-damage of 4 would be indistinguishable from a census that "
                  "cannot see cleanup at all."),
        witness="edit_snapshot.guard — the successor that makes this class recoverable",
        note="⚑⚑ AND THE FIGURE THE BRIEF REFUTES IS STILL LIVE IN A GATE. "
             "`check_snapshot_guard` prints 'the shape that made 33 files "
             "unrecoverable' in its own remediation text. The 33 is "
             "`--applied-args 33 -> 0` — sites REPAIRED, not files lost — and the "
             "live tree-wide `--applied-args` count today is 2. NOT carried as a "
             "figure here; recorded as a location where it survives. ⚑ THE FOURTH "
             "TRANSCRIPT ITEM IS ALSO REFUSED: `--repair-telescopes` three layers, "
             "two landed, layer three abandoned to hand-work with a proposed "
             "ⓉREWIRE-LEAVES never built. An unbuilt proposal has nothing to "
             "re-derive, so it is a worklist item, not a certified edge.",
    ),
]

# ⚑ THE OVERLAP CLUSTER IS DECLARED AS A CANDIDATE AND NOT AS A DECISION.
# The brief names it: check_argv / store.tenant / intent_census / require_at_entry
# "may be FOUR SPELLINGS OF 'refuse an unstated intent'". Making that visible is
# this file's job; deciding it is the operator's, so `verdict` is deliberately
# absent from this structure and no mode prints one.
CLUSTERS = [
    dict(
        name="refuse an unstated intent",
        members=["E1-unstated-intent-argv", "E2-guard-runs-too-late",
                 "E3-silent-default-tenant", "E6-positional-intent"],
        shared="Each refuses to proceed when the CALLER'S INTENT was not stated: "
               "an argv token no mode claims (E1), a mutation with no declared "
               "intent (E2), a store read with no declared tenant (E3), a "
               "positional intent with two propositions in one spelling (E6).",
        against="They differ in WHAT is unstated and WHEN it is checkable. E1 is "
                "decidable from argv alone at entry; E3 needs a resolver with a "
                "tenant registry; E2 is a PLACEMENT contract (its own tool reports "
                "placement and explicitly not necessity); E6 parses a grammar. A "
                "single generic would have to take all four as strategies, which "
                "may be a shared interface rather than a shared body.",
    ),
    dict(
        name="a refusal names its successor",
        members=["E7-gate-refusal-names-successor", "E8-hand-rolled-successor",
                 "E9-successor-not-found"],
        shared="One relation at three levels of consolidation: forwarded from a "
               "shared authority (14), hand-rolled per gate (11), absent (6).",
        against="E9 is not a remedy at all — it is the recorded absence. Folding "
                "it into the cluster as a third 'implementation' would be the "
                "error this edge set exists to prevent.",
    ),
    dict(
        name="a census keyed on one spelling",
        members=["E4-defined-never-dispatched", "E5-census-counted-the-string"],
        shared="Both are MODES over the call graph rather than functions, and "
               "both answer 'does anything actually route here'.",
        against="⚑ NOT A GENERICIZATION CANDIDATE. E5 is the instrument E4 is "
                "read WITH; merging them would make the census its own witness.",
    ),
    dict(
        name="a split dropped a telescope",
        members=["R1-residue-idem-inequality", "R2-residue-semidirect-product",
                 "R3-residue-surreal", "R4-residue-f2-fixity"],
        shared="All four are `RESIDUE.md` written by the SAME "
               "`split_lemmas.write_residue`, all four untracked, all four read "
               "back by NOTHING — no gate in this repo opens them. Three record a "
               "dropped `module … where` telescope.",
        against="⚑⚑ THE CLUSTER IS NOT A CONSOLIDATION CANDIDATE, AND SAYING SO IS "
                "THE WHOLE POINT OF THE KIND. R1 and R3 are identical in damage "
                "class and successor tool and OPPOSITE in verdict, so any single "
                "remedy applied cluster-wide would repair one and corrupt the "
                "other's record. R4 does not even share the predicate — a fixity "
                "declaration binds no name. What they share is a WRITER and an "
                "unmade decision, which is a reason to ASK four times, not once.",
    ),
]

_BY_KEY = {e["key"]: e for e in EDGES}

# ⚑ THE WITNESS REGISTRY `bibstruct --add` RESOLVES `item:<KEY>` AGAINST, and the
# reason this module is named `items.py`. The resolver looks for `findings.py` or
# `items.py` BESIDE THE BIB before falling back to `catalog/library/items.py` — so
# a runner named anything else has its every entry refused against a project the
# filer is not using. That refusal FIRED here, correctly, on the first `--add`.
# ⚑ CONFORMING TO THE TOOL RATHER THAN ROUTING AROUND IT: the alternative was
# `cat >>`, which is on summit's floor as `friction-capability-summary-drifts` —
# a peer bypassed exactly these refusals and lost the duplicate-key, unresolvable-
# witness and dangling-edge checks in one move.
# ⚑⚑ SPELLED OUT, AND NOT BY PREFERENCE — A COMPREHENSION IS REFUSED. The first
# cut wrote `ITEMS = {e["key"]: (lambda e=e: _witness(e)) for e in EDGES}`, which
# is the non-drifting form and is exactly what this project would otherwise argue
# for. `bibstruct --add` rejected it: its resolver is a REGEX for a line-initial
# `"<key>": lambda`, so a roster derived from its own authority is INVISIBLE to
# the guard and every entry files as unresolvable.
# ⚑ SO THE DRIFT RISK IS REAL AND IS PAID DOWN AT THE SELFTEST INSTEAD — the
# `items-covers-edges` check asserts `set(ITEMS) == set(_BY_KEY)`, so a spelled
# roster that falls behind `EDGES` fails loudly rather than silently. That is the
# honest trade: the tool requires a textual registration, so the invariant moves
# from "cannot drift by construction" to "cannot drift undetected".
# ⚑⚑⚑ AND THIS IS ITSELF AN EDGE THIS INDEX SHOULD CARRY, filed as E10: a guard
# whose predicate is TEXTUAL refuses the very construction that would make the
# thing it guards non-drifting. Recorded rather than quietly worked around.
ITEMS = {
    "E1-unstated-intent-argv": lambda: _witness(_BY_KEY["E1-unstated-intent-argv"]),
    "E2-guard-runs-too-late": lambda: _witness(_BY_KEY["E2-guard-runs-too-late"]),
    "E3-silent-default-tenant": lambda: _witness(_BY_KEY["E3-silent-default-tenant"]),
    "E4-defined-never-dispatched": lambda: _witness(_BY_KEY["E4-defined-never-dispatched"]),
    "E5-census-counted-the-string": lambda: _witness(_BY_KEY["E5-census-counted-the-string"]),
    "E6-positional-intent": lambda: _witness(_BY_KEY["E6-positional-intent"]),
    "E7-gate-refusal-names-successor": lambda: _witness(_BY_KEY["E7-gate-refusal-names-successor"]),
    "E8-hand-rolled-successor": lambda: _witness(_BY_KEY["E8-hand-rolled-successor"]),
    "E9-successor-not-found": lambda: _witness(_BY_KEY["E9-successor-not-found"]),
    "E10-textual-guard-refuses-derived-roster": lambda: _witness(
        _BY_KEY["E10-textual-guard-refuses-derived-roster"]),
    "R1-residue-idem-inequality": lambda: _witness(_BY_KEY["R1-residue-idem-inequality"]),
    "R2-residue-semidirect-product": lambda: _witness(_BY_KEY["R2-residue-semidirect-product"]),
    "R3-residue-surreal": lambda: _witness(_BY_KEY["R3-residue-surreal"]),
    "R4-residue-f2-fixity": lambda: _witness(_BY_KEY["R4-residue-f2-fixity"]),
    "R5-snapshot-arming-per-call": lambda: _witness(_BY_KEY["R5-snapshot-arming-per-call"]),
    "R6-sed-truncation-emptied-modules": lambda: _witness(
        _BY_KEY["R6-sed-truncation-emptied-modules"]),
}


def _witness(edge):
    """Re-derive ONE edge. rc 0 = holding, 1 = OPEN, 2 = cannot witness.

    ⚑ NO `standing` KIND EXISTS HERE, DELIBERATELY. The precedent registry
    (`.claude/agents/findings.py`) reports 169 of 209 witnesses as `standing`,
    which its own `--kinds` mode labels "⚑ VACUOUS — passes unconditionally".
    An index whose checks cannot fail is the frozen roster this project was
    commissioned to not become, so every edge here re-derives something.
    """
    # ⚑ THE RESIDUE ARM RE-DERIVES ITS THIRD FIELD BEFORE ANY OTHER ROUTE IS
    # TRIED, including `terminal`. A residue row that fell through to the
    # terminal branch would report "mode executes" — a true statement about
    # pycodemod and a silent non-answer about the residue.
    # ⚑ THE RESIDUE ARM DELEGATES BEFORE ANY OTHER ROUTE IS TRIED, `terminal`
    # included. A residue row that fell through to the terminal branch would
    # report "mode executes" — a true statement about pycodemod and a silent
    # non-answer about the residue. ALL FOUR go through the one predicate,
    # including the fixity row: the mode's `no-binders` verdict covers it, so
    # this file needs no special case of its own.
    if edge.get("kind") == "residue":
        rc, verdict, why = _residue_verdict(edge)
        return rc, "%s — %s" % (verdict, why)
    if edge.get("kind") == "damage":
        # ⚑ A `damage` ROW HAS NO RESIDUE FILE, so no census decides its third
        # field. It re-derives the SUCCESSOR TOOL instead — that the mode which
        # now prevents this class still exists and is dispatchable. That is a
        # weaker claim than the residue arm's and is LABELLED as such rather than
        # dressed up: `mechanism-holds` never says the incident was cleaned.
        # ⚑⚑ AND IT MUST NOT FALL THROUGH TO THE GENERIC `terminal` BRANCH, which
        # runs `pycodemod --dead scratch/vfs.py` — a probe unrelated to this row,
        # reporting "mode executes" about a DIFFERENT mode. That is precisely the
        # vacuous-check shape this project excludes.
        tool, mode = edge["successor_check"]
        rc, out = _run([os.path.join("scratch", tool), "--find", mode])
        if rc == 124:
            return 2, "TIMEOUT resolving successor %s" % mode
        if rc != 0:
            return 2, "toolmodes --find did not run — cannot witness"
        if "0 hit(s)" in out:
            return 1, ("OPEN: successor %s RESOLVES TO NOTHING — the tool this row "
                       "names as the mitigation is gone" % mode)
        return 0, ("mechanism-holds: successor %s is declared and dispatchable. "
                   "⚑ THIS DOES NOT SAY THE INCIDENT WAS CLEANED — see `terminal`."
                   % mode)
    if edge.get("sites"):
        rc, n = edge["sites"]()
        if rc == 124:
            return 2, "TIMEOUT re-deriving site count — reported as a timeout, not as zero"
        if rc != 0 or n is None:
            return 2, "site census did not parse — refusing to report a count"
        if n == 0:
            return 1, "OPEN: remedy has ZERO call sites — an UNREACHABLE REMEDY"
        return 0, "holding: %d call site(s) [scoped=%s — an upper bound, see _calls]" % (n, edge["scoped"])
    if edge.get("terminal"):
        # ⚑ A TERMINAL EDGE STILL RE-DERIVES SOMETHING: that its remedy is
        # reachable at all. The `terminal` text explains WHY no call census
        # applies; it does not excuse the edge from being checked.
        if edge["scoped"] == "gate-arm":
            rc, out = _run([os.path.join("scripts", "gate_census.py"), "--successors"])
            if rc == 124:
                return 2, "TIMEOUT running gate_census --successors"
            if rc != 0:
                return 2, "gate_census --successors did not run — cannot witness"
            return 0, "holding: gate arm re-derived from gate_census --successors"
        rc, out = _run([os.path.join("scratch", "pycodemod.py"), "--dead",
                        os.path.join("scratch", "vfs.py")])
        if rc != 0:
            return 2, "mode did not execute — cannot witness"
        return 0, "holding: mode executes (terminal edge — no call census applies)"
    if edge["scoped"] == "gate-arm":
        rc, out = _run([os.path.join("scripts", "gate_census.py"), "--successors"])
        if rc == 124:
            return 2, "TIMEOUT running gate_census --successors"
        if rc != 0:
            return 2, "gate_census --successors did not run — cannot witness"
        return 0, "holding: gate arm re-derived from gate_census --successors"
    return 2, "no witness route — an honest gap, not a pass"


def _gate_rows():
    """Live rows from `gate_census.py --successors`, as (named, notfound, na)."""
    rc, out = _run([os.path.join("scripts", "gate_census.py"), "--successors"])
    if rc != 0:
        return None, out
    named = notfound = na = 0
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 3 or not parts[0].endswith((".py", ".sh")):
            continue
        if parts[1] == "no-refusal":
            na += 1
        elif parts[2] == "yes":
            named += 1
        elif parts[2] == "NO":
            notfound += 1
    return (named, notfound, na), out


def main(argv):
    if "--selftest" in argv:
        return _selftest()

    if "--remedies" in argv:
        rows = [e for e in EDGES if e.get("remedy")]
        for e in rows:
            rc, why = _witness(e)
            print("── %-34s %s" % (e["remedy"], {0: "holding", 1: "OPEN", 2: "UNWITNESSED"}[rc]))
            print("     answers  %s" % e["shape"])
            print("     arc      %s" % e["arc"])
            print("     sites    %s" % why)
            print("     witness  %s" % e["witness"])
            over = [c["name"] for c in CLUSTERS if e["key"] in c["members"]]
            if over:
                print("     overlaps %s" % "; ".join(over))
        print("\n%d remedy row(s) of %d edge(s)" % (len(rows), len(EDGES)))
        return 0

    if "--residue" in argv:
        # ⚑ A THIRD PROJECTION OF `EDGES`, not a second table. Same list, filtered
        # by kind — so it cannot disagree with `--list` or `--cover` about a row.
        # ⚑ BOTH KINDS OF THE CORRUPTION ARM. `residue` rows are the four
        # RESIDUE.md files, whose third field a census DECIDES; `damage` rows are
        # transcript-sourced instances with no residue file, whose third field is
        # carried by a mechanism check instead. Kept in one projection because
        # they are one class — a damage instance and its successor tool — and
        # split by kind only where the DECISION PROCEDURE differs.
        rows = [e for e in EDGES if e.get("kind") in ("residue", "damage")]
        tally = {}
        for e in rows:
            rc, why = _witness(e)
            # ⚑ TALLY ON THE VERDICT TOKEN, not the whole line: the damage arm's
            # text carries its own caveat, and splitting on the em-dash made two
            # identical verdicts tally as two distinct ones.
            verdict = why.split(" — ")[0].split(":")[0]
            tally[verdict] = tally.get(verdict, 0) + 1
            print("── [%s] %s" % (e["kind"], e["artifact"]))
            print("     names    %s" % (", ".join(e["residue_names"]) or
                                        "(none — records no binding)"))
            print("     successor %s" % (e["remedy"] or "(none named — see note)"))
            print("     VERDICT  %s" % why)
        print("\n%d residue row(s) of %d edge(s): %s"
              % (len(rows), len(EDGES),
                 ", ".join("%d %s" % (v, k) for k, v in sorted(tally.items()))))
        print("⚑ NO DECISION IS PRINTED. Re-home or delete is the operator's call; "
              "`write_residue`'s own\n  docstring asks for it as a decision, and this "
              "mode is the asking, not the answer.")
        return 0

    if "--arcs" in argv:
        arcs = {}
        for e in EDGES:
            arcs.setdefault(e["arc"], []).append(e)
        for arc in sorted(arcs):
            print("── %s" % arc)
            for e in arcs[arc]:
                print("     %-28s %s" % (e["remedy"] or "(no remedy — recorded absence)", e["key"]))
                print("       %s" % e["shape"])
        print("\n%d arc row(s) over %d edge(s)" % (len(arcs), len(EDGES)))
        return 0

    if "--overlap" in argv:
        ranked = sorted(CLUSTERS, key=lambda c: -len(c["members"]))
        for c in ranked:
            print("── %-30s %d member(s)" % (c["name"], len(c["members"])))
            for k in c["members"]:
                e = _BY_KEY[k]
                print("     %-34s %s" % (e["remedy"] or "(recorded absence)", k))
            print("   shared:  %s" % c["shared"])
            print("   against: %s" % c["against"])
            print()
        print("%d cluster(s) of %d edge(s) — CANDIDATES. No verdict is printed: "
              "whether these consolidate is the operator's call." % (len(ranked), len(EDGES)))
        return 0

    if "--cover" in argv:
        # ⚑ BOTH DIRECTIONS. An index that only lists is a snapshot.
        unreachable, uncovered = [], []
        for e in EDGES:
            rc, why = _witness(e)
            if rc == 1:
                unreachable.append((e["key"], why))
            if e.get("remedy") is None:
                # ⚑ AN EMPTY REASON IS THE DEFECT THIS DIRECTION EXISTS TO CATCH,
                # so it must not print as a blank line. A row with no remedy and
                # no recorded reason is a silent gap — say so.
                uncovered.append((e["key"], e.get("terminal")
                                  or "⚑ NO REASON RECORDED — a remedy-less row "
                                     "must say WHY, or it is the silent gap this "
                                     "audit reports."))
        gate, _ = _gate_rows()
        print("── direction 1: an edge here with NO refusal implementing it")
        for k, why in uncovered:
            print("     UNREACHABLE-REMEDY %s" % k)
            print("       %s" % why)
        if not uncovered:
            print("     none")
        print("── direction 2: a remedy whose site census is EMPTY")
        for k, why in unreachable:
            print("     ZERO-SITE %s — %s" % (k, why))
        if not unreachable:
            print("     none")
        print("── direction 3: refusals asserted by gate_census, absent here")
        if gate is None:
            print("     UNWITNESSED — gate_census --successors did not run")
        else:
            named, notfound, na = gate
            print("     gate_census live: %d named · %d not-found · %d n/a" % (named, notfound, na))
            print("     recorded here as E7 (forwarded) + E8 (hand-rolled) = named;"
                  " E9 = not-found. n/a is NOT an edge and is deliberately unrecorded.")
        # ⚑ DIRECTION 4 IS THE RESIDUE ARM'S, AND IT IS A DIFFERENT KIND OF
        # UNCOVERED. Directions 1-3 ask whether a REMEDY is routed to. This asks
        # whether a recorded DAMAGE INSTANCE is still open — an edge whose third
        # field re-derives as live-damage is a hole in the tree, not in the index.
        res = [e for e in EDGES if e.get("kind") in ("residue", "damage")]
        print("── direction 4: a recorded damage instance still OPEN")
        if not res:
            print("     none recorded")
        for e in res:
            rc, why = _witness(e)
            if rc == 1:
                print("     OPEN %s — %s" % (e["key"], why))
            elif rc == 2:
                print("     UNDECIDED %s — %s" % (e["key"], why))
        print("     ⚑ these four RESIDUE.md are UNTRACKED and read back by NOTHING "
              "in pre-commit;\n       `--stranded-residue` decides them and this "
              "index records the asking.")
        print("\n%d uncovered of %d edge(s); %d zero-site" %
              (len(uncovered), len(EDGES), len(unreachable)))
        return 0

    if "--successors-drift" in argv:
        gate, out = _gate_rows()
        if gate is None:
            print("gate_census --successors did not run — REFUSING to report drift, "
                  "since an unreadable census is not an agreeing one")
            return 2
        named, notfound, na = gate
        # Recorded expectation lives in the E7/E8/E9 notes.
        exp_notfound = 6
        ok = (notfound == exp_notfound)
        print("live   %d named · %d not-found · %d n/a" % (named, notfound, na))
        print("edges  E7+E8 = named · E9 = not-found (recorded at %d)" % exp_notfound)
        print("%s" % ("AGREES" if ok else
                      "⚑ DRIFT — the not-found population moved; E9's note is stale"))
        return 0 if ok else 1

    if "--sibling" in argv:
        # ⚑ THE SIBLING'S CORPUS IS READ, NEVER RE-SWEPT. ⟡remedy-sweep derived an
        # edge set over the FULL commentary corpus into a session-scratchpad cotype.
        # This project is the committed, CERTIFIED subset — every row here carries a
        # runnable check — so the two are a coarse/fine pair over one relation, not
        # duplicates. Re-running its sweep would be the duplication we were told to
        # avoid, and would also cost a corpus-wide pass this mode does not need.
        # ⚑ ITS PATH IS AN ARGUMENT, NOT A CONSTANT: a scratchpad path baked in here
        # would rot the moment the session id changes, which is the restated-constant
        # defect with a shorter half-life than usual.
        want = [a for a in argv if not a.startswith("--")]
        if not want:
            print("usage: items.py --sibling <path-to-edges.json>")
            print("  ⚑ the sibling cotype is session-scoped; pass its path rather "
                  "than baking one in")
            return 2
        import json
        try:
            with open(want[0], encoding="utf-8") as fh:
                d = json.load(fh)
        except FileNotFoundError:
            # ⚑ ABSENT IS NOT EMPTY. The sibling may simply not have landed yet.
            print("sibling corpus not present at %s — reporting ABSENT, which is "
                  "not the same as an empty edge set" % want[0])
            return 2
        except (json.JSONDecodeError, OSError) as e:
            print("sibling corpus unreadable (%s) — REFUSING to report a count, "
                  "since an unreadable corpus is not an empty one" % e)
            return 2
        n = len(d)
        keys = sorted(d)[:8] if isinstance(d, dict) else None
        print("sibling corpus %s: %d top-level %s"
              % (want[0], n, "key(s)" if isinstance(d, dict) else "row(s)"))
        if keys:
            for k in keys:
                print("     %s" % k)
        print("\n⚑ COARSE/FINE PAIR, NOT DUPLICATES: that corpus is the full "
              "commentary sweep\n  (uncertified, session-scoped). This project is "
              "the %d-edge certified subset,\n  every row carrying a runnable check. "
              "Both READ gate_census --successors." % len(EDGES))
        return 0

    if "--items" in argv:
        # ⚑ THE REAL PREDICATE bibstruct TESTS IS DICT MEMBERSHIP, not the presence
        # of a `def` — its own comment records `def D0_KERNEL(` existing while
        # `--items D0-kernel` still said `unknown item key(s)`. This mode is what
        # makes that resolvable here rather than asserted.
        want = [a for a in argv if not a.startswith("--")]
        if want:
            miss = [k for k in want if k not in ITEMS]
            if miss:
                print("unknown item key(s): %s" % ", ".join(miss))
                return 2
            for k in want:
                rc, why = ITEMS[k]()
                print("  %-12s %s" % ({0: "holding", 1: "OPEN", 2: "unwitnessed"}[rc], k))
                print("     %s" % why)
            return 0
        for k in sorted(ITEMS):
            print("  %s" % k)
        print("\n%d witness(es) registered of %d edge(s)" % (len(ITEMS), len(EDGES)))
        return 0

    if "--list" in argv:
        counts = {0: 0, 1: 0, 2: 0}
        for e in EDGES:
            rc, why = _witness(e)
            counts[rc] += 1
            print("  %-12s %-34s %s" % ({0: "holding", 1: "OPEN", 2: "unwitnessed"}[rc],
                                        e["key"], why[:70]))
        print("\n%d holding · %d OPEN · %d unwitnessed, over %d edge(s)"
              % (counts[0], counts[1], counts[2], len(EDGES)))
        return 0

    if len(argv) == 1 and argv[0] in _BY_KEY:
        e = _BY_KEY[argv[0]]
        rc, why = _witness(e)
        print("%s: %s" % (e["key"], why))
        return rc

    if len(argv) == 1:
        print("edges.py: no edge keyed '%s'. Known keys:" % argv[0])
        for k in sorted(_BY_KEY):
            print("  %s" % k)
        return 2

    print(__doc__.strip().splitlines()[0])
    print("\nusage: items.py <KEY> | --remedies | --arcs | --residue | --overlap"
          " | --cover | --successors-drift | --items | --list | --selftest")
    return 2


def _selftest():
    fails = []

    def ck(name, cond, why=""):
        if not cond:
            fails.append("%s: %s" % (name, why))

    ck("keys-unique", len(_BY_KEY) == len(EDGES), "duplicate edge key")
    for c in CLUSTERS:
        for m in c["members"]:
            ck("cluster-member-resolves", m in _BY_KEY, "%s names %s" % (c["name"], m))
    for e in EDGES:
        ck("edge-has-shape", bool(e.get("shape")), e["key"])
        ck("edge-has-witness", bool(e.get("witness")), e["key"])
        # ⚑ THE INVARIANT THAT KEEPS THIS FROM ROTTING INTO A ROSTER: an edge with
        # no site census MUST record WHY (terminal), or it is a silent gap.
        # ⚑ A RESIDUE ROW SATISFIES THIS VIA ITS OWN RE-DERIVATION, not an
        # exemption: `residue_names` IS the census (the query `_residue_verdict`
        # runs), exactly as `sites` is for the remedy arm. Widening the predicate
        # rather than special-casing the kind keeps one invariant over one list.
        ck("absence-is-recorded",
           bool(e.get("sites")) or bool(e.get("terminal"))
           or e["scoped"] == "gate-arm" or bool(e.get("residue_names")),
           "%s has neither a site census nor a recorded reason" % e["key"])
        ck("no-verdict-field", "verdict" not in e,
           "%s carries a verdict — consolidation is the operator's call" % e["key"])
    # ⚑ THE ROSTER MUST COVER THE RELATION. An edge with no registered witness is
    # an entry `bibstruct --add` refuses, so this catches the drift AT THE SOURCE
    # rather than at file time. The precedent's registry carries 30 rows of exactly
    # this drift (20 witness-only, 6 bib-only, 4 spelling pairs).
    ck("items-covers-edges", set(ITEMS) == set(_BY_KEY),
       "ITEMS and EDGES disagree — a witness roster drifting from its relation")
    ck("clusters-carry-against", all(c.get("against") for c in CLUSTERS),
       "a cluster with no counter-argument is advocacy, not a candidate")
    # A positive control: the witness machinery must be able to report OPEN.
    probe = dict(key="x", shape="s", witness="w", scoped="name",
                 sites=lambda: (0, 0))
    rc, _ = _witness(probe)
    ck("witness-can-report-open", rc == 1,
       "a zero-site remedy did not read as OPEN — the check cannot fail, so it is vacuous")
    # And must report a timeout as a timeout, never as a pass.
    probe2 = dict(key="y", shape="s", witness="w", scoped="name",
                  sites=lambda: (124, None))
    rc2, why2 = _witness(probe2)
    ck("timeout-is-not-zero", rc2 == 2 and "TIMEOUT" in why2,
       "a timeout did not read as unwitnessed")

    # ── RESIDUE-ARM INVARIANTS ────────────────────────────────────────────
    for e in EDGES:
        if e.get("kind") not in ("residue", "damage"):
            continue
        ck("residue-has-artifact", bool(e.get("artifact")), e["key"])
        # ⚑ A `damage` ROW MUST NAME THE SUCCESSOR ITS CHECK RESOLVES. Without
        # it the row falls to the generic terminal branch and reports "mode
        # executes" about an unrelated probe — a check that cannot fail.
        ck("damage-declares-successor-check",
           e["kind"] != "damage" or bool(e.get("successor_check")),
           "%s is a damage row with no successor_check — its witness would be "
           "vacuous" % e["key"])
        # ⚑ THE INVARIANT THAT KEEPS `cleaned?` FROM BECOMING A STORED CURSOR.
        # A residue row must carry NO decided field — the verdict is a function
        # of the tree, re-derived by `_residue_verdict` on every run. A row that
        # cached it would read correct on the day it was typed and drift
        # silently thereafter, which is the defect this repo retired by name.
        ck("residue-verdict-not-stored",
           not any(k in e for k in ("cleaned", "verdict", "status", "repaired")),
           "%s stores a verdict — it must be re-derived, never asserted" % e["key"])
        # ⚑ `residue_names` IS DOCUMENTATION, NOT THE PREDICATE, and the selftest
        # says so by checking only its shape. The verdict comes from
        # `--stranded-residue`; the hand-read roster for R2 was WRONG (four names,
        # actually six — `_≈N_` and `_≈H_` were invisible to an eye read). A
        # verdict that consulted this list would inherit that error.
        ck("residue-names-are-a-list", isinstance(e.get("residue_names"), list),
           "%s must declare its bindable names (possibly empty)" % e["key"])
        # A leaf_ref may only name a name the residue actually records.
        for n in (e.get("leaf_refs") or {}):
            ck("residue-leafref-resolves", n in e["residue_names"],
               "%s cites a leaf ref for %r which is not a residue name" % (e["key"], n))

    # ⚑ TWO POSITIVE CONTROLS FOR THE NEW ARM, matching the two the remedy arm
    # already carries. Without these, "1 live damage, 2 re-homed" would be a fact
    # about the instrument rather than about the tree.
    #
    # (1) the three-valued verdict must be able to SEPARATE live damage from
    #     unused residue on the SAME unbound name — the distinction the brief
    #     warns is over-reported when collapsed to two values.
    saved = globals()["_run"]
    CENSUS = ("-- a split's RESIDUE --\n"
              "  agda/X/RESIDUE.md\n"
              "      live-damage  aa\n"
              "          used by Some.Leaf\n"
              "      re-homed     bb\n"
              "  agda/Y/RESIDUE.md\n"
              "      unused       cc\n"
              "  agda/Z/RESIDUE.md\n"
              "      no-binders   (not a telescope)\n")
    try:
        globals()["_run"] = lambda a, timeout=110: (0, CENSUS)
        r_dmg = _residue_verdict(dict(artifact="agda/X/RESIDUE.md"))
        r_unu = _residue_verdict(dict(artifact="agda/Y/RESIDUE.md"))
        r_nob = _residue_verdict(dict(artifact="agda/Z/RESIDUE.md"))
        ck("residue-can-report-live-damage",
           r_dmg[0] == 1 and r_dmg[1] == "live-damage",
           "a live-damage row did not read as OPEN")
        # ⚑ THE THREE-VALUED CONTROL. `unused` must NOT collapse into damage:
        # bound nowhere and used nowhere is neither repaired nor breaking, and
        # a two-valued bit over-reports it as damage.
        ck("residue-can-report-unused", r_unu[0] == 1 and r_unu[1] == "unused",
           "an unused row did not read as unused — the verdict has collapsed to two")
        ck("residue-three-values-differ", r_dmg[1] != r_unu[1] != r_nob[1],
           "live-damage / unused / no-binders do not read distinctly")
        # ⚑ WORST-VERDICT-WINS: X holds one live-damage AND one re-homed name.
        # A majority or a sum would let the repaired name outvote the broken one.
        ck("residue-worst-verdict-wins", r_dmg[1] == "live-damage",
           "a file with both live-damage and re-homed names did not read as damaged")
        # An UNREADABLE census is not a clean one.
        globals()["_run"] = lambda a, timeout=110: (124, "TIMEOUT")
        r_to = _residue_verdict(dict(artifact="agda/X/RESIDUE.md"))
        ck("residue-timeout-is-undecided",
           r_to[0] == 2 and r_to[1] == "UNDECIDED" and "TIMEOUT" in r_to[2],
           "a timed-out census did not read as UNDECIDED")
        # ⚑ AND AN ABSENT ROW IS NOT A REPAIRED ONE — the failure mode that
        # would silently retire a residue file the mode stopped covering.
        globals()["_run"] = lambda a, timeout=110: (0, CENSUS)
        r_abs = _residue_verdict(dict(artifact="agda/NOPE/RESIDUE.md"))
        ck("residue-absent-is-not-clean",
           r_abs[0] == 2 and r_abs[1] == "UNDECIDED",
           "an artifact absent from the census read as a verdict rather than UNDECIDED")
        # ⚑ AND THE DAMAGE ARM'S OWN POSITIVE CONTROL: a successor that resolves
        # to nothing must read OPEN. Without this, "2 mechanism-holds" would be a
        # fact about the instrument.
        globals()["_run"] = lambda a, timeout=110: (0, "0 hit(s) for 'gone'")
        r_gone = _witness(dict(key="p3", kind="damage",
                               successor_check=("toolmodes.py", "gone")))
        ck("damage-can-report-open",
           r_gone[0] == 1 and "RESOLVES TO NOTHING" in r_gone[1],
           "a vanished successor tool did not read as OPEN")
    finally:
        globals()["_run"] = saved

    for f in fails:
        print("  FAIL %s" % f)
    # ⚑ THE TOTAL IS DERIVED FROM THE POPULATIONS IT COUNTS, never a literal.
    # 5 fixed + 4 per edge + 3 remedy-arm controls, plus the residue arm:
    # 3 per residue row + 1 per leaf_ref + 6 residue controls.
    _res = [e for e in EDGES if e.get("kind") in ("residue", "damage")]
    total = (5 + len(EDGES) * 4 + 3
             + len(_res) * 4
             + sum(len(e.get("leaf_refs") or {}) for e in _res)
             + 7)
    print("%d check(s), %d failure(s)" % (total, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
