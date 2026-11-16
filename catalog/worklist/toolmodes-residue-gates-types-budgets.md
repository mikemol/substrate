# Ⓝ31 residue — gates, types, probes and the retired budget

**Concern: what the gates actually assert, what a refusal is as evidence, and the size budget's
retirement.** Index and arc frame: [`toolmodes-split.md`](toolmodes-split.md).

⚑⚑ **Ⓝ59 ⟡the-refusal-is-not-a-probe IS THE LOAD-BEARING ENTRY.** A gate's refusal text is real
evidence and the ONLY form in this repo that leaves nothing behind — no file, no exit code,
nothing to re-run. Five of the session's decisions arrived that way, including the measurement
that decided a 67-file migration and which was never written down. Ⓝ57's dissolution is its
answer: *a probe worth running is a suite worth keeping.*

⚑ Ⓝ53 is the four-form repair (`getattr` → `isinstance` → `singledispatch` → `match`), with
three competing mechanisms for one error and only the probe separating them. Ⓝ80
⟡line-length-is-obsolete retires the size budget, which dissolves Ⓝ79 rather than answering it.
Ⓝ73 corrects a red gate read as breakage: EMPTY is the strongest setting, never a defect.

## Residue

* ⚑ **Ⓝ41 ⟡callee-surface-assumed — SIX TIMES TODAY, MEASURED.** `Tool.accepts` (it is
  `accepted`), `undocumented_collisions` (returns a dict, not pairs), three nonexistent
  `tool_overlap` functions (`all_signatures`/`all_kinds`/`all_gloss_words`), and `gate_module`.
  Each cost a full gate refusal and file revert. **`module_outline <path>` is ONE call and
  prevents all of them**; the habit is not forming, so it belongs in a procedure rather than in
  intent.

* ⚑⚑ **Ⓝ41 ⟡write-not-edit-for-new-symbols — FOUR MORE INSTANCES THIS TURN, IN THE TURN WHERE I
  NAMED THE RULE.** I called `_is_future`, `_after_future`, `_dataclass_import` and `FUTURE` in
  one edit and defined them in the next, four times; each refusal reverts the file, discarding
  both halves. **The rule generalises past class conversions: ANY symbol introduced and referenced
  together must land in ONE write.** What finally worked was ordering by dependency — the constant
  alone (references nothing), then the helper (references only the constant), then the call sites
  (`replace_all` over both) — so each edit was independently valid.

* ✅ **Ⓝ31s⁴‴ ⟡let-ruff-place-it — DONE, AND THE FIX WAS A DELETION.**
  `_module_name`, `_sorts_after_dataclasses`, `_dataclass_import` and the `FUTURE` constant are
  gone from `record_transform`; the transform now inserts the dataclass import at ANY valid
  position and `record_migrate._autofix` hands the staged file to `ruff --fix` before checking it.

  **VERIFIED on the two files that had failed:**

      CLEAN     substrate/tool_cli.py   (2 record(s): Refusal, Parsed)   — 2 flags
      CLEAN     substrate/arm_shape.py  (1 record(s): Arm)               — 1 flag

  ⚑⚑⚑ **THE PATTERN WAS THE FINDING, NOT ANY OF THE THREE BUGS.** Each `I001` fix was correct
  about the case in front of it and produced the next failure with the OPPOSITE cause:

      2. import appended after `typing`                 → I001
      3. `__future__` alone above it, flush             → I001, opposite cause
      4. an owned blank line splitting a stdlib group   → I001, opposite cause again

  Three clauses of an isort reimplementation growing inside a codemod — **while the real sorter
  ran in the very next step of the same pipeline.** `feedback_fix_infra_not_route_around` (conform
  to the tool; do not rebuild its core), arriving mid-transform. The tell was not any single
  failure but that each fix produced a new one from the other direction.

  ⚑⚑ **AND THE FIX EXPOSED A SECOND DEFECT IT WOULD OTHERWISE HAVE INTRODUCED: the WRITTEN text
  must be the CHECKED text.** `_check` fixes a staged copy and verifies THAT; writing the unfixed
  transform output would commit a file no checker ever saw, with a CLEAN verdict about a different
  document. `_fixed` reads the text back from staging so the two cannot diverge — the same
  read-your-write discipline cassian named for the visitor control, applied to the artefact.

  ⚑ **`_autofix` FAILS SILENTLY, AND ONLY BECAUSE THE CHECK STILL RUNS AFTER IT.** If ruff cannot
  fix the file, `run_checks` reports what remains and the verdict is FINDINGS or UNKNOWN — never
  CLEAN. It is an OPTIMISATION of the transform's output, not a step whose success is inferred
  from. Safe fixes only (`--fix` without `--unsafe-fixes`), because whatever it produces is what
  gets written.

* ⚑⚑ **Ⓝ41″ ⟡imports-cannot-land-alone — THE DEPENDENCY-ORDERING RULE HAS A LIMIT, MEASURED.**
  Last turn's rule was *"order by dependency: constant, then helper, then call sites, so each edit
  is independently valid."* It works for DEFINITIONS and fails for IMPORTS: `import subprocess`
  with no user is `F401`, a finding, so the intermediate state is not clean and the edit reverts.
  **The amended rule: dependency-ordering only helps when each intermediate state is independently
  CLEAN — imports and their user are therefore always ONE write.** Measured twice this turn,
  the second time immediately after stating the unamended rule.
* ⚑⚑⚑ **Ⓝ53 ⟡singledispatch-erases-the-type — THE OPERATOR'S SUGGESTION IS RIGHT IN DESIGN AND
  MAY BE UNUSABLE UNDER THIS GATE. MEASURED, NOT ASSUMED.** Operator: *"I think we don't need to
  use isinstance if we use singledispatch."* Correct as design — dispatch on the type rather than
  interrogating it, so each handler receives a NARROWED type and reads its declared fields with
  no guard. It is the honest third form of the `_nested_bodies` repair:

      1. `getattr(node, "orelse", None)`      — erasure; `Any` at every access
      2. `isinstance` chain                   — better, and still field-probing WITH A GUARD IN
                                                FRONT: the union stayed wider than the attribute
                                                set (`With` has no `orelse`), so the narrowing
                                                was the AUTHOR's claim, not the language's
      3. `@singledispatch` + per-type register — the narrowing becomes the LANGUAGE's

  ⚑⚑ **BUT THE GATE REFUSES IT FOR A REASON THAT IS NOT THE MISSING IMPORT:**

      Untyped decorator makes function "_nested_bodies" untyped   [untyped-decorator]
      Function is untyped after decorator transformation          [misc]

  **`functools.singledispatch` is typed as returning `Any` in typeshed**, so the decorator ERASES
  the type of every function it wraps — and this repo runs `disallow_untyped_decorators`. The
  erasure the technique exists to remove is reintroduced BY the technique, at the decorator
  boundary. ⚑ NOT YET ESTABLISHED whether a typed wrapper (a `Protocol` over the dispatcher, or
  `singledispatchmethod` on a class) satisfies it; that is the open question, and it is worth
  answering because the design is right.

  ⚑ **AND IT IS A CAPABILITY THE TREE HAS NEVER USED:** `--binding singledispatch` over
  `substrate/`, `scripts/`, `scratch/`, `jea/metalanguage/` → **0 in 945 files.** Same shape as
  `TypedDict` (also 0) and `ABC` (also 0): stdlib answers to questions this tree keeps solving by
  hand. ⚑⚑ Three such measurements in one session says the pattern is not incidental — **this
  codebase reaches for its own idioms before the language's**, and the per-file gate then makes
  the hand-rolled version expensive to correct.

* ⬜ **`substrate/import_reach.py` IS LANDED AND CLEAN with the `isinstance` form (form 2).** The
  `singledispatch` conversion is NOT landed: the import and its use are non-contiguous, so it
  needs one `Write` of the whole file (Ⓝ41″ again — an unused import is itself a finding, so the
  two cannot land in separate edits).

  ⚑ **Form 2 is not wrong, only weaker.** It reads each group for exactly the fields that group
  declares, which is what the checker accepted. What form 3 would buy is that a NEW node kind
  cannot be added to a union without someone noticing the attribute set no longer matches.


* ⚑⚑⚑ **Ⓝ53 ⟡singledispatch-erases-the-type — MY INFERENCE WAS WRONG ABOUT THE MECHANISM, RIGHT
  ABOUT THE CONCLUSION, AND THE DIFFERENCE IS THE FINDING.** `linux-sources` read typeshed
  (`fa7a8e30a9b58bb8f1ac7093cbc54899d9172758`) and refuted it byte-cited:

      stdlib/functools.pyi:230
          def singledispatch(func: Callable[..., _T]) -> _SingleDispatchCallable[_T]: ...

  **NOT `Any` — a fully typed generic protocol** (`_SingleDispatchCallable`, lines 210-228, with
  typed `registry`, `dispatch`, three `register` overloads and `__call__`). My sentence
  *"singledispatch is typed as returning Any, so the decorator erases the function's type"* is
  **false**.

  **THE REAL MECHANISM, and it is narrower:** the transformation is `Callable[..., _T]` IN →
  `_SingleDispatchCallable[_T]` OUT, and the protocol's own `__call__` is
  `(*args: Any, **kwargs: Any) -> _T`. **The decorated function keeps its RETURN type and loses
  its PARAMETER types.** The erasure is real and it is in the parameters — which is why a
  fully-annotated function comes out the other side with an `Any`-parametered call signature.

  ⚑⚑ **AND THE PEER STOPPED WHERE THE SOURCE STOPPED.** Whether that Any-parameter result is the
  EXACT thing mypy's `untyped-decorator` check keys on is a fact about mypy's `checker.py`, not
  the `.pyi` — so they declined to assert it and named the probe that settles it (`reveal_type`
  the decorated name; expect `functools._SingleDispatchCallable[str]`). **That is the discipline I
  asked for and did not apply to myself**: my claim fit the error text, which is exactly what
  makes a plausible-fit dangerous. Fourth such inference today; the first three were also refuted
  by measurement.

  **Q3 — `singledispatchmethod` DOES NOT HELP.** `functools.pyi:232-246` carries
  `dispatcher: _SingleDispatchCallable[_T]` and `__get__(...) -> Callable[..., _T]`: identical
  shape, identical erasure. ⚑ **And no caller-side annotation can recover parameter types the STUB
  erased** — the types are gone by the stub's signature, not by a missing annotation of ours.

  ⚑⚑⚑ **THE CORRECTION TO HOW I RECORDED IT, WHICH MATTERS MORE THAN THE FACT.** I wrote that
  `singledispatch` (0), `TypedDict` (0) and `ABC` (0) were "three stdlib capabilities the tree
  never reached for" — one pattern. **They are three UNRELATED absences**: only `singledispatch`
  is blocked by a flag, and specifically by `disallow_untyped_decorators` refusing a decorator
  whose typeshed return is a `...`-parametered callable object. TypedDict and ABC are not
  decorator-erasure at all. **A shared symptom (count 0) collapsed into a shared cause** — the
  census-keyed-on-one-spelling shape, applied to my own generalisation.

  **THE HONEST RECORDED FACT, narrow:** `singledispatch` is incompatible with
  `disallow_untyped_decorators` by the shape of its typeshed stub. Not "unusable under strict
  mypy", not "a stdlib idiom this tree avoids".

* ⚑⚑ **AND THE DESIGN GOAL SURVIVES, VIA A ROUTE THE SOURCE DOES NOT FORECLOSE: `match`.**
  The operator's reasoning was right — dispatch-on-type narrows where an `isinstance` chain leaves
  the union wide (`node.orelse` over a 7-member `ast` union, `With`/`AsyncWith` lacking it). A
  `match node: case ast.If(): … case ast.For(): …` gives each arm the matched type WITH THE
  CHECKER ENFORCING IT — no decorator, no erasure, each arm reading its declared fields. **That is
  singledispatch's semantics without the decorator the flag refuses**, and it is the fourth form
  of one repair:

      1. getattr(node, "orelse", None)   erasure; Any everywhere
      2. isinstance chain                field-probing with a guard; union wider than the fields
      3. @singledispatch                 REFUSED — parameter types erased by the stub
      4. match / case ast.If()           narrowing enforced by the language  ← the route

* ⚑ **Ⓝ55 ⟡stub-vs-runtime — the general form, worth keeping.** A mypy finding about a stdlib
  callable is a claim about the STUB (`typeshed/stdlib/*.pyi`), and reading the RUNTIME source
  (`Lib/functools.py`) can neither confirm nor refute it. Two artifacts, two maintainers, one
  symptom — and the fix differs completely: an imprecise stub is upstream work or a local `.pyi`
  override, while a strict-config interaction is entirely ours. ⚑ The operator caught me phrasing
  these as alternatives (*"typeshed? I thought singledispatch was in functools?"*), which is
  exactly the ambiguity that would send a reader to the wrong file.
* ⚑⚑⚑ **Ⓝ53 — MEASURED IN OUR OWN VENV, AND THE ANSWER IS A THIRD MECHANISM NEITHER OF US
  NAMED.** `linux-sources` retracted their Q2/Q3 (*"params erased, hard-to-impossible"*) after a
  probe in THEIR env showed a two-arg `_SingleDispatchCallable` and a clean pass. They asked me to
  run it here, because the question is about OUR checker. Run:

      Revealed type is "functools._SingleDispatchCallable[str, def (x: object) -> str]"

  **TWO type args — our mypy HAS the functools plugin and RETAINS the parameter signature.** Their
  retraction is correct and my *"the decorator erases the function's type"* was wrong for a second,
  independent reason.

  **BUT IT STILL CANNOT LAND HERE, AND THE CAUSE IS NEITHER OF THE TWO WE PROPOSED:**

      error: Expression type contains "Any"
        (has type "Callable[[Callable[..., _T]], _SingleDispatchCallable[_T]]")  [misc]   ← the decorator
      error: Expression type contains "Any" (has type overloaded function)      [misc]   ← @f.register

  **Not `[untyped-decorator]`. It is `disallow_any_expr`.** The `Callable[..., _T]` INSIDE the
  decorator's own type is an `Any`-containing expression, and this repo forbids that irrespective
  of what the plugin reconstructs downstream. The plugin fixes what the decorated FUNCTION becomes;
  it cannot change what the DECORATOR's type expression contains.

  ⚑⚑⚑ **THREE READINGS, THREE DIFFERENT MECHANISMS, ONE SYMPTOM — AND ONLY THE PROBE SEPARATED
  THEM:**

      mine        "typeshed types it as Any"                    FALSE (it is a typed protocol)
      theirs      "the plugin is absent / params erased"        FALSE (plugin present, params kept)
      measured    `disallow_any_expr` on the decorator's own    ← the actual refusal
                  type expression, and on `register`'s overload

  Both wrong readings were derived from a real artifact — I from the error text, they from the
  `.pyi` — and both fit. **A plausible fit derived from the right file is still not a measurement**,
  and the file that settles a checker question is the checker, run.

  ⚑⚑ **AND THE PROBE HAD TO RUN IN *THIS* ENVIRONMENT.** linux-sources' identical probe PASSED in
  theirs (mypy 2.3.1, empty config, `Success: no issues found`). Same code, same mypy family,
  opposite verdict — because the config differs. **Their measurement was sound and not transferable**,
  which is the sharper form of paperkit's *"a shared gate makes your ANSWER portable and your TREE
  STATE uninformative"*: here even the ANSWER was not portable, because the question was about
  configuration rather than about the library.

  **THE RECORDED FACT, now third-time narrow:** `singledispatch` is refused in this repo by
  **`disallow_any_expr`**, because its own type expression contains `Callable[..., _T]`. Not by
  `disallow_untyped_decorators`; not by a missing plugin; not by parameter erasure. ⚑ And the
  earlier correction stands doubly: the 0-in-945 absence of `singledispatch`, `TypedDict` and `ABC`
  is THREE UNRELATED ABSENCES, and now the `singledispatch` one has a different cause than the one
  I recorded an hour ago.

* ⚑⚑ **SO `match` IS THE ROUTE AFTER ALL — but for the third stated reason, not the first two.**
  A `match node: case ast.If(): …` introduces no decorator, so no decorator type expression, so
  nothing for `disallow_any_expr` to refuse. It delivers exactly the property the operator wanted:
  each arm narrowed by the LANGUAGE rather than by the author's `isinstance` claim.

      1. getattr(node, "orelse", None)   erasure; Any everywhere
      2. isinstance chain                probing with a guard; union wider than the fields  ← LANDED
      3. @singledispatch                 refused by disallow_any_expr (measured, not inferred)
      4. match / case ast.If()           narrowing enforced by the language  ← the route


* ✅ **Ⓝ53′ ⟡match-not-isinstance — LANDED FIRST TRY. `_nested_bodies` is now `match`/`case`.**
  The fourth form of one repair, and each earlier form was wrong in a way the next exposed:

      1. getattr(node, "orelse", None)     erasure — Any at every access (the reflex, ×3 today)
      2. isinstance chain                  probing WITH A GUARD: the union stayed wider than the
                                           attribute set, so the narrowing was the AUTHOR's claim
                                           — refused for reading `orelse` off `With`/`AsyncWith`
      3. @functools.singledispatch         refused by `disallow_any_expr` on the decorator's own
                                           type expression — MEASURED, after two wrong inferences
      4. match / case ast.Try()            ← LANDED. The checker narrows each arm and enforces
                                           the fields that class declares

  ⚑⚑ **AND THE FORM ITSELF DEMONSTRATES THE PROPERTY.** `case ast.With() | ast.AsyncWith():`
  is accepted while `orelse` remains unreadable there — the same union that form 2 got wrong is
  expressible here precisely because the checker, not the author, decides what each arm may read.
  **A class pattern is not a prettier `isinstance`**: inside `case ast.Try():` the binding IS an
  `ast.Try`, so `finalbody` and `handlers` are available because a `Try` HAS them.

* ⚑⚑⚑ **AND A REAL TRAP FOUND ON THE WAY: THE SCRATCHPAD CANNOT HOLD A PROBE.**
  `INP001 File … is part of an implicit namespace package. Add an __init__.py.` — and **writing
  the `__init__.py` is refused BY THE SAME RULE**, because the parent is still an implicit
  namespace package at the moment the file is checked. The rule fires on the very file that would
  satisfy it.

  ⚑⚑ **A MEASUREMENT THAT CANNOT BE WRITTEN IS AN INFERENCE BY DEFAULT**, and this session paid
  for that four times — three refuted codemod diagnoses and one refuted typeshed claim, every one
  settled in the end by a two-line probe. The probes that DID land avoided `INP001` only by
  accident of where they sat. **The instrument that keeps catching my errors is the one the gate
  makes hardest to write**, which is worth naming rather than routing around.

  → **Ⓝ57 ⟡scratchpad-cannot-hold-a-probe.** Not a lint nuisance: it is a structural bias toward
  reasoning over measuring, in a repo whose standing rule is the opposite.

* ⬜ **`substrate/import_reach.py` REMAINS UNVERIFIED AND UNCONSUMED.** `--binding import_reach`
  → 0 in 263 files, which is correct and expected: it is stranded until the runner retires, the
  ⟡stranding lesson operating as designed rather than as a defect. ⚑ The parity probe against the
  monolith's copy is still owed and the window is still open — the origin is on disk until
  `run_selftests.py` is deleted whole.

* ✅ **Ⓝ57 ⟡scratchpad-cannot-hold-a-probe — DISSOLVED BY THE OPERATOR, NOT WORKED AROUND.**
  I recorded the `INP001` catch-22 as a structural bias toward inference: a probe in the session
  scratchpad is refused, and the `__init__.py` that would satisfy the rule is refused by the same
  rule. Operator: *"You should be rebuilding the module in a sanctioned place. You can use the
  package approach there."*

  ⚑⚑⚑ **THE GATE WAS NOT OBSTRUCTING THE MEASUREMENT; IT WAS SAYING THE WORK WAS IN THE WRONG
  PLACE.** `substrate/` is the sanctioned home, `INP001` does not fire there, and what I was about
  to write as a throwaway probe is a REAL SUITE — `substrate/import_reach_selftest.py`, **19/19**,
  discoverable by `suite_discovery`, surviving the session instead of dying with it.

  ⚑⚑ **AND THAT IS `usecase-the-per-file-gate-is-a-design-signal` ONE LEVEL UP: A GATE THAT
  REFUSES A LOCATION IS SAYING THE LOCATION IS WRONG**, exactly as a per-file gate that keeps
  firing says the UNIT is wrong. I read a placement refusal as a capability gap and filed it as
  debt — the same misreading as *"no tool covers this, so grep is legitimate here"*: a fact about
  where I put the file, reported as a fact about what the toolkit permits.

  **THE SUITE PINS WHAT THE WALK MUST NOT COLLAPSE**, each arm a defect measured before it was a
  case: module-level vs function-local (the 54-of-99 false positive), a route rather than a
  boolean, deferred hops MARKED rather than merged, and an unparseable file reading EMPTY rather
  than raising — because a walk that raises on one bad file reports nothing about the other 262.

  ⚑ Fixtures are written to the shapes real modules have — a `TYPE_CHECKING` block, a
  module-scope `try`, a conditional import — rather than the shapes the walk finds convenient.
  That is ⟡per-binding-is-not-per-shape applied on purpose, having cost thirteen files earlier in
  this same session by not being.

* ⚑ **STILL OWED: the parity comparison against the monolith's `store_reach`.** These 19 cases pin
  what the extracted walk DOES; they do not establish that it agrees with the copy inside
  `run_selftests.py`. That comparison is possible only while both are on disk, and the origin is
  frozen-but-present until it is deleted whole. ⚑ The suite is now the right HOME for that arm —
  it belongs beside these cases, not in a scratch file.


* ⚑⚑⚑ **Ⓝ57 — THE RATIONALE, AND IT CORRECTS WHAT I FILED. THE SCRATCHPAD REFUSAL IS A FORCING
  FUNCTION, NOT A COST.** Operator: *"we don't whitelist scratchpad writes as workaround because
  if you're going to have to write something high-quality anyway, write it somewhere it can
  persist."*

  I read `INP001` as *"probes are hard to write here"* and filed it as **a structural bias toward
  inference**. Wrong axis. **The gate's standard applies wherever the file lives, so the only
  thing a scratchpad buys is IMPERMANENCE** — same work, and it evaporates. The bias is toward
  throwing away, not toward not-measuring.

  ⚑⚑ **AND I DID EXACTLY THAT, EIGHT TIMES THIS SESSION.** `parity.py`, `parity_decl.py`,
  `seam.py`, `reachparity.py`, `sd_probe.py`, `reachcheck.py`, `slots_probe.py` and others — each
  answered a question that RECURS, each died with the session:

      seam.py       dumped a file at each pipeline stage and settled the thirteen-file mystery
                    in one run, after two turns of refuted inference. **The next reader hitting a
                    transform/autofix seam rebuilds it from nothing.**
      sd_probe.py   `reveal_type` under our config — the only thing that distinguished three
                    competing explanations of one error, two of them from a peer's source read
      slots_probe.py  measured what `__slots__` does to unpacking, which decided a 67-file
                    migration

  **Every one of those is a capability, not a scratch note.** `substrate/import_reach_selftest.py`
  is what one looks like when written where it can persist: 19/19, `suite_discovery` finds it, and
  it will still be answering next month.

  ⚑ **THE DISTINCTION THAT DOES HOLD:** the `-add.md` bodies genuinely are transient — they are
  inputs to `mdstruct --append-section`, consumed on the next call, and the durable artefact is
  the worklist they land in. A tool's INPUT is scratch; a MEASUREMENT is not. I had both in one
  directory and treated them alike.

  ⚑⚑ **SO THE RULE IS NOT "PROBES ARE ALLOWED IN SUBSTRATE" BUT "A PROBE WORTH RUNNING IS A SUITE
  WORTH KEEPING."** If it is worth measuring once it is worth measuring again — the same argument
  the standing rule makes about tooling (*judgement in the turn evaporates when the turn ends*),
  applied to the instrument rather than the judgement. **A one-off measurement is judgement in the
  turn wearing a `.py` extension.**
* ✅ **Ⓝ58 ⟡rebuild-the-lost-probes — FIRST SALVAGE LANDED: `substrate/stage_diff.py` +
  `stage_diff_selftest.py`, 15/15.** The pipeline-stage dumper that settled the thirteen-file
  mystery, generalised from a one-file `seam.py` into `Stage`/`Step`/`run`/`lost_at`/`gained_at`/
  `changed_at`/`render`.

  ⚑⚑ **AND THE OPERATOR CORRECTED MY PREMISE MID-TURN: THE PROBES WERE NEVER LOST.**
  *"(the files may still be in your scratchpad)"* — they are. **Eleven parity probes plus
  `seam.py`, `slots_probe.py`, `sd_probe.py`, all present.** I wrote "lost" when I meant NOT
  PERSISTED: the directory survives the session, but it is untracked, ungated, and nobody but me
  knows to look there. **A file that exists where no one looks is not the same as a missing one,
  and calling it missing misdescribes the fix** — this was salvage, not reconstruction.

  ⚑ **WHICH MADE THE GENERALISATION CHECKABLE RATHER THAN INVENTED.** `seam.py`'s decisive output
  was two lines (`import after transform: True` / `after fix: False`); `Step.holds` and `lost_at`
  are exactly that reading, so the abstraction is faithful to what WORKED rather than to what I
  remembered working. ⚑ It also exposed a real gap: `seam.py` reached into
  `record_migrate._transformed`/`._fixed` (private, `noqa: SLF001`). `Stage` takes
  `Callable[[str], str]`, so the instrument needs no privacy violation — but a CALLER still does,
  and that is unresolved rather than fixed.

* ⚑⚑⚑ **AND I INFERRED-BEFORE-MEASURING AGAIN, ON A TWO-WORD PROBLEM — FIFTH TIME TODAY.** One
  arm failed: *"the render does not carry the not-a-verdict caveat"*. I diagnosed a LINE WRAP
  (the caveat spans a `\n` in the renderer), shortened the needle to `culprit`, and **it failed
  identically**. One `pycodemod --source render` showed the renderer emits **`CULPRIT` in CAPS**.
  A case-sensitivity mismatch, "fixed" once on a wrong diagnosis.

  **The wrap explanation was plausible, specific, and available without reading anything** —
  which is precisely the shape of the other four: the codemod diagnosis from two files sharing a
  symptom, the `noqa`-stripping hypothesis, the typeshed `Any` claim, and the `[untyped-decorator]`
  attribution. Every one was refuted by a single read or probe. ⚑ **Ⓝ47 ⟡dump-dont-infer is not a
  lesson about hard problems; the two-word ones are where it is easiest to skip.**


* ✅ **Ⓝ58′ ⟡eleven-parity-probes — SALVAGED AS ONE MODULE: `substrate/parity.py` +
  `parity_selftest.py`, 17/17.** Eleven `parity_*.py` files in a session scratchpad were one
  pattern with eleven callers, and it is now a module: `shared`, `differing_keys`,
  `differing_values`, `compare`, `unmeasured`, `Disagreement`, `Report`.

  **THE SHARED SHAPE, read from two of the eleven rather than recalled:**
  load the origin and refuse cleanly if unreachable → cast through a `Protocol` naming only what
  is needed → restrict to the SHARED population → compare sets AND per-key values → count
  disagreements with denominators.

  ⚑⚑⚑ **THE THREE STATES ARE THE MODULE'S REASON FOR EXISTING.** A probe that cannot load its
  origin and reports zero disagreements is **indistinguishable from a clean comparison** and gets
  banked as one — `census-green-is-a-fact-about-the-census`, applied to the instrument built to
  catch it. `AGREED` / `DIFFERING` / `UNMEASURED` have three separate exit codes and the reason
  travels with the third, because *"could not import"* and *"no such attribute"* send a reader to
  different places.

  ⚑⚑ **AND THE COST SIDE IS BUILT IN, NOT APPENDED.** Of five disagreements found in one session,
  **three were probe defects or intended changes misread as regressions**. So `Disagreement` is a
  row to ADJUDICATE and the render says so; a report that reads as a verdict invites acting on the
  wrong half. `shared(..., widened=)` is the specific remedy: an extraction widens what the reader
  sees, and comparing over the union reports the intended change as a regression — which is how
  those three arose.

* ⚑⚑ **AND A CORRECTION TO MY OWN SALVAGE LIST: `slots_probe.py` AND `sd_probe.py` DO NOT EXIST.**
  I listed both as recoverable. Measured (`ls scratchpad/*.py`): eleven `parity_*` files, `seam.py`,
  and neither of those two. **They are precisely the two the gate REFUSED** — I never landed them,
  and read their answers out of the refusal text instead of from a run.

  ⚑⚑⚑ **SO THE MEASUREMENT THAT DECIDED A 67-FILE MIGRATION WAS NEVER WRITTEN DOWN.**
  `Cannot determine type of "one"` — the finding that slotted dataclasses refuse positional
  unpacking, which the whole `⟡symbolic-reference-only` arc rests on — came from a REFUSAL
  MESSAGE, not from a probe anyone can re-run. It was later corroborated byte-cited by
  `linux-sources` against CPython 3.13.1, so the claim is sound; but the local instrument for it
  does not exist and never did. **A finding read out of an error message is a finding nobody can
  reproduce.**

  → **Ⓝ59 ⟡the-refusal-is-not-a-probe.** A gate's refusal text is evidence, and it is the ONLY
  form of evidence in this repo that leaves nothing behind: no file, no exit code, no re-run. Five
  of today's findings arrived that way.
* ⚑⚑⚑ **Ⓝ59 ⟡the-refusal-is-not-a-probe — ENUMERATED, AND THE COUNT IS FIVE.** A gate's refusal
  text is real evidence and it is the ONLY form in this repo that **leaves nothing behind**: no
  file, no exit code, no artefact, nothing to re-run. Every other instrument here — a suite, a
  census mode, a probe — persists its own reading.

  **THE FIVE, each a decision made on text that scrolled past:**

  | finding | what the refusal said | what it decided |
  |---|---|---|
  | slotted records refuse unpacking | `Cannot determine type of "one"` | ⚑ **a 67-file migration** |
  | `mdstruct.py` cannot be edited | `1,534 findings` | Ⓝ36a filed as unfixable-in-place |
  | `run_selftests.py` cannot be edited | `1,832 findings` | the runner declared FROZEN |
  | `singledispatch` is refused here | `Expression type contains "Any"` | Ⓝ53's whole conclusion |
  | `sorted_stream` unimportable | `411 findings` | ⟡typed-carrier's entire premise |

  ⚑⚑ **AND THE FIRST ONE IS THE SHARPEST: THE MEASUREMENT THAT DECIDED THE ARC WAS NEVER
  WRITTEN.** `slots_probe.py` does not exist — the gate refused it, and I read the answer out of
  the refusal instead of landing the probe. `linux-sources` later corroborated it byte-cited
  against CPython 3.13.1, so **the claim is sound and the local instrument for it is absent**. A
  future reader asking *"how do we know slotted dataclasses refuse positional unpacking"* finds a
  worklist assertion and a peer's message, not a runnable file.

  ⚑⚑⚑ **THE ASYMMETRY THAT MAKES THIS A CLASS RATHER THAN AN OVERSIGHT.** A refusal is
  ADVERSARIAL evidence — it appears exactly when you are trying to do something else, it is
  maximally convincing (the gate has no reason to lie), and it costs nothing to read. Those three
  properties together are why it gets banked without being recorded: **a passing test is
  celebrated and kept; a refusal is an obstacle you route around, and its content leaves with the
  scrollback.** Two of the five above were *also* refused as probes, which is the trap closing:
  the gate refused the file AND supplied the answer, so the answer arrived without the artefact.

  ⚑ **WHAT WOULD FIX IT IS NOT A TOOL BUT A HABIT WITH A HOME:** when a refusal decides something,
  the finding needs a runnable witness in `substrate/` — which is exactly what
  `⟡scratchpad-cannot-hold-a-probe` was pointing at and what I read as an obstruction.


* ⚑⚑⚑ **Ⓝ73 ⟡selftest-contract-blocks-too — CORRECTED. "BROKEN — 228 NEW" IS A GATE AT ITS
  STRONGEST SETTING, NOT A GATE THAT BROKE.** The wave-one agent reported it as a blocker that
  fires before the reach gate, and I relayed that framing. Measured (`gate_census --baselines`):

      scripts/run_selftests.py   selftest_contract_baseline.txt   EMPTY   0 keys

  and the census states what EMPTY means, in its own legend: *"ZERO-TOLERANCE: the empty set as
  baseline, so every offender is a NEW key and NO exception is grandfathered. **The STRONGEST
  setting, never a defect.**"* ⚑ **228 NEW is therefore the correct rendering of an unpaid debt
  against a baseline that grandfathers nothing** — not a regression, and not something that
  "broke". The word BROKEN in the gate's own output means *this census is non-empty*, which is
  exactly what a zero-tolerance ratchet says until the debt is paid.

  ⚑⚑ **AND 11 OF 20 RATCHETS ARE IN THAT STATE**, including `cap_ratchet`, `mypy_ratchet`,
  `mode_contracts`, `sorted_order`, `snapshot_guard` ×3. **A red gate here is not evidence of
  damage; it is evidence of a census that has never been grandfathered.** Reading EMPTY as
  degradation inverts the meaning of the strictest setting the family has — which is the same
  inversion as reading a coverage ratio as progress while the denominator moves.

  ⚑ **THE DISTINCTION THAT MATTERS FOR Ⓝ71: fixing the TypeError still does not make the runner
  exit 0**, and that part of the agent's report stands. What changes is the READING — the
  remaining non-zero exit is an unpaid paydown-only census, which is a scheduled arc, not a
  breakage to diagnose.

* ⚑⚑ **AND THE GATE'S OWN DOCSTRING IS THE BEST STATEMENT OF THIS SESSION'S RECURRING DEFECT,
  WRITTEN BEFORE IT:** *"`mypy_ratchet_baseline.txt` DOES NOT EXIST, so `check_mypy_ratchet
  --quiet` exits 0 while printing 'would record 116 type errors'. **'The type gate is green'
  means 'the ratchet has never been baselined', NOT 'the tree typechecks'.** … A count of 0
  renders exactly as legitimately as a count of 116; only a case can tell them apart."*

  ⚑ ABSENT and EMPTY are OPPOSITE states wearing the same zero: **ABSENT exits 0 having measured
  nothing** (a false green), **EMPTY refuses everything** (the strictest gate). `os.path.exists`
  is true for both a grandfathered baseline and a zero-byte one, which is why the census carries
  baseline STATE as a first-class column rather than letting a verdict stand unqualified.

* ⚑ **Ⓝ73a — AND I REACHED FOR A GUESSED FILENAME FIRST** (`scripts/check_selftest_contract.py`
  — does not exist), then `toolmodes --find selftest-contract` → **0 hits over 606 modes, 3,495
  functions, 98 tools**, for a gate that demonstrably runs and reports. The gate lives inside
  `run_selftests.py` and owns a baseline; it is not a mode, so the mode index cannot see it.
  **A zero from the mode census is a fact about what a MODE is**, and the third false-absence of
  the session — after `--attr`'s dotted form and `module_importers`' path spelling. The reader
  that answered was `gate_census --baselines`, which owns the question.

* ⚑⚑⚑ **Ⓝ79 ⟡the-budget-has-two-values — THE PREMISE OF ⟡the-frozen-twelve IS UNMEASURED, AND I
  SCOPED THE WHOLE WAVE ON ONE SIDE OF IT.** Verified myself, both commands:

      substrate/module_size.py    scripts/sppf_db.py  →  1239 code  (39 over, 3.25%)
      scratch/pycodemod.py --size scripts/sppf_db.py  →  2109 code  (909 over, 76%)

  **Same file. Identical physical (4360) and def (47) counts.** The divergence is entirely the
  CODE-LINE predicate, on a file that is ~70% commentary — and **one of these tools is the
  authority for a gate.** ⚑ *You cannot size a cut against a number that has two values*: the
  same edit scores 3% over or 76% over depending on which reader you asked. **The entire
  ⟡the-frozen-twelve population is ranked by this quantity**, so every "eleven over budget" I have
  quoted today is a fact about `module_size`'s predicate, not about the tree.

  ⚑ This is the derived-view divergence class the repo guards, **sitting inside the sizing tool** —
  and neither reader states which lines it counts. **Ⓝ79a: resolve which census is authoritative
  BEFORE any size-budget paydown anywhere.**

* ⚑⚑⚑ **Ⓝ79b ⟡module-size-ignores-its-operand — AND I USED IT TO SCOPE THIS WAVE, TWICE.**
  `module_size.py scripts/sppf_db.py` returns **the full 1181-file corpus census, byte-identical
  to bare invocation.** The operand is silently discarded. A reader who passes a path and finds
  their file in the output **believes they scoped the query** — and gets a true line for the wrong
  reason, which is worse than an error.

  ⚑ Same shape as `pycodemod --attr` (documented, never implemented) and `--forwards` (answered
  the question asked, not the one meant) — **the third instance today of an operand a tool
  accepts and does not honour.** Ⓝ79c: accept and scope it, or REFUSE it the way
  `pycodemod --literal` refuses a flag-shaped operand. Silent discard is the one option that
  cannot be right.

* ⚑⚑⚑ **Ⓝ79d ⟡tests-cannot-hold-an-assertion — THE TWIN IS BLOCKED BY A RULE PAIR THAT IS
  JOINTLY UNSATISFIABLE.** `tests/` DOES admit new files (unlike `scratch/` — probed, no
  `INP001`, ruff and mypy green). **But the file cannot contain an assertion:**

      PT009  Use a regular `assert` instead of unittest-style `assertEqual`
      S101   Use of `assert` detected

  `pyproject.toml:348` exempts `S101` for `scripts/*` ONLY; `tests/` has no `per-file-ignores`
  entry. **Every assertion spelling is refused, so no new test file can be written at all.**

  ⚑⚑ **AND THE INCUMBENTS ARE GRANDFATHERED, NOT CLEAN.** Every existing test carries `PT009`
  (`test_agda_lex_public.py`: 10 of its 35 findings) and survives only because nobody has edited
  it — the write hook checks any file you touch regardless of mypy's `files = ["substrate"]`
  scope. **A directory can be uniformly non-compliant and read as fine, indefinitely, because
  compliance is only ever evaluated at the moment of an edit.**

  ⚑ So `Ⓝ71g`'s one-keyword fix is **blocked, not abandoned**: the direct edit is refused (165
  findings) and the drain route is refused by the rule pair. `gate_status` line 1 stays
  `FAIL(1) tool unit tests`. **The unblock is a `pyproject.toml` decision** — `"tests/*" =
  ["PT009"]` (keeping the `unittest` idiom the pre-commit gate actually runs) or `["S101"]`
  (matching the `scripts/*` precedent). ⚑ The config's own doctrine argues against a glob —
  exemptions are granted per single-responsibility file — **but that doctrine was written for
  `S603` on subprocess callers and collides with a directory of ~6 modules that all need one
  idiom.** Not the agent's call, and not mine.

  ⚑ **A SECOND CONFLICT FOUND AND SOLVED, worth keeping:** `D400`/`D415` demand a first docstring
  line ending in a period, but `gherkin_scan.SCENARIO` captures `(.+?)` to the closing quotes, so
  a trailing period becomes part of the scenario NAME and breaks `check_feature_coverage`'s match
  against `features/`. **The escape is to put `Scenario:` on a LATER line** — `D400` governs only
  the first, and the pattern is `re.MULTILINE`.

* ⚑⚑ **Ⓝ79e ⟡sppf-db-do-not-cut — A REASONED REFUSAL, WHICH IS THE RIGHT DELIVERABLE.** Four
  disqualifiers, three verified directly: (1) the premise is unmeasured — see Ⓝ79 above;
  (2) it is `MM` in git, staged AND unstaged — cutting it means rebasing onto someone's in-flight
  work, the same ground that excluded `schema.py`; (3) **the cut is unverifiable today** — its
  selftest reaches the store and postgres refuses on 5432; (4) it is the de-facto sole authority
  for the `obs_node` write path, and `pack_core_sql`'s correctness invariants live as PROSE
  ADJACENT TO THE CODE THEY GOVERN (ascending height order, `base` surrogate seeding — unseeded
  re-run is silent corruption, assert-don't-establish after measured deadlocks under
  `make -j 8 promote`). **A split that separates those paragraphs from their code manufactures
  the exact class this repo guards**, and `pack_core_sql`/`project_sppf` have ZERO external
  callers, so no API pressure forces one.

  ⚑ **THE BULK THAT MAKES IT "OVER BUDGET" IS THE PAYDOWN RECORD ITSELF.** Trimming it to satisfy
  a budget whose measurement two tools dispute would destroy re-derivable history to move a number
  that is not agreed.

* ⚑ **Ⓝ79f — `tests/` FILES ARE ALL HARDLINKED** (link count 2 on every one). Not investigated;
  recorded because an in-place write could surprise whatever holds the other link.

* ⚑⚑⚑ **Ⓝ80 ⟡line-length-is-obsolete — THE SIZE BUDGET IS SUPERSEDED, WHICH DISSOLVES Ⓝ79 RATHER
  THAN ANSWERING IT.** Operator, 2026-09-02: *"line length paydown is obsolete, replaced by
  n-splitting, the lint hooks and the single responsibility principle. line length paydown was an
  attempt to force guidance toward good, modular code. the lint hooks don't put up with emission
  of bad code or partial solutions."*

  ⚑⚑ **SO Ⓝ79a — *resolve which code-line census is authoritative* — NEEDS NO ANSWER.** The two
  readers disagree by 870 lines on `sppf_db.py` (1239 vs 2109) and **the quantity is no longer
  load-bearing**, so the disagreement is a curiosity rather than a blocker. *A dispute about a
  measurement dissolves when the measurement stops being the criterion* — which is a different and
  better resolution than picking a winner, and I would not have found it by comparing the two
  predicates, because both were faithful readings of a proxy nobody needed.

  ⚑⚑⚑ **THE BUDGET WAS A PROXY FOR "IS THIS FILE DOING TOO MUCH", AND THE REAL PREDICATE NOW
  ENFORCES ITSELF.** A line count is a stand-in for modularity that can be satisfied by
  reformatting and violated by a perfectly modular long file. What replaced it enforces the actual
  property AT THE MOMENT OF EDIT: the per-file gate refuses any file left with a finding (so a
  partial solution cannot land), and n-splitting is what a refusal PUSHES you toward. **The gate
  is not a stricter version of the budget — it measures the thing the budget was approximating.**

  ⚑ **AND THIS IS THE `the-per-file-gate-is-a-design-signal` MEMORY ARRIVING FROM THE OTHER
  SIDE.** That memory says a gate which keeps firing means the UNIT is wrong — decompose to match
  its grain. Here the same fact retires an entire metric: **once the gate names the unit, a
  separate size census is a second authority for a question already answered**, and this repo's
  standing shape is that a second authority drifts.

* ⚑⚑ **Ⓝ80a — SO ⟡the-frozen-twelve WAS RANKED BY A RETIRED CRITERION, AND THAT CHANGES WHAT THE
  POPULATION IS.** "Eleven files over budget" was the FRAME for wave 2 and for the nine `scratch/`
  files still queued. It is not a defect list; it never was. **What remains genuinely broken in
  that population is what the LINT gate says about each file, not its length** —
  `run_selftests.py` was retired because it CRASHED, not because it was 1,299 lines, and the
  agent's `sppf_db.py` refusal turned on four grounds of which "over budget" was the weakest.

  ⚑ **Ⓝ71b WAS SOLVING A NON-PROBLEM.** I built a distinction — *findings measure distance from
  the gate, not bulk; `run_selftests.py` is the SMALLEST over-budget file* — to rank a population
  by a quantity that is not the criterion. **The observation is true and the use was wrong**: the
  finding count IS the signal, and the line count was never the denominator it needed.

* ⚑ **Ⓝ80b — WHAT IS OWED NOW.** `substrate/module_size.py` is a census over a retired criterion,
  and `scratch/pycodemod.py --size` is its rival. Neither should be quoted as a defect measure
  again. ⚑ **Do not delete on this** — `module_size` has a live consumer surface and its
  `--top`/`--budget` shape may still be useful as a READING (where is the bulk?) rather than a
  VERDICT (what is wrong?). The distinction is the whole point: **a reading that stops being a
  verdict does not stop being a reading.** Its path-operand bug (Ⓝ79b — silently returns the
  whole corpus) is still a real defect either way.


* ⚑⚑⚑ **Ⓝ79′ — THE CAUSE, FROM THE OPERATOR: ONE COUNTED COMMENTS AND ONE DID NOT. AND THAT MAKES
  THE DISAGREEMENT DIRECTIONAL RATHER THAN SYMMETRIC.**

      substrate/module_size.py     1239   `code_count` — a NAMED predicate delegating to
                                          `substrate/code_lines.py`, which has its own suite
      scratch/pycodemod.py --size  2109   counts commentary as code

  ⚑⚑ **ON A FILE THAT IS ~70% COMMENTARY, THE SECOND READER SCORED THE PAYDOWN RECORD AS THE
  DEBT.** `sppf_db.py`'s bulk IS its correctness argument — ascending height order, `base`
  surrogate seeding (unseeded re-run = silent corruption), assert-don't-establish after measured
  deadlocks under `make -j 8 promote`. **The reading that called it 76% over was counting the
  documentation of why it is correct as the reason it is wrong**, and a paydown driven by that
  number would have deleted exactly the prose the repo keeps deliberately.

  ⚑ **SO "WHICH IS AUTHORITATIVE" WAS THE WRONG QUESTION TWICE OVER.** Ⓝ80 retires the criterion,
  so neither is; but even while it stood, one predicate was NAMED, extracted and case-covered
  (`code_lines.py`) and the other was an unnamed inline count. **A disagreement between a
  delegated predicate and an inline one is not a tie** — and I recorded it as *"two values,
  neither reconciled"* without opening either, which is the same shape as reporting a census
  result without asking what the census counts.

  ⚑⚑ **AND THE GENERAL FORM IS SHARPER THAN THE INSTANCE: A METRIC THAT PENALISES COMMENTARY
  PUNISHES THE ARTIFACT THIS REPO MOST WANTS.** Every ⚑ block, every recorded incident, every
  *"measured 2026-08-20"* line is the residue this practice exists to keep — `never discard
  residue` is a root memory. **A size budget counting comments is a gate against the repo's own
  discipline**, which is a stronger argument for Ⓝ80's retirement than the modularity one, and it
  is the operator's parenthetical that surfaced it.

* ✅ ⚑⚑⚑ **Ⓝ73 ⟡selftest-contract — READ, AND THE SPLIT I ASKED FOR WAS THE WRONG AXIS. THE
  `substrate/` SUITES WERE BLOCKED, NOT UNCONVERTED.** I asked for *trivially convertible vs needs
  judgement*. The predicate that matters: **does the suite have an emitter it is PERMITTED to
  call?**

      ~200  scratch/ + scripts/   can `import rungs` directly — trivial
      ~50   substrate/            BLOCKED — `scratch/` is unimportable from `substrate/` BY GATE,
                                  and `suite_record` is a READER; all 4 of its importers PARSE
      ~15-20                      genuine judgement (DB-dependent skips, a live TypeError)

  ⚑⚑⚑ **A CONTRACT WHOSE SATISFYING MOVE HAS NO IMPLEMENTATION IS ONE EVERY SUITE IN THAT PACKAGE
  FAILS BY DEFAULT.** That is why the baseline is EMPTY and everything reads NEW — the rendering
  was correct (Ⓝ73's earlier correction stands) **and the debt had a STRUCTURAL cause nobody had
  named.** The agent built the missing half: `substrate/suite_emit.py` + suite (11/11), citing
  `suite_record.RECORD_PREFIX` rather than respelling it.

  ⚑ **BUILT BEFORE CONVERTING, DELIBERATELY:** `rungs.Cases`' own header records the alternative —
  *"55 defs, 55 reimplementing, 0 delegating, 40 of them the identical single statement."*
  **Copying five lines into 249 suites would mint that shape a second time.**

  **COST, WORKED NOT ESTIMATED:** 3 hunks, ~8 lines net; count unchanged 12/12 before and after.
  Verified live: `#row {"key": …, "passed": 12, "total": 12}` plus the prose line.
  ⚑ **AND A COST THE ESTIMATE MUST CARRY: each conversion is ONE ATOMIC WRITE** — import,
  constant and tail cannot land incrementally because every intermediate has an F401 or F821 and
  the gate REVERTS the file. The agent hit this five times. *Mechanizable, but not "edit two
  lines."*

  ⚑⚑ **THE BENEFIT IS REAL AND ARGUED FROM THE CODE:** `read_result` tries record → prose →
  nothing, record FIRST and unconditionally. It buys (a) **`unread` distinguishable from
  `silent`** — a suite printing `PASS` or `0 of 15 check(s) failed` matches no `N/M` and reports
  SILENT *while passing*, recorded as having happened to five restored suites; (b) **`skipped` and
  `reason` expressible at all** — `N/N` cannot say *"8 ran, 4 skipped, the store is down"*, so
  those suites report VACUOUS `0/0` and three different next actions collapse into one;
  (c) the banner can no longer be re-read as the verdict. ⚑⚑ And the sharpest: **`N/M` prose is a
  TEXTUAL QUERY AGAINST A STRUCTURED ARTIFACT — the shape this repo's standing rule forbids
  everywhere else, sitting in the instrument that gates every commit.**

  ⚑ The emitter's own suite pins the round-trip against the ACTUAL consumer, and its load-bearing
  assertion is **`by_prose is False`** — because the human line beside the record *also* satisfies
  the prose regex, so a case checking only counts would pass **with the record entirely unread.**


* ⚑⚑⚑ **Ⓝ79d′ ⟡pt009-assumes-a-runner-we-do-not-RUN — RESEARCHED BY `linux-sources`, AND ONE OF MY
  PREMISES WAS MEASURED FALSE.** I asked them to cite the tools rather than confirm my reading.
  They did both, and the correction is the valuable half.

  **FALSE, as I stated it:** *"I believe there is a standard recommendation here — does
  flake8-bandit expect a test-dir exemption as the norm, and does ruff document one?"* Measured
  against the installed ruff: `ruff check --isolated --select S101` on `def test_foo(): assert 1
  == 1` → **S101 FLAGGED**, and `ruff config lint.per-file-ignores` → **`Default value: {}`**.
  **Ruff ships ZERO default per-file-ignores** and applies S101 inside `test_*` like anywhere
  else. ⚑ The carve-out is **near-universal CONVENTION plus a documented MECHANISM — not an
  inherited default**, and the recollection most likely comes from upstream `bandit`, which does
  have an `assert_used` skip convention. *A convention observed everywhere reads as a default
  until someone runs the tool with `--isolated`.*

  ⚑ **SO MY INSTINCT WAS RIGHT FOR THE WRONG REASON:** I called a `per-file-ignores` entry a
  POLICY change rather than a local fix. Correct — **and because ruff documents it as a policy the
  user states**, not because the tool declines to help.

  ⚑⚑ **THE DOCTRINE QUESTION IS SETTLED BY CITATION, NOT ARGUMENT: PT009 AND S101 CONTRADICT BY
  THEIR OWN "Use instead" BLOCKS.** `ruff rule PT009`: *"To make use of pytest's assertion
  rewriting, a regular `assert` statement is preferred over unittest's assertion methods"* → use
  `assert a == b`. `ruff rule S101`: assertions are stripped under `-O`, *"Consider raising a
  meaningful error instead"* → use `raise ValueError(...)`, **which is not a form a test assertion
  takes.** Enabling both in a test directory with no carve-out is inconsistent **by the rules' own
  recommended outputs** — a citable contradiction, not a reading of an error message.

  ⚑⚑⚑ **AND THE FINDING I DID NOT ASK FOR IS THE ONE THAT DECIDES IT: "just use bare `assert`" IS
  NOT A FREE DISSOLUTION.** PT009 only fires on unittest-style assertion METHODS, so a file using
  `assert a == b` faces ONE rule, not two. **But our pre-commit runs `python3 -m unittest
  discover`, and under unittest a bare `assert` yields a bare `AssertionError` with NO
  introspection** — no `1 != 2` expansion. *That introspection is precisely what PT009's rationale
  is buying, and it comes from pytest's assertion rewriting, which unittest does not provide.*

  **So the trade is two rules for one AND a real loss of assertion diagnostics under the runner we
  actually execute.** ⚑ PT009 is a pytest-ecosystem rule; we run unittest. **The tension between
  the rule and the runner is not incidental — it IS the item**, and no arrangement of ignores
  resolves it.

  **THE TWO COHERENT RESOLUTIONS, and both are doctrine rather than tooling:**
  (a) **adopt pytest** — bare-assert becomes both PT009-clean and diagnostic-rich, dissolving both
  rules with no carve-out; (b) **keep unittest + a warranted `S101` carve-out for `tests/`** —
  honest, because **S101's `-O`-stripping rationale genuinely does not apply to tests never run
  under `-O`**, which is the same warrant `linux-sources` uses for its own scoped S101.

* ⚑⚑⚑ **Ⓝ73′ ⟡selftest-contract-IS-superseded — THE OPERATOR NAMED THE DESTINATION AND IT RETIRES
  THE ARC, NOT JUST THE ITEM.** Operator: *"Not sure what this is, but I know I want to migrate
  away from --selftest and toward proper pytest."*

  Ⓝ73 is a paydown converting ~249 suites from `N/N` PROSE to a typed `#row` record, so the runner
  can distinguish **skipped** from **silent** from **vacuous** — distinctions `N/N` cannot express
  (measured: five restored suites printed `PASS` or `0 of 15 check(s) failed`, matched no `N/M`,
  and reported SILENT *while passing*).

  ⚑⚑ **PYTEST PROVIDES ALL OF THAT NATIVELY.** Skip and xfail with REASONS, structured reporting,
  collection errors distinct from failures, exit codes. **The typed record is a hand-rolled
  reconstruction of a protocol that already exists** — so converting 249 suites to it and then
  converting them again to pytest is **paying twice for one capability.** Ⓝ73 should be marked
  SUPERSEDED, not paused; the ~248 unconverted suites are no longer debt on this road.

  ⚑ **NOT WASTED:** `substrate/suite_emit.py` (11/11) unblocked a genuine structural finding — the
  `substrate/` suites were BLOCKED, not unconverted, because `scratch/rungs.py` is unimportable
  from `substrate/` by gate and no emitter existed on that side. **A contract whose satisfying
  move has no implementation is one every suite in that package fails by default.** That remains
  true and remains worth having recorded.

  ⚑⚑ **AND THE MIGRATION IS LARGER THAN THE FILES, WHICH IS WHY IT NEEDS SCOPING BEFORE DISPATCH.
  The `--selftest` LITERAL IS LOAD-BEARING IN AT LEAST FIVE MECHANISMS:**
  `run_selftests.discover()` keys on it · `suite_gap`'s coverage census keys on it ·
  `ratchet_suites` composes by it · `selftest_mk` GENERATES `Selftest.mk` from it ·
  `gate_status` runs it as a pre-commit gate. **A migration moves discovery, composition, the
  coverage census and a gate — not a directory of files.** ⚑ And it lands assertions into
  `tests/`, which is exactly where Ⓝ79d says none can currently be written — **so Ⓝ79d is not a
  side question, it is the migration's first gate.**


* ⚑⚑⚑ **Ⓝ79d″ ⟡ruff-does-not-enable-it-on-itself — THE ANSWER INVERTS THE QUESTION, AND IT IS
  SHARPER THAN THE CARVE-OUT I WENT LOOKING FOR.** I asked `linux-sources` whether ruff's own test
  suite carves `S101` out. **It does not carve it out — it never ENABLES it.** From
  `astral-sh/ruff`'s own `pyproject.toml` (web-tier source, HEAD, quoted through a fetch):

      select              a CURATED list — categories plus hand-picked codes, NOT ["ALL"]
      from family S       EXACTLY ONE rule: subprocess-popen-with-shell-equals-true
      S101                NOT SELECTED
      PT family           ZERO rules selected — no PT009 either
      per-file-ignores    SECTION ABSENT — no test carve-out needed, because the rules are off
      ignore              drops `assert-false` with: "only relevant if you run a script with
                          `python -0`, which seems unlikely for any of the scripts in this repo"

  ⚑⚑ **THE TOOL'S MAINTAINERS DECLINE THE ASSERT-FAMILY RULE CITING THE SAME `-O` RATIONALE S101
  ITSELF CARRIES.** So the reference strict project's posture is **curate the select and decline
  the assert rules**, not *take ALL and then carve out tests* — and **a project running
  `select = ["ALL"]` + S101 over a test dir is running STRICTER ON ITSELF THAN RUFF RUNS ON
  RUFF.** ⚑ Honest bound, theirs: ruff is a Rust project whose Python is fixtures and scripts, so
  this answers the SELECT/IGNORE POSTURE cleanly and answers *"how a strict project configures a
  pytest suite"* only partly.

  ⚑⚑⚑ **AND THE MAINTAINER RULING EXISTS AFTER ALL — ONE COMMAND, IN OUR OWN ENVIRONMENT.**
  `linux-sources` could fetch only the issue BODY of `astral-sh/ruff#14149` and **explicitly
  refused to infer a ruling from the issue's existence**, offering the revealed config position
  instead and naming the command that would settle it. I ran it (`gh issue view 14149 --comments`)
  and a ruff CONTRIBUTOR answers directly:

      "You can safely ignore S101 in test code, it's only really relevant for runtime code and
       only if you are worried that your code will break in unexpected ways if those assertions
       are removed during compilation."
      [tool.ruff.lint.extend-per-file-ignores]
      "tests/**/*.py" = ["S101"]

  ⚑ **THREE INDEPENDENT SOURCES NOW AGREE AND NONE OF THEM IS MY RECOLLECTION** — the rules'
  own "Use instead" blocks contradict; the maintainers' shipped config declines both; a
  contributor states the test-code exemption with its warrant and its exact spelling
  (`extend-per-file-ignores`, which is additive — not the `per-file-ignores` I would have typed).

  ⚑⚑ **AND THE REFUSAL IS WHY THE ANSWER IS TRUSTWORTHY.** A peer that declined to read a
  maintainer position off an issue title, and named the command that would read it properly,
  produced a better outcome than a peer that guessed correctly would have. *Revealed preference in
  a shipped config beats a forum sentence — and a forum sentence read in full beats both.*


* ⚑⚑ **AND THE MIGRATION'S CASE GOT STRONGER, FROM THEIR READING RATHER THAN MINE:** on real
  pytest the tension dissolves AT THE SOURCE — bare `assert a == b` gets assertion rewriting (the
  introspection lost under `unittest`), **PT009 has nothing to flag** (no unittest methods), and
  **S101 becomes the ONLY question**: one rule, with an honest warrant a contributor states, in
  the additive spelling. **The migration removes a rule PAIR and leaves one warranted carve-out —
  cleaner than adding two ignores to the unittest status quo.**

  ⚑ NOT ESTABLISHED, and they flagged it rather than asserting: no verified Python-project
  reference yet for *strict mypy over a pytest suite + conftest*. They offered to pick and VERIFY
  one rather than name it from memory. **That is the next research question if the migration
  needs a template.**


* ⚑⚑⚑ **Ⓝ79d‴ ⟡tests-may-assert — RULED, AND THE CONFIG ALREADY CONTAINS ITS OWN PRECEDENT.**
  Operator, 2026-09-02: *"The answer: `"tests/*" = ["S101"]`"* — resolving the jointly-unsatisfiable
  pair (PT009 forbids `assertEqual`, S101 forbids `assert`, `tests/` had no entry, so **no new
  test file could contain an assertion at all**).

  ⚑ **AND THE SPELLING QUESTION ANSWERS ITSELF FROM THE BLOCK.** The ruff contributor on #14149
  gave `extend-per-file-ignores`; the operator gave `per-file-ignores`. **The operator's is the one
  that matches**, because `pyproject.toml:340` already declares a `[tool.ruff.lint.per-file-ignores]`
  table with **`"scripts/*" = ["S101"]` carrying the IDENTICAL `-O` warrant**:

      # ⚑ `assert` IS THE SELFTEST IDIOM AND `-O` NEVER RUNS THESE. S101 bans `assert` because
      # it vanishes under `-O`; a gate invoked by the harness or a probe is never run that way.

  `extend-` is for ADDING to a table inherited from another config; this table is declared here.
  *A citation from upstream is not automatically the right spelling for a config that already has
  the section.*

  ⚑⚑ **SO THE RULING IS NOT A NEW EXEMPTION — IT IS THE SAME WARRANT REACHING THE SECOND
  POPULATION IT ALWAYS APPLIED TO.** `scripts/*` got it because gates are never run under `-O`.
  Tests are never run under `-O` either. **The gap was that nobody had written the second line**,
  and the doctrine objection I raised (*"exemptions here are per single-responsibility file, and a
  glob over ~6 modules collides with that"*) is answered by the block itself: **`scripts/*` IS a
  glob**, granted per-PURPOSE rather than per-file, precisely because the warrant is a property of
  how the code is INVOKED, not of what any one file does.

  ⚑⚑⚑ **AND THE BLOCK CARRIES A CAVEAT THAT NOW BECOMES LOAD-BEARING.** Its own comment:
  *"substrate's suites happen to use explicit comparison instead — ONE file verified, not the tree
  (⟡assert-census owed). This exemption is safe for gates and would NOT be safe as a blanket."*
  **The `scripts/*` entry is written as safe-because-currently-unused.** A pytest migration writes
  `assert` into `tests/` **deliberately and everywhere** — so the tests entry is the first one
  whose exemption will actually be EXERCISED at scale.

  ⚑ That is not an argument against it — `-O` is not how tests run, and pytest's assertion
  rewriting is the entire point (Ⓝ79d′: under `unittest` a bare `assert` loses introspection;
  under pytest it gains it). **It does mean ⟡assert-census stops being owed-in-principle and
  becomes a real question about `scripts/*`**, whose asserts, if any, DO vanish under `-O` in a
  way nobody has measured. **Ⓝ79e: census the asserts under `scripts/*` — the entry says one file
  was verified, not the tree.**

  ⚑ **UNBLOCKS Ⓝ71g** — `tests/test_rederive_agreement.py:202` calls `ratchet.may_write(False)`
  positionally against a keyword-only definition, fails a live gate (`gate_status`:
  `FAIL(1) tool unit tests`), and is **one keyword** from correct. The file carries ~165 findings
  so the direct edit is refused; with `tests/*` able to hold an assertion, the drain route is
  open — and under Ⓝ88 that drain is one operation, not a split followed by an annotation pass.


* ⚑⚑⚑ **Ⓝ89 ⟡new-file-writes-BYPASS-the-gate — THE ZERO-TOLERANCE GUARANTEE I QUOTED IN EVERY
  BRIEF TODAY IS FALSE FOR NEW FILES. REPRODUCED BY ME, DELIBERATELY.** The Ⓝ79d‴ agent hit it by
  accident — *"my first version of `test_ratchet_write_guard.py` landed on disk with a SYNTAX
  ERROR and a `noqa`, caught only because I linted manually afterward."* I tested it directly:

      Write substrate/probe_gate_hole.py  ←  content: `def broken(  # noqa: ANN201` + newline
        → "File created successfully."

  **A syntax error AND a `noqa` — two unconditional refusals on an edit — accepted without
  comment.** Probe removed immediately.

  ⚑⚑ **SO THE SENTENCE I HAVE REPEATED ALL SESSION — *"zero tolerance: ruff+mypy on every write;
  ANY finding refuses the write AND REVERTS the file"* — IS TRUE OF EDITS AND FALSE OF
  CREATIONS.** And **every module written this session went in through that path**: `attr_reads`,
  `module_trim`, `doc_split`, `walk_scope`, `suite_emit`, `bare_speech`, `file_mode`,
  `type_census_summary`, `module_importers`, the sixteen runner modules, every new `*_selftest.py`.
  **The clean-in-one-write discipline they were held to was self-imposed, not enforced.**

  ⚑⚑⚑ **AND THAT INVERTS THE PER-FILE GATE'S DESIGN SIGNAL.** The gate's whole teaching —
  recorded in its own refusal text and in `pyproject.toml`'s S603 note — is *extract the concern
  into a NEW module, written clean in one pass*. **The escape hatch it prescribes is the one place
  it does not look.** A monolith is frozen and a new file is unchecked, so the gradient points
  exactly where verification stops. *Every drain this session took that route.*

  ⚑ **IT DOES NOT INVALIDATE THE WORK, AND SAYING SO PRECISELY MATTERS:** every module above was
  checked, by its author, by running `pycheck_show` or the suites afterwards — several agents
  report refusals hit and repaired during creation, which means they were linting deliberately.
  **What is missing is the ENFORCEMENT, not the compliance.** ⚑ But `census-green-is-a-fact-about-
  the-census` applies to the hook itself: **a file that was never checked and a file that passed
  render identically on disk**, and only a case can tell them apart.

  ⚑⚑ **THE FIX IS NOT OBVIOUSLY "CHECK NEW FILES TOO", WHICH IS WHY THIS IS RECORDED RATHER THAN
  PATCHED IN PASSING.** `hook_pycheck` is a PreToolUse hook over `Edit|Write|NotebookEdit`; whether
  it declines to run on a create by design (a new file has no prior state to revert TO, and the
  revert is half the contract) or simply misses the case is a question about the hook's own
  intent. **Ⓝ89a: read `scripts/hook_pycheck.py`'s dispatch and establish which** — a deliberate
  exemption and an oversight need different repairs, and this session has twice recorded
  ABSENT-vs-EMPTY as opposite states wearing one zero.

* ⚑⚑⚑ **Ⓝ71g′ ⟡the-twin-is-a-five-class-drain — PARTIALLY DELIVERED, AND THE AGENT SAID SO
  PLAINLY RATHER THAN CLAIMING THE CRITERION.** *"Before: `FAILED (errors=1)`, 52 tests. After:
  the same error still fires, 54 tests. I did not clear the acceptance criterion."*

  ⚑ **AND THE FINDING IS WORTH MORE THAN THE FIX: THE FAILING ARM WAS ALREADY CORRECTLY OWNED.**
  `substrate/baseline_io_selftest.py:67` pins `may_write(write=False)` **with the right
  spelling**, and `baseline_io.py`'s own docstring **already names
  `tests/test_rederive_agreement.py:202` as a frozen positional caller.** So the monolith's class
  is a **DUPLICATE THAT DRIFTED OUT OF THE SIGNATURE'S REACH WHILE ITS TWIN STAYED GREEN** — the
  derived-view divergence class, occurring inside the file that documents it. The agent did not
  copy it; its module keeps only the arm the sibling genuinely lacks (the
  `SUBSTRATE_RATCHET_WRITE` environment default).

  ⚑ **REMOVING THE STALE CLASS REQUIRES DRAINING ALL FIVE** (`ImportEdgeAgreement`,
  `ImportNameCharClass`, `RatchetWriteGuard`, `ModuleSetAgreement`, `DeclarationVisibility`) —
  *"the step is incomplete until the file is fully drained"* — over guards whose history would be
  rewritten. **It stopped rather than half-do it**, and the two extracted modules
  (`tests/test_ratchet_write_guard.py`, `tests/test_baseline_writers_guarded.py`) are the
  prerequisite. ⚑ `module_trim --dry-run` is ALSO refused here: **the trim tool holds the same
  whole-file bar**, so even removing one class fails.

  ⚑⚑ **AND `check_feature_coverage` WENT BROKEN ON THE NEW SCENARIO NAMES, WITH THE RIGHT FIX:**
  name the scenario the spec **already declares** (`the write guard defaults to read-only`) as one
  case with three arms, rather than mint names `features/` does not have. **A test that invents a
  scenario name is asserting a spec that does not exist.** ⚑ Currently clean *partly because the
  monolith still declares its copies* — completing the drain needs the correspondence rechecked.

  ⚑ **HARDLINKS: RESOLVED AND BENIGN.** Every `tests/` file has link count 2; the twin is
  `/home/mikemol/.claude/file-history/<uuid>/…` — **Claude Code's own pre-edit snapshot store.**
  A `Write` replaces the inode rather than mutating shared bytes, so the snapshot correctly stays
  the "before". No action. *A measurement I flagged as a hazard was the harness's own safety net.*


* ⚑⚑⚑ **Ⓝ89′ ⟡the-hole-is-UNPARSEABLE-not-NEW — Ⓝ89 ABOVE IS WRONG IN ITS MECHANISM AND IN ITS
  BLAST RADIUS. THE OPERATOR ASKED "…how?" AND THE ANSWER FALSIFIED IT.** I wrote that `Write`
  bypasses the gate and that every module created this session was unenforced. **Measured, four
  probes:**

      Write, file DOES NOT exist, `def broken(  # noqa: ANN201`   →  ACCEPTED
      Write, file DOES exist,     same content                    →  ACCEPTED   ← so not new-vs-existing
      Write, valid python, no annotations                         →  REFUSED (ANN201/D103/ANN001)
      Write, valid python, bare `# noqa: ANN001,ANN201,D103`      →  REFUSED BY MYPY   ← noqa is not a bypass

  **`Write` IS GATED.** `_EDIT_TOOLS = ("Write", "Edit", "NotebookEdit")`, and
  `hook_shellcheck.post_edit_content` handles `Write` FIRST and exactly — it carries the whole
  file, so no on-disk read is even needed. The refusals printed correctly, including Ⓝ84's new
  deny text.

  ⚑⚑ **THE DISCRIMINATOR IS THE CONTENT: MY PROBE WAS A SYNTAX ERROR.** `def broken(` with no
  closing paren — **neither ruff nor mypy can parse it, so neither emits findings**, and
  `analyze_python` reads *no findings* as CLEAN. The `noqa` was irrelevant: with valid syntax,
  ruff went silent as instructed and **mypy caught it anyway** — the two-checker design working
  exactly as designed.

  ⚑⚑⚑ **SO THE REAL DEFECT IS `census-green-is-a-fact-about-the-census`, INSIDE THE HOOK: A FILE
  NOTHING COULD ANALYZE AND A FILE THAT PASSED RENDER IDENTICALLY.** That is ABSENT-vs-EMPTY
  again — **which I have recorded twice today and then reproduced in my own diagnosis.** It is
  narrower than I reported and still real, because **a syntax error is exactly what a half-finished
  write leaves**, which is the failure mode a pre-write gate exists to catch.

  ⚑ **AND THE HOOK ALREADY IMPLEMENTS THE FIX FOR A DIFFERENT CAUSE.** `analyze_python` returns a
  TRISTATE: `ok is None` → `_announce_inert` → *"ARMED BUT INERT … no Python is being checked …
  This fails OPEN deliberately."* **UNPARSEABLE belongs in that arm and is currently in the CLEAN
  arm.** The hook's own docstring states the principle it is missing here: *"UNKNOWN IS NOT CLEAN,
  AND UNKNOWN IS NOT GUILTY — a silently-toothless gate must not be able to masquerade as a
  passing one."*

  ⚑⚑ **WHAT I GOT WRONG, AND HOW:** I ran ONE probe, saw it accepted, and generalised to a
  CATEGORY OF WRITE — then stated it as a table and wrote it into the record as *"the guarantee I
  quoted in every brief today is false."* **One observation, one inference, no control.** The
  control was two commands away and I did not run it until asked. ⚑ *Every claim in this session
  that survived did so because someone ran the second command;* Ⓝ89 is what happens when nobody
  does, and the operator's *"…how?"* is that second command arriving as a question.

  **STANDING CORRECTED: the modules written this session WERE gated.** `attr_reads`, `module_trim`,
  `doc_split`, `walk_scope`, `suite_emit`, `bare_speech`, `file_mode`, `type_census_summary`, the
  sixteen runner modules and every new suite passed ruff+mypy at write time. **Ⓝ89a is narrowed:
  route UNPARSEABLE to the inert arm** — not "make the hook check new files", which it already
  does.


* ⚑⚑⚑ **Ⓝ91 ⟡enospc-turns-the-gate-into-a-rubber-stamp — AN AGENT REFUSED TO WORK AND ITS
  REASONING WAS BETTER THAN MY DISPATCH.** I sent four writers at the tree; the `pycodemod` agent
  measured the disk instead and stopped:

      /dev/nvme0n1p2  469G  444G  1015M  100%  /     ← 1015 MB free of 469 GB

  Its argument, verbatim: *"A truncated write under ENOSPC produces exactly that — a half-written
  file that neither checker can parse, that reports CLEAN, and that gets banked as good. The disk
  condition converts the stated safety net into a rubber stamp, on the one file class where I'd
  have no independent signal."*

  ⚑⚑ **SO Ⓝ89 STOPPED BEING A CURIOSITY AND BECAME THE EXPECTED FAILURE MODE.** I recorded
  *unparseable reads as CLEAN* an hour earlier as a narrow defect worth one branch. **Under ENOSPC
  it is what EVERY write degrades to** — and both checkers would have blessed each one. *A defect's
  severity is a function of the conditions, and I filed it at the severity of the day it was
  found.*

  ⚑⚑⚑ **AND THE AGENT FOUND IT THE WAY THIS SESSION KEEPS FINDING THINGS: A WRITE FAILED WHERE IT
  DID NOT EXPECT ONE.** *"redirects to the scratchpad fail with ENOSPC, which is itself how I found
  the disk state."* It was capturing before-output, hit an error that was not about its task, and
  followed it instead of routing around it.

  ⚑ **I STOPPED THE OTHER THREE MID-FLIGHT** — one was writing (*"Now the producers module"*) —
  and verified the tree: **no partial files.** `sorted_stream.py` untouched, `test_rederive_
  agreement.py` unchanged, nothing new under `substrate/` from the killed runs.

  ⚑⚑ **THE CONSUMER WAS NOT OURS, AND THE AGENT DECLINED TO RECLAIM IT.**
  `~/.cache/paperkit-sweep` held **96 GB** across 13 `paperkit-delta-*` directories, mtimes minutes
  old and still growing — a LIVE sweep from another repo (`agda/_build` is 86 MB). *"I did not
  delete it — it is being written right now, it is outside my ownership, and reclaiming it would
  destroy another repo's work in flight. It needs its owner's call, not mine."* **An agent with a
  blocked task and an obvious 96 GB fix, correctly refusing to take it.**

  ⚑ **RESOLVED BY THE OPERATOR: 104 GB free, 77%.** Redispatching.

  ⚑ **AND ONE CONSTRAINT WAS SHARPENED BEFORE IT STOPPED:** `substrate/tool_usage_selftest.py`
  quotes the `--attr` gloss VERBATIM, and **`--attr` is a RETIRED mode** refused at the hook. The
  verbatim-quote constraint and the retirement are COUPLED — whatever happens to that doc text
  must keep both the selftest and the hook refusal green. `--literal pycodemod.py` → 115 sites in
  40 files; `_dispatch` confirmed at `:1878`, 2,173 lines.


* ✅ ⚑⚑⚑ **Ⓝ89a ⟡unparseable-is-not-clean — LANDED, AND MY MECHANISM WAS WRONG A SECOND TIME. THE
  CORRECTION FOUND A DEFECT NEITHER OF US WAS LOOKING FOR.** Verified by me, the exact write that
  was ACCEPTED an hour ago:

      Write substrate/zz_verify_unparseable.py  ←  `def broken(  # noqa: ANN201`
        → REFUSED.  --- syntax ---  '(' was never closed (line 1)  [syntax]
      Write a clean annotated module               → ACCEPTED   ← the discriminator holds

  ⚑⚑⚑ **I SAID: NEITHER CHECKER CAN PARSE IT, BOTH REPORT NOTHING, EMPTINESS READS AS CLEAN.
  MEASURED, THAT IS NOT WHAT HAPPENS.** `ruff` on `def broken(` exits 1 with
  **`invalid-syntax: unexpected EOF while parsing` — A FINDING.** *ruff was refusing it correctly
  all along.* mypy exits 2, which `run_checker` honestly reads as UNKNOWN — and
  **`analyze_python`'s loop RETURNS ON THE FIRST `None` IT SEES, DISCARDING THE FINDING RUFF HAD
  ALREADY COLLECTED.**

  **So the fail-open was A REAL REFUSAL OVERWRITTEN BY A LATER CHECKER'S UNKNOWN — an ORDERING
  ACCIDENT**, not a blind spot. The `--check-file` output proved it: `UNKNOWN` printed with ONLY
  mypy's report and no ruff section. ⚑⚑ **A fix keyed on my premise — *both checkers are blind* —
  would have missed it**, and the hole would have survived a parse-aware checker.

  ⚑ **AND THE DETECTOR IS `ast.parse`, NOT A SCAN OF EITHER CHECKER'S MESSAGE TEXT** — *"keying on
  vendor wording in a gate whose whole subject is not confusing the instrument for the substrate
  would be self-defeating."* It runs BEFORE the checkers, **so the verdict no longer depends on
  who speaks last.**

* ⚑⚑ **THE STATE CHOICE, AND THE RATIONALE INVERTS RATHER THAN FAILING TO APPLY.** UNPARSEABLE is
  resolved onto the REFUSING side (`False`) — not a fourth return value, and NOT the `ok is None`
  arm. That arm fails open because *"a gate cannot deny every edit because its own dependency is
  missing, and could not be repaired from inside the session it broke."* **On a syntax error the
  checkers ran FINE and the FILE is broken, and the author repairs it with their very next write
  without restoring anything.** ⚑ A genuinely fourth return value would have forced a new arm into
  every consumer to express a verdict `False` already carries.

  ⚑⚑ **AND THE MID-REPAIR TRAP I WORRIED ABOUT DOES NOT EXIST — VERIFIED LIVE, NOT ARGUED.** The
  hook gates POST-EDIT content, so the only writes refused are those whose RESULT does not parse;
  a repair parses and is admitted however broken the file was before. The agent created an
  unparseable file on disk outside the hook and repaired it through the hook: **admitted.**
  ⚑ It deliberately did NOT build an "improves parseability" allowance — **it would be strictly
  WEAKER, admitting a write that leaves the file unparseable, which is exactly the ENOSPC
  artifact this closes.** *The guard I asked for would have reopened the hole.*

  ⚑ **THE INERT PATH STILL FAILS OPEN, VERIFIED WITH A BROKEN INTERPRETER:** both `None` guards
  precede the syntax check, so **an unparseable file in a TOOLLESS environment is still UNKNOWN,
  not a refusal.** The gate does not start denying edits when its own dependency is missing —
  which is the ordering the not-a-fourth-value choice buys.

  **Files:** `scripts/pycheck_syntax.py` (new, 0755) — `syntax_error(content, path)`, empty means
  parses, **catching `ValueError` alongside `SyntaxError` because a NUL byte is the reachable case
  and a truncated write is exactly how one arrives** · `pycheck_analyze.py` (syntax check before
  the loop; also paid down a pre-existing I001 that made the file un-editable under its own gate)
  · `hook_pycheck.py` (+`_cases_syntax`, 6 arms including **still-admits-clean**). Hook `--selftest`
  **19/19**. ⚑ `check_hook_set --manifest` picked the new sibling up from the IMPORT GRAPH — *"5
  declared, 5 on disk"* — **no hand-maintained roster to drift** (Ⓝ85's rule, already built here).

  ⚑ **AND THE GATE REFUSED TWO OF THE AGENT'S OWN INTERMEDIATE EDITS** (F401: an import landed
  before its use), forcing import+use into one atomic write. *The zero-tolerance claim holding
  against the author fixing it is the paired-arm evidence that it is not refusing everything.*


* ✅ ⚑⚑⚑ **Ⓝ91a ⟡the-first-none-wins — LANDED, AND THE AGENT FOUND A FOURTH STATE MY FRAMING
  MISSED. IT IS THE DANGEROUS ONE.** I named two lossy options for MIXED (UNKNOWN discards a true
  finding; findings-only hides partial coverage) and proposed *both*. The agent agreed and then
  named the case I had not:

      all(True or None), at least one None      ruff CLEAN, mypy CANNOT RUN

  **Neither of my two.** ⚑⚑ *"Banking it as a pass is `census-green-is-a-fact-about-the-census` in
  its purest form: the checker that didn't run is EXACTLY the one that might have objected."* It
  resolves to `None` — fails open, announces. **So the fold covers four states, not three**, and
  the one I missed is the one that would silently bank a green.

  ⚑⚑⚑ **AND THE ARGUMENT FOR THE REFUSING ARM IS SHARPER THAN MINE: A FINDING IS MONOTONE
  EVIDENCE.** *"A checker ran, saw the content, objected. Nothing an un-run checker MIGHT have
  said can retract that — so `any(False) → False` regardless of what sits beside it."* That is the
  arm the defect inverted, and stating it as monotonicity explains WHY order-independence is the
  right repair rather than merely a safer one.

  ⚑ **THE FOLD IS A NEW SIBLING (`scripts/pycheck_compose.py`), NOT A PATCH IN THE LOOP.**
  `analyze_python` now COLLECTS `(name, outcome)` and hands the SET to the fold — **so permuting
  the roster cannot change the verdict**, which is the defect stated as a property. ⚑ And **the
  all-UNKNOWN case is NOT special-cased** — it falls out of the no-findings-plus-any-`None` arm.
  *That the general rule SUBSUMES the instance is the evidence it is a rule and not a patch shaped
  around the bug.*

  **Verified by me:** `hook_pycheck --selftest` **31/31** (was 19) · a clean module still ADMITTED
  · a dirty one still REFUSED with `F401` **and no `--- coverage ---` note**, because coverage was
  full. *The note appears only under partial coverage, so it carries information rather than
  decorating every refusal.*

* ⚑⚑ **THE MISSING-CHECKER PROBE WAS BUILT TO AVOID PROVING THE FOLD AGAINST A MOCK.** mypy was
  made genuinely unlaunchable via a **fake venv** — a shim `python3` that execs the real
  interpreter for everything except the named checker (exit 127). *"Nothing in the verdict path is
  stubbed; only the launch fails. I deliberately avoided monkeypatching the roster — that would
  have proved the fold against a mock."* Six live payloads through `main`, and the one that
  matters:

      C: ruff finds, mypy cannot launch  →  DENY, F401 SURVIVES, plus
         --- coverage ---
           ⚑ PARTIAL: this verdict rests on the checkers that RAN. These did not:
             - mypy exited 127: no such interpreter

* ⚑⚑⚑ **AND MY FLAGGED HAZARD WAS REAL, WITH THE OPPOSITE RESOLUTION TO THE ONE I EXPECTED.** I
  asked whether `_announce_inert`'s once-per-process guard would interact badly. It would have —
  *"had I attached partial-coverage there, the SECOND refused file in a session would carry a
  silent coverage claim."* **So the blindness deliberately does NOT route through it**: the guard
  is correct for a STANDING condition (venv absent — say it once) and wrong for a PER-WRITE fact.
  The note rides in the verdict's own report, bounded by the existing `clip`/`MAX_LINES` budget.
  ⚑ *Two facts with different lifetimes cannot share one announcement channel* — and E/E2 prove
  the standing notice still fires exactly once.

  ⚑ **`pycheck_verdict.py` UNCHANGED** — *"the per-checker tristate was already correct; the defect
  was purely in the composite."* The repair is where the defect was, not spread across the family.
  ⚑ The gate **refused the agent's own first three attempts** (import-before-use ×2, then a real
  `EXE001` on the new file's missing exec bit) — *it is working, and it accepted edits to itself,
  so it is not in the un-repairable state.*


* ⚑⚑⚑ **Ⓝ90 ⟡the-five-stale-censuses — 1 SYNCED, 1 SELF-RESOLVED, 3 REFUSED, AND THE CAUSES SPLIT
  THREE WAYS RATHER THAN THE TWO I BRIEFED.** I framed it as *tree-moved (sync) vs uncommitted-work
  (don't)*. The third cause is **a concurrent writer mid-drain**, and it is the one that decided
  two of the three refusals.

  **SYNCED — build census.** Drift `33930→33919` import edges is the Agda tree moving under
  today's landings: tracked source, legitimate. ⚑ But it banked the same `35→36` gate figure whose
  CAUSE is refused below — *the count is honest (the gate really is wired in
  `.githooks/pre-commit`); its IMPLEMENTING SCRIPT is untracked.* Flagged as owed, not as an error.

  **SELF-RESOLVED — selftest roster.** First read: 20 findings (19 undeclared suites from today's
  landings, one declared-but-missing). Minutes later: **clean, `Selftest.mk` byte-identical to
  HEAD.** *"Nothing I did caused that — the concurrent agent landed the declarations in the
  interval. Both readings were honest readings of a tree that moved between them."*

* ⚑⚑⚑ **THE SQL CENSUS REFUSAL TURNS ON THE DIRECTION OF THE DRIFT, AND I VERIFIED IT.**
  `sql_lift --check-census`:

      1198 → 1177 pipelines · 2631 → 2592 carrier nodes
       119 → 114  licensed lifts · 61 → 59 recursion-pole · 51 → 49 carrier-unmodelled

  **Every count moves DOWN. Interning six NEW files would push them UP.** ⚑ So this is **a DRAIN
  SIGNATURE, not an internment** — the concurrent agent pulling pipelines out of `schema.py`.
  Syncing would bank a **half-drained snapshot** and freeze `carrier-unmodelled` at 49,
  **understating the ⟡graded-relational-carrier work remaining — in the census that exists to make
  that work legible.**

  ⚑ And the agent verified the internment premise rather than trusting my brief: `_py_files()` is
  a **filesystem glob**, not git-scoped, so the six untracked files ARE in the corpus. **The
  hazard I named is real and is not what is moving these numbers.**

  **TOOL MODE CENSUS — refused, and the contamination is precise:** `schema.py` gains `--sizes`
  (undocumented) — *the file I told it not to touch, mid-edit* — and `sorted_stream.py` vanishes
  entirely, the same agent's drain. ⚑ It used the offered oracle first: **`toolmodes --selftest`
  104/104, so the tool is correct and the staleness is real drift, not a defect.**

  **GATE CENSUS — refused, both drift terms from untracked files:** `ratchet_legacy.py` drives
  `17→18` and the `UNREAD` baseline row; `selftest_mk.py` is the new 36th gate. *"Syncing would
  record `ratchet_legacy.py` as a ratchet WITH NO BASELINE LITERAL — i.e. a gate that takes the
  absent-baseline free-pass branch."* **Stable across two reads**, so not a race.

* ⚑⚑⚑ **THE STRUCTURAL FINDING REFRAMES THE HAZARD I BRIEFED — VERIFIED BY ME: ALL FIVE CENSUS
  HOST FILES ARE UNTRACKED.** `git status --untracked-files=all .claude/skills` → `??` on
  `build-system`, `precommit-gates`, `sql-relalg`, `struct-tools`, `agda-codemod`,
  `transcript-mining`, `witness-tower`.

  **So "banking into a GATED artifact" cannot happen via git here — these blocks live only in this
  working tree.** ⚑ The hazard is real and its mechanism is different: **the danger is a block
  that reads as DERIVED-AND-AUTHORITATIVE to the next reader while resting on source git has never
  seen.** *A generated block's authority comes from being derived, and nothing about being
  untracked diminishes how derived it looks.* The three refusals stand on that reading.

  ⚑⚑ **AND THE FAILURE THIS TASK GUARDS AGAINST WAS ALREADY REALIZED BEFORE THE AGENT ARRIVED:**
  HEAD's `Selftest.mk` **already declares a target for `sorted_stream.py`, a file git has NEVER
  held** (`git log` empty). *A previous sync banked untracked work into that roster.* **The
  precaution I wrote the brief around has a prior instance in the committed tree.**

* ⚑⚑ **AND THREE OF THE FIVE TRACK ONE WRITER.** Selftest roster, sql census and toolmodes are all
  following the same `schema.py`/`sorted_stream.py` drain — the roster already flipped green
  without a write, and the other two go stale again the moment it lands. *"Chasing them now buys
  nothing"* — which is the brief's own instruction, applied.

  **OWED, and the last three are the interesting ones:** re-run the three refused censuses after
  the drain lands and the six files are committed · **`scripts/ratchet_legacy.py` untracked, so
  the 18th ratchet is a gate with no baseline (free-pass branch)** · **`substrate/selftest_mk.py`
  untracked YET WIRED AS A BLOCKING GATE in `.githooks/pre-commit` — a clean checkout FAILS this
  gate** · `Selftest.mk`'s pre-existing `sorted_stream` declaration · **and whether five untracked
  `SKILL.md` census hosts is intended, since it means no census here is actually under git's
  gate.**

  ⚑ Process note: `gate_census --sync` refuses without an explicit `--apply`/`--dry-run`
  (mutation contract). *"I did not force it — my intent there was refusal, so I left it."*


* ⚑⚑⚑ **Ⓝ93 ⟡twenty-red-and-two-populations — THE AGENT'S CAUTION WAS RIGHT AND NEEDED SPLITTING,
  AND I WOULD HAVE RELAYED IT WHOLE.** It corrected its own framing unprompted: *"My report said
  the five censuses were the stale surface. More precisely: they were the five SYNC gates I was
  asked about, and they are five of TWENTY red gates. Anyone reading my report as 'fix these five
  and the tree is green' would be badly misled."*

  **36 gates: 16 pass, 20 FAIL.** Fifteen of the twenty are ratchets reporting NEW debt — mypy
  1132, ban 375, cap 146, rederive 42, public 35, sumtype 26, divergence 14, claims 7, discharge
  4, carrier-locality 2, private 2. Its caution: *"almost certainly not real debt… a tree with
  four agents mid-flight and six untracked modules will light up every EMPTY-baseline ratchet at
  once. The honest statement is that these counts are facts about the BASELINES, not yet facts
  about the TREE."*

  ⚑⚑⚑ **I RAN `gate_census --baselines` AND THE FIFTEEN SPLIT INTO TWO POPULATIONS THE CAUTION
  COVERS ONLY ONE OF:**

      EMPTY (zero-tolerance, nothing grandfathered — the caution HOLDS)
        mypy 1132 · cap 146 · divergence 14 · mode-contracts 1 · sorted-order · clause-unused
        snapshot-guard ×3 · selftest-contract · set1

      ok (a REAL recorded baseline, and STILL reporting NEW — the caution does NOT hold)
        ban 15552 keys → 375 NEW · public 552 → 35 · private 226 → 2 · rederive 133 → 42
        sumtype 48 → 26 · discharge 28 → 4 · claims 14 → 7 · carrier-locality 5 → 2

  **Eight ratchets carry grandfathered sets and report additions PAST them.** ⚑ So ban's 375 and
  rederive's 42 are *not* zero-tolerance artifacts — they are genuine additions against a
  baseline that already tolerates 15,552 and 133 respectively. **The caution is exactly right for
  eleven and exactly wrong for eight, and only the baseline census distinguishes them.**

  ⚑ *This is the fifth time today the ABSENT/EMPTY/ok distinction has decided a reading* — and the
  first time the answer was "both, and you must split the population." **A verdict that is true of
  most of a set reads as true of the set**, which is the shape that let me carry "postgres is
  down" for a session (Ⓝ92) and "the size budget measures bulk" (Ⓝ71b).

  ⚑⚑ **AND ITS OTHER SELF-CORRECTION IS THE MORE TRANSFERABLE ONE:** *"I wrote that
  `gate_status --list` confirms 36 wired gates. That was the DECLARED roster. This run is the
  OBSERVED one… the build census block I synced carries the declared count and the two are
  DIFFERENT MEASUREMENTS."* **They agreed here, which is why the conflation was invisible** — a
  declared/observed pair that happens to match is the one case where nobody notices they are two
  questions.

* ⚑ **THREE ITEMS ADDED TO WHAT IS OWED, EACH NAMING ITS OWN FIX:**
  **`snapshot guard`** specifies a one-line mitigation — insert `edit_snapshot.guard(...)` at
  `scratch/split_census.py:768`, above the first write in that run. *A gate that names the exact
  edit is the cheapest red on the board.*
  **`scratch-independence (Λ8)`** — a promoted project depends on `scratch/` at runtime, which is
  the invariant the drain arc exists to restore.
  **`Set₁ ratchet` exits 2, not 1** — a guard refusing the INVOCATION (*"states it in code:
  `tenant(require='live'|'sandbox')`"*), so it **assessed nothing.** ⚑ Same class as the REFUSED
  suites: **not a failure, an unmeasured gate** — and it would read as a failure in any count that
  sorts by exit status rather than by verdict.

  ⚑ **The fifteen ratchet reds want a baseline audit before anyone treats those counts as debt**,
  and the `gate-oracle` is the instrument. **Ⓝ93a** — and per the split above, that audit's first
  job is the eight `ok`-baseline gates, because those are the ones whose NEW keys are real.


* ⚑⚑⚑ **Ⓝ93a ⟡baseline-audit — TWENTY RATCHETS, AND THE HEADLINE ROW IS A REPAIR SCORED AS DEBT.**
  `gate-oracle`, verified by me on the two load-bearing claims. Not 15 ratchets — **20**
  (`check_snapshot_guard.py` contributes THREE baselines): **8 ok · 11 EMPTY · 0 ABSENT · 1 UNREAD**.
  ⚑ **Zero ABSENT** — the free-pass state I had been treating as the danger is not present at all;
  `ratchet_legacy.py` is the UNREAD one, and it is why `--check` fails.

  ⚑⚑ **`private`: 2 NEW KEYS BLOCK 166 PAYDOWNS, AND BOTH NEW KEYS ARE THE CORRECT REPAIR
  MID-FLIGHT.** Verified directly (`check_private_ratchet.py --quiet`):

      + OrientationRigCatPerm/Private.agda::lookup-swPerm     ← the DESTINATION
      + OrientationRigCatPerm/Private.agda::lookup-γ
      - OrientationRigCatPerm.agda::lookup-swPerm             ← the SOURCE, in the paydown list
      - OrientationRigCatPerm.agda::lookup-γ

  **One move, same two names, two files — scored +2/−2 instead of a wash, because the ratchet keys
  on `path::name` and sees the destination before it credits the source.** The gate's own refusal
  text prescribes exactly this extraction (*"EXTRACT it to its own file and bind it at the
  owner"*), so **the gate is refusing the act it demands.** ⚑ And the 166 held hostage are
  unrelated genuine paydowns across F2, Nat, Quotient, Coxeter, WitnessTower.

* ⚑⚑⚑ **NO RATCHET CAN DATE A NEW KEY — `gate-F44`.** Verified: `git log -1 --format=%cd` on the
  baselines → **Tue Jul 28 05:49:24 2026**. Every baseline was banked FIVE WEEKS ago, so "NEW"
  means only *after Jul 28*, and **no read mode carries a per-key timestamp.** A five-week-old
  regression and a five-minute-old one are the same row. *That is what makes the `private`
  misreading invisible: nothing says the two additions arrived in the same edit as the 166.*

* ⚑⚑ **`gate-F43` — THE BAN RATCHET'S NEW KEYS ARE UNREACHABLE BY ANY READ MODE.** 15,552 keys,
  over half the surface's debt, and the 8,516-line paydown list **exhausts output before the NEW
  block**. My "375 NEW" figure could be **neither corroborated nor refuted** — a fact about the
  reader, banked as a fact about the tree. ⚑ *The biggest ratchet is the one with no way to read
  the half that blocks it.*

* ⚑ **`set1_ratchet_cores.py` EXITS 2 — UNMEASURED, NOT FAILING.** A guard refused the invocation,
  so it assessed nothing. **Any count sorting by exit status reads it as a failure**; only a
  verdict-sorted count is honest. Same shape as `census-green-is-a-fact-about-the-census`, inverted.

  ⚑ The oracle's standing note, carried unresolved: *"the `private` row is the clearest case of
  debt that was occluded — four of the eight `ok` gates are hiding some."*
















* ⚑⚑⚑ **Ⓝ124 ⟡gates-per-file — BOTH OF MY CATEGORY-(a) EXAMPLES WERE FALSE, AND ONE IS A DEFECT IN
  A GATE BUILT TODAY.** I cited `check_dep_addressing` and `stub_top_type` as proof that per-file
  gates already exist here. **Neither is on the roster:** `stub_top_type`'s own docstring says *"THIS
  IS A READER, NOT A WIRED GATE, AND THAT IS DELIBERATE"*, and `check_dep_addressing` **declares
  `_FLAGS` and IGNORES a path operand** — verified by me: passed `pyproject.toml`, it exits 0
  silently having read its own fixed file.

  ⚑⚑ **THAT IS THE FOURTH INSTANCE TODAY OF A TOOL ACCEPTING AN OPERAND AND SILENTLY DISCARDING
  IT** — after `module_size.py <path>` returning the whole corpus, `type_gate` ignoring its path,
  and `store.py`'s CLI ignoring every flag it did not know. *In a gate built THIS SESSION, with
  `ratchet_flags.check_argv` available and unused.* **Ⓝ124a ⟡dep-gate-ignores-its-operand.**

  ⚑ **AND THE ROSTER COUNT I GAVE WAS STALE:** `build_census --gates` reads **37 declared**, not 31.

* ⚑⚑ **THE CENSUS: (a) ZERO wired per-file gates · (b) the majority inherently whole-tree ·
  (c) ~FIVE whole-tree BY ACCIDENT** — def/proof separation, ban / public / private ratchets,
  snapshot guard. Each is literally `for path in agda_files(): <predicate over that file's own
  text>`. ⚑ **The cost is NOT the `iface_dataflow` O(slots × corpus) shape** — *there is no index to
  invert, because each iteration is already independent.* Extracting `census_one(path)` and making
  `census()` its union is mechanical; `check_carrier_locality.scan(paths=…)` is the standing
  precedent.

  ⚑ **AND (b) ARGUES FOR ITSELF IN THE SOURCE.** `check_carrier_locality.judge()`'s docstring:
  *"its `unique` filter … is a global property, so scanning a subset and judging it would call every
  carrier unique."* **Note `scan()` ALREADY accepts `paths=` — so the per-file question was
  anticipated and refused ONE LAYER DOWN, at `judge()`.** *The distinction was drawn by the author,
  not discovered by this census.*

* ⚑⚑⚑ **THE MEANING IS WHERE THE PAYOFF SHRINKS, AND IT IS THE INTERESTING HALF. A PER-FILE GREEN
  CANNOT BE A RATCHET VERDICT.** NEW-vs-PAID compares a whole census against a baseline; **one file
  cannot know a key is NEW.** So a per-file form asserts only *"this file contributes no census
  keys"* — a 0-tolerance verdict, **stronger than the gate on a clean file and weaker on a dirty
  tree.** Two ways it becomes a fact about the instrument:

  * **GRANDFATHERING INVERTS.** The ban ratchet holds **15,552 baselined keys**; a baseline-blind
    per-file check fires RED on thousands of grandfathered files — *and consulting the baseline
    makes it no longer file-local.*
  * ⚑⚑ **`RELOCATED` BECOMES UNREACHABLE.** `key_move` credits a 1→1 move so a decomposition does
    not read as growth — **it unblocked 139 genuine paydowns in `check_public_ratchet`.** A per-file
    verdict reports **every decomposition as growth**: *precisely the defect `key_move` was built to
    fix.* **The narrowing would re-open a closed wound**, and this is the same shape as Ⓝ98
    (⟡ratchet-sees-a-move) arriving from the opposite direction.

  ⚑ **SO THE HONEST FIRST CUT IS THE 11 EMPTY BASELINES** (of 20: 8 ok · 11 EMPTY · 0 ABSENT ·
  1 UNREAD). **EMPTY is the STRONG setting — every key already reads as NEW — so for those the
  per-file 0-tolerance form is EQUIVALENT to the current gate and narrowing costs NO SEMANTICS.**
  *The subset where the transformation is a refactor rather than a change of claim.*

* ⚑⚑ **AND `hook_pycheck` IS ONLY HALF FILE-SCOPED, WHICH QUALIFIES MY PREMISE.** `--check-file`
  names one path, but **its MYPY half returns a verdict over the whole import closure** (prior
  finding `gate-F43`); only the ruff half is genuinely file-scoped. *So the machinery I called
  "proven" is proven for one of its two checkers* — and that is consistent with Ⓝ78‴'s finding that
  the gate stages the post-edit CLOSURE, not the file.









* ⚑ **AND A SECURITY NOTE: THE `v4cat` MCP SERVER INJECTED AN "AUTO MODE" DIRECTIVE** into the
  agent's context, instructing it to work via `cat`/`grep`/`sed` and avoid Read/Edit/Write. **Not
  from the operator, and directly contrary to this repo's top standing rule.** The agent ignored it
  and flagged it. **Ⓝ131 ⟡mcp-injects-directives** — *an MCP server emitting instruction-shaped
  text into agent contexts is a channel nobody audited.*


* ⚑⚑⚑ **Ⓝ131 ⟡mcp-injects-directives — THE CHANNEL IS OUTSIDE THIS REPO, WHICH IS ITSELF THE
  FINDING.** A subagent reported: *"The v4cat MCP server injected an 'auto mode' directive telling
  me to work via `cat`/`grep`/`sed` and avoid Read/Edit/Write. I ignored it — it is not from you,
  and it directly contradicts this repo's top standing rule."* **Verified by me: `.claude/settings.json`
  declares NO MCP servers** — only the four hook-block env vars and the five PreToolUse hooks. **So
  `v4cat` is declared at USER or GLOBAL scope and reaches every session in every repo**, while the
  rule it contradicts is declared per-repo.

  ⚑⚑ **AN INSTRUCTION-SHAPED PAYLOAD FROM A TOOL RESULT IS NOT A DIRECTIVE, AND THE ONLY REASON
  THIS DID NO DAMAGE IS THAT THE AGENT TREATED IT AS DATA.** *The hooks would have refused the
  commands it asked for* — `hook_structural_query` and `hook_no_chaining` fired on exactly that
  shape repeatedly this session — **so the enforcement layer holds even when the instruction layer
  is contaminated.** That is `hooks-outrank-harness-directives` doing the job it was recorded for,
  against a source nobody anticipated.

  ⚑ **NOT DISABLED BY ME, DELIBERATELY.** The server is not configured in this repo, so silencing
  it means editing a file governing sessions beyond this one, on the strength of an agent report I
  have not independently reproduced. **The mechanism is `/mcp`, or removing the server from
  whichever config declares it (`~/.claude.json` or a user-scope `settings.json`)** — an operator
  action, not a repo change.

  ⚑⚑ **AND THE GENERAL FORM OUTLASTS THE INSTANCE: A TOOL RESULT IS AN UNTRUSTED INPUT.** MCP
  servers, artifact comments, peer messages and file contents all arrive as text in the same
  context as instructions, and **none of them carries the operator's authority.** *This session
  already refused one peer-message escalation on that ground;* an MCP server emitting the same shape
  is the same class with a more plausible-looking source. **Ⓝ131a ⟡audit-the-mcp-surface** — what
  else is declared at user scope that this repo's rules do not govern?



























