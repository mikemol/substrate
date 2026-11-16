# Ⓝ31 ⟡toolmodes-layers — draining `scratch/toolmodes.py`

**Goal: fully n-split the file, then RETIRE it.** Not "carve off a concern" — that strands,
because the only consumer of each extraction is inside the file being drained.

## ⚑⚑⚑ THE STRANDING IS THE LESSON, AND IT COST TWO MODULES BEFORE IT WAS NAMED

The per-file gate's refusal says: *"Extract the one concern you need into a NEW module, written
clean in one pass, and let the next consumer import that instead."* Read literally that is
**carve off a piece**, and it is right whenever the consumer is elsewhere. When the consumer is
INSIDE the monolith, wiring the new module in is an edit to the monolith — refused — so the
extraction lands a clean module nothing imports: a built-then-orphaned rung, not a repair.

MEASURED this session, twice:

| extraction | suite | consumer | outcome |
|---|---|---|---|
| `substrate/compile_recipe.py` | 16/16 | `gen_build_makefiles.flat_text` (291 findings) | ⚑ STRANDED |
| `substrate/tool_population.py` | 14/14 | `toolmodes.roster` (2,196 findings) | ⚑ STRANDED |

⚑ **THE GATE'S MESSAGE NOW SAYS SO** (`scripts/pycheck_message.py`, this session): *"BUT IF THE
ONLY CONSUMER IS INSIDE THIS FILE, ONE EXTRACTION STRANDS… the move is to keep cutting until the
DISPATCH moves out as well, then RETIRE this file. Extracting one concern is a step; draining the
file is the finish."* Operator: *"That's why we fully n-split the file, so that we can retire the
original file and replace it."*

## ⚑⚑ PARITY AGAINST THE ORIGIN IS THE CHECK THAT EXPIRES

A rewritten reader that DISAGREES with the one it replaces is the real risk of a split, and it is
**invisible to a suite written against the new module** — cases pin whatever the rewrite happens
to do, so a faithful rewrite and a subtly broken one both go green.

The origin is still on disk and still runs during the split. That is the only window in which the
comparison exists, so every layer is parity-checked BEFORE its cases are written:

    substrate/tool_usage vs toolmodes.parse_usage
      → 432 tool(s) compared, 0 disagreement(s)   [modes, signatures AND glosses]

⚑ The probe lives in the session scratchpad, not the tree: it is scaffolding for the split and
becomes meaningless the moment the origin is retired. What survives is the per-layer suite.


⚑⚑⚑ **WHAT PARITY CAUGHT THAT NO SUITE WOULD HAVE — the argument for the next n-split.**
Each defect below passed its own cases. A case tests what its author thought of; parity tests what
the origin actually did, which is a different question and the only one that catches a
transcription. **Recorded here because the instrument does not survive the retirement.**

| defect | how it presented | why cases could not see it |
|---|---|---|
| **5 dropped stopwords** in the near-miss stoplist | 19/19 green; parity showed differing near-miss sets | the fixtures used none of the five. A transcribed CONSTANT is asserted by nothing — cases test the ALGORITHM over the constant, never the constant |
| **two header spellings dropped** (`modes:`, `optional arguments:`) | 20/20 green; parity showed **3 tools losing EVERY mode** | every fixture used a spelling the parser knew. The fixtures were written FROM the parser, so they exercised only what it already handled |
| a symmetric relation compared as ordered tuples | 12 false siblings | ⚑ the PROBE was the defective half — a disagreement is a hypothesis about either side |
| `parse_usage` compared against a `modes_of` that unions the option roster | 39 false disagreements | the layer boundary was drawn differently on the two sides |
| the intended `substrate/` widening | population differed by ~150 | a probe reports DIFFERENCE, not defect; an intended change reads identically to a regression |

⚑⚑ **ONE PATTERN: a transcribed CONSTANT and a transcribed CASE-SPACE are invisible to cases
derived from the same reading.** Both the stopword list and the header spellings were copied by
eye, and both suites were written by the reader who copied them — so the suite inherits the
transcription's blind spot exactly. Parity does not, because the origin never read the
transcription.

⚑ **THE LAST THREE ROWS ARE THE COST SIDE, kept deliberately.** Three of five findings were probe
defects or intended changes misread as regressions — false disagreements outnumbered real ones
3:2. A parity probe is a second implementation carrying a second implementation's bugs; its output
is evidence, never a verdict.

**For the next n-split:** write the probe against the origin BEFORE the cases, budget for triaging
probe bugs first, and record what it caught in the arc file — the origin is deleted at the end and
the instrument goes with it.

## The layers, and where the cut has reached

`toolmodes.py` is 3,700 lines / 58 defs / 28 constants. `_selftest` alone is **615 lines** (17%),
`cmd_find` 186, `bare` 152, `main` 134, `render_block` 111, `literal_flags` 110.

| # | layer | defs | state |
|---|---|---|---|
| 1 | **population** — which files are tools | `roster`, `_publishes_modes`, `_tool_py`, `_has_entry_point`, `_TOOL_DIRS` | ✅ `substrate/tool_population.py`, 14/14 |
| 2 | **usage parsing** — text → modes | `parse_usage`, `_split_gloss`, `_outside_brackets`, `bracketed_options`, `_names` | ✅ `substrate/tool_usage.py`, 17/17 |
| 3 | **declarations** — five shapes + option rosters | `bare`, `_argparse_help`, `parse_options`, `_OPTHEAD`, `_OPTROW`, `_METAVAR` | ✅ `substrate/tool_declaration.py`, 20/20 |
| 4 | **dispatch reading** — AST → flags accepted | `literal_flags`, `_is_argv`, `_argv_aliases` | ✅ `substrate/tool_dispatch.py`, 15/15 |
| — | **pagination** (new, not from the origin) | — | ✅ `substrate/page.py`, 18/18 |
| 5 | census — the derived picture | `census`, `bare`, `census_row_modes`, `_index`, `_read_source` | ⬜ |
| 6 | conventions / declines | `Convention`, `Decline`, `_universal`, `_fixtures`, `_citations`, `_invisible` | ⬜ |
| 7 | similarity | `_stem`, `_tokens`, `_edit_distance`, `_sig_families`, `kind_families`, `near_misses` | ⬜ |
| 8 | queries — the CLI surface | the nine `cmd_*` | ⬜ |
| 9 | block / drift gate | `render_block`, `splice`, `_span`, `current_body`, `cmd_sync`, `cmd_check` | ⬜ |
| 10 | **dispatch** — `main` | ⚑ LAST: it routes to all of the above, and until it moves the file cannot be retired | ⬜ |

## ⚑ WHAT LAYER 1 FIXED ON THE WAY THROUGH — the blind spot that started this

`_TOOL_DIRS` was `("scratch", "scripts", "jea/metalanguage")`. **`substrate/` was absent**, so
~230 modules were invisible to every capability query. MEASURED: `toolmodes --find outline` →
**0 hits over 98 tools**, while `substrate/module_outline.py` does exactly that. The reader then
guessed two `pycodemod` mode names, got two usage dumps, and found the right tool by accident.

⚑⚑ **AND THE ORIGIN'S OWN DOCSTRING RECORDS THE SAME DEFECT ONE DIRECTORY OVER.** `--find locks`
returned 0 across 93 declared modes and was read in a dispatch brief as *"the breakdown method was
never built"* — while `schema.py` had `--locks`, `--activity`, `--census` and seventeen more. Its
verdict on itself: ***"a fact about the census's POPULATION reported as a fact about the tree."***

⚑ **THE OMISSION IS INVISIBLE FROM INSIDE.** Every hit `--find` returns is real, so the index
never looks broken — it looks like the capability does not exist. An unsearched directory and an
absent tool produce byte-identical output. After the fix: **~150 `substrate/` tools admitted**,
population 432 total.

## The residue, split by concern

⚑⚑⚑ **Ⓝ60 ⟡residue-is-a-drawer — CLOSED. THE `## Residue` DRAWER IS NOW A SET OF DOCUMENTS
ORGANISED BY SUBJECT, AND NOTHING WAS DELETED.** Every finding is a real measured finding and
`never discard residue` is a root memory of this practice — so the fix was never pruning. It is
that each finding's record now travels with the concern it belongs to, which is exactly what
n-splitting does for a module and for the same reason (Ⓝ81 ⟡commentary-is-load-too: *"a file doing
too much and a file carrying too much record both defeat the same faculty"*). **The table below is
the enumeration**; it is the authority for which parts exist, and nothing above it restates a count.

⚑ **CONSERVATION IS VERIFIED, NOT REASONED.** `substrate/doc_split.py` (run its `--selftest` for
the case count) compares the origin against the parts as a MULTISET IN BOTH DIRECTIONS —
origin-minus-parts catches a dropped line, parts-minus-origin catches one silently rewritten in
transit, and the multiset catches a duplicate or a lost repetition that a set comparison calls
present. The parts are SLICED from this document by line span rather than retyped, so the guard
checks a machine's output instead of adjudicating between two hand copies.

⚑⚑⚑ **AND IT EARNED ITS KEEP TWICE, ON THE ONE DEFECT NO REASONING ABOUT THE PLAN COULD HAVE
FOUND: THE DOCUMENT GREW WHILE IT WAS BEING SPLIT.** A concurrently-dispatched agent appended
Ⓝ29a/Ⓝ83 (now [the store and its tenants](toolmodes-residue-the-store-and-its-tenants.md)) and
then Ⓝ32a′/Ⓝ61/Ⓝ84 (now [the type gate](toolmodes-residue-the-type-gate.md)) after the partition
was derived. Both arrived as `dropped` rows in the guard's report — content the plan covered
nothing of, reported by a mechanical check rather than noticed. ⚑ It also caught one genuine
omission of mine, a Ⓝ73/Ⓝ71 entry left out of
[the frozen monoliths](toolmodes-residue-the-frozen-monoliths.md). **Three real losses, none of
which inspection would have surfaced; a partition is a snapshot, and this one was taken three
times before it held.**

⚑ **THE ORDER BELOW IS A READING ORDER AND IS DELIBERATE** — it runs from the tooling that writes
this record, through the arc's named subject and the migration it hands off to, to the gates and
walls that blocked them. It is a judgement worth recording, kept the way `ratchet_suites.ORDER`
stays hand-typed while its membership is derived. ⚑⚑ **It is ONE statement in ONE place, which is
exactly why it survives where the ordinals did not:** an ORDER is a sequence stated once, an
ORDINAL is that statement copied into every member and rewritten whenever one is inserted.

| concern | threads |
|---|---|
| [writing the record](toolmodes-residue-writing-the-record.md) | Ⓝ36a ⟡preview-is-not-the-write · Ⓝ60 ⟡residue-is-a-drawer · Ⓝ81 ⟡commentary-is-load-too · Ⓝ85 ⟡a-restated-fact-is-a-second-authority — the tooling that writes this record, and what its shape cost |
| [draining toolmodes](toolmodes-residue-draining-toolmodes.md) | Ⓝ31h″ ⟡retire-toolmodes · Ⓝ31j ⟡render-halves · Ⓝ31m ⟡yield-dont-return · Ⓝ31m″ ⟡typed-carrier · Ⓝ31n — the arc's named subject |
| [⟡symbolic-reference-only](toolmodes-residue-symbolic-reference-only.md) | Ⓝ31q ⟡erasure-is-a-reflex · Ⓝ31s (and s″) · Ⓝ39 ⟡importers-blind-to-from-import · Ⓝ62 ⟡namedtuple-api-surface — nothing is identified by a number |
| [the codemod pipeline](toolmodes-residue-the-codemod-pipeline.md) | Ⓝ31s⁴ ⟡check-the-prospective-output · Ⓝ31s⁶ (the 13, the 5) · Ⓝ31s⁹ ⟡wrong-matcher-control · Ⓝ44 · Ⓝ47 ⟡dump-dont-infer · Ⓝ63⁴ ⟡the-trim-is-a-write · Ⓝ63⁵ ⟡the-apply-loop · Ⓝ71c · Ⓝ72 |
| [suite coverage](toolmodes-residue-suite-coverage.md) | Ⓝ63′–Ⓝ63⁶ ⟡cover-the-spine · Ⓝ66 ⟡witness-not-victim · Ⓝ67 ⟡the-slot-is-the-reach · Ⓝ68 ⟡the-registry-is-the-reason · Ⓝ68a ⟡derive-the-roster · Ⓝ69/69a · Ⓝ70 ⟡the-partition-has-an-exception |
| [the frozen monoliths](toolmodes-residue-the-frozen-monoliths.md) | Ⓝ48 ⟡drain-run-selftests · Ⓝ71/71a–71i ⟡retire-the-runner · Ⓝ75 ⟡mv-is-not-an-edit · Ⓝ76 ⟡scratch-admits-no-new-files · Ⓝ68b′ ⟡two-stale-origins |
| [false zeros](toolmodes-residue-false-zeros.md) | Ⓝ68b ⟡attr-misses-the-alias · Ⓝ72a ⟡shebang-permission-census · Ⓝ72c ⟡state-the-walk · Ⓝ74 ⟡importers-path-spelling · Ⓝ82 — a zero must name what it could not see |
| [gates, types, budgets](toolmodes-residue-gates-types-budgets.md) | Ⓝ41 ⟡callee-surface-assumed · Ⓝ53 ⟡singledispatch / ⟡match-not-isinstance · Ⓝ57 ⟡scratchpad-cannot-hold-a-probe · Ⓝ58 · Ⓝ59 ⟡the-refusal-is-not-a-probe · Ⓝ73 · Ⓝ79 · Ⓝ80 ⟡line-length-is-obsolete · Ⓝ89/89a ⟡unparseable-is-not-clean · Ⓝ90 · Ⓝ91 ⟡enospc · Ⓝ93/93a ⟡baseline-audit · Ⓝ124 ⟡gates-per-file · Ⓝ131 ⟡mcp-injects-directives |
| [the store and its tenants](toolmodes-residue-the-store-and-its-tenants.md) | Ⓝ29a ⟡store-drain-cause · Ⓝ83 ⟡tenant-scoped-refusal-is-not-an-outage · Ⓝ83a · Ⓝ78‴ ⟡drain-query-topo · Ⓝ92b′ ⟡drain-store · Ⓝ112 ⟡drain-schema-rows · Ⓝ119′–119⁗ ⟡use-the-compiler / ⟡settle-the-paramstyle · Ⓝ127/127a ⟡sync-needs-a-green-suite · Ⓝ128 ⟡our-stubs-not-theirs · Ⓝ132 ⟡canon-syms-cases-stale |
| [the type gate](toolmodes-residue-the-type-gate.md) | Ⓝ32a ⟡type-gate-broken · Ⓝ32a′ ⟡the-jea-any-subtree · Ⓝ32a⁶ ⟡files-if-none-are-given · Ⓝ61 ⟡type-gate-needs-a-summary · Ⓝ84 ⟡the-sanctioned-boundary-does-not-EXIST · Ⓝ84a · Ⓝ117 ⟡the-import-mechanism-is-the-blocker · Ⓝ125 ⟡the-easier-escape-hatch |
| [the derived interface](toolmodes-residue-the-derived-interface.md) | Ⓝ94/94a ⟡audit-the-stubs · Ⓝ100a ⟡declines-by-ast · Ⓝ103 ⟡infer-the-interface · Ⓝ104 ⟡the-pyi-is-a-function-of-the-sources · Ⓝ104a–104g ⟡reach-vs-dead / ⟡witness-provenance / ⟡union-is-not-conflict · Ⓝ106 ⟡interpret-the-constructor · Ⓝ128c ⟡typeengine-false-export — what a `.pyi` can be COMPUTED, and what only an author can state |
| bazel and the cross-repo surface | Ⓝ133h ⟡bazel-shard · Ⓝ147 ⟡hooks-package · Ⓝ148 ⟡scripts-not-a-package · the three-repo audit |

⚑⚑⚑ **Ⓝ85 ⟡a-restated-fact-is-a-second-authority — THIS INDEX REPRODUCED THE ARC'S ROOT FINDING
THREE TIMES IN ONE AFTERNOON, AND EACH LAYER WAS INTRODUCED WHILE FIXING THE PREVIOUS ONE:**

    1. a MEASURED FIGURE   a `lines` column of sizes. First estimated from span arithmetic, wrong
                           by up to 60%; corrected to real `mdstruct --budget` values; then
                           measured at 95 where the table said 97 — stale on its first day, with
                           nobody having edited the file it described.
    2. a SET CARDINALITY   "Part N of 10" in every header — one fact about the SET restated in
                           every member, so an eleventh part falsifies all ten at once.
    3. an ORDINAL          "Part 4", and a numeric prefix in every filename. Inserting a document
                           renumbers every one after it, plus this table and every cross-reference,
                           for documents that did not change.

⚑⚑⚑ **AND (3) IS THE ARC'S OWN SUBJECT, BUILT INTO THE FILENAMES OF THE RECORD THAT ARGUES AGAINST
IT.** ⟡symbolic-reference-only is one row above; `lifecycle.py` states it exactly — *"a POSITION
standing in for an IDENTITY. Positions renumber; identities do not."* The integer-keyed scheduler
roster `{3: retire, 2: promote, 1: ingest}` silently DROPPED `retire` when the chain shortened.
**Two cross-references cited parts by number and had to be repaired** — proof the numbering was
already load-bearing after a single afternoon.

⚑⚑ **THE TEST THAT COVERS ALL THREE IS AUTHORITY, NOT PROVENANCE: DOES SOMETHING ELSE ALREADY KNOW
THIS?** My first boundary was *structural vs measured*, which let the cardinality through because
nobody ran a command to get it; my second kept the ordinal because this document seemed to own it.
Both wrong in the same direction. `mdstruct --budget` owns the size, the DIRECTORY owns the
membership, and **the CONCERN owns the identity**. The general rule: **anything that has to be
rewritten when something ELSE changes does not belong in the document.** This is `MEM_CAP` —
`128m` in the file that owns it, restated as `256m` in three files that quoted it, including the
gate that ENFORCES the cap.

⚑ **CROSS-REFERENCES SURVIVE BECAUSE THE SYMBOLS DID.** Findings in this arc cite each other by
Ⓝ-number and ⟡-tag constantly (Ⓝ71 → Ⓝ71a → Ⓝ71b; ⟡mv-is-not-an-edit cited from four places),
and **no symbol was renamed, reworded or renumbered by the split** — the conservation guard's
both-directions rule makes that checkable rather than promised. So every existing citation still
resolves: the table above maps symbol to document, and a reader with a bare Ⓝ-number scans one
row rather than the whole drawer. ⚑⚑ THIS PATH REMAINS THE ENTRY POINT: other sessions, agents and
this conversation's own record cite `catalog/worklist/toolmodes-split.md`, so it keeps the arc's
frame above and became the index rather than moving.

⚑ **THE SPLIT IS BY CONCERN, DERIVED FROM THE DOCUMENT'S OWN VOCABULARY** — the Ⓝ-numbers and
⟡-tags the arc coined for itself — never from a taxonomy imposed on it. Where a thread genuinely
dominates it was left dominant, because cutting a single argument in half trades one readable
thread for two unreadable ones.

⚑⚑ **AND SOME PARTS ARE STILL TOO LARGE TO HOLD, WHICH IS A FINDING TO REPORT RATHER THAN A REASON
TO CUT ARBITRARILY.** *The codemod pipeline*, *suite coverage*, *the frozen monoliths* and *gates,
types, budgets* are each one continuous argument a reader must carry whole — the codemod learning
to verify its own output, the coverage taxonomy converging under four corrections, the wall
dissolving from *edit* to *mv*, and the refusal-as-evidence class. **The drawer is gone and those
four are still the session's longest arguments**, so Ⓝ60 is closed and its successor is not.
(`mdstruct --budget` on any of them for the current size.)

⚑ **Ⓝ60a ⟡the-sub-seam-is-not-visible-yet.** A further split of those four needs a seam INSIDE an
argument, and none of the four offers one today — each is a single thread whose middle depends on
its beginning. The honest reading is that the concern grain was right and the concerns themselves
are large, not that the partition was lazy. Re-read as the threads extend; a sub-seam that does
not exist cannot be found by cutting at a line count, **which is exactly the proxy Ⓝ80 retired —
and cutting at one is what a size column in this index would have invited.**

## Residue — where it went

The `## Residue` section that stood here is now the documents listed above. **Nothing was deleted,
summarised, or reworded**; `substrate/doc_split.py` verifies that mechanically. New findings append
to whichever document owns their concern, which is what keeps this from becoming a drawer again —
and `--append-section` targets a named section, so each is a bounded place to land.

⚑ **A NEW CONCERN GETS A NEW FILE AND A NEW ROW, AND NOTHING ELSE CHANGES.** No renumbering, no
count to update, no sweep — which is the whole point of naming these by concern rather than by
position (Ⓝ85, above).
