# Ⓝ31 residue — the codemod pipeline

**Concern: the machinery that performed the migration — transform, stage, autofix, check, refuse
— and every defect it caught before anything reached disk.** Index and arc frame:
[`toolmodes-split.md`](toolmodes-split.md).

⚑ Ⓝ31s⁴ ⟡check-the-prospective-output is the operator's correction that made a 67-file batch
safe, and it earned out six times. Ⓝ31s⁹ ⟡wrong-matcher-control is cassian's correction that a
bare positive control is a transport-200. Ⓝ44 made the batch readable; the thirteen-file and
five-file mysteries are here in full, including the two diagnoses that were refuted by
measurement and the probe that settled it in two lines. `module_trim` and the apply-loop's
mutation testing close it out.

⚑ **THIS IS THE LARGEST PART AND IT IS ONE THREAD** — a mechanical rewriter learning to verify
its own output — so it is long because the argument is, not because the cut was lazy.

## Residue

* ⚑⚑⚑ **Ⓝ31s⁴ ⟡check-the-prospective-output — THE CODEMOD MUST RUN THE HOOKS ON WHAT IT IS ABOUT
  TO WRITE, AND I HAD DESIGNED IT TO WRITE AND HOPE.** Operator, 2026-09-01: *"your codemod needs
  to run all of the hooks on its prospective output before it makes those changes."*

  I had been reading the per-file gate as an obstacle to the codemod's OWN source (`N802` forbids
  the `visit_ClassDef` method names libcst's `VisitorBasedCodemodCommand` API mandates; `INP001`
  fires on `scratch/`). That framing produced a wall and a policy question. **It was the wrong
  frame**: the codemod's job is to emit 66 files that must EACH pass, so validating the
  prospective output is not an extra safeguard — it is the tool's actual contract.

  ⚑⚑ **AND IT IS THE `split_lemmas` CONSERVATION GUARD ONE LANGUAGE OVER.** That splitter refuses
  to write unless every non-blank body line lands in exactly one unit, and it has caught SEVEN
  distinct silent-deletion bugs. The discipline is identical: **a mechanical rewriter verifies its
  output before committing it, because a plausible-looking wrong output is exactly what a regex or
  a CST transform produces best.**

  **THE SEAM EXISTS: `scripts/pycheck_show.run_checks(target) -> str`** — runs ruff and mypy under
  the HOUSE config (passed explicitly, because a checker that discovers its own config is *"a
  checker that agrees with you"*) and returns their output. Empty means clean.

  ⚑ **THREE PROPERTIES OF THAT FUNCTION ARE LOAD-BEARING AND MUST NOT BE RE-DERIVED:**
  - **The config is passed explicitly**, and the temp file must sit INSIDE the project — ruff and
    mypy walk upward to discover configuration, so a tempfile in `/tmp` is checked under different
    rules than the file it stands for.
  - **Exit 2 is `COULD NOT RUN`, not a clean bill.** ruff and mypy both use 1 for "flagged
    something" and 2 for a broken invocation. `summit-1c`'s probe read a rejected config as "no
    findings" — a GREEN whose cause was a broken instrument, inside a probe written to test an
    instrument. The codemod must carry that third state through, never collapse it into pass.
  - **`--pretty` and the `EXE001,EXE002` exclusion** encode which QUESTION is being asked (the
    edit, versus the file as it sits on disk). Copying the hook's argv without them inherits the
    hook's omissions — the function's own docstring records making exactly that mistake.

  **THE REDESIGN, which also dissolves the `N802` block:**
  1. The TRANSFORM (libcst visitor, mandated method names) is one module.
  2. The ORCHESTRATOR — walk, transform, write to a temp path inside the project, `run_checks`,
     decide — is a SEPARATE module with ordinary method names. Only the transform needs the API
     that trips `N802`, and whether that module can land is now a smaller question than whether
     the whole approach can.
  3. **A file that would land dirty is never written.** Its findings go to a work list instead,
     which is `codemod_store_reads`' own stated rule: *"the mechanical 90% and PRINTS the residue
     as a worklist. A tool that silently 'handled' the other 10% would be worse than one that
     names it."*

  ⚑ **THIS IS WHAT MAKES 66 FILES IN ONE PASS SAFE.** Serially, each refusal reverts one file and
  costs a re-derivation. With prospective checking, nothing is written until it is known to pass —
  so the batch either lands clean or reports exactly which files need a human, and the
  keyless-sort / numeric-subscript finds arrive as a LIST rather than one surprise per file.


* ⚑⚑⚑ **Ⓝ31s⁷ ⟡grandfathered-is-the-design, NOT AN ANOMALY — AND A SHARED GATE IS NOT EVIDENCE
  OF A SHARED SOLUTION.** I observed that `scratch/codemod_store_reads.py` is loaded with findings
  and passes only because nobody edits it, and filed it as debt peculiar to this repo. paperkit
  measured their own tree and corrected the reading:

      uv run ruff check --statistics paperkit/ tools/ checks/   →  3,832 findings

  Their `pyproject.toml` states it as policy: *"the tree meets it file-by-file as each file is
  next edited — which is what a PER-FILE gate makes possible. A tree-wide count is not the thing
  being enforced; a file is."* **So the grandfathering is the DESIGN, on both sides**, and a
  red-but-untouched file is the expected state rather than a lapse.

  ⚑⚑ **AND THE INFERENCE I DREW FROM THE SHARED HOOKS WAS BACKWARDS.** I told paperkit that
  because we run the same gate, their solution would be *"directly portable rather than an
  analogy."* Their reply: *"it cuts the other way — because the gate is shared and paperkit has
  3,832 outstanding findings, the shared gate is not evidence that anyone has solved anything. A
  peer's clean file proves someone EDITED it; a peer's dirty file proves nothing was NEEDED there.
  Neither is a pattern."* Treat a shared constraint as RAISING the value of a measured answer and
  LOWERING the value of a remembered one — which is why they ran the counts before replying.

  **MEASURED, and it retires the premise this whole detour rested on:** paperkit has **no libcst
  shim and has never hit the problem** — `--binding visit_ClassDef` → 0 in 125 files; the one file
  mentioning libcst is `bibstruct.py`, OUR file adopted there and excluded from their lint by
  ownership. Their AST work is stdlib `ast`, read-only. Their only two N802 sites are `F_of` and
  `W` — mathematical notation, both grandfathered, neither an API contract. **There is no pattern
  to copy; the operator's recollection is most likely of their `Any`/`T201` boundary discipline,
  a different rule and a different shape.**

  ⚑ **paperkit REFUSED TO INVENT ONE FOR THE REPLY, AND WAS RIGHT TO:** *"Please do not take a
  design from me here — building on a shim I'd have to invent for this message is the worst case:
  you would be copying a pattern that has never run."* An absence reported as an absence, with the
  measurements that establish it.

* ⚑⚑ **Ⓝ31s⁶ ⟡api-name-shim — THE RECOMMENDATION IS TO NOT BUILD A SHIM.** paperkit's reasoning,
  offered explicitly as reasoning rather than precedent: **a per-file ignore on the ONE codemod
  module, held sole and bounded by `scripts/check_ignore_holder.py`, writes `visit_ClassDef` as a
  real `def` — the only form guaranteed to survive ANY dispatch mechanism.** Every shim shape
  (base class, `__getattr__`, metaclass) adds a layer whose interaction with libcst's dispatch
  must then be PROVEN, and the proof is the hard part.

  **Their test for whether a scoped rule is legitimate, worth adopting verbatim:** *"is this rule
  wrong for our DOMAIN, or wrong for our CONVENIENCE? A short ignore list of domain-conflicts is a
  bar; a growing list of convenience-waivers is a subset wearing a bar's name."* `visit_ClassDef`
  is a THIRD-PARTY API CONTRACT, not a naming preference — domain, cleanly. Their own instance is
  `T201`, scoped per-file to entrypoints whose stdout IS their verdict protocol and refused
  tree-wide, **after measuring the population** (1,021 findings over 138 files, 51 files with ≤3
  prints — smeared rather than concentrated, so a tree-wide waiver would have surrendered the
  signal to buy silence).

  ⚑⚑⚑ **AND THE DISPATCH QUESTION MUST BE MEASURED, NOT READ.** A visitor method that binds wrong
  is NEVER CALLED — no error, exit 0, zero files changed, indistinguishable from "no matching
  nodes". paperkit's instrument: **a two-method probe, one visitor a real `def` and one
  deliberately aliased wrong, over a file containing both node kinds — see which fires.** An F arm
  whose mutation is *"the binding is broken"*, because an inspection cannot settle it and a
  confident source read is exactly what produces a silent green. (They declined to guess at
  libcst's internals on precisely these grounds.)

* ⚑ **`uv sync` IS BROKEN IN THIS TREE** — `uv run` fails because substrate depends on `paperkit`,
  which is not in the package registry (their Ζ·wheel·library gap; on their board). Workaround:
  invoke `python3` / `.venv/bin/python` directly, which is what this session has done throughout.


* ✅ **Ⓝ31s⁶ ⟡api-name-shim — DISSOLVED, NOT SOLVED. NO SHIM, NO EXCEPTION, NO GATE CARVE-OUT.**
  `linux-sources` read libcst **v1.9.0** (pinned upstream `c029c17bf45a…`, fetched as a corpus
  rather than read from our venv) and walked every hop rather than stopping at "decorators exist":

  - **Q1 — resolution is plain `getattr` AT DISPATCH TIME.** `libcst/_visitors.py:42` (and `:121`):
    `visit_func = getattr(self, f"visit_{type(node).__name__}", None)`. Not a class-creation table,
    not a `dir()` scan. So both aliasing strategies WOULD have worked — and neither is needed.
  - **Q2 — THE DECORATOR MAKES THE NAME STOP BEING THE CONTRACT.** Chain verified:
    `VisitorBasedCodemodCommand` (`codemod/_command.py:174`) → `ContextAwareTransformer`
    (`codemod/_visitor.py:16`) → `MatcherDecoratableTransformer` (`matchers/_visitors.py:440`).
    `_gather_constructed_visit_funcs` (`:304`) iterates `dir(obj)` and keys each handler by the
    **matcher attribute the decorator stamps**, never by its name; `on_visit` (`:493`, line 498)
    fires them via `_visit_constructed_funcs`.
    ⚑⚑ **AND libcst ACTIVELY FORBIDS THE CONCRETE NAME ON A DECORATED METHOD** —
    `_assert_not_concrete` (`:321`) raises `MatchDecoratorMismatch` iff `func.__name__` is in
    `CONCRETE_METHODS`. **Snake_case is not tolerated, it is the INTENDED shape.**

  ⚑⚑⚑ **Q3 — THE TWO PATHS HAVE OPPOSITE FAILURE MODES, AND THE SHIM WOULD HAVE REINTRODUCED THE
  SILENCE I WAS TRYING TO AVOID:**

  | path | a mis-bound handler |
  |---|---|
  | name-based (shim/alias) | **SILENT.** `getattr` → None → `on_visit` returns True → children visited, no error, exit 0, ZERO FILES CHANGED. No strict mode, no unrecognised-name warning, no registry. |
  | decorator-based | **LOUD AT CONSTRUCTION.** `__init__` (`:470-481`) runs `_check_types` → `_verify_parameter_annotations` / `_verify_return_annotation`; a malformed handler raises `MatchDecoratorMismatch` on INSTANTIATION. |

  **So the safe route and the N802-clean route are the same route.** Every shim shape would have
  bought the forbidden-name problem back AND the silent no-op with it.

  ⚑ **THE HONEST RESIDUAL, flagged rather than buried:** a WRONG MATCHER
  (`@m.visit(m.FunctionDef())` when `m.ClassDef()` was meant) binds fine and fires on the wrong
  node, silently. The decorator path removes *"never called at all"*, not *"called on the wrong
  node kind"*. **A positive control is still owed** — assert the handler fired on a known input,
  and that the changed-file count across the 67 is non-zero — but it guards a narrower and
  harder-to-hit gap than the name route's.

  ⚑ **AND GO ALL-DECORATOR, NOT MIXED:** `on_visit` (`:510`) still runs the concrete `getattr`
  path AFTER the decorated funcs, so a stray `visit_X` would also fire. All-decorator leaves N802
  nothing to flag anywhere.

* ⚑⚑ **WHAT THE THREE-PEER CONSULT ACTUALLY PRODUCED, worth keeping as method.** The premise I
  opened with ("paperkit, linux-sources and cassian all hit this and shimmed it") was FALSE —
  paperkit measured and had never met it. Two peers then declined to guess: paperkit refused to
  invent a shim shape for the reply (*"you would be copying a pattern that has never run"*), and
  linux-sources was asked to say "not plainly shown" rather than infer — and instead came back
  with a byte-cited chain because the source DID show it plainly.

  **The answer that landed was not the one the premise sought.** A remembered pattern would have
  produced a shim; a source read produced the finding that the shim was the DANGEROUS option. ⚑
  paperkit's own framing of this: treat a shared constraint as *"raising the value of a MEASURED
  answer and lowering the value of a remembered one."*
* ⚑⚑⚑ **Ⓝ31s⁹ ⟡wrong-matcher-control — A BARE POSITIVE CONTROL IS A TRANSPORT-200, AND I HAD
  SETTLED ON THE WEAKER FORM.** cassian-observability, asked whether read-your-write was
  over-engineering for an in-process visitor, answered that it is **the same discipline** and that
  the bare control *"is the weaker version that can still lie green."*

  **THE FAILURE ONE LEVEL IN:** a binding that aliases `visit_Call` correctly and `visit_ClassDef`
  WRONG fires on the Call, the control goes green, and the ClassDef conversion silently visits
  nothing. ⚑ *"A single positive control over 'something fired' inherits exactly the omission you
  named from `pycheck_show` — it cannot report the binding it does not test."*

  **THE READ-YOUR-WRITE FORM, mapped onto a visitor:** PLANT a known node of EACH kind the codemod
  claims to handle, and assert the transform TOUCHED THAT SPECIFIC PLANTED NODE — leaving a marker
  only that handler could produce. Not *"a visitor fired"* but *"the ClassDef handler fired ON A
  ClassDef I planted and left the mutation only it produces."* The value you control is the
  planted node plus its expected mutation; the read-back is the post-transform assertion that THAT
  node changed THAT way.

  ⚑⚑ **AND THE COST ARGUMENT IS WHAT SETTLES IT — the risk is PER-BINDING.** Each handler can
  independently bind wrong, the failure shape is the worst one (green, exit 0, zero files, reads
  as *"nothing to convert"*), and the extra cost is one planted node + one marker assertion per
  claimed visitor — **bounded by the node kinds dispatched on, which is small and enumerable.**
  cassian's framing: *enumerate the bindings you CLAIM (finite, a whitelist) rather than trust
  "something fired" (a proxy that quantifies over nothing).*

  ⚑ **IT ALSO REDESIGNS THE F-ARM.** The two-method probe (one real handler, one deliberately
  mis-bound) is the right SHAPE, but each arm must assert it touched ITS OWN planted node with ITS
  OWN marker. Otherwise the broken arm is absorbed into a file-level *"something changed"* and
  fails silently — the exact absorption the probe exists to prevent.

  **STATUS: NOT BUILT.** The design is settled; `record_transform.py` currently claims three
  handlers (`ClassDef` leave, `Call` visit, `Subscript` visit, plus `Module` leave), so the
  control needs four planted nodes and four marker assertions.

* ✅ **Ⓝ31s⁴ — `substrate/record_transform.py` LANDED, GATE-CLEAN, ALL-DECORATOR.** The approach
  linux-sources' source read predicted works exactly as described: `@m.leave(m.ClassDef())` and
  `@m.visit(...)` on snake_case methods satisfy libcst AND ruff N802 simultaneously. **No shim, no
  exception, no gate change.** ⚑ And the operator's correction was needed: the matcher must be
  INSTANTIATED — `@m.visit(m.ClassDef())`, never `@m.visit(m.ClassDef)`.

  ⬜ **`substrate/record_migrate.py` — the orchestrator — is ONE FINDING from landing.**
  `checks.run_checks` on a path-loaded module is `Any`, and `str()` around it does not confine it;
  the fix is an annotated `object` binding plus a `callable` guard.

  ⚑⚑ **AND THE ORCHESTRATOR HIT THE DEFECT IT EXISTS TO PREVENT.** I assumed `gate_module`
  returned a module; it returns `(module, why)`. The repair improved it: an unimportable checker
  now returns `COULD NOT RUN` rather than `""`, because empty would have rendered as CLEAN and
  written 67 files on the strength of a check THAT NEVER RAN.


* ✅ **Ⓝ31s⁴ ⟡check-the-prospective-output — THE CODEMOD IS BUILT AND THE CONTRACT IS PROVEN.**
  `substrate/record_transform.py` (the matcher-decorated transform) and
  `substrate/record_migrate.py` (the orchestrator) are both landed and gate-clean. A single-file
  dry-run demonstrates the whole sequence:

      CLEAN     substrate/tool_cli.py  (2 record(s): Refusal, Parsed)
         ⚑ rest[0] — a POSITION identifying a thing; destructure by name instead
         ⚑ args[0] — a POSITION identifying a thing; destructure by name instead
      1 clean · 0 with findings · 0 UNKNOWN · 2 site(s) needing a human
         (--dry-run: nothing written)

  Transform → stage INSIDE the project → house checker → refuse to write → report the residue.

  ⚑⚑⚑ **AND THE PROSPECTIVE CHECK CAUGHT FOUR OF THE TRANSFORM'S OWN BUGS BEFORE ANY WRITE.**
  Every one produced a CORRECT conversion that COULD NOT LAND, and every one was invisible until
  the output was checked rather than assumed:
  1. `NamedTuple` left in the `typing` import with no remaining use → `F401`. Fixed; the whole
     statement is removed when it was the only name (an empty `from typing import` is a syntax
     error, so remove-the-name and remove-the-line are different repairs).
  2. The added import appended after `typing` → `I001`. Fixed by inserting at SORTED position.
  3. With `typing` gone, `__future__` became the only import and `dataclasses` landed flush
     beneath it → `I001` again. `__future__` is its own isort SECTION and sorts AFTER
     `dataclasses` lexically, so it needs an explicit exception plus an owned blank line.
  4. ⬜ **OPEN:** that owned blank line is now WRONG in the common case — a file with plain
     `import x` lines gets `from dataclasses` separated from the stdlib group it belongs to.

  ⚑⚑ **BUG 4 SAYS THE APPROACH IS WRONG, NOT THE PLACEMENT: I am reimplementing isort inside the
  transform, badly, one special case at a time.** `ruff --fix` OWNS import sorting and is already
  invoked by the checker this tool calls. The transform should insert the import ANYWHERE valid
  and let `ruff --fix` place it — which is `feedback_fix_infra_not_route_around` (conform to the
  tool; do not rebuild its core) arriving in the middle of a codemod. Each of bugs 2, 3 and 4 was
  one more hand-rolled clause of a sorter that already exists.

  ⚑ **NONE OF THE FOUR REACHED DISK.** That is the operator's correction working exactly as
  intended: *"your codemod needs to run all of the hooks on its prospective output before it makes
  those changes."* A write-and-hope version would have landed four bad files and had them reverted.

  **THE FULL SURVEY RAN** (`--dry-run substrate/`, 29.6 KB): every file reports FINDINGS on bug 4,
  and the flags are already visible as a work list — `keyless sorted()` in `argument_consumed`,
  `arm_shape`, `case_count`; `found[0]` in `ban_witness`. ⚑ The residue is real and enumerable
  BEFORE any conversion, which is what the batch approach was for.




* ✅ **Ⓝ31s⁹ ⟡wrong-matcher-control — DONE. `record_transform_selftest` 20/20, PER BINDING.**
  Five handlers, five planted nodes, and each arm asserts THAT node carries the mutation only
  THAT handler produces — never merely that the source changed.

  | handler | planted | the mutation only it produces |
  |---|---|---|
  | `@m.leave(m.ClassDef())` | a `NamedTuple` record | the decorator added AND the base dropped |
  | `@m.leave(m.ImportFrom(typing))` | a sole-name import | the whole statement removed |
  | " | a shared import | `NamedTuple` gone, `TYPE_CHECKING` kept |
  | `@m.visit(m.Call(sorted…))` | `sorted(items)` | a flag naming FIELD POSITION |
  | `@m.visit(m.Subscript())` | `pair[0]` | a flag naming `pair[0]` and POSITION |
  | `@m.leave(m.Module())` | a converted record | the dataclass import supplied, exactly once |

  ⚑⚑⚑ **THIS IS cassian's CORRECTION IMPLEMENTED, NOT THE CONTROL I HAD PLANNED.** I intended a
  bare positive control — *"assert a handler fired on a known input"* — which they identified as a
  transport-200: *"it proves dispatch happened, not that the RIGHT dispatch happened on the node
  you care about."* Their case: bind `Call` right and `ClassDef` wrong, the Call fires, the
  control greens, the conversion silently visits nothing. **The population each arm asserts over
  is now {one planted node per claimed handler}, not {did anything happen}.**

  ⚑⚑ **AND TWO F ARMS PIN THE DISCRIMINATION, which the positive arms cannot.** A keyed
  `sorted(items, key=Row.rank)` must NOT flag, and a string subscript `mapping["name"]` must NOT
  flag — without these, a handler that flagged EVERYTHING would pass every positive arm. A control
  that only ever asserts the positive cannot tell a working predicate from a constant one.

  ⚑⚑ **THE STRONGEST ARM IS THE UNTOUCHED ONE:** a module declaring no record must come back
  BYTE-IDENTICAL. A transform that added its import unconditionally would pass every other arm and
  dirty ~200 files that need nothing — and in a 67-file batch that damage is invisible per file.

  ⚑ **PLUS THE ONE libcst GIVES FREE:** constructing the transform runs `_check_types` over every
  decorated handler, so a malformed signature raises `MatchDecoratorMismatch` at instantiation
  rather than silently never firing. It cannot see a WRONG MATCHER — that is precisely what the
  planted-node arms cover, and the residual linux-sources flagged honestly.

  **THE BATCH IS NOW GATED ON NOTHING BUT REVIEW.** `--dry-run substrate/` enumerates the residue
  (29.6 KB, ⚑ unreadable without paging — Ⓝ44), and `--apply` writes only files the house checker
  passed clean.

* ✅ **Ⓝ44 ⟡migrate-needs-paging — DONE. `--summary` MAKES THE BATCH READABLE, AND THE PICTURE IS
  THE ARC'S THESIS MEASURED.** One line per file plus the residue grouped BY KIND, replacing a
  29.6 KB dump that could not be read without the shell composition the hook refuses.

      50 clean · 13 with findings · 0 UNKNOWN · 75 site(s) needing a human

      keyless comparison   38 site(s) across 34 file(s)
      numeric subscript    37 site(s) across 21 file(s)

  ⚑⚑ **75 SITES WHERE MEANING IS CARRIED BY POSITION, ACROSS A QUARTER OF THE PACKAGE** — measured
  over all 67 files rather than extrapolated from the four converted by hand. 38 orderings nobody
  chose (a keyless `sorted`/`min`/`max` comparing by field declaration order) and 37 positions
  standing in for identities. `⟡symbolic-reference-only` is not a type migration that happens to
  surface issues; the issues ARE the subject and this is their census.

* ⚑⚑⚑ **Ⓝ31s⁶ ⟡the-13 — ONE SHARED CAUSE, AND IT IS A HOLE IN MY OWN CONTROL.** Read two of the
  thirteen (`deadline_floor.py`, `edge_census.py`, both `0 flag(s)` so nothing else is in play):

      F821 Undefined name `dataclass`  →  @dataclass(frozen=True, slots=True)

  **The import is simply absent from the output.** `_add_import` did not place it, on files whose
  import block is not a plain run — `deadline_floor` has `from __future__`, a stdlib group, a
  `from substrate import …`, and then an `if TYPE_CHECKING:` block containing a nested import.

  ⚑⚑⚑ **AND `record_transform_selftest` PASSES 20/20 WHILE THIRTEEN REAL FILES FAIL.** That is
  precisely the residual cassian named and I acknowledged and then did not close: the control
  asserts each handler fires on ITS OWN planted node, but **the planted nodes all have the shape I
  thought of.** `the_module_handler_adds_the_import` uses a fixture whose imports are one simple
  block; it never plants a `TYPE_CHECKING` block, so the arm is green and the handler is wrong.

  **A per-binding control is not a per-INPUT-SHAPE control**, and the second is what a batch over
  a real corpus needs. The fixtures were written FROM the handler — the same
  `Ⓝ31i ⟡parity-expires` defect (a suite inherits the blind spot of whoever wrote both), arriving
  in the suite built to prevent a blind spot.

  ⚑ **THE DRY-RUN CAUGHT IT ANYWAY, WHICH IS THE OPERATOR'S CORRECTION EARNING ITS KEEP A FIFTH
  TIME.** Thirteen files that would have landed `F821`-broken were reported instead of written.
  The control missed it; the prospective check did not. **Two instruments with different blind
  spots, and the batch needed both.**

  **NEXT:** plant the real shapes — a `TYPE_CHECKING` block, a `from substrate import` after the
  stdlib group, a module whose only import is `__future__` — as ARMS, then fix `_add_import`. The
  thirteen are one fix, not thirteen.


* ⚑⚑⚑ **Ⓝ31s⁶′ — THE ARMS LANDED AND PASSED, WHICH REFUTES MY DIAGNOSIS OF THE 13.**
  `record_transform_selftest` is **23/23** with three new fixtures planting the shapes I claimed
  were missing — a `TYPE_CHECKING` block, a `from substrate import` after the stdlib group, and a
  `__future__`-only module. **The handler works on all of them.**

  I had written that `_add_import` "silently placed nothing on every file with a `TYPE_CHECKING`
  block" and filed it as one shared cause. **That was a hypothesis stated as a finding**, from two
  files sharing a symptom and a plausible mechanism. The arms were the right move and they
  falsified it — which is what an arm is for, and why writing them BEFORE the fix mattered.

  ⚑ **THE ARMS STAY REGARDLESS.** They pin three real input shapes nothing covered, and
  `Ⓝ45 ⟡per-binding-is-not-per-shape` remains true as a class even though this instance was not
  it. A control whose fixtures all have the author's imagined shape is still the weaker control.

  **WHERE THE CAUSE ACTUALLY IS, narrowed but NOT isolated:** `substrate/edge_census.py` is
  structurally identical to the passing fixture (`__future__`, `import sys`,
  `from typing import TYPE_CHECKING, NamedTuple`, `from substrate import …`, `if TYPE_CHECKING:`).
  The transform alone handles that shape. **The difference is that `record_migrate` runs
  `ruff --fix` on the staged file between the transform and the check** — and `F401` would remove
  a `from dataclasses import dataclass` it considers unused. The suite tests the transform WITHOUT
  the fix pass, so it cannot see an interaction between the two.

  ⚑⚑ **IF THAT IS THE MECHANISM, THE AUTOFIX IS DELETING THE IMPORT THE TRANSFORM JUST ADDED** —
  and `⟡let-ruff-place-it` bought placement correctness at the cost of an unmodelled interaction.
  **STATED AS THE HYPOTHESIS IT IS**, because the last one at this confidence was wrong: the
  next step is to stage one of the thirteen and read the file BETWEEN the transform and the fix,
  not to reason further.

  ⚑ **AND THE CONTROL'S REAL GAP IS NOW NAMEABLE:** it exercises `record_transform` in isolation
  while the ORCHESTRATOR's pipeline is transform → autofix → check. Whatever the mechanism turns
  out to be, a suite over one stage cannot see a defect that lives in the seam between two — the
  `fresh-and-accumulated-context-catch-different-defects` shape, applied to pipeline stages.

  **50 files still convert cleanly.** The thirteen are one cause, still unidentified, and the
  dry-run continues to refuse all of them rather than writing broken output.


* ✅ **Ⓝ31s⁶″ ⟡read-the-seam — MEASURED, AND THE CAUSE IS THE SEAM ITSELF.** A probe dumping
  `edge_census.py` at each pipeline stage settles it in one run:

      ── import after transform: True
      ── import after fix:       False

  **The transform ADDS the import; `ruff --fix` DELETES it as `F401` unused.** The autofix
  introduced by `⟡let-ruff-place-it` removes the very import the transform supplies.

  ⚑⚑ **WHY THESE THIRTEEN AND NOT THE OTHER FIFTY.** `_add_import` anchors after the LAST statement
  matching an import — and `m.findall` on an `if TYPE_CHECKING:` block matches the import NESTED
  INSIDE it, so the anchor becomes the `if` and the new import lands after the whole block, in a
  position ruff reads as dead. Files without that block get the import inside the real import run,
  where `--fix` leaves it alone.

  ⚑⚑⚑ **AND MY FIXTURE HAD THE BLOCK AND STILL PASSED**, which is why 23/23 coexisted with 13
  failures: the fixture's record sits BELOW the block, so the placement happened to work. **Two
  inputs with the same named shape and different outcomes — the shape was never the discriminator,
  and I had asserted twice that it was.**

  ⚑ **THREE DIAGNOSES, TWO WRONG, AND BOTH WRONG ONES WERE INFERRED RATHER THAN DUMPED.**
  (1) *"`_add_import` places nothing on `TYPE_CHECKING` files"* — refuted by arms that passed.
  (2) *"`ruff --fix` removes it"* — right mechanism, but I stated it before measuring and could
  not have said WHERE it was placed or WHY only these files. (3) The probe: printed the text at
  each boundary and the answer was two lines of output. **The measurement was available the whole
  time and cost one file; the inference cost two turns.**

* ⚑⚑ **Ⓝ46 ⟡suite-cannot-see-the-seam — CONFIRMED AS THE CLASS, not a suspicion.**
  `record_transform_selftest` exercises the transform in isolation and is 23/23. The defect exists
  only in the composition transform → autofix, so **no suite over either stage can see it** — and
  the prospective check caught it precisely because it runs the WHOLE pipeline on real files. Two
  instruments with different blind spots, and the batch needed both:

  | instrument | sees | blind to |
  |---|---|---|
  | `record_transform_selftest` | each handler's binding, on planted shapes | anything in a seam, and any shape not planted |
  | `record_migrate --dry-run` | the whole pipeline, on the real corpus | which STAGE is at fault (hence this probe) |

  **THE FIX:** insert the import inside the actual import RUN — anchoring on top-level
  `Import`/`ImportFrom` statements only, never on a compound statement that merely CONTAINS one.
  Then `--fix` sorts it rather than deleting it. ⚑ And the arm that pins it must be a file whose
  `TYPE_CHECKING` block is the LAST import-ish statement, which is the shape no fixture had.


* ✅ **Ⓝ31s⁶‴ ⟡anchor-top-level-only — FIXED. 50 → 58 CLEAN, and the arm was written FIRST and
  FAILED FIRST.**

      before:  50 clean · 13 with findings
      after:   58 clean ·  5 with findings

  `_is_import_line` inspects a statement's OWN body (`isinstance(part, cst.Import | cst.ImportFrom)`
  over a `SimpleStatementLine`) instead of searching its subtree with `m.findall` — so an
  `if TYPE_CHECKING:` block is no longer mistaken for an import line, the new import lands INSIDE
  the run, and `ruff --fix` sorts it rather than deleting it as unused.

  ⚑⚑⚑ **THE ARM FAILED BEFORE THE FIX, WHICH IS THE WHOLE POINT OF WRITING IT FIRST:**

      selftest: the import landed at line 11 — AFTER the TYPE_CHECKING block at 9, outside
      the import run, where `ruff --fix` deletes it

  A fixture reproducing the real defect, failing for the real reason, then passing. **Had the fix
  come first, a green suite would have said nothing** — and the two previous diagnoses show how
  easily that green would have been believed.

  ⚑⚑ **AND THE DISCRIMINATOR WAS POSITION, NOT PRESENCE.**
  `the_import_lands_beneath_a_type_checking_block` asserts the import EXISTS and passed on the
  BROKEN handler — presence was never the property that failed. The new arm asserts WHERE it
  landed relative to the block. **An arm checking the wrong property is indistinguishable from a
  passing one**, which is why 23/23 coexisted with thirteen broken files.

  **THE REMAINING FIVE ARE A DIFFERENT CAUSE:** `module_importers`, `name_collision`,
  `ratchet_log`, `self_import`, `tool_find` — all carry flags (3–6 each), unlike the eight just
  fixed which carried none. Not yet read; ⚑ and on this arc's record the next step is to DUMP
  one, not to infer from the correlation.

* ⚑⚑ **Ⓝ47 ⟡dump-dont-infer — THE TURN'S OWN LESSON, MEASURED.** Three diagnoses of the thirteen:
  1. *"`_add_import` places nothing on `TYPE_CHECKING` files"* — inferred from two files sharing a
     symptom. **Refuted** by arms that passed.
  2. *"`ruff --fix` removes it"* — right mechanism, still inferred; could not say WHERE the import
     was placed or WHY only these files.
  3. A probe printing the text at each pipeline boundary — **two lines of output settled it**
     (`import after transform: True` / `after fix: False`) and located the anchor bug.

  The measurement was available throughout and cost one scratch file. **The inference cost two
  turns**, and the second inference was *closer* to right, which is what made it more persuasive
  and no better founded.


* ⚑⚑⚑ **Ⓝ31s⁶⁗ ⟡the-five — TWO DIFFERENT CAUSES, AND ONE OF THEM IS NOT A DEFECT AT ALL.**
  Dumped two rather than inferring from the flags correlation (`Ⓝ47 ⟡dump-dont-infer`), and the
  two disagree — which the correlation would have hidden.

  **`tool_find.py` — NOT A BUG. THIS IS THE MIGRATION'S SUBJECT.**

      mypy: Value of type variable "SupportsRichComparisonT" of "sorted" cannot be "ModeHit"
      (three sites: :139, :150, :173)

  A keyless `sorted(ModeHit…)`. Under `NamedTuple` it compared by FIELD POSITION; as a slotted
  dataclass the checker refuses it. **Exactly what `tool_gap.capability_gaps` did on file one, and
  exactly what this codemod exists to surface.** The conversion is correct and the file needs a
  named `rank()` first — human work, not a transform repair.

  ⚑⚑ **SO `FINDINGS` CONFLATES TWO STATES THE READER MUST SEPARATE:** a file the transform
  MISHANDLED (the thirteen, now eight fixed) and a file whose RESIDUE IS LOAD-BEARING enough to
  block its own conversion. The first is my bug; the second is the arc's actual work arriving as a
  gate. **A single verdict for both makes a work list read as a defect list.**

  **`ratchet_log.py` — A REAL CODEMOD DEFECT, and a different one.**

      ruff: S603 `subprocess` call: check for execution of untrusted input  (:230)

  The original file carries a `# noqa: S603` on that call with a comment explaining why (module
  constants plus an env URL; the untrusted payload is JSON on stdin). **The transformed copy has
  lost the suppression** on a line the transform never touched — so something in the pipeline
  strips it, most likely `ruff --fix` reformatting the call and dropping the trailing comment.

  ⚑⚑⚑ **THAT IS THE AUTOFIX EDITING CODE OUTSIDE THE CONVERSION'S SCOPE**, which is a sharper
  problem than misplacement: `⟡let-ruff-place-it` handed the whole file to `--fix`, and `--fix`
  has opinions about every line, not just the imports. A codemod whose blast radius is "whatever
  ruff wants to change" is not the bounded transform this was designed as. ⚑ NOT YET CONFIRMED as
  the mechanism — the next step is to dump `ratchet_log.py` at the transform/autofix boundary the
  way `edge_census.py` was, not to act on this reading.

  **STATE: 58 clean · 5 with findings.** At least one of the five (`tool_find`) is CORRECT and
  waiting on human work; at least one (`ratchet_log`) is a pipeline defect. The other three
  (`module_importers`, `name_collision`, `self_import`) are unread.


* ⚑⚑⚑ **Ⓝ31s⁶⁵ ⟡noqa-stripped — REFUTED, AND THE REAL CAUSE IS A LIMIT ON THE VERIFICATION
  ITSELF: A PER-FILE-IGNORE KEYS ON THE PATH, AND THE STAGING FILE HAS A DIFFERENT PATH.**

  The dump refutes the hypothesis cleanly: `ruff --fix` moved `from dataclasses import dataclass`
  from line 28 into sorted position at line 25 and **preserved it** (`import after fix: True`).
  Nothing is stripped; the autofix does exactly its job.

  The file's own comment names the mechanism, three lines above the flagged call:

      # ⚑ THE S603 EXEMPTION IS IN `pyproject.toml`, KEYED TO THIS FILE.

  **`substrate/ratchet_log.py` is CLEAN** (`pycheck_show` confirms). The staged copy is
  `.record-migrate-staging.py` — a DIFFERENT PATH — so `[tool.ruff.lint.per-file-ignores]` does
  not match and `S603` fires on a call the project has deliberately exempted.

  ⚑⚑⚑ **THIS IS `run_checks`' OWN WARNING ARRIVING ONE LEVEL UP.** Its docstring: *"ruff and mypy
  discover configuration by walking up from the file they are given, and a checker pointed at the
  wrong config is a checker that agrees with you."* I put the staging file INSIDE the project so
  discovery would find the right `pyproject.toml` — and that is necessary but NOT SUFFICIENT,
  because a per-file rule keys on the PATH, not the directory. **The staged file inherits the
  project's config and not the target's exemptions.**

  ⚑⚑ **SO THE VERDICT FOR SUCH A FILE IS STRUCTURALLY WRONG IN THE SAFE DIRECTION.** It reports
  FINDINGS for a file that would land CLEAN, so nothing bad is written — but it is a FALSE
  NEGATIVE about writability, and a reader chasing it finds a defect that does not exist. I spent
  a turn on exactly that.

  **THE FIX IS TO STAGE AT THE TARGET'S OWN PATH**, not a fixed name: write the prospective text
  over the real file, check it, and restore the original from memory in a `finally`. ⚑ That trades
  a false verdict for a WRITE-AND-RESTORE window on a file the tool was designed never to touch
  until it passed — and on a crash the original is gone. **The alternative is to read
  `per-file-ignores` and re-apply the matching patterns to the staged path**, which duplicates
  ruff's own matching (`⟡let-ruff-place-it`'s lesson pointing the other way).
  ⚑ NOT DECIDED — the two options trade a real risk against a real duplication, and that is a
  scoping call rather than a detail.

  ⚑ **AND THE ARC'S OWN METHOD RULE HELD TWICE THIS TURN.** `Ⓝ47 ⟡dump-dont-infer`: the noqa
  hypothesis was plausible, specific, and wrong — the dump cost one command and refuted it, while
  acting on it would have bounded the autofix to repair a bug that was never there. **Three
  hypotheses about this pipeline, three refuted by measurement.** The pattern is now the finding.

* ⚑ **STATE: 58 clean · 5 with findings, and the five are at least THREE causes.**
  `tool_find` — correct conversion, blocked by its own keyless `sorted` (the arc's SUBJECT, human
  work). `ratchet_log` — a false FINDINGS from the staging-path exemption gap. The other three
  (`module_importers`, `name_collision`, `self_import`) remain unread, and the two read so far
  disagreed, so the correlation predicts nothing.


* ✅✅✅ **Ⓝ31s ⟡symbolic-reference-only — APPLIED. 58 FILES CONVERTED IN ONE PASS.**

      58 clean · 5 with findings · 0 UNKNOWN · 75 site(s) needing a human
      ✓ WROTE 58 file(s) — only the clean ones.

  Every written file had its prospective output transformed, autofixed, and checked by the house
  ruff+mypy BEFORE the write. The five unwritten ones are reported, not lost.

  **SPOT CHECKS GREEN:** `tool_census` 14/14, `ratchet_core` 7/7, `page` 18/18. Full
  `run_selftests` is running in background (>120s).

  ⚑⚑⚑ **WHAT THE MIGRATION BOUGHT, STATED AS THE PROPERTY RATHER THAN THE COUNT.** 58 files' worth
  of records can no longer be indexed or unpacked positionally. `row[0]` and `a, b, c = row` are
  now STATIC ERRORS naming their own line, because a slotted dataclass carries neither `tp_iter`
  nor the sequence protocol (CPython 3.13.1, byte-cited by `linux-sources`). **The type checker is
  the enforcement; symbolic reference is no longer a convention a reader must remember.**

  ⚑⚑ **AND THE 75 FLAGS ARE THE ARC'S ACTUAL SUBJECT, NOW ENUMERATED RATHER THAN SUSPECTED:**
  38 keyless comparisons across 34 files (orderings by field declaration order that nobody chose)
  and 37 numeric subscripts across 21 files (positions standing in for identities). Not defects
  introduced by the conversion — defects the conversion made VISIBLE, each one a place where
  meaning was carried by position and nothing checked it.

  **THE OPERATOR'S CORRECTION IS WHAT MADE THIS SAFE**, and it earned out six times: four
  transform bugs (`F401` on the stale `typing` import, three successive `I001` placements), the
  `TYPE_CHECKING` anchor bug that broke thirteen files, and the staging-path exemption gap. **None
  reached disk.** A write-and-hope codemod would have landed all six and had the gate revert them
  one file at a time.

* ⚑ **THE FIVE THAT REMAIN ARE THREE DIFFERENT THINGS, and the distinction matters more than the
  count:**
  - `tool_find` — the conversion is CORRECT; its own keyless `sorted(ModeHit…)` blocks it. Human
    work, and the arc's subject arriving as a gate.
  - `ratchet_log` — a FALSE findings: `per-file-ignores` key on the path, and the staged copy has
    a different one, so an exemption the project granted does not apply (Ⓝ31s⁶⁶).
  - `module_importers`, `name_collision`, `self_import` — unread. ⚑ The two read disagreed, so the
    correlation predicts nothing; dump each rather than infer.


* ✅ **Ⓝ31s⁶⁷ ⟡the-remaining-three — ALL FIVE NOW READ, AND FOUR ARE ONE CAUSE.**

  | file | cause | verdict |
  |---|---|---|
  | `tool_find.py` | keyless `sorted(ModeHit…)` ×3 | conversion CORRECT, residue blocks it |
  | `self_import.py` | keyless `sorted(Cycle…)` | " |
  | `module_importers.py` | keyless `sorted(Site…)` | " |
  | `name_collision.py` | keyless `sorted(Collision…)` | " |
  | `ratchet_log.py` | staging-path exemption gap (Ⓝ31s⁶⁶) | FALSE findings |

  **Four of five are not defects at all.** Each has a `sorted()` over the very record being
  converted, with no key — under `NamedTuple` that compared by FIELD POSITION, and the dataclass
  refuses it. The codemod is correct; the FILE needs a named `rank()` before it can convert.

  ⚑⚑⚑ **AND THIS SPLITS THE 75 INTO TWO POPULATIONS THE FLAG COUNT ALONE CANNOT SEPARATE.** A
  keyless comparison is either INERT (flagged, conversion still lands — 34 files did) or
  LOAD-BEARING (the ordering is actually used on the converted record, so the checker blocks it —
  these four). **The blocking ones are the ones where a real ordering decision was being made by
  field declaration order and nobody knew.** They are the sharpest instances in the whole census,
  and they surfaced by refusing to convert.

  ⚑⚑ **`module_importers.py` CARRIES `argv[0]`** — the operator's own example of the principle
  (*"we don't say argv[1]"*), found by the tool built to enforce it, in the package that enforces
  everything else. Six flags in one file: a keyless `sorted`, `got[0]`, `got[1]`, `got[2]`, an
  unnamed `?[0]`, and `argv[0]`.

  **SO Ⓝ31s⁷ HAS AN ORDER, AND IT IS NOT ARBITRARY:** the four blocking files first — each needs
  ONE named `rank()` and converts immediately, taking the batch to 62 — then the 34 inert
  comparisons and 37 subscripts as ordinary paydown.
* ⚑ **THE FULL `run_selftests` FROM THE 58-FILE CONVERSION IS STILL RUNNING** (>120s, background,
  no output yet). Spot checks were green (`tool_census` 14/14, `ratchet_core` 7/7, `page` 18/18);
  the full run is the one that would catch a suite constructing a converted record POSITIONALLY,
  which is the failure mode the conversion is designed to expose. ⚑ Not yet established either
  way — an unfinished run is not a green one.


* ⚑⚑⚑ **THE FULL `run_selftests` FAILED, AND IT IS **NOT** CONVERSION DAMAGE — BUT I ALMOST
  REPORTED IT AS SUCH.**

      run_selftests.py:724  →  ratchet.may_write(write)
      TypeError: may_write() takes 0 positional arguments but 1 was given

  **`substrate/baseline_io.py` IS UNCHANGED BY THE CONVERSION** (`git diff --stat` names only
  `scripts/ratchet.py` and `scripts/run_selftests.py`, neither of which the codemod touched —
  they hold no `NamedTuple`), and it is the file carrying the keyword-only signature. Its own
  docstring declares the divergence deliberate:

      ⚑ `write` IS KEYWORD-ONLY HERE AND WAS POSITIONAL IN `ratchet.may_write`, which is a
      DELIBERATE DIVERGENCE rather than an oversight. `FBT001` refuses a boolean positional
      because a bare `may_write(True)` says nothing at the call site about what the True
      means… The three existing callers keep working against `ratchet.may_write`.

  **So `ratchet.may_write` is now the keyword-only one and the positional callers broke** —
  `run_selftests.py:724`, `set1_ratchet_cores.py:318`, and three sites in
  `tests/test_rederive_agreement.py`. A pre-existing break in the migration the docstring
  describes, surfaced by a full run rather than caused by one.

  ⚑⚑ **AND THE FIRST THING I WROTE WAS *"A real regression, and it's mine."*** The failure
  arrived immediately after a 58-file write, so attributing it to the write was the available
  reading — and it took two commands to refute (`--calls may_write` for the def site, `git diff
  --stat` for what actually changed). **Proximity is not causation, and a 58-file change is
  exactly the kind of event that absorbs blame for whatever fails next.** Ⓝ47's discipline
  applies to attribution, not only to mechanism.

  ⚑ **WHAT IS THEREFORE STILL UNESTABLISHED: whether the conversion broke anything.** The run
  aborted at `reach_ratchet` before reporting per-suite results, so the suites BELOW that point
  never ran. Spot checks were green (`tool_census` 14/14, `ratchet_core` 7/7, `page` 18/18,
  `tool_gap` 11/11, `tool_convention_audit` 14/14, `tool_decline_run` 17/17, `tool_find` 19/19)
  — seven suites, not 255. **An aborted run is UNMEASURED, not clean**, and reporting the
  conversion as verified on spot checks would be the census-green defect this repo names.

  **NEXT:** fix the `may_write` call sites (one keyword each), then re-run — the conversion's
  verification depends on a run that reaches the suites.
* ✅ ⚑⚑⚑ **Ⓝ63⁗ ⟡the-trim-is-a-write — DONE. `substrate/module_trim.py` (53/53, 22 arms) MAKES
  THE TRIM A MODE.** Three agents plus me hit the same wall independently today, which is what
  turned a technique into a tool: the excision and the now-stranded imports are NON-CONTIGUOUS,
  both `Edit` orderings leave a finding (`F821` vs `F401`), and any finding reverts the whole
  file — so there is no clean intermediate to pass through and a trim can only ever be one
  `Write`. One case retyped 250 lines by hand.

  ⚑⚑ **THE DILEMMA DISSOLVES IN `record_migrate`'s PIPELINE RATHER THAN NEEDING A SECOND WRITE
  PATH.** `_autofix` hands the STAGED text to `ruff --fix`, which removes the stranded import
  mechanically — so the intermediate never has to be clean, it is FIXED BEFORE IT IS CHECKED.
  The new module contributes only the transform and the guard; staging, fixing, checking and the
  verdict lattice are called, never reimplemented. **Demonstrated: one `--apply` removed two
  definitions AND both stranded imports (`sys`, `pathlib.Path`) in a single write**, independently
  confirmed CLEAN by `pycheck_show`.

  ⚑⚑ **CONSERVATION IS VERIFIED IN THREE LAYERS, NOT REASONED ABOUT** — `split_lemmas`' guard one
  language over, reproduced as DISCIPLINE (it is line-oriented over Agda and not callable here):

      partition over `Module.body`     "top level" is a fact about the statement list, not a
                                       depth counter — a METHOD spelled `selftest` is unreachable
      multiset compare, BOTH ways      ORIGINAL⊆PARTS catches deletion; PARTS⊆ORIGINAL catches a
                                       line REWRITTEN in transit, which a line COUNT cannot see.
                                       Multiset, so a doubled excision is caught too
      an unmatched name is UNSAFE      trimming 4 of 5 requested names is the plausible-and-wrong
                                       output, and the caller is about to delete the sibling

  ⚑ **AND THE IMPORT EXEMPTION IS ONE-DIRECTIONAL, WHICH IS THE DETAIL THAT KEEPS IT HONEST.**
  `ruff --fix` legitimately REMOVES a stranded import, so imports are exempt in the losing
  direction — but an INVENTED import is still refused. An exemption admitted in both directions
  would have swallowed the check standing beside it.

  ⚑ **`UNSAFE` IS A FOURTH VERDICT, refused on the same footing as FINDINGS/UNKNOWN**, and an arm
  proves `main` consults it AT THE WRITE rather than merely printing it — the distinction between
  a report and a gate, which this session has watched collapse twice.

* ⚑⚑ **AND THE DEMONSTRATION FOUND A REAL LIMIT ON ITS FIRST RUN, WHICH IS WHY IT WAS A
  DEMONSTRATION AND NOT AN ARGUMENT.** The first dry-run came back `FINDINGS`: the
  `if __name__ == "__main__":` dispatch block ALSO references `selftest` and is not a named
  definition the trim can take, so removing the def strands the reference. **Nothing was written.**

  ⚑ So the mode carries a stated constraint rather than a hidden failure: **the dispatch block
  must be moved by hand (or already absent) before a tail can be trimmed** — the tool refuses
  instead of emitting an F821. That is a genuine bound found by RUNNING it, and it would not have
  appeared in any amount of reading. ⚑ Ⓝ63⁗′: the dispatch block is itself part of the tail and
  could be recognised as such — a `__main__` guard whose body references only trimmed names is
  mechanically identifiable. Not built; named.

  ⚑ **Demonstration was on a FIXTURE, not a live module, and the agent said so unprompted.** The
  only remaining inline tail is `ratchet_suites.py`, concurrently owned by another agent. A
  fixture reproducing the shape was planted in-project and removed after — the same
  path-keyed constraint that puts STAGING inside the tree (`consider` does
  `relative_to(corpus.ROOT)`), not a workaround.

* ✅ ⚑⚑⚑ **Ⓝ63⁵ ⟡the-apply-loop — DONE, 48/48 → 66/66, AND THE ARMS WERE MUTATION-TESTED RATHER
  THAN MERELY OBSERVED GREEN.** Three mutations to `record_migrate.main`, each caught, each
  reverted (`git diff` on the module is EMPTY — verified independently):

      if outcome.writable → if outcome.verdict != UNCHANGED   caught by the FINDINGS + UNKNOWN arms
      write outcome.report instead of outcome.source          caught by the checked-bytes arm ONLY
      if apply → if True                                      caught by the dry-run arm

  ⚑⚑⚑ **THE `if True` MUTATION IS THE SHARPEST RESULT THIS SESSION HAS PRODUCED: the tool kept
  printing `(--dry-run: nothing written)` WHILE WRITING.** That is the report-versus-gate
  collapse in its exact form — the distinction this arc has watched collapse three times — and
  **only a FILE-OBSERVING arm can see it.** Every arm that consults `outcome.writable` stays
  green, because `writable` is the loop's INPUT and cannot fail when re-read.

  ⚑⚑ **AND THE SECOND MUTATION PROVED THE ARMS ARE INDEPENDENT RATHER THAN CORRELATED** — only
  ONE arm caught it while the others stayed green. `correlated-instruments-agreeing-is-not-
  coverage` answered constructively: coverage is the UNION of blind spots, and a mutation that
  exactly one arm catches is the evidence that the union is real. **Nobody asked for mutation
  testing; the agent supplied the discriminating check this session kept finding absent.**

  All six loop arms plant a DIRECTORY under `corpus.ROOT`, run the real `main`, and assert on
  BYTES READ BACK FROM DISK. `_PlantedTree.__exit__` uses `shutil.rmtree` unconditionally, so it
  removes files the LOOP wrote, not only the ones it planted.

* ⚑⚑ **AND THE ONE UNTESTABLE PROPERTY WAS ANSWERED BY MOVING IT, NOT BY WRITING A VACUOUS ARM.**
  My brief asked for *"the exit code reflects what happened, including some-writable-others-not"*.
  `main` returns `0` for any completed batch, and the agent declined to assert otherwise:

  ⚑ **THE SIBLING `module_trim` RETURNS 1 ON REFUSAL BECAUSE IT CONVERTS EXACTLY ONE MODULE** —
  its exit code can name that module's verdict. **Over a BATCH it cannot:** `1` is
  indistinguishable between one refusal and all of them, and would make a normal partly-clean
  sweep look like a crash. So the property was pinned WHERE IT LIVES — the written count and the
  refused count must both be legible in the summary and not collapsed — with the rationale in the
  arm's docstring so the next reader does not read the `0` as an oversight. **A cardinality
  difference between two tools makes the same exit-code convention right in one and wrong in the
  other**, which is not visible from either tool alone.

* ⚑⚑ **Ⓝ72 ⟡the-lost-executable-bit — A LATENT `EXE001` BLOCKS THE NEXT EDIT TO A FILE AND IS
  INVISIBLE UNTIL THEN.** `record_migrate_selftest.py` had lost its executable bit while keeping
  its shebang; under zero tolerance that refuses ANY subsequent edit, for a reason unrelated to
  the edit. The agent restored it and flagged the same defect in a peer's file.

  ⚑ **MEASURED: IT IS TWO FILES, NOT ONE** — `module_trim_selftest.py` AND
  `attr_reads_selftest.py`, both `-rw-rw-r--` with shebangs, both from this session's agent work.
  Fixed. **A file can be gate-clean today and refuse tomorrow's edit on a property no suite reads
  and no census counts** — it is not in the file's TEXT, so every instrument this repo has for
  file health is blind to it. A `--mode` census over shebang-vs-permission is a ~10-line reader
  and would have found all three at once.

* ⚑⚑ **Ⓝ71c ⟡the-guard-that-did-not-move — `module_trim`'s CONSERVATION GUARD WAS COMPARING
  ACROSS TWO DIFFERENT BASELINES, AND ITS TELL WAS THAT THE COMPLAINT NEVER CHANGED.**
  `--dry-run` on the monolith returned UNSAFE with 11 "vanished" lines — **byte-identical for
  `reach_ratchet` alone, for four defs together, and for `_selftest` alone.** ⚑ **A guard whose
  complaint does not move with its input is not measuring its input**, and that is a stronger
  signal than the verdict itself.

  Cause: `consider` compared the FIXED trimmed text against the RAW original, so every unrelated
  `ruff --fix` change read as a deletion. **Invisible on a clean target, fires on any dirty one**
  — so the tool was correct exactly where it was exercised and wrong exactly where it was needed.

  ⚑ The first fix (compare against fixed-original) broke a DIFFERENT case, caught by the module's
  own suite in minutes (`Path(".")` → `Path()` present in the fixed baseline, absent from the
  unfixed `extracted`). **The shipped rule intersects them: a line is a genuine loss only if BOTH
  baselines accuse it** — the two false-refusal classes are different, so intersecting separates
  them from real deletion. 4 failures → **53/53**; `record_migrate` still 66/66. After the fix the
  monolith trim reports FINDINGS, not UNSAFE — the excision is verified content-safe.
