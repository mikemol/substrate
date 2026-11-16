# Audit — `other:NotInScope`: six causes, not one missing tool

Dispatched 2026-08-03 after `worklist_gate.py --solvers` measured **1 of 13 build-failure classes
mechanised** (`file-not-found`, 42 modules) and **12 classes / 73 modules with no tool** — the largest
being `other:NotInScope` at 44.

⚑ **THE BRIEF WAS CORRECTED BEFORE IT WAS WRITTEN** (user): *"We have tools for working with that
problem, but it usually involves regenerating something else after a tooling fix is in place."* I was
about to ask *"what tool is missing"*, which presumes absence. The real shape is **fix upstream, then
regenerate** — so `--solvers` is not reporting a missing tool, it is reporting that its remedy field
holds ONE command and a two-phase repair does not fit in one command. An instrument limit, not a
substrate gap.

## 1. The cause-partition of the 44

Derived from `split_pipeline.py --diagnose --blockers` over the full 115 population plus per-module
`agda/_build/2.8.0/**/*.agdai.log`.

| # | cause | count | witness |
|---|---|---|---|
| **C1** | **stale `using`** — definer no longer exports the requested names; log carries `-W[no]ModuleDoesntExport` ABOVE the error, so the name binds to an empty provision | 7 measured (S5 cluster) + more inferred | `S5Carrier.agdai.log:10-21` (`Substrate.S5.S5Verdict doesn't export _≡_ refl sym trans cong`) → error `:23-27`. Same root across `S5TwoFuel`, `S5Fixpoint`, `S5Real`, `S5Matrix`, `S5Regress`, `S5TorsorBridge`: one retired `S5Verdict` conduit |
| **C2** | **stale `renaming`** — the alias is LIVE, but the source name moved to a sibling leaf | 1 measured, ≥2 inferred | `Algebra/Q/Order.agdai.log:7-20`: `Nat.Times doesn't export z≤n, s≤s` under `renaming (z≤n to ℕ-z≤n; …)`; the names now live in `Foundation.Nat.Le` (`Le.agda:18-20`) |
| **C3** | **orphaned collision alias** — a leaf body carries `Name⟦hash⟧` with NO surviving binder anywhere | 6 measured (FUSep) | `FUSepQConfluence/PIdx.agda:19` uses `Tm⟦27e68fcc⟧`; imports `:13-16` bind nothing of the sort; no definer in tree |
| **C4** | **leaf emitted without a sibling import** | ~8 measured | `Instances/FreeMonoidContentful.agda:27` uses `,`; imports `:13-22` omit `Foundation.Product`. Same in `ConeLimitContentful`, `FreeModuleContentful`, `FreeLinearizationContentful`, `AdjunctionContentful` |
| **C5** | **telescope name used above its import** (§29/§31 positional class) | ≥1 measured, blocks **391** | `Groups/Symmetric/Permutation.agda:9` header `(A : Set)`, `_≡_` at `:16-17`, ZERO imports in the file |
| **C6** | **renamed at definer, consumer never updated** | ≥2 measured, blocks **400** | `Foundation/Fin/From2.agda:17` uses `_<ℕ_`; no definer resolves. `Le.agda:4` declares `_≤_` |

⚑ **~25 of 44 firmly attributed.** The remaining ~19 are single-module tails not individually opened.
C1–C6 is the partition; per-module assignment is complete only for the 25 witnessed. **Do not quote 44
as classified.**

## 2. Tool per cause, and its regeneration dependency

| cause | tool | regeneration dependency (verified) |
|---|---|---|
| C1 | `scratch/fix_stale_using.py` | **Reads build logs** (`:16-19`), so: `make -C agda -j` THEN the tool. Its own `stage_warning` declares it *"stage 11, after the build"* |
| C2 | **none** | Excluded by name from every candidate — `drop_dead_renames.py:10-17`: `prune_imports` treats renaming imports as untouchable; `fix_stale_using` repairs `using` lists; `rewire_to_leaves` does not parse `renaming`. Confirmed live: the tool printed `⚠ no using-list at …Q/Order.agda:20` and skipped |
| C3 | **none** | `drop_dead_renames.py:26-28` names the prerequisite (`agda_lex.binds_at` + a token-conservation ledger) as unbuilt. Worse than a live alias: the binder is GONE, so re-binding needs the pre-split parent (`recover_presplit` is a candidate source) |
| C4 | `scratch/fix_notinscope.py` | keys off `agda_defs.def_index()` which re-scans source per call — no cached artifact. **But it has regressed; see §4** |
| C5 | `scratch/hoist_telescope_imports.py` | self-declared run-on-demand, NOT pipeline-chained (`:33-36`); then rebuild |
| C6 | `scratch/rename_at_source.py` | fix at the definer, `def_index` re-read is automatic, then rebuild. ⚠ `spellings` has **2 rival definitions** (`rename_at_source.py:39`, `split_telescoped.py:61`) — corroborate before relying |

**Where the chain stops.** `split_pipeline` imports `split_lemmas`, `check_indented_imports`,
`fix_stale_using`, `rename_at_source` (`:35-38`). **`fix_notinscope` and `hoist_telescope_imports` have
ZERO call sites anywhere.** The chain ends at the build; nothing consumes the build's own NotInScope
output.

⚑ **A live infra break blocking C1:** `fix_stale_using.py:271` **crashes** (`FileNotFoundError`) on
`…/Cocycles/V4Signature/Codeword/LiveS4.agda` — the source was consumed into a leaf dir but its stale
`.agdai.log` survives, so the tool cannot complete a census pass. Stale derived artifacts outliving
their sources: memory `feedback_delete_module_rebuild_importer_cores`.

## 3. Why `--solvers` reports `none` — the instrument's limit

`worklist_gate.py solvers()` derives the tool by regexing `_classify`'s **third return element**.
`split_pipeline._classify()` returns a remedy from **exactly one branch** — the consumed-parent case;
the `other:*` path returns `kind, detail, None`. So `none` is not a judgement about repairability, it
is the absence of a third-slot value.

**Teaching `_classify` more remedies is insufficient**, because:

- C1's remedy is `make -C agda -j` **then** `fix_stale_using agda/_build` — order-dependent, and phase 1
  is a whole-tree action, not a per-module one.
- The classifier's input is a STALE log; C1/C2 need a fresh one. **A remedy computed from a stale
  artifact that instructs you to regenerate that artifact is self-referential** — it must be re-derived
  between phases.

**What would express it.** `parts` rows are `(label, n, route)` with one route string — that is the
ceiling. A two-phase remedy needs an ordered list of `(phase, command, invalidates)`, where
`invalidates` names the derived artifact the phase makes stale (`.agdai.log`, `Flat.mk`,
`.leaf-verify.tsv`) so the consumer knows classification must be re-run. The vocabulary already exists:
`agda_imports.stage_warning(tool, why, pipeline_stage)` carries *(why, position-in-sequence)* — but
returns a **banner string for humans**, not a structure a gate can route on. `solvers()` would then
report **SEQUENCED (2 phases)** — a third verdict beside SOLVED / MIXED / none.

## 4. Genuinely missing vs. merely unsequenced

**No tool exists:**

1. **C2** stale `renaming` with a live alias — needs to re-point the renaming's SOURCE module to the leaf
   that now defines it, keeping the alias. ~3+ modules.
2. **C3** orphaned `⟦hash⟧` alias — 6 modules; prerequisite named as unbuilt.
3. **Two-phase remedy expression** — §3. No structure carries it.

**Covered by a tool nobody has sequenced — which is NOT covered:**

4. **C1** — `fix_stale_using` exists and is stage-aware, but is blocked today by the `:271` crash.
5. **C5** — `hoist_telescope_imports` exists, **zero call sites**, blocks 391 modules via one file.
6. **C4** — ⚑ **THE USER'S PATTERN, MEASURED.** `fix_notinscope`'s `FALLBACK` map (`:110-113`) fires only
   when `def_index` returns EMPTY (`:115`, `if not defs and name in FALLBACK`). `def_index` has since
   improved to find record constructors — **`resolve_notinscope ","` now returns 9 homes** — so the
   fallback is unreachable and `:121`'s `len(defs) != 1` refuses all 5 `Contentful` modules.
   **A tooling improvement silently disabled a downstream compensation, and nothing re-validated the
   consumer.** Verified independently at `fix_notinscope.py:114-116`.

## Instrument defects found while measuring

- **`items._census_witness` truncates `parts` at 12** — so `--dispatch other:NotInScope` shows 12 of 44,
  alphabetically (A–C only). Mine, introduced the same session.
- **`split_pipeline --diagnose <mod>` truncates the error at `_classify`'s 160-char `detail`**, cutting
  BEFORE the not-in-scope name — the single most useful field. Only the raw `.agdai.log` has it.
- **`resolve_notinscope.py` silently corrupts multi-argument input** — given 8 log paths it treated each
  as a NAME and emitted 8 identical wrong answers. Its log-detection works single-arg only. Two
  measurements disagreed; the agent trusted the single-arg run (hand-verified against the raw log) and
  discarded the other.

## Reading — what is confirmed vs. carried

**Independently re-verified by me before recording:** the `,` → 9 homes measurement, and
`fix_notinscope.py:114-116`'s `if not defs and name in FALLBACK` gate. Those two are the load-bearing
claim and they hold.

**Carried as the agent's measurement, not re-run:** the S5-cluster attribution, the FUSep `⟦hash⟧`
count, the `fix_stale_using:271` crash, the zero-call-site findings, and the per-cause counts. Each
carries a file:line; none was reproduced here.

**A recorded finding is a hypothesis at a later tree state.** Every count above describes the tree of
2026-08-03 with 115 build-failed modules. Re-measure with `worklist_gate.py --solvers` and
`split_pipeline.py --diagnose --blockers` before treating any figure as current.
