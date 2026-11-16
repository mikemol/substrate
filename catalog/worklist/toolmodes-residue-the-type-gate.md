# Ⓝ31 residue — the type gate

**Concern: what the mypy gate actually measures, the scope mismatch that made it measure the
wrong thing, and the sanctioned boundary that does not exist.** Index and arc
frame: [`toolmodes-split.md`](toolmodes-split.md).

⚑⚑ **Ⓝ32a′ ⟡the-jea-any-subtree IS THE APEX: THE GATE WAS APPLYING THE PROMOTED-FRONTIER BAR TO
THREE UNPROMOTED TREES**, and the discriminator is that `substrate/` scores zero under the
identical config. `files` bounds DISCOVERY, not an explicit path list — so a stated policy was
defeated by a scope the statement did not mention. *A stated policy governs the mechanism it
names.*

⚑ Ⓝ61 built the summary and found the key count understated the debt 40× (1,133 keys, 45,035
messages). Ⓝ84 ⟡the-sanctioned-boundary-does-not-EXIST is the sharper one: every refused `.py`
edit in this repo cites `check_ignore_holder.py`, which is absent — including every refusal in
this session, and every agent brief that quoted it.

⚑ Ⓝ32a corrects the same EMPTY-is-not-ABSENT misreading that Ⓝ73 corrects one gate over, in
[gates, types, budgets](toolmodes-residue-gates-types-budgets.md); read them together.

## Residue

* ✅ ⚑⚑⚑ **Ⓝ32a′ ⟡the-jea-any-subtree — DISSOLVED, NOT PAID DOWN. IT IS A CONFIG SCOPE MISMATCH,
  AND THE DISCRIMINATOR IS THAT `substrate/` SCORES ZERO UNDER THE IDENTICAL CONFIG.** Verified by
  me (`type_census_summary --roots` / `--codes`):

      jea 24095 (53.5%) · scripts 15358 (34.1%) · el-atlas 5582 (12.4%) · substrate 0 (0.0%)
      misc 36337 (80.7%) · no-untyped-call 5179 · no-untyped-def 2355   → 97.4% ANNOTATION COVERAGE
      arg-type 66 · attr-defined 47 · union-attr 25 · used-before-def 3 → ~230, 0.5% DEFECTS

  **So it is not "jea is dirty" — it is the PROMOTED-FRONTIER BAR APPLIED TO THREE UNPROMOTED
  TREES.** `pyproject.toml [tool.mypy]` sets `disallow_any_expr = true` scoped by
  `files = ["substrate"]`, deliberately, with a comment that a file is checkable to this bar only
  once its IMPORT CLOSURE is. But `mypy_census._run` passes explicit paths with no
  `--config-file`, so mypy auto-discovers the strict block and applies it to whatever it is
  HANDED — and `type_gate.census` hands it `promoted.POPULATION` = jea, el-atlas, substrate,
  scripts. ⚑ **`files` bounds DISCOVERY, not an explicit path list.**

  ⚑⚑⚑ **AND `type_gate.py`'s OWN DOCSTRING FORBIDS EXACTLY WHAT HAPPENED:** *"⚑ WHAT THIS GATE IS
  NOT: an annotation-coverage push… Adding a stricter flag would convert a defect census into an
  annotation census and bank hundreds of keys that are not the policy."* **It happened without
  anyone adding a flag** — the policy was stated, correct, and defeated by a scope the statement
  did not mention. *A stated policy governs the mechanism it names.*

  ⚑ **NEITHER "legitimate boundary" NOR "accumulated debt" — the operator-decidable framing is
  THE SAME BAR IN THE WRONG SCOPE.** Two cheap options: scope `mypy_census._FLAGS` with an
  explicit `--config-file`/per-root strictness, or narrow the gate's population to match `files`.
  ⚑ **No paydown is even POSSIBLE while population and config disagree** — typing `jea/` to
  `disallow_any_expr` is the whole migration, not a cleanup. Concentration confirms it: top file
  2.9%, top 15 = 30%, 284 files. **Uniform — no root-cause cluster to cut.**

* ✅ ⚑⚑ **Ⓝ61 ⟡type-gate-needs-a-summary — BUILT (`substrate/type_census_summary.py` + suite
  18/18), AND THE KEY COUNT UNDERSTATED THE DEBT 40×.** 1,133 keys stand for **45,035 messages** —
  a key is a `(code, file)` pair and one file carries up to 1,296. Every figure I quoted all
  session (1,154 / 1,145 / 1,133) was the wrong order of magnitude for the thing being discussed.

  ⚑ **THE DISCRIMINATOR ARM IS THE LOAD-BEARING ONE:** a fixture where key-weighting and
  message-weighting DISAGREE (`misc` 2 keys/210 msgs vs `arg-type` 4 keys/4 msgs). **The natural
  first cut — counting keys — renders identically and ranks them BACKWARDS.** ⚑ `mypy_census` had
  no summary capability to wire (3 defs), so this is a build, not a rebuild — checked before
  writing. Reuses `type_errors` rather than re-taking the census, and propagates `UNRUNNABLE` as
  a refusal (exit 2) rather than an empty summary.

* ⚑⚑ **Ⓝ32a ⟡type-gate-broken — NOT BROKEN. THIRD TIME THIS SESSION THIS MISREADING WAS TESTED
  AND REFUSED.** `mypy_ratchet_baseline.txt` is **EMPTY (0 keys)** — zero-tolerance, the strongest
  setting — so `BROKEN — 1133 NEW` is the correct rendering of unpaid debt. ⚑ Repo-wide there are
  now **0 ABSENT baselines** (8 ok · 11 EMPTY · 1 UNREAD), so this gate has STRENGTHENED — and
  `gate_census.py`'s own docstring still says this baseline *"DOES NOT EXIST"* and exits 0, which
  was the free-pass state and is **now stale in the file that teaches the distinction.**

* ⚑⚑⚑ **Ⓝ84 ⟡the-sanctioned-boundary-does-not-EXIST — AND EVERY REFUSED EDIT CITES IT.**
  `scripts/check_ignore_holder.py` is **ABSENT, with no successor** (confirmed independently by
  the `gate-oracle`, filed `gate-F48`/`gate-F49`) — while `scripts/pycheck_message.py:139` names
  it in the DENY MESSAGE. **So every refused `.py` edit routes its author to a gate that is not
  there.** The agent hit it live: *"every one of my own refusals printed that citation."*

  ⚑ I have quoted that boundary in **every agent brief this session** — *"the ONE sanctioned
  exception is the numpy `Any` boundary, gated by `check_ignore_holder.py` (sole-holder +
  fixed-count)"* — copied from the hook's own text and never checked. **The real constraints are
  `warn_unused_ignores` (self-prunes, bounds no count) and the hook itself; nothing enumerates
  holders or fixes a count.** ⚑⚑ And it overturns a ledger entry: `gate-F45` claimed the
  pre-commit gate could not emit `Expression has type "Any"`. **It is 44% of the census.**

* ⚑ **Ⓝ84a — AND ONE FLAGGED LOOSE END WAS A FALSE ABSENCE I CAUGHT BY RUNNING IT.** The agent
  reported *"`substrate/type_gate_verdict.py` does not exist — but its suite does, and
  `run_selftests --list` discovers it. A suite without its module."* I ran the suite: **4/4, and
  it exercises the real verdict paths** (NEW-key refusal, paydown preview, no-baseline remedy).
  The module is not missing; the verdict logic lives elsewhere and the suite reaches it. ⚑ The
  agent was right to flag rather than investigate — out of its scope — **but recording it as
  written would have banked a seventh false absence.** *One command settles a claim about a
  module.*

  ⚑ Also measured: `uv run --with mypy` FAILS (`paperkit` unresolvable in the registry), so **the
  gate's own printed remedy is currently broken**; the plain interpreter with mypy 2.3.0 works.


* ⚑⚑⚑ **Ⓝ32a″ ⟡jea-is-not-exempt — THE OPERATOR NAMED A THIRD OPTION NEITHER THE AGENT NOR I
  CONSIDERED, AND BOTH OF OURS WERE THE SAME MOVE.** Operator, 2026-09-02: *"The jea stuff needs
  cleanup and n-split just like anything else."*

  The agent offered two: **scope `mypy_census._FLAGS` with an explicit `--config-file`**, or
  **narrow the gate's population to match `files = ["substrate"]`**. I relayed both as *"cheap,
  operator-decidable."* ⚑⚑ **They are the same move wearing two spellings — EXEMPT `jea/` FROM THE
  BAR.** One does it at the flag, one at the population; neither changes a line of `jea/`. **A
  scope fix and a population fix are one option, not two**, and presenting them as a choice made
  the exemption look like a decision space rather than a single direction.

  ⚑⚑⚑ **AND THE "97.4% IS ANNOTATION COVERAGE, NOT DEFECTS" FRAMING WAS DOING WORK IT SHOULD NOT
  HAVE.** It is true — `misc` + `no-untyped-call` + `no-untyped-def` dominate, defect-shaped codes
  are ~230 of 45,035 — and I read *not defects* as *not owed.* **Missing annotations ARE the debt
  when the destination is promotion.** `pyproject.toml`'s own comment says a file is checkable to
  this bar once its IMPORT CLOSURE is; that is a description of the ROUTE, not a permanent fence.
  The bar is right and `jea/` should meet it.

  ⚑ **SO Ⓝ32a′ IS NOT A CONFIG QUESTION — IT IS THE SAME WORK AS EVERY OTHER DRAIN THIS SESSION.**
  n-split, single responsibility, the per-file gate at the moment of edit. `substrate/` scores 0
  across all 25 codes under the identical config **because it went through this**; `jea/` scores
  24,095 because it has not. **The zero is the existence proof that the bar is meetable**, not
  evidence the bar is misapplied — and I had that measurement in hand and drew the opposite
  conclusion from it.

  ⚑⚑ **THE SHAPE, AND IT IS THE SESSION'S RECURRING ONE:** a gate fires, the reflex is to ask
  what is wrong with the GATE. `the-per-file-gate-is-a-design-signal` says a gate that keeps
  firing means the UNIT is wrong — **decompose to match its grain, never raise/exempt/route
  around it.** I quoted that memory today about `run_selftests.py` and did not apply it to the
  45,035-message census in front of me, because the census was large enough to read as a fact
  about the instrument.

  ⚑ **WHAT DOES NOT CHANGE: `mypy_census` still applies the strict block to whatever it is
  HANDED**, because `files` bounds DISCOVERY, not an explicit path list. That mechanism is
  correctly diagnosed and is not a defect under this ruling — it is the gate reaching the trees
  the promotion arc will drain. **Ⓝ32a‴: the paydown is per-file and per-concern, and its unit is
  the same one n-splitting already uses.**


* ⚑⚑⚑ **Ⓝ32a‴ ⟡jea-is-not-exempt — A REASONED REFUSAL WITH A MEASURED CLOSURE BOUNDARY, AND IT
  INVERTS THE DRAIN PLAN. NO `jea/metalanguage/` FILE CAN REACH ZERO TODAY, AND THE BLOCKER IS NOT
  ANNOTATION DEBT.** The agent took `dump_agdai_pyast.py` (3 defs, ~45 lines, 2 sibling imports,
  no static importers) from **37 ruff findings to 0** and still could not land it. Verified by me:
  `git diff --stat` → **0 insertions, 0 deletions**; no half-drained file left behind.

  **TWO BLOCKERS, BOTH DIRECTORY-SCOPED, NEITHER IN ANY FILE:**

  ⚑⚑ **(1) THE GATE'S MYPY CANNOT RESOLVE SIBLING IMPORTS IN `jea/metalanguage/`.**
  `scripts/pycheck_checkers.py` invokes mypy with **only** `--config-file pyproject.toml` — no
  `--ignore-missing-imports`, no `--explicit-package-bases` (I read the argv myself). Every file
  there reaches its siblings through a runtime `sys.path.insert(...)`, and **`find jea -name
  __init__.py` returns NOTHING** (I ran it). So `import jea_pyalg` is `import-not-found`, which
  makes `Intern` `Any`, which makes every downstream expression `Any`. `--explicit-package-bases`
  does not help — the agent ran it.

  ⚑⚑⚑ **SO THE GATE'S BAR IS STRICTLY HARSHER THAN THE CENSUS'S, AND THE 24,095 FIGURE IS
  MEASURED UNDER THE LENIENT ONE.** `substrate/mypy_census._FLAGS` carries both flags; the pycheck
  hook carries neither. **A file that reaches zero on the census can still be refused by the
  gate** — so every per-file estimate this arc has made, mine included, is against the wrong
  instrument.

  ⚑⚑ **(2) `jea_pyalg.IR` TAINTS `type[IR]`, AND THE FIX IS UNREACHABLE.** `IR` is a frozen
  dataclass with bare `children: tuple` / `payload: tuple`; the taint flows through
  `Intern.nodes: list[IR]` into every consumer. **The fix is two characters** (`tuple[int, ...]`,
  `tuple[str, ...]`) — and `jea_pyalg.py` carries ~282 ruff findings, so pycheck refuses any edit
  to it. **A two-character fix behind a 282-finding wall**, which is `Ⓝ71`'s shape exactly, one
  tree over. Same for `schema_decl.py` (SQLAlchemy `Column[Any]` throughout).

* ⚑⚑⚑ **AND THE ANSWER TO "was n-splitting required?" IS NEITHER REQUIRED NOR AVAILABLE — WHICH IS
  THE MOST IMPORTANT FINDING.** `dump_agdai_pyast.py` does exactly one thing. **The `Any`s are not
  structural-within-the-file; they are IMPORTED.** Splitting it yields two clean-shaped files that
  both still fail, because both still import `jea_pyalg`.

  ⚑ **SO THE PER-FILE GATE'S USUAL ADVICE — *"extract the concern into a new clean module"* — DOES
  NOT APPLY HERE, BECAUSE THE DEBT IS NOT IN THE FILE.** Every drain this session succeeded by
  that route (`run_selftests`, the six inline tails, `record_migrate`). This is the first one
  where it is provably the wrong instrument, and knowing that BEFORE 283 more files is the whole
  value of the dispatch.

  ⚑⚑ **THE ONE CHANGE THAT UNBLOCKS IT IS STRUCTURAL, NOT A CODEMOD: make `jea/` and
  `jea/metalanguage/` real packages** (`__init__.py`, relative imports replacing the `sys.path`
  prologues). It clears `INP001` for the ~14 library-only files **whose VIRTUE — having no
  `__main__` — currently blocks them**, and makes sibling imports resolvable by the gate's bare
  mypy, *converting the directory from BLOCKED to ordinary annotation work.*

  ⚑ **AND IT NEEDS THE `sql-oracle`'s VIEW BEFORE IT LANDS:** `jea/metalanguage/` has duplicate
  basenames against other trees (`schema.py`, `store.py`, `lifecycle.py`, `reconstruct.py`) —
  which is precisely why the census needs `--explicit-package-bases` — so **making it a package
  changes module identity tree-wide**, across the compiled-query and store layer.

* ⚑⚑ **Ⓝ32a⁗ ⟡the-gate-and-the-census-disagree — AND `pycheck_checkers.py` ALREADY RECORDS THE
  MECHANISM I ASKED A PEER TO FIND A CITATION FOR.** Line 63, measured with a POSITIVE CONTROL:
  ***"`files` names the DEFAULT TARGET when mypy is given no path; it does not filter what a named
  path is checked as."*** A file containing `X: int = "not an int"` placed OUTSIDE the repo
  entirely is still reported `[assignment]`.

  ⚑ I dispatched a research request to `linux-sources` asking for the documented sentence behind
  exactly this behaviour, while our own hook carried a measurement of it with a control. **The
  citation would have been weaker than the evidence already in the tree** — and I did not look,
  because the question felt like an upstream-docs question rather than a local one. *A behaviour
  measured with a positive control beats a doc paragraph, and we had one.*

  ⚑ **Ⓝ32a⁵ ⟡scoped-per-file-type-read — the missing mode the agent named:** `type_gate` IGNORES
  its path argument and always runs the full tree; `type_census_summary --files` reports
  whole-corpus attribution. **Neither separates a target's OWN messages from its CLOSURE's**,
  which is the exact distinction this refusal turned on. A `--file <path>` mode would pay for
  itself immediately; the agent left a working probe in the scratchpad rather than promoting it
  unasked.


* ⚑⚑⚑ **Ⓝ87 ⟡packaging-CREATES-identity — THE `sql-oracle` CAUTION WAS A NON-QUESTION, AND I
  RELAYED IT WITHOUT TESTING IT.** Operator: *"Of course make jea a real package. All of the
  python stuff should be real packages. It dramatically simplifies **everything**. What's the
  question about sql-oracle?"*

  **There was no question.** The Ⓝ32a‴ agent flagged that `jea/metalanguage/` has duplicate
  basenames against other trees (`schema.py`, `store.py`, `lifecycle.py`, `reconstruct.py`) so
  *"making the directory a real package changes module identity tree-wide"* and *"wants the
  `sql-oracle`'s view before it lands."* I passed that through as a blocker. ⚑ **It cuts the other
  way: those duplicate basenames are exactly WHY identity is currently ambiguous.** Packaging does
  not endanger identity — **it creates it.** `jea.metalanguage.schema` becomes distinguishable
  from every other `schema`, instead of colliding on `sys.path` order.

  ⚑⚑ **AND THE COLLISION IS MEASURABLE TODAY.** `module_importers schema`:

      ⚑ the bare name `schema` resolved to `jea.metalanguage.schema`
      jea.metalanguage.schema: 0 import site(s) in 0 of 1191 file(s)
        ⚑ 8 shape(s) this reader CANNOT resolve …
          re-export-chain: jea/metalanguage/schema_selftest.py:41 re-exports `schema` with a
          star; consumers reach it under THIS module's name and name it nowhere

  **The reader resolves a bare name to ONE module and reports ZERO sites for a module the store
  layer demonstrably uses**, because every consumer arrives through a `sys.path.insert` prologue
  no static reader can follow. **The import graph for the compiled-query and store layer is
  currently UNREADABLE**, and the packaging change is what makes it readable — the opposite of
  the risk as I relayed it.

  ⚑ **THE ZERO NAMED ITS BOUNDS, WHICH IS WHY THIS WAS ANSWERABLE IN ONE COMMAND** rather than
  requiring an oracle dispatch. Ⓝ68b's `unresolved()` reported the `re-export-chain` and the seven
  dynamic imports, so the zero read as *"this reader cannot see the edges"* instead of *"nothing
  imports it."* ⚑⚑ *A caution about a subsystem is still a hypothesis. I have spent this session
  recording that agent reports are hypotheses and then forwarded one as a blocker because it named
  a subsystem I do not own — deference is not verification.*

  ⚑⚑⚑ **AND THE RULING IS GENERAL, NOT LOCAL: ALL OF THE PYTHON SHOULD BE REAL PACKAGES.** That
  retires the framing of several items at once — `INP001` stops being a wall that blocks a whole
  directory (Ⓝ76 measured `scratch/` admitting no new `.py` file; the answer is not *route around
  it* but *make it a package*), the gate's mypy stops needing `--explicit-package-bases` to
  disambiguate basenames, and sibling imports become resolvable **so a leaf file's annotations can
  actually reach it** — which is the entire Ⓝ32a‴ closure boundary. *One structural change
  dissolves a blocker in three separate items, which is what "simplifies everything" means
  concretely.*


* ⚑⚑⚑ **Ⓝ87a ⟡packaging-is-not-the-blocker — THE AGENT STOPPED BEFORE WRITING ANYTHING AND
  FALSIFIED MY BRIEF'S CENTRAL PREMISE. TREE UNMODIFIED.** I briefed: the gate's mypy sees
  `import jea_pyalg` as `import-not-found` → `Any` → everything downstream `Any`, so `__init__.py`
  plus real imports unblocks the leaf. **Verified by me, `type_census_summary --codes 25`:**

      import-not-found  →  ABSENT. Zero of 45,035 messages. Not among the 25 codes.
      misc 36337 (80.7%) · no-untyped-call 5179 · no-untyped-def 2355   → 97.4% MISSING ANNOTATIONS

  ⚑⚑ **THE `Any` CASCADE IS REAL AND ITS ORIGIN IS `disallow_any_expr = true` MEETING UNANNOTATED
  FUNCTION BOUNDARIES — WHICH PACKAGING DOES NOT TOUCH.** Confirmed on the file I pointed at:
  `jea/metalanguage/sorted_stream.py` imports **stdlib only** (`0 of 7 undeclared or missing`), so
  its `sys.path.insert` at lines 41/649 imports NOTHING. Running the gate's exact mypy invocation
  yields hundreds of errors, **every one `Function is missing a type annotation` /
  `Expression has type "Any"` / `Missing type arguments`. Not one import-related.** Adding
  `__init__.py` and deleting the dead prologue would change its count **by zero**.

  ⚑⚑⚑ **AND I FUSED TWO SEPARATE DEFECTS INTO ONE CAUSAL STORY.** `module_importers schema` → 0
  sites IS a real readability defect, correctly reported, with its bounds named. **It is simply
  not the thing gating the type errors** — and my acceptance criterion rested on the half that was
  invented. *A true observation plus a true observation does not make a mechanism*, and I built a
  dispatch on the join.

* ⚑⚑⚑ **Ⓝ87b ⟡retiring-an-injection-SURFACES-findings — AND `pyproject.toml` ALREADY CARRIES THE
  PEER MEASUREMENT.** From paperkit, in the `packages` block I never read:

      boundaries_ladder     3 own findings  →  231 with paperkit/grade.py followed
      boundaries_without_k  0 own findings  →  312 with _fixture_model.py followed

  Its stated conclusion: **"Type the callee, verify it clean, then name it."** ⚑ **Retiring an
  injection does not REDUCE findings — it SURFACES them onto the declaring file**, and under
  zero-tolerance that converts a silent hole into a BLOCKED EDIT. **Packaging `jea/metalanguage/`
  first would make ~130 files newly followable and land tens of thousands of `Any` errors onto
  whichever file declares the import, with no path to landing any of them.** *My plan's first act
  would have been its own worst outcome, and the repo had measured it in advance.*

  ⚑ **AND THE ORDER IS INVERTED FROM WHAT I DISPATCHED:** I said *start at `jea/metalanguage/`, it
  is the measured blocker.* It is the **WIDEST** tree (24,095 msgs, 53.5%) — **the worst possible
  place to start a leaves-inward walk.** Packaging must FOLLOW annotation, not precede it:
  **(1)** annotate a stdlib-only leaf to zero under `disallow_any_expr` — bounded, needs no
  packaging; **(2)** promote it via `check_scratch_independence`'s predicate or `mypy.files`;
  **(3)** package only once a tree's leaves are clean, when naming the imports surfaces nothing.

* ⚑⚑ **Ⓝ87c ⟡scratch-must-NOT-be-packaged — AND THE REASON IS MECHANIZED, NOT DEFERENTIAL.** I
  asked for an argument either way and got the one that settles it: **`check_scratch_independence`
  (Λ8) IS the predicate "residence in `scratch/` means not-yet-promoted."** Packaging it would
  make that gate's invariant **unstatable** and cement the staging area as permanent. ⚑ **So
  `INP001` in `scratch/` is the policy working as designed, not a wall to route around** — which
  reverses how I have framed Ⓝ76 all session. *`substrate/` is the destination; modules promote
  one at a time through the gate that owns the predicate.*

  ⚑ **`substrate/` and `scripts/` are ALREADY real packages** (`__init__.py` present, declared) —
  so "make the Python stuff real packages" is already true where it has been earned, and the
  remaining trees are the ones that have not yet done the annotation work that makes it safe.

* ⚑ **AND THE AGENT BOUNDED ITS OWN CLAIM RATHER THAN OVERSTATING IT:** *"I verified the
  import-error claim against the census and against one leaf run directly. I did not exhaustively
  re-run mypy over all ~130 files, so I can say `import-not-found` is absent from the census the
  gate's own tooling produces — I cannot say no individual invocation anywhere produces one."*
  **That is the distinction between a census result and a universal**, stated unprompted, in the
  report that overturns a dispatch. ⚑ My own check adds one datum it did not have:
  `sorted_stream.py` carries **20 defs and a 227-line inline `_selftest`** — so the annotation
  candidate also holds the tail debt the six-module split retired. **Ⓝ87d: the leaf wants
  splitting and annotating, and the order between those is not obvious.**


* ✅ ⚑⚑⚑ **Ⓝ32a⁵ ⟡scoped-per-file-type-read — BUILT (`substrate/type_scope.py`, 14/14), AND THE
  PROBE I POINTED AT COULD NOT HAVE ANSWERED THE QUESTION.** The agent read it before writing and
  reported why: *"mypy given ONE path reports messages only for that path, so the probe's TARGET
  vs other split was always 100% TARGET."* **The shape was right and the mechanism was
  impossible** — and I had recommended promoting it as *"one tool improvement that would pay for
  itself immediately."*

  ⚑⚑ **THE WORKING MECHANISM IS A DIFFERENTIAL: TWO mypy RUNS OVER THE SAME FILE, IDENTICAL BUT
  FOR `--follow-imports`.** Three arms, and the third is the design:

      OWN                  in BOTH arms — does not depend on the closure; SURVIVES a drain
      CLOSURE-INDUCED      `normal` only — a followed import brought an untyped value in;
                           this is what a drain REMOVES
      CLOSURE-SUPPRESSED   `skip` only — the closure's REAL types PREVENT it

  ⚑ **The third arm is held explicitly *"so `induced` is never computed as a difference of
  totals"*** — and I verified why that matters: `substrate/type_census_summary.py` reads **0 OWN,
  0 INDUCED, 13 SUPPRESSED.** *A difference-of-totals design shows nothing there while the closure
  is actively preventing 13 messages.*

  ⚑ **AND MULTISET, NOT SET, IS LOAD-BEARING**: 80.7% of corpus messages share one code and a
  handful of texts, so **a set diff would report almost every file as entirely self-owned.**
  That is a discriminator case in the suite, not a note.

* ⚑⚑⚑ **THE LIVE READING CORRECTS A DRAIN PREMISE — VERIFIED BY ME.**
  `type_scope jea/metalanguage/sql_lift.py` → **722 OWN, 3 CLOSURE-INDUCED, 1 SUPPRESSED.** The
  induced three are `Column[Any]`, `ReadOnlyColumnCollection[…]`, `Select[tuple[Any]]` —
  SQLAlchemy, a followable TYPED dep. **A drain moves 3 of 725.**

  *That is the reading that would have stopped me proposing packaging as the `jea/` unblock:* the
  closure is barely the problem in that file, and Ⓝ87a already established `import-not-found` is
  absent from the census. **Now there is a per-file instrument to say so before the work, not
  after.**

  ⚑ **AND A THIRD READING IS A BLIND SPOT FIRING, REPORTED AS SUCH:** `scripts/sppf_tree.py` →
  822 OWN, 0 induced — *"not a clean result: `scripts/` reaches its deps via `sys.path.insert`, so
  mypy follows nothing in EITHER arm."* **Which is exactly why the blind roster prints on every
  run.**

* ⚑⚑ **ESTABLISHED vs INFERRED IS PRINTED ON EVERY MODE, AND THE REFUSAL IS THE PART THAT
  MATTERS.** The leads rank the induced arm's **error CODES** (measured); the agent **deliberately
  did not rank suspect IMPORTS** — *"mypy names the USE of an `Any`, never its source, and an
  import ranking reads as measured because it names real modules"* — the `record_migrate` failure
  where *the error names the DUMP, not the literal* cost six wrong attributions in a row.

  ⚑ **SO THE ANSWER TO "IS CLOSURE ATTRIBUTION DERIVABLE" IS SPLIT AND BOTH HALVES MATTER:** the
  own/closure PARTITION is derivable **exactly** — *"a real measurement of a real counterfactual
  (what does this file look like with its closure erased), not a proxy."* The finer question —
  *which of my 40 imports caused these 3 messages* — is **not derivable, and the tool refuses to
  guess it.**

  ⚑⚑ **AND THE MECHANISM WAS ALREADY MEASURED HERE FROM THE OPPOSITE DIRECTION**, which the agent
  found in `pyproject.toml`: paperkit converting three suites off `sys.path.insert` saw **3 own
  findings become 231, and 0 become 312**, purely because naming a module made its edge followable.
  **That is this differential with the arms swapped** — the same counterfactual, run by accident,
  a month earlier.

* ⚑ **COST, MEASURED, AND IT SETTLES THE GATE QUESTION ON GROUNDS OTHER THAN SPEED.**

      cold (.mypy_cache removed)   full-tree 82s   per-file 18s
      warm                         full-tree  7s   per-file  6s

  A per-file split costs ~2× a single-file run and **warm is cheaper than the full-tree census**.
  ⚑ *"It is viable interactively and is not disqualified from a gate on cost — but it should not
  BE a gate: it answers a drain-planning question about ONE file, and `type_gate`'s ratchet
  quantifies over the CORPUS. Two different questions, not two speeds."*

  ⚑ **OPERAND HONOURED OR REFUSED, NEVER DISCARDED** — and *"there is deliberately NO no-operand
  form: the tool has nothing to say about a corpus, so an absent operand cannot fall back to
  one."* **The `module_size` defect made structurally impossible rather than fixed.** Both
  refusals verified by running them. `mypy_census_selftest` 4/4; two private names promoted after
  `attr_reads` confirmed no external reader.

  ⚑ Independently noticed and flagged, not touched: **`type_gate` reports all 1132 keys as NEW —
  its baseline is absent or empty**, the ABSENT-vs-EMPTY distinction this session has now recorded
  four times.


* ⚑⚑⚑ **Ⓝ94 ⟡the-networkx-precedent-is-a-retreat — THE OPERATOR CORRECTS THE RECORD, NOT JUST MY
  PLAN.** On `pyproject.toml`'s account of removing `types-networkx`: *"Yeah I don't think that was
  the right move; that was a 'oh shit this propagated and I'm not propagating annotations'."*

  ⚑ **AND I HAVE BEEN QUOTING IT AS PRECEDENT ALL SESSION** — most recently to decline dispatching
  a psycopg stub on my own judgement, on the grounds that *"the obvious approach has a precedent
  against it."* **The precedent is a retreat wearing a doctrine.**

  **WHAT THE RECORD CLAIMS** (`pyproject.toml:37-46`): *"the reason is THIS FILE'S OWN RULE READ
  CORRECTLY: stub an untyped dep (that ADDS types); ignore a typed dep whose types contain `Any`
  at a boundary walled by a concrete return. The published stubs are the second category by
  appearance and the first in fact."*

  ⚑⚑ **THE OBSERVATION IS EXACT AND THE INFERENCE IS NOT.** `DiGraph[T, dict[str, Any], dict[str,
  Any]]` genuinely does make every graph expression `Any` under `disallow_any_expr`, and `cast()`
  genuinely cannot rescue it — *the `Any` is flagged before the cast concretises.* **But
  `dict[str, Any]` in an attribute dict is a REAL untyped surface, and the honest response is
  parameterising it, not withdrawing the types.** A propagation that reaches further than expected
  is the annotation gate WORKING.

* ⚑⚑⚑ **AND THE REPLACEMENT STUB NAMES THE ACTUAL MOVE WITHOUT CALLING IT THAT.** Read
  (`stubs/networkx/__init__.pyi`, 68 lines, four names):

      "⚑⚑ SO THE PARAMETER THAT MATTERS IS DROPPED, NOT THE SURFACE. `DiGraph` here is generic
       over the NODE type ALONE; the attribute-dict parameters are simply ABSENT."
      "⚑ THE `**attr` KEYWORDS ARE DELIBERATELY NOT DECLARED. Accepting them would RE-ADMIT the
       attribute dicts this stub exists to drop."

  **Dropping a type parameter is not ADDING types — it is declining to propagate through it**,
  and the second note says so outright: the stub exists *to drop* a surface. ⚑ *A narrowing
  justified by "this repo never uses them" is a claim about today's callers, which the same file
  elsewhere refuses to make* — its own §18-20 insists signatures be *"READ FROM THE LIBRARY, NOT
  FROM THE CALL SITES… typing only what this repo happens to pass would encode the CALLER's habits
  as the library's contract."* **It applies that principle to the METHOD SIGNATURES and violates it
  on the TYPE PARAMETERS, in one file.**

  ⚑ **THE STUB IS GOOD WORK IN THE PARTS THAT ARE NOT THE RETREAT** — it reads `add_edge` and
  `descendants` from `classes/digraph.py` and `algorithms/dag.py` rather than from call sites, and
  it types `descendants`' **raise** as a contract, making visible that two guards elsewhere are
  *"load-bearing rather than defensive."* **That half should survive whatever replaces it.**

* ⚑⚑ **SO Ⓝ94 ⟡the-psycopg-stub IS UNBLOCKED IN ITS FRAMING, AND THE SHAPE IS THE OPPOSITE OF WHAT
  I ASSUMED.** I was treating *drop the parameter that propagates* as the sanctioned pattern. The
  ruling says the sanctioned pattern is **propagate the annotations** — so a psycopg stub should
  type `dict_row`, `Connection`, `Cursor` and `Error` **through** their generics rather than
  narrowing them away, and accept that the first draft surfaces work rather than hiding it.

  ⚑ **AND THAT REFRAMES Ⓝ92b's WALL.** Its measurement stands — *"no module in `substrate/`
  imports psycopg; `dict_row` and `psycopg.Error` are themselves `Any`-typed"* — but the wall is
  **unpropagated annotations in a dependency**, not a category error in the gate. `store.py`'s 13
  CLOSURE-INDUCED messages all naming psycopg/SQLAlchemy types is the same fact from the other
  side: **the driver's untyped surface, arriving as our debt.**

  ⚑⚑ **Ⓝ94a: THE SAME QUESTION IS OWED OF `stubs/`' OTHER SEVEN ENTRIES** — how many are
  ADDITIONS and how many are NARROWINGS that decline a propagation? *A stub that drops a parameter
  is indistinguishable from one that adds a type, in a census that counts stubs.*

* ⚑⚑⚑ **THE BLOCKER IS NOT SIZE — I FRAMED THIS AS BULK REDUCTION AND IT IS A TYPING BOUNDARY
  PROBLEM.** `pyproject.toml:321` sets **`disallow_any_expr = true`** with `select = ["ALL"]` and
  **no `[[tool.mypy.overrides]]` by design**, so **every untyped boundary poisons every downstream
  expression.** `wg_order.Row` is an untyped `collections.namedtuple` (`wg_order.py:444`), and the
  suite reads `r.key`/`r.layer`/`r.lev` throughout — ***each read is an `Any` expression, so the
  sibling cannot be typed by MOVING code; each row read must be NARROWED AT THE EDGE.***
  Convergence measured: **309 → 96 → 63 → 46 → ruff 0 / mypy 43**, the residue all implicit-`Any`
  from `Callable[..., X]` ellipsis fields, `getattr` results, and `__import__`.

* ⚑⚑ **AND MY "LAND INCREMENTALLY" INSTRUCTION IS UNACHIEVABLE FOR THIS FILE.** I added it after a
  529 killed a prior dispatch mid-analysis. **But the gate is ALL-OR-NOTHING PER FILE, so there is
  no partial write** — *the only workable loop is ITERATE OUTSIDE THE TREE to zero on both tools,
  then WRITE ONCE.* ⚑ A converged draft sits at `/home/mikemol/.tmp/wgwork.py` with 43 mechanical
  narrowings specified but unapplied; **the `.txt` extension is what gets a draft past the hook**,
  since it reverts in-repo `.py` writes *and* writes to the session scratchpad.

  ⚑ **A THIRD CORRECTION, SMALLER: "461-line `_selftest`, more than half the file" WAS RAW LINE
  SPAN.** By CODE lines it is **213 of 587 — 36%**. *The split is still the right first move and
  buys less than I projected.*

* ⚑ **NO INSERT RETIRED, AND THE SHARER LIST IS THE DELIVERABLE.** `drain_leverage` unchanged at
  **491 inserts**; `worklist_gate` reads `retires 2, contested 9, consumers 2`, co-drained by
  **`agda_lex, fix_noparse, fix_notinscope, gate_keys, gate_status, jea_agdai, pycodemod, ratchet,
  shared_cache, split_lemmas, split_pipeline` — all eleven remain.** *Four drains now, four walls:
  untyped callee · frozen consumers · shared inserts · and now a typing boundary that moving code
  cannot cross.*

  ⚑⚑ **AND THE CASE IDIOM HAD TO CHANGE, WITH THE LINT RULE IN THE RIGHT:** the origin's
  `check(label, got, want)` makes every boolean expectation a **boolean positional argument**
  (`FBT003`, dozens of times). The landed precedent
  (`substrate/drain_leverage_selftest.py:62`) returns **cases as DATA** —
  `_cases() -> list[tuple[str, object, object]]` — *and as tuple elements the same expectations are
  values, so the class vanishes.* **Every assertion preserved; the shape changed.**


* ⚑⚑⚑ **CORRECTION TO THE ENTRY ABOVE — "THE BLOCKER IS NOT SIZE, IT IS `disallow_any_expr`" IS
  WRONG, AND I RELAYED IT WITHOUT TESTING IT.** Operator: ***"No, the blocker is size. If
  `disallow_any_expr` rejects, then: (1) the file is likely doing too much — your attention frayed
  when you attempted a whole-file write, the docs WARN you about this; (2) you're transitively
  including something that leaks `Any` (or `...`) in a type signature. Type stubbing is the normal
  fix."***

  ⚑⚑ **`disallow_any_expr` IS THE SIGNAL, NOT THE WALL.** It fires on exactly two conditions, **both
  with established remedies in this repo**: a file doing too much (**decompose** — the per-file gate
  as a design signal, recorded eleven times this session) or a transitive `Any` leak (**stub it** —
  `stubs/` holds ELEVEN, five landed today, and `check_stub_authority` + `stub_reexport` gate them
  from both directions).

  ⚑⚑⚑ **AND THE AGENT NAMED THE DIAGNOSIS WITHOUT RECOGNISING IT.** Its 43 residual errors were
  *"all implicit-`Any` from three sources: `Callable[..., X]` ellipsis fields, `getattr` results,
  and `__import__`."* ***`...` in a signature is PRECISELY the shape the operator names as
  stub-remediable*** — not an irreducible boundary but **an untyped surface with a known fix**.
  *43 errors after a 309 → 46 convergence is the rule saying KEEP GOING and the remainder has a
  specific cause, not the rule refusing to be satisfied.*

  ⚑ **AND `wg_order.Row` IS A TWO-LINE FIX AT ITS DEFINITION, NOT A NARROWING AT DOZENS OF EDGES.**
  Calling an untyped `collections.namedtuple` *"the real blocker"* made it sound structural.
  **Typing it where it is DEFINED fixes every consumer at once** — the same
  `fix-infra-at-source-never-per-consumer` rule this repo records, arriving as a typing question.
  *The narrow-at-the-edge plan was the per-consumer sprawl the rule forbids.*

  ⚑⚑ **THE SHAPE OF MY ERROR IS THE ONE THIS SESSION KEEPS RECORDING, NOW IN MY OWN RELAY: A
  DIFFICULTY SATISFYING A GATE READ AS A PROPERTY OF THE GATE.** Three prior instances —
  `hook_shellcheck` refusing a per-line disable (*"a disable directive is not a relief valve, it IS
  the defect being gated"*), `stub_top_type` rejecting a marker rule (*"satisfiable by typing a
  sentence"*), and the ad-hoc-SQL mode (*"like writing to scratch"*). **Ⓝ125 ⟡the-easier-escape-hatch
  now has a fourth witness, and this one is mine.**

* ⚑⚑⚑ **Ⓝ117 ⟡the-import-mechanism-is-the-blocker — THE COMPOUND-INTEREST ARGUMENT IS FALSIFIED,
  AND I SUPPLIED IT.** I claimed *"a large share of the 1133 mypy findings are PLAUSIBLY
  `import-not-found` against modules that EXIST"* and dispatched a strict gate inversion on that
  basis. **Verified by me: ZERO of 1132 keys, 0 of 44468 messages, across 25 error codes — not one
  is an import code.**

      misc 35867 (80.7%) · no-untyped-call 5134 (11.5%) · no-untyped-def 2307 (5.2%)
      `Expression has type "Any"` alone is 44.2% of all messages

  ⚑⚑ **AND NONE COULD BE: `substrate/mypy_census.FLAGS` INCLUDES `--ignore-missing-imports`**,
  defended at its authority as deliberate policy for optional deps (*"without it the census is
  dominated by rows saying nothing about our code"*). **Import errors are suppressed BY
  CONSTRUCTION.** *A `sys.path` conversion cannot pay down a single one of those keys.* **The 1133
  is an UNTYPED-SURFACE census, not an import-resolution census** — and I read the name of the gate
  as the nature of its contents.

  ⚑ **"NOBODY HAS MEASURED IT" WAS ALSO FALSE.** `type_census_summary --codes` has been able to
  answer this the whole time. **A DISCOVERY failure, not a measurement gap** — the shape CLAUDE.md
  names for summit: *a capability nobody knows about is functionally absent.* ⚑ The agent found it
  by reuse-search **after starting to add `--codes` to the ratchet itself**.

* ⚑⚑⚑ **AND THE AGENT REFUSED TO LAND A RED GATE ON A FALSIFIED REASON — THE RIGHT CALL.** The
  operator's ruling (*"the repo can't go green until stuff a LOT worse gets fixed, and fixing THIS
  will earn compound interest"*) is sound as a DIRECTION; **the interest had been quantified as the
  mypy blocker, and that quantity is zero.** Landing a permanently-RED gate whose stated payoff is
  disproved *would bank a red state on a reason that does not survive its own measurement* — **the
  failure mode this repo catalogues, not a paydown of it.** ⚑ Nothing installed, nothing inverted,
  nothing converted, no summit ask filed — *the ask as scoped would have filed a misstatement into
  a shared forum.*

  ⚑ **TWO FURTHER PREMISES OF MINE, DEAD:** `substrate` **is already installed** (editable), and
  **mypy already resolves these imports cleanly with no install change** — `--explicit-package-bases`,
  already in the gate's flag set, resolves sibling `scripts/` modules **regardless of `sys.path`
  inserts and regardless of install kind**, verified clean from a foreign cwd. *So the
  `not-found → import-untyped → clean` ladder, while real, does not connect to the 1133.*

* ⚑⚑⚑ **Ⓝ32a ⟡type-gate-broken — THE GATE COULD NOT RUN AT ALL, AND THAT WAS MY REGRESSION.**
  It did not report 1,145 errors; it CRASHED:

      AttributeError: 'Report' object has no attribute '_replace'. Did you mean: '__replace__'?

  **`_replace` is a `NamedTuple` method.** The ⟡symbolic-reference-only conversion turned
  `ratchet_render.Report` and `type_gate.GATE` into frozen slotted dataclasses, whose
  copy-with-changes spelling is `__replace__` (PEP 681, Python 3.13). Seven call sites across
  three files — `gate_main.py:127`, `type_gate_selftest.py` ×2, `type_gate_verdict_selftest.py`
  ×4 — all repaired; both suites green (**8/8**, **4/4**).

  ⚑⚑ **AND THIS TIME PROXIMITY *WAS* CAUSATION — WHICH IS WHY I CHECKED.** This morning a suite
  failure arrived right after the 58-file write and I opened with *"a real regression, and it's
  mine"*; two commands refuted it (`baseline_io.py` was untouched). Here the same instinct was
  correct, and the same two commands established it: `--calls _replace` for the population,
  `--binding Report` for the definition site. **The discipline is not "distrust the obvious
  cause" — it is "measure either way", and it costs the same when the obvious cause is right.**

  ⚑⚑⚑ **WHAT THE GATE NOW REPORTS, AND WHAT I CANNOT ESTABLISH:**

      mypy-ratchet: BROKEN — 1154 NEW type errors

  The population is entirely OUTSIDE `substrate/`: `el-atlas/tools/`, `jea/evolution/`, `jea/`,
  `scripts/`. The dominant kind is `misc:: Expression has type "Any"` at 15–129 per file across
  dozens of `jea/` modules — a subtree written before `disallow_any_expr` was enabled.

  ⚑ **THE 1,145 → 1,154 DELTA IS NOT ATTRIBUTABLE, AND SAYING SO IS THE POINT.** The gate could
  not execute before the repair, so the earlier figure came from somewhere other than a run of
  this gate in this state. Nine more may be newly introduced or newly VISIBLE, and **no reading I
  can take distinguishes those** — the baseline predates a gate that crashed. Reporting "I added
  nine" or "I added none" would both be unfounded.

  ⚑⚑ **AND THE CENSUS IS 125 KB WITH NO SUMMARY — Ⓝ44's SHAPE, ONE GATE OVER.** `--list`
  enumerates every key and cannot be read without the shell composition the structural hook
  refuses. A gate whose debt cannot be READ cannot be PAID DOWN in any ordered way: there is no
  reading of *"which subtree carries most"*, so nobody can choose where to start.
  → **Ⓝ61 ⟡type-gate-needs-a-summary**: per-subtree and per-kind counts, the way
  `record_migrate --summary` made 67 files reviewable.

* ⚑ **SO THE COMMIT BLOCKER IS UNCHANGED IN SUBSTANCE AND CHANGED IN KIND.** It was *"the gate
  reports 1,145 errors"*; it is now *"the gate RUNS and reports 1,154, none of them in the code
  this session wrote"*. **Everything landed today is still uncommittable** — 58 conversions, seven
  modules, five suites — behind debt in trees this arc never touched.

* ⚑⚑⚑ **Ⓝ32a⁶ ⟡files-if-none-are-given — THE MYPY CITATION, VERBATIM, AND THE CLAUSE IS
  LOAD-BEARING.** `python/mypy` `docs/source/config_file.rst`, the `files` entry:

      "A comma-separated list of paths which should be checked by mypy
       IF NONE ARE GIVEN ON THE COMMAND LINE."

  **`files` bounds discovery ONLY in the no-args case.** A gate handing mypy EXPLICIT paths
  bypasses it entirely, and the strict settings apply because they live in the global `[mypy]`
  section, which governs every file mypy actually checks however it arrived. **`files` was never a
  promise that other paths are exempt.**

  ⚑ So the operator's ruling (Ⓝ32a″ — those trees should MEET the bar) turns a bypass into a
  feature, and it is **documented behaviour rather than an accident**. ⚑⚑ And our own
  `pycheck_checkers.py:63` already carried this, measured WITH A POSITIVE CONTROL — a file
  containing `X: int = "not an int"` placed outside the repo entirely is still reported. **The
  evidence in our tree was stronger than the doc paragraph I sent a peer to find**, and I did not
  look because the question felt like an upstream-docs question. *A behaviour measured with a
  control beats a documented sentence; having both is the luxury.*
