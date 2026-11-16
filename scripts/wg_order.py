#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""wg_order.py — the worklist DAG: layers, leverage, and the ordered rows.

⚑ THIS IS A SEAM, NOT A NEW LAYER.  Split out of `worklist_gate.py` (1,458 code
lines, over the 1200 threshold) on 2026-08-11.  The seam is chosen by WHAT STATE
THE GROUP TOUCHES: everything here reads the WARRANT GRAPH — `warrants.bib`
edges, the derived failure nodes, each item's witness verdict — and produces the
`Row` sequence every report consumes.  It is the only group that walks a graph.

⚑ THE COST OF THIS MODULE IS `order()`, AND THE COST OF `order()` IS `reads()`.
Measured 2026-08-11 while splitting: `order()` calls `reads(_k)` once per bib
key, and `reads()` RUNS that item's witness with spies installed.  So the
ordering's price is the whole witness roster executed twice over (once for
openness via `_drain`, once for the footprint via `reads`) — which is why the
`--selftest` suite peaks at ~190 MB against a 192 MB lease and takes 4½ minutes.
That cost is in the WITNESSES, not in this file's line count; splitting the
module does not move it, and this note exists so the next reader does not
re-derive that measurement or expect the split to have paid for it.

⚑ `worklist_gate.py` RE-EXPORTS EVERY NAME HERE.  The public surface did not
move — a caller still writes `worklist_gate.order()`.
"""

import builtins
import collections
import os
import re
import sys

import wg_engine


def derived_failures(ledger=None):
    """{key: rec} — one VIRTUAL item per compiler-error class in the build census.

    ⚑ THE COMPILER ERROR IS A DAG ITEM (user, 2026-08-03: *"the individual
    compiler errors need to surface as DAG items so they can be matched to
    solutions"*).  I had this inverted: I was going to AUTHOR items for the 18
    todo labels with no bib entry, then match modules to them top-down — my
    judgement about which label covers what, which is the thing the tooling is
    supposed to replace.  The population is DISCOVERED from the build instead,
    and "no solution yet" stops being a gap in my authoring: it becomes a node
    with no incoming `enables`, computable per-run.

    ⚑ VIRTUAL — NOTHING IS WRITTEN.  These are derived at read time, the way
    the census is a projection of the build rather than a second store.  So
    there is no generated-file-versus-hand-edits conflict, no regeneration to
    remember, and no third peer to reconcile: `warrants.bib` stays 43 authored
    entries and the DAG the ordering walks is bib ∪ derived, recomputed every
    run and therefore unable to go stale.

    ⚑ CLASS-KEYED, WITH THE MODULES AS THE POPULATION.  A node per FAILING
    MODULE would put 44 copies of one edge in the graph (44 of the 115 are
    `NotInScope`); a node per ERROR CLASS carries one edge to one solution and
    holds its modules as `size`.  That mirrors how `A5-using`/`A5-as`/
    `A5-renaming` are already split by directive class rather than per import.
    Cone-ranking within a class stays available from the census rows.

    ⚑ OPENNESS IS NOT DECLARED HERE.  `order()` computes it by running each
    item's `check` witness; a virtual item's witness IS the census row, so it
    is open exactly while the class still has failing modules.  Nothing to
    author, nothing to keep in sync."""
    # ⚑ ONE PARTITION, ONE OWNER.  This walked the ledger and called
    # `SP._classify` itself — a THIRD derivation of the same relation beside
    # `figures._failures_by_kind` and `solvers()`.  When `_refine` split
    # `NotInScope` into three verdicts, the witness roster gained three keys and
    # this kept minting the old single node, so a derived node existed whose key
    # resolved to no witness.  The selftest caught it (`every derived node's key
    # IS its witness key`), which is the guard working — and the fix is to
    # DELETE the derivation, not to patch a third copy.
    sys.path.insert(0, wg_engine.LIBRARY)
    try:
        import figures as _F

        by_class, _ = _F._failures_by_kind()
    except Exception:
        return {}  # no census: no derived nodes, said by absence
    out = {}
    for kind, mods in by_class.items():
        # ⚑ THE NODE KEY IS THE KIND, matching its witness and its parts.  It
        # was `F:<kind>` while the witness registered `<kind>` and filed parts
        # under `F:<kind>` — three spellings, which forced the dispatcher to
        # carry `"F:"+key if in PARTS else key`.  A fallback that works is how
        # an undeclared convention survives long enough to break something.
        key = kind
        out[key] = {
            "claim": (
                f"no module fails with {kind} --- {len(mods)} module(s) "
                f"in the build census carry this class"
            ),
            # ⚑ A MISSING `check` IS A BUG IN THE NODE, NOT A STATE TO
            # ACCOMMODATE (user, 2026-08-03).  Two wrong turns, in order:
            # first I left `check` absent and let `openness=None` carry it —
            # measured, all 13 landed `open=None size=0`, in the graph and
            # invisible to the ranking.  Then I nearly "fixed" that by giving
            # derived nodes private `_open`/`_size` fields, i.e. a SECOND path
            # through the ordering, so a virtual node would be measured by a
            # different mechanism than an authored one.  That is the
            # derived-view defect being introduced deliberately.
            #
            # Every node — authored or derived — is open iff its `check`
            # witness says so.  A node whose `check` does not resolve is
            # DEFECTIVE, and the ordering already has the right word for it
            # (`openness=None`, reported not ranked).  The fix is to give these
            # a real witness, which is a worklist item, not a special case here.
            "check": "census:" + kind,
            "_derived": True,
            "_modules": sorted(mods),
        }
    return out


def order():
    """The worklist, TOPOLOGICALLY SORTED and ranked by unblocking leverage.

    ⚑ THIS WAS MY JUDGEMENT AND IT WAS WRONG ONCE ALREADY.  Plan section 59
    records the worklist ordered by what I happened to have open rather than by
    what unblocked the most -- sunk-cost ordering -- while three cheap
    high-leverage items sat untouched.  Section 55 then MEASURED that cone size
    and citation count differ by ~10x.  An order I assert is a guess; an order
    the DAG computes is a fact about the DAG.

    Two keys, in this precedence:

      1. TOPOLOGICAL LAYER -- an item cannot precede what it `rests-on`.  This
         is grounding, and it is the only hard constraint.
      2. LEVERAGE within a layer -- how many OPEN items transitively rest on
         this one.  That is the measured form of "greatest leverage to
         subsequent items", and it is why tooling sorts to the front without
         being privileged by hand: a tool that sizes N items has N dependents.

    ⚑ CLOSED ITEMS ARE REPORTED, NEVER RANKED.  Leverage counts only OPEN
    dependents, so finishing an item collapses the cone it was holding open --
    which is the ordering updating itself rather than aging."""
    sys.path.insert(0, wg_engine.LIBRARY)
    import contextlib
    import io
    import items as I

    root, why = wg_engine.engine()
    if root is None:
        print("worklist-gate: CANNOT ORDER -- %s" % why, file=sys.stderr)
        return 2
    if root not in sys.path:
        sys.path.insert(0, root)
    import paperkit.bib as B

    bib = B.parse(os.path.join(wg_engine.PROJECT, "warrants.bib"))
    # ⚑ THE DAG IS bib ∪ DERIVED, JOINED AT THE ONE BINDING.  Measured before
    # writing: `bib` is bound HERE and nowhere else on the ordering path (live
    # :197-391; `leverage` takes it as a parameter), so the join is one call
    # rather than a lift.
    bib.update(derived_failures())

    # verdicts first: openness is what leverage is measured over
    openness, _SIZES = {}, {}
    for key, rec in bib.items():
        chk = rec.get("check", "")
        label = chk.split(":", 1)[1] if ":" in chk else None
        fn = I.ITEMS.get(label)
        if fn is None:
            openness[key] = None  # unresolvable — reported, not ranked
            continue
        # ⚑ OPENNESS AND SIZE COME FROM ONE WALK (2026-08-05).  This called
        # `fn()` for the verdict and then read `I.SIZES` for the size — the two
        # halves of the OLD witness contract, and the THIRD caller that knew how
        # to run a witness (after `_row` and `items()`).  Under streaming a
        # witness returns a generator, so the direct call would have made every
        # item read as open, and the size — which the ORDERING SORTS BY — would
        # have silently gone to 0 for every converted witness.  Measured: `--
        # order` showed `A5-renaming`/`A5-using` at `size -` where they had
        # carried 97 and 83.
        #
        # ⚑ A SIZE THAT SILENTLY BECOMES 0 RANKS AN ITEM AS FREE WORK, which is
        # the same defect class as the OOM-killed witnesses that produced the
        # last tie set: the ordering adjudicating between figures that are not
        # there.  `_drain` returns `(rc, parts_forwarded)`, so the count is what
        # crossed the boundary — and for a legacy witness it still reads the
        # deposited size, so both contracts size correctly during the migration.
        with contextlib.redirect_stdout(io.StringIO()):
            _rc, _n = I._drain(label, fn)
        openness[key] = _rc != 0
        _SIZES[key] = I.SIZES.get(label) or _n

    # ⚑ A DANGLING GROUNDING EDGE IS REPORTED, NOT FILTERED AWAY (T28-closure).
    # This was `[d for d in rec.get("rests-on", []) if d in bib]` — so an edge
    # pointing at a key defined in NO bib simply vanished, and the ordering
    # showed an item resting on nothing with no trace that a premise had been
    # dropped.  The engine's `bib.rests_closure` returns `(reachable, dangling)`
    # precisely so that edge surfaces; we re-rolled the walk and kept only the
    # half that never complains.
    #
    # ⚑ AND IT MATTERS MORE NOW THAN WHEN THE ITEM WAS WRITTEN, because this
    # session started GENERATING `rests-on` edges from `reads()`.  An authored
    # bib is hand-checked; a derived edge is only as good as `figures.DERIVED`,
    # and the producer named there could be misspelled or retired.  MEASURED:
    # 0 dangling today, authored-only and authored+derived alike — so this is a
    # guard on a live generator, not a cleanup of existing debt.
    rests, dangling = {}, []
    for k, rec in bib.items():
        keep = []
        for d in rec.get("rests-on", []):
            if d in bib:
                keep.append(d)
            else:
                dangling.append((k, d))
        rests[k] = keep

    # ⚑ A DERIVED EDGE MUST ENTER THE GRAPH, NOT BE PRINTED AT A HUMAN (user,
    # 2026-08-03: *"an instrument is an operational dependency, and our dag
    # interleaves both, because operations depend on things that need
    # fixing"*).  `reads()` now TYPES a read as `op:` when it touches a derived
    # artifact, and `figures.DERIVED` names that artifact's producer -- so the
    # edge `<reader> rests-on <producer>` is DERIVABLE.  Until this, `rests`
    # was sourced from `warrants.bib` ALONE, so the ordering computed the edge,
    # printed "declare `rests-on CENSUS` in warrants.bib", and dropped it.
    # That is the printed-command-is-not-a-path defect (plan section 58b) inside
    # the ordering itself: a tiebreak whose resolution the tool already knows.
    #
    # ⚑ IT ALSO CLOSES A GAP NOBODY HAD NAMED: the 13 synthesized `other:*`
    # nodes appear in no bib entry, so they could never carry ANY edge and sat
    # at layer 0 as though nothing grounded them -- while every one of them
    # reads a ledger that declares itself STALE.
    #
    # ⚑ THE PRODUCER IS EXCLUDED FROM ITS OWN ARTIFACT'S READERS.  CENSUS's
    # witness reads the ledger it produces, so a naive union yields
    # `CENSUS rests-on CENSUS` -- a self-loop the layer walk would drop
    # silently, i.e. a wrong answer that looks like a measurement.
    sys.path.insert(0, wg_engine.LIBRARY)
    import figures as _FD

    for _k in list(bib):
        _prods = set()
        for _t in reads(_k) or []:
            if _t.startswith("op:"):
                _p = _FD.DERIVED.get(_t[3:])
                # ⚑ A DERIVED PRODUCER THAT NAMES NO ITEM IS DANGLING TOO, and
                # this is the half most likely to break: `figures.DERIVED` is
                # HAND-DECLARED, so a typo or a retired item makes every reader
                # of that artifact silently lose its grounding edge.  The
                # authored bib is reviewed; a generated edge is only as good as
                # the table behind it.
                if _p and _p != _k and _p not in bib:
                    dangling.append((_k, _p))
                elif _p and _p != _k:
                    _prods.add(_p)
        if _prods:
            rests.setdefault(_k, [])
            for _p in sorted(_prods):
                if _p not in rests[_k]:
                    rests[_k].append(_p)

    # ⚑ `enables` IS NOT `rests-on`, AND CONFLATING THEM IS THE ERROR SECTION 65
    # CAUGHT.  `rests-on` is GROUNDING: B3 cannot be true unless its premises
    # are.  `enables` is SEQUENCING: T17 does not make A5 true, it makes A5's
    # gate askable without an env-var bypass -- a tool that sizes the work.
    #
    # The first `--order` run made the distinction visible by getting it wrong:
    # T17 and T11 ranked at leverage ZERO, below every paydown, because nothing
    # grounds on them.  That is the sunk-cost ordering inverted -- the tooling
    # that unblocks the most sorting last.  So `enables` is read as a SEPARATE
    # edge: it contributes to the leverage rank and NOT to the topological
    # layer, because a tool is not a premise.  Unknown bib fields are dropped
    # silently by the parser, so this is additive and the engine ignores it.
    # ⚑ READ VIA `bibstruct`, NOT A LOCAL REGEX.  `bib._LIST` is a fixed
    # whitelist (`from`, `rests-on`, `reads`), so `enables = {...}` silently
    # becomes an empty list -- `rec.get("enables", [])` would return nothing
    # FOREVER while looking correct, the inert-guard shape.  Dropping unknown
    # fields is right for the ENGINE (it renders claims); reading them is this
    # ordering's own concern.
    #
    # ⚑ BUT MY FIRST FIX HAND-ROLLED THE GRAMMAR HERE -- a FOURTH parser of a
    # format whose own module documents being a consolidation of THREE that
    # "each re-derived the format and disagreed on which fields survive".
    # `scratch/bibstruct.py` is now the structural query surface, and its own
    # selftest immediately caught the defect my inline version shared: a
    # line-anchored field pattern misses `section = {s}, from = {A}` on ONE
    # line, which is how the real bib writes it.
    sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
    import bibstruct

    _fields = bibstruct.entries(os.path.join(wg_engine.PROJECT, "warrants.bib"))
    # ⚑ A DANGLING `enables` IS REPORTED TOO — same filter, same silence, one
    # edge kind over.  `enables` is SEQUENCING rather than grounding, so a bad
    # target does not make an item unsatisfiable; it makes a declared unblocking
    # relation vanish, and the tool that exists to rank by leverage quietly
    # ranks without it.
    #
    # ⚑ AND THE SPLIT PRODUCES A SPURIOUS EMPTY TOKEN.  `re.split(r"[,\s]+", "")`
    # returns `['']`, which `if d in bib` also absorbed — so an entry with NO
    # `enables` was indistinguishable from one whose target does not exist.  The
    # empty string is dropped as ABSENCE; a non-empty unknown is a finding.
    enables = {}
    for k, v in _fields.items():
        keep = []
        for d in re.split(r"[,\s]+", v.get("enables", "")):
            if not d:
                continue  # no `enables` field at all
            if d in bib:
                keep.append(d)
            else:
                dangling.append((k, d))
        enables[k] = keep

    # transitive dependents, over OPEN items only
    def _dependents(key):
        """One hop: the items that depend on `key`, by EITHER edge.

        ⚑ Grounding AND sequencing both count here, because both describe work
        that `key` unblocks -- but only `rests-on` sets the LAYER below, so a
        tool never becomes a false premise."""
        return [
            other for other in bib if key in rests.get(other, []) or other in enables.get(key, [])
        ]

    def cone(key):
        """Everything transitively depending on `key`.

        ⚑ THE WALK IS `dagcone.reach`, NOT A LOCAL RECURSION (user: *"that
        needs lifting to support dedup"*).  This was a hand-rolled closure over
        bib edges while `split_pipeline.leverage` ran the SAME closure over
        import edges -- two `leverage` defs under one name, the `agda_files()`
        class over a graph relation.  Both also called their result "what
        clearing this frees", so the overclaim had two homes to be fixed in.

        Only the EDGE RELATION differs between them, which is exactly the part
        a caller should supply."""
        return _dagcone().reach([key], _dependents)

    # ⚑ LAYER BY LONGEST PATH, not by a single pass: an item's layer is one more
    # than its deepest premise, so a chain cannot be reported as parallel.
    layer = {}

    def depth(key, stack=()):
        if key in layer:
            return layer[key]
        if key in stack:  # a cycle is a FINDING, not a crash
            return 0
        d = 0
        for dep in rests.get(key, []):
            d = max(d, depth(dep, stack + (key,)) + 1)
        layer[key] = d
        return d

    for k in bib:
        depth(k)

    # ⚑ THE TIE-BREAK IS COMPUTED, NOT NARRATED.  T11 and T17 both scored
    # leverage 9, and I broke the tie in PROSE -- citing a `from` edge, relative
    # size, and file overlap.  Three judgements, re-derived from scratch every
    # time anyone asks "what's next", which is the definition of reasoning that
    # should have been codified.  All three inputs were already here:
    #
    #   3. PROSE ORDER (`from`) -- the bib already states that T11 follows T17.
    #      An item whose premise is a tied sibling comes second, by declaration.
    #   4. SIZE -- each witness reports its own open population, and the figure
    #      is in the claim's `[tag=N]`.  Smaller first: it lands sooner and
    #      shrinks the tied sibling's population when the two overlap.
    #
    # Both are STRICTLY BELOW layer and leverage: a cheap item never jumps a
    # grounding edge, and never outranks one that unblocks more.  They only
    # decide between items that are otherwise equal -- which is exactly where I
    # was improvising.
    # ⚑ AND `from` — the third edge kind, the same filter, the same silence.
    # `from` is a CITATION: it says this item's premise was stated elsewhere, so
    # a target that does not exist means the citation names nothing and the
    # tiebreak that ranks a cited sibling ahead of its citer quietly stops
    # firing.  Three edge kinds, one drop, reported once.
    froms = {}
    for k, rec in bib.items():
        keep = []
        for d in rec.get("from", []):
            if d in bib:
                keep.append(d)
            else:
                dangling.append((k, d))
        froms[k] = keep

    def size(key):
        """The item's LIVE open population, from what its witness reported.

        ⚑ MY FIRST CUT READ THE CLAIM'S `[tag=N]` AND WAS INERT.  Every tag is
        the TARGET (`=0`, paid down), so the column printed `-` for all 18 items
        and broke no ties — a sort key that is constant is a sort key that does
        nothing, and it LOOKED like it was working.  Same shape as the four
        inert guards this repo has already paid for.

        The live gap is what the witness prints ("the tree says N", "holds N
        of M"), and it is already computed by the openness pass above.  Absent
        -> 0, sorting FIRST: an unmeasured item is trivial or unported, both
        cheap to look at.  Never a large sentinel — a missing measurement must
        not be mistaken for a big job."""
        return _SIZES.get(key, 0)

    rows = []
    keys = set(bib)
    for k in bib:
        # ⚑ ONE GRADED KEY, NOT TWO INDEPENDENT ONES (user: *"what you just
        # calculated IS leverage; what you're calculating as leverage is a
        # grade-0 calculation of leverage"*).  `lev` (declared cone) and
        # `blocked` (evaluated blockers) are the SAME relation at grades 0 and
        # 1.  Ranking them as separate columns let the stale grade outrank the
        # live one; the graded read compares at the HIGHEST AVAILABLE grade and
        # falls back only where grade 1 has not been evaluated.
        lev, blocked = leverage(k, bib, cone, openness, keys, enables)
        # a tied sibling that is this item's stated premise ranks ahead of it
        after = len([d for d in froms[k] if openness.get(d)])
        # ⚑ `None` (grade 1 UNAVAILABLE) sorts WITH the actionable, not against
        # them: an unmeasured item is unported or trivial, both cheap to look
        # at.  Treating "not evaluated" as "blocked" would bury exactly the
        # items whose grade-1 read is missing — a gap reading as a finding.
        graded = 1 if blocked else 0
        # ⚑ `deps` CARRIES THE LIST, NOT A JOINED STRING.  It was
        # `", ".join(rests[k])`, so the structure died at construction and every
        # consumer re-split it — and a membership test (`r.key in r.deps`)
        # silently became a SUBSTRING test: `"A5" in "A5-as, A5-using"` is True.
        # That is the bare-name-is-not-a-decidable-unit defect (T20) inside the
        # row type, and it made a self-loop check report four false positives.
        rows.append(
            Row(layer[k], graded, -lev, after, size(k), k, openness.get(k), lev, list(rests[k]))
        )
    rows.sort()
    # ⚑ THE CONE RIDES ALONG so `ties()` can ask the closure question without
    # re-deriving the walk.  A plain list cannot carry an attribute, so it is a
    # subclass — the alternative was for the caller to rebuild `cone`, and a
    # second derivation of one relation is how two views start disagreeing.
    out = _Rows(rows)
    out.cone = cone
    # ⚑ THE DROPPED EDGES RIDE ALONG TOO.  A grounding edge pointing at no item
    # was FILTERED OUT and the ordering said nothing — so a premise that cannot
    # be satisfied looked identical to an item with no premises.  Carrying it
    # here is what lets the report name it, the same reasoning as `cone`.
    out.dangling = sorted(set(dangling))
    return out


class _Rows(list):
    """The ordering's rows, carrying the cone walk that produced them."""

    cone = None
    dangling = ()


# ⚑ NAMED FIELDS, NOT POSITIONS.  Every consumer unpacked these rows
# positionally (`r[5]` for openness, `r[2]` for the key), so ADDING a sort key
# silently shifted all of them — the second time this session, and the first
# cost a `grouped`-out-of-scope crash.  A tuple whose meaning is its index is a
# bare name one layer up: not a decidable unit.
#
# ⚑ `graded` BEFORE `neg_lev` IS THE GRADING, IN THE FIELD ORDER.  Grade 1
# (evaluated: is anything blocking this today) is consulted first; grade 0
# (declared cone size) breaks ties WITHIN a grade-1 class.  The old order had
# them reversed, which let the declared reading outrank the evaluated one.
Row = collections.namedtuple("Row", "layer graded neg_lev after size key is_open lev deps")


def _content_size(key):
    """How many DEDUPED things this item folds — 0 when it folds nothing.

    ⚑ READ, NEVER RE-DERIVED.  Each witness already measures its own population
    and passes it as `size=`; recomputing it here would be a rival implementation
    of every census in `items.py`, and the two would disagree the first time
    either was fixed.

    ⚑ AND A MISSING SIZE IS 0, NOT 1.  An item with no measured content folds
    nothing and should rank on its edges alone; defaulting to 1 would give every
    unmeasured item a phantom unit of content and quietly re-flatten the very
    distinction this exists to draw."""
    sys.path.insert(0, wg_engine.LIBRARY)
    import items as I

    try:
        return int(I.SIZES.get(key, 0) or 0)
    except Exception:
        return 0


def leverage(key, bib, cone, openness, keys, enables=None):
    """LEVERAGE AT BOTH GRADES: (declared, evaluated).

    ⚑ THE REGRADE (user: *"what you just calculated IS leverage.  What you're
    calculating as leverage is a grade-0 calculation of leverage"*).  I had
    these as two sort keys — `neg_lev` from the cone and `waiting` from the
    witness — and defended them as different relations.  They are ONE quantity
    at TWO GRADES of the same read:

      * grade 0 — the DECLARED graph: `rests-on` + `enables`, closed
        transitively, evaluated against nothing.  This is what the bib says.
      * grade 1 — the EVALUATED graph: the same relation after each claim's
        witness has run against today's tree.  A discharged premise is an edge
        the declared grade still carries and the evaluated grade has dropped.

    Grade 0 is not a different measurement from grade 1; it is grade 1 with the
    evaluation not yet performed.  B3 `rests-on` EIGHT and waits on SEVEN — the
    same edge set, one grade apart, differing by exactly the discharge of S1.

    ⚑ WHY THIS IS NOT TWO SORT KEYS.  Ranking `neg_lev` above `waiting` treats
    them as independent criteria and lets a grade-0 figure outrank a grade-1
    one — the ungraded shadow, where a stale reading beats a live one because
    it was consulted first.  A graded quantity is compared AT ITS HIGHEST
    AVAILABLE GRADE, with the lower grade as the fallback when the higher has
    not been evaluated.  That is one key, not two.

    Returns `(declared, evaluated)`.  `evaluated` is None when the item has no
    witness to run — grade 1 is UNAVAILABLE, not zero, and the caller falls
    back to grade 0 rather than treating an unmeasured item as unblocked.

    ⚑ AND THIS IS NOT `split_pipeline.leverage`, DESPITE THE SHARED NAME (user:
    *"I question whether the concrete difference is legitimate"* -- checked, and
    for THIS one it is).  That function computes a cone; this one COMPOSES two
    readings of a graph it does not walk itself: the declared closure (via
    `cone`, now `dagcone.reach`) and the evaluated blockers (via `waits_on`,
    which RUNS witnesses).  The walk is one of two inputs.

    ⚑ AND MY DEFENCE OF IT WAS ALSO WRONG, ONE LEVEL IN (user: *"that's just a
    tree merge, though.  That doesn't feel distinct from what we're doing"*).
    I said this COMPOSES two readings and called that distinct from cone work.
    The declared half was `len([c for c in cone(key) if openness.get(c)])` --
    reach filtered by a per-node predicate, which is `dagcone.reach_where`.
    Combining readings of one graph per node is the same operation at another
    grade, not a different one.  What is left here is the PREDICATE and the
    second READING; both are about warrants, neither is about graphs.

    ⚑ THE SHARED NAME REMAINS A DEFECT, filed as T23 rather than deferred in
    prose.  `--rivals leverage` reporting REIMPLEMENTS twice is the honest
    state; pretending otherwise would staple a permission slip to a
    duplication."""
    # ⚑ `cone` IS THE CALLER'S CLOSURE and already delegates to `reach`, so the
    # filter composes with it rather than re-deriving the successor relation
    # here.  My first cut invented a `_dependents_of(bib, key)` that does not
    # exist -- the FIFTH invented API this session, and the reason each was
    # caught is that the call was checked before it shipped.
    # ⚑ THE COLLAPSE MUST NOT SHRINK THE RANK (user, 2026-08-02: *"something that
    # has hundreds or thousands of items doesn't get to have a leverage of any
    # smaller than its deduped content"*).  An item is a FOLD of its population --
    # `A5` is 216 ban keys shown as one row -- and counting only open items in the
    # cone charges 215 of those keys nothing, so the fold that made the worklist
    # readable also made it mis-ordered: `A5` (216) and `G1` (1) both scored 1.
    #
    # ⚑ AND IT IS NOT A FLOOR RULE.  I was about to enforce `leverage >= content`;
    # instead the content JOINS THE GRAPH, and `len(descendants) >= 216` holds by
    # construction -- no rule, no second grade to reconcile.  `_content_size` reads
    # the size the witness ALREADY measured, so this is a read, not a judgement.
    declared = len([c for c in cone(key) if openness.get(c)])
    declared += _content_size(key)
    for c in cone(key):
        if openness.get(c):
            declared += _content_size(c)
    if not openness.get(key):
        return (declared, None)  # a closed item orders nothing
    # ⚑ THE `enables` EDGES ARE PASSED, because an item cannot wait on what it
    # unblocks -- that is a cycle, and the bib is a DAG.  Without this,
    # `A5-as-reach` read as BLOCKED BY `A5-as`, the very item it exists to
    # unblock, and the highest-leverage item in the set sorted as waiting.
    blocking = waits_on(key, keys, (enables or {}).get(key, ()))
    return (declared, None if blocking is None else len(blocking))


def waits_on(key, keys, enables=None):
    """Tracked items this one names as its REASON for being open — GRADE 1.

    ⚑ THIS IS `leverage`'s EVALUATED GRADE, not a rival to it.  Kept as its own
    function because it returns the KEYS (which `--next` prints) where
    `leverage` returns the count; the grading lives in the caller.

    ⚑ THIS IS THE CHOICE I MAKE WHEN TOLD TO PICK (user: *"if I tell you to
    choose between B3 and R12b, which would you choose, and why? That's what
    needs mechanization"*).  I reached for R12b, and the reason was not
    preference: B3's own verdict says *"7 tracked gate item(s) still open"*,
    so working it now cannot change its verdict — every hour spent on it is
    spent on the seven.  R12b's verdict names no item: its blocker (CENSUS) is
    discharged and the WORK has simply not run.

    So the distinction is ACTIONABLE vs merely OPEN:
      * an item whose reason-for-being-open is OTHER TRACKED ITEMS is waiting;
      * an item whose reason is UNPERFORMED WORK is actionable now.

    ⚑ READ FROM THE WITNESS'S OWN REPORT, not from `rests-on`.  The declared
    edge says what the claim GROUNDS on; this says what is blocking it TODAY.
    Those differ exactly when a premise has been discharged — which is the case
    that decides this tie, and a static edge could never show it.

    ⚑ IS THIS JUST THE INVERSE OF LEVERAGE?  THE ANSWER TOOK THREE PASSES AND
    THE THIRD IS THE USER'S, WHICH RETIRES THE FIRST TWO:

      1. (mine, WRONG) *"a different relation"* — leverage is the transitive
         cone, this is one hop from the witness.  Defensible-sounding and it
         made them siblings.
      2. (mine, LESS WRONG) *"a different time, not a different source"* — the
         same graph before and after evaluation.  Closer, and still framed as
         two things that happen to agree about their subject.
      3. (user: *"what you just calculated IS leverage.  What you're
         calculating as leverage is a grade-0 calculation of leverage"*) — THE
         SAME QUANTITY AT TWO GRADES.  Not two relations, not two views: one
         relation, read at grade 0 (declared) and grade 1 (evaluated).  Pass 2
         still had them as a PAIR; this makes the lower one a DEGENERATE CASE
         of the higher.

    Why the correction changes the code and not just the prose: as a pair they
    were two sort keys ranked in sequence, so a grade-0 figure could outrank a
    grade-1 one.  As a grade they are ONE key read at its highest available
    grade — which is what `leverage()` above now returns.

    The observation that survives intact: `waits_on` counts items blocking THIS
    one while the cone counts items THIS one blocks, so the two are NOT
    antisymmetric.  B3 has the highest declared leverage in the set and cannot
    move — which is exactly why grade 0 alone ranked it and R12b as
    interchangeable."""
    sys.path.insert(0, wg_engine.LIBRARY)
    import contextlib
    import io
    import items as I

    fn = I.ITEMS.get(key)
    if fn is None:
        return None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            fn()
        except BaseException:
            pass
    text = buf.getvalue()

    # ⚑ SUBSTRING over the KNOWN key set, not a word scan: keys carry `-` and
    # digits, and `\b` is a `\w` transition (the `agda_lex.word` defect).
    #
    # ⚑ BUT A KEY IS ALSO A SUBSTRING OF ANOTHER KEY, and that shipped a wrong
    # answer the moment A5 was split: `A5-as`'s own report contains the text
    # "A5", so the bucket read as BLOCKED BY ITS OWN PARENT and the ordering
    # ranked three actionable items as waiting.  Same class as `V4` matching
    # `V4Compose` and `_-ℤ_`/`-ℤ_` -- a bare name is not a decidable unit.
    #
    # The fix is a DELIMITER TEST, not a longest-match: a key mentioned as a
    # blocker is surrounded by non-key characters, while `A5` inside `A5-as`
    # abuts `-`.  Key characters are alnum plus `-` (the shapes the census
    # actually emits), so a match whose neighbours are key characters is a
    # fragment of a longer key and not a citation of this one.
    def _cited(k):
        i = text.find(k)
        while i >= 0:
            before = text[i - 1] if i else " "
            after = text[i + len(k)] if i + len(k) < len(text) else " "
            if not _keychar(before) and not _keychar(after):
                return True
            i = text.find(k, i + 1)
        return False

    # ⚑ AND AN ITEM'S OWN FAMILY IS NOT ITS BLOCKER.  `A5-as-reach` exists to
    # unblock `A5-as`, so its verdict NAMES `A5-as` -- as its subject, not as
    # something waiting on it.  The delimiter test (added when A5 split) reads
    # that as a citation and ranked the highest-leverage item in the set as
    # BLOCKED by the very thing it unblocks.
    #
    # The relation is already declared: `enables` says this item unblocks that
    # one.  A key this item ENABLES cannot be a key it waits on -- that would
    # be a cycle, and the bib is a DAG.  Subtracting them is not a heuristic
    # about prose, it is the graph refusing to contradict itself.
    mine = set(enables or ())
    return sorted(k for k in keys if k != key and k not in mine and _cited(k))


def _dagcone():
    """The lifted cone authority — imported lazily so a bare run still parses."""
    sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
    import dagcone

    return dagcone


def _keychar(c):
    """Is `c` a character a worklist key can contain?

    ⚑ THE DELIMITER SET IS DERIVED FROM THE KEYS, not guessed: they are
    alphanumerics plus `-` (`A5-as`, `R14-v2`, `T12-rederive`, `keys-unique`).
    Anything else -- space, comma, colon, quote, end of line -- ends a key, so
    a match bounded by those is a citation and a match bounded by key
    characters is a fragment."""
    return c.isalnum() or c == "-"


def reads(key):
    """The FIGURES an item's witness consumes — its measurement footprint.

    ⚑ THIS IS THE ADJUDICATION RATIONALE, MECHANIZED (user: *"figure out the
    rationale you're using to make the distinction, and THAT is the thing to
    mechanize"*).  Facing the B3/R12b tie I reached for: *does either one's
    completion change the other's measurement?*  That is not taste — it is
    whether their witnesses read overlapping state, and it is derivable.

    Two items reading a SHARED figure are ordered by it: finishing one moves
    what the other measures, so doing them in the wrong order means re-measuring.
    Two reading DISJOINT figures are genuinely independent, and a tie between
    them is a real equivalence rather than a missing edge.

    ⚑ MEASURED BY RUNNING THE WITNESS, not by reading its source.  A witness
    calls a shared helper (`_ratchet_item`) and passes the gate name as an
    ARGUMENT, so a static call-graph sees one call site for eight items —
    `--calls ratchet_census` reports exactly that.  The figure a witness
    actually touches is a runtime fact, so the footprint is captured by
    recording what the figure layer served during the call.

    ⚑ AND THIS IS `order()`'s DOMINANT COST, MEASURED 2026-08-11.  `order()`
    calls this once per bib key, and each call RUNS that key's witness — so the
    ordering executes the whole witness roster a second time (after `_drain`).
    That is where the suite's ~190 MB peak and 4½-minute wall live; it is a
    property of the WITNESSES, not of any module's line count."""
    sys.path.insert(0, wg_engine.LIBRARY)
    import contextlib
    import io
    import figures as F
    import items as I

    fn = I.ITEMS.get(key)
    if fn is None:
        return None
    # ⚑ EVERY PROBE IS RESTORED, and the restore is the part that must not be
    # improvised: a spy left installed makes every LATER witness report the
    # previous one's footprint, which is a wrong answer that looks like a
    # measurement.  Saved as a list of (name, original) and undone in `finally`.
    seen = []
    # ⚑ THE POPULATION IS DISCOVERED, NOT DECLARED — and the declared version
    # reported a LIE, not a gap.  This was a hardcoded five-name allow-list, so
    # a witness reading state through any other route registered as `reads
    # nothing`, and `ties()` printed "measurement footprints are DISJOINT ... a
    # real equivalence, not a missing edge" for `T25-library` / `T28-closure`
    # while `pycodemod --touches` measured BOTH reading `scratch/pycodemod.py`.
    # An empty footprint is indistinguishable from an unmeasured one, so the
    # allow-list did not merely miss an item: it manufactured a confident
    # verdict of independence out of its own blind spot.  Same class as the four
    # `agda_files()` bodies under one name, and as `check_snapshot_guard`
    # censusing the predicate it declared rather than the one it meant.
    #
    # ⚑ TWO LAYERS, BECAUSE ONE DOES NOT COVER IT.  Spying `figures.*` alone
    # cannot see a witness that walks the tree itself: `T25-library` reaches
    # `pycodemod._cached_defs` over `items.py`, touching `F.ROOT` (a path
    # CONSTANT) and no instrumented figure at all.  So the figure layer is
    # discovered by introspection, and `open()` is spied underneath it to catch
    # every witness that reads a file by any other route.
    FIG = sorted(
        n
        for n, v in vars(F).items()
        if not n.startswith("_") and callable(v) and getattr(v, "__module__", None) == F.__name__
    )
    # ⚑ DISCOVERED BY WHAT THE FIGURE RETURNS, not by a name I remember.  A
    # figure whose result is a filesystem path is a CONSTRUCTOR — its argument
    # is a lookup input, not the identity of a measurement — so it reports one
    # token, not one per call.  Probing the return keeps this from becoming the
    # allow-list the paragraph above retires; a figure added tomorrow is
    # classified by its behaviour.
    # ⚑ READ THE CODE, NOT THE PROSE, AND NOT BY RUNNING IT.  Two wrong cuts:
    #   1. CALLING each figure with a probe string — which invoked
    #      `figures.main()` (a module-level callable like any other) and printed
    #      eighty `unknown flag 'S'` refusals.  Learning a type by triggering
    #      side effects is §61's class (a diagnostic that regenerates what it
    #      inspects).
    #   2. Matching `"path"` in the docstring's first line — which `build_log`
    #      does not contain (it says "the per-module `.agdai.log` for source"),
    #      so the set came out EMPTY and the fix silently did nothing.  A guard
    #      keyed on wording FAILS OPEN: no match reads as "not a path figure",
    #      and the `build-log:` wall came straight back.
    #
    # The structural fact is the RETURN STATEMENT: a figure that returns
    # `os.path.join(...)` constructs a path.  That is behaviour, checkable from
    # source, executing nothing — and it cannot drift when someone rewords a
    # docstring.
    import ast as _ast
    import inspect as _insp
    import textwrap as _tw

    PATH_FIGURES = set()
    for _n in FIG:
        try:
            _tree = _ast.parse(_tw.dedent(_insp.getsource(getattr(F, _n))))
        except (OSError, SyntaxError, TypeError):
            continue
        for _node in _ast.walk(_tree):
            if not isinstance(_node, _ast.Return) or _node.value is None:
                continue
            _v = _node.value
            if (
                isinstance(_v, _ast.Call)
                and isinstance(_v.func, _ast.Attribute)
                and _v.func.attr == "join"
                and isinstance(_v.func.value, _ast.Attribute)
                and _v.func.value.attr == "path"
            ):
                PATH_FIGURES.add(_n)
                break
    LABEL = {
        "ratchet_census": None,  # keyed by its argument, below
        "census_is_current": "census-stamp",
        "gates_without_universal_flags": "gate-flags",
        "gates_missing_check_argv": "check-argv",
        "own_agda_files_definers": "agda-files",
    }
    saved = [(n, getattr(F, n)) for n in FIG]

    def mk(name, original):
        def wrapped(*a, **k):
            # a ratchet figure is keyed by WHICH gate, since eight items share
            # one helper and differ only in that argument
            if name == "ratchet_census" and a:
                seen.append("ratchet:" + str(a[0]))
            elif name in PATH_FIGURES:
                # ⚑ THIS IS PREMATURE, NOT RIGHT, AND THE DISTINCTION IS THE
                # WHOLE ITEM (user, 2026-08-03: *"the fix is 'one error per
                # row', and the module is the route"*).  I read the per-module
                # `build-log:` tokens as noise and unkeyed the figure.  They are
                # redundant ONLY because a failure-class item currently emits one
                # row per MODULE — so the token repeats what the row already
                # says.  Make the row an ERROR and the module its ROUTE, and the
                # per-module footprint becomes exactly right: two classes reading
                # one module's log genuinely share a measurement, because that
                # log is where both their errors live.
                #
                # ⚑ `_classify` RETURNS ONE VERDICT PER MODULE, so the error-per-
                # row granularity does not exist anywhere yet — it is a change to
                # the CLASSIFIER's return, not to this spy.  Measured: Agda stops
                # at the first error per module, so errors == modules TODAY and
                # the collapse is invisible.  That is exactly the coincidence
                # that lets a wrong unit survive: it is numerically right for the
                # wrong reason, until a multi-error log arrives.
                #
                # RE-EXAMINE THIS BRANCH when `_classify` yields errors.  Below
                # is the reasoning that made it look correct.
                #
                # ⚑ A PATH CONSTRUCTOR IS NOT A KEYED FIGURE, AND KEYING IT BY
                # ARGUMENT REINTRODUCED THE WALL I FIXED THIS SESSION.
                # `ratchet_census(gate)` and `failing_modules(kind)` take an
                # argument that NAMES WHICH CENSUS — so the argument is part of
                # the measurement's identity.  `build_log(rel)` takes a module
                # path and returns a FILE PATH: the argument is an input to a
                # lookup, not an identity.  Keying it emitted one token per
                # module read, so six failure classes intersected on ~100
                # `build-log:` tokens and TIEBREAK 3 printed 9,456 characters.
                #
                # That is the `.agdai.log` path wall from the top of this
                # session, re-created by generalizing the ratchet special-case
                # without asking WHICH KIND of parameter each figure takes.
                # The generalization was still right; it just needed this
                # second kind named rather than assumed away.
                seen.append(LABEL.get(name) or name.replace("_", "-"))
            elif a and isinstance(a[0], str):
                # ⚑ A PARAMETERIZED FIGURE IS KEYED BY ITS ARGUMENT (user,
                # 2026-08-03: *"shouldn't `failing-modules` be splitting out
                # into virtual items? … it needs split up so it can be reasoned
                # about in a more fine-grained fashion"*).
                #
                # `ratchet_census` had this and NOTHING ELSE did, so
                # `failing_modules(kind)` — a figure whose whole job is to
                # project the failure set ONTO one kind — reported the same
                # bare token for all 13 derived nodes.  Six unrelated classes
                # then read as "shared measurement: failing-modules", i.e. as
                # if fixing `NoSuchModule` moved what `ParseError` measures.
                # It does not: they read one SOURCE and project it disjointly.
                #
                # ⚑ AND THE SPECIAL CASE WAS THE TELL.  Keying one figure by
                # argument and every other by name is the collapse this whole
                # sitting has been about, one layer in: a relation flattened to
                # a scalar because only one instance had been noticed.
                # Generalized rather than extended — a second named exception
                # would rot the same way.
                seen.append((LABEL.get(name) or name.replace("_", "-")) + ":" + a[0])
            else:
                # ⚑ AN UNDECLARED FIGURE REPORTS ITS OWN NAME, never KeyErrors.
                # `LABEL` is now a PRESENTATION table over a discovered
                # population, so a figure added tomorrow must degrade to a
                # readable default -- a lookup that raises would make the
                # discovery a liability and push the next reader back to the
                # allow-list this replaces.
                seen.append(LABEL.get(name) or name.replace("_", "-"))
            return original(*a, **k)

        return wrapped

    # ⚑ THE FILE-READ BOUNDARY IS THE LAYER THE FIGURES CANNOT COVER.  A witness
    # reaching the tree directly (`pycodemod._cached_defs` over `items.py`)
    # calls NO figure, so figure-spying alone reports it as reading nothing.
    # Keyed by repo-relative path: that is the same unit `--touches` derives
    # from the AST, so the two instruments become comparable rather than
    # merely both-present.
    real_open = builtins.open

    def spy_open(file, mode="r", *a, **k):
        try:
            p = os.path.abspath(file)
            if (
                isinstance(file, (str, bytes, os.PathLike))
                and "w" not in str(mode)
                and "a" not in str(mode)
                and p.startswith(F.ROOT + os.sep)
            ):
                rel = os.path.relpath(p, F.ROOT)
                if not rel.startswith(".git" + os.sep):
                    # ⚑ AN INSTRUMENT *IS* AN OPERATIONAL DEPENDENCY, AND THE
                    # DAG INTERLEAVES BOTH (user, 2026-08-03: *"an instrument is
                    # an operational dependency, and our dag interleaves both,
                    # because operations depend on things that need fixing"*).
                    #
                    # My first cut here folded `agda/_build/**` to one token and
                    # called a build artifact "an instrument, NOT a dependency"
                    # — suppressing the display instead of typing the edge, and
                    # DELETING a real edge in the process.  Every failure-class
                    # witness reads the leaf-verify ledger; that ledger has a
                    # PRODUCER (the census run), and until it runs every figure
                    # read from it is fiction — `census-current` says exactly
                    # that, in the figure layer, right now.
                    #
                    # So a read splits by what the path IS, not by how noisy it
                    # is in a report:
                    #   op:   a DERIVED artifact — some item produces it, so the
                    #         edge is `rests-on <producer>`, and two readers of
                    #         it are SIBLINGS UNDER that producer, not peers
                    #         whose completions move each other.
                    #   file: a SOURCE read — editing it is the work itself, so
                    #         two readers genuinely do move each other's figure.
                    # Collapsing the two is what made 6 unrelated failure
                    # classes report "finishing either moves what the other
                    # measures" — true of the substantive kind, false here.
                    kind = "file"
                    for _pfx in sorted(F.DERIVED, key=len, reverse=True):
                        if rel == _pfx or rel.startswith(_pfx + os.sep):
                            # ⚑ FOLDED TO THE ARTIFACT, NOT PER-FILE: 2810
                            # per-module logs are ONE artifact with one
                            # producer.  The fold is now a consequence of the
                            # typing (an op-token names an artifact) rather
                            # than a display hack that discards the edge.
                            rel, kind = _pfx, "op"
                            break
                    tok = kind + ":" + rel
                    if tok not in seen:
                        seen.append(tok)
        except Exception:
            pass  # a spy must never change what it observes
        return real_open(file, mode, *a, **k)

    # ⚑ THE DECLARED HALF, WHICH SPYING CANNOT REACH (user, 2026-08-04: *"That
    # means reads() was spying on the wrong thing."*).  `open()` measures the
    # TRANSPORT; a cached derivation performs no read, so its footprint came back
    # EMPTY and `ties()` reported a missing edge between items that share a
    # producer.  `agda_lex.observed()` is the same fact declared at the L2
    # wrapper, where the artifact is named — so a HIT and a MISS report
    # identically, and the edge stops depending on whether a cache was warm.
    try:
        sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
        import agda_lex as _lex

        _lex.observed(reset=True)  # drain, so this witness starts clean
    except Exception:
        _lex = None

    for n, original in saved:
        setattr(F, n, mk(n, original))
    builtins.open = spy_open
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            fn()
    except BaseException:
        pass  # a witness that raises still read what it read
    finally:
        builtins.open = real_open
        for n, original in saved:
            setattr(F, n, original)
    # ⚑ A DECLARED DEPENDENCY IS AN `op:` TOKEN, same as an observed one, because
    # it names the SAME KIND of thing: a derived artifact with a producer, whose
    # two readers are SIBLINGS UNDER that producer rather than peers.  Typing it
    # differently would split one relation across two vocabularies and put the
    # `free`-group classification back where it started.
    if _lex is not None:
        for _c in _lex.observed(reset=True):
            _tok = "op:" + _c
            if _tok not in seen:
                seen.append(_tok)
    return sorted(set(seen))
