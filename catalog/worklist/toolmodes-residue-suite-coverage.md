# Ⓝ31 residue — suite coverage and the census taxonomy

**Concern: which modules have suites, what a suite-coverage census can and cannot see, and the
roster that broke sixteen gates three times.** Index and arc frame:
[`toolmodes-split.md`](toolmodes-split.md).

⚑ This thread is one taxonomy converging under correction: covered/uncovered → +inline →
+tailed/dispatch_only → +delegating. Ⓝ67 ⟡the-slot-is-the-reach states the general form — a
census finds what it has a CATEGORY for, which is sharper than `census-keyed-on-one-spelling`.
Ⓝ66 ⟡witness-not-victim is the arm-design rule that came out of it; Ⓝ68/Ⓝ68a the derived roster;
Ⓝ70 the write-agent partition's exception.

## Residue

* ✅ **Ⓝ63 ⟡converted-without-a-suite — MEASURED. `substrate/suite_gap.py` + report + suite
  (15/15), and the answer is 25.**

      120/145 module(s) have a suite; 25 do not

  ⚑⚑⚑ **AND THE UNCOVERED SET IS CONCENTRATED EXACTLY WHERE TODAY'S SILENT BREAK LIVED — THE
  RATCHET/GATE SPINE.** Of the ten converted ratchet and gate modules, **four have no suite**:

      baseline_io.py · gate_main.py · ratchet_log.py · ratchet_render.py

  `ratchet_render.Report` is the record whose conversion crashed the type gate through seven
  callers in three other files, and `gate_main.py:127` is where the crash surfaced. **Both are in
  the uncovered set, and the batch verification could not have caught either** — which is not a
  coincidence but the mechanism: a module with no suite passes "the suites still pass" vacuously,
  so the failure surfaces at whatever unrelated thing runs it next.

  ⚑⚑ **TWO OF THE 25 ARE MINE FROM TODAY:** `record_migrate.py` (the codemod orchestrator that
  wrote 58 files) and `sort_key.py`. ⚑ The orchestrator having no suite is the sharper one — it
  is the tool that decides what gets written to the tree, and nothing checks it.

  ⚑ **THE MODULE REPORTS A POPULATION, NEVER A VERDICT**, and the render says so. A module without
  a suite is not thereby defective — a pure constant table needs none — but it IS a module whose
  changes nothing catches, and that is the fact a reader weighing a batch needs. Deciding which of
  the 25 deserve suites is a judgement the census must not make.

  **AND THE INCIDENT IS PINNED AS AN ARM**: `the_motivating_module_is_found` asserts against the
  LIVE tree that `ratchet_render.py` is uncovered and `tool_gap.py` is not. ⚑ It fails if the
  situation is repaired, and its message says to REPOINT it rather than delete it — a case that
  goes green by the world changing is a case that has stopped measuring.

* ⚑⚑ **WHAT THIS CHANGES ABOUT THE 58-FILE VERIFICATION CLAIM.** I reported the conversion as
  "written, spot-checked, unverified" and treated the block as `run_selftests` being frozen. That
  was true and incomplete: **even a working runner would not have covered the four spine modules
  above**, because they have nothing to run. The verification gap has two independent causes —
  a frozen runner AND an uncovered population — and only the first was recorded.


* ✅ **Ⓝ63′ ⟡cover-the-spine — FIRST SUITE LANDED: `ratchet_render_selftest.py`, 29/29.**
  Twenty-one arms over the module whose MISSING suite let a `NamedTuple`→dataclass conversion
  break the type gate through seven callers in three other files. Coverage **120/145 → 121/145**.

  **EVERY ARM PINS A DEFECT THE SOURCE ALREADY RECORDED** — the module's ⚑ comments are measured
  incidents, so the suite writes itself from them:

      the renderer is TOTAL on keys       a paid-down key is ABSENT from the current census by
                                          definition, so a renderer indexing that census raises
                                          exactly on the branch reporting PROGRESS — a gate
                                          crashing on its own good news
      paydown despite additions           the old code returned on `added` FIRST; measured live at
                                          375 new hiding 8,516 paid down
      the mint names the ROUTE            it used to name the ENV VAR the commit path exports,
                                          handing every reader a BYPASS of the minting gate
      a MOVE is its own line              not paydown, not growth — absorbing it lets a
                                          decomposition silently relabel debt
      quiet suppresses SUCCESS only       a gate quiet about a REFUSAL is indistinguishable from
                                          one that passed

* ⚑⚑⚑ **AND THE INCIDENT ARM FIRED, WHICH IS THE DESIGN WORKING RATHER THAN A FAILURE.**
  `suite_gap_selftest.the_motivating_module_is_found` pinned `ratchet_render.py` as uncovered
  against the LIVE tree. Landing its suite turned that arm red — with the message it was written
  to carry:

      selftest: ratchet_render.py was not reported — is it now covered? repoint the arm

  **A case that goes green because the world improved has STOPPED MEASURING.** The witness moved
  to `gate_main.py` (still uncovered) and the property stays pinned; the comment now records that
  it has been repointed once and why. ⚑ Deleting it instead would have removed the only thing
  asserting that the uncovered population is READ rather than assumed.

* ⚑⚑ **THE UNTYPED-LAMBDA DEFECT, FOURTH SCALE.** The first cut used `lambda k: f"<{k}>"` and
  `lambda _k: ""` as fixtures; mypy refused both (`Expression type contains "Any"`). Named
  functions carry the annotation. This is the same boundary erasure as `getattr` field-probing,
  `object`-typed rows, and an `isinstance` union wider than its attribute set — arriving through a
  one-line convenience. ⚑ **FIXTURES ARE WHERE IT HIDES, because nobody reviews a test's helper.**

  **REMAINING IN THE SPINE:** `gate_main.py` · `baseline_io.py` · `ratchet_log.py` — and 21 others
  in the uncovered set, including `record_migrate.py`, the orchestrator that wrote 58 files to the
  tree with nothing verifying it.


* ✅ **Ⓝ63′ ⟡cover-the-spine — SECOND SUITE: `gate_main_selftest.py`, 16/16. HALF THE SPINE
  COVERED.** Twelve arms over the authority that can say *"I did not run"* — the module holding
  the line that crashed the type gate.

  **THE ARMS PIN WHAT ITS OWN DOCSTRINGS RECORD AS BANKED DEFECTS:**

      exit 2 exists at all           a `python3` without mypy produced no error lines, the parse
                                     honestly found nothing, and **0 keys over 60 unannotated
                                     files was banked as a clean census**. A gate that can only
                                     say 0 or 1 reports its blind spot as a PASS
      --quiet never silences it      quiet suppresses a PASS; blindness is not one
      three codes, three actions     0 passes · 1 is fixed AT THE SITE · 2 is fixed IN THE
                                     ENVIRONMENT — conflating 1 and 2 sends a reader hunting code
                                     that is not wrong
      the census is not taken        …when argv is refused. ⚑ The arm COUNTS INVOCATIONS, because
                                     an exit code cannot distinguish a census that ran from one
                                     that did not
      the reason survives            *"not importable"* was once a guess printed as a fact
      `__replace__`, not `_replace`  ← THE CRASH, pinned directly

* ⚑⚑⚑ **AND THE WITNESS ARM EXPIRED TWICE IN TWO TURNS, WHICH IS A FINDING ABOUT THE ARM.**
  `suite_gap_selftest`'s incident arm named `ratchet_render.py` as uncovered; landing that suite
  turned it red. I repointed it to `gate_main.py`; landing THAT suite turned it red again.

  **A witness that must be repointed every time the work succeeds is friction the work itself
  creates** — and the third repointing would have been mechanical, which is exactly where a reader
  starts editing a case to make it pass rather than reading what it says.

  ⚑⚑ **SO THE ARM NOW ASSERTS THE PROPERTY, NOT AN INSTANCE:** the census READS the live tree
  rather than reporting a constant — some covered, some not, and a known-covered module never
  reported uncovered. All three survive the population improving. ⚑ The `_COVERED` half is the
  discriminator: without it, a census reporting EVERY module as uncovered would satisfy the rest,
  which is the constant-predicate failure a positive-only assertion cannot see.

  ⚑ **THE GENERAL FORM — Ⓝ66 ⟡witness-not-victim.** A case pinned to a NAMED instance of a
  population expires when that instance is fixed; a case pinned to the POPULATION'S SHAPE does
  not. The first reads as more concrete and is strictly weaker, because its failure mode is
  "someone edited the name" rather than "the property broke".

  **REMAINING IN THE SPINE:** `baseline_io.py` · `ratchet_log.py`. Coverage 121/145 → 122/145.


* ⚑⚑⚑ **Ⓝ63′ — THE SPINE WAS ALREADY COVERED, AND MY CENSUS WAS LYING. `census-keyed-on-one-
  spelling`, IN THE TOOL BUILT THIS TURN TO AVOID EXACTLY THAT.**

  About to write a suite for `baseline_io.py`, I read it first — and found `def selftest()` with
  ten cases already in it. It runs: **`baseline_io --selftest` → 10/10.** `suite_gap` reported it
  UNCOVERED because `has_suite` asked one question — *does `<module>_selftest.py` exist* — while
  the runner accepts TWO conventions and executes both identically.

      before  121/145 covered · 24 uncovered
      after   128/145 covered · 17 uncovered      ← seven false positives

  **`baseline_io`, `baseline_state`, `ratchet_flags`, `ratchet_log` all carry inline suites** —
  including `ratchet_log`, the other half of the spine I was about to write. **I nearly wrote a
  duplicate suite for a module that already had one**, which is the `agda_files()`-had-four-bodies
  shape arriving through a census rather than through a name.

  ⚑⚑ **AND THE FAILURE WAS IN THE ALARMING DIRECTION, which is why it was findable at all.** A
  census reading one convention reports the CONVENTION, not the property. Over-reporting generates
  work that already exists; under-reporting hides work that does not — and only the first is
  caught by doing the work. ⚑ The census I built specifically to make a vacuous pass legible had
  the same defect one layer up, and it took writing its own subject to notice.

  **SO THE SPINE IS DONE:** `ratchet_render` (29/29) and `gate_main` (16/16) genuinely had none
  and now have suites; `baseline_io` and `ratchet_log` had them all along.

* ⚑⚑ **AND THE PREDICATE CHANGE BROKE AN ORDERING THAT AN EXISTING ARM CAUGHT IMMEDIATELY.**
  `has_suite` was a pure `.exists()` on a sibling, so `uncovered_among`'s
  `not has_suite(p) and p.exists()` was harmless. Reading the module for an inline suite made it
  RAISE on an absent path — and `a_name_not_present_is_not_reported` failed on the next run, with
  a traceback naming the line.

  ⚑ **THAT ARM EXISTS BECAUSE ABSENT AND UNCOVERED ARE DIFFERENT FACTS** — written for a semantic
  reason, and it caught a mechanical regression the semantics never anticipated. **A case pinned
  to a PROPERTY catches changes its author did not foresee; a case pinned to an INSTANCE catches
  only what it was aimed at** (Ⓝ66 ⟡witness-not-victim, from the same file, two turns earlier).

* ⚑⚑⚑ **THE ENTRY ABOVE IS WRONG IN ITS CONCLUSION, AND THE OPERATOR CORRECTED IT WITHIN THE
  TURN THAT WROTE IT: *"n-split that crap. No more in-line/tail testing."*** I found four modules
  carrying `def selftest()` in their own tails, observed that the runner executes them, and
  concluded the census had missed a SECOND CONVENTION. **There is one convention. The other shape
  is DEBT**, and widening the predicate to accept it reported coverage improving 121→128 with
  nothing written.

  ⚑⚑ **THE RUNNER EXECUTING BOTH IS EXACTLY WHY IT LOOKED LIKE A CONVENTION** — and executability
  is the one property the two shapes share. Everything else that makes a suite useful is weaker
  inline: **the cases cannot run without importing the module under test**, they inflate the file
  the per-file gate measures, and a module too dirty to edit takes its own suite hostage.
  `toolmodes.py` — 615-line `_selftest` inside 3,700 lines that no edit can touch — is where this
  shape ENDS, and this session has spent two arcs unable to run it.

  ⚑ **SO IT IS A THIRD CATEGORY, NOT A SECOND SPELLING, and two categories could not have held
  it.** Reporting inline as *covered* hides the split that is owed; reporting it as *uncovered*
  sends a reader to write a duplicate — which is what nearly happened to `baseline_io`. Both
  facts have to survive, so `Coverage` now carries `covered / inline / uncovered` and `render`
  names the middle one as *"cases in the wrong place, owed a split"*.

  **THE HONEST CENSUS — and NEITHER of my two earlier numbers was it:**

      122/145 split (the accepted shape)
        6     INLINE — debt        baseline_io · baseline_state · proc_ancestry
                                   ratchet_flags · ratchet_log · withheld_verdict
       17     uncovered
                                   ⚑ 121 called inline "uncovered"; 128 called it "covered"

  ⚑ **AND THE INLINE POPULATION IS 6, NOT THE 4 THE PREDICATE-WIDENING FOUND** — `proc_ancestry`
  and `withheld_verdict` surfaced only once the census had a category to PUT them in. A census
  finds what it has a slot for; the 4 was the reach of a hand-run `--binding` probe, the 6 is the
  reach of a mode. `suite_gap_selftest` 15/15 → **20/20** (two arms: inline is neither covered nor
  uncovered; a sibling suite beats a vestigial tail).

  **Ⓝ63‴ ⟡n-split-the-tails** — six modules whose cases move to `<module>_selftest.py`. ⚑ Each is
  a `Write` of the new suite plus a `Write` of the trimmed module: **two files, atomic each**, and
  the trim cannot precede the extraction (a module losing `selftest` while nothing else defines it
  is the intermediate state that is never independently clean).


* ⚑⚑⚑ **Ⓝ67 ⟡the-slot-is-the-reach — A CENSUS FINDS WHAT IT HAS A CATEGORY FOR, WHICH IS A
  SHARPER CLAIM THAN `census-keyed-on-one-spelling`.** Measured within one turn, on one
  population, by two methods:

      hand-run `pycodemod --binding selftest`   →  4 inline suites
      `suite_gap` once it had an `inline` slot  →  6 inline suites

  **`proc_ancestry` and `withheld_verdict` were invisible to the probe and visible to the mode**,
  and nothing about the spelling differed — both spell it `def selftest(`. What differed is that
  the probe was aimed at a HYPOTHESIS I already held (*"are there more like `baseline_io`?"*)
  while the mode enumerated a POPULATION.

  ⚑⚑ **SO THE FAMILIAR FORM UNDERSTATES IT.** `census-keyed-on-one-spelling` says: ask for the
  other name and you will find the rest. That is true and it was not the failure here. **The
  failure is that a finding has nowhere to LAND until the instrument has a category for it** — a
  two-category census (covered / uncovered) cannot report "inline" however many spellings it
  checks, so the two extra modules were not merely unasked-for, they were *unrepresentable*.

  ⚑ **AND THE DIRECTION IS THE USUAL ONE: the missing category collapses into whichever
  neighbour is nearest, silently.** Before the fix, all six sat in `uncovered` — which reads as
  *"write a suite"* and would have produced six duplicates. After I widened the predicate, all
  six sat in `covered` — which reads as *"nothing owed"* and hid six splits. **Two-thirds of the
  possible readings of that population were wrong, and both wrong readings looked like a clean
  census.** Only the three-way split is honest, and it took the operator's correction to get
  there.

  **THE OPERATIONAL FORM:** when a probe and a mode disagree on a population size, do not
  reconcile the counts — ask what CATEGORY the smaller one lacked. Sibling of
  `the-fact-may-be-an-edge-not-a-property` (when a per-item predicate cannot express the
  distinction, the discriminator is elsewhere) and of Ⓝ63′'s own finding one entry up.
* ⚑⚑⚑ **Ⓝ68 ⟡the-registry-is-the-reason — THE INLINE SUITES WERE NOT AN ACCIDENT, AND SPLITTING
  THEM TOOK DOWN SIXTEEN GATES THREE TIMES.** `substrate/ratchet_suites.py` composes a ROSTER OF
  CALLABLES:

      SUITES = (ratchet_log.selftest, ratchet_flags.selftest, proc_ancestry.selftest,
                withheld_verdict.selftest, baseline_state.selftest, baseline_io.selftest,
                ratchet_core_selftest.selftest)

  **Those are exactly the six modules the census reported as INLINE.** The convention I had just
  finished calling *debt* had a reason: a registry that reaches `<module>.selftest` requires the
  callable to live in the module. Each trim raised `AttributeError` **AT IMPORT**, propagating
  through `scripts/ratchet.py` to every one of the sixteen gates that imports it — caught each
  time by an unrelated `mdstruct` call, never by anything aimed at the change.

  ⚑⚑ **AND BOTH PROPERTIES I VERIFIED WERE TRUE THROUGHOUT.** Module clean, suite green
  (14/14), far end never checked — `the-holder-is-not-the-worker`, walked into with the memory
  loaded. **A split is not done when the module is clean; it is done when its CONSUMERS are
  repointed.**

  ⚑⚑⚑ **AND THE CALL I THEN PRESCRIBED AS THE FIX DOES NOT WORK — measured by the agent I
  prescribed it to.** I wrote, twice, that `pycodemod --attr <mod>.selftest` would have found the
  registry in one call. It returns:

      --attr ratchet_flags.selftest   →   0 attribute read(s) in 0 of 1142 file(s)

  **while `ratchet_suites.py:46` was literally `ratchet_flags.selftest`.** The mode does not
  resolve the `from substrate import ratchet_flags` alias form; `--importers
  substrate.ratchet_flags` likewise returned 0, because the real consumers arrive through the
  `ratchet.py` re-export. **So the remedy for a false-absence finding was itself a false
  absence** — a zero that is a fact about the METHOD, reported in the same breath as the lesson
  about facts-about-the-method. ⚑ Ⓝ68b: `--attr` must resolve `from <pkg> import <mod>` bindings,
  or say it cannot; this repo DELETES on `--dead`.

  ⚑ **THE ROSTER'S OWN DOCSTRING ARGUES FOR THE SHAPE THAT BROKE:** *"a new module cannot be
  silently left uncovered the way a hand-typed roster once omitted `BaselineState.UNREAD`."*
  True, and it is why the file exists — but it is still a HAND-TYPED ROSTER, now of modules
  instead of cases, with the same failure mode one level up. **⟡selftest-discovery already solves
  this generically** (`run_selftests.discover()` keys on the `--selftest` literal), so the only
  thing the list holds that discovery does not is the leaf-first ORDER. **Ⓝ68a: derive the
  roster, keep the order.**

* ⚑⚑ **AND A REGISTRY REPOINT IS ATOMIC BY CONSTRUCTION — I INSTRUCTED THE OPPOSITE AND IT COST
  THREE REFUSED WRITES ACROSS TWO AGENTS.** I told both agents *"one `Edit` call per entry,
  matching only the line you own"*, to keep them from clobbering each other. **Not achievable
  under zero tolerance:** the import name and the `SUITES` member are NON-CONTIGUOUS, and both
  orderings leave a finding — import first `F401 imported but unused`, roster line first `F821
  Undefined name` — with a stale sibling entry adding mypy `[attr-defined]` plus an `Any` cascade
  through `SUITES` and `run_all`.

  ⚑ **THE FILE IS THE GATE'S UNIT, SO IT IS THE REPAIR'S UNIT.** Two agents splitting different
  modules into one roster can only land by writing EVERY entry — which means the ownership
  partition I built the dispatch around (disjoint file sets, so nobody clobbers anybody) has an
  exception it cannot express: a shared registry is co-owned by every splitter. Both agents
  converged on the same conclusion independently, from opposite ends. **The same non-contiguous
  hazard as the trims, reappearing one layer up**, which is the third instance this session.


* ⚑⚑ **Ⓝ70 ⟡the-partition-has-an-exception — DISJOINT FILE SETS ARE NOT DISJOINT WORK, AND THE
  REGISTRY PROVED IT TWICE IN ONE DISPATCH.** The write-agent partition this session used is
  *give each agent files nobody else owns*, which is sound against the per-file gate (any finding
  reverts the WHOLE file, so two writers on one file silently undo each other). It has an
  exception it cannot express: **a shared registry is co-owned by every splitter.**

  Both ⟡n-split-the-tails agents converged on this independently, from opposite ends: a
  per-entry repoint of `ratchet_suites.py` is refused under zero tolerance, and — worse — while
  ANY peer's entry was stale, mypy cascaded `[attr-defined]` and `Any` through `SUITES` and
  `run_all`, so **each agent's CORRECT entries were refused on the other's pending work.** Three
  refused writes for me, three for one agent, before one of them wrote all seven entries at once.

  ⚑ **THE FILE IS THE GATE'S UNIT, SO IT IS THE REPAIR'S UNIT** — and that reaches past this
  incident: any file that N agents must each touch is a serialization point the partition hides.
  The partition should name it as SHARED and assign it to exactly one agent as a final step,
  rather than telling N agents to edit "only their line".

  ⚑⚑ **AND MY INSTRUCTION MADE IT WORSE, NOT NEUTRAL.** *"One `Edit` call per entry, matching
  only the line you own"* was aimed at the clobber hazard and was unachievable for the same
  structural reason the trims were: the import name and the `SUITES` member are NON-CONTIGUOUS,
  and both orderings leave a finding (`F401` vs `F821`). **Third instance of that shape today** —
  the trim, the roster repoint, and the census-predicate change all needed one atomic write, and
  I re-derived it as a surprise each time.

* ⚑⚑ **Ⓝ70a ⟡dispatch-order-is-a-dependency — A SECOND WAVE CAN BE BLOCKED BY A FIRST WAVE'S
  RESHAPING, NOT ONLY BY ITS FILES.** Ⓝ69 ⟡cover-the-composer writes cases for
  `ratchet_suites.py` while Ⓝ68a ⟡derive-the-roster is REWRITING that module's shape. The file
  sets are disjoint (one writes a suite, one writes a module) so the partition reports no
  conflict — **and dispatching them together would produce cases pinned to a shape about to
  change, which is the witness-expiry failure created deliberately in advance.**

  ⚑ Same for Ⓝ66 ⟡witness-not-victim, an audit ACROSS suites the current agents are editing. The
  dependency is not on the files; it is on the SHAPE being settled. Held both until wave one
  reports.
* ✅ ⚑⚑⚑ **Ⓝ68a ⟡derive-the-roster — DONE, AND THE DERIVATION FOUND A SILENTLY UNCOVERED MODULE
  ON ITS FIRST RUN. THE ROSTER WAS 7 AND SHOULD ALWAYS HAVE BEEN 8.**

  `ratchet_render` is re-exported by the facade (`Report`), its suite passes **29/29**, and the
  hand-typed roster simply never named it. **Not caught by review, not by the coverage census,
  not by the three splits that broke this very file within one hour** — caught the instant
  membership stopped being typed.

      before   ratchet: 7/7 module suite(s) passed
      after    ratchet: 8/8 module suite(s) passed      ← ratchet-render 29/29

  ⚑⚑ **AND IT WAS LATENT IN THE FILE WHOSE DOCSTRING CLAIMED IT WAS IMPOSSIBLE:** *"a new module
  cannot be silently left uncovered the way a hand-typed roster once omitted
  `BaselineState.UNREAD`."* The sentence was written about the CASES the file replaced and read
  as if it covered the MODULES it now lists. **The same defect, one level up, under a docstring
  asserting immunity to it.** Verified independently: `substrate/ratchet_suites.py --selftest`
  and `scripts/ratchet.py --selftest` both report 8/8 with byte-identical member lines, so the
  import chain feeding the sixteen gates is intact.

  ⚑ **MEMBERSHIP IS DERIVED FROM AN AUTHORITY THAT ALREADY EXISTED AND WAS BEING MAINTAINED FOR
  A DIFFERENT REASON.** `scripts/ratchet.py`'s module-level `from substrate.<mod> import …`
  lines ARE the extraction manifest of ⟡ratchet-seams — load-bearing for 22 consuming files.
  Read by `import_edges.module_level_dotted` (AST, never an import — several of these modules do
  work at import time) and joined to `suite_discovery.is_suite`. **Nothing new defines
  membership; the list was in the tree already.**

  ⚑⚑ **THE ORDER STAYS TYPED, AND THAT IS THE CORRECT SPLIT.** `ORDER` is a judgement —
  dependency order is not derivable from a flat import set — but it now names the CAPABILITY
  (`ratchet_log`) rather than `<module>.selftest`, so **the sibling convention is the sole
  authority on where cases live and the next split moves nothing in this file.** That is the
  exact failure that broke it three times in an hour, removed at the root rather than repaired.

  ⚑ **BOTH DISAGREEMENT DIRECTIONS REFUSE, NEITHER SKIPS.** Discovered-but-unordered raises
  `UnorderedSuiteError` — appending would make *"ordered deliberately"* and *"fell to the end
  because nobody said"* indistinguishable, and would drop an unjudged module into the
  load-bearing last slot. Listed-but-missing stays loud (`hasattr` + `NoEntryPointError`, never
  `getattr(…, None)`, which is one keystroke from a silent skip). ⚑ `UnorderedSuiteError` is
  WITNESSED, not hypothetical: it fired on `ratchet_render`.

  ⚑ **RESIDUE, NAMED BY THE AGENT RATHER THAN LEFT IMPLICIT: NOTHING GATES `ORDER` AGAINST THE
  ACTUAL DEPENDENCY EDGES.** Completeness is checked (every discovered member is placed); the
  leaf-first CLAIM is asserted by comment and verified by nothing. `import_edges` could derive a
  topological check. **Ⓝ68a′ ⟡gate-the-order** — a hand-typed judgement with no gate is the
  shape this whole item was about, surviving one layer smaller.


* ⚑⚑ **Ⓝ69 ⟡cover-the-composer IS A SPLIT, NOT A FRESH SUITE — I FRAMED IT WRONG AND THE AGENT
  CORRECTED ME FROM INSIDE ITS OWN TASK.** I listed `ratchet_suites.py` as UNCOVERED on the
  paths-forward board and briefed Ⓝ69 as *"write its suite"*. The census says INLINE: the
  composer carries cases in its own tail, so the owed work is an extraction, and a fresh suite
  would have been a DUPLICATE.

  ⚑ **THAT IS THE `baseline_io` NEAR-MISS AGAIN, ONE TURN AFTER BUILDING THE CATEGORY THAT
  PREVENTS IT** — and this time the three-way census was RIGHT while my summary of it was stale.
  I read the census when the inline category was empty, carried "uncovered" forward in prose, and
  the tree moved underneath. **A board entry is a snapshot; the census is the authority.**
  Re-read it at dispatch time, not at planning time.

  ⚑ **AND THE DENOMINATOR IS MOVING UNDER THE COUNT: 145 → 147** while three agents run. So
  `130/147` is not comparable to the `129/145` recorded twenty minutes earlier — the population
  grew (`attr_reads.py`, a new module from the Ⓝ68b work, is one of the two). **A coverage RATIO
  read across a moving population reports progress it did not measure**; only the named
  membership is stable enough to compare. Same class as the store figures that must be re-read at
  point of use and stamped, never carried between steps.

  ⚑ **THE Ⓝ68a AGENT ALSO REPORTED THE SPLIT IS NOW SUBSTANTIALLY MORE EXPRESSIBLE**, which is a
  consequence worth keeping: `extracted`, `has_suite` and `members` became pure functions taking
  a `root`, so a sibling can point them at a FIXTURE TREE and assert the derivation itself —
  the manifest read, exclusion of a member with no sibling, `UnorderedSuiteError` on an unplaced
  member, `ORDER`-relative ordering regardless of discovery order, `NoEntryPointError` on a
  sibling with no entry point. **None of that was reachable when the roster was a bare tuple of
  already-bound callables** — deriving the membership did not just fix the defect, it made the
  defect testable.
* ✅ ⚑⚑⚑ **Ⓝ69 ⟡cover-the-composer — DONE (9 arms, `ratchet: 9/9`), AND MY BRIEF'S PREMISE WAS
  WRONG FOR THE SECOND TIME ON THE SAME ITEM.** I first called it *uncovered* (it was INLINE);
  corrected that, and briefed a SPLIT. **There was nothing to split: `ratchet_suites.py` has no
  `selftest` definition at all.** The INLINE classification came from `suite_discovery.is_suite`
  matching the module's own `__main__ --selftest` dispatch — which runs `run_all` — with no
  sibling to hold cases. The fix was purely ADDITIVE.

  ⚑⚑ **AND THE TOOL BUILT ONE HOUR EARLIER IS WHAT ESTABLISHED THAT.**
  `module_trim --dry-run … selftest` returned **`UNSAFE / no top-level definition named:
  selftest`** — the name-not-found refusal working exactly as documented, catching a
  coordinator's mis-framing before any write. **An unmatched name being a REFUSAL rather than a
  no-op is what made the tool able to correct the person driving it**; a tool that trimmed what
  it found and reported success would have confirmed the wrong premise.

  ⚑ **SO `is_suite` MATCHES THE DISPATCH LITERAL, NOT A DEFINITION** — which is correct for
  discovery (that is what `run_selftests` keys on) and means INLINE, as a census category, spans
  two different shapes: *cases in the tail* and *a CLI with no sibling*. Both are honestly "cases
  not in a sibling"; only the first is a split. **Ⓝ69a: the category could distinguish them, and
  a reader acting on it currently cannot.**

* ⚑⚑⚑ **AND THE DERIVATION FOUND ITS SECOND MISSING MEMBER, ON A DIFFERENT MECHANISM — 8/8 →
  9/9.** Creating the sibling raised `UnorderedSuiteError: ratchet_suites` **before a single case
  ran**: the facade re-exports `run_all` FROM the composer, so the moment the composer had a
  suite it became a discovered member its own `ORDER` did not place. **The composer is a composed
  capability like any other, and nothing had ever typed that fact.**

  Placed LAST, after `ratchet_core`, by judgement rather than append — its arms call
  `members()`/`suites()` over the live tree, so it is the one row that depends on every other row
  resolving. No recursion: the sibling exercises the DERIVATION, never `run_all`.

  ⚑⚑ **SECOND TIME IN TWO TASKS THAT ⟡derive-the-roster's REFUSAL FOUND A MEMBER REVIEW MISSED**
  — `ratchet_render` (29/29, silently unlisted) and now the composer itself. Both were invisible
  to review, to the coverage census, and to me; both surfaced the instant membership stopped
  being typed. **A refusal that fires twice on its first day is not a strict gate, it is a
  measurement of how much the hand-typed form was hiding.**

  ⚑ **A HAZARD THE AGENT NAMED RATHER THAN ABSORBED:** the `NoEntryPointError` arm PLANTS a real
  module into the package for the length of the case and removes it in a `finally`, popping
  `sys.modules`. **Borrowing an existing module would have pinned `ModuleNotFoundError` while
  reading as a pass** — green for a reason unrelated to the property, which is the vacuous-arm
  shape this whole arc has been closing. Census verified at 147 modules afterwards; nothing
  survived.

  ⚑ **AND THE PER-FILE GATE SAID THE UNIT WAS WRONG AGAIN:** a single `selftest` tripped
  `PLR0915`, so the sibling is split `_derivation` / `_refusals` / `selftest`. Three writes were
  refused first (RUF100, FBT003 positional booleans, E501, EXE001). ⚑ Ⓝ68a′ ⟡gate-the-order is
  now **partly** expressible — the suite pins ordering as `ORDER`-relative rather than
  discovery-relative (the mechanism half), but NOT that `ORDER` is topologically sound; the
  leaf-first claim is still comment-only. The fixture harness `_fixture(root, imports, siblings)`
  makes it a ~15-line arm in an existing file rather than new machinery.

* ⚑⚑⚑ **Ⓝ31s⁸′ ⟡verify-the-58 — GREEN, UNDER TWO DISPATCHERS, AND THE AGENT NAMED THE
  CORRELATION RATHER THAN CLAIMING INDEPENDENCE.**

      arm 1  run_selftests.py (verbose)   170 suites, every one N/N, zero failures
      arm 2  make -f Selftest.mk -k -j8   17 failed, NONE implicating the conversion

  Arm 2's failures are store-dependent suites with postgres/VM down, three `Error 143` timeouts,
  a bare-module dispatch artifact whose `_selftest` sibling passes 15/15, and `run_selftests.py`
  on this very TypeError. `record_migrate --dry-run substrate/` now finds **8 candidates** (2
  clean, 6 needing a human) — the 58 are converted and no longer candidates.

  ⚑ **THE CAVEAT IS THE AGENT'S OWN AND IT IS THE RIGHT ONE:** both arms run the SAME suites, so
  they are correlated on suite CONTENT; what decorrelates them is the DISPATCH. ⚑ And the first
  attempt could not answer at all — **`--quiet` suppresses the per-suite lines**, so the verbose
  run was required. *A flag that suppresses output changes what a run can be asked afterwards.*

* ✅ ⚑⚑⚑ **Ⓝ66 ⟡witness-not-victim — AUDITED, AND THE POPULATION WAS GENUINELY SMALL: 1 SUITE, 2
  ARMS, OUT OF 132.** The agent reported one rather than padding a list, which is the correct
  outcome to report and the harder one to write up.

  ⚑⚑ **AND THE AT-RISK SET WAS DERIVED STRUCTURALLY RATHER THAN BY READING ARMS AT RANDOM.**
  `pycodemod --attr 'corpus.*'` returns the 14 suites that reach the LIVE tree — **the mechanical
  signature of a real-tree fixture** — plus four more by live-count and roster-membership
  signals. 18 read in depth, out of 132. *The instrument for "which arms can expire" is "which
  arms touch the thing that moves"*, and that is a query, not a reading exercise.

  **THE FINDING — `substrate/grade_witness_selftest.py`, and it fails in the ALARMING direction
  inverted.** Two arms called `witness(...)` against live `corpus.ROOT` and asserted the verdict
  says `UNMEASURED`. `graded()` returns unavailable exactly while `catalog/worklist/grades.json`
  is ABSENT — so **both arms would go RED THE DAY THE MUTATION SWEEP RUNS**, i.e. red exactly
  when the work they exist to demand SUCCEEDS. Not "expires when fixed" but "punishes the fix".

  ⚑⚑⚑ **AND THE SUITE'S OWN HEADER ALREADY GAVE THIS REASON FOR ITS OTHER ARMS** — *"would go
  green the day the sweep runs, which is exactly when the OTHER arms need to start working"* —
  while these two were the ones that did not follow it. **The policy was stated in the file that
  violated it**, which is the same shape as CLAUDE.md instructing a grep against the artifact its
  own first section forbids grepping.

  ⚑⚑ **THE REPAIR CARRIES A DETAIL THAT WOULD HAVE SILENTLY UNDONE IT: `witness` IS A GENERATOR.**
  A `list()` taken after the `finally` would read the LIVE tree while the case believed it held a
  controlled root — **a fixture that silently stops being one**. `_rows_at(root)` materialises
  inside the rebind. *Laziness moves WHEN a read happens, and a fixture is a claim about when.*

  ⚑ **AND THE NEW ARM IS THE DISCRIMINATOR, WHICH INVERTS THE POLARITY:**
  `a_present_record_set_does_not_open_unmeasured`. Without it a witness hardcoded to open
  UNMEASURED passes every other arm — and **the origin defect for this very module was a constant
  predicate** (`getattr(fn, "_graded", False)`, which nothing writes). The sweep landing is now
  what the case DEMANDS rather than what breaks it. 8/8 → **10/10**.

* ⚑⚑ **Ⓝ66a — THE TREE HAS ALREADY INTERNALISED THIS DISCIPLINE, AND THAT IS THE REPORTABLE
  RESULT.** Four suites (`family_roster`, `edge_witness`, `census_denominator`, `grade_witness`)
  carry *"fixtures are written here, not read from the live corpus"* in their module docstrings.
  Others were judged sound FOR STATED REASONS rather than by verdict: `sole_authority` (fake
  censuses plus an explicit rival positive control), `case_lens` (a missing-file arm separating a
  blind lens from a moved file), `suite_discovery`/`import_edges` (live positive controls that
  exist because *"zero is what a broken walk and a correct walk over an empty tree both
  return"*), `tenant_census` (its live arm REPORTS and returns 0 BY DESIGN, so it cannot expire),
  `suite_record` (reads a cross-file authority deliberately and fails loudly with a follow-it
  message if the authority moves), `collision_scope` (`corpus.ROOT` as a path BUILDER only).

  ⚑ **A ONE-FINDING AUDIT OVER 132 SUITES IS A MEASUREMENT OF THE CONVENTION'S REACH, not a weak
  result** — and it is only readable as that because the agent said WHY each suite was sound.
  A bare "17 fine" would have been indistinguishable from 17 unread.

* ✅ ⚑⚑⚑ **Ⓝ63⁶ ⟡the-remaining-15 — DONE, AND THE HONEST SPLIT IS THE DELIVERABLE: 10 SUITES
  WRITTEN (251 cases), 5 GENUINELY OWED NONE.** Census **132/147 → 142/147**, same denominator, so
  the ten are comparable by name. ⚑ The five that remain uncovered are EXACTLY the five argued to
  need nothing — **the census and the judgement now agree**, which is the state where the number
  is finally readable.

      sort_key 41 · gen_selftest_mk 37 · tool_find_render 36 · store_reach 33 · twin_check 26
      library_module 22 · promote_agree 21 · md_tables_show 19 · ratchet_census_show 17
      store_calls 15

  **REFUSED WITH REASONS, not left silent:** `gate_module_exiting_fixture` IS DATA (1 statement,
  `sys.exit(2)` at module scope; a suite would duplicate the consumer's case or execute the exit)
  · `md_spans_show` / `kind_partition_show` **already delegate `--selftest` to their reader's
  suite** · `suite_gap_report` is a 12-line formatter over predicates `suite_gap_selftest` pins ·
  `engine_edges` returns `paperkit.bib._LIST` and is already gated by `check_stub_authority.py`
  running `stubtest` — **a decorrelated instrument, which is the right reason to not write a
  second one.**

* ⚑⚑⚑ **AND THE AGENT'S OWN FIXTURE LEAKED WHILE ITS SUITE REPORTED 21/21 CLEAN.** Three `.pyc`
  caches survived in `catalog/library/`, found ONLY by sweeping the filesystem afterwards — not
  by the suite, which was checking what it knew it had written. **A cleanup verified against its
  own record of what it created cannot see what the RUNTIME created**; bytecode caches are
  written by the interpreter, not the test.

  ⚑ Fixed, and turned into a 22nd arm that **reads the directory before and after** rather than
  enumerating known files — the observe-the-effect discipline applied to the cleanup itself.
  Same lesson as Ⓝ63⁵'s write-loop arms asserting on bytes read back from disk rather than on
  the predicate the code consults. **Verified independently: no `library_module_selftest_*` stem
  survives; the remaining `__pycache__` entries belong to `figures`/`items`/`concepts`, real
  modules, and are gitignored.**

* ⚑ **THREE PROPERTIES WITHDRAWN AS UNFALSIFIABLE, EACH BECAUSE THE TYPE GATE ALREADY PROVES
  THEM** — `twin_check.PROMOTED` non-empty (literal tuple), `store_calls.connect_sites` returns
  `frozenset` (the annotation decides it), `promote_agree._ARMS` non-empty and callable (literal
  tuple of functions). **A case whose failure branch is statically unreachable cannot fail**, and
  writing it would have been the vacuous-arm shape this arc exists to close. Documented as
  withdrawn, with the reason, in each suite's header.

  ⚑ **AND ONE ARM WENT RED AGAINST CORRECT CODE, WHICH IMPROVED IT:** `gen_selftest_mk`'s stamp
  reaches `suite_run` as make's `$@`, not a re-spelled literal, so **the recipe cannot disagree
  with its own rule**. The first arm asserted the literal; the shipped one pins the stronger
  property. A red case over correct code is information about the ARM.

  ⚑ `promote_agree --discover`: **276 suites, identical to the pre-split implementation** — the
  ten new suites are visible to the runner. 8 write refusals during the work, each reverted and
  repaired rather than suppressed.

* ⚑⚑⚑ **Ⓝ69a′ ⟡delegation-is-not-dispatch-only — THE CATEGORY SPLIT LANDED AND IMMEDIATELY
  CONTRADICTED A JUDGEMENT FROM THE PREVIOUS WAVE. BOTH READINGS ARE DEFENSIBLE AND THEY POINT
  OPPOSITE WAYS.** Observed live, minutes apart:

      Ⓝ63⁶ (agent, reading the modules):
        md_spans_show / kind_partition_show — OWED NONE. "argument-check-plus-print over readers
        already covered; both already DELEGATE `--selftest` to their reader's suite. No branch a
        case could pin that md_spans_selftest / kind_partition_selftest doesn't."

      Ⓝ69a (census, reading the same modules):
        2 DISPATCH --selftest with no cases defined — owed a NEW SUITE
        ? kind_partition_show.py    ? md_spans_show.py

  ⚑⚑ **THE CENSUS IS RIGHT ABOUT THE PREDICATE AND WRONG ABOUT THE OBLIGATION.** These modules
  DO answer `--selftest` and DO define no cases — the mechanical test is satisfied. But they
  answer it by **calling a sibling suite that already covers the reader they wrap**, which is a
  third thing: not a tail owed a split, not a bare CLI owed a suite, but a DELEGATION that is
  already covered at the far end. `dispatch_only` currently means *"answers --selftest, defines
  nothing"*, and that spans both a genuine gap and a deliberate forward.

  ⚑ **SO THE CATEGORY SPLIT THAT FIXED ONE CONFLATION INTRODUCED ANOTHER, ONE LEVEL FINER** —
  which is the same motion as `covered/uncovered` → `+inline` → `+tailed/dispatch_only`, and is
  evidence the taxonomy is converging rather than that it was wrong. **The discriminator is where
  the dispatch GOES:** a delegating `--selftest` names another module's suite; a bare one runs
  nothing. That is statically readable (`attr_reads`, `import_edges`) and is the missing test.

  ⚑⚑ **DO NOT RESOLVE THIS BY WRITING TWO SUITES.** The Ⓝ63⁶ agent's reason stands unrefuted —
  a case over `md_spans_show` would either duplicate `md_spans_selftest` or assert that a
  passthrough passes through, and *"writing a vacuous suite to move a number is worse than
  leaving the module uncovered."* **A census category is not an instruction; it is a reading,
  and this one currently over-reports.** Ⓝ69a″: distinguish DELEGATES (dispatch resolves to
  another module's suite — covered at the far end) from BARE (dispatch runs nothing — genuinely
  owed).

* ⚑ **AND THE DENOMINATOR MOVED AGAIN MID-MEASUREMENT: 147 → 148**, with `file_mode.py` — the
  Ⓝ72a agent's new module — appearing in the uncovered list seconds after being written. **A
  coverage ratio taken while three agents are landing modules is not comparable to one taken ten
  minutes earlier**; only named membership is. Recorded because I have now watched this
  denominator move five times in one session, and every ratio I quoted was true only at the
  instant it was read.
* ✅ ⚑⚑⚑ **Ⓝ68a′ ⟡gate-the-order — CLOSED, AND FALSIFIABILITY WAS PROVED BY MUTATION RATHER THAN
  ASSERTED.** `ratchet_suites` gained `member_edges(root)` and `inversions(root)`; `ORDER` stays
  hand-typed (dependency order is a judgement) but its CONSEQUENCE is now checked —
  **underivable ≠ unverifiable**, which is the distinction the comment now records.

      wrong prefix (`substrate.` → `substrates.`, computes NO edges)   12/13, only the
                                                                       known-inverted arm red
      reversed comparison (sees edges, judges direction backwards)      10/13, three arms red

  ⚑⚑ **THE FIRST MUTATION IS THE ONE THAT MATTERS: an implementation computing NO edges passed
  both no-inversion arms AND the live-tree zero** — exactly the indistinguishability a
  positive-only assertion cannot see. Only the fixture with a KNOWN-INVERTED dependency caught
  it. ⚑ And the second mutation **proves the live zero is a READ, not an empty computation**: it
  printed the tree's real edges (`ratchet_core→baseline_io`, `ratchet_core→ratchet_render`,
  `ratchet_flags→ratchet_log`). Deferred imports excluded — pinned by its own arm — since they
  are not load-order constraints. Composer suite 9 → **13/13**, `ratchet: 9/9` intact.

* ✅ ⚑⚑⚑ **Ⓝ69a ⟡inline-spans-two-shapes — CLOSED AS FOUR SHAPES, NOT TWO, AND MY MID-TASK
  CORRECTION WAS A REAL DEFECT RATHER THAN A READING.** `tailed` (owes a SPLIT) · `dispatch_only`
  (owes a NEW SUITE) · `delegating` (owes NOTHING — forwards to the suite of the reader it wraps)
  · `inline` kept as their union so no existing consumer silently changes meaning.
  `has_inline_suite` became `TAIL_SUITE`, **anchored at column zero, so the census and
  `module_trim` agree on what a tail IS** — a substring test would match a call, a nested def, or
  a docstring word, and point at work no tool can perform.

  **The census and the previous wave's JUDGEMENT now agree:** `kind_partition_show` and
  `md_spans_show` read as **delegating, owed nothing**, where an hour earlier the same census
  called them *"owed a NEW SUITE"* and the Ⓝ63⁶ agent called them *"owed none"*. No vacuous
  suites written. **143/148, three uncovered.**

  ⚑⚑⚑ **AND THE AGENT'S FIRST CUT OF `delegates_to` WAS WRONG IN THE WAY THE CENSUS HIDES.** It
  used `deferred_dotted` alone, reasoning that a `__main__`-guarded import is not module-level.
  **It is** — `import_edges._eager_bodies` descends `ast.If` bodies — so both live delegators kept
  reading as bare dispatches, PLAUSIBLY. A wrong predicate over a real population produces a
  plausible list, which is why the fix is pinned by an arm asserting a guarded forward AND a
  function-body forward from both sides.

  ⚑ **A PARTITION ARM WAS ADDED BECAUSE FOUR CATEGORIES CAN DO WHAT TWO CANNOT:** the denominator
  is computed by SUMMING them, so a module counted twice inflates the total and one counted
  nowhere vanishes from a census whose whole purpose is that nothing vanishes. **Neither shows up
  as an error — both just move a number.** Asserted over a directory holding one of every shape
  at once, since a leak that only appears when they coexist is invisible to per-shape arms.
  `suite_gap_selftest` 20 → **44/44**.

* ✅ ⚑⚑⚑ **Ⓝ63⁗′ ⟡the-dispatch-block-is-tail — CLOSED. 53/53 → 78/78.** The block is identified
  on the `Comparison` NODE'S STRUCTURE (operator plus both operands), never on source text —
  **a substring test would accept `if __name__ != "__main__"`, which is the OPPOSITE block.**
  `names_used` counts an attribute's BASE (`sys` from `sys.exit`) and not its LEAF, because no
  top-level def named `exit` exists to strand.

  ⚑⚑ **THE REFUSAL IS THE CONSERVATIVE HALF, ASKED IN THE DIRECTION THAT CAN REFUSE:** a guard
  referencing any definition that SURVIVES the trim is a module whose CLI outlives its cases, and
  taking it would **silently delete the entry point — the file still imports, still lints, and
  simply stops being runnable.** UNSAFE naming the survivor, BEFORE the checker, so the reader
  gets the cause instead of the F821 symptom.

  ⚑⚑⚑ **AND MUTATION 3 IS THE LOAD-BEARING RESULT: dropping the block instead of EXTRACTING it
  was caught by the PRE-EXISTING conservation guard, unaided, naming both vanished lines.** That
  is evidence the block is partitioned rather than exempted — not an assertion of it. An
  exemption would have re-opened the hole the both-baselines rule was written to close.


* ⚑⚑⚑ **Ⓝ73′ ⟡scope-pytest-migration — A REFUSAL THAT EARNS IT: "DO NOT ATTEMPT THIS AS ONE ARC,"
  AND THE SEAM IS NOT WHERE THE RULING ASSUMED.** The `--selftest` protocol is **not a bespoke
  reinvention of pytest** — it is *"pytest PLUS a memory-lease scheduler, a cross-process mutex, a
  dependency supplier, and a reach ratchet. Converting it wholesale trades a working instrument
  for a standard one that measures LESS."*

  ⚑ **THE INVENTORY WAS 5 MECHANISMS IN MY BRIEF AND IS ~15 MODULES** — `run_selftests.py` is no
  longer a runner at all but a DISPATCH TABLE over the fleet extracted under ⟡retire-the-runner,
  plus **49 path literals across 27 files** naming it. Two Phase-A gates, not one: `selftest roster
  current` AND `tool selftests`.

* ⚑⚑⚑ **THE MEASURED CONVERSION PRODUCED THE FINDING THAT DECIDES THE ARC, AND I VERIFIED IT BOTH
  WAYS. `"tests/*" = ["S101"]` IS PATH-KEYED, SO THERE IS NO INTERMEDIATE LOCATION WHERE A
  CONVERTED SUITE LINTS.**

      pycheck_show tests/test_import_edge_agreement.py   →  CLEAN
      Write substrate/zz_probe_assert.py  (one bare `assert`)  →  REFUSED, S101

  **Conversion and RELOCATION are one atomic act.** So the per-suite cost is not the body rewrite
  (which is cheap and mechanical — `out.append(...); return 1` → `assert`, `try/except/else` →
  `pytest.raises`, and the `_ARMS` tuple plus hand-summed `_CASE_COUNT` **delete outright**). It is
  a `Write` + `git mv` + sibling deletion + `Selftest.mk` regeneration + a `reach_baseline` row
  retirement, **and it does not BATCH, because each move changes the discovery roster the two
  gates read.**

  ⚑ The agent converted a scratchpad FIXTURE rather than a live suite — *"correct under three
  concurrent agents, and the fixture answered the question anyway."*

* ⚑⚑⚑ **AND THE RISK I BRIEFED DOES NOT EXIST, WHILE ITS INVERSE DOES — I VERIFIED:
  `pyproject.toml:271` is `files = ["substrate"]`, so `tests/` IS NOT TYPE-CHECKED AT ALL.**
  I asked about *"conftest.py plus strict mypy over a test tree, which nobody here has done."*
  **The real hazard is that moving ~300 suites INTO `tests/` moves them OUT of type coverage** —
  *"a coverage REGRESSION wearing the uniform of a migration."*

  ⚑⚑ **A destination chosen for one exemption inherits every other property of that destination**,
  and the exemption is exactly what makes the destination attractive. *The `S101` glob and the
  mypy `files` scope are two path-keyed policies pointing opposite ways at the same directory.*

  ⚑ **AND `tests/__init__.py` MUTATES `sys.path`** — inserting `scratch/` and `scripts/`, *"which
  is precisely what the operator refused on 2026-08-31: 'NOO. No sys.path modification.'"* Growing
  `tests/` from 10 to ~310 files **scales an already-refused pattern by 30×.** pytest's
  rootdir/conftest mechanism fixes it — *"which is an argument FOR, but it must be done FIRST, not
  discovered mid-arc."*

* ⚑⚑⚑ **FOUR CAPABILITIES WITH NO PYTEST ANALOGUE, EACH A MEASURED INCIDENT HERE:**

      reach_ratchet     catches DENOMINATOR loss — a suite that still CONTAINS its cases and
                        silently stopped REACHING them, printing a green N/N. ⚑ pytest's count is
                        not ratcheted against a recorded baseline. "The crown jewel."
      suite_claims      a CROSS-PROCESS EXCLUSIVE LOCK on `pg`/`roster` via membudget's label.
                        Its docstring: "ENOUGH CONCURRENCY THROWN AT THE POSTGRES BACKEND CAUSED
                        KERNEL HANGS." ⚑ xdist does not do this.
      suite_command     the per-suite membudget cgroup lease — `items.py --selftest` went from
                        OOM-KILLED to passing inside a 192MB lease.
      suite_pragmas     `requires:` + `uv run --with` — an absent dep once scored as a
                        PASS-SHAPED SKIP; `jea_circuit` returned True on "SKIP (numpy absent)"
                        and actually runs 300/300.

  **Each would need a plugin written and PROVEN before a single suite moves.**

* ⚑⚑ **THE SEAM, AND IT IS A BOUNDED ARC WITH A REAL PAYOFF: STOP AFTER `tests/`.** Migrate the 10
  unittest files, install and DECLARE pytest (*"`pyproject.toml` records twice that a dependency
  named only in prose is a permission slip, not a declaration"* — and pytest is currently neither
  installed nor declared), add `conftest.py`, retire `tests/__init__.py`'s `sys.path` insert.
  **That resolves the PT009 refusal actively blocking today, kills an already-refused pattern, and
  builds every piece of infrastructure the larger migration would need — then judge the ~300 from
  there.**

  ⚑ **ORDER MATTERS AND THE GATE IS NOT THE HARD PART:** `selftest_mk --check` compares RENDERED
  TEXT and `reach_ratchet` carries forward absent rows rather than banking zeros, so **the gate
  degrades honestly.** Per suite: write at `tests/`, delete sibling, regenerate, run both gates —
  *"roster shrinks by one, pytest grows by one, NEITHER IS EVER EMPTY."* `run_selftests.py`
  retires LAST, after the 49 literals.

* ⚑⚑ **COMPOSITION WITH Ⓝ86 — AGREED FROM BOTH SIDES, WITH A CORRECTION THAT SPLITS THE
  POPULATION.** Every suite trailer is `sys.exit(selftest() if "--selftest" in sys.argv …)`, and
  pytest owns collection — so **~300 readers are retired WHOLESALE by this migration and Ⓝ86 must
  NOT convert them.** ⚑ But the reduction is not total: **`suite_pragmas` reads `--sandbox`/`--live`
  TENANT FLAGS off the same trailer** and `suite_command` appends them to argv. Those become
  markers/fixtures, **not deletions.** So Ⓝ86's correct scope is the NON-SUITE readers — the CLIs
  and gates — and the ~300 trailers are owned by this arc.
