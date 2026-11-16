# Ⓝ31 residue — false zeros

**Concern: readers that answer `0` when they mean "I could not ask that question" — in a repo
that DELETES on zeros.** Index and arc frame:
[`toolmodes-split.md`](toolmodes-split.md).

⚑⚑ **THE REMEDY IS NOT A TRUE COUNT; IT IS A COUNT THAT STATES ITS OWN BOUNDARY.**
`attr_reads.unresolved()` is the pattern that closes the class, and Ⓝ74 shows it being inherited
correctly one reader over. ⚑ The general form, witnessed three times in one session: **a promoted
reader inherits the QUESTION but not the BOUNDARY**, because the origin's bounds were never
written down — only its symptom.

⚑ Two boundaries, not one: `unresolved()` names what the PREDICATE could not decide about a file
it held; Ⓝ72c ⟡state-the-walk names what the POPULATION never handed it. The second is
structurally unreachable from the first.

## Residue

* ✅ ⚑⚑⚑ **Ⓝ68b ⟡attr-misses-the-alias — DONE, AND MY DIAGNOSIS WAS WRONG. THE MODE WAS
  DOCUMENTED AND NEVER IMPLEMENTED.** I stated twice — in the worklist and in the agent's brief —
  that `--attr` fails to resolve `from <pkg> import <mod>`. Measured, it resolves that form fine:

      --attr 'ratchet_flags_selftest.*'       →  finds the site
      --attr ratchet_flags_selftest.selftest  →  0 reads in 0 of 1 file(s)   ← SAME FILE, SAME SITE

  **`_attr_reads_one` special-cases only `endswith(".*")`.** Every other dotted operand falls
  through to the leaf branch and is compared `node.attr.value == "ratchet_flags.selftest"` — a
  string no attribute name can ever equal, since it is not an identifier. **The mode cannot ASK
  the dotted question, and answers `0` instead of saying so.**

  ⚑⚑ **SO THE FALSE ZERO WAS NOT AN ALIAS GAP BUT A MISSING IMPLEMENTATION BEHIND A DOCUMENTED
  FLAG** — which is strictly worse, because the documentation is what licenses a reader to trust
  the zero. My own hypothesis, stated as fact twice, would have sent the fix into the resolver
  and left the branch untouched. **The agent measured instead of accepting the brief.**

  **THE MATRIX (`--attr Recv.leaf`, before → after):** `import pkg.mod` · `import pkg.mod as m` ·
  `from pkg import mod` · `from pkg import mod as m` · `from . import mod` — **all five returned
  0; all five now resolve.** Bare-leaf queries are unchanged and still receiver-blind (186 live
  reads). Live: `--attr substrate.corpus.py_files` went **0 of 1147 → 14 reads in 10 files**, a
  query that would have read as a DEAD CAPABILITY in the census this repo deletes on.

  ⚑ **THE FIX IS A PROMOTED READER BECAUSE THE ORIGIN IS WRITE-LOCKED.** `scratch/pycodemod.py`
  (2,145 findings) and `scratch/_pycodemod_query.py` (1,948) are both refused by the per-file
  gate, which has no partial-credit path — measured, not assumed. The gate's own text names
  extraction as the move, and `module_importers.py` had already taken that route for the
  `--importers` half. New: `substrate/attr_reads.py` + suite (**16/16**, discovered by
  `run_selftests`).

  ⚑⚑⚑ **AND `unresolved()` IS THE PART THAT MATTERS MOST: A ZERO NOW NAMES WHAT IT CANNOT SEE.**

      ratchet_flags_selftest.selftest: 0 attribute read(s) in 0 of 1147 file(s)
         ⚑ 4 shape(s) this reader CANNOT resolve — a zero above is not yet an absence:
           dynamic-import: substrate/ratchet_suites.py:215 binds a module at runtime

  Three shapes are named rather than folded into the count: `re-export-chain` (the `ratchet.py`
  star form), `dynamic-import`, `relative-package`. **The remedy for a false-absence finding is
  not a true count — it is a count that states its own boundary**, which is the one thing the old
  `0` could not do. ⚑ And it points at `ratchet_suites.py:215`, the file another agent rewrote
  MID-SESSION to derive its roster via `importlib` — so the honest zero is honest about a
  genuinely unreadable shape, not a stale one.

  ⚑ **THE MOTIVATING SITE HAD ALREADY EXPIRED, AND THE CASE WAS WRITTEN AGAINST THE PROPERTY
  ANYWAY.** By the time the suite was written, Ⓝ68a's rewrite had removed the static
  `ratchet_flags_selftest.selftest` read — a case pinned to that file would now be **green for
  the wrong reason**. The matrix case iterates `attr_reads.BINDING_FORMS` instead. Ⓝ66
  ⟡witness-not-victim, applied prospectively by an agent rather than found in an audit.

* ⚑⚑ **Ⓝ68b′ ⟡two-stale-origins — `--attr` AND `--importers` NOW BOTH RETURN FALSE ZEROS FROM
  `scratch/pycodemod.py`, AND NEITHER IS FIXABLE IN PLACE.** They are superseded by
  `substrate/attr_reads.py` and `substrate/module_importers.py`, but the origin modes still
  dispatch and still answer. **A superseded reader that still responds is worse than a deleted
  one**: it answers the question asked, wrongly, to anyone who reaches the old spelling first.
  Retiring them needs the ⟡promote-pycodemod drain to reach the dispatch layer.

  ⚑ `--importers` is a SEPARATE root cause, already repaired before this session: `importers()`
  keys on `node.module.split(".")[0]`, so inside a package every importer spells the dependency
  as the PACKAGE and any submodule query answers 0. Two different bugs, one symptom, and I had
  merged them in the worklist entry.

* ⚑⚑⚑ **Ⓝ74 ⟡importers-path-spelling — THE REPLACEMENT READER HAS THE DEFECT IT REPLACED, IN A
  DIFFERENT SPELLING. REPRODUCED DIRECTLY:**

      module_importers.py substrate/reach_ratchet.py   →  0 import site(s) in 0 of 1155 file(s)
      module_importers.py substrate.reach_ratchet      →  1 import site(s) in 1 of 1155 file(s)

  Same module, same question, one answer true and one a bare zero **with no note, no "did you
  mean", nothing distinguishing it from a genuine absence.** `substrate/module_importers.py` was
  promoted BECAUSE `pycodemod --importers` keys on `node.module.split(".")[0]` and answers 0 for
  any submodule — and it now carries the same class one spelling over.

  ⚑⚑ **AND THE PATH FORM IS THE ONE A READER ACTUALLY TYPES.** Someone arriving from a census
  row, a traceback, a `git status` line, or `suite_gap_report` has a PATH in hand; the dotted
  module name is what you have only if you already know the answer's shape. **The spelling most
  likely to be typed is the spelling that lies** — which is the inverse of a safe default.

  ⚑ **THIS REPO DELETES ON ZEROS.** `--dead` is the census that authorises removal, and this is
  the third false-zero measured today (`--attr` dotted form, `--importers` package-keying, now
  `module_importers` path-keying). Ⓝ68b's fix established the pattern that closes it: **a zero
  must name what it could not resolve.** `attr_reads.unresolved()` does exactly that; this reader
  does not, and the fix is to normalise the operand (accept both spellings) AND to say which one
  it answered.

  ⚑⚑ **THE GENERAL FORM, NOW WITNESSED THREE TIMES IN ONE SESSION: A PROMOTED READER INHERITS THE
  QUESTION BUT NOT THE BOUNDARY.** Each promotion fixed the specific miss that motivated it and
  re-introduced the class at a different operand shape, because the ORIGIN's boundary was never
  written down — only its symptom. **A replacement that does not state its own bounds is a
  hypothesis that it has none.**

* ⚑⚑ **Ⓝ74a — `store_reach.py` IS DISTINCT, AND `--calls` MISLED ON IT IN A NEW WAY.**
  `pycodemod --calls store_reach` finds the FUNCTION `store_reach` inside `import_reach.py`, not
  the MODULE of that name — **a name-scoped census answering about a different kind of thing than
  the question was about.** Not two spellings of one name this time, but one spelling over two
  KINDS (module vs function). The module has zero importers and is genuinely newer work: built on
  `substrate.import_edges` (where `import_reach` inlines its own AST walk), adding `through_cuts`
  and `eager_prefix`. **Uncalled but not dead** — and `--dead` would have said otherwise.

* ⚑⚑ **Ⓝ74b — A REAL LIMITATION RECORDED RATHER THAN ASSERTED AWAY: `store_reach.reaches`
  RETURNS AT THE FIRST SEED FOUND** in an unordered DFS, so when a module is reachable both
  conditionally and eagerly, WHICH ROUTE comes back depends on traversal order. Nothing is lost
  (the narrow reading returns the eager route unmarked) but **a wide route is not guaranteed
  MINIMAL**. Consumers joining a call census against one should truncate with `eager_prefix`.
  ⚑ The agent put this in the suite HEADER instead of writing an arm that pins current traversal
  order — which would have frozen an implementation detail as a contract.

* ✅ ⚑⚑⚑ **Ⓝ72a ⟡shebang-permission-census — 45 → 0, AND THE REPAIRER ALREADY EXISTED. ITS SCOPE
  WAS THE DEFECT.** `scripts/fix_exe_bit.py` (⟡exe-sweep, 2026-08-30) sweeps BOTH rules and was
  written for exactly this failure. Its population is `_TREES = ("scripts", "scratch", "jea")` —
  **`substrate/` is not in it, and all four instances found by hand today were `substrate/`
  files.** Measured: `fix_exe_bit --check` reported **1 mismatch while the tree held 45.**

  ⚑⚑ **IT ANSWERED TRUTHFULLY AND ITS ANSWER WAS BOUNDED BY A SCOPE NOTHING IN ITS OUTPUT
  CARRIED** — the false-zero class one level up, in the tool built to prevent this very defect.
  **A scoped instrument's clean answer needs its scope IN THE OUTPUT.** Widening `_TREES` is the
  outstanding fix (Ⓝ72b); the agent correctly declined, the file being outside its ownership.

  Population found: 44 `EXE001` + 1 apparent `EXE002` across 1160 files — `catalog/memory/` 13,
  `el-atlas/tools/` 9, `substrate/` 9, `scratch/estate/mat260/tools/` 7, `decomposition/` 5.
  New `substrate/file_mode.py` + suite (19/19), and **its zero names its own blind spot**: the
  git INDEX mode is unread, so a staged `100644` still ships the defect.

  ⚑⚑⚑ **AND THE AGENT'S FIRST READER MADE A WRONG REPAIR THAT ITS OWN GREEN SUITE COULD NOT
  SEE.** It tested `read(2) == b"#!"`; ruff scans for a `#!` anywhere in the LEADING COMMENT
  BLOCK. `scratch/strip_using.py` carries its shebang on **line 6**, behind four lines of
  `sys.path` surgery — so the reader called it *no shebang*, saw `+x`, reported EXE002, and
  **cleared a bit ruff wants set.** The suite was 17/17 throughout, **because every fixture was
  built by the suite and therefore encoded the reader's own assumption.** Only running
  `ruff --select EXE001,EXE002` BESIDE the census exposed it. *A suite whose fixtures come from
  the same premise as the code cannot falsify the premise.*

* ⚑⚑⚑ **AND I FOUND THE TWO INSTRUMENTS DISAGREEING AFTER THE AGENT REPORTED BOTH AT ZERO** —
  which is the decorrelation working a second time, in the other direction:

      substrate/file_mode.py                    →  0 disagreement(s) in 1160 file(s)
      ruff --select EXE001,EXE002 .             →  1 error

  `.claude/agents/findings.py` — **a DOTFILE DIRECTORY the census does not walk and ruff does.**
  Fixed (`chmod +x`); both instruments now report zero. ⚑ The population operand has its own
  boundary, distinct from the predicate's: `file_mode`'s zero names what it cannot RESOLVE but
  not what it cannot REACH. Ⓝ72c: a census must state its walk as well as its bounds — 1160
  files is a number, not a scope.

* ✅ ⚑⚑ **Ⓝ74 ⟡importers-path-spelling — CLOSED, BOTH WAYS REQUIRED AND BOTH DELIVERED.**
  Suite 15 → **28/28**.

      substrate/reach_ratchet.py  →  1 site in 1 of 1160 (resolved from the path spelling …)
      substrate.reach_ratchet     →  1 site in 1 of 1160

  Operand normalised through `Operand(given, module, spelling)`; path, dotted and bare all
  resolve, and `a/b/__init__.py` → `a.b` (**carrying `__init__` would have built a false zero
  into the normaliser itself**). The render NAMES the translation when it happened and stays
  silent when it did not — both directions pinned. `unresolved()` reuses `attr_reads`' exact
  three shape names rather than coining new ones.

  ⚑ **THE RELATIVE-IMPORT CASE WAS PREVIOUSLY CORRECTLY EXCLUDED BUT SILENTLY**, and that
  exclusion is now SPOKEN — *dropping it quietly reinstates the same false zero one level in.*
  ⚑ Value showed immediately: `module_importers scripts/fix_exe_bit.py` → 0 sites **plus four
  `dynamic-import` shapes**, so that zero cannot be read as unused — which under `--dead` is
  exactly the deletion this repo makes on zeros.

* ⚑⚑ **Ⓝ72d ⟡bare-generator-writes-an-empty-artifact — `gen_selftest_mk.py` RUN BARE writes a
  VALID-LOOKING `Selftest.mk` with an EMPTY ROSTER.** The real driver is `selftest_mk.py` (277
  suites). **A generator that produces a well-formed empty artifact when invoked directly** is
  the same shape as an absent baseline exiting 0: nothing about the output says it measured
  nothing. Bad artifact removed and regenerated correctly by the agent.

* ⚑ **AND ZERO-TOLERANCE MADE A CAPABILITY UNREACHABLE, WHICH THE AGENT DECLARED RATHER THAN
  WORKED AROUND.** `subprocess` cannot be used from `file_mode.py`: `S603` clears only an inline
  literal argv, `S607` refuses a bare `git`, and there is no suppression path — **mutually
  exclusive**. Rather than grow a second responsibility into the module, it DECLARED the
  git-index blind spot as an unresolved shape. `pyproject.toml`'s `collapse_check.py` entry
  already names the required move (*"if a second git-reading tool appears, that is the extraction
  to make"*), so this is a named, owned gap rather than a silent one.

* ✅ ⚑⚑⚑ **Ⓝ72c ⟡state-the-walk — DONE (`substrate/walk_scope.py` + suite 12/12), AND IT FOUND A
  HOLE NOBODY HAD NAMED.** `corpus.roots()` yields `d.is_dir()`, so a `.py` file AT THE REPO ROOT
  is under NO root and enters **no census built on this walk**. Three exist:
  `applied_grammar.py`, `s4_structure.py`, `verify_applied_grammar.py`. ⚑ Verified consequential:
  `module_importers applied_grammar` → **28 import sites in 2 files**. *Not an excluded tree
  anyone could have guessed — just invisible, and a scope reader listing only skipped DIRECTORIES
  would still have reported clean over them.*

  ⚑⚑ **TWO BOUNDARIES, NOT ONE, AND THAT IS WHY THE EXISTING DISCIPLINE DID NOT COVER IT.**
  `unresolved()` names what the PREDICATE could not decide **about a file it held**. Nothing named
  what the POPULATION never handed it — **an unwalked tree cannot appear as a caveat about a file,
  because there is no file to caveat.** The `attr_reads` pattern was the right pattern and was
  structurally incapable of reaching this.

  ⚑⚑ **AND THE PER-ENTRY SPLIT INVERTS THE HEADLINE, WHICH IS THE REASON IT IS PER-ENTRY.** The
  aggregate reads `7999 .py file(s)` not looked at — catastrophic. The breakdown shows **7,995 are
  `.venv`** (correctly out) and **the entire actionable shadow is 4 files.** ⚑ The agent's first
  cut printed the reason on EVERY row, which stapled *"one of them holds real tools"* onto `.git`
  and `.venv` where it is false; the reason now prints once per KIND. *A true caveat attached to
  the wrong row is a false statement.*

  ⚑ Exclusions are DERIVED (`corpus.roots()` / `corpus.excluded()` asked, never `SKIP_DIRS`
  copied) — so it cannot drift into the `MEM_CAP` shape. **Owed elsewhere:** `module_importers`
  and `attr_reads` YES (same `corpus.py_files` population, one line each); **`suite_gap` NO, for a
  real reason** — it is DIRECTORY-SCOPED, so its bound is the operand the caller passed and is
  already visible at the call site. *Different instrument, different obligation.*

* ✅ ⚑⚑ **Ⓝ72d ⟡bare-generator-empty-artifact — DONE, AND THE TWO MODULES ARE NOT ONE CAPABILITY.**
  `gen_selftest_mk` is a pure renderer (`text()` → str, no `main`, no I/O); `selftest_mk` is the
  CLI owning discovery, the roster, the file and `--check`. The split is argued in the CLI's
  header and is correct — *a renderer that also wrote could not be case-driven without a
  filesystem.* ⚑ Also: my brief said `scripts/gen_selftest_mk.py`; the file is
  `substrate/gen_selftest_mk.py`. **I named a path I had not read.**

  ⚑⚑ **THE HALF THAT WAS STILL ARMED WAS THE SILENT SUCCESS, NOT THE EMPTY WRITE.**
  `gen_selftest_mk.py --check` **printed nothing and exited 0**, having rendered nothing and
  written nothing — *indistinguishable from success*. Fixed by REFUSAL (exit 2 naming the three
  driver invocations), not documentation. ⚑ Side effect worth keeping: gaining a `--selftest`
  literal made it DISCOVERABLE, so the roster grew and `--check` correctly flagged 13 stale
  targets (11 pre-existing). Regenerated — **292 suites, `--check` exits 0.**

* ⚑ **Ⓝ82 — `module_importers corpus` → `0 in 0 of 1181` while `substrate.corpus` has 69.** A
  SPELLING miss (the operand normalises to top-level `corpus`), independent of the walk. **A
  second way that denominator misleads**, in the reader promoted to fix exactly this class.


* ✅ ⚑⚑⚑ **Ⓝ84 ⟡the-sanctioned-boundary-does-not-EXIST — CLOSED, AND THE SHAPE WAS THE SECOND
  ONE: THE EXEMPTION DOES NOT EXIST AS POLICY EITHER.** I offered the agent two readings — *the
  policy stands and only its gate is gone*, or *the exemption was never policy*. It established
  the second from the config and the tree, so the deny message now **stops offering the hatch**
  rather than restating it without an enforcer.

  **THE EVIDENCE, none of it from the message's own text:** `per-file-ignores` carries **no `Any`
  entry at all** (every row is `S101`/`S603`/`FBT*`/`PLR*`, each scoped to one responsibility) ·
  `disallow_any_explicit = true`, so **the word cannot be spelled** · `[tool.mypy]`'s own comment
  refuses the hatch generally — *"Relief lives on the ENUMERABLE side, never on the unenumerable
  one"* · **there is no numpy boundary module and no `stubs/numpy`**, and `module_importers numpy`
  finds **227 importers, NOT ONE in `substrate/`** — so **the gate has never once seen numpy** ·
  and where the same question WAS answered (`types-networkx`) the answer was a **stub**, with
  `pyproject.toml` explicitly rejecting the framing: *"that is not a walled boundary; it is the
  interface itself."*

  ⚑⚑ **SO THE SENTENCE I QUOTED IN EVERY BRIEF THIS SESSION — *"the ONE sanctioned exception is
  the numpy `Any` boundary, gated by `check_ignore_holder.py` (sole-holder + fixed-count)"* —
  DESCRIBED A GATE THAT DOES NOT EXIST GUARDING A BOUNDARY THAT WAS NEVER POLICY, FOR A LIBRARY
  THE GATE HAS NEVER CHECKED.** I copied it from the hook's own refusal text and never checked one
  clause. Verified now: `module_importers check_ignore_holder` → **0 sites, and the zero NAMES ITS
  BOUNDS** — Ⓝ68b's fix working on the question it was built for.

  ⚑ **AND THE SWEEP FOUND A SECOND LIVE SITE OF THE SAME CITATION**, which is why the sweep was
  the instruction: `scripts/hook_pycheck.py:46` asserted it in the **PRESENT TENSE** — *"THE
  SUPPRESSION IS GATED BY A TOKEN WALK — see `scripts/check_ignore_holder.py`"*. **An earlier
  repair had landed on one of two sites**, which is the shape that makes a citation survive its
  referent. The new text names the two REAL enumerable routes (a stub that ADDS types; a
  per-responsibility `per-file-ignores` entry) — each as a reviewed addition, *"not something this
  refusal grants you."* ⚑ The agent did NOT rebuild the gate: nothing enumerates holders or fixes
  a count, and `warn_unused_ignores` is explicitly recorded as **not that gate under another
  name**.

  ⚑ **ONE DANGLING CITATION FOUND AND LEFT, CORRECTLY:**
  `scripts/check_categorical_grounding.sh:87` cites Agda module `Category.UniversalProperty.Registry`
  in the text an operator reads when the advisory fires — **absent**, while three live `Registry`
  modules exist on the **Algebra** side the gate's own text calls unreachable. Not owned, not in
  the ledger; proposed `gate-F50`. Also: **`gate_census --check` EXITS 1** (blocking 35→36,
  ratchets 17→18, `ratchet_legacy.py` UNREAD) — pre-existing.

* ✅ ⚑⚑⚑ **Ⓝ82 ⟡importers-bare-name-miss — CLOSED BY REFUSAL, AND THE TREE FORCED THE CHOICE.**
  The bug was where predicted: `normalise("corpus")` returned `spelling=DOTTED`, so `package =
  None` and **the `from <pkg> import <mod>` branch — the one this module exists for — could never
  fire.**

  ⚑⚑ **AND A BARE NAME IS GENUINELY AMBIGUOUS HERE: `corpus` denotes BOTH `substrate.corpus` AND
  `tests.corpus`.** So resolution would have been a coin flip. Verified live by me:

      corpus       →  AMBIGUOUS — 2 modules carry this bare name … substrate.corpus / tests.corpus
                      (exit 2, candidates NAMED, nothing guessed)
      suite_emit   →  ⚑ the bare name resolved to `substrate.suite_emit` — 3 sites, bounds declared

  `candidates()` **enumerates and does not choose**; `main` resolves when unique, refuses with
  candidates when not, and leaves the name bare when nothing carries it (so `import agda_lex`
  still works). **A refusal naming the candidates, never a guess and never a zero** — in the
  reader promoted specifically to stop false zeros. ⚑ `substrate.corpus` re-derived at **72**
  sites; the 69 I briefed was stale.

* ⚑⚑⚑ **Ⓝ84a ⟡the-arms-bought-nothing-and-mutation-proved-it — THE BEST RESULT IN THIS DISPATCH,
  AND IT DELETED CODE RATHER THAN ADDING IT.** The agent first wrote three arms pinning an
  explicit `if "." in operand …: return ()` guard. **It then MUTATED THE GUARD AWAY — and the
  suite stayed 34/34.**

  **So the guard was DEAD CODE and the three arms READ LIKE COVERAGE WHILE BUYING NONE** — the
  leaf-name test already rejected dotted and path operands. ⚑ It deleted the guard rather than
  keeping it as reassurance, and rewrote the arms to pin the PROPERTY (real) instead of the BRANCH
  (not). *A case can be green, honest, and worthless; only a mutation distinguishes it from one
  that holds something up.*

  ⚑ **AND THE LOAD-BEARING ARMS DO DISCRIMINATE, BY THE SAME METHOD:** mutating `candidates` to
  pick-first instead of enumerate **fails the ambiguity arm with `('substrate.corpus',)`** —
  exactly the guess-instead-of-refuse defect, caught by the case written for it. **Cases 27 → 34**
  — and `_CASE_COUNT` said 28 against a 27-arm roster, **fixed by deriving it with `len(_ARMS)`**
  rather than correcting the number. *The count had an authority; it was being restated* (Ⓝ85).


* ✅ ⚑⚑⚑ **Ⓝ85d · Ⓝ79b · Ⓝ71f — ALL THREE CLOSED, AND THE CENSUS BUILT TO FIND THE CLASS COMMITTED
  IT FIRST.** `doc_split` 32/32 · `module_size` 21/21 · `store_calls` 20/20 · new
  `substrate/bare_speech.py` 13/13.

  ⚑⚑⚑ **THE FIRST CUT OF THE BARE-INVOCATION CENSUS REPORTED 32 SILENT CLIs AND MOST WERE ITS OWN
  FALSE POSITIVES.** It stopped at `sys.exit(main(sys.argv[1:]))` — **the dominant idiom in this
  tree** — so `file_mode.py`, `module_outline.py` and `attr_reads.py` read as mute. The agent RAN
  three of the accused; each printed a usage line and exited 2. **A fact about the method reported
  as a fact about the substrate, committed by the instrument built to find that.** Fixed by
  following the delegation one hop: **32 → 5**, and the header and output now STATE THE RESIDUAL —
  *"speech two calls deep still reads SILENT, so confirm a row by RUNNING it."*

  ⚑ **VERIFIED BY ME: `type_gate.py` bare DOES speak** (it runs the full census — 1133 NEW,
  re-derived live), so the false-positive call is right and the two-hop caveat is exactly why it
  still reads SILENT. **Ground truth by running all five: 3 genuinely silent
  (`edge_split`, `warrant_bib`, `witness_row` — named, not fixed, not owned), 2 false positives.**

  ⚑ **AND THE CENSUS CLASSIFIES FOUR WAYS BECAUSE THREE WOULD LIE:** SPEAKS / SILENT / **LIBRARY**
  / SUITE. **~96 guard-less libraries print nothing for a reason that is not the defect** — *"a
  fact about running a library as a script, not a swallowed query."* Collapsing them into SILENT
  would have produced a 100-row work list of non-problems, which is Ⓝ67 ⟡the-slot-is-the-reach
  arriving in a new census: **a category the population needs, or the count is about the
  instrument.**

* ⚑⚑ **Ⓝ85d — THE GUARD SITS AT `conserved`, NOT AT THE CLI, AND THAT PLACEMENT IS THE FINDING.**
  A vacuous origin raises `VacuousOriginError` at **the predicate every caller reaches**, so the
  suites and `consider` cannot obtain the vacuous green either — *a refusal wired only at the CLI
  protects the operator and not the program.* Keyed on `body_lines(origin)` being empty — **the
  same unit the comparison consumes** — so empty / whitespace-only / blank-lines-only are ONE
  refusal rather than four spellings of one.

  ⚑ **AND `consider` CATCHES THE `OSError` SEPARATELY, refusing AS UNREADABLE**, because *"the
  file is empty" and "the file is absent" are different repairs* — **and the measured `git show`
  failure produced both at once**, which is precisely why one refusal covering both would have
  been the wrong shape.

* ⚑⚑ **Ⓝ79b — SCOPING, NOT REFUSAL, AND THE REASON IS IN THE CODE RATHER THAN IN TASTE.**
  `budget_for` is keyed **on the path alone**, so every column is file-local and **a scoped row is
  BYTE-IDENTICAL to that file's row in the full census** — which is what makes honouring the
  operand honest rather than a second implementation. ⚑ **The opposite resolution is correct one
  module over:** `substrate/tool_cli.py` REFUSES its operand, because its predicates are
  corpus-relative. *Same defect shape, two different right answers, decided by whether the
  predicate is file-local.* Per Ⓝ80 the summary is reworded from *"over budget"* to *"past the
  reference mark … a READING, not a verdict"* — numbers unchanged.

* ⚑⚑ **Ⓝ71f — IT HAS NO MODES, SO IT SAYS WHAT IT IS INSTEAD OF FAKING A MODE LIST.**
  `store_calls` bare now names the module, its one entry point, **and the capability its name
  SUGGESTS BUT LACKS** — which is the sentence that would have saved me the misread. The roster is
  **read from `CONNECT_CALLS`**, not restated (Ⓝ85). ⚑ An operand is REFUSED rather than
  interpreted: *"there is no name-search to route it to, and accepting one would rebuild the false
  zero."*

* ⚑⚑⚑ **AND THE DISCRIMINATORS ARE WHERE THE RIGOUR IS — EACH REFUSAL PAIRED WITH AN ARM PROVING
  THE LEGITIMATE CASE IS NOT REFUSED.** A one-line origin still measured both ways (vs. a guard
  that refuses everything); **a scoped row asserted EQUAL TO its full-census row** — *vs. a
  `scoped` returning nothing, which would satisfy "the corpus census isn't returned" perfectly*;
  a bare `module_size` still exiting 0; the library still answering `connect_sites`; **four
  fixtures required to produce ≥3 distinct classes**, vs. a constant classifier.

  ⚑ **AND FOUR THINGS DELIBERATELY NOT REFUSED, each with its reason** — a one-line origin (it has
  content; a size threshold would refuse honest work to catch a vacuum); **empty PARTS against a
  real origin** (*that is every line dropped — the guard's sharpest TRUE finding; refusing it by
  symmetry would convert the best detection the tool has into an error about the invocation*);
  `module_size`'s bare corpus call; and libraries printing nothing under `python3 <path>`.
  **Knowing what must keep passing is the harder half of building a refusal.**

  ⚑ Process note the agent kept: the zero-tolerance hook **caught it writing the untyped-lambda
  sort key that `module_size`'s own header warns against — in the suite testing `module_size`.**


* ⚑⚑⚑ **Ⓝ86 ⟡no-module-owns-the-pid — THE OPERATOR REJECTED THE IDIOM THE CENSUS TREATS AS
  CORRECT.** Operator, on `sys.exit(main(sys.argv[1:]))`: *"Yeah, that has to stop. No code should
  assume it is The Owner of the PID."*

  ⚑⚑ **`bare_speech` WAS BUILT TO FOLLOW THAT LINE, NOT TO QUESTION IT.** Its first cut reported
  32 silent CLIs because it stopped AT that delegation; the repair was to follow it one hop. **So
  the census now encodes the idiom as the norm** — it complains only when speech fails to reach
  through it. *An instrument built to audit a population inherits that population's conventions
  unless someone asks whether the convention is the defect.*

  **THE TWO OWNERSHIP CLAIMS IN ONE LINE, AND BOTH ARE FALSE FOR A MODULE:**

      sys.argv   "the process's arguments are MINE"  → a caller cannot invoke it with different
                                                       arguments; the parameter is a global read
      sys.exit   "the process's lifetime is MINE"    → a caller cannot compose it; control of the
                                                       PID is taken, not returned

  ⚑⚑⚑ **AND IT IS THE SAME DEFECT THIS ARC HAS RETIRED FOUR TIMES, WEARING A THIRD COSTUME.**
  `Ⓝ48 ⟡may-write-positional` — a positional boolean a caller could transpose. `q_drainable`'s
  positional floor — a POSITION standing in for an IDENTITY, sliced across cores. The integer-keyed
  scheduler roster that silently dropped `retire`. `Ⓝ85b ⟡the-ordinal-is-a-position`. **Every one
  is an implicit global or position where an explicit named parameter belongs — and `sys.argv` is
  the largest global in the process.**

  ⚑ **THE TEST FROM Ⓝ85a APPLIES UNCHANGED: *does something else already know this?*** The
  CALLER knows the arguments; the caller owns the exit. A module reading `sys.argv` is restating
  a fact its caller holds — and, like every other restatement this session, **it goes stale the
  moment the caller wants something different**, except here "stale" means "uninvokable."

  **MEASURED, and the population is large:** `attr_reads sys.argv` returns **84 KB of sites**
  across `catalog/`, `el-atlas/`, `jea/`, `scripts/`, `substrate/`. ⚑ **Reading that as a flat
  list is the shape the standing rule forbids** — the same 125 KB-with-no-summary defect as Ⓝ61,
  in a population I have not yet given a category to.

  ⚑⚑ **SO THE FIRST WORK IS A CENSUS WITH THE RIGHT CATEGORIES, NOT A SWEEP** — and Ⓝ85d's
  four-way split (SPEAKS / SILENT / LIBRARY / SUITE) is the precedent: **collapsing kinds that
  differ produces a work list of non-problems.** The kinds that plausibly differ here:

      a `__main__` guard's own body            the ONE place a process may claim its argv
      a `main(argv)` taking its args as a PARAMETER and returning an int   ← the shape wanted
      a module-level read of `sys.argv` inside a function
      a `sys.exit` in a library path, unreachable from `__main__`
      a suite reading `sys.argv` to detect `--selftest`   ← ⚑ tangled with the pytest migration

  ⚑ **AND THE LAST ROW IS NOT INCIDENTAL.** ⟡selftest-discovery keys on the literal `--selftest`
  appearing in a file, and every suite reads `sys.argv` to honour it. **The pytest migration
  retires that reader wholesale** — pytest owns collection and invocation — so **Ⓝ86 and Ⓝ73′ are
  the same work on the suite population**, and doing them separately would convert ~290 suites
  twice. *Scope them together or the second pass pays for the first.*


* ⚑⚑⚑ **Ⓝ86a ⟡the-center-already-exists — I FRAMED 84 KB AS A BURDEN AND IT IS THE ARGUMENT FOR
  THE FIX.** Operator: *"On the bright side, centralizing sys.argv processing is **good**
  modularity and reuse promotion."*

  ⚑⚑ **A LARGE POPULATION OF ONE PATTERN IS THE STRONGEST CASE FOR A SHARED READER, NOT A REASON
  TO DREAD THE SWEEP.** N call sites converging on one module is precisely the reuse this repo's
  standing rule exists to produce. I read the size as cost — *"84 KB, a large population"* — which
  is the paydown reflex reading a modularity opportunity as debt.

  ⚑⚑⚑ **AND THE REUSE-SEARCH FIRES AND HITS: THE CENTER IS ALREADY BUILT AND ALREADY WIDELY
  CONSUMED.** `pycodemod --calls check_argv` → **1 def, 43 calls** —
  `substrate/ratchet_flags.check_argv`, reached by **every ratchet gate**
  (`check_ban_ratchet`, `check_cap_ratchet`, `check_claims`, `check_mypy_ratchet`,
  `check_public_ratchet`, `check_snapshot_guard`, `check_sorted_order`, `check_sumtype_ratchet`,
  …), plus `gate_census`, `run_selftests`, `worklist_gate`, `set1_ratchet_cores`, `gate_main`,
  and consumers as far out as `jea/metalanguage/sorted_stream.py` and `scratch/procstruct.py`.

  **Its refusals are the ones printed all session and they are exactly the right shape:**

      unknown flag(s) --queit — known: --dry-run --quiet
        "Refusing rather than running with a flag you did not mean; a silently ignored
         --quiet is a gate that looks like it ran."
      neither --apply nor --dry-run was given … State one.
      BOTH --sandbox and --live given — mutually exclusive. Refusing rather than picking one.

  ⚑ **SO Ⓝ86 IS NOT GREENFIELD — IT IS EXTENDING AN EXISTING CENTER TO THE POPULATION THAT HAS NOT
  REACHED IT YET**, which is a categorically better-shaped task than a sweep: the design question
  is settled, the refusal vocabulary is settled, and each conversion is a DELETION of local
  parsing rather than an addition. *The `agda_files()` shape inverted — instead of four bodies
  under one name, one body that four dozen callers already share and the rest have not found.*

  ⚑⚑ **AND `module_importers climode` RETURNS ZERO WHILE `climode` DEMONSTRABLY RUNS** — its
  refusals appear in every ratchet run. **The zero NAMED ITS BOUNDS** (7 dynamic-import shapes) so
  I did not read it as absence, and asked `--calls` instead. *Ⓝ68b's fix earning its keep on the
  first question I put to it after landing: an import census cannot see a capability reached by
  call, and the honest zero is what sent me to the right instrument.*

* ⚑ **Ⓝ86b — SO THE CENSUS TO BUILD IS "WHO HAS NOT REACHED THE CENTER", NOT "WHO TOUCHES
  `sys.argv`".** The second is 84 KB of undifferentiated sites; the first is a WORK LIST with a
  destination already named. ⚑ And the four kinds from Ⓝ86 still matter, because **the `__main__`
  guard's own body is the ONE place a process may legitimately claim its argv** — a census that
  flags it produces a list of non-problems, which is Ⓝ85d's LIBRARY category all over again.

  ⚑ **The suite population remains entangled with the pytest migration** (⟡selftest-discovery keys
  on the `--selftest` literal, so every suite reads `sys.argv` to honour it, and pytest retires
  that reader wholesale). **Convert them once, under whichever arc goes first.**


* ✅ ⚑⚑⚑ **Ⓝ79e ⟡assert-census — THE WARRANT IS SOUND AND UNFALSIFIABLE, AND THE EXEMPTION IT
  DEFENDS IS BARELY EXERCISED.** Verified by me:

      assert_census.py scripts     →  2 site(s) — arm=2, load=0, unknown=0
      assert_census.py substrate   →  0 site(s) across ~330 modules

  ⚑⚑ **`pyproject.toml`'s `"scripts/*" = ["S101"]` PROTECTS TWO ASSERTS, NEITHER `-O`-FRAGILE.**
  And its own caveat — *"substrate's suites happen to use explicit comparison instead — ONE file
  verified, not the tree (⟡assert-census owed)"* — **is now discharged and it HELD**: zero sites,
  backed by a positive control proving the predicate fires on a literal `assert`.

  ⚑⚑⚑ **AND NOTHING IN THIS REPO RUNS UNDER `-O`.** No `PYTHONOPTIMIZE`, no `python -O` in the
  Makefiles, hooks, `membudget` or the agda shim — **with a positive control**: the same pattern
  relaxed to any flag returns ~45 hits, so the search sees flags and there are simply no `-O`
  ones. *"The warrant is sound but unfalsifiable: the premise '`-O` never runs these' is true
  because `-O` never runs ANYTHING here. It is a claim about the absence of a PRACTICE, not a
  property of the exempted code — which means it stops holding the moment someone adds an
  optimized invocation, and nothing would fire."*

  ⚑ **THE TWO LOAD-BEARING ASSERTS ARE IN `tests/`, NOT `scripts/`** —
  `test_declaration_visibility.py:88` and `test_import_edge_agreement.py:75`, each
  `assert isinstance(X, re.Pattern)` **narrowing a symbol the stub declares `object`, licensing
  the `.finditer` that follows.** Under `-O` both narrowings vanish and the reads go unguarded.
  **Named, not deleted.** *So the exposure lives in the exemption that landed TODAY, and the
  pytest migration is where it grows* — not in the entry the caveat was written about.

  ⚑⚑ **AND THE AGENT CAUGHT ITS OWN PREDICATE REPORTING ITSELF.** Its first `_narrows` read every
  `is`/`is not` as narrowing, so `assert may_write() is False` — a pytest arm checking a RETURN
  VALUE — graded LOAD, and `tests/` came back **5-for-5 LOAD with not one real guard among them**.
  *"The census was reporting its own rule."* Identity narrows only against `None`; fixed, with a
  paired discriminator (`is None` → LOAD, `is False` → ARM). **A census whose every row is the
  same verdict is the tell**, and it caught it before reporting.

  ⚑ **ITS ZERO NAMES FIVE THINGS IT CANNOT SEE**, and one is a genuine class boundary:
  *"cross-function consequence — a caller depending on an arm's assert is an EDGE, not a site"* —
  a per-statement predicate cannot express it. Plus 960 `unknown` sites corpus-wide,
  overwhelmingly `jea/`, **reported as a fact about the predicate's coarseness on production code,
  not as a finding about the tree.**

* ✅ ⚑⚑ **Ⓝ85d′ ⟡the-three-silent — FIXED, AND ALL THREE WERE THE `store_calls` SHAPE.** Read
  first: **all three are libraries with no modes**, so printing a mode list would have been the
  wrong shape. Each now `speak()`s and exits 2. Verified live —

      warrant_bib  →  exit 2, names its four functions, paths READ FROM CONSTANTS, and:
        "⚑ IT IS NOT A WARRANT QUERY TOOL, AND THE NAME READS LIKE ONE. There is no lookup mode
         here… Running this bare, OR WITH A KEY, would have to either fake a query or answer
         nothing — and answering nothing is the silence this refusal replaces."

  **That is exactly the failure I hit with `store_calls`**: I ran it with a name, got nothing,
  exit 0, and read it as *no matches*. ⚑ Each banner discloses the trap its NAME sets —
  `edge_split` *"does not read a bib, and the name suggests it might"*; `witness_row` *"runs no
  witness and collects no rows."*

  ⚑⚑⚑ **AND AT FOUR MODULES IT BECAME A CONVENTION, SO THE AGENT BUILT THE CONTRACT INSTEAD OF
  COPYING THE ARMS A FOURTH TIME.** `substrate/spoken_text.py` + suite (**17/17**) — one body,
  each module a row naming *its own* disclaimer words. The arms are the discipline this session
  has been converging on, stated compactly:

      every banner says what it owes (4 rows)   PAIRED WITH `an_absent_word_is_reported` —
                                                a deficient banner the audit MUST fail, without
                                                which the table passes against an `audit` that
                                                always returns ok
      every_banner_check_asks_for_something     a row with empty `needs` CANNOT FAIL, so
                                                `demands()` guards the vacuous predicate
      an empty banner reports EMPTY              not "omitting everything" — two different next
                                                actions
      the_libraries_still_answer                the required pair: each real capability exercised
                                                beside the refusal, so a module that refused
                                                EVERYTHING cannot read as repaired

  ⚑ *A discriminator for the discriminator* — `every_banner_check_asks_for_something` guards
  against a row that cannot fail, which is the vacuous-arm class one level up from the arms
  themselves. Suites still 13/13, 11/11, 8/8; `unittest discover` **52 OK**. The gate refused four
  times and the agent fixed rather than suppressed; `chmod +x` before first write on all four new
  files, per the hazard measured earlier today.


* ✅ ⚑⚑⚑ **Ⓝ86 ⟡no-module-owns-the-pid — CENSUS BUILT (`substrate/pid_ownership.py`, 21/21), AND
  THE KIND DESIGN IS THE DELIVERABLE.** **186 owed of 1217 read.** Verified by running it:

      480  ENTRY      the `__main__` guard's own body — the ONE legitimate PID claim; the BOUNDARY
       24  REACHED    already reaches `ratchet_flags.check_argv`
      101  UNREACHED  parses flags itself — THE WORK LIST; each conversion DELETES local parsing
       40  CAPTIVE    reads argv inside a NON-entry function — a caller cannot invoke it with
                      different arguments
       44  FATAL      `sys.exit` with NO `__main__` guard anywhere — a library taking the
                      process's lifetime, which no import ever authorises
      175  SUITE      held out — belongs to the pytest migration
      353  CLEAR

  ⚑⚑ **TWO KIND-DESIGN CORRECTIONS THE POPULATION FORCED, AND BOTH ARE THE POINT.**
  **(1) CAPTIVE vs UNREACHED are the same SYNTAX and UNRELATED WORK.** My brief folded them into
  one row (*"a module-level read of `sys.argv` inside a function"*). Splitting them matters because
  **UNREACHED swaps in a call, while CAPTIVE needs a PARAMETER THE FUNCTION DOES NOT HAVE — so the
  fix changes its signature and every call site.** *One list needing two different edits is a list
  an operator cannot act on.*
  **(2) FATAL required no-guard-ANYWHERE, not "unreachable from `__main__`."** *"Reachability is
  undecidable statically; 'the module has no entry point at all' is decidable and is the claim
  with no defence."* **A weaker predicate chosen because it is honest** — the opposite of the
  usual reflex.

* ⚑⚑⚑ **TWO LIVE FINDINGS I CONFIRMED IN THE OUTPUT, AND THE FIRST IS RECURSIVE.**
  **`substrate/ratchet_flags.py` itself reads CAPTIVE — `_rest()` reads argv. THE CENTER OWNS A
  CAPTIVE READ.** *The module that exists so nothing else claims the process's arguments claims
  them internally.*
  ⚑⚑ **AND FIVE HOOK SCRIPTS SHARE ONE `_arg_after()` SHAPE** — `hook_cmdparse`,
  `hook_no_chaining`, `hook_shellcheck`, `hook_structural_query`, plus `fix_exe_bit._findings`.
  **One capability copied five times** — the `agda_files()`-had-four-bodies shape from
  `pycodemod`'s own banner. *Probably the cheapest cluster to pay down first, and it is a
  DELETION of four copies rather than five conversions.*

* ⚑⚑ **THE CONVERSION COST WAS MEASURED BY DOING ONE, AND IT IS NOT THREE LINES.** The agent
  converted `main` in the file it owns end to end — it read UNREACHED in its own first run and now
  reads REACHED, with `--calls check_argv` moving **43 → 44**, verified by buying the refusal:
  `pid_ownership.py --suties` → *"unknown flag(s) --suties — known: --dry-run --suites"*, exit 2.

  ⚑ *"An import, a flag constant, and a two-line replacement — touching THREE REGIONS, so under
  the per-file zero-tolerance gate it is ONE WHOLE-FILE `Write`. That's the unit for all 186 rows,
  and it's why this is a work list rather than a codemod I should have run."* **The atomic-write
  constraint sets the granularity of the arc, not the size of the edit.**

* ⚑⚑ **A DEFECT THE CENSUS COMMITTED AGAINST ITSELF, CAUGHT BEFORE REPORTING.** `_delegates` first
  collected EVERY bare-name call under a guard — `print`, `len`, `sorted`. **The visible symptom
  was unreadable detail lines; the real damage is that `callees` is ALSO what EXCUSES a function
  from CAPTIVE, so a guard calling a builtin could SILENTLY SUPPRESS a real finding.** Fixed by
  filtering against the module's own functions, with
  `a_builtin_in_the_guard_does_not_excuse_a_captive` as the regression arm. *A cosmetic symptom
  and a false-negative sharing one cause.*

  ⚑ **DISCRIMINATORS ON SYNTHETIC FIXTURES ONLY** — no live filenames, which expired four times
  today. Two negative controls carry it: `a_center_reaching_module_is_not_on_the_work_list` (fails
  any reader that flags everything) and **`a_bare_module_claims_nothing` (fails any reader keyed
  on the `sys` IMPORT — near-universal here)**. `a_main_guard_may_claim_its_own_argv` pins the
  exemption **in both directions so it cannot be satisfied by absence.**

  ⚑ **BOTH BOUNDARIES PRINT:** predicate blindness (`one-hop` — reaching the center two calls deep
  reads UNREACHED, *"a false positive in the safe direction"* · `dynamic-dispatch` · `re-export`
  under a different name · `nested-def`, under-reporting CAPTIVE by exactly that shape) **and**
  the walk (`walk_scope`: 19 root entries, 7999 `.py` unseen, of which 7995 are `.venv` — the
  actionable shadow is 4 files).

* ⚑⚑ **AND THE COMPOSITION WITH Ⓝ73′ IS DISJOINT BY CONSTRUCTION — BOTH AGENTS REACHED IT
  INDEPENDENTLY.** 175 suites held out entirely and exposed as `--suites` so the migration can
  size its own overlap. *"They read `sys.argv` to honour the `--selftest` discovery literal — that
  read is COMPLIANCE, not the defect, and pytest owning collection retires it wholesale.
  Converting any of them here would be work Ⓝ73′ deletes."* **186 owed ∩ 175 suites = ∅.**

  ⚑ **AND IT DID NOT GATE THE WORK LIST**: *"a ratchet needs a baseline and a paydown policy
  nobody has set; `main` returns 0 always, and the docstring says why."* **A census that declines
  to become a gate until someone sets its policy** — the inverse of the eleven EMPTY-baseline
  ratchets this session has been reading.

* ⚑⚑⚑ **`module_importers` RETURNED A CONFIDENT 3-SITE REPORT FOR A PATH THAT DOES NOT EXIST.**
  I wrote `scratch/reuse_catalog.py`; the file is `scripts/`. **It resolves the leaf name and NEVER
  STATS THE FILE.** Verified by me on a fabricated path: *"0 import site(s) in 0 of 1280 file(s)
  (resolved from the path spelling `scratch/does_not_exist_at_all.py`)"* — **a clean zero, no
  complaint, and it echoes the spelling back as though it had resolved something.**

  ⚑⚑ ***So a TYPO IN A PATH reads as "nothing imports this" — and in a repo that deletes on a zero,
  that is the dangerous direction.*** **Ⓝ122h ⟡importers-does-not-stat** — the reader must refuse an
  operand naming no file, rather than answering about the leaf it guessed.

* ⚑⚑⚑ **Ⓝ122d ⟡import-writes-to-cwd — DOES NOT REPRODUCE, AND THE DIAGNOSIS OF WHY IS THE FINDING.**
  Run from an empty foreign cwd: **probe directory empty BEFORE and AFTER**, `adopter_import`
  identical (**388/394 · 96/130**). And the witness does not exist — `pycodemod --literal
  hook_shellcheck.py` finds **2 sites in 1272 files, NEITHER a write**: a string in
  `check_hook_set.py:62`'s declared-roster LIST, and `hook_shellcheck.py:473`'s own refusal prose.

  ⚑⚑ **THE LIKELY CAUSE IS A CENSUS VOCABULARY READ AS A SUBSTRATE FACT.** A census reports that
  module-scope **string literal** as a `decl` at `<module>()` scope, and the prior agent read
  *"declared at module scope"* as *"written at import time."* ***`decl` means a NAME-BINDING SITE,
  not a filesystem write.*** **The session's recurring shape, arriving one level up — in the READING
  of an instrument's output rather than in the instrument.**

  ⚑ **HONEST RESIDUE, NOT CLOSED: something DID corrupt a prior probe, and this is not it.** Cause
  unidentified. ⚑ And on `corpus.resolve_root`'s "CWD FIRST" — **not the wrong default.** Its
  docstring records the incident: *a peer running the tooling symlinked into their own checkout got
  substrate's entire 6,005-line census back*, because a relative path resolved against the TOOL's
  root. **CWD-first is the fix for that, and the root fallback can only WIDEN what a caller could
  already reach, never redirect it** — and `resolve_root` is only ever a READER, so it cannot itself
  cause a write.

* ⚑⚑⚑ **Ⓝ122g ⟡importers-collapses-the-axis — MY DESCRIPTION OF THE DEFECT WAS WRONG, AND THE
  CORRECTION IS SHARPER.** I said the reader *"normalizes bare names to dotted and then reports only
  the already-dotted sites."* **The operand normalization is CORRECT and worth keeping.** The defect
  was on the **SITE** axis: `normalise` maps `_agdatext` → `scripts._agdatext`, then `_plain` tests
  `alias.name == "scripts._agdatext"` **against source that reads `import _agdatext`.**
  ***The reader was asking for a spelling NO FILE IN THE TREE WRITES.*** ⚑ Every prior note in that
  module (Ⓝ74, Ⓝ82) is about the OPERAND — *this was the same class arriving on a genuinely new
  axis.*

  ⚑ **Verified by me: 21 bare, 0 dotted, printed BY DEFAULT with no flag** — and it names the
  consequence rather than leaving it to be inferred: *"a bare site resolves only under a `sys.path`
  insert and FAILS for an adopter importing the installed wheel — the paydown queue, not a second
  spelling."* **Three site shapes now resolve, not two**: bare `import`, **bare `from`**
  (`from agda_lex import agda_files`), and the dotted forms. ⚑ Uncovered en route: `_strip` joins
  `_agdatext` on the star-unexportable list, reached via `from _agdatext import _strip` at three
  sites.

  ⚑⚑ **AND IT PINNED THE SHAPE, NOT THE COUNT — with the reason.** *A count pinned here goes red
  exactly when the paydown queue drains, i.e. when it is working.* **The two readers agree at 21,
  member-for-member** — and the agent **refused to collapse that into equivalence**: *"agreement on
  ONE measured case, not proof the readers are equivalent — different populations (working tree vs
  installed distribution) and different scopes (all scopes vs module-scope), so a function-scope
  import would legitimately split them."*

  ⚑ Suites: `module_importers` **11/11** (new), `iface_dataflow` **31/31**, `iface_cost` **5/5**;
  `selftest_mk --apply` → **341**. ⚑ *The `no-chaining` hook refused a `for`-loop over the four
  modules and was right — a before/after verdict comparison is judgement that belongs in a program,
  and `iface_cost --cache` already owns that shape.* ⚑ `PLR0911`/`PLR0915` correctly identified that
  `_from` and `_selftest` **had each grown a third job**, which became `_bound` and `_cases_index`.

* ⚑⚑⚑ **Ⓝ86′ ⟡the-five-hooks — THE CLUSTER WAS FOUR, AND THE FIFTH WAS A NAME MATCH.**
  `fix_exe_bit._findings` names a LOCAL variable `argv` holding a `ruff check` command line and
  never reads `sys.argv`. **The census matched the NAME, not the CAPABILITY** — the `--calls emit`
  / `_emit_one` shape running in the opposite direction, producing a false MEMBER instead of a
  false absence. *I briefed five; the substrate had four.*

  ⚑⚑ **PAID DOWN AS A DELETION, AND IT WAS A BEHAVIOURAL FIX TOO.** Four byte-identical
  `_arg_after` bodies → one authority (`substrate.ratchet_flags.arg_after`); the
  `hook_structural_query` copy had **zero callers** and was deleted outright. **Every copy called
  `.index` unguarded, so an ABSENT flag raised `ValueError` where its own docstring promised
  `""`** — unobservable because the input was a global, *which is what CAPTIVE is*. CAPTIVE 40 → 38.

  ⚑ **`check_argv` DID NOT FIT, FOR ALL FOUR** — it VALIDATES a flag set and returns an exit code;
  `arg_after` EXTRACTS a value. Neither is spellable in the other, so the honest paydown was a new
  sibling in the center rather than a conversion. ⚑ All four verified still REFUSING (not merely
  still importing), by fire-probe from a foreign cwd — *the discriminator a "uses the center" test
  alone would miss.*

  ⚑ **TWO ITEMS FOR THE OPERATOR:** the new imports carry `# noqa: E402`, matching these files'
  own documented convention but against the no-`noqa` constraint — flagged, not assumed. And
  `hook_shellcheck`'s docstring names an adoption manifest `scripts/HOOKS.tsv` **that does not
  exist anywhere in the tree**, newly load-bearing because adopters now also need
  `substrate/ratchet_flags.py`.

* ⚑⚑⚑ **Ⓝ69a″ ⟡delegating-vs-bare — A FIFTH SHAPE IS PRESENT, AND IT HIDES BY BEING
  MIS-BUCKETED RATHER THAN UNCLASSIFIED.** `suite_gap`'s `dispatch_only` count of 2 is a fact about
  the instrument: `sandbox_connect.py` holds `def _selftest` and `type_scope.py` holds `def _cases`,
  both top-level, both holding real cases — and `TAIL_SUITE = ^def selftest\s*\(` matches neither.
  **They are `tailed` (owed a SPLIT) reported as owed a NEW SUITE**, so writing one would duplicate
  cases that already exist — *precisely the miss `delegating` was added to prevent, recurring one
  category over.*

  ⚑⚑ **AND THE FIX IS NOT WIDENING THE REGEX TO `_?selftest`.** `_cases` is a THIRD spelling, and
  the census must agree with `module_trim` about what a tail IS — **widening the census without
  widening what the SPLIT TOOL can move would point at work no tool can do.** The honest shape is
  a predicate keyed on the CAPABILITY (a top-level def owning cases), cross-checked with a second
  spelling. ⚑ The ordered partition is why nothing reads as unclassified.

* ⚑⚑ **Ⓝ97 ⟡plc0415 — 1450 REPO-WIDE, AND THE MEASUREMENT THAT MATTERS IS THE ONE THAT SEPARATES
  LEGACY FROM PROPAGATION.** `substrate/` carries **ZERO**. So the danger the item names — an
  author reading `store.py`'s carefully-argued lazy imports as sanction — **has not materialised**;
  the 1450 are older unratcheted trees. ⚑ The zero is enforced BY CONSTRUCTION (the write gate
  refuses PLC0415 on every edit there), not by authorial restraint — *inferred, and stated as
  inferred.* ⚑ `PLC0415` appears in NO `per-file-ignores` entry, so ruff cannot distinguish
  sanctioned debt in a frozen file from a finding that would refuse the next edit.


* ⚑⚑⚑ **Ⓝ133c ⟡structural-hook-is-cwd-scoped — THE REFUSAL DEPENDS ON WHERE YOU STAND, NOT ON
  WHAT YOU TOUCH, AND THE TWO HOOKS DISAGREE ABOUT THIS.** Fire-probed during Ⓝ133a with the
  operand held FIXED as an absolute path into the repo, varying only the cwd:

      cwd = repo   grep -r foo /home/…/substrate/catalog/worklist/toolmodes-split.md   REFUSED
      cwd = /tmp   grep -r foo /home/…/substrate/catalog/worklist/toolmodes-split.md   RAN, exit 1
      cwd = /tmp   bash -c 'echo a | cat'                                              REFUSED

  ⚑⚑ **SO `hook_structural_query` SCOPES BY CWD AND `hook_no_chaining` DOES NOT.** The same
  textual query against the same structured artifact is a violation from one directory and
  permitted from another — *and the admitted case exits 1 for want of a match, which reads
  exactly like a legitimate empty answer.* **A textual read of a `.md` that returns "nothing
  found" is precisely the false zero this shard exists for**, arriving with the gate that would
  have caught it silently out of scope.

  ⚑ **THE DIRECTION MATTERS: `/tmp` IS WHERE THE FIRE-PROBES RUN.** Every acceptance in this arc
  verifies hooks "from a foreign cwd" — which is the one position where this hook cannot refuse.
  *An acceptance ritual standing in the blind spot of the thing it certifies.* ⚑ Not repaired
  here: `hook_structural_query` is a five-hook set with a `check_hook_set` manifest, and changing
  refusal scope is a policy act with a firing gate attached. **Reported with its probe, both arms
  live.**


* ⚑⚑⚑ **Ⓝ133c ⟡the-ritual-in-the-blind-spot — MY DIAGNOSIS WAS WRONG AND THE TRUTH IS WORSE.
  THERE IS NO CWD-SCOPING.** `hook_structural_query.verdict()` keys purely on the ARGUMENT'S SUFFIX
  against the routing table; it consults no cwd, its `claims()` docstring **explicitly rejects a
  location test as unportable**, and a selftest already pinned *"a `.py` in ANOTHER repo is still
  claimed."* ***I observed a real bypass and attributed it to a policy the code does not have.***

  ⚑⚑⚑ **THE DEFECT IS IN THE SHARED TOKENIZER: `hook_cmdparse.programs()` SKIPPED A WRAPPER'S FLAG
  BUT NEVER THE FLAG'S ARGUMENT.**

      env -C /tmp grep …        program read as `tmp`      grep INVISIBLE
      timeout -s KILL 60 grep   program read as `KILL`     grep INVISIBLE
      sudo -u nobody grep …     program read as `nobody`   grep INVISIBLE

  ⚑⚑ **SO THE BYPASS HAD NOTHING TO DO WITH LOCATION** — `env -C <repo-path> grep` from INSIDE the
  repo also ran. **A parser defect wearing the costume of a policy decision, and I read the
  costume.** ⚑ `hook_no_chaining` was immune only because it scans for a `-c` token directly rather
  than through `programs()`.

  ⚑⚑⚑ **AND `programs()`' OWN DOCSTRING NAMED THE BROKEN CASE AS ITS WORKED EXAMPLE:**
  *"A wrapper's own flags (`env -i`, `timeout -s KILL`) are skipped too."* ***`timeout -s KILL` was
  precisely the one that failed; `env -i` passed only because `-i` takes no argument.***
  **A comment illustrating a capability with the instance that disproves it.**

  ⚑ **VERIFIED BY ME, BOTH BEFORE AND AFTER:** the exact command that returned an answer earlier
  now **hits the gate and names the owning tool.**

* ⚑⚑ **THE FIX IS A WIDENING, AND ITS BLAST RADIUS IS FIVE REPOS AT WRITE TIME.**
  `_FLAGS_WITH_ARG` — a per-wrapper map of flags taking a SEPARATE argument, with attached forms
  (`-C/tmp`, `--chdir=/tmp`) cased so they do not double-skip. ⚑ **`hook_cmdparse.py` is vendored
  and live without a commit**, so *commands previously invisible now reach the verdict* — **it
  cannot make a passing command fail except where that command was bypassing a gate.**
  ⚑ `_is_operand` deliberately NOT extended: *it is value-shaped, and a flag's argument can be any
  string.*

* ⚑⚑⚑ **THE NEW PROBE FOUND TWO DEFECTS IN ITSELF, BOTH REACHABLE ONLY BECAUSE IT DRIVES REAL
  SUBPROCESSES.**
  **The unarmed arm was not unarmed** — `.claude/settings.json` exports the arming vars into the
  session, so `{**os.environ}` inherited them: ***a probe testing "hook off" was testing "hook
  on."***
  ⚑⚑ **And `tool_name` was missing from the payload**, so `hook_shellcheck` dispatched on nothing,
  found no `"Bash"`, and **returned 0 having analysed nothing** — ***the probe reported ALLOW for a
  command whose SC2086 the same hook prints on demand.*** **A false silence manufactured by the
  probe's own fixture**, in the instrument built to detect false silences.

  ⚑ `scripts/hook_fire_probe.py` + `hook_fire_run.py`: twelve rows × two arms, **every verdict
  asserted including the five where correct behaviour is SILENCE** — *an unasserted silence is the
  vacuous-case shape.* **Deliberate-failure demonstrated**: removing `-C`/`--chdir` from the `env`
  entry turns both arms red naming the regression; restored, green.

* ⚑⚑ **THE `/tmp` CORRECTION IS CORROBORATED BY A MEASURED INCIDENT IN THIS TREE.**
  `substrate/worklist_engine.scratch_root` records **`/tmp` on this box as a small shared tmpfs that
  FILLED TWICE**, after which children failed at spawn with ENOSPC — *"reads as THE TOOL IS BROKEN
  rather than THE VOLUME IS FULL."* ⚑ The probe now derives its foreign directory via
  `tempfile.mkdtemp()` (honouring `TMPDIR`), **creates and removes it** so the arm is hermetic, and
  **CHECKS its foreignness via `project_root.project_for`** — *if it lands inside a project the
  probe says so and fails rather than testing the wrong relation.* ⚑ Census: **68 `mkdtemp` sites
  already derive correctly** against three real `/tmp` literals.

  ⚑⚑⚑ **AND THE INJECTION AND THE HOLE POINTED AT THE SAME GAP.** The MCP "auto mode" directive
  tells agents to use `cat`/`grep`/`sed` — **the exact shape this hook refuses, and until this fix
  the exact shape that succeeded behind ANY flag-taking wrapper.** *Worth taking as an adversarial
  signal rather than an annoyance.*
