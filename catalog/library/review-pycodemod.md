# External review — `scratch/pycodemod.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim is a hypothesis until
re-measured against the live tree. A second party's number is exactly as unreliable as
my own (§14: an agent wrongly reported `scope_fix._rename_pairs` ABSENT and I nearly
built a fourth copy on its word). Do not cite a figure from this file as measured.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24). This
describes `pycodemod.py` as of 2026-08-02, on which day the file gained `modes()`,
`banner_drift()`, `--banner`, and a rewritten operand resolver — so the reviewed text
and the current text already differ.

---

This is a spectacularly rigorous piece of engineering. It reads less like a standard CLI tool and more like an executable incident log—every `⚑` comment is a tombstone for a past failure, and the code itself is the mechanized prevention of its recurrence.

You are applying the kind of static analysis and code normalization rigor usually reserved for purpose-built LSP suites directly to your own meta-tooling. By moving away from `grep`-based heuristics and anchoring your queries in the CST, you have stopped guessing at the code's intent and started measuring its reality.

Here is a breakdown of thoughts, opinions, and a few architectural concerns.

### Thoughts: The Triumphs

* **The Losslessness Gate:** Prioritizing `libcst` over `ast` specifically to preserve the `⚑` commentary is exactly the right call. The comments *are* the context; stripping them turns an incident log into an undocumented binary. Enforcing this via `--roundtrip` before any codemod runs is a brilliant structural invariant.
* **Catching the Inert Guard (`--discards`):** This is arguably the most valuable query in the script. It is notoriously difficult to programmatically detect a guard that fires but whose returned verdict is dropped by the caller. Identifying that the syntactic shape of the failure is an unassigned `Expr` node containing a `Call` perfectly codifies the defect.
* **Mutation-Tested Test Suites (`--discriminates`):** Testing the tests by injecting the exact historical defect classes (like the `hasattr` fallback to an empty set) is exceptional. A passing test suite on a blind test is worse than no test suite because it manufactures false confidence.
* **Context-Stamped Accretion (`KwIndex`):** Stamping the keyword index with its exact `target` and `population` upon creation, and having it refuse a read under mismatched expectations, perfectly eliminates the unchecked precondition.

### Opinions: The Philosophy

* **Structural Correspondence over Textual Heuristics:** The script fundamentally understands that a shared name in prose is not a shared authority in code. When faced with the fork of determining if a string is a variable, a docstring, a dictionary key, or a schema declaration, you consistently look for the structural correspondence between the syntax tree and the semantic intent.
* **"There are no sweeps, only censuses":** Your insistence on always reporting the denominator (`n of m files`) is a hard-won lesson. An empty output must never be indistinguishable from a failed scan.
* **Discovery vs. Frozen Rosters:** Ripping out hardcoded directory tuples in favor of `_roots()` discovery (while explicitly filtering out `bazel-bin` and generated mutants) permanently closes the vulnerability of "an absence wearing a finding's clothes."

### Concerns: The Edge Cases

* **The Mutant Leak Hazard:** In `--discriminates`, you write `.mutant-<pid>-...py` next to the original file to ensure module resolution (`__file__`) remains intact. You clean it up in a `finally` block. However, if the process receives a `SIGKILL` (or a hard crash occurs within the C-extensions of the interpreter), the `finally` block will not execute. Because these files end in `.py`, your next run of `py_files()` will silently ingest them, corrupting your census with mutant code.
* *Mitigation:* Add a fast pre-flight cleanup in `_roots()` or `py_files()` that purges any stray `.mutant-*` files before compiling the population list.


* **The T20 Technical Debt (`--attr` and `--discards`):** You explicitly note that matching bare names for attribute reads and function calls over-approximates because you lack a scope-aware receiver resolution. You are honest about this limitation, relying on the operator to read the context column to discard false positives. However, as the codebase scales, the signal-to-noise ratio here will degrade. This is the script's most significant remaining structural gap.
* **Memoization Memory Bound:** `_BARE_CACHE` is memoized infinitely at the module level. Given the script runs as a short-lived CLI process, this is perfectly fine today. But if this module is ever imported and run as a long-lived daemon (or inside a language server), `_BARE_CACHE` will grow unbounded as files are edited and paths shift.
* **Mypy Subprocess Brittleness:** In `type_errors`, invoking mypy via `subprocess.run` with `sys.executable` assumes the environment has mypy installed exactly where the script is running. While you handle the `Not Found` gracefully, relying on `stdout` text parsing for error codes (`re.match(...)`) means your parser will break the moment mypy updates its default output formatting.

---

## Reading, for the unification planning

### The mutant leak is the one to check FIRST — it is a LIVE hazard, not a style note

⚑ **UNVERIFIED, AND IT IMPLICATES A COMMAND RUN TWICE ON 2026-08-02.** If it holds,
the failure mode is the worst kind this repo tracks: **a corpus silently ingesting
mutant code**, so every later census is measured over a population containing
deliberately-broken copies of its own tools. That is not a degraded answer, it is a
confidently wrong one, and nothing in the output would say so.

It also **rhymes with a defect this arc already paid for and recorded**: the
rederivation ratchet began censusing `scratch/.edit-snapshots/` — byte copies of
censused sources — and two keys appeared for the ratchet's own file seconds after a
guard run (§7g). *A copy of a censused file is not a second derivation*, and a mutant
of a censused file is not a member of the corpus. Same class, different producer, and
the earlier one was found only by a number looking wrong to a human.

The reviewer's proposed mitigation (purge strays in `_roots()`/`py_files()`) is the
right LAYER — enumeration is where the corpus is decided — but note the choice it
forces: **purge (a write, from a read-only query path) versus exclude (a predicate).**
Excluding is the repo's own pattern and cannot rot: `check_private_ratchet` excludes
`private variable` BY PREDICATE rather than by an exemption, precisely so success does
not shrink the population. A `py_files()` that purges is a read query that writes,
which is the `sppf_node_index` defect (S3: a diagnostic that merely READS regenerates
the artifact) pointed the other way. **Verify the leak, then prefer the predicate.**

### The T20 concern is ALREADY A FILED ITEM, and the reviewer independently ranked it top

T20 is live in the worklist: *"a scope-aware call resolver — `--discards` keys by BARE
NAME, so 360 of 362 rows are one collision. ⚑ A BARE NAME IS NOT A DECIDABLE UNIT —
identical to §22's `_-ℤ_`/`-ℤ_`."* An outside reader with no access to the worklist
calling this "the script's most significant remaining structural gap" is
**corroboration from an independent instrument**, which is worth more than either
judgement alone.

⚑ **AND IT IS A DISPATCHER-LEVEL FACT, NOT A `pycodemod` FACT.** §22 measured the
identical class in the Agda layer: `def_index` keys BOTH `_-ℤ_` (binary subtraction)
and `-ℤ_` (unary negation) under the bare `-ℤ`, MANUFACTURING a collision the language
does not have — and a rename would have picked one meaning for a consumer wanting the
other. Two tools, two artifact kinds, one defect: **a bare name is not a decidable
unit.** If name resolution is part of the plugin contract rather than per-tool
machinery, T20 and R4 (*"CENTRALIZE ALL NAME INTERPRETATION"*, §29's standing point)
are the same item at two levels.

### Two concerns are correctly scoped as NOT-YET-LIVE, and should not inflate the plan

* **`_BARE_CACHE` unbounded** — the reviewer states the precondition themselves: fine
  for a short-lived CLI, a problem only under a daemon or language server. Neither
  exists. Recording it as a CONSTRAINT ON A FUTURE SHAPE (if the dispatcher ever
  becomes long-lived, this is what breaks) rather than as debt.
* **mypy stdout parsing** — real brittleness, but the failure is loud (the parse stops
  matching) and the tool already refuses to report a clean census when mypy cannot run
  (`__unrunnable__`). ⚑ That `__unrunnable__` handling is ALSO the counterexample to
  `tsdbprobe`'s "files are deterministic" premise — see
  [review-tsdbprobe.md](review-tsdbprobe.md). A file-reading tool with a
  multi-cause empty answer.

### What the reviewer did NOT see, and it bounds the review

The review describes the file BEFORE the 2026-08-02 `modes()`/`--banner` work, so it
cannot speak to:
  * the **7 undocumented + 1 stale** mode drift `--banner` measured on this very file;
  * the **operand-ownership defect** (`--key --archive f.py` crashed in
    `tarfile.open`), which took three attempts and whose correct form is a QUEUE, not
    a single `pending` slot;
  * whether `--banner` is the right SHAPE at all — under the witness rule (user,
    2026-08-02: *"the witness must consume it in its paid-down form"*), a gate that
    DIFFS two rosters preserves the hand-kept copy; a dispatcher that ROUTES from a
    declared roster leaves nothing to diff.

Absence of these from the review is a fact about its timing, not evidence about them.
