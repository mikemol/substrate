# Ⓝ31 residue — the frozen monoliths

**Concern: files the per-file gate refuses every edit to, what that blocked, and the move that
dissolved it.** Index and arc frame: [`toolmodes-split.md`](toolmodes-split.md).

⚑⚑ **Ⓝ75 ⟡mv-is-not-an-edit IS THE APEX OF THIS THREAD AND IT ARRIVED LAST.** For a whole
session every route asked *how do I EDIT this file*, and three independent proofs of "no
edit-based repair exists" were all correct and all useless: the freeze is a property of the
BYTES, not the PATH. Ⓝ76 then found the packaging rule directly behind it (`scratch/` admits no
new files), and Ⓝ71/Ⓝ71a ⟡retire-the-runner is the thread's completion — the runner runs.

⚑ Read Ⓝ48 → Ⓝ71 → Ⓝ75 → Ⓝ76 in order; the earlier entries are the wall being verified from
inside, and the later ones are it dissolving.

## Residue

* ⚑⚑⚑ **Ⓝ48 ⟡may-write-positional — CANNOT BE FIXED WHERE THE CALLS LIVE. EVERY CALL SITE IS IN A
  MONOLITH.** The repair is one keyword (`may_write(write=write)`) and it is unlandable:

      scripts/run_selftests.py        1,832 findings   — refused
      scripts/set1_ratchet_cores.py   (E501/E401/I001/F401/PTH/E402/T201…) — refused

  **The gate's own runner cannot be edited to fix the gate's own runner.**

  ⚑⚑ **THIS IS THE FIFTH MONOLITH THIS SESSION AND THE PATTERN IS NOW A POPULATION:**

      scratch/toolmodes.py              2,196
      scripts/run_selftests.py          1,832
      scratch/mdstruct.py               1,534
      jea/metalanguage/sorted_stream.py   411
      scripts/gen_build_makefiles.py      291

  Each blocked a DIFFERENT arc this session — the mode census, the suite verification, the
  worklist writes, the ordering carrier, the build generator. ⚑ **The per-file gate is not
  occasionally inconvenient here; it is the binding constraint on five independent lines of work,
  and in this case on VERIFYING A CHANGE THAT IS ALREADY WRITTEN.**

  ⚑⚑⚑ **AND THE SHAPE IS SHARPER THAN "BIG FILES ARE DIRTY".** A one-character correctness fix
  cannot land, while a 58-file semantic migration landed cleanly this morning — because the
  migration went into files that were already clean and the fix must go into files that are not.
  **The gate admits large correct changes and refuses small correct ones, sorted entirely by the
  hygiene of the host file.** That is the per-file gate working as designed (`usecase-the-per-
  file-gate-is-a-design-signal`), and the signal it is sending is that these five files must be
  split before anything inside them can be repaired.

  **THE ROUTE THAT EXISTS:** `baseline_io.may_write` is already the extracted, clean,
  keyword-only authority — the migration `ratchet.may_write` was meant to complete. The callers
  cannot be edited to use it, so the fix is not a caller edit at all: it is **draining the two
  monoliths**, which is Ⓝ30a′'s shape applied to `run_selftests.py` and `set1_ratchet_cores.py`.

  ⚑ **CONSEQUENCE FOR THIS SESSION, STATED PLAINLY: the 58 converted files CANNOT BE VERIFIED.**
  `run_selftests` aborts before any suite reports, and the abort cannot be repaired. Seven suites
  were spot-checked green; 255 exist. **The conversion is written, spot-checked, and UNVERIFIED**,
  and no amount of further work on the conversion changes that — the blocker is elsewhere.


* ✅ **Ⓝ48′ ⟡drain-run-selftests — FIRST CUT LANDED: `substrate/reach_verdict.py`.**
  The reach ratchet's CLASSIFIER, extracted clean from a 1,832-finding monolith. Six kinds
  (`new`/`grew`/`held`/`deleted`/`shrank`/`unknown`), the scaled two-lens comparison, and the
  slack calibration — with every ⚑ that explains why each is shaped as it is.

  ⚑⚑⚑ **AND THE CUT DISSOLVES Ⓝ48 RATHER THAN FIXING IT.** The broken line is
  `write = ratchet.may_write(write)` inside `reach_ratchet` — a WRITE-POLICY decision sitting in
  the middle of a CLASSIFIER. Split apart, `reach_verdict` classifies and `may_advance` reports
  whether the census MAY advance; **the caller decides whether it does.** The keyword-only
  signature never enters this module, so the one-keyword repair is not needed here at all — the
  seam was in the wrong place, and the positional call was a symptom of that.

  ⚑⚑ **THE MODULE'S OWN OUTPUT NOW OBEYS ⟡symbolic-reference-only.** `regressions()` returned
  `tuple[tuple[str, Verdict], ...]` sorted by `lambda row: row[0]` — a positional pair and an
  untyped lambda, which mypy correctly reported as `Any`. It returns `Regression` records sorted
  by a named `rank()`. **The arc's own rule caught the arc's own new code**, which is what makes
  it a rule rather than a preference.

  ⚑ **WHAT STILL BLOCKS THE VERIFICATION:** `run_selftests.py` still holds the broken call and
  still cannot be edited. This cut makes the classifier available and clean; **wiring it in is an
  edit to the monolith**, so the runner needs further draining before the 58 conversions can be
  verified. One cut of an estimated five or six (`main` 499 lines, `_selftest` 921, plus the
  telemetry, discovery, store-reach and case-counting groups).

* ⚑ **THE FILE'S SEAMS, READ RATHER THAN GUESSED** (`module_outline`), for whoever continues:

      verdict reading    unreadable_output · verdict_kind · read_result
      case counting      _own_cases · static_cases
      reach ratchet      _read_reach · _write_reach · reach_verdict · reach_ratchet   ← CUT
      telemetry          _emit_one · _series_of · _emit_sample · emit_series
      discovery          discover · _requires · _tenant · population_stamp
      store reachability _connect_sites · _local_imports · _deferred_seed_imports ·
                         _module_index · store_reach
      dispatch           main (499) · _selftest (921)   ← 42% of the file, LAST

  ⚑ `_selftest` at 921 lines is 27% of the file on its own, and `main` another 15%. The same
  shape as `toolmodes` (`_selftest` 615 of 3,700): **the dispatch and its suite are the bulk, and
  they move last** — until they do, every extraction is stranded, which is Ⓝ31's whole lesson
  arriving in the next monolith.
* ⚑⚑⚑ **Ⓝ48′ — THE VERDICT-READING LAYER IS **ALREADY EXTRACTED**, AND THE MONOLITH CARRIES A
  DUPLICATE. I nearly cut it a third time.**

  About to extract `unreadable_output` + `verdict_kind` + their four constants from
  `run_selftests.py`, I checked whether the constants were already owned elsewhere before
  duplicating them (`pycodemod --binding RESULT` / `--binding KILL_CODES`). They are:

      substrate/suite_record.py:55    RESULT
      substrate/suite_outcome.py:51   KILL_CODES     ← and REFUSAL_CODE, INTENT_WORD, INTENT_ARITY
      scripts/run_selftests.py:246    KILL_CODES     ← the duplicate

  **`substrate/suite_outcome.py` already holds `unreadable_output`, `verdict_kind`, `Reported`,
  and all four constants — 18/18 green.** The layer I was about to cut exists.

  ⚑⚑ **SO THIS IS `agda_files()`-HAD-FOUR-BODIES, IN THE PYTHON, IN THE RUNNER.** Two spellings
  of one classifier, both live, and **nothing declares which is authoritative**. The extracted
  copy is clean and cased; the monolith's is 1,832-findings-dirty and unreachable from any suite
  — which is the exact property `verdict_kind`'s own docstring says it was made a function to
  avoid (*"it is a function so a case can reach it… this logic was inline in `run_one`, i.e.
  unreachable from the suite"*). **The extraction fixed that for the copy nobody calls.**

  ⚑⚑⚑ **AND ONE `--binding` CALL IS WHAT STOPPED A THIRD COPY.** I have written five new modules
  today; had I written a sixth for a layer that already existed, the monolith would hold one
  duplicate and `substrate/` two. `Ⓝ41′ ⟡callee-surface-assumed` generalises past callee
  surfaces: **check whether the thing you are about to build EXISTS, not merely whether the names
  it needs do.** The reuse-search trigger in CLAUDE.md fires on exactly this and I ran it only
  because the constants forced the question.

  **WHICH CHANGES WHAT DRAINING THE RUNNER MEANS.** It is not "extract six layers" — some are
  already out and the monolith is holding stale copies. The first move is a CENSUS of which of
  its seven groups already have a home in `substrate/`:

      verdict reading    ✅ substrate/suite_outcome.py (18/18) — monolith holds a DUPLICATE
      reach ratchet      ✅ substrate/reach_verdict.py (this session)
      case counting      ⬜ unchecked
      telemetry          ⬜ unchecked
      discovery          ⬜ unchecked  (⚑ `substrate/suite_discovery.py` exists — check it)
      store reachability ⬜ unchecked
      dispatch           ⬜ main (499) · _selftest (921), moves LAST

  ⚑ **A duplicate is worse than an un-extracted layer**: the un-extracted one is honest debt,
  while a duplicate makes the tree look drained while the live path still runs the dirty copy.


* ✅ **Ⓝ48″ ⟡census-before-cutting — DONE, AND IT REFRAMES THE DRAIN. THE RUNNER IS NOT ONE
  MONOLITH TO SPLIT; IT IS FOUR DIFFERENT SITUATIONS.**

  | group | state in `substrate/` | what draining actually means |
  |---|---|---|
  | verdict reading | ✅ `suite_outcome.py` 18/18 | **DELETE the monolith's duplicate**, rewire |
  | reach ratchet | ✅ `reach_verdict.py` (today) | wire it in |
  | case counting | ⚠️ **PARTIAL** — `case_lens.own_cases` extracted, `static_cases` (112 lines) NOT | finish the cut |
  | discovery | ✅ `suite_discovery.discover` | delete + rewire |
  | store reachability | ⚑⚑⚑ **DEFINED IN THE MONOLITH, IMPORTED BY CLEAN MODULES** | EXTRACT — the dependency runs backwards |
  | telemetry | ⬜ absent (`emit_series` 0 bindings) | genuine extraction |
  | dispatch | ⬜ `main` 499 · `_selftest` 921 | LAST |

  ⚑⚑⚑ **`store_reach` IS THE FINDING.** `pycodemod --calls store_reach`: **1 def at
  `scripts/run_selftests.py:1536`, and three clean `substrate/` modules import it** —
  `tenant_census.py`, `census_show.py`, `tenant_census_selftest.py`. So cased, gate-clean modules
  DEPEND ON A FUNCTION INSIDE A 1,832-FINDING FILE. **The dependency runs the wrong way**, and
  every consumer inherits the monolith's fate: it cannot be edited, so neither can the definition
  they rely on.

  ⚑⚑ **AND THE CENSUS METHOD BROKE ON ITS OWN TWO-SPELLING DEFECT, MID-CENSUS.**
  `--binding static_cases substrate/` → **0 bindings**; `--binding CASE_CALLS substrate/` →
  `case_lens.py`. Same group, two names, opposite answers — and the first would have licensed a
  duplicate extraction. **`census-keyed-on-one-spelling` inside the very census run to avoid
  duplicating.** The fix is what it always is: ask for the CAPABILITY under more than one
  spelling before concluding absence.

  ⚑ **SO "DRAIN THE MONOLITH" WAS THE WRONG UNIT OF WORK.** Three of seven groups are already out
  and the file holds stale copies; one is half out; one is *inside-out* (defined here, consumed
  clean); one is genuinely absent; one moves last. **Deleting and rewiring is a different
  operation from extracting, and doing the second where the first was needed is how a tree grows
  a third copy.**

  **THE ORDER THIS IMPLIES:**
  1. `store_reach` — extract FIRST. Three clean consumers are currently held hostage.
  2. Delete the duplicated verdict-reading block; rewire to `suite_outcome`.
  3. Delete the duplicated discovery block; rewire to `suite_discovery`.
  4. Finish `static_cases` into `case_lens`.
  5. Extract telemetry.
  6. `main` + `_selftest`, then retire.


* ✅ **Ⓝ48a ⟡extract-store-reach — LANDED: `substrate/import_reach.py`.**
  The store-reachability walk, out of the 1,832-finding runner: `store_reach`, `local_imports`,
  `deferred_seed_imports`, `module_index`, `STORE_SEEDS`, and a `Reach` record whose
  `through_cut` property makes the deferred-hop mark readable rather than a string convention.

  ⚑⚑⚑ **THIS WAS THE FIRST CUT BECAUSE THE DEPENDENCY RAN BACKWARDS.** `store_reach` was defined
  in `run_selftests.py` and imported by three clean `substrate/` modules — `tenant_census`,
  `census_show`, and its suite. **Gate-clean code depended on a definition inside a file no edit
  can touch**, so every consumer inherited the monolith's frozen state.

  ⚑⚑⚑ **AND THE ERASURE REFLEX APPEARED A THIRD TIME, IN CODE WRITTEN AFTER RECORDING IT TWICE.**
  My first cut of `_module_level` read `getattr(node, "body"/"orelse"/"finalbody", None)` and
  probed for `handlers` the same way. The AST node types are KNOWN; probing their fields by name
  discards what the type already says and returns `Any` at every access. Now `_nested_bodies`
  matches by type. **Instances today: `sort_key.default_get`, `record_migrate._check`, this.**
  → `Ⓝ52 ⟡getattr-is-the-tell`: `getattr` over a KNOWN type is the reflex, and the fix is always
  to match the type.

  ⚑⚑ **THE CHECKER THEN CAUGHT THE SAME MISTAKE ONE LEVEL SUBTLER.** My typed version still read
  `node.orelse` off a seven-member union — and `With`/`AsyncWith` carry no `orelse`. **The union
  was wider than the attribute set**, which is field-probing with an `isinstance` in front of it.
  Each group is now matched for exactly the fields it declares.

* ⚑⚑ **THE OPERATOR'S CONSTRAINT CHANGES THE ENDGAME, AND IT IS NOT OPTIONAL.**
  *"You won't be able to delete from the monolith, because that would require the monolith to be
  passing."* **A deletion is an edit; an edit to a file with findings is refused.** So the drain
  can only ADD clean modules beside it. `run_selftests.py` is FROZEN — it cannot shed its
  duplicates, cannot have the `may_write` call repaired, and cannot be partially retired.

  **The only terminal move is: extract every group, write a clean entry point, DELETE THE FILE
  WHOLE.** That is ⟡retire-toolmodes' shape arriving as a constraint rather than a choice — and
  it means the five monoliths are each an all-or-nothing retirement, not a gradual paydown.

* ⬜ **NOT DONE: the parity probe.** `store_reach`'s rewrite is UNVERIFIED against the origin.
  The probe is written but refused — it needs the `Protocol` + `cast` treatment used in
  `record_migrate._check`, because a path-loaded module's attributes are `Any`. ⚑ **The origin is
  still on disk and will not be after the retirement**, so this is the window Ⓝ31i argued for,
  open now and closing.

* ⚑⚑⚑ **Ⓝ71 ⟡may-write-keyword-only — THE RUNNER IS CRASHING, THE FIX IS ONE CHARACTER, AND THE
  FILE REFUSES IT.** `scripts/run_selftests.py:724` calls `ratchet.may_write(write)` positionally
  against a definition that is now keyword-only:

      TypeError: may_write() takes 0 positional arguments but 1 was given

  **MEASURED BLAST RADIUS (`--forwards may_write write`): 5 of 9 call sites do not forward it** —
  `run_selftests.py:724` (crashing), `set1_ratchet_cores.py:318` (latent; a tenant check guards
  earlier), and `tests/test_rederive_agreement.py:198,200,202`. The four that pass are all in
  already-extracted modules.

  ⚑⚑ **AND IT IS A STALE PREMISE INSIDE THE DECOMPOSITION'S OWN RATIONALE.**
  `substrate/baseline_io.py:47-51` states the keyword-only choice is *"a DELIBERATE DIVERGENCE
  rather than an oversight"* — `FBT001` is right that a bare `may_write(True)` says nothing about
  what the True decides, and this boolean decides whether a gate WRITES — and then adds: *"The
  three existing callers keep working against `ratchet.may_write`."* **That was true when written
  and is now false.** The facade was repointed at the keyword-only definition, so the escape
  hatch the comment relies on no longer exists. `fresh-comments-are-hypotheses-too`, firing
  inside the file whose job was to be the single resolver.

  ⚑ **I ALSO GOT THIS WRONG EARLIER IN THE SESSION**, recording `may_write` as *"pre-existing,
  `baseline_io.py` untouched"* and moving on. Untouched was true of the FILE and false of the
  BINDING — the facade moved under it. A verification aimed at the definition cannot see a change
  in what its name resolves to.

* ⚑⚑⚑ **Ⓝ71a ⟡the-stranded-extraction — AND THE REPAIR IS UNREACHABLE FROM EVERY DIRECTION,
  WHICH IS THE REAL FINDING.** `run_selftests.py` carries **1,832 findings**, so the per-file
  gate refuses a ONE-CHARACTER fix to an actively-crashing line, and has no partial-credit path
  to stage it through. The gate's own refusal text names the route — *extract the concern into a
  new module* — **and that extraction has ALREADY HAPPENED:**

      --calls reach_ratchet   →   2 def(s), 16 call(s)
        def  scripts/run_selftests.py:698      ← crashing, unfixable, 10 callers all inside the file
        def  substrate/reach_ratchet.py:100    ← correct, forwards `write=`, 6 cases in its suite

  **Two definitions under one name — the `agda_files()`-had-four-bodies shape.** The extracted
  copy is tested and right; the monolith's copy is what runs. ⚑ The gate's text names this
  outcome exactly: *"if the only consumer is inside this file, one extraction STRANDS… you are
  left with a clean module nothing imports, which is a built-then-orphaned rung rather than a
  repair."* All ten `reach_ratchet` call sites are inside the frozen file, so wiring the good one
  in is itself a refused edit.

  ⚑⚑ **SO THE MONOLITH IS NOT MERELY UNCOVERED — IT IS AN ACTIVE DIVERGENCE THAT NOTHING CAN
  CORRECT.** Ⓝ31s⁸′ ⟡verify-the-58 has been blocked on this file all session as an inconvenience;
  it is now blocking a live crash in the runner that every suite reports through. **The unit of
  repair is the whole file, and the finish is RETIRING it, not extracting one more concern.**

  ⚑ **AND THE CRASH IS DOWNSTREAM OF A GREEN CENSUS.** In the full 265-suite run every extracted
  module passed — `attr_reads 16/16`, `module_importers 15/15`, `pycodemod 408/408` — and the run
  still exits 1, because the composition crashed in the one file no suite covers. **A green
  membership over a population that excludes the failing member.**

* ⚑⚑ **Ⓝ71b ⟡findings-are-not-size — THE DRAIN TARGET IS THE SMALLEST OF THE TWELVE OVER-BUDGET
  FILES, AND I HAD BEEN READING 1,832 AS A MEASURE OF ITS BULK.** Measured (`module_size --top`):

      scripts/run_selftests.py     1,299 code / 3,381 physical ·  37 defs   ← 1,832 findings
      scratch/agda_defs.py         2,991 code / 6,253 physical ·  68 defs
      scratch/pycodemod.py         1,826 code / 4,143 physical ·  23 defs   ← 2,145 findings
      scratch/toolmodes.py         1,660 code / 3,700 physical ·  64 defs

  **`run_selftests.py` is the SMALLEST over-budget file in the tree** — about a third of
  `agda_defs.py`, below `toolmodes.py` and `pycodemod.py` — while carrying nearly the highest
  finding count. **The findings come from DENSITY, not bulk**, so a retirement is a much smaller
  cut than "1,832 findings" suggests, and I had been treating the number as a proxy for the work.

  ⚑ **A FINDING COUNT MEASURES HOW FAR A FILE IS FROM THE GATE, NOT HOW MUCH FILE THERE IS** —
  two facts a single scalar cannot separate, and I quoted it all session as if it were one.
  Sibling of `cost_is_structural_times_live`: the structural term (lines, defs) and the
  efficiency term (findings per line) were multiplied into a scalar and then read as the first.

  ⚑ **AND `pycodemod.py` IS THE CLEARER CASE FOR THE SAME POINT:** 23 defs across 1,826 code
  lines and 2,145 findings — the highest count in the tree, over a file with fewer definitions
  than `ratchet_log` had before it was split. **A high finding count can mean a few very dense
  bodies rather than a large surface**, which is the shape that responds best to extraction and
  worst to paydown-in-place.


* ⚑⚑⚑ **Ⓝ71 — MY BLAST RADIUS WAS THE CENSUS, NOT THE IMPACT. 5 SITES DON'T FORWARD; ONLY 2
  CRASH.** I reported `--forwards may_write write` → *"5 of 9 do NOT forward"* as the breakage
  count. Measured per site by the agent, and confirmed by RUNNING them:

      run_selftests.py:724          may_write(write)    ← CRASHES
      test_rederive_agreement:202   may_write(False)    ← CRASHES
      set1_ratchet_cores.py:318     may_write()         ← fine, zero-arg
      test_rederive_agreement:198   may_write()         ← fine, zero-arg
      test_rederive_agreement:200   may_write()         ← fine, zero-arg

  **`--forwards` answers *does this site forward the keyword*, not *does this site break*.** A
  zero-arg call does neither and is correctly counted as not-forwarding. ⚑ Same shape as the
  `--calls emit` miss CLAUDE.md records: **a census answered the question ASKED and I reported it
  as the question MEANT**, one turn after writing Ⓝ67 about exactly this.

* ⚑⚑⚑ **Ⓝ71a — THE STRANDED EXTRACTION WAS NOT STRANDED, IT WAS BROKEN, AND THE STRANDING IS
  WHAT HID IT.** `substrate/reach_ratchet.py` **did not import at all**: it was written against a
  HYPOTHESISED callee — `reach_verdict(label, ran, static, base) -> (kind, detail)`, the
  monolith's private signature transcribed — while what actually landed in
  `substrate/reach_verdict.py` is a different, richer API (`classify` → `Verdict`, plus
  `regressions`/`may_advance`/`advanced`). `ImportError` at module load.
  **`reach_verdict_selftest.py` carried the same defect.**

  **Two clean modules, two clean suites, nine arms — NONE HAD EVER EXECUTED.** ⚑ *Nothing imports
  an orphan, so nothing runs its suite.* The orphan status was not merely a missed wiring: it was
  the thing that kept a non-importable module reading as done. **A built-then-orphaned rung is
  not idle, it is UNVERIFIED — and it looks identical to a finished one.**

  ⚑ Repaired and now genuinely running: `reach_ratchet` **8/8**, `reach_verdict_selftest`
  **22/22** (boundary arms carried over from the monolith's `_selftest` so trimming the duplicate
  loses no coverage), `reach_baseline_selftest` 7/7. ⚑ One arm the agent wrote was itself wrong
  (used a 50→48 row, slack 2, to test *"1:1 gets no slack"*); **its own suite caught it** and a
  genuine `(40,40)` row was added.

* ⚑ **AND THE RUNNER STILL CRASHES — STATED PLAINLY, FILE BYTE-IDENTICAL TO HOW IT WAS FOUND.**
  The TypeError fires at **two** sites (`main:2393` and `_selftest:2586`), not one.
  ⚑⚑ **`module_trim` CAN NEVER WRITE THIS FILE**, and that is structural rather than incidental:
  `writable` requires CLEAN, and a partial trim leaves ~1,830 findings. **The pipeline built for
  this class of repair is inapplicable to the file that most needs it.**
  ⚑ Half the monolith's concerns ALREADY have clean, CONSUMED homes — `store_reach`,
  `read_result`, `verdict_kind`, `discover` all have live consumers outside it. **What is missing
  is only the `main` dispatch**, which is the whole remaining cut.
  ⚑ **Ⓝ73 ⟡selftest-contract-blocks-too:** `selftest-contract: BROKEN — 228 NEW suites reporting
  by PROSE instead of a typed record`, a paydown-only census that fires BEFORE the reach gate. So
  even with the TypeError fixed the runner exits non-zero. A distinct and larger arc.
  ⚑ **`module_importers` gives a FALSE ZERO ON THE PATH SPELLING** (`substrate/reach_ratchet.py`
  → 0) and the right answer on the dotted one (`substrate.reach_ratchet` → 1). Two spellings, one
  question, and this repo deletes on zeros.

* ⚑⚑ **Ⓝ68b′ ⟡two-stale-origins — NOTHING CAN BE DONE, AND THE FREEZE IS PROVED RATHER THAN
  ASSUMED.** Trial edit run as asked: `module_trim --dry-run scratch/pycodemod.py _opt` →
  **FINDINGS**, nothing written. Both false zeros reproduced **against a positive control**,
  which is what makes them readable as defects rather than as absences:

      corpus.ROOT reads          frozen origin 0        promoted reader 121 in 66 files
      substrate.corpus importers frozen origin 0        promoted reader many

  ⚑ **AND THE DISPATCH CANNOT BE INTERCEPTED FROM OUTSIDE.** Both modes dispatch from `_dispatch`
  — a **2,173-line function inside `pycodemod.py` itself**, not in any of the twelve shards. *The
  drain moved the censuses out and left the dispatch body behind*, so there is no shard to edit.
  `gate_module` is an IMPORTER, not a dispatcher, and is not on this path.

  ⚑⚑ **THE AGENT DECLINED THE HALF-MEASURE FOR THE RIGHT REASON:** a wrapper at a DIFFERENT
  spelling would not stop anyone reaching the old one first, *which is precisely the defect* — a
  superseded reader that still responds answers whoever arrives at the old spelling. **Ⓝ68b″:**
  the retirement needs `_dispatch` moved into shards in one clean write, then both branches
  changed from ANSWERING to **REFUSING WITH A REDIRECT** (`--attr` → `attr_reads`, `--importers`
  → `module_importers`). A refusal, never a zero.

* ⚑⚑⚑ **Ⓝ75 ⟡mv-is-not-an-edit — THE FREEZE IS A PROPERTY OF THE CONTENT, NOT THE PATH, AND
  EVERY ROUTE I TRIED ASKED THE WRONG QUESTION.** Operator, on Ⓝ68b′: *"it sounds like the
  existing files should be `mv`'d out of place and replaced with valid, functioning ones."*

  I asked **how do I EDIT this file** — and so did every agent I briefed. The answers were all
  correct and all useless: the gate refuses any edit and reverts (proved, `module_trim --dry-run
  scratch/pycodemod.py _opt` → FINDINGS); `module_trim` cannot write it because `writable`
  requires CLEAN and a partial trim leaves ~1,830 findings; the dispatch cannot be intercepted
  because `_dispatch` is a 2,173-line function INSIDE the frozen file, not in any of the twelve
  shards. Three independent proofs of *no edit-based repair exists* — **and a `mv` is not an
  edit.** A NEW file written clean at that path has no findings to inherit; move the content away
  and the freeze goes with it.

  ⚑⚑ **SO THE PER-FILE GATE WAS NEVER A WALL AROUND THE PATH — IT IS A WALL AROUND THE BYTES,
  and I read it as the first for a whole session.** `feedback_declaring_wall_rebuild_reflex`
  fired here and I did not notice it, because each individual refusal was a genuine measurement.
  **A wall verified three times from inside is still only verified from inside**: every probe
  tested *can I modify these bytes*, none tested *must these bytes be at this path*.

  ⚑ **AND THE GATE'S OWN REFUSAL TEXT POINTS AT IT WITHOUT NAMING IT:** *"Extract the one concern
  you need into a NEW module… keep cutting until the DISPATCH moves out as well, then RETIRE this
  file."* **Retire** is the word — and retiring is what `mv` does in one operation, where
  extraction does it one concern at a time and strands each one until the last. The instruction
  was for the incremental route; the operator named the terminal one.

  ⚑⚑ **THE SAME MOVE IS AVAILABLE FOR EVERY FROZEN FILE THIS SESSION HIT** —
  `scripts/run_selftests.py` (1,832 findings, crashing, Ⓝ71/Ⓝ71a),
  `tests/test_rederive_agreement.py` (165 findings, one keyword from correct), and the ten other
  over-budget files. **Ⓝ75a: the drain arcs have been scoped as PAYDOWN when they are
  REPLACEMENTS.** Half of `run_selftests.py`'s concerns already have clean, CONSUMED homes; what
  blocked it was never discovery, it was that each extraction had to leave the monolith
  importable. A replacement does not.

  ⚑ **THE CONSTRAINT THAT REMAINS IS REAL AND IS ABOUT CONSUMERS, NOT CONTENT.**
  `module_importers scratch/pycodemod.py` → **0 import sites** — with four `dynamic-import`
  shapes it cannot resolve, named. **That zero must not be acted on**: this tool's consumers are
  CLI INVOCATIONS (skills, hooks, agents, makefiles), not imports, so the population that matters
  is a different one than the reader answers. ⚑ `scripts/hook_structural_query.py` NAMES this
  tool when refusing a textual query — **if the hook points at a path that no longer works, every
  refusal it issues becomes a dead end**, which would break the standing rule at its enforcement
  layer.


* ⚑⚑⚑ **Ⓝ71d ⟡the-runner-has-a-string-surface — CAPTURED BEFORE THE TOOL THAT READS IT MOVES.**
  `module_importers scripts/run_selftests.py` → **0 import sites** (with four `dynamic-import`
  shapes named). Acting on that zero would have read the runner as consumed by nothing. It is a
  CLI, so the population is INVOCATIONS AND PATH LITERALS — `pycodemod --literal
  run_selftests.py` → **49 sites in 27 files**, and the consumers that matter are:

      scripts/gate_status.py:353    the PRE-COMMIT GATE that RUNS it ("tool selftests")
      scripts/climode.py:778-789    4 sites, incl. a `compare` — self-inclusion declared BY PATH
      scripts/build_census.py:219   readers_census names it as a reader
      scripts/worklist_gate.py:440  names it in a refusal message
      substrate/tool_convention.py  :62, module level
      substrate/suite_declared*.py  9 sites — DECLARES the runner's own self-inclusion by path

  ⚑⚑ **SO A REPLACEMENT MUST KEEP THE PATH, NOT MERELY THE BEHAVIOUR.** Half of these are string
  literals naming `scripts/run_selftests.py`; a retirement that moves the working dispatch to a
  new path leaves seven files pointing at a name that no longer answers, and `gate_status` is one
  of them. **⟡mv-is-not-an-edit works precisely because the PATH stays and the CONTENT goes.**

  ⚑ And `suite_declared` DECLARES SELF-INCLUSION BY THAT PATH — the runner is a suite that runs
  suites, so its own identity is spelled as a string in a module that reasons about it. That is
  the sharpest reason the path is load-bearing rather than incidental.

* ⚑⚑ **Ⓝ71e ⟡store-calls-is-not-a-call-census — I GUESSED A CAPABILITY FROM A NAME, AGAIN.**
  Reaching for invocation sites I ran `store_calls.py run_selftests` → **silent, exit 0**. Then
  ran it BARE to read its modes → **also silent, exit 0**. `module_outline` gives the answer in
  one call:

      substrate/store_calls.py: 2 definition(s)
        _called_name      the bare name a call invokes
        connect_sites     the STORE-OPENING call names this file mentions

  It is a **store-connection reader**, not a general call census. The name suggested a capability
  it does not have and I did not check first — the assumed-callee-surface failure, repeatedly
  measured this session, with `module_outline` as the standing one-call fix.

  ⚑⚑ **AND IT EXITS 0 PRINTING NOTHING WHEN RUN BARE**, which is the *"run the tool bare to read
  its modes"* failure the agda-codemod skill records for four tools — **now present in a module
  written HOURS AGO, by an agent, under this session's own conventions.** A tool that cannot
  self-describe teaches its reader to guess. ⚑ Ⓝ71f: bare invocation must print the modes or
  refuse; silence-and-exit-0 is indistinguishable from *"your query matched nothing"*, which is
  the false-zero class in the CLI surface rather than in a census.

* ⚑⚑⚑ **Ⓝ76 ⟡scratch-admits-no-new-files — THE `mv` ROUTE DISSOLVES THE EDIT DEADLOCK AND LANDS
  ON A PACKAGING ONE DIRECTLY BEHIND IT.** Measured with a four-line probe, not inferred:

      scratch/probe_inp.py  →  INP001 File `scratch/probe_inp.py` is part of an implicit
                               namespace package. Add an `__init__.py`.   Found 1 error.

  **No new `.py` file can be created under `scratch/` at all.** `pyproject.toml` declares
  `packages = ["substrate", "scripts"]` and excludes `scratch` DELIBERATELY — *"residence there
  IS the not-yet-promoted status (Λ8)"*. Adding `scratch/__init__.py` would make Λ8's invariant
  unstatable, which is a repo-wide policy change rather than a repair.

  ⚑⚑ **SO ⟡mv-is-not-an-edit IS CORRECT AND INSUFFICIENT: step 1 (move the content away) works;
  step 2 (write a clean replacement AT THE OLD PATH) is refused by a rule neither the operator
  nor I had checked.** The agent performed the move, proved the replacement could not land, and
  RESTORED the file — verified byte-identical against baselines it captured first
  (`--check-contracts`, `--calls`, `--forwards`, `--dead`, `--source`). ⚑ Capturing the baseline
  BEFORE the move is what made the restoration checkable rather than merely claimed.

  ⚑ **AND THE REPAIR'S REAL SHAPE IS NOW NAMED:** `_dispatch` must drain OUT of
  `scratch/pycodemod.py` INTO `substrate/`, because that is the only tree admitting clean files.
  **That is the ⟡mode-standardize / Λ8 promotion arc, not a file swap.** Ⓝ76a: the reachable
  interim is intercepting at the INVOCATION layer — `scripts/hook_structural_query.py` already
  inspects Bash commands and could refuse `pycodemod --attr`/`--importers` using
  `substrate/pycodemod_retired.py` (landed, 12/12, a library nothing yet calls).

  **NOT DONE, and the agent said so plainly rather than reporting the extraction as the fix:**
  both dead modes still answer false zeros. `--importers substrate.corpus` → 0 of 1162;
  `--attr corpus.ROOT` → 0. **The extraction exists; the interception does not.**

* ⚑⚑⚑ **Ⓝ76b ⟡the-correction-was-itself-a-false-absence — AND IT WAS PRODUCED WHILE REPORTING ON
  FALSE ABSENCES.** The agent corrected the prior agent (and my relay, twice) that
  `module_trim --dry-run scratch/pycodemod.py _opt` *"names a tool not in the toolkit"*, on the
  strength of `toolmodes --find module_trim` → **0 hits over 98 tools**. I ran the invocation:

      module_trim --dry-run scratch/pycodemod.py _opt
        FINDINGS  scratch/pycodemod.py  (1 definition(s): _opt)   (nothing written)

  **It works, exactly as originally reported.** `toolmodes` indexes DECLARED MODES over the
  scratch toolkit; `substrate/module_trim.py` is a promoted module and is not in that census. The
  zero was a fact about the index — **the fourth instance this session, and the first produced BY
  an agent whose task was that class.**

  ⚑ **THE CORRECTION WAS STILL WORTH MAKING AND THE METHOD WAS STILL WRONG**, which is the part
  to keep: it doubted a cited invocation (right instinct — I had relayed it twice unverified) and
  then verified against an index rather than by RUNNING IT. **One command settles a claim about a
  command.** The freeze itself was independently reproduced by a one-line whitespace Edit →
  2,145 FINDINGS, so the conclusion survived its broken premise.

* ⚑⚑ **Ⓝ76c ⟡a-shim-would-break-source-readers — WHY THE OBVIOUS DESIGN IS REFUSED.**
  `--literal pycodemod.py` → **97 sites in 36 files**, and the load-bearing consumers do not
  merely INVOKE the tool, they **READ ITS SOURCE**: `check_mode_contracts.ADOPTED` imports it and
  reads `MODES`; `catalog/library/figures.cst_blob_sites` calls `source_of("_cached_defs")`
  against that path; `substrate/tool_usage_selftest.py` quotes the `--attr` doc text VERBATIM.
  **A thin delegating shim at the old path would break every one of them** — the file's TEXT is
  its interface to a third of its consumers, not just its behaviour. All twelve `_pycodemod_*`
  shards already hold the analysis bodies, so what remains at the path is banner + `MODES` +
  `_dispatch`, and all three are read by something.

* ✅ ⚑⚑⚑ **Ⓝ71 / Ⓝ71a ⟡retire-the-runner — DONE. THE RUNNER RUNS.** After a full session blocked
  on it, `python3 scripts/run_selftests.py` completes with **no TypeError**. Verified
  independently: `--list` → **287 suites**, nothing from `docs/`; `module_size` → **12 → 11 over
  budget** with `run_selftests.py` off the list; `run_selftests_selftest` **9/9**.

  ⚑ **`scripts/` ADMITS NEW FILES; `scratch/` DOES NOT** — probed rather than assumed
  (`scripts/probe_admits.py` drew a CONTENT finding, D400, not `INP001`). Both are declared
  packages in `pyproject.toml`; that is the whole difference, and Ⓝ76's wall does not apply here.

  **Moved to `docs/retired/run_selftests.py.retired` by `git mv`, with TWO independent
  guarantees of inertness read from the authorities rather than recalled:** `docs` is in BOTH
  `corpus.SKIP_DIRS` and `suite_discovery._SKIP_TOP`, and the `.retired` suffix means no
  `.py`-keyed walker can reach it at all. ⚑ The empirical confirmation is the one that counts —
  `module_size` scanned it before the move and does not now.

  **16 new files, each clean in one pass with real cases:** `suite_reach_lens` 8/8 · `suite_sample`
  9/9 · `suite_census` 13/13 · `suite_ledger` 11/11 · `suite_report` 11/11 · `suite_modes` 10/10 ·
  `suite_currency` 9/9 · `suite_tenants` 11/11 · `scripts/selftest_pool.py` (roster fan-out) ·
  `scripts/selftest_series.py` (OTLP transport) · the new `run_selftests.py` + suite 9/9.

* ⚑⚑⚑ **AND THE STRUCTURAL CAUSE IS NOW NAMED: THE RUNNER HAD NO SUITE, WHICH IS WHY THE CRASH
  SURVIVED.** *It ran every other tool's cases and had none it could reach.* ⚑ The load-bearing
  arm reads `reach_ratchet`'s **PARAMETER KIND** — it fails when `quiet`/`write` merely become
  positional-CAPABLE, **before any caller makes the mistake**. That is a case pinned upstream of
  the defect rather than at it, and it is the correct answer to a bug whose whole history was
  *the call site and the definition drifting apart*. `--selftest` is now a ROW IN THE MODE TABLE
  rather than a branch beside it, and the flag set is `set(MODES) | MODIFIERS` — derived, not
  restated, with both directions asserted.

* ⚑⚑ **EXIT 1 REMAINS, AND BOTH REASONS ARE PRE-EXISTING RATHER THAN BREAKAGE — the agent
  separated them instead of reporting a red run.**

      selftest-contract: BROKEN — 246 prose suites   (was 240; +6 are its OWN new suites,
                                                      reporting by prose like their siblings)
      selftests: NOT-OK — 22 of 284: 3 cases, 4 refused, 13 silent, 1 unfit, 1 vacuous

  ⚑⚑⚑ **THE 22 ARE NEWLY *VISIBLE*, NOT NEWLY *BROKEN*, AND THE AGENT PROVED IT RATHER THAN
  ASSERTING IT:** the old runner died at `main:2393` **before it ever reached the failure block**,
  and none of the 22 printed a passing line in the before-capture either. **A crash upstream of a
  report is indistinguishable from a clean report, and for a whole session it was read as one.**
  ⚑ And the machinery that was crashing now runs: `selftest-reach: 265 suite(s) reported a count;
  265 classifiable by source, 0 not.`

* ⚑⚑ **Ⓝ71g ⟡the-twin-is-blocked-the-same-way — A SECOND, INDEPENDENT INSTANCE OF THE SAME BUG,
  FOUND BY THE GATE THE FIX RESTORED.** `gate_status` now shows
  `FAIL(1) tool unit tests — TypeError: may_write() takes 0 positional arguments but 1 was given`
  at `tests/test_rederive_agreement.py:202` (`ratchet.may_write(False)`). The one-keyword fix was
  attempted and **refused — 165 findings, the identical shape one file over.** ⚑ It became
  visible only because the runner stopped crashing first: **a fix upstream turns the next
  instance from invisible into named**, which is what draining a monolith buys beyond the drain.

* ⚑⚑⚑ **Ⓝ71h ⟡nearly-reinvented-a-deleted-module — CAUGHT BY READING CONFIG FOR AN UNRELATED
  REASON, WHICH IS NOT A REPEATABLE METHOD.** The first cut put the roster fan-out at
  `substrate/suite_runner.py`. **`pyproject.toml:479` records that exact file being DELETED under
  ⟡last-retire**, because `make` now owns the build path's fan-out and `substrate/suite_run.py`
  was narrowed to one suite.

  ⚑ The CLI roster's fan-out IS a genuinely different consumer, so the capability was real — it
  landed at `scripts/selftest_pool.py` **with that distinction stated in its docstring, rather
  than as the deleted module returning under a new spelling.** ⚑⚑ *A deletion rationale that
  lives only in `pyproject.toml` is reachable by accident.* The reuse-search this repo mandates
  fires on `catalog/reuse-index.md` and the structural tools; **a module deleted for a stated
  reason is invisible to both, because it is not there to be found.** Ⓝ71i: deletions with
  rationale need a reader — the residue is the argument, and it is currently in a config comment.

* ✅ ⚑⚑⚑ **Ⓝ76a / Ⓝ76b ⟡intercept-at-the-hook — DONE. THE FALSE ZEROS ARE GONE, REFUSED AT THE
  ONLY LAYER THAT COULD SEE THEM.** Verified live by me, not from the report:

      pycodemod --attr corpus.ROOT
        pycodemod: --attr is RETIRED — it returned FALSE ZEROS.
          why:      DOCUMENTED BUT NEVER IMPLEMENTED: only `.*` was special-cased, so a dotted
                    operand was compared against a bare attribute name and could never match.
          measured: corpus.ROOT: the origin said 0; the successor finds 121 in 66 files.
          use:      python3 substrate/attr_reads.py <operand>

  ⚑ **THE REFUSAL CARRIES ITS OWN MEASUREMENT AND ITS SUCCESSOR COMMAND**, so a reader who hits
  it needs no second lookup. Compare what it replaced: `0 attribute read(s) in 0 of 1181 files`,
  delivered with full confidence, in the census this repo DELETES on.

  ⚑⚑ **THE HAZARD I FLAGGED WAS REAL AND WAS GUARDED CORRECTLY: the verdict keys on
  tool-AND-retired-flag, never on the tool.** The hook's own refusal text RECOMMENDS
  `scratch/pycodemod.py` as the owner of `.py`; keying on the tool would have made the gate
  refuse the tool it recommends and **turned every refusal it issues into a dead end.** Verified
  end-to-end: `grep -n def scratch/pycodemod.py` still refuses and still names that tool, and the
  route works (`--calls` answered in the same session). ⚑ The mirror case is armed too — the
  SUCCESSOR `attr_reads.py` takes the same `--attr` flag and is NOT refused.

  ⚑⚑ **AND TWO DESIGN CHOICES THE AGENT MADE THAT I WOULD NOT HAVE SPECIFIED:**
  (1) the retirement verdict **DENIES UNCONDITIONALLY** while the textual-query verdict stays
  advisory — *"an advisory textual query still yields a truthful-if-clumsy answer; a retired mode
  answers 0 with full confidence."* **Advisory is right for a style rule and wrong for a
  known-wrong instrument.** (2) the import of `pycodemod_retired` is **OPTIONAL**, because the
  hook is symlinked into five checkouts with no `substrate/` package and an ImportError there
  would take the whole gate down — **which fails OPEN, allowing every subsequent command.**

  `ORIGIN_STEMS` keys on the STEM, so `python3 scratch/pycodemod.py`, `./scratch/pycodemod.py`
  and an absolute path from a borrowing checkout are ONE case — *keying on one spelling is the
  defect this repo has paid for twice.* `--` honoured live: `--literal -- --attr` searched for
  the STRING, 47 sites. Counts: `hook_structural_query` 35 → **52/52**; `pycodemod_retired`
  12 → **22/22**; `run_selftests --list` 287 unchanged; `file_mode` 0.

* ⚑⚑⚑ **AND A WORKING-MODE CHECK INDEPENDENTLY CONFIRMED Ⓝ71a's STRANDED EXTRACTION IS NOW
  WIRED.** `--calls reach_ratchet` returns **1 def, 7 calls** — where it read **2 defs, 16 calls**
  before the retirement. The monolith's duplicate is gone; only `substrate/reach_ratchet.py:141`
  remains, and the new runner CALLS it rather than redefining it.

  ⚑ **THE AGENT NOTED THE DRIFT AGAINST ITS OWN BRIEF** (*"note the tree has moved since the 2/16
  in the brief"*) rather than reporting the number it was given. A figure quoted in a brief is a
  snapshot; the tree moved between dispatch and execution, as it has all session. **That is the
  same discipline as re-reading the census at dispatch time, applied by an agent to the
  coordinator's own numbers.**

* ⚑ **Ⓝ78 ⟡mode-contracts-red-from-elsewhere:** `check_mode_contracts.py` fails on
  `jea/metalanguage/schema.py::--sizes::undeclared`. That file was `AM` in the session's OPENING
  git status — someone else's in-flight work, untouched here. **It will block a commit until
  resolved**, and it is named rather than fixed because fixing another arc's staged file silently
  is worse than a red gate that says which file.


* ⚑⚑⚑ **Ⓝ88 ⟡split-and-annotate-are-one-drain — I INVENTED A SEQUENCING QUESTION BY TREATING
  "ANNOTATE" AS A SEPARATE PASS.** Operator, on my *"the leaf wants splitting and annotating, and
  the order between those isn't obvious"*: *"I don't see a conflict; That's just a full drain,
  like any other monolith."*

  **There is no ordering problem because there are not two operations.** When `sorted_stream.py`'s
  20 defs become single-responsibility modules, **each lands in ONE WRITE under the per-file
  gate — and a clean write under `disallow_any_expr` IS an annotated one.** The gate does not
  accept a split-but-unannotated file. *Annotation is not a pass that follows the split; it is
  what landing a module COSTS.*

  ⚑⚑ **AND THAT DISSOLVES Ⓝ32a‴'s CENTRAL FINDING, WHICH WAS REASONING ABOUT THE WRONG
  DESTINATION.** The agent reported *"n-splitting was neither required nor available… splitting it
  would produce two clean-shaped files that both still fail, because both would still import
  `jea_pyalg`."* **That asks whether splitting fixes the file IN PLACE. It does not — and the
  drain never fixes anything in place.** It moves the concerns OUT, to `substrate/`, where they
  can be clean. **The same route this session proved five times** (`run_selftests` retired, six
  inline tails split, `record_migrate`): *extract the concern into a NEW clean module and keep
  cutting until the dispatch moves too.*

  ⚑ **SO THE "CLOSURE BOUNDARY" WAS A BOUNDARY ON A ROUTE NOBODY NEEDED TO TAKE.** `jea_pyalg.IR`
  taints `type[IR]` **for a file that stays in `jea/`**. A concern extracted to `substrate/`
  carries its own annotated types and does not import the untyped hub at all. **The wall is real
  and it is around the wrong thing** — it bounds in-place repair, not the drain.

  ⚑⚑ **AND THE PAPERKIT MEASUREMENT (Ⓝ87b) IS CONSISTENT WITH THIS, NOT AGAINST IT.**
  *"3 own findings → 231 with the callee followed"* is what happens when you NAME AN IMPORT into
  an untyped hub. A drain does the opposite: it takes the concern away from the hub, so there is
  no import to name and nothing to surface. **"Type the callee, verify it clean, then name it" —
  the drain IS the first two clauses**, performed by relocation rather than by editing a file that
  refuses edits.

* ⚑⚑⚑ **Ⓝ88a ⟡scratch-is-drained-not-packaged — AND THAT CORRECTS MY Ⓝ76 FRAMING TWICE OVER.**
  Operator: *"we're not converting scratch to a package; we're draining it."*

  I framed `INP001` in `scratch/` as **a wall to route around** (Ⓝ76 — *"the `mv` route lands on a
  packaging deadlock"*), then the Ⓝ87 agent framed it as **a policy to preserve** (*"the invariant
  is live and mechanized; packaging would make it unstatable"*). ⚑ **Both readings treat
  `scratch/` as a place that persists.** It is not: **it is a staging area whose correct final
  size is zero.** `INP001` is neither an obstacle nor a fence — **it is the exit sign.**

  ⚑ So `check_scratch_independence` (Λ8) is not defending a permanent boundary; it is measuring a
  RESIDUE, and the answer to *"scratch admits no new `.py` files"* is **stop putting things there
  and take out what is left** — the same shape as `never discard residue` meaning *rehome it*,
  never *keep the drawer*.

  ⚑⚑ **AND `scratch/pycodemod.py` IS THE INSTANCE THAT PROVES IT** — 2,145 findings, `_dispatch`
  at 2,173 lines, unfixable in place, its `--attr`/`--importers` modes now REFUSED at the hook
  because they answered false zeros. **The refusals are live and the origin still sits in the
  staging area.** Ⓝ68b″ read as *"promote the dispatch"*; under this ruling it reads as **the next
  file to drain**, and the destination was never in doubt.


* ⚑⚑ **Ⓝ71g″ — THE GATE READING LANDED, AND THE "CHECK THE OTHER FOUR FOR THE SAME SHAPE"
  HYPOTHESIS IS FALSE FOR THE FIRST ONE I TESTED.** The agent's closing advice was that the
  monolith's `RatchetWriteGuardTest` *"was redundant before it was broken — worth checking the
  other four classes for the same shape before rewriting them."* **A good instinct and a
  hypothesis, so I tested it.**

  `--source ImportEdgeAgreementTest` returns a **real cross-authority agreement test with no twin**:
  the BUILD GENERATOR's import-edge set (`gen_build_makefiles.IMPRE`) against the LEXER's
  (`imports_via_agda_lex`), asserting the generator never holds FEWER — *"a missing edge is the
  unsafe direction, because make's staleness model depends on it."* It carries its own incident:
  *"the assertion that would have caught the Añelé bug on the day it was written, instead of it
  shipping into a committed artifact."*

  ⚑ **SO THE FIVE CLASSES ARE NOT ONE POPULATION.** One was a stale duplicate of a correctly-owned
  arm; this one is the ONLY thing pinning an agreement between two independent readers of the same
  fact. **A drain that treats them alike would delete a cross-authority check to remove a
  duplicate** — and I would have carried the hypothesis forward as guidance had I not run
  `--source`. *An agent's closing advice is a hypothesis with the least scrutiny on it, because it
  arrives after the verified part.*

  ⚑ It also does `sys.path.insert` + a bare `import gen_build_makefiles` **inside the test body**,
  which is Ⓝ87's shape (the prologue that makes a tree unreadable) and Ⓝ86's (`sys` ownership),
  in a file that cannot be edited. **The drain of these four is where three arcs meet.**

* ⚑⚑ **THE GATE READING ITSELF — 36 gates, 14 pass, 22 FAIL, and the agent partitioned the reds
  rather than reporting a number.** Line 1 is still `FAIL(1) tool unit tests — TypeError:
  may_write() takes 0 positional arguments`, so **Ⓝ71g's criterion is measured NOT MET**, not
  inferred. `feature coverage` moved to PASS — the gate its scenario-renaming broke and then
  repaired by aligning to the scenario `features/` already declares.

  **The 21 other reds, by kind:** 5 census/sync drift (each naming its regenerating command) ·
  **12 paydown-only ratchets** (ban 375, mypy 1133, cap-128 146, public 35, sumtype 26, divergence
  14, claims 7, discharge 4, private 2, mode contracts 1, rederive 42, carrier locality) ·
  1 environmental (`tsdbprobe` → *"NOT CONFIRMED within 45s — Connection refused"*, **and the
  agent applied this repo's own rule: not confirmed is NOT failed**) · 3 other.

  ⚑ **AND IT BOUNDED ITS OWN CLAIM ABOUT THE MYPY RED:** *"I typechecked only my two new files
  (clean); I have not established that my additions are absent from that 1133, only that they are
  not the CAUSE of it."* **That distinction is exactly the one Ⓝ89′ cost me** — *not the cause* and
  *not present* are different claims, and only one of them was measured.

  ⚑ **A LATENT TRAP THE AGENT NAMED FOR THE FUTURE DRAINER:** `check_feature_coverage` is
  currently clean **partly because the monolith still declares its copies**. When the drain lands,
  two scenarios in `features/derived_view_invariant_0_agreement.feature` will be claimed only by
  the extracted modules. The names were aligned deliberately so the transition is a no-op —
  **"but it should be re-run at that point rather than assumed."**


* ⚑⚑⚑ **Ⓝ78 ⟡mode-contracts-red — REFUSED, AND A ONE-LINE DECLARATION IS NOW GATED BEHIND A
  FOURTH DRAIN.** `jea/metalanguage/schema.py` is **gate-frozen at 582 findings** (`INP001`,
  `I001`, 4,547 further lines withheld). The write was refused and reverted; **`git status` shows
  `AM`, unchanged from session start** — the other arc's in-flight state, untouched.

  ⚑ **AND THE DISPATCH LIVES IN `schema.py`'s `__main__` BLOCK**, so this is exactly the shape the
  refusal text warns about: *extracting one concern STRANDS when the only consumer is inside the
  file, because wiring the new module in is itself a refused edit.* **The drain has to carry the
  dispatch out too** (Ⓝ88). *A one-line mode declaration is behind a 1,300-line monolith.*

* ⚑⚑ **THE AGENT RAN A FOURTH VERIFICATION I HAD NOT ASKED FOR, AND IT IS THE ONE THAT SETTLES THE
  GATE'S OWN AMBIGUITY.** `toolmodes --find sizes` — confirmed by me:

      ── NAMED but not declared  (prose mention / undocumented dispatch)
         --sizes   dispatched by jea/metalanguage/schema.py, in no usage line — UNDOCUMENTED
      ── by FUNCTION
         corpus_size_report  in jea/metalanguage/schema_diag.py  `--sizes` — the .agdai and jsonb …

  **The gate's message offers three remedies — declare / delete the phantom row / honour the
  contract — and cannot tell you which.** `toolmodes` HAS a category for it, names the dispatcher
  AND the implementation, **and therefore rules out "phantom" on its own.** ⚑ *A gate that names
  its remedies without discriminating between them leaves the choice to whoever reads it; a census
  with the right category makes the choice for them.* Ⓝ67 ⟡the-slot-is-the-reach, arriving as a
  tool that already had the slot.

* ⚑⚑ **AND `pycodemod --declare-modes` DOES NOT SOLVE THIS, BY DESIGN — the gate's own suggested
  remedy is inapplicable and says so.** It emitted 38 skeletons as
  `Mode(operand=?, paths=?, scans=?, writes=?, why="")` and printed *"this file declares none — a
  foreign file has no roster"* (it compares against ITS OWN `MODES`). Its footer states the
  blanks are deliberate: ***"a `scans=False` emitted by a program satisfies `--check-contracts` by
  construction, which would clear the gate by removing its power to bite."***

  ⚑ **A GENERATOR THAT COULD FILL THOSE FIELDS WOULD DEFEAT THE CENSUS IT FEEDS** — so the tool
  refuses to guess, and the entry must be hand-written. *The gate names a remedy that the remedy's
  own author has deliberately made unable to complete it.*

* ⚑ **THE DECLARATION THE AGENT WOULD HAVE LANDED, and both placement arguments come from lessons
  the file already records about ITSELF:**

      ("--sizes", "does .agdai FILE size predict DECODED document size? — the two distributions "
                  "joined per core, with Pearson and Spearman. It answers a SIZING question: a "
                  "capacity estimate taken from disk is measuring the wrong variable, because "
                  "the expansion happens in the DECODE")

  **In `_MODES`, never a post-hoc `MODES["--sizes"] = Mode(...)`** — because `check_mode_contracts`
  imports the module and reads the RUNTIME roster (a post-hoc entry satisfies it) while
  `toolmodes --divergence` reads the SOURCE pairs list (a post-hoc entry stays invisible).
  **Paying one census does not pay the other** — `census-keyed-on-one-spelling`, recorded three
  times in that file and still the live trap. And **no `writes`**: `--sizes` is a pure read, and
  the file records guessing `--transport`'s `writes` wrong in the direction that would demand an
  `--apply` guard on a mode that changes nothing.

  ⚑ **No measured number in the gloss** — r and ρ stay in the mode's OUTPUT, where they are
  re-derived per run (Ⓝ85). The agent applied that unprompted.

  **Ⓝ78′ ⟡drain-schema — the fourth drain**, queued behind the three. Its acceptance is the
  one-line declaration that could not land today.


* ✅ ⚑⚑⚑ **Ⓝ88b ⟡drain-sorted-stream — THE DRAIN ROUTE WORKS FOR `jea/`. THE MONOLITH IS AT ZERO.**
  Verified by me: `pycheck_show jea/metalanguage/sorted_stream.py` → **CLEAN**. A
  `jea/metalanguage/` file at zero findings under ruff+mypy, which **Ⓝ32a‴ concluded was
  unreachable.**

  ⚑⚑ **THAT CONCLUSION WAS ABOUT IN-PLACE REPAIR, AND THE DRAIN NEVER REPAIRS IN PLACE.** The
  agent's evidence is the sharpest possible form: **the five `substrate/` modules import nothing
  from `jea/` at all** — *"which is exactly why they are clean, and exactly what in-place repair
  could not achieve."* The `jea_pyalg.IR` taint bounds a file that STAYS in `jea/`; a concern
  extracted carries its own annotated types and never names the untyped hub. **The closure
  boundary was real and it bounded the wrong thing.**

  ⚑ Measured payoff: the ratchet's `arg-type::jea/metalanguage/sorted_stream.py (2x)` entry is
  **paid off**. 7 touched/new files all clean. `self_import`: substrate 332→334 modules, **0 new
  cycles** — the new suites import their subjects ONE-WAY, *"cleaner than the 15 existing trailer
  pairs."*

* ⚑⚑⚑ **AND THE REUSE-SEARCH FOUND A PRIOR DRAIN ~60% DONE — WHOSE CASES NEVER MOVED WITH THE
  CONCERN.** `substrate/sort_key.py`, `sorted_carrier.py` and `sorted_source.py` already held
  `SortKey`/`OrderError`/`Rev`/`extractor`, the carrier, and all four producers. **Two gaps: the
  combinator layer was never extracted, and `sorted_carrier` + `sorted_source` were extracted
  WITHOUT SUITES.** Only `sort_key` had one.

  ⚑⚑ **SO THE DEFECT THIS SESSION HAS BEEN CLOSING ALL DAY — a module whose changes nothing
  catches — WAS SITTING INSIDE ITS OWN PRIOR WORK, UNCOUNTED.** Verified: `sorted_carrier` now
  **22/22**, `sorted_source` 15/15, both suites written today for modules extracted earlier.
  *An extraction that leaves its cases behind produces a clean-looking module and a silent one,
  and the coverage census reads it as covered the moment a sibling appears.*

* ⚑⚑ **THE MODULE SEAM IS A PROPERTY, NOT A SIZE — AND IT IS THE BEST SPLIT-CRITERION THIS SESSION
  HAS PRODUCED.** `sorted_combinator` (29/29) is *everything that calls `require` and CAN REFUSE*;
  `sorted_transparent` (12/12) is *everything TOTAL*. **A reader learns from the import line
  whether a call can fail.** Compare every other split today, which cut by concern-name; this one
  cuts by a property the type system almost expresses.

  ⚑ **AND THE SUITES ARE NOT A TRANSCRIPTION OF THE OLD 227-LINE `_selftest`** — they add arms it
  never had: a producer's DECLARED KEY (not just its rows); **`already` staying SILENT on a lying
  source** (its contract, previously untested — *only the `checked`/`already` PAIR discriminates*);
  `project` DROPPING a getter bound to a replaced row shape; and cost arms with ceilings **derived
  from the algorithm rather than fitted to the observation.** *That last is the difference between
  a case and a recording of what happened once.*

* ⚑⚑ **TWO GATE FINDINGS TO PROPAGATE, AND THE FIRST CORRECTS MY OWN BRIEF.**
  **(1) `chmod +x` is required BEFORE the first edit, not after.** Both new modules passed their
  initial `Write` and were refused on the NEXT edit with `EXE001` — **a shebang'd file lands
  looking accepted and fails later.** My brief called it "a latent EXE001"; *it is not merely
  latent, it fires on the second touch*, which is worse because the author has by then banked the
  file as good.
  **(2) Reading a mutable property twice around a mutation is refused as `unreachable`.**
  `if not stream.consumed` after `list(stream)` narrows to a constant. **Collect both readings as
  DATA, then compare the pair** — recorded in the suite's docstring, and a shape that will recur
  in any test of a consumable.

  ⚑ **AND THREE TOOLS PRODUCED EMPTY OUTPUT ON EVERY INVOCATION INCLUDING A POSITIVE CONTROL** —
  `substrate/mypy_census.py`, `substrate/suite_discovery.py`, `module_outline --tail`. *"They are
  libraries, not CLIs. I report that as a fact about those entry points, not about the tree."*
  **That is Ⓝ71f ⟡bare-invocation-must-speak, found again by someone who needed them to work** —
  and the agent routed to the write gate and the checkers directly rather than trusting a silence.

  ⚑ **THE MONOLITH IS A FORWARDING SHIM, NOT DELETED.** `module_importers` reports 0 static sites
  **and names 7 dynamic-import shapes it cannot resolve** — *"a zero that bounds itself is not an
  absence"*, and those 7 are the selftest/gate discovery machinery reaching the file as a suite.
  **Ⓝ68b's fix deciding a deletion question, correctly, for the third time today.**


* ✅ ⚑⚑⚑ **Ⓝ71g″ ⟡drain-test-rederive — COMPLETE. THE MONOLITH IS GONE AND THE LIVE GATE FAILURE
  IS CLOSED.** Verified by me: `python3 -m unittest discover -s tests -q` → **`Ran 52 tests … OK`**
  (was `Ran 54 … FAILED (errors=1)` on the `may_write()` TypeError that has held `gate_status`
  line 1 red all session). `check_feature_coverage` run AFTER the drain, not assumed:
  **`clean (52 scenario(s), all implemented)`** — the name alignment held as a genuine no-op in
  BOTH directions, no orphans and no stale.

  ⚑ 52 not 54 because `RatchetWriteGuardTest`'s two arms were the already-superseded duplicates —
  `substrate/baseline_io_selftest.py:67` had pinned the failing arm correctly all along.

  ⚑⚑⚑ **AND THE "CHECK THE OTHERS FOR THE SAME SHAPE" HYPOTHESIS IS FALSE FOR ALL FOUR, NOT JUST
  THE ONE I TESTED.** Each was checked for a twin before moving, and each is unique for a
  DIFFERENT reason — which is why a uniform drain would have destroyed coverage:

      ImportEdgeAgreement     `gen_build_makefiles.IMPRE` bound at 2 sites tree-wide, neither a
                              test; the generator has NO `--selftest` (the agent RAN it — the flag
                              was ignored and it did a real generation run). The near-miss uses
                              IMPRE only as a synthetic source STRING.
      ImportNameCharClass     a co-owner exists with a BYTE-IDENTICAL regex — and it is a PAYDOWN
                              RATCHET: tolerates offenders, admits `⚑rederive:` opt-outs, excludes
                              tests/. ⚑ It asserts NO NEW KEY; this asserts ZERO. Its own docstring
                              names this suite as the complete instrument it approximates.
      ModuleSetAgreement      the near-miss pins `agda_files()` on SYNTHETIC TEMPDIRS, never
                              touching agda/Substrate; `agda_lex._selftest` spot-checks ONE
                              hardcoded file out of ~3598.
      DeclarationVisibility   `check_carrier_locality` has 0 static import sites; the near-miss
                              counts SPELLINGS, never runs `DECL`, and does not know about the
                              indent anchor — which is the actual defect.

  ⚑⚑ *"A co-owner that asserts a weaker claim is not a twin"* is the distinction that saved three
  of these. **A duplicate-detector keyed on TEXT would have deleted `ImportNameCharClass` on a
  byte-identical regex.**

* ⚑⚑⚑ **Ⓝ87 ARRIVED AS A WALL AND THE ANSWER WAS STUBS, NOT PACKAGING.** The prologue could not
  simply be *"imported properly"*: a bare `import agda_lex` from a clean file is
  `import-not-found` and the `Any` propagates; `from scripts.gen_build_makefiles import IMPRE`
  **FOLLOWS INTO THE UNTYPED SOURCE (135 findings) and is refused.** ⚑ **A stub is keyed on the
  BARE module name, so the package-path spelling BYPASSES it** — the bare import plus
  `tests/__init__.py`'s anchored `sys.path` is the only route that is both typed and clean.
  Three new stubs (`agda_lex`, `gen_build_makefiles`, `check_carrier_locality`); the prologue is
  gone from all four modules. *That is `pyproject.toml`'s own rule — "a STUB that ADDS types" —
  applied to first-party code rather than a dependency.*

  ⚑⚑ **AND `check_stub_authority` (stubtest) CAUGHT SIX INVENTED SIGNATURES ACROSS THE FIRST
  DRAFTS** — `head_span`'s `limit`, `intended_operator`'s `op`/`index`, `telescope_groups`' `span`,
  `unresolved_sections`' arity, `root_text`'s parameters, and **`AGDA_JOBS` which is `str` ('20')
  not `int`.** *Exactly the failure the existing stubs' docstrings predicted.* Now
  `clean (5 stubs match)`. **A stub is a claim about a callee, and this repo has a gate that
  refuses an invented one.**

* ⚑⚑ **Ⓝ68b″ ⟡drain-pycodemod — PARTIAL, ONE CONCERN, AND THE ORIGIN'S BEHAVIOUR IS VERIFIED
  UNCHANGED BY DIFFS RATHER THAN BY BYTES.** `substrate/module_layout.py` + suite (8/8) — the
  "where does this file cut" reader — **verified row-identical to `pycodemod --layout` on the same
  input.** Every captured mode re-run: `--calls` byte-identical, `--check-contracts` fully green
  (11 of 11, 0 harmful), `pycodemod --selftest` **408/408**; the only diffs are the denominator
  moving (1198→1206 files) and `--literal` gaining exactly 2 `doc`-role sites — **its own two new
  docstrings citing the origin.**

  ⚑ **I CHECKED ITS "BYTE-IDENTICAL" CLAIM AND IT IS NOT LITERALLY TRUE, WHICH IS FINE.**
  `git diff --stat scratch/pycodemod.py` → **2,966 insertions** (1,204 staged). Both pre-existing
  (`MM` at session start), and `ls` shows the file modified at **17:54 — hours AFTER
  `module_layout.py` at 11:33**, so ANOTHER ARC IS WRITING IT NOW. *The agent's mode-level
  before/after is the stronger evidence anyway: it tests behaviour, and bytes in a concurrently-
  edited file cannot be a control.*

  ⚑ **THREE DELIBERATE IMPROVEMENTS OVER THE ORIGIN, EACH CARRYING ITS INCIDENT:** `ast` instead
  of libcst (*"in a checkout without libcst the one mode whose job is 'help me split this file' is
  unavailable — the exact failure the origin already paid for when `--size` died in
  `cst.metadata`"*) · **decorator spans** (`node.lineno` points at `def`, not the first `@`, so a
  cut on that line leaves decorators behind — **a syntax error in BOTH halves**; the origin has
  this bug) · **a printed denominator** (the origin prints nothing for a file with no groups,
  *"which reads as THIS FILE NEEDS NO SPLIT — the confident zero, on the question where it is most
  expensive"*).

  ⚑⚑ **`MODES` MUST STAY AT `scratch/pycodemod.py` — A REAL CONSTRAINT ON THE END STATE.** It is a
  declaration inseparable from the dispatch it declares (`scan_contract`/`declare_modes` compare
  roster against dispatch SOURCE); **it drains only when `_dispatch` does.** All three
  source-readers verified green. Both retired-mode refusals still fire. ⚑ **The remaining mass is
  ONE OBJECT**: `_dispatch` is 2,173 of the file's lines and every other def is roster-analysis
  coupled to `MODES` — *"the cheap, genuinely-separable concern was `layout`; the rest does not
  decompose further without moving the dispatch itself, which is the transaction, not a step."*

* ⚑ **TWO FINDINGS TO CARRY:** `substrate/module_outline.py` **has no selftest** (`--selftest` is
  read as a PATH and crashes) and uses the retired `sys.exit(main(sys.argv[1:]))` — *the tool I
  have told six agents to use before assuming a callee's surface.* And
  **`gherkin_scan.quoted()` DISCARDS CLAIMANT ATTRIBUTION** — it holds the path `p` and drops it
  into a flat set, so nothing can answer *"which test claims scenario N"*; `_stale_lines` renders
  name-only while `_orphan_lines` renders `file: name`. **`claimants(tests) -> dict[str,
  list[str]]` beside it would close it** — `list`, not `str`, since two tests may legitimately
  quote one scenario. Left as a finding, outside that task's ownership.


* ⚑⚑⚑ **Ⓝ78′ ⟡drain-schema — REFUSED, AND THE AGENT DISTRUSTED THE INSTRUMENT I HANDED IT.**
  `type_scope jea/metalanguage/schema.py` → **287 messages, 287 OWN, 0 INDUCED, 0 SUPPRESSED** —
  which reads as *"a drain moves nothing."* **It is the `sppf_tree` blind shape**, and the agent
  confirmed it two ways rather than banking it:

      module_outline schema.py  →  1 definition in ~1,300 lines   (verified by me)
      the file does sys.path.insert and imports its siblings BY BARE NAME

  **`unfollowed-first-party` — mypy cannot resolve those from source, so they are `Any` in BOTH
  arms, the differential never reaches them, and the file reads as OWNING WHAT IT INHERITS.**
  ⚑ A 1,300-line file with ONE def owns almost nothing; its body is star-imports and dispatch.
  *I briefed that caveat as a thing to read against the result, and the result was entirely that
  caveat.*

* ⚑⚑⚑ **AND THE `sorted_stream` PRECEDENT DOES NOT TRANSFER, ON ITS OWN STATED CONDITION.** That
  drain worked because **the extracted modules import nothing from `jea/` at all.** `--sizes`
  fails that at both ends:

  **(1) Its implementation is DB-BOUND TO THE HUB BY CONSTRUCTION.** `corpus_size_report`
  (`schema_diag.py:1493-1599`) depends on `_cli_connect`, `relations`, `scalar`, `rows`,
  `_bucket_pow2`, `_pearson`, `_spearman`, `_human` — the live connection layer and shared
  formatting, all inside `jea/metalanguage/`. **Not an accident of layout.**

  **(2) The hub carries 323 ATTRIBUTE READS ACROSS 16 FILES** — verified by me
  (`attr_reads "_schema.*"`): `sppf_db` ~150 alone, plus `reconstruct`, `sppf_decode`,
  `sppf_drain`, `sppf_tree`, `sppf_vocab`, `catalog_db`, `graded_orbit`, `query_registry`,
  `scope_store`, `catalog_query`, `set1_ratchet_cores`, and more. ⚑⚑ **The module's own docstring
  says NINE importers. The measured figure is sixteen files and 323 reads.**

  ⚑ **AND `module_importers schema` RETURNS 0 — A FALSE ZERO THE AGENT DID NOT BANK.** It
  disclaims 8 unresolvable shapes including the star re-export chain. *"The 323-read census is the
  decorrelating second spelling, and it disagrees by 16 files."* **Two readers, one question, and
  the honest zero is what sent it to the other reader** — Ⓝ68b's fix deciding a scoping question
  for the fourth time today.

* ⚑⚑ **THE ESCAPE ROUTE WAS TESTED AND IS CLOSED — a genuinely new finding.** Could the declaration
  land in a NEW clean module, avoiding the frozen file? **No.** `climode.contract_rows` locates
  each branch with `branch_bounds(src)` **over the DISPATCHING FILE'S OWN SOURCE**, and the
  `--sizes` branch is at `schema.py:539`. **The roster must resolve as `schema.MODES` AND the
  branch must be IN `schema.py`. Both halves require editing the frozen file.**
  ⚑ The freeze was confirmed empirically, not assumed: the minimal correct `_MODES` pairs entry
  was attempted and **refused and reverted**, quoting 582 findings and no partial-credit path.

  ⚑ **"CENSUSES I EXPECT TO HAVE MOVED: NONE"** — and it verified rather than asserting:
  `check_mode_contracts` still exit 1 on the SAME SINGLE ROW (not grown), `toolmodes --divergence`
  unchanged, `--sizes --live` byte-identical to the captured baseline (r = 0.7779, ρ = 0.7631,
  2,477 pairs). **A report that a concurrent agent's readings are undisturbed, stated as a
  measurement.**

* ⚑⚑⚑ **THE SEAM, WITH A HARD ORDERING CONSTRAINT AND TWO GUARDS THAT WILL FIRE:** it is a
  **RE-EXPORT HUB RETIREMENT**, not a drain. **(1)** rewire the 16 consumers off `_schema.*` onto
  the real owners (`rows`/`ph`/`scalar`/`execute`/`upsert` → `schema_rows`;
  `core_path`/`relations`/`columns_of` → `schema_diag`; `_TIERS`/`apply` → `schema_decl`;
  `drained`/`reclaim` → `schema_queue`) — **each an edit to a CONSUMER, individually landable, none
  touching the frozen file**; `sppf_db` (~150 reads) can go alone. **(2)** only then do the
  star-imports lose their justification and the F401/F403 mass become deletable. **(3)** the
  dispatch moves out LAST, carrying `_MODES`, at which point `--sizes` is declared in a file clean
  by construction and `schema.py` is RETIRED rather than edited.

  ⚑⚑ **AND TWO GUARDS PIN BODY-IN-PLACE AND WILL FIRE AT STEP 3:** `schema_selftest` slices
  `getsource(schema)` between `'if "--holes" in sys.argv:'` and `'if "--fibre"'` asserting three
  literals are inside, and `_selftest` scans this module's own source for direct-connect bypasses.
  **Moving the dispatch without moving those guards leaves them scanning a file that no longer
  contains what they police — PASSING BY MEASURING NOTHING, which is the failure they exist to
  catch.** They must move in the same commit.

* ⚑⚑ **AND A CORRECTION TO THE Ⓝ90 AGENT'S CLOSING CLAIM, WHICH I VERIFIED RATHER THAN RELAYED.**
  It reported *"`tests/test_import_edge_agreement.py` … `ModuleNotFoundError: No module named
  'agda_lex'` — now declared in the roster, so it will run and fail on the next full gate pass.
  Worth fixing before the roster's green is trusted."* **Measured:**

      python3 -m unittest tests.test_import_edge_agreement -q   →  Ran 1 test … OK
      python3 -m unittest discover -s tests -q                  →  Ran 52 tests … OK

  **The `ModuleNotFoundError` was an artifact of how the ROSTER HARNESS invoked it**, not a
  property of the suite — run with the package context `tests/__init__.py` provides, it imports
  and passes. ⚑ *A failure observed through one dispatcher reported as a fact about the subject* —
  the same shape as the four false absences this session, arriving in a closing paragraph where
  scrutiny is lowest. **Its other four verdicts stand; this one does not.**


* ⚑⚑⚑ **Ⓝ78″ ⟡rewire-the-schema-consumers — REFUSED, AND IT CAUGHT A MAPPING ERROR I WOULD HAVE
  SHIPPED. FIVE OF THE NAMES I GAVE IT WERE WRONG.** I supplied an owner mapping from a prior
  agent's read and flagged it as a hypothesis to verify. It verified, and corrected — confirmed by
  me against `module_outline schema_rows.py`:

      relations · columns_of        I said schema_diag  →  ACTUALLY schema_rows (:302, :347)
      apply                         I said schema_decl  →  ACTUALLY schema_rows (:769)
      require_indexes · require_tiers · intern
                                    I said schema_decl  →  ACTUALLY schema_diag (:604, :652, :270)
      sandbox_fixture · dedup · schema_version · set_schema_version
                                    I left unmapped     →  ACTUALLY schema_rows

  ⚑⚑ **AND THE STAR RE-EXPORT WOULD HAVE MADE EVERY WRONG REWIRE STILL RUN.** *That* is why the
  brief said verify: a rewire to the wrong owner is not a crash, it is a working import that
  records a false ownership claim — **and the next reader inherits it as fact.** *The safety net
  that makes the hub convenient is exactly what hides a mis-rewire.*

* ⚑⚑⚑ **THE BLOCK IS ONE LAYER DOWN FROM WHERE I EXPECTED: IT IS NOT THAT `schema.py` IS FROZEN —
  IT IS THAT ALL 16 CONSUMERS ARE FROZEN TOO.** Aggregate ruff over them: **3,976 findings**.
  `reuse_tui.py` alone is **1,074**; the SMALLEST is `query_topo.py` at 80 (verified: 3 defs).

  ⚑ **AND IT RAN THE DECISIVE TEST RATHER THAN INFERRING IT** — a single-token Edit on
  `reuse_tui.py:95` (`import schema as _schema` → `import schema_rows as _schema`, the minimal
  correct rewire, which *also* pays down a `PLC0415`). **Refused**, with the governing rule in the
  refusal: *"1074 FINDINGS — THIS FILE CANNOT BE MADE CLEAN IN ONE EDIT… DO NOT PAY THIS DOWN TO
  MAKE YOUR CHANGE."*

  ⚑ **`hook_pycheck` stages the WHOLE post-edit file** — ruff via `--stdin-filename`, mypy on the
  temp path — **it is not diff-scoped.** *So a one-line rewire inherits the file's entire existing
  finding population.* **The property that makes the gate honest is the property that makes this
  task unlandable**, and stating it that way is what turns a refusal into a plan.

* ⚑⚑ **SO THE UNIT IS NOT "REWIRE A CONSUMER" BUT "DRAIN A CONSUMER"** — the gate's own words:
  *"Extracting one concern is a step; draining the file is the finish."* **Ⓝ78‴: drain
  `scripts/query_topo.py` (80 findings, 3 defs) whole, and its rewire becomes a free consequence
  rather than a blocked prerequisite.** *The smallest consumer is the cheapest place to prove the
  route, exactly as `sorted_stream` was for `jea/`.*

  ⚑ **Read count unchanged at 323 — and it says why: the refusal is ATOMIC** (no write, then
  revert), confirmed by re-reading the line byte-identical. ⚑ It also re-reported the census's own
  bound: **7 dynamic-import shapes unresolved, so 323 is a FLOOR, not a total.** Live verified
  both times (31 relations); `schema.py` untouched.

  ⚑ *This is the fifth agent today to hand back a refusal with the next cut named, and the fifth
  time the refusal was worth more than the attempt would have been.* **A wrong rewire that still
  runs would have been the worst available outcome**, and only the verify-first instruction stood
  between the brief and it.

* ⚑⚑⚑ **Ⓝ122e⁹ ⟡the-stale-roster-declaration — THE FOSSIL WAS OVER-SERIALISING THE ENTIRE SELFTEST
  BUILD, AND NOBODY KNEW.** I filed it as *"a false fact two gates report."* **It was load-bearing in
  the GENERATED MAKEFILE:** `suite_claims.claim_for` gives a fan-out suite **`claim:roster`, which
  outranks `pg` and SERIALISES it against every pg-claiming suite.** *A stale declaration was
  costing the roster its parallelism.* **Non-leaf count 1 → 0**, verified by me: the
  `⚑ SELF-INCLUDING` block is gone and `worklist_gate` reads `[declared]` with no fan-out claim.

  ⚑ **THE ENTRY WAS KEPT, NOT DELETED** — *"assessed and found not to fan out" is a stronger
  statement than silence, and no walk derives it* — with the retired claim recorded verbatim beside
  the current truth. **Residue, not erasure.**

  ⚑⚑ **AND FIXING IT BROKE FOUR SELFTEST ARMS THAT USED THE STALE ENTRY AS THEIR LIVE EXEMPLAR.**
  *A case that goes red when a stale claim is REPAIRED is testing the data, not the reader* — so the
  table became injectable and the cases moved onto fixtures. ⚑⚑⚑ **One arm in `suite_modes_selftest`
  was guarded `if including and …`, so it would have gone VACUOUS RATHER THAN RED** — *silently
  measuring nothing instead of failing loudly.* Now unconditional, plus an arm asserting the live
  table declares no fan-out.

  ⚑ **A SECOND STALE ENTRY, REPORTED NOT FIXED:** `scratch/fix_notinscope.py`'s `why=` says *"a
  56-case suite"*; it reports **57/57**. *Benign drift-by-growth, unlike the worklist_gate fossil
  which was an INVERTED FACT.* `sppf_db` and `check_mode_contracts` both hold.

* ⚑⚑⚑ **THREE OF MY FIGURES WERE WRONG, ALL QUOTED FROM STALE REPORTS RATHER THAN MEASURED.**
  `wg_order` carries **234**, not 382. `worklist_gate` carries **473 in 42 rules**, not 831.
  ⚑⚑ And **`module_importers` is 11/11 — the 34/34 I kept quoting is the SIBLING suite
  `module_importers_selftest`.** ***The sibling suites are the authorities***, and I had been
  conflating module with suite for several dispatches. *Every one of these was a number I carried
  forward instead of re-deriving.*

* ⚑⚑⚑ **Ⓝ122e¹¹ ⟡stub-the-ellipsis-leaks — NOTHING LANDED, CORRECTLY, AND TWO OF MY PREMISES WERE
  WRONG IN THE DIRECTION THAT WASTES WORK.** Four of five leak sources have **a BETTER CALL, and
  none warrants a stub**:

      re.findall        -> re.finditer, `.group(1)` is `str`        CLEAN
      sys.stdout.write  -> discard the return                       CLEAN
      __import__        -> importlib.import_module -> ModuleType    CLEAN
      Callable[..., X]  -> NOT STUBBABLE AT ALL
      getattr           -> NEITHER

  ⚑⚑ **`getattr` WITH A DEFAULT STILL LEAKS `Any | None` EVEN UNDER `isinstance` NARROWING** —
  measured, not assumed; *the remedy is a DECLARED ATTRIBUTE, i.e. not doing the dynamic lookup.*
  ⚑⚑⚑ **AND `Callable[..., X]` FIRES `explicit-any`, NOT `misc`: the `...` SPELLS `Any`, so no stub
  can reach it.** *I grouped it with the stub-remediable shapes; only a real parameter list fixes
  it.*

  ⚑ **THE STRUCTURAL REASON NO STDLIB STUB WAS RIGHT:** `stub_declines` shows the relief mechanism
  is scoped to third-party packages and local modules — **of 27 `.pyi` files, NOT ONE shadows a
  stdlib module.** *"Do not write a stub where a better call exists" held on four of five, and the
  fifth is not a stub problem at all.*

* ⚑⚑ **Ⓝ122e¹⁰ ⟡type-the-row — LANDED AS AN EXTRACTION, WITH A DELIBERATE CONVENTION DEVIATION THE
  CONSUMERS DECIDED.** The definition **cannot** be typed in place — established empirically, the
  gate refused and reverted at 357 findings **and gave the instruction directly**. `substrate/wg_row.py`
  (5/5) uses **`NamedTuple`, not `@dataclass(frozen=True, slots=True)`**, because ***`order()` calls
  `rows.sort()` WITH NO KEY — the bare tuple comparison IS the ranking policy***, and a frozen
  dataclass would compare as a dataclass and break tuple identity for the `_Rows(list)` subclass.
  **`PYI024` says the same from the other side.** ⚑ Wiring it in is owed: `Row`'s only importer is
  `worklist_gate`'s re-export, and binding lands when `wg_order.py` drains.

  ⚑ **AND THE CHECKER CAUGHT A CASE THAT COULD NEVER GO RED:** a first draft asserted
  `isinstance(row, tuple)`, and **mypy reported the failure branch UNREACHABLE** — *a `NamedTuple`
  is statically a tuple.* Replaced with positional unpacking, **the operation the identity exists
  for.**

* ⚑⚑ **Ⓝ122e⁸′ — NOT LANDED, AND THE REASON IS A HARD CONSTRAINT RATHER THAN AN OBSTACLE.**
  `_selftest` is **structurally bound to `sys.path.insert(0, wg_engine.LIBRARY)` plus dynamic
  `import items` / `import figures`**, the live bib and `paper.toml`. ***"No `sys.path` modification
  in new code" is the arc's whole point, so the extraction cannot carry its own dependencies*** —
  and extracting without moving the dispatch leaves the built-then-orphaned rung the gate warns of.
  ⚑ **My FBT003 hypothesis confirmed in mechanism** (23 in the file), *and verified independently:*
  `wg_row`'s fixtures went 5 → 0 by switching to keyword construction, **where the rule is RIGHT
  rather than merely satisfied** — that record's whole point is that positions carry meaning.

  ⚑⚑ **NEW TOOL, AND IT FOUND A DEFECT IN ITSELF: `scripts/pycheck_show.py --count`** (15/15). *The
  count was being taken in the turn; there was no mode for it.* **Its first version printed
  `0 finding(s)` for a file carrying hundreds** — run as a copy outside the tree, `_ROOT` resolved a
  venv that was not there, both checkers failed, and `census` counted no codes in a COULD-NOT-RUN
  report. ***A count mode that cannot distinguish CLEAN from UNRUN banks the zero as success.***
  Now refuses on the marker, **case-insensitively because the two writers differ in case**, with
  positive controls for both spellings.



* ⚑⚑⚑ **Ⓝ122e⁷ ⟡drain-wg-consumers — MY ARITHMETIC WAS WRONG, AND THE TOOL SAYS SO IN ONE LINE.**
  Verified by me: `drain_leverage --name wg_profile` → **`retires 0, contested 8`**, co-drains
  `bibstruct, figures, items, ratchet, wg_dispatch, wg_engine, wg_order`. ***A contested insert
  retires only when the LAST sharer drains*** — so **even a COMPLETED rewire here would have moved
  nothing.**

  ⚑⚑ **I SAID "THIS IS THE CASE WHERE A COUNTER SHOULD MOVE." That was not a sequencing error: I
  CONFLATED *MODULE DRAINABLE* WITH *INSERT RETIRABLE*.** "7 sites are ALL path reads" is true and
  **irrelevant** to whether the insert retires. *The reader had the number the whole time; I did not
  ask it before recommending.*

* ⚑⚑⚑ **AND THE BLOCK IS THE CALLER, NOT THE FILE'S OWN FINDINGS.** I wrote *"nothing but the file's
  own 168 findings stands in the way."* **The rewire is TWO TOKENS at `worklist_gate.py:133`, and it
  is refused at 831 findings.** ***This is the `reuse_catalog` block REFLECTED*** — that one blocked
  at the **callee** (untyped, unreachable), this one at the **consumer** (clean callee, dirty
  caller). **Three drains, three different walls, each further along the same path.**

  ⚑ **The stranding trap does not apply — but NOT for the reason I gave.** Verified 1 def / 1 call /
  1 ref, single importer: *not because the whole file moves, but because the consumer is EXTERNAL
  and blocked.* **My reason was wrong and my conclusion right, which is the harder kind to catch.**

* ⚑⚑ **FIVE MODULES, 56 CASES, ALL IMPORTABLE FROM A FOREIGN CWD** — `profile_join` (11/11, pure
  `(file,line)` join of pstats × tracemalloc, `Row.verdict` classifying the three shapes) ·
  `process_memory` (11/11) · `profile_report` (14/14, **returns lines, never prints**) ·
  `profile_run` (10/10, the effectful half) · `profile_order` (10/10, composition and **the only
  writer**, cache probes by injection). Suites 347 → **352**.

  ⚑ **THE REUSE-SEARCH CLEARED TWO CANDIDATES AND CAUGHT A REAL TYPING IMPROVEMENT.** `_rss` was
  1 def / 3 calls, all in-file; **`peak_mb` is a LEDGER COLUMN FOR FINISHED SUBPROCESSES — not the
  live self-measurement `resident()` provides**, so no duplicate. ⚑⚑ And **`pstats.Stats.stats` is
  UNTYPED IN TYPESHED**, forcing the adapter through `Any`; **`Profile.getstats()` types cleanly AND
  drops a dependency layer.** *A reuse-search that found no duplicate still improved the design.*

* ⚑ **THE INSTRUMENTS ARE FLAT AND NOW THE REASON IS ARITHMETIC RATHER THAN CIRCUMSTANCE:**
  `drain_leverage` 491 inserts unchanged · `import_effects` scripts 59 unchanged, **substrate
  406 → 416 modules with side effects still 69 — ten new files, zero added** · `adopter_import`
  unchanged. ⚑ `worklist_gate` and `wg_profile` were **never edited**, so the roster runs exactly as
  before — verified as the one non-leaf.

  ⚑⚑ **Ⓝ122e⁸ ⟡retire-worklist-gate — THE UNBLOCKING MOVE IS NOT ANOTHER LEAF.** Drain the remaining
  `wg_*` consumers, **then retire `worklist_gate` itself**: the eight shared inserts lose their last
  sharers and **the counter moves for all eight at once.** *Recorded in `substrate/profile_order.py`'s
  own docstring, not only here* — **the finding lives where the next reader will be.**

  ⚑ **AND A PROCESS NOTE THAT COST A DISPATCH:** the first attempt at this item died to a
  **server-side 529** after identifying the decomposition and before its first write, losing
  everything. *The re-dispatch was told to LAND INCREMENTALLY* — write each module as it finishes
  rather than batching. **A brief that assumes the agent survives to the end is a brief with an
  unstated dependency.**


* ⚑⚑⚑ **Ⓝ122e⁸ ⟡retire-worklist-gate — NOTHING LANDED, AND THE MOST VALUABLE FINDING IS THAT I
  INVENTED THE HAZARD I TOLD THE AGENT TO PROTECT.** I wrote *"`worklist_gate` is the one non-leaf
  suite that RUNS THE ROSTER — a split that silently stops running 352 suites is the worst outcome
  available."* **It does not run the roster and has not for some time.** Verified by me:
  `pycodemod --literal run_selftests scripts/worklist_gate.py` → **2 sites, BOTH non-invocations** —
  a docstring, and a string ARGUMENT at `:440`, which is
  `ratchet.check_cycle("run_selftests.py", "worklist_gate")`, **a ppid-walk guard that REFUSES
  re-entry.** *The fork-bomb back-edge was fixed by DELETING the edge, not by declaring it.*

  ⚑⚑⚑ **AND BOTH READERS THAT SAY OTHERWISE READ A TABLE, NOT THE CODE.**
  `run_selftests --declarations` and `selftest_mk` both consult `substrate/suite_declared.py:65`,
  whose entry states `runs_roster=True, "its suite invokes run_selftests"` — **describing behaviour
  the file no longer has.** ***A gate green on a declaration nobody re-derives***, in the roster
  governing 352 suites. **`census-green-is-a-fact-about-the-census` + `fresh-comments-are-hypotheses`,
  compounded** — and *my acceptance criterion, "verify the roster still runs afterward", was
  UNFALSIFIABLE AS POSED.* **Ⓝ122e⁹ ⟡the-stale-roster-declaration** — correcting it is cheap,
  independent, and load-bearing for every later reading of that table.

* ⚑⚑⚑ **Ⓝ122d⁷ ⟡drain-wg-cluster — FLAT AGAIN, BUT THE BLOCK MOVED, AND THAT IS THE RESULT.**
  `reuse_catalog` was blocked at the **CALLEE** — untyped, unreachable, so the rewire was illegal
  under type-the-callee. **Here the callee is DONE**: typed, clean, tested, side-effect-free,
  importable from a foreign cwd. ***The block is now DOWNSTREAM at the consumers, and it is a
  FILE-CLEANLINESS block rather than a typing one.*** **A different wall, further along** — and
  distinguishing the two is what makes a flat number informative rather than discouraging.

      drain_leverage    182 candidates / 491 inserts / 312 files   IDENTICAL
      import_effects    scripts 59 with side effect                 59
      adopter_import    scripts 96/130                              96/130
                        substrate 396/402                           400/406  (+4 new, all importable)

  ⚑ **The instruments measure the CONSUMERS, and every consumer is frozen** — `wg_dispatch` /
  `wg_order` / `wg_profile` still report `No module named 'wg_engine'` because their import line is
  unchanged. ***The insert total falls only when a consumer's `sys.path` line is DELETED, and that
  edit is precisely what the per-file gate refuses.***

* ⚑⚑⚑ **`wg_engine` IS NOT ONE MODULE, AND MY "DRAIN THE LEAF WHOLE" FRAMING WAS WRONG.**
  `attr_reads wg_engine.*` → **54 attribute reads, of which 46 are `ROOT`/`PROJECT`/`LIBRARY`** —
  plain path constants — **and only 8 reach `engine`/`run`/`_sandbox`/`scratch_size`.**
  ***Three of the four consumers never touch the subprocess boundary at all.*** **The module's NAME
  describes one sixth of its use.** ⚑ Splitting by responsibility also **kept the `S603` exemption
  off a pure path join** — moving it whole would have carried a subprocess exemption onto path
  arithmetic.

  ⚑⚑ **AND `ROOT` WAS A HAND-ROLLED DUPLICATE.** `wg_engine` computes its own root via
  `os.path.dirname(...abspath(__file__))`, but **`substrate.corpus.ROOT` is the established
  authority — 150 reads across 83 files.** *The reuse-search caught it BEFORE the module was
  written*, and `worklist_paths.ROOT` is now `corpus.ROOT` **by identity**, with an arm pinning
  **identity rather than equality — because the two agree today only by coincidence.**

  Landed: `substrate/worklist_paths.py` (10/10) · `worklist_engine.py` (**31/31**, verified by me).
  Suites → **347**.

* ⚑⚑ **ALL FOUR CONSUMERS FROZEN, EACH REWIRE ATTEMPTED AND REVERTED BY THE GATE:**

      wg_profile     7 sites (all paths)                   168 findings
      wg_dispatch   15 sites (all paths)                   269
      wg_order      12 sites (11 paths, 1 engine)          382
      worklist_gate 20 sites (paths + ALL 8 engine reads)  870

  ⚑ The gate's own message is the instruction that was followed: *"an edit that leaves it dirty is
  refused too, so staging a fix does not converge… DO NOT PAY THIS DOWN TO MAKE YOUR CHANGE. Extract
  the one concern you need into a NEW module… The monolith stays dirty; your fix lands."*
  ⚑ **`worklist_gate.py` still runs the roster** — `selftest_mk` reports it as the one non-leaf, and
  it was never modified. *The far end no import census can see, checked.*

  ⚑⚑ **AN HONEST READ OF THE INSTRUMENT ITSELF: `wg_engine` WAS NEVER IN `drain_leverage`'s
  RANKING** — that reader lists targets by CONSUMER COUNT, so *"do these names leave the ranking"*
  **had no yes/no to give.** *A question posed to a reader that cannot answer it, reported as such
  rather than answered anyway.* ⚑ What it does show: **`ratchet`'s co-drain list still names all
  four `wg_*` modules** — the real remaining coupling.

* ⚑ **Ⓝ122e⁷ ⟡drain-wg-consumers** — the cluster finishes only by full decomposition, cheapest
  first: **`wg_profile` (168) → `wg_dispatch` (269) → `wg_order` (382) → `worklist_gate` (870).**
  ⚑ `wg_profile` is the natural next target: **7 sites, all paths, and `substrate.worklist_paths` is
  already sitting there waiting for it** — *the typed callee exists, so the law is satisfied and only
  the file's own 168 findings stand in the way.*

* ⚑⚑⚑ **Ⓝ122d⁗ ⟡the-contested-clusters — THE THIRD-PARTY SPLIT COLLAPSES THEM, AND THE CAUSE IS IN
  THE INSTRUMENT.** `drain_leverage.candidates()` filters **only `sys.stdlib_module_names`**, so
  **installed third-party names sit in the candidate population and count as blockers.** *That is
  why `numpy`'s row reads as a 16-insert opportunity when it is structurally ZERO:* its 54 co-drains
  — `cupy, sympy, matplotlib, networkx, libcst, bpy, bmesh, mathutils, sqlalchemy, psycopg` — are
  **every one third-party**, and an insert held open by a third-party import **can never be retired
  by draining.**

  ⚑ **THE TWO INSTRUMENTS DISAGREE LEGITIMATELY AND `--reach-back` IS THE RIGHT ONE HERE:** it
  reports **43 unpackaged names actually blocking adopters, 71 of 532 modules blocked, 461 usable**
  — and the giant co-drain rosters are **largely absent from that 43.** *`drain_leverage`'s contested
  counts are inflated by names that are installed, importable, and were never path debt.*

  **Retirable, ranked by first-party leverage:**

      _agdatext   21 consumers   first cut {agda_lex, _agdatext} IN THAT ORDER — agda_lex is the leaf
      ratchet     20            finish the substrate.ratchet_* facade; co-drain {gate_census, gate_keys}
      wg_engine    4            {wg_engine, wg_order, wg_dispatch, wg_profile} — a CLOSED 4-CYCLE,
                                best retirement-to-blast-radius ratio, the one to actually finish
      SPPF/pg   6+8+4+4+3       blocked behind ⟡package-jea — THE CLUSTER GATING ITEM 1

  ⚑⚑ **`numpy` IS STRUCTURAL: RECORD IT AND REMOVE IT FROM THE PAYDOWN LIST.** *Its 16 "retires" are
  files whose ONLY candidate name is numpy — an insert that should not exist, whose removal is a
  one-line deletion rather than a drain.* **A cluster that cannot be retired is a complete answer,
  and keeping it on a list is the thing to stop doing.**

  ⚑ **Ⓝ122d⁶ ⟡drain-leverage-owes-a-kind-split** — `candidates()` must partition first-party
  (drainable) from third-party (never retirable), and split contested inserts by which kind holds
  them. *Today the two are indistinguishable in the `co-drain:` line.* **One mode on an existing
  reader, not a new tool.**

* ⚑⚑⚑ **Ⓝ122d‴ ⟡drain-reuse-catalog — THE NUMBERS DID NOT MOVE, AND THE CAUSE IS PRECISE ENOUGH
  THAT THE REFRAMING SURVIVES.** All three instruments flat: `drain_leverage` identical,
  `import_effects` identical, `adopter_import` **+4/+4 for the new modules only** — *the three
  `NameError` consumers did NOT become importable.*

  ⚑⚑ **RETIRING THOSE INSERTS IS GATED ON THE CALLEE, NOT THE CONSUMERS, AND `pyproject.toml:685-706`
  STATES IT AS GOVERNING LAW** (measured by paperkit): ***"THE ORDER IS TYPE-THE-CALLEE, THEN
  NAME-IT… Converting a site whose callee is untyped converts a silent hole into a BLOCKED EDIT —
  strictly worse than leaving it."*** The rewire was attempted, `hook_pycheck` **refused and
  reverted** it on two blockers — `PLC0415` (no function-level imports, so the callee must be named
  at top level) and **mypy following imports regardless of `files = ["substrate"]`**, charging the
  CONSUMER with `Expression has type "Any"`.

  ⚑ **SO THE TWO CLEAN MODULES LANDED ARE EXACTLY THE TYPED LEAVES THE MIGRATION REQUIRES** —
  `substrate/catalog_targets.py` (13/13, pure) and `catalog_drive.py` (17/17, injection-only).
  *The drain stopped where the gate said to stop rather than forcing it.* Suites → 345.

* ⚑⚑⚑ **AND `generate` WAS NEVER FUNCTIONAL — "fix the live defects" UNDERSTATED IT.** It calls
  `_db_tier_unported(...)` **unconditionally before the render loop**, raising `SystemExit`, and
  `ruff --select F821` finds **17 undefined names** in that file — **16 uses of `con`, bound
  nowhere.** *The tool has been wholly non-functional, not merely path-fragile.* ⚑ And the
  `NameError` is **not in the three consumers** — all three spell `import os, sys` correctly; the
  defect is `scripts/reuse_catalog.py:58`, a bare `sys.path.insert` where only `sys as _sys` is
  bound. ***The error is REPORTED AT THE IMPORTER and LIVES IN THE IMPORTED*** — the same
  displacement a path mutation makes, one layer up.

* ⚑⚑⚑ **Ⓝ122d″ ⟡the-sanctioned-shadowing — THE OPERATOR REFRAMED THE WHOLE DRAIN ARC, AND MY
  RANKING WAS WRONG.** *"we must stop fucking around with `sys.path`. Drain things into proper
  packages so that package-based lookup works."* ⚑⚑ **That makes the drains THE MECHANISM, not three
  independent cleanups**: all 59 mutating modules live in bare directories reachable only by path
  surgery, so **draining a module into `substrate/` is what lets its consumers stop needing the
  insert.**

  ⚑⚑⚑ **AND THE RIGHT METRIC OVERTURNS BOTH ORDERINGS I HAD. ALL THREE OF MY CANDIDATES RETIRE
  ZERO INSERTS**, verified by me:

      sppf_decode   366 findings   retires 0   contested 2
      split_census  424            retires 0   contested 7
      rank4_shred   428            NOT A CANDIDATE — holds no bare import under an insert

  *The finding-count order did not mis-sequence; it selected three targets that accomplish nothing
  under the reframing.* ⚑ **And `--reach-back`'s consumer-count order fails identically at the
  top:** `_agdatext` (21 consumers, rank 1) **retires 0** — `check_ban_ratchet.py:43,50` has two
  inserts serving three names, and `ratchet` and `agda_lex` each hold one open.

* ⚑⚑⚑ **`reuse_catalog` IS THE ONLY CLEAN WIN ON THE BOARD — retires 3, contested 0, consumers 3.**
  The **sole high row with an empty co-drain**: draining it retires every insert it touches with no
  coordination. Both instruments agree independently — `module_importers` reports 3 bare sites, 0
  dotted, in `gen_catalog` / `gen_reuse_graph` / `gen_reuse_index`, **each binding exactly one name**
  — *and those same three are the modules `adopter_import` reports failing with `NameError: name
  'sys' is not defined`.* **Live defects, not merely drain debt.**

  ⚑⚑ **EVERYTHING RANKED ABOVE IT IS COUPLED, AND THAT IS THE SHAPE THE REFRAMING EXPOSES.**
  `numpy` retires 16 with **64 contested across 54 co-drains**; `edit_snapshot` retires 15 with 54
  contested; `agda_lex` retires 4 with 59. ***Almost every insert is held open by MULTIPLE names, so
  most drains SHORTEN a dependency without RETIRING it*** — and **`retired` and `contested` are
  deliberately NEVER SUMMED**, which is what keeps that visible instead of averaging it into a
  score.

* ⚑⚑⚑ **THE INSTRUMENT OVERTURNED ITSELF MID-BUILD, AND IT WOULD OTHERWISE HAVE CONFIRMED MY WRONG
  ORDER BY ACCIDENT.** Its first cut resolved insert targets **from string literals only** — but the
  dominant `scripts/` idiom, `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`,
  **has no literal at all.** It reported **291 of 491 inserts unattributable and EVERY candidate
  retiring zero.** ***A ranking that was a fact about the METHOD, presented as a ranking of the
  SUBSTRATE*** — *and its output at that moment agreed with my finding-count order, so a less
  careful pass would have banked the agreement as corroboration.* Fixed by resolving
  `__file__`-relative inserts from the label (counting `dirname` depth, so a doubled walk is the
  parent); **blind spot 291 → 156, and only then did the ranking discriminate.** Both arms pinned as
  cases.

  ⚑ **THE RESIDUAL 156 REMAIN A REAL BOUNDARY** — *a zero in this ranking is still not yet an
  absence*, and the reader says so in its own footer.

* ⚑ **STEP 2 DELIBERATELY NOT STARTED.** The measurement consumed the budget, including two
  refuse-and-revert cycles and the instrument repair. **Starting a drain without room to verify at
  the far end would have risked the exact failure recorded three times this session** — a 16-gate
  roster broken by verifying the edited module and never its importers.

  ⚑ `adopter_import` before/after: **blocking 71 of 526 → 71 of 528**, usable 455 → 457 —
  *denominator +2, usable +2, blocked flat, which is CORRECT for two clean modules and no drain.*
  ⚑ `import_effects`: `substrate:` **327/396 → 329/398 inert**, both new modules absent from the
  effects list. **The instruments measuring the `sys.path` surface do not themselves mutate it.**
  ⚑ `selftest_mk` was **STALE after the new suite and correctly said so** — regenerated to 343.

  **Ⓝ122d‴ ⟡drain-reuse-catalog** — 3 bare sites, one bound name each, no co-drain, and its three
  consumers currently raise `NameError` under the adopter probe. ⚑ *Note `store`, `jea_agdai`,
  `query_builders` and `_content_addr` still reach into `scratch/` from `reuse_catalog` itself.*

* ⚑⚑⚑ **Ⓝ122d′ ⟡find-the-real-corruption — REPRODUCED. THE FIRST AGENT HAD THE CLASS RIGHT AND THE
  VECTOR WRONG, AND THE SECOND WAS RIGHT ONLY ABOUT THE HALF IT TESTED.** The literal claim is false
  — under a non-editable wheel install probed from an empty foreign cwd, **nothing was written and
  nothing shadowed via the filesystem.** ⚑⚑ **But the shadowing half is REAL and previously
  unmeasured: 59 of 130 `scripts` modules MUTATE `sys.path` AT IMPORT TIME.** All five hooks prepend
  the repo root; **`check_mypy_ratchet` prepends `scratch/` ELEVEN times, `set1_ratchet_cores`
  FIFTEEN.** Plus 26 of 396 `substrate` modules prepending a `paperkit` site-packages dir, and
  **three writing files at import** (`iface_construct`, `iface_readers`, `stub_top_type`).

  ⚑⚑⚑ **AND THE MECHANISM EXPLAINS WHY IT WAS UNATTRIBUTABLE: A `sys.path` MUTATION CORRUPTS EVERY
  *LATER* IMPORT IN THE PROCESS, NOT THE ONE THAT DID IT.** *Invisible to an exception-typed probe,
  and it produces a corrupted result with no culprit at the site of the corruption.* **That is why
  the first agent saw a real effect and reached for a filesystem write** — the only vector that
  would have been locally visible.

  ⚑ **THE REPO'S OWN GATE MANDATES IT.** `check_hook_set` passes with *"every sibling-importing hook
  repairs `sys.path`."* ***The sanctioned repair for one problem is the shadowing mechanism for
  another*** — and Ⓝ114″ established the counterpart: those hooks are vendored into five repos where
  removing the insert ships a SILENT-ALLOW. **Both directions are now measured, and they conflict.**

  ⚑ **NEW INSTRUMENT: `substrate/import_effects.py` (8/8), FOUR AXES MEASURED SEPARATELY** — write /
  spawn / `sys.path` / `sys.modules` — via `sys.addaudithook`, per-module subprocess, bytecode
  writing off. **Its cases include an INERT control, a discrimination check, an UNMEASURED-≠-INERT
  check and a read-is-not-a-write check** — *the set that makes the census trustworthy rather than
  merely green.* ⚑⚑ **Its own first cut was defective in this session's recurring shape: without a
  stdlib filter it reported 363 of 396 modules leaving names in `sys.modules`, burying the real
  finding under ordinary transitive imports.** Fixed to `sys.stdlib_module_names`; **signal 363 →
  69.** *A census whose noise floor swallowed its signal.*

  ⚑ **WHAT REMAINS UNPROVEN, STATED AS SUCH:** *this* mechanism cannot be shown to have caused *that*
  probe corruption — **the original observation was not recorded in enough detail to replay.** What
  it does is **remove the need to posit an unknown cause.**

* ⚑⚑⚑ **Ⓝ96″ ⟡stub-edit-snapshot — STUB LANDED, BOTH GATES GREEN FROM BOTH DIRECTIONS, GUARD STILL
  CANNOT ARM.** `check_stub_authority` **10 → clean (11 of 11)** with `edit_snapshot` listed and its
  declines printed; `stub_reexport` **26 → clean (27 of 27)**, verified by me. ⚑ *That second is the
  half stubtest structurally cannot cover* — **and after eleven false re-exports were found across
  two stubs earlier today, it earning its keep on a NEW stub is the point.**

  ⚑⚑ **BOTH JUDGEMENT CALLS IN THE STUB ARE REFUSALS TO NORMALISE:**
  `guard(...) -> str | None`, because the source documents returning `None` rather than raising
  outside a git worktree — ***declaring `str` would erase that IN THE DIRECTION THAT READS AS
  SAFE***; and `MutationContractError(BaseException)` **kept on `BaseException`**, because the
  source records that base chosen **against a census of 31 `except Exception` sites that wrap a
  `guard()` call and write anyway** — *normalising it would assert a containment relation the
  runtime does not have, at 31 sites, silently.*

  ⚑ **THE GUARD DID NOT ARM AND THE GATE IS RIGHT.** `scratch/split_census.py` carries **424
  pre-existing findings**; the one-Write insert at `:768` was refused and reverted. Its refusal text
  forbids both escapes — *pay it down*, or *extract-and-strand*, since **`run_census` is the only
  consumer of that write.** ***The unit is draining the file*** — the
  per-file-gate-is-a-design-signal shape, where routing around it is the forbidden move.
  **Ⓝ96‴ ⟡drain-split-census.**

* ⚑⚑⚑ **Ⓝ122e ⟡fix-the-bare-spellings — ZERO CONVERSIONS REACHABLE, AND MY COUNTS WERE
  UNDERCOUNTS.** `adopter_import` for `scripts:` **96 of 130 before and after** — *by my own
  acceptance criterion nothing worked, and that IS the finding.* **Every candidate consumer is
  frozen**: `type_sppf` 639+, `rank4_shred` 428+, `sppf_label` 685+, `check_carrier_locality` 1072+,
  `check_mode_contracts` 946+, `wg_dispatch` 1619+. Corroborated at population scale —
  `pycodemod --types scripts/` reports **339 keys across 19 error codes**, *the mypy half alone
  freezing most of the tree.* **`rank4_shred` (428) is the cheapest entry point.**

  ⚑⚑ **AND THE BLOCKING COUNTS ARE LARGER THAN I STATED, FOR A REASON WORTH KEEPING.** I cited
  `_agdatext` 14 / `ratchet` 6. `adopter_import --reach-back` reports **`_agdatext` 21, `ratchet`
  20, `agda_lex` 14** across **43 unpackaged names blocking 71 of 522 modules.** ***The 14/6 are
  each module's FIRST import failure*** — **a module blocked on `_agdatext` never reaches its
  `ratchet` line** — *so a naive count undercounts every name after the first.* **`ratchet` is more
  than 3× the stated size and is the SECOND-largest cause, not a minor one.**

  ⚑⚑ **THE STUB-KEYING HAZARD I FLAGGED DOES NOT BIND EITHER TARGET.** `stubs/` holds `.pyi` for
  `agda_lex`, `check_carrier_locality`, `check_scratch_independence`, `gen_build_makefiles`,
  `tsdbprobe` — **not `_agdatext`, not `ratchet`.** *So a bare→dotted conversion of these two could
  not have bypassed a stub.* **The collision (Ⓝ122c) is real and scoped to a DIFFERENT consumer
  set**, and `check_stub_authority` 10/10 + `stub_reexport` 26/26 confirmed nothing was disturbed.

* ⚑⚑⚑ **A LIVE TOOLING GAP: `module_importers.py` CANNOT ANSWER THIS QUESTION, DESPITE BEING THE
  SUCCESSOR `--importers` NAMES ON REFUSAL.** It **NORMALIZES bare names to dotted** (*"the bare name
  '_agdatext' resolved to 'scripts._agdatext'"*) and then reports only the **already-dotted** sites —
  **0 for `_agdatext`, 2 for `ratchet`.** ***It collapses precisely the bare-vs-dotted axis this item
  turns on, so its zero is a fact about the READER.*** Only `adopter_import --reach-back` sees both
  axes. **Ⓝ122g ⟡importers-collapses-the-axis** — *a retired reader's successor inheriting a
  different blind spot is the shape this repo records as `census-keyed-on-one-spelling`, one
  generation on.*

  ⚑ `selftest_mk --apply` → **340 suites**; `check_stub_authority` 10/10; `stub_reexport` 26/26;
  `row_upsert` 8/8; suites 19/50/23/52/31; hooks fire-probed from `/tmp` with real refusals, each
  naming its successor. ⚑ **The MCP "auto mode" injection appeared a THIRD time** and was ignored;
  *the hooks refused those shapes independently, twice.*

* ⚑⚑⚑ **Ⓝ129 ⟡inp001-is-a-location — THE PREMISE WAS FALSE ALL SESSION, AND THE CONCLUSION SURVIVES
  ITS DEATH.** `INP001` has been recorded throughout as *"a pure LOCATION property that no edit to
  the file's contents can clear"*, and **every supersession in this arc was justified by it.** The
  finding's own message names the fix — *"Add an `__init__.py`"* — and `jea/` plus
  `jea/metalanguage/` are **both bare directories.** ⚑ **Measured: with the markers,
  `schema_rows.py` goes 154 → 153 ruff findings. `INP001` is ONE of 154.**

  ⚑⚑ **SO THE STRATEGY WAS RIGHT FOR A DIFFERENT REASON THAN THE ONE WRITTEN DOWN:** not *"the
  location cannot be changed"* but ***"`INP001` is 0.6% of the debt, and the file is unsalvageable
  under a per-file gate regardless of where it sits."*** **The wall was never the location.**

  ⚑⚑⚑ **AND THAT CHANGES SCOPING, NOT JUST THE RECORD. A location wall is BINARY AND UNFIXABLE; a
  154-finding debt is RANKABLE** — it says which files might actually be drainable. **The strategy
  must be re-derived PER FILE from its finding count, never applied uniformly from a false
  universal.** *A false premise that produced correct behaviour is the hardest kind to catch,
  because nothing it decided ever looked wrong.*

* ⚑⚑⚑ **THE LOAD-BEARING ANSWER IS NO, AND THE SUBSTRATE HAD ALREADY RECORDED WHY — ONE READ AWAY.**
  `substrate/tenant_choice.py:47-52`: *"IT IMPORTS NOTHING FROM `jea/`, AND THAT IS LOAD-BEARING
  RATHER THAN TIDY. A module extracted out of that package but still NAMING it inherits the untyped
  hub through the import and cannot be made clean — **measured on the sibling extractions, which
  succeeded precisely because they reached back for nothing.**"*

  ⚑⚑ ***Packaging changes the SPELLING of a dependency, never its TYPE SURFACE.*** `__init__.py`
  adds no annotations, and `substrate/` would inherit `no-untyped-call`/`attr-defined` from the hub
  whether the import reads `import store` or `from jea.metalanguage import store`. **So packaging is
  ORTHOGONAL to the drain, not a prerequisite for it** — `substrate/` could import a packaged `jea/`
  only once the imported modules are themselves clean, *which IS the drain, and packaging
  contributes nothing to it.*

* ⚑⚑ **NOT LANDED, AND THE REASON IS A HAZARD THE FIX WOULD CREATE.** The marker is runtime-inert
  TODAY — a throwaway-copy probe ran `query_defs --selftest` **19/19** inside the marked package,
  with bare names still resolving because *the `sys.path` insert puts the DIRECTORY on the path and
  `__init__.py` only ADDS the dotted route.* ⚑⚑ **But it would put `jea.metalanguage.store` and bare
  `store` on the path as TWO DISTINCT MODULE OBJECTS the moment any consumer adopts the dotted
  spelling — duplicate class identities and duplicate module state, on a 43-CONSUMER module.**
  *It purchases one lint finding and no packaging benefit while creating a dual-spelling hazard.*

  ⚑ **And the dotted conversion is not two files: `pycodemod --imports jea/metalanguage` reports 35
  FIRST-PARTY bare-name modules** of 80 imports — `store` (43 files), `jea_pyalg` (32),
  `schema_decl` (20). *A ~100-site rewrite, not a `touch`.*

* ⚑⚑ **THE TWO-READER CROSS-CHECK EARNED ITS KEEP AGAIN, AND BOTH READERS NAMED THE SAME BLIND
  SPOT.** On `schema_rows`: `module_importers` → **0 sites in 0 of 1270 files**; `attr_reads` →
  **8 attribute reads in `scripts/ddl_lifecycle.py`.** ⚑ Both flag the cause — **`schema.py:85`
  re-exports `schema_rows` with a star, so consumers reach it under `schema`'s name and NAME IT
  NOWHERE** — *and both say so rather than reporting a bare zero.* **That hidden remainder must be
  enumerated before Ⓝ119‴'s supersession is scoped.**

* ⚑ **Ⓝ122e IS CONFIRMED INDEPENDENT, AND THE EVIDENCE IS DIRECT.** `_agdatext` and `ratchet` live
  in `scripts/`, **which IS in the `packages` list**, and `adopter_import` still reports
  `No module named '_agdatext'` **for 14 modules** and `'ratchet'` for 6, among 31
  `ModuleNotFoundError`s at `scripts: 96 of 130`. ***Being packaged did not fix the bare
  spellings*** — **packaging and bare-name resolution are separate axes**, which is also the second
  confirmation that markers on `jea/` would have fixed nothing there.

  ⚑ **Ⓝ119‴ IS NOT BLOCKED ON PACKAGING EITHER** — `jea/metalanguage/` is editable today; **the
  per-file gate is what blocks it**, since any edit must land the whole file clean against 154 ruff
  + 5 mypy error codes. *Supersede the consumers — and record the reason as the 153 RESIDUAL
  findings, not the location.*

* ⚑⚑⚑ **Ⓝ130 ⟡the-build-lib-shadow — DONE BY HAND, AND IT TOOK Ⓝ121 WITH IT.** `build/` was an
  untracked setuptools artifact holding a stale copy of `scripts/` and `substrate/`. **It flooded
  `selftest_mk`'s roster with ~200 phantom `build__lib__*` entries that HID ~22 REAL ones** — every
  suite built this session, buried in noise. Deleted; regenerated: **338 suites, `--check` GREEN.**
  *The signal was there the whole time and unreadable.* ⚑ **Ⓝ122f: `pyproject.toml`/`uv.lock` were
  NOT gitignored — just never added.** Staged.

* ⚑⚑⚑ **Ⓝ122 ⟡substrate-must-be-importable — THE OPERATOR'S CHOSEN SHAPE IS BLOCKED BY A
  DEPENDENCY NOBODY HAD CHECKED.** `substrate-tooling` declares a **HARD dependency on `paperkit`,
  which is not on PyPI** — it is a local sibling repo. `uv pip install /home/mikemol/github/substrate`
  **fails outright**: *"paperkit was not found in the package registry."* ⚑ **No adopter can install
  substrate today, regardless of packaging or `py.typed`** — and no prior measurement caught it,
  because every earlier probe installed into a venv where the sibling was reachable.
  **Ⓝ122b ⟡the-paperkit-dependency** — vendor, publish, or make optional; an operator decision.

* ⚑⚑⚑ **MY "EVERY FAILURE IS ONE CAUSE (scratch)" CLAIM WAS WRONG, AND WRONG IN THE DIRECTION THAT
  MATTERS.** Verified: **442 of 512 packaged modules usable by an adopter today**, 70 blocked by 42
  unpackaged names. **The two largest blockers live in `scripts/`, WHICH IS PACKAGED:**

      _agdatext   21 consumers  |  ratchet  20 consumers      <- scripts/, packaged
      agda_lex    14            |  schema    8 · store  6      <- scratch/ and jea/metalanguage/

  **`_agdatext` and `ratchet` are BARE-SPELLING DEFECTS, fixable today — not drain debt.** *The
  census I framed as a paydown queue for `scratch/` is mostly a queue of modules importing PACKAGED
  SIBLINGS BY THE WRONG NAME.* ⚑ And a third category I never named: `schema`/`store` in
  `jea/metalanguage/`, **neither packaged nor `scratch/`.**

  ⚑⚑ **AND THE AGENT DELIBERATELY DID NOT APPLY THE FILTER I ASKED FOR.** I said group by the
  `scratch/` module depended upon. It kept every unpackaged name instead, **because filtering to
  `scratch/` would have HIDDEN the `gen_build_makefiles` defect by classifying it as drain debt.**
  *My filter would have concealed the finding it was meant to surface.*

* ⚑⚑⚑ **A GENUINE CONFLICT, NOT AN OVERSIGHT: A TYPING DECISION THAT BREAKS UNDER INSTALLATION.**
  `substrate/agda_import_dag.py` argues for the BARE spelling **on purpose** — `stubs/gen_build_makefiles.pyi`
  is keyed on the module NAME, so the honest `from scripts.` spelling **would bypass the stub**.
  ⚑ *So the two requirements are in direct tension: name-keyed stubs want the bare spelling;
  installation wants the packaged one.* **Ⓝ122c ⟡stub-keying-vs-package-path** — this is the one
  blocker that is not a defect to fix but a design collision to resolve.

* ⚑⚑ **AND THE 544 `path.insert` SITES ARE NOT IN THE CLEAN POPULATION.** `pycodemod --calls
  path.insert substrate/` → **ONE site** (`promoted_selftest.py:47`). *`substrate/` is already clean
  of path surgery*, so the conversion step I briefed was near-empty work. **The 544 live in the
  UNDRAINED trees, which is consistent — but I had implied `substrate/` was among them.**

* ⚑⚑⚑ **AN ADOPTER IMPORTING ONE MODULE GETS FILES WRITTEN INTO THEIR WORKING DIRECTORY.** A probed
  module **writes `scripts/hook_shellcheck.py` into the adopter's CWD at import time** (a selftest
  fixture resolving via `corpus.resolve_root`, documented *"CWD FIRST"*) — **and it then SHADOWS the
  installed `scripts` package**, corrupting one probe result before the agent noticed. *An import
  with a filesystem side effect that also hijacks package resolution.* **Ⓝ122d ⟡import-writes-to-cwd**
  — filed, not repaired; out of that dispatch's scope and the most dangerous row in it.

* ⚑⚑ **STALENESS: NO NEW STAMP WAS NEEDED, AND THE REASON IS A MEASUREMENT.** The packaging tooling
  **already writes both halves** — `RECORD` holds a sha256 per installed file, `direct_url.json`
  records the source tree. ⚑ *Measured while building: three reinstalls of genuinely DIFFERENT trees
  all reported the SAME VERSION*, so a hand-maintained stamp would be **a promise to remember whose
  failure mode is READS FRESH WHILE STALE.** `substrate/install_freshness.py` passes both controls:
  content change → `STALE` naming the file, exit 1; `touch` (mtime only) → `FRESH`, no false alarm.
  ⚑ **`UNVERIFIABLE` is a separate verdict, never a degraded `FRESH`** — the three-valued discipline
  again, reached independently for a fourth time today.

  ⚑ `py.typed` landed for both packages as `[tool.setuptools.package-data]` (**not automatic — it is
  not a `.py` file**), ladder re-verified end to end. `substrate/adopter_import.py` is a RUNTIME
  probe **because every other import reader here is STATIC and none could see this**. Hooks
  untouched, `check_hook_set` un-inverted and green, all five suites matching from a foreign cwd,
  `tests/` 68/68. **The operator's `.venv` was not touched** — all measurement in a throwaway.


* ⚑⚑⚑ **Ⓝ122b ⟡the-paperkit-dependency — RESOLVED, AND THE INSTALL NOW WORKS WITH NO ORDERING
  INSTRUCTION.** `pyproject.toml` carries a PEP 508 direct reference —
  `paperkit @ git+https://github.com/mikemol/paperkit.git@main` — **read from
  `git -C ~/github/paperkit remote -v`, not guessed**, branch confirmed by `ls-remote` at a commit
  identical to local HEAD. ⚑ Verified by me: the gate reports **17 INDEXED · 1 DIRECT**, and
  `uv pip install` into a clean venv **with no paperkit pre-installed and no ordering instruction**
  succeeds, auto-fetching from git. **The client folklore is now encoded where the resolver can act
  on it.**

  ⚑⚑ **AND THE SPELLING WAS DECIDED ON EVIDENCE, NOT PREFERENCE.** `[tool.uv.sources]` is **uv's own
  extension**: read when uv resolves THIS project and **DROPPED from the metadata of any wheel built
  from it.** Since adopters install this tree AS A DISTRIBUTION (which is what `install_freshness`
  reads `direct_url.json` to verify), *the requirement must survive into `Requires-Dist` or the
  adopter inherits the exact bare-name failure.* A direct reference is honored by pip and uv alike,
  and carries no local path. ⚑ **Cost stated rather than hidden: resolving it needs a git fetch** —
  a real property of depending on an unpublished distribution, not a defect of the spelling.

* ⚑⚑⚑ **THE PREDICTED BLOCKED POPULATION WAS WRONG — MINE AND THE PRIOR AGENT'S BOTH.** We expected
  the five paperkit modules to be the blocked set. **Measured: `adopter_import` from a foreign cwd
  reports 377 of 383, and the five paperkit modules IMPORT CLEANLY.** The six blocked are a
  different population entirely — **five reaching un-promoted `scratch/` names** (`gen_build_makefiles`
  ×4, `agda_lex` ×1) **and one deliberate `SystemExit` fixture.** ⚑ And the two dynamic-import sites
  I flagged as possibly reaching paperkit **do not**: `gate_module:68` imports gate stems,
  `ratchet_suites:286` imports `substrate.*` suites. *The population really is 5 — the floor was the
  total, this time.*

* ⚑⚑⚑ **`paperkit` WAS IN NO ENTRY OF `uv.lock` — 109 PACKAGES, AND A DECLARED HARD DEPENDENCY SINCE
  2026-08-31 WAS NOT AMONG THEM.** *The gap was observable in the lockfile the whole time and nothing
  read it.* ⚑ **That is the gate's real justification: not that someone erred, but that a manifest and
  its lockfile DISAGREED FOR DAYS with no reader.**

* ⚑⚑ **AND `pyproject.toml` AND `uv.lock` ARE UNTRACKED BY GIT.** So **an adopter cloning this repo
  gets NO MANIFEST AT ALL**, and the dependency fix reaches nobody until they are committed. *Not
  caused by this work, flagged rather than acted on.* **Ⓝ122f ⟡the-manifest-is-untracked** — and it
  is the same shape as Ⓝ95 (`selftest_mk.py` untracked yet wired as a blocking gate) and Ⓝ71i
  (`suite_runner`'s whole life postdating HEAD): **the tree's own record does not hold the thing the
  tree depends on.**

* ⚑ **NEW GATE — Ⓝ123 ⟡dep-addressing, BUILT AND PROVEN ABLE TO FAIL.**
  `substrate/dep_addressing.py` (18/18) classifies each requirement **by FORM** — INDEXED / DIRECT /
  UNADDRESSED / LOCAL — and **never touches the network**, *because attempting resolution would fail
  offline and report a machine fact as a repo fact* (the collapse recorded four times today).
  ⚑ **Baseline is EMPTY BY CONSTRUCTION — no baseline file, a bijection rather than a ratchet** — and
  relief is an `UNPUBLISHED` roster listing the known-unpublished, *so every entry makes the gate
  STRICTER and it cannot go green by accretion.*

  ⚑ **Fire-probed against a temp copy with the defect reintroduced:** *"BROKEN — 1 of 18 resolve from
  neither an index nor a git URL ✗ paperkit — UNADDRESSED: paperkit is published on no index, so a
  bare name resolves nowhere"*, with the successor spelling and explicit warnings against
  `[tool.uv.sources]` and `file://`. **Not wired into pre-commit** — the operator's call.

  ⚑ Suites all at expected counts from a foreign cwd (19/50/23/52/31); `warrant_bib_selftest` 11/11
  and `engine_grades_selftest` 11/11 in the throwaway. **The operator's `.venv` was never written
  to**, and the hooks refused the agent live 6× during the work — *including a `pycheck`
  refuse-and-revert on an edit that had already written into `substrate/`.*

* ⚑⚑⚑ **Ⓝ114 ⟡strip-the-file-derivation — THE OPERATOR WAS RIGHT AND THE AGENT OVERTURNED ITS OWN
  IMPOSSIBILITY CLAIM.** It reported *"installing does not dissolve the mypy failure — the
  MetaPathFinder editable install is invisible to mypy BY CONSTRUCTION."* **The first half is
  correct and well-measured; the second does not follow.** *A fact about the EDITABLE install
  generalized into a fact about the MECHANISM* — the shape recorded five times today, arriving in
  a form that would have abandoned a working fix on a false wall. **Operator: *"It does if
  substrate gets installed into the .venv, too."***

  ⚑⚑ **AND THE PROOF IS THE ERROR CHANGING KIND, NOT THE ERROR GOING AWAY:**

      editable (current .venv)        Cannot find implementation   [import-not-found]
      regular install, no marker      module is INSTALLED, but missing py.typed  [import-untyped]
      regular install + py.typed      clean

  ***`not-found` → `installed-but-untyped` is the discriminator*** — it proves mypy's ORDINARY PATH
  SEARCH finds the package. `site-packages` holds real `scripts/` and `substrate/` directories;
  nothing needs `.pth` execution or `sys.meta_path`. **The editable install's invisibility is real
  and is a property of EDITABLE, not of INSTALLED.**

* ⚑⚑⚑ **RESOLUTION TODAY IS POSITIONAL, AND THAT IS WHY THE BUG HIDES INSIDE SUBSTRATE.** The
  peer's failure **does not reproduce here**, and `mypy -v` says why: `base_dir` is computed by
  **walking up past `scripts/__init__.py` to the repo root, which HAPPENS TO CONTAIN
  `substrate/`.** *Resolution works for the same reason the `sys.path` insert works — position.*
  ⚑ Reproduced verbatim by **building an adopter-shaped tree**: the vendored hook reports
  `import-not-found` at `:765`; the same file under regular install + `py.typed` from the same
  foreign cwd is **clean**.

  ⚑⚑ **AND THE DECISIVE OBSERVATION: THE ADOPTER COPY EXECUTED CORRECTLY — refusing `[ $x = y ]`
  with SC2154 — WHILE ITS `sys.path` INSERT POINTED AT A ROOT WITH NO `substrate/`.** *The install
  did the work; the derivation contributed nothing.* **The mechanism the comment block defends at
  length was already inert in the case it was written for.**

* ⚑⚑ **IT STOPPED BEFORE EDITING, FOR A REASON I HAD NOT ANTICIPATED: `check_hook_set.py` ASSERTS
  THE MECHANISM BEING REMOVED.** Its arm 2 reports *"every sibling-importing hook repairs
  `sys.path`."* **Stripping the derivation turns that gate RED, so the gate must be INVERTED — to
  assert that NO hook derives a root — in the SAME change**, not exempted, not fixed afterward.
  *A gate that encodes the defect as the requirement.*

  ⚑ **THE COST, STATED PLAINLY AND LEFT TO THE OPERATOR:** a regular install **SNAPSHOTS** the code
  — working-tree edits do not reach `site-packages` until reinstall — *in a repo whose hooks gate
  every write and are edited constantly.* **That loss is exactly what buys the static resolution.**
  Two things absent today: the non-editable install, and **`py.typed` declared as PACKAGE DATA** for
  `substrate` and `scripts`.

* ⚑ **THREE CORRECTIONS TO MY BRIEF.** **SIX files carry the derivation, not five** —
  `hook_shellcheck:77`, `hook_no_chaining:80`, `hook_structural_query:75`, `hook_pycheck:165`,
  **`pycheck_analyze:54` (a non-hook sixth with the identical body)** — and **`hook_cmdparse` does
  not have it at all**, though I listed it. ⚑ And I mis-attributed **52/52 to `pycheck`, which is
  31/31**; 52 is `structural_query`'s. *Baselines captured before any edit: 19/19, 50/50, 23/23,
  52/52, 31/31.*

  ⚑⚑ **`--manifest` CARRIES AN INACCURATE ADOPTION CLAIM:** it calls `hook_shellcheck.py`
  *"standalone — no sibling required"* while the file imports `substrate.ratchet_flags` at `:765`.
  **The manifest is blind to cross-PACKAGE imports and tracks only `scripts/` siblings.** ⚑ Under
  installation this stops mattering — **the dependency graph becomes the manifest**, which is
  ⟡install-dont-vendor's whole point — but today the claim is false. `scripts/HOOKS.tsv` was **not
  created**: under installation it is unnecessary, *which is a finding, not a file.*

* ⚑ **AN INCIDENTAL FINDING THAT IS `project_root`'s OWN DOCUMENTED DEFECT FIRING LIVE.** Writing a
  probe to the scratchpad — **outside any project** — was refused with `INP001 implicit namespace
  package`: *a file under NO project fell back to SUBSTRATE's bar.* `pycheck_analyze.project_for`
  calls that fallback *"the honest one"*, and **for a file genuinely outside any project it
  produced a rule that is simply wrong for it.** **Ⓝ116 ⟡no-project-is-not-this-project.**

  ⚑ Nothing was edited and **the `.venv` was not touched** — all testing ran in a throwaway venv
  and a fake adopter tree, both disposable. *The measurement was taken without changing the thing
  being measured.*

* ⚑⚑⚑ **Ⓝ71i ⟡deletions-need-a-reader — THE MOTIVATING CASE IS ONE GIT CANNOT RECONSTRUCT AT ALL.**
  `git log --all -- '**/suite_runner.py'` returns **nothing** under any filter: **its entire life
  and death postdates HEAD** (2026-07-28) and has never been committed. *So the reader this item
  asks for cannot be sourced from commit history for the very case that motivated it* — the record
  must be written **at retirement time by the retiring agent**, not mined afterward. ⚑ 13 deleted
  `.py` across 4 commits repo-wide; under `substrate/`, zero.

  ⚑⚑ **FOUR INCONSISTENT RATIONALE HOMES, AND ONE IS A TRAP.** Commit messages (universal, but
  retrievable only by knowing to run `--diff-filter=D`) · `pyproject.toml` (used ONCE, and only
  incidentally — it rides an unrelated exemption, so it is not a register) · `catalog/memory/*`
  (richest, used once) · and `catalog/worklist.md`'s **"RETIRED" section, which holds a DISJOINT
  population** (task labels, explicitly *"never module names"*). **A reader consulting the wrong
  index gets a correct empty answer and banks it as "not retired."**

* ⚑⚑ **Ⓝ96 ⟡snapshot-guard — REFUSED, AND THE REFUSAL NAMES THE UNIT.** The gate specifies the
  exact insert (`edit_snapshot.guard` above the first write in `run_census`), its baseline is EMPTY
  so the finding is real, and `scratch/split_census.py` **cannot accept a one-line edit** — a large
  standing ruff population plus 9 mypy error classes, and zero tolerance has no partial-credit path.
  **The cheapest red on the board is a drain**, and the next cut is the `ratchet_flags`-out-of-
  `ratchet.py` move. ⚑ Two peers not owned: `_pycodemod_census.py` needs an ENTRY guard (2 write
  scopes, no dominating line) and `_pycodemod_fingerprint.py:843`.

* ⚑⚑⚑ **⟡the-unaddressable-section — A CORRECT REFUSAL WITH NO ESCAPE IS A DEAD END, AND I HIT ONE
  WRITING THIS FILE.** `md_spans.find_section` refuses an ambiguous heading (right — the target is
  a WRITE). But this document's H1 CONTAINS its only H2 (`# Ⓝ31 residue — …` ⊃ `## Residue`), so
  **no substring names the section**, and the matcher is `casefold`ed and sees no `#` — neither
  case nor level breaks the tie. **The refusal was permanent: this worklist could not be written by
  its own tool.**

  ⚑ **FIXED AS AN ESCAPE, NOT A DEFAULT** — `exact=True` compares the heading whole; substring
  matching stays the default because it lets a caller name a section without reproducing its
  punctuation. **The ambiguity message now names the escape**, so the next caller is routed rather
  than stopped. ⚑ Pinned by a DISCRIMINATOR arm that fails if substring matching ever resolves the
  contained heading on its own — *without it the exact-match case would pass on a build where the
  flag was ignored entirely.*

  ⚑⚑ **AND THE CLI COULD NOT BE EXTENDED: `scratch/mdstruct.py` IS FROZEN (~1525 findings) AND
  CARRIES A SECOND `find_section` BODY** — same name, same job, `.lower()` where the package uses
  `.casefold()`, so an escape added to one is invisible from the CLI routing through the other.
  *That is `agda_files`' four-bodies-one-name incident, in the tool whose subject is structural
  duplication.* Retiring it is refused until the monolith drains. **New: `substrate/md_write.py`
  (6/6) — the bounded write reaches a command line without touching the frozen file.**

  ⚑ **A THIRD DEFECT FELL OUT: `md_spans_selftest` REPORTED `6/6` WHILE RUNNING EIGHT ARMS.**
  `_CASE_COUNT` was a hand-typed `1 + 1 + …` beside the real roster — **a second roster that
  drifts in both directions**, and the over-count (a deleted arm still claimed) is the dangerous
  half. Now `len(_ARMS)`. ⚑ And `md_write`'s own first cut counted a flag's VALUE as an operand,
  refusing a correct invocation for having three — *invisible to any test whose happy path carries
  no valued flag*, which is why that case is now the suite's first arm.
