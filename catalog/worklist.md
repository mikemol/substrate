# Worklist — ⟡helper-sweep / ban-decompose arc

⚑ **THIS FILE EXISTS SO THE COHERENCE AUDIT HAS TWO READABLE SIDES** (M4, §63).
Until it landed, the worklist lived ONLY in harness todo state and
`mdstruct --coherence` had one document it could read and one it could not — so
every coherence pass (§24, §25, §63) was half-blind by construction.

Its companion is [`plan.md`](plan.md), the arc’s finding-by-finding record. The
two are audited against each other by:

    python3 scratch/mdstruct.py --coherence catalog/plan.md catalog/worklist.md

which reports three populations and never one verdict:

- **ORPHAN** — an item here with no plan witness: its figures are unsourced.
- **UNWITNESSED** — a plan finding nobody scheduled (§24’s dominant direction).
- **DANGLING** — a `§N` cited here that `plan.md` does not have as a section.

⚑ **AN ITEM’S ORDER IS NOT AUDITED BY THAT COMMAND.** The audit finds missing
links and stale numbers; it cannot find a wrong *judgement* about leverage.

✅ **`C4` LANDED (§65)** — ordering over the BUILD CHAIN is now measured:

    python3 scratch/split_pipeline.py --leverage [--applied-open|--failed|<paths…>]

reports **COST** (files to work), **LEVERAGE** (modules transitively unblocked)
and their **ratio**. Seeds come from the tool that owns each item’s shape — never
a label→files table invented in the ranker (§6d).

⚑ **BUT IT RANKS BY MODULES UNBLOCKED, WHICH IS THE WRONG AXIS FOR TOOLING
ITEMS.** `C4` itself has a cone of ZERO and was the right thing to build.
Leverage over the tree is one axis; leverage over the WORKLIST is another, and
nothing measures the second — so the tooling-first ordering below remains a
JUDGEMENT, labelled as one rather than smuggled in beside a number.

⚑ **AND EVERY FIGURE HERE IS DATED BY THE COMMAND THAT PRODUCED IT.** A recorded
finding is a hypothesis at a later tree state (§24, §62) — re-measure before
consuming one as a dependency.

------------------------------------------------------------------------------------------------------------------------

## RETIRED labels — declared, so the audit can subtract them

⚑ **§64: the audit’s UNWITNESSED population was 17, and most were correct-but-noise** — labels the
plan still records because a section is a permanent record, but which are no longer items. A census
that reports them forever is one nobody reads (§63’s own lesson about its supersession scan), so the
lifecycle is DECLARED here rather than maintained as a growing exemption list inside the tool.

**RETIRED** (done or superseded; the plan section stands as record):
`A0` `A1` `C3` `R7` `R7a` `T2` `T2b` `T6` `R6` `G2` `A4-UNBLOCK` `A4-CLASSIFY` `C1` `R9-VERIFY`
`R9-GATE` `R9-TOOLING` `R11-TOOLING` `R12` `R13` `T13` `T14` `T15` `T2b-APPLY` `M4` `S2` `G4` `R1`
`R2` `R9` `R10` `C4` `R7b-APPLY` `S2`

**NOT AN ITEM** (incident tags, phase names, module names — never worklist labels):
`F1` `F2` `F17` `F18` `GLF1` `L0` `P1` `P3` `S5` `V4`

⚑ *`B1` is deliberately NOT in that list — it is a live item (re-baseline). I nearly wrote it in
because `Bijection` shares the prefix; a not-an-item entry for a real item would make the audit
silently stop reporting a genuine orphan, which is worse than the noise it removes.*

------------------------------------------------------------------------------------------------------------------------

## Legend

`⚡` = high leverage · `[deps]` = what must be true first · `⚑` = a measured
correction worth carrying.

------------------------------------------------------------------------------------------------------------------------

## DONE

- **TOOLING** — `R1` `R7a` `R7b` `R9-GATE` `R9-TOOLING` `R11-TOOLING` `R12`
  `--manifest` `blame()`
- **PAYDOWN** — `R2` (8 barrels) · `R9` (589 leaves, private 226→66) · §29
  Coxeter · `T6` · `R6`✗ · `G2`✗
- **§44–§55** — `T2b-APPLY` · `gate_status.py` · `pycodemod.py` · `R13` ·
  `mdstruct.py` · `diagnose()`/`tree_stamp()` · the census is a projection of the
  build · `T14` · `C1` · `A4-CLASSIFY` (cone inverts citation \~10×)
- **§56–§58d** — `IdemInequality` is `R7b`’s class; `recover_presplit.py`;
  `edit_snapshot --from-snapshot`; `body_prelude()` + the coupling fix →
  **`Op.agda` compiles clean**
- **§60 — `T13` + `T15`.** 10/10 callers forward `list_keys`; 4 dispatch blocks
  deleted via `render=`/`summary=`. ⚑ I nearly built a `forwards-declined`
  marker — machinery recording that a duplication is intentional.
- **§61 — `G4`.** Shape-node index green. ⚑ A diagnostic wrote it: a read-only
  *intention* is not a read-only *operation*.
- **§62 — `R2`-residue.** `F2/Linear` barrel retired, sumtype 71→70. New stage
  `split_pipeline --retire` + `refresh_derived()`.
- **§63 + `S2`** — the coherence audit is now a command; supersession predicate
  keyed on order-of-magnitude. Suite → 638/29.
- **census reader** — `--last` printed a fixed 3 verdicts while the census emits
  6, swallowing 1548 rows; it now declares its own staleness.
- **`M4`** — this file, and `plan.md` moved in-repo.

------------------------------------------------------------------------------------------------------------------------

## TOOLING — do first, each unblocks or sizes later work

- ⚡ **`C4`** — \[§59; no deps\] rank the worklist by MEASURED cone. `_blast_radius`
  and `.leaf-verify.tsv` both exist; nothing composes them into *“what would
  clearing this root free?”* ⚑ §63: the coherence audit cannot find a wrong
  ordering — this is the item that can.

- ⚡ **`CENSUS`** — \[needs: no concurrent Agda edits; feeds `C4` `A4` `R12b`\]
  re-run `make -C agda -j` then `--verify --leaves`. ⚑ The ledger’s own stamp now
  says the tree has moved; every `A4`/`R12b` figure is a hypothesis until this
  lands.
  ✅ **`C2` FALSE NEGATIVE DONE (§67) — AND ITS CAUSE WAS NOT THE FILED ONE.** §66
  recorded *“the `import … as` form misses its pattern”*; the regex matched fine.
  **`--diagnose` was reading a build log 23.5 hours stale.** `log_is_fresh` lifted
  out of `census_from_build` (§52 measured **1770 of 2810 logs stale**); a stale log
  now falls back to compiling. `Core.agda` classifies `file-not-found` with a
  runnable remedy. ⚑ `--trace` was built first, because the only way to ask *why did
  it decide that* was a `python3 -c` wrapper.

- ⚡ **`C2`-residue** — the false POSITIVE half (§56) is still open: `diagnose`
  infers “rewire” from *a leaf DIRECTORY exists*, and §56’s witness was a directory
  of leaves that had never compiled. ⚑ §62 handed it the predicate —
  `classify_occupied` + `CII.sweep`, already composed by `--retire`. ⚑ **`Core.agda`
  IS STILL LEFT UNREPAIRED** — it is now `A4-FNF`’s first row with an emitted
  remedy, not a witness to preserve.

- ⚡ **`S1`** — \[§60; small\] `scripts/worklist.py` rewrites the file it reads with
  no snapshot — the last genuinely-unarmed in-place editor, found only once §60’s
  predicate fix cleared the false positives burying it.

- ⚡ **`S3`** — \[§61; small\] `sppf_node_index.py` has no `main()`: its body runs at
  import, so importing it regenerates the artifact and `--check` cannot be asked
  without doing the work.

- ✅ **`T16` DONE (§70)** — the **mypy ratchet is wired**, at the §69 scope
  (`check_scratch_independence.ROOTS` + `scripts/`), **census 108**, keys
  `<code>::<relpath>`, 7 selftest cases, hook line `type gate (mypy)`.
  **Decision (user): *“Goes in now, joins the paydown queue.”*** The baseline is
  MINTED BY THE COMMIT PATH — nothing is hand-written — so it records when B3 runs.
  ⚑ **B3 IS NOW 13 RED, NOT 12**, deliberately: the 108 keys are debt that existed
  whether or not a gate named them. Paydown is `--list` → fix at the site; never a
  `# type: ignore`, never widening to `Any`.

  ⚑ **THE GATE WAS THE SMALL PART.** Four refusals during the wiring, each naming a
  question the tooling could not answer, all now built: `pycodemod --discriminates`
  (*does a selftest case discriminate, or would it pass against the bug it names?*),
  `set_ratchet`’s write round-trip (*did the baseline land intact?*),
  `gate_status.gates()` refusing invalid shell (*does the hook still parse?*), and
  `mdstruct --spans` (*where does section N end?*).

  ⚑ **`--discriminates` FOUND A REAL BLIND SPOT — and its own first run was a lie.**
  Loading the mutant from a tempdir broke every gate’s `__file__`-relative
  `sys.path`, so three mutators returned `ModuleNotFoundError` and the harness
  scored all three as DISCRIMINATES. Fixed, it reported `empty-census-passes: BLIND`:
  no case asserted the gate REFUSES on a grown census, so a gate short-circuited to
  always-pass stayed green — §9a at the CASE level. Case 4 closes it.

- ⚡ **`T17`** — \[NEW §70; TOOLING, no deps, small\] **BACK-FILL `--dry-run` ACROSS THE
  OTHER NINE RATCHET GATES.** `set_ratchet(dry_run=)` is built and `check_mypy_ratchet`
  forwards it; the other nine do not, so each still has read-only-by-default plus an
  env var and **no way to preview a write**. MEASURED: `--dry-run` is the repo’s
  write-tool convention (6 tools) and **0 of 16 gates carried it** before §70 — a gate
  is a write tool exactly when it mints or lowers a baseline, which is the least
  recoverable moment there is. One flag per gate, forwarded to the authority.

- ⚡ **`T20`** — \[NEW §70b; TOOLING, no deps; **BLOCKS a trustworthy `T19` re-run**\]
  **A SCOPE-AWARE CALL RESOLVER — `--discards` RESOLVES CALLS BY BARE NAME.**
  MEASURED: 360 of 362 census rows are `check`, because **five module-level
  `def check` exist** (`fix_notinscope:86`, `fix_ambiguous_import:109`,
  `prune_leaf_opens:51`, `untethered_disjunct_advisory:91`, …) so the name enters the
  population legitimately — and `_bare_calls` then matches every bare `check(...)` in
  the corpus, including the test-local helper \~30 files define.
  ⚑ **A BARE NAME IS NOT A DECIDABLE UNIT** — identical to §22, where `def_index`
  keyed `_-ℤ_` and `-ℤ_` both as `-ℤ` and would have renamed 18 operators
  correctly-per-the-plan and wrongly-per-the-language. The question is *does THIS call
  site resolve to THAT def* (module scope vs enclosing function scope vs import).
  ⚑ Until it lands, `--discards` OVER-REPORTS on any name that is both a module-level
  def somewhere and a local helper elsewhere; the census header stamps its predicate
  so a stale reading refuses rather than misleads.

- ✅ **`T19` DONE (§70b) — ZERO LIVE FINDINGS, and that is a real outcome.**
  `verdict_returners()` DERIVES the population (**340 defs**) instead of the five names
  I had listed from memory — none of which are in it (§69’s hand-drawn-population miss,
  on my own item text). Final census: 3 names with discarding sites, all benign —
  `check` (test-local assertion helper, and see `T20`), `_insert_decoded` (a DB INSERT;
  the effect is the write), `fix` (the caller re-reads and diffs the file).
  The one genuine inert guard this class has produced is §70a’s, which was mine.
  ⚑ **`.discards-census.tsv` + `--last`** persists the sweep (156s) so it is not re-run
  to be re-read, **stamped with a hash of the predicate** — a ledger read after the
  predicate changed describes the OLD predicate, and `--last` now REFUSES rather than
  presenting it as current. It fired within minutes of being written.
  ⚑ **`_bare_calls` memoised** — the per-name version was §55’s repeated-work defect
  (341 identical CST walks); the fix is one pass, not concurrency.

- ⚡ **`T19-RERUN`** — \[needs `T20`\] re-run the sweep once calls resolve by scope. The
  current census’s 2 non-`check` rows are both verified benign, so this is about making
  the instrument trustworthy, not about known debt.

- ⚡ **`T21`** — \[NEW §72; TOOLING, no deps\] **REFINE `[UnequalTerms]` INTO ITS TWO
  CAUSES.** `_classify` buckets it as undifferentiated `other:UnequalTerms`, but the
  operator names two distinct origins that want two distinct tools (2026-08-04):

  1. **a NAME COLLISION** — “multiple things have the same name, and the wrong things
     are being compared”. That is `rename_at_source`’s class, and `agda_defs.py <name>`
     already answers *how many homes does this name have* — so the refinement is
     computable, not a judgement.
  2. **an OPAQUE-SPLIT DIAMOND** — “proofs are split and made opaque in a way that
     causes a diamond to fail to close somewhere else”. That is a SEAL question
     (`opaque` staging bounds dense elaboration), and its remedy is unsealing or
     re-routing the proof, never a rename.

  ⚑ **THE TWO ARE INDISTINGUISHABLE FROM THE ERROR TEXT ALONE**, which is why the
  bucket is currently undifferentiated and why an operator re-derives the distinction
  by hand each time. The discriminator to build: for the terms Agda reports unequal,
  ask `def_index` whether either name is MULTIPLY-HOMED (cause 1), and whether either
  side is under an `opaque` block (cause 2).

  ⚑ **AND `A4-OTHER`’s ~80 ARE SIZED AGAINST THE UNREFINED BUCKET** — this is the same
  shape as `A4-FNF`’s “~40 mechanical” being unverified until `C2` tightened its
  predicate. Refine before sizing, or the population is a guess.

  *Measured §72*: three `[UnequalTerms]` in `DeriveOrFetch.agda` were NEITHER cause —
  all three were my own wrong signatures (`≈ℚ-refl` at wrong arity; `demorgan` assumed
  over ℚ when it is over ℕ constructor pairs; then `recip` on both sides of DeMorgan).
  So a THIRD partition exists — *the statement is simply wrong* — and a classifier that
  offered only the operator’s two causes would mis-route it.

- ⚡ **`T18`** — \[NEW §70; TOOLING, no deps\] **RUN `--discriminates` OVER EVERY GATE
  AND SELFTEST-BEARING TOOL.** It is built, it found a live blind spot on its first
  target, and it has been run against exactly ONE module. The four mutators are this
  arc’s own measured defect classes (sentinel-read-as-clean, line-keyed key,
  empty-census-passes, scope-hardcoded). ⚑ **A `BLIND` ROW IS NOT AUTOMATICALLY A
  DEFECT** — a mutator names one class and a suite may legitimately not cover it, so
  this produces a REVIEWABLE LIST, never an exit code. Feeds `T3`/`T4`.

  ⚑ **§69 DISSOLVED THE SCOPE QUESTION — `scratch/` IS A STAGING AREA** (user:
  *“they can be promoted out of `scratch/` if they’re brought to meet common
  quality status”*). §67 and §68 both proposed hand-drawn populations; the repo
  already draws the line by MOVING FILES OUT, and
  `check_scratch_independence.ROOTS` is the declared promoted set.

  | population                    | keys    | profile                                                        |
  |:------------------------------|:--------|:---------------------------------------------------------------|
  | `jea` + `el-atlas` (promoted) | **80**  | `arg-type` · `attr-defined` · `union-attr` · `used-before-def` |
  | `scripts/`                    | **28**  | mostly `var-annotated`/`assignment`                            |
  | **promoted + `scripts/`**     | **108** | **defect-shaped, 15 codes**                                    |
  | `scratch/` (staging)          | \~99    | annotation debt + the silos                                    |

  ⚑ **THE PROFILE INVERTS AT THE BOUNDARY** — the promoted corpus has **no
  `var-annotated`, no `assignment`** (it is already annotated; that is what
  promotion means) and carries the real defect classes instead. *A boundary that
  changes the KIND of finding is a boundary, not a filter.*

  ⚑ **AND IT REFRAMES §68’s CONCLUSION.** §68 called the gate PROSPECTIVE-only from
  a 12-key tool census — measured over the wrong population. Over the promoted
  corpus there ARE 80 keys including `used-before-def` and 6 `attr-defined`.

  **REVISED RECOMMENDATION:** scope to **`ROOTS` + `scripts/` = 108 keys**, and have
  the gate IMPORT that list rather than restate it (§6d). `scratch/` stays
  deliberately UNGATED — gating staging defeats the point of staging. Promotion
  then acquires a mechanical meaning: **a candidate must not add census keys.**
  **Both decisions remain the user’s** — 108 is larger than §68’s 41, so the
  worse-before-better cost on B3 is real.

- **`M5`** — \[§64; needs the RETIRED list above to settle\] teach `--coherence` to
  read the declared lifecycle so retired labels are subtracted BY CONSTRUCTION.
  ⚑ Today the section above is prose the tool cannot see: it reports every retired
  label as UNWITNESSED, and a census that cries wolf is one nobody reads. The list
  is the SPEC; the parse is the work.

- ⚡ **`T11`** — \[must precede `T4`\] Audit-V residue. ⚑ Re-measured §60: only
  **4 of 10** ratchet gates call `check_argv`.

- **`T3`** — \[must precede `T4`\] selftests for `capstone_to_dir`,
  `narrow_leaf_imports`. ⚑ §62 cleared `collapse_carrier_nesting`; §63 cleared
  `mdstruct`’s 0/0.

- **`R3`** — \[blocks `R4`/`T1`\] make `_conduit_set` a fixpoint. 1506 of 2964
  modules reach past 3 hops.

- **`T12`** — the 6d residue: 5 files still define their own `agda_files`.

- **`T2c`** — a `-- Defines:` regenerator for the 19 under-declaring leaves.

- **`T5`** — lift `telescope_text`; check overlap with the `agda_lex` primitives.

- **`R5`** — \[partly done §44\] `def_index` still indexes non-definitions.

------------------------------------------------------------------------------------------------------------------------

## DECOMPOSITION — the R7b/R11 chain

⚑ **§65 MEASURED THIS ORDER AND IT INVERTS §59’s.** The measured table:

| item                    | cost  | leverage | ratio     |
|:------------------------|:------|:---------|:----------|
| **`R7b-APPLY`**         | **2** | **559**  | **279.5** |
| `R11`                   | 54    | 712      | 13.2      |
| `A4` (all 121 failures) | 121   | 1663     | 13.7      |

§59 moved `R11` ahead on the argument that the applied-open class is *underneath*
`R7b`. That argument was about MECHANISM and it was right — but I let it decide
ORDER, which is a different question. `R7b-APPLY` is 21× `R11`’s ratio and its 559
is a third of everything clearing all 121 failures would free.

⚑ **AND THE COMPILER RETIRED A CAVEAT CARRIED THROUGH THREE SECTIONS.** `--why`
shows `V4-Coxeter`’s 501 is blocked by `Idem.agda:24` — **`R7b-APPLY`’s own
file**. The cone was never `V4-Coxeter`’s; `V4-Coxeter` is *in* it. Neither
`IdemInequality` nor `V4-Coxeter` is in the applied-open population, so the two
cones are independent, not nested.

✅ **`R7b-APPLY` DONE (§66) — AND IT RETIRED THE GENERATOR.** Both leaves compile
clean. The fix was **one sibling import**, not a telescope selection: `Op` defines
`_≉_`, `Idem` uses it, nothing imported it. ⚑ §58d predicted the right OUTCOME by
the wrong MECHANISM, and `R7b-REWRITE` was sized against that misdiagnosis.

⚑ **THE ACTUAL R9 DEFECT SURFACED BEHIND IT:** `_≉_` was `private` pre-split —
deliberately unexported because `Core/Operations.agda:44` defines it
byte-identically. R9 made it a public leaf and the ROOT re-exported it, so
`Core.agda` saw two (`[ClashingDefinition]`). Dropping `public` from that one
re-open cleared it; `Core.agda` moved `dependency` → `own`.

- **`R14`** — ⚑ **RE-CLASSIFIED (user, 2026-08-01): NOT a tooling build — a PAYDOWN
  under EXISTING policy.** I filed it as *“nothing checks that the root doesn’t
  re-export the leaf”*, i.e. a new gate over a new invariant. But a `private` helper
  colliding with a public sibling **is a name collision**, and the ban skill already
  states the rule: *“The only ban-compliant fix is renaming at source. Not re-adding
  `using`, not qualifying, not aliasing.”* `private` was MASKING the collision —
  exactly what the skill says a filter does.
  ⚑ **So the fix is `rename_at_source` on the two definitions**, after which there is
  no clash to re-export and the invariant I proposed gating cannot be violated.
  ⚑ *Why I mis-filed it:* the symptom arrived through the SPLITTER rather than through
  the typechecker, so I treated it as a splitting defect. The class is the same one
  §13 records — an ambiguity is not automatically a new mechanism.
  **Population: unknown** — needs one `--list` over the `private` census cross-checked
  against public names, then rename each pair. Overlaps `R8`.
- ⚡ **`R11`** — the applied-open pre-split restructurer, 54 files, one kind, 712
  blocked, ratio 13.2. ⚑ Still *underneath* `R7b` mechanically (§58c) — that
  shapes HOW, not WHEN.
- **`R7b-SWEEP`** — ⚑ **DOWNGRADED by §66**: it exists to size a generator whose
  one live instance turned out to be a one-line import fix. Run it to learn the
  population, but do not treat it as a precondition for anything.
- **`R7b-REWRITE`** — ⚑ **SIZED AGAINST A MISDIAGNOSIS (§66)**, so its premise is
  open. The keep-biased polarity finding stands on its own (`prune_imports`’
  stated rule); whether a GENERATOR is owed depends on `R7b-SWEEP`’s count.

------------------------------------------------------------------------------------------------------------------------

## BUILD FAILURES

- ⚡ **`A4-FNF`** — \[needs `C2` + `CENSUS`\] the `file-not-found` failures. ⚑ The
  “\~40 mechanical” is unverified. Work in cone order.
- ⚡ **`A4-OTHER`** — \[needs `A4-FNF`\] the \~80 heterogeneous failures. ⚑ Do not
  treat as one population.
- ⚡ **`T2b-RESIDUE`** — \[feeds `A4-OTHER`\] 295 sections: 81 `_+_` ambiguous + 214
  no-candidate whose class is not yet known.

------------------------------------------------------------------------------------------------------------------------

## PAYDOWN — measured populations, tools exist

- ⚡ **`R2-SWEEP`** — \[§62/§26; the `--retire` stage exists\] §26 measured **21
  sumtype rewrite-keys counting both `X.agda` and `X/Name.agda`**; §62 retired one
  (71→70). Each remaining is a `--retire` candidate. ⚑ `Wedge/Graded`’s leaves are
  hand-written (no provenance marker), so it needs hand-verified exports.
- ⚡ **`G1`** — \[blocks `B3`\] `check_claims` red — **1 new** (measured 2026-08-01).
- ⚡ **`G6`** — \[blocks `B3`\] cap ratchet red — **11 new**. ⚑ Baseline is a 0-byte
  file: a LEVEL, not a delta.
- **`G5`** — \[blocks `B3`\] Σ metalanguage regression: `jea_seam_provenance`. ⚑ A
  silo this arc never touched.
- ⚡ **`A3`** — un-rename the fully-safe statements. SAFE 126 / OCCUPIED 47 /
  COLLISION 31 / CAPTURE 1 — re-measure.
- ⚡ **`R8`** — \[blocks `B1`\] the leaf-side `public` residue. ⚑ Re-measured
  2026-08-01: **36 new**, not 23 — the figure aged.
- **`A2`** — the 31 COLLISION clauses. Check the provider for a pattern synonym
  first.
- **`G2`-residue** — retire the last 3 capstone `.agda` modules.
- ⚡ **`R12b`** — \[needs `A4-OTHER` + `CENSUS`\] re-emit the leaf-own failures.
  ⚑ Both prior figures void (113, 345) and the ledger is stale.
- ⚡ **`R10a`** — \[needs `R12b` + `R7b-REWRITE`; 46 defs\] hoist the parameterized
  inner modules, then `split_telescoped`.
- **`R10b`** — \[needs `R12b`; 15 defs\] `private` blocks inside plain inner
  modules — ordinary `split_lemmas`.

------------------------------------------------------------------------------------------------------------------------

## MARKDOWN

✅ **THE APPLY EXISTS (§70c)** — `mdstruct --fixpoint --apply`: `--apply`-gated,
snapshots via `edit_snapshot.guard`, and **REFUSES a non-fixpoint**. It was ONE
RETURN VALUE away, not a build — `fixpoint()` already ran to convergence and threw
the converged text away, which is why `--table-style` could report *“48 → 0”* while
nothing could write it. MEASURED: worklist converges in **1 round**, plan in **4**;
applied to the worklist, **MD060 48 → 0**.

⚑ **AND THE SURVEY FOUND NO REPO MARKDOWNLINT CONFIG** — no `.markdownlint*`, no
`.editorconfig`, no pandoc defaults. The MD060 warnings come from the IDE’s GLOBAL
markdownlint, and **`mdstruct.WRITER` is the repo’s only declaration of markdown
style**. Treat that constant as the authority; do not conform to a config that does
not exist.

- ✅ **`M6` + `M1` DONE (§70e)** — **`WRITER` is `--columns=120`** (user: *“standard
  classic widebar”*), **applied to both documents, both idempotent on re-run, MD060
  = 0 in each.** The class is retired by construction rather than by fixing rows.
  ⚑ **The first attempt reported 120 as a NON-fixpoint and I built a theory on it** —
  inferring that convergence is non-monotone in width, inventing a grid-vs-pipe-table
  mechanism, and deleting a binary search as inapplicable. **120 converges in 12
  rounds**; the sequence descends in PLATEAUS and `fixpoint()` bailed on the first
  non-strict step. *§50’s defect in its own successor:* “iterate while progress is
  STRICT” is a stronger claim than termination needs, so it became a capability bound
  wearing a termination bound’s clothes — the exact distinction `head_span` settled.
  Fixed: stop on `n == 0` or a GROWING delta, plateau budget 8 (measured worst: 3).
- ⚡ **`M2`** — \[BLOCKS `M1` for any generated file\] fix the GENERATORS, not their
  output. ⚑ §70c measured the population: `scripts/reuse_catalog.py` hand-builds
  pipe rows via f-strings (`:536,581,585,661,666,714,718`) and
  `el-atlas/tools/el-atlas-structured-gen.py:209,223` emits `|---|---|` with no
  padding — **the exact MD060 shape**. Normalizing a generated file is undone by the
  next regeneration, and I was one command from doing it.
- **`M1`** — \[needs `M6`; `M2` first for generated files\] normalize the tracked
  markdown to the fixpoint. ⚑ The tool is built and the documents converge; what is
  owed is the DECISION (`M6`) and the generator fix (`M2`), not machinery.
- **`M3`** — \[needs `M1` + `M2` + `M5`; and `B3` first\] a fixpoint gate over tracked
  markdown — and, per §63, a COHERENCE gate. ⚑ §70c: **no markdown gate exists in
  any hook today**, so this is the layer that makes the class unrepresentable rather
  than merely reported. Deliberately last.

------------------------------------------------------------------------------------------------------------------------

## THE COMMIT CHAIN

- ⚡ **`A4`** — \[needs `CENSUS` + `A4-FNF` + `A4-OTHER` + `R7b-APPLY` + `R12b` +
  `A2` + `A3` + `R8`\] the build census. ⚑ Its baseline (clean 1303 · failed 121 ·
  blocked 1286 · stale 141) is now self-declared stale by `--last`.
- ⚡ **`A5`** — \[needs `A4`\] the ban additions. ⚑ Re-measured 2026-08-01:
  **216 new, not 66** — the figure is a day stale and `A5` was sized against it.
- **`B1`** — \[needs `A5` + `R8`\] re-baseline — ONLY for predicate changes. ⚑ §60
  changed one: `check_snapshot_guard`’s in-place predicate (48 → 44 editors, 3
  false-positive shapes retired).
- **`B2`** — \[needs `A5`\] `make catalog` — settles §8’s Set₁ question. ⚑ Measured
  2026-08-01: `140 of 3130 cores UNDECODABLE — census incomplete`.
- ⚡ **`B3`** — \[needs `A5` `G1` `G5` `G6` `B1` `B2`\] the gated commit.
  ⚑ Re-measured 2026-08-01 after `T16`: **28 gates, 13 red** — `G4` cleared, and
  the mypy type-gate added ONE deliberately (user: *“goes in now, joins the
  paydown queue”*). The 13: carrier-locality · ban · claims · rederive ·
  discharge · snapshot · sumtype · public · private · Σ6 · Set₁ · cap · **mypy**.
  ⚑ **The commit is what MINTS `T16`’s 108-key baseline** — it is not hand-written
  (`.githooks/pre-commit:46` exports the write flag; setting it by hand is the
  `--no-verify` shape).

------------------------------------------------------------------------------------------------------------------------

## LATER / OPEN

- ⚡ **`T10`** — \[needs `R10a` + `R10b` + `R11`\] one-definition-per-file.
  347-of-656 predates every census since.
- ⚡ **`R4`** — \[needs `R3`; subsumes `T1`, `T7`, `R7a`\] centralize all name
  interpretation.
- **`T1`** — \[needs `R3`; is `R4`’s barrel case\] the conduit apply — do it inside
  `R4`.
- **`T7`** — \[needs `R4`; is `R4`’s `as` case\] qualified-name matcher + body
  rewriting.
- **`T4`** — \[needs `T3` + `T11`\] the 9g completeness gate.
- **`T8`** — \[open, method\] the `\b` motif censuses SHAPE not INTENT. Live: 7 tool
  files.
- **`T9`** — a static stale-clause reporter. Low value while the tree is red.
- **`G3`** — corrected by attribution, mostly not actionable.

------------------------------------------------------------------------------------------------------------------------

## USER DECISIONS

- ✅ **`U4` DONE (§70f) — AND THE ANSWER WAS NOT `CLAUDE.md`** (user: *“the place to
  put it is in tooling, which will surface such rules when they’re violated …
  CLAUDE.md is not tooling”*). I proposed writing the promotion policy into
  `CLAUDE.md` — a document a reader must CHOOSE to consult, which nothing checks.
  **That is the weakest enforcement layer there is**, and this arc measured its cost
  as §9a’s five baselined-and-unwired gates.
  ✅ **`check_scratch_independence.promotion_report()` + `--promotable <dir>`** states
  the rule as a PREDICATE: no live `scratch/` reference, and **it adds no census
  keys** — asked of `check_mypy_ratchet`, never restated. Live: `--promotable scratch/cotype-ebnf-strictness` → **BLOCK, 50 type-census key(s) would be ADDED**,
  with the first one named.
  ⚑ **AND IT WAS NOT IDEMPOTENT** (user: *“that should just be idempotent”*):
  `--promotable jea` returned BLOCK/exit 1, asserting that an ALREADY-PROMOTED
  project is not promotable. Same shape as §62’s `--retire` early-return — **a
  predicate that reports its own success as a failure cannot be used to CONVERGE on
  the state it describes.** Re-asking is now free and agrees with reality.
- **`U1`** — harness guard blocking tree-wide `git checkout/reset -- agda/`.
- **`U3`** — should the ban skill state that `private` is now banned? ⚑ **NARROWED
  (user, 2026-08-01): its second half is RETIRED, not owed.** I had queued *“the
  skill does not say a `private` helper may be private for CLASH AVOIDANCE”* — but
  that is a name collision, and the skill’s rename-at-source rule already covers it.
  Adding a `private`-specific clause would restate a general policy as a special
  case, which is the shape §60 retired when four gates hand-rolled what one
  parameter expressed. **What remains is only:** the skill documents the pipeline
  and the `public` ban but never mentions that `private` is banned too, though
  `check_private_ratchet` enforces it (baseline 226 → 66 paid).
- **`U2`** — standing instructions, now including §60 *“the difference between N
  call sites and their authority is one VALUE, not the dispatch”*, §61 *“a
  read-only intention is not a read-only operation”*, §62 *“‘blocked because X’
  recalled from a plan is a hypothesis — ask the tool that owns the shape, and
  make its refusal name the route”*, and §63 *“a census too wide to read has
  already failed; when two cases are in genuine tension the discriminator is
  usually a different DIMENSION, not a better rule”*.
