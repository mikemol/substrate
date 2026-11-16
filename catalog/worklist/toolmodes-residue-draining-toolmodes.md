# Ⓝ31 residue — draining toolmodes

**Concern: the arc's named subject — n-splitting `scratch/toolmodes.py` into layers, and the
carrier that split should have used.** Index and arc frame:
[`toolmodes-split.md`](toolmodes-split.md).

⚑ Ⓝ31h″ found the real remainder (four layers have no renderer); Ⓝ31j was blocked on a missing
denominator; Ⓝ31m dissolved that block by naming the eager shape as the cause and ⟡sorted-stream
as the carrier already built one directory over; Ⓝ31m″ typed that carrier. The type-migration this
thread hands off to is [⟡symbolic-reference-only](toolmodes-residue-symbolic-reference-only.md);
the frozen-file constraint it keeps hitting is
[the frozen monoliths](toolmodes-residue-the-frozen-monoliths.md).

## Residue

* **⟡findings-two-homes** — `scratch/findings.py` and `.claude/agents/findings.py` are DIFFERENT
  files sharing a name; the second is the Ⓝ27b orphan (50/50, unreachable because
  `suite_discovery.roots()` filters dot-dirs). Do not conflate them.
* **⟡compile-recipe-stranded** — `substrate/compile_recipe.py` (16/16) waits on
  `gen_build_makefiles.py` being drained the same way. Same shape, different monolith: Ⓝ30a′.

* ⚑⚑⚑ **Ⓝ31h″ ⟡retire-toolmodes — ATTEMPTED 2026-09-01, AND THE ATTEMPT FOUND THE REAL REMAINDER:
  FOUR LAYERS HAVE NO RENDERER.** `substrate/tool_modes.py` was written twice and refused by
  pycheck both times; nothing landed. The second refusal was the useful one — it named
  `tool_gap_render` and `tool_overlap_render` as imports of modules that do not exist, and
  `tool_convention_audit.render` / `tool_decline_run.render` as attributes that do not exist.

  **The layers return DATA and stop there.** Verified by reading each surface
  (`module_outline` over all eight): `tool_overlap` gives `collisions()` / `siblings()`,
  `tool_gap` gives `capability_gaps()` / `divergence()`, `tool_convention_audit` gives
  `standing()` / `required_pairs()`, `tool_decline_run` gives `verify() -> Report`. Only
  `tool_report.render` and `tool_find_render.render` turn data into output.

  ⚑⚑ **SO THE SPLIT IS NOT NINE-TENTHS DONE; the origin's `cmd_*` functions were BOTH the
  computation and the rendering, and only the computation was extracted.** `cmd_collisions` (45
  lines), `cmd_siblings` (58), `cmd_gaps` (73), `cmd_divergence` (34), `cmd_conventions` (80),
  `cmd_nearmiss` (33) and `cmd_declines` (94) each still hold their presentation layer. The
  arc read as one wiring step away from retirement because the census-building half was the half
  that got parity-checked — **a completion estimate keyed on the half that was measured.**

  ⚑ **WHAT THE ATTEMPT DID ESTABLISH, and it is worth keeping:** the dispatch shape is a TABLE
  of `(census, parsed) -> int`, not an if-chain (the chain tripped C901/PLR0911 at 13 branches —
  the gate reading the shape correctly); `ratchet_flags.check_argv` is the shared authority for
  the unknown-flag refusal (45 call sites, and it folds in `UNIVERSAL_FLAGS`), so `tool_cli`
  correctly owns only the ROSTER; and `tool_decline.invisible` — not `tool_gap` — is where the
  undocumented-flag count comes from.

  **Remaining, in order:** `tool_overlap_render`, `tool_gap_render`, `tool_convention_audit`'s
  render half, `tool_decline_run`'s render half — each parity-checked against the origin's `cmd_*`
  WHILE IT IS STILL ON DISK — then `tool_modes.py`, then the routing-table repoint, then the
  deletion.

* ⚑ **AND `--find render` CONFIRMED THE POPULATION BLIND SPOT AGAIN, LIVE.** The origin reports
  82 hits over **98 tools** and lists neither `tool_report.render` nor `tool_find_render.render`
  — both exist. `_TOOL_DIRS` omits `substrate/`, which is the defect layer 1 fixed and the reason
  a capability search inside this arc cannot see the arc's own output.

* ⚑⚑ **Ⓝ31j ⟡render-halves — STARTED 2026-09-01 on `tool_overlap_render`; BLOCKED ON A MISSING
  DENOMINATOR, which is a gap in the COMPUTATION layer rather than the renderer.**

  The origin's `cmd_siblings` prints, for each of three family signals, `N cross-tool X of M Y` —
  where **M is the count over the UNFILTERED population** (`len(bysig)`, `len(kinds)`,
  `len(vocab)` are computed before the cross-tool filter). `substrate/tool_overlap`'s
  `signature_families` / `kind_families` / `vocabulary_families` return **only the filtered
  cross-tool groups**, so the unfiltered total is unreachable from the renderer.

  ⚑⚑ **AND THE FILTERED COUNT IS NOT A SUBSTITUTE — IT WOULD PRINT `N of N`.** Every section
  would report 100% cross-tool coverage: a denominator equal to its numerator, which is worse
  than no denominator because it reads as a measurement. This is the same class as
  `census-green-is-a-fact-about-the-census`, arriving through a convenience in the layer below.

  **The fix is three accessors on `tool_overlap`** (the population sizes, not new judgements) —
  an edit to a LANDED, GREEN, PARITY-CHECKED layer (18/18). Worth stating plainly: re-opening a
  parity-checked module after its probe was written is a decision, not a detail, and the probe
  must be re-run against the origin afterwards. The origin is still on disk, so that is still
  possible; it will not be after Ⓝ31h″.

  ⚑ **WHAT THE RENDERER DID ESTABLISH.** Three pycheck refusals, each from ASSUMING a callee's
  surface rather than reading it: `Tool.accepts` (it is `accepted`, and `Tool.undocumented`
  additionally subtracts `options` — the origin's inline `accepted - modes` counted an
  argparse-declared option as undocumented); `undocumented_collisions` returns a DICT, not a
  sequence of pairs; and `signature_families`/`kind_families` ALREADY filter to cross-tool, so
  the renderer's own second filter was redundant and its denominator wrong. **The gate caught
  all three before anything landed** — but each cost a full rewrite, because a refusal reverts
  the file.

  ⚑ **SAME REFLEX, THIRD TIME THIS SESSION:** `all_signatures` / `all_kinds` / `all_gloss_words`
  were written as calls before checking they exist. They do not. Read the callee's outline
  FIRST — `module_outline <path>` is one call and would have prevented all six.

* ⚑⚑⚑ **Ⓝ31m ⟡yield-dont-return — THE WHOLE SPLIT CARRIED THE ORIGIN'S EAGER SHAPE, AND PARITY
  IS STRUCTURALLY BLIND TO IT.** Operator, 2026-09-01, on being told `undocumented_collisions`
  "returns a dict, not a sequence of pairs": *"'sequence of pairs' is my preferred model, because
  if everything can be guaranteed to be sorted, then everything can be yielded instead of
  returned, which leads to smoother resource consumption and finer-grained...everything."*

  **MEASURED** (`pycodemod --reifies` over the five computation layers):

      25 of 25 reification(s) over 5 file(s)
        returns-call  15 · returns-comp  8 (dicts) · returns-accum  2

  **Not one function yields.** Eight dicts, two accumulators, fifteen eager tuples.

  ⚑⚑ **AND PARITY CONFIRMED THE PORT WAS FAITHFUL — INCLUDING TO THE THING WORTH CHANGING.**
  Both sides materialize identically, so a probe comparing outputs cannot see this class. Ⓝ31i
  recorded that parity catches what cases cannot; this is its dual, and it belongs beside it:
  **parity catches TRANSCRIPTION defects and is blind to INHERITED-DESIGN ones.** A faithful port
  of a shape that should have changed passes every check either instrument can run.

  ⚑⚑⚑ **THE CARRIER ALREADY EXISTS AND THE SPLIT BYPASSED IT.**
  `jea/metalanguage/sorted_stream.py` (⟡sorted-stream) is a one-pass relational algebra over
  ordered streams: `Sorted` (an iterator PLUS its declared order PLUS the provenance of that
  claim), `already` / `checked`, `merge` (n→1, key-preserving), `dedup` (DISTINCT as an ADJACENT
  collapse, O(1) state), `group` (GROUP BY as an ADJACENT run), `join` (sort-merge, no hash
  table), `where`, `limit`, `project`, and **`from_dict` as the migration ramp**.

  `tool_overlap.signature_families` builds a dict to group — and `group` IS group-by as an
  adjacent run. This is the reuse-search that should have fired before the layer was written,
  and CLAUDE.md's own trigger names the shape: the plan proposed new machinery, and the
  structure it would reinvent was already built one directory over.

  ⚑ **AND IT DISSOLVES Ⓝ31j′ RATHER THAN ANSWERING IT.** The missing denominators exist only
  because a dict forces the whole population resident, so `signature_families` filtered
  internally to avoid holding the unfiltered map. A sorted generator has no such pressure: yield
  every family, let the consumer filter and count as it goes. **Three accessors on a
  parity-checked layer become unnecessary — the block was an artifact of the eager shape.**

  ⚑ **SCOPE, STATED HONESTLY:** this is a rewrite of five landed layers (25 call sites), not an
  adjustment, and each one is currently green with cases. It is ALSO the arc's own thesis
  ("everything is ordered, constraints pushed upstream" — the sql-lift arc's stated purpose)
  arriving at the tooling. Whether it lands before or after Ⓝ31h″ is a scoping call: the origin
  is on disk only until the retirement, but parity cannot check this class anyway, so the
  retirement does NOT have to precede it.


* ⚑⚑⚑ **Ⓝ31m — THE PORT IS BLOCKED ON THE CARRIER ITSELF, AND THE BLOCK EXPLAINS THE CARRIER'S
  ONE CONSUMER.** `substrate/tool_overlap_stream.py` was written (the full port: `declared` as a
  sorted base, `collisions` / `undocumented_collisions` / the three family signals as generators
  over `ss.group`, every family yielded so the denominator survives) and **refused — with 411
  findings, all of them in `jea/metalanguage/sorted_stream.py`**, not in the new file:

      sorted_stream.py:98   Missing type arguments for generic type "Callable"
      sorted_stream.py:105  Expression type contains "Any"
      sorted_stream.py:108  Function is missing a type annotation  [def ex(row)]

  **MEASURED — `pycodemod --importers sorted_stream`: 1 import site in 1 of 1,121 files**
  (`query_defs.py:1561`, taking `SortKey, Sorted`).

  ⚑⚑ **SO THE CARRIER'S ADOPTION PROBLEM IS MECHANICAL, NOT CULTURAL.** The ⟡sorted-stream arc
  built a complete one-pass relational algebra — `group`, `join`, `dedup`, `merge`, `where`,
  `limit`, `project`, with `SortKey.covers` making the order a checkable contract — and **nothing
  under the type gate can import it**, because the import pulls it into the importer's own check
  and it is untyped. A file with 411 findings is a file every gated consumer must refuse. That is
  the whole explanation for one consumer in 1,121 files, and it was invisible until something
  tried to become the second.

  ⚑ **AND IT IS THE PER-FILE GATE READING THE SITUATION CORRECTLY AGAIN** (`usecase-the-per-file-
  gate-is-a-design-signal`): a shared carrier that cannot be shared is the gate saying the carrier
  is not yet a library. The fix is the same shape as everything else in this arc — the typed core
  (`SortKey`, `Sorted`, `already`/`checked`, the combinators) extracted clean into
  `substrate/sorted.py`, with `jea/metalanguage/sorted_stream.py` retained as its untyped CLI/demo
  shell until it retires.

  ⚑⚑ **WHICH MAKES Ⓝ31m TRANSITIVELY BLOCKED AND THE ORDER FORCED:** no layer can be ported onto
  a carrier no gated file may import. `substrate/sorted.py` is the precondition, not a parallel
  task — and it is ALSO the thing that would let `query_defs`' single use become the pattern the
  sql-lift arc says it should be ("everything is ordered, constraints pushed upstream").

  ⚑ **WHAT THE WRITTEN PORT ESTABLISHED, kept for the retry:** the family signals FAN OUT (one
  mode taking `<file> <name>` joins both kind families; one gloss joins a family per content
  word), so they are a PROJECTION to a new key plus a sort — NOT a grouping of the base stream.
  Reading a fan-out as a grouping puts each row in one family instead of all it belongs to.
  `group` requiring its key to be a PREFIX is what forces this to be explicit; a dict accepts any
  key and hides it.

* ⚑⚑ **Ⓝ31m″ ⟡typed-carrier — THE EXTRACTION IS DESIGNED AND DOWN TO ONE QUESTION: WHAT TYPE IS
  A FIELD?** `substrate/sorted.py` was written three times 2026-09-01; the third reached **5
  findings, all the same root cause**, from 411 in the original.

  What converged: PEP 695 generics throughout (`class Sorted[Row]`, `def group[Row](...)`, `def
  project[Row, Out](...)`) rather than `TypeVar`/`Generic` — ruff's UP046/UP047 name this
  directly. Semantics preserved exactly: `SortKey.covers` as the prefix test, `require` naming
  the PRODUCER in its refusal, `group`/`dedup`/`merge`/`join` refusing an unordered stream,
  single-pass `__iter__` raising rather than yielding empty.

  **The remaining five are one question.** `_default_get` resolves a field dynamically — mapping
  key, then attribute, then positional index — so its return type is whatever the caller's row
  holds. Typed as `object` (or a `type Cell = object` alias) every comparison downstream is
  `Any`, and mypy reports each one. That is not incidental: **it is exactly how the original
  accumulated 411 findings**, and therefore why nothing gated could import it.

  ⚑ **THE ANSWER IS A COMPARISON PROTOCOL, NOT `object`** — comparison is the ONLY operation this
  carrier performs on a field, so the type should say precisely that:

      class Cell(Protocol):
          def __lt__(self, other: object, /) -> bool: ...

  Structural, so `str` / `int` / `tuple` / `_Rev` satisfy it without declaring anything — which
  is required, because the rows belong to the CALLER and cannot inherit from ours. `_Rev` (the
  descending wrapper) then implements it rather than being special-cased.

  ⚑⚑ **AND A REFUSAL REVERTS THE WHOLE FILE, WHICH IS WHY THIS COST FOUR REWRITES.** The
  per-file gate has no partial credit, so a 380-line module failing on five lines is retyped in
  full each attempt. The lesson is not to write less carefully — it is that a NEW file should be
  landed in the smallest form that passes, and grown, rather than authored complete and then
  debugged through the gate. Every rewrite here re-derived 375 correct lines to change five.

* ⚑ **Ⓝ31n ⟡reifies-sweep — RUN, AND THE TOOL HAS NO SUMMARY FORM.** `--reifies substrate/`
  emits 32.6 KB of per-site rows with no aggregate; reading a population from it means counting
  the output, which is the shape the standing rule forbids. **`pycodemod --reifies --summary`
  (per-file counts by kind) is the missing mode** — filed rather than worked around. What the
  raw output does establish: the reification shape is pervasive across `substrate/`, far beyond
  the five layers of Ⓝ31m, so `substrate/sorted.py` serves the package rather than one arc.


* ⚑⚑⚑ **Ⓝ75b′ ⟡the-remaining-monoliths — FOUR REASONED REFUSALS, ONE EXTRACTION, AND A FINDING
  THAT REFRAMES THE ARC'S OWN NAME: `toolmodes.py` WAS ALREADY DRAINED AND THE DRAIN WAS NEVER
  WIRED.** **17 `substrate/tool_*.py` modules** exist carrying the arc tag ⟡toolmodes-layers —
  `tool_census`, `tool_find`, `tool_dispatch`, `tool_usage`, `tool_declaration`, `tool_population`,
  `tool_convention`, `tool_convention_audit`, `tool_decline`, `tool_decline_run`, `tool_overlap`,
  `tool_similarity`, `tool_gap`, `tool_report`, `tool_block`, `tool_cli`, `tool_find_render` —
  each with its own suite, all green. **`tool_cli.CENSUS_MODES` already names every mode the
  monolith publishes.** And `scratch/toolmodes.py` **consumes none of them** and ships.

  ⚑ **MY CHECK REFINES THE AGENT'S CLAIM AND THE SUBSTANCE SURVIVES.** It said *"every one of them
  imported by nothing but its own selftest."* Measured: `module_importers substrate.tool_census` →
  **13 sites in 13 files** — six sibling `tool_*` MODULES import it, not just suites. **But every
  importer is inside the cluster: it imports itself and nothing outside reaches it.** *So the
  17 modules are not dead code — they are a live subsystem with no consumer, which is a different
  and more wasteful shape than dead code.*

  ⚑⚑ **THE HIGHEST-VALUE MOVE WAS THEREFORE NOT A NEW CUT.** The agent extracted the ONE layer
  with no substrate counterpart — **`substrate/tool_glossary.py` + suite (23 cases)**, the
  documented-function corpus the `--find` function arm reads — and stopped. *"Every other concern
  already had a sibling."*

  ⚑⚑⚑ **AND ITS SUITE CAUGHT A DEFECT THAT WOULD HAVE PRODUCED A WELL-FORMED ANSWER ABOUT THE
  WRONG TREE.** The first cut passed RELATIVE root names to `corpus.py_files`; **`corpus.resolve_root`
  reads CWD FIRST — by design, so a peer's shell wins** — so every fixture arm silently walked the
  **LIVE corpus** and returned thousands of real entries. *That function's own docstring records
  nearly having a peer bank this repo's flag count as their own.* Fixed by absolute roots, pinned
  by an arm. **A fixture that silently becomes the live tree is the same class as Ⓝ66's generator
  read after the `finally`.**

* ⚑⚑ **`applied_grammar (1).py` IS DEAD, NOT FROZEN — AND I CONFIRMED IT TWO WAYS.**
  `git log` → **one commit ever** (*"scratch helper Python + Agda type cache"*).
  `module_importers applied_grammar` → **28 sites in 2 files, ALL resolving to the ROOT-LEVEL
  `applied_grammar.py`**, none to the parenthesised copy. Its definition set is **identical to the
  root's (122 defs, 29 constants), offset ~2 lines** — a stale near-copy nobody cleaned up.
  **Recommend deletion, not draining.** ⚑ The agent left it in place because deletion was not its
  call, which is right — *and this repo deletes on zeros, so a deletion recommendation carrying
  two independent positives is the honest shape.*

* ⚑⚑ **THE FOUR REFUSALS, EACH WITH A DIFFERENT AND CORRECT REASON — this is the deliverable:**

      toolmodes.py    its `--check` is a ZERO-TOLERANCE pre-commit gate. A drafted composer was
                      refused at 65+ findings. ⚑ "Building a second `--check` beside the live one
                      risks TWO ANSWERS TO ONE GATE QUESTION — the defect this arc is named for."
      agda_defs.py    67 literal sites in 18 files, FIVE of `decl` role — its consumers read its
                      SOURCE, so it cannot take a delegating shim. Needs its own arc.
      findings.py     already well-formed: ONE mode (`--sweep`) behind a refusal that redirects to
                      the different `.claude/agents/findings.py`. ⚑ "Not a mode monolith; a single
                      expensive analysis. Draining it buys nothing."
      claims.py       ⚑ NOT IMPORTABLE AS A PYTHON MODULE AT ALL — its parent path
                      `cotype-ebnf-strictness/` contains dashes, so the `0 importers` is
                      STRUCTURAL. One node in an 87-file self-contained paper directory, live,
                      128 named claim checks, single-responsibility ALREADY satisfied (one claim
                      per function). Moving it severs it from `warrants.bib`.

  ⚑ **AND `verify_applied_grammar.py` IS A TEST SUITE, NOT A MONOLITH** — 167 defs of which ~160
  are `test_*`, and it is the live consumer of the root `applied_grammar.py`. **Its destination is
  the suite conventions, a different arc.** *Five files on a "monoliths" list and four were
  something else: a wired-nowhere drain, a source-read authority, a single analysis, an
  unimportable paper node, and a test suite.*

  ⚑ **FLAGGED: `toolmodes --check` was ALREADY STALE ON ARRIVAL**, from other agents' concurrent
  work (`run_selftests`, `schema --sizes`, `pycheck_show`), not from anything this agent did. It
  needs a `--sync` before commit — **and the agent used `--selftest` (104/104) as its equality
  oracle instead, since `--check` could not serve as one.** *Choosing a different oracle when the
  obvious one is compromised, rather than trusting it.*
