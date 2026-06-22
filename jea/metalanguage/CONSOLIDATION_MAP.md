# Consolidation map (Π4) — the codebase's shared-shell + carrier-hole pairs

A **regenerable snapshot** produced by the `jea_pysim --shape` instrument (Π1), now trusted (Π5
controlled-perturbation validation) and proven (Π2 used it to fold the circuit-solve). Each entry is
a pair of units that share a structural *shell* with the difference isolated as *typed holes* at
specific depths — i.e. a candidate for one carrier-/parameter-parametric definition. Triaged: not
every high-similarity pair should be folded (intentional parallels, by-design families, versioned
rewrites). **This goes stale as code changes — regenerate, don't trust the line numbers.**

## Sweep status (2026-06-21, Π6–Π8)

Full regen across all three scans. **jea/ core:** two NEW byte-identical clusters folded — `check` ×4 → `jea_check.Checks` (Π6 ✅) and the canon→partition helper ×3 → `jea_zsppf.partition` (Π7 ✅); see §①. **el-atlas/tools + cross (Π8):** re-run found NO new actionable fold — every RFS ≥3 cluster triages to an existing category: `conj` ×4 is the trivial CD-conjugation 1-liner inside the **exploratory zero-divisor pilots** (the pedagogical curriculum — each `*-pilot.py` self-contains its own Cayley-Dickson arithmetic by design, same family as the left `vadd`/`vsub`); `work` ×3 is the inline `np.dot` measurement-spinner (the "a probe should show its load" intentional-workload judgment, §⑤-adjacent); the `el-atlas-depsort-v3` self-clusters (`t_*`, `trees`, `bridge`, `io_pass`) are §③ within-file/versioned; the cross scan surfaces only `jea_onegraph.{operating_point_qgraph,operating_point_shunt}` (the §② coordinate pair, 2×, below RFS 3). The jea⨯el-atlas self-hosting parallel stays at 0.62–0.67 (below the cluster threshold) — the intentional validation oracle, kept.

## Regenerate

```bash
# jea/ core (fast, ~1s)
python3 jea/metalanguage/jea_pysim.py --shape --min-size 10 jea/*.py
# el-atlas/tools internal (~3s)
python3 jea/metalanguage/jea_pysim.py --shape --min-size 12 el-atlas/tools/*.py
# cross: jea self-hosting el-atlas
python3 jea/metalanguage/jea_pysim.py --shape --min-size 10 jea/jea_onegraph.py \
        el-atlas/tools/{live_dispatcher,perf_graph_integrated,kron_reduction}.py
```

## ① CONSOLIDATE — real duplication to fold

| frac | pair | the fold |
|---|---|---|
| 1.00 (×4) | `jea_strictify_{gcalc,kirchhoff,rotation}.check` ↔ `jea_parity_species_probe.check` (+ the `results`/TALLY harness) | **FOLDED (Π6 ✅).** The byte-identical self-test harness (`check` + `results` + the TALLY/FAILURES summary), copied across 4 scripts, now lives once in `jea_check.Checks`; each script keeps `check`/`results` as bindings to a local `Checks()` instance (call sites unchanged) and calls `_checks.tally("<label>")` (rotation's all-pass message preserved via the returned bool, parity's `main` via `sys.exit`). RFS ≥3 (4 instances, free duplication — no generating symmetry) + the new shared **test-fixtures home** = the exact trigger the `build_Eq` row (below) had been waiting on. All 4 re-run identically: 25/25, 9/9, 11/11, 4/4. |
| 1.00 (×3) | `jea_mega._part` ↔ `jea_mega_eval.part` ↔ `jea_zsppf.partition` | **FOLDED (Π7 ✅).** The canon→index-partition helper (group positions by canon value → set of frozensets), byte-identical in 3 modules. The canonical home already existed AND both consumers already import it: `jea_mega` and `jea_mega_eval` both `import jea_zsppf as Z`, and `jea_zsppf.partition` is the def — so (like `_lh→jea_core.lh`, Φ3) just `_part = Z.partition` / `part = Z.partition`, **zero new dependency edges**, call sites unchanged. `jea_mega_eval`'s copy was a *nested* local def, now a 1-line alias. Re-run identically (jea_mega_eval W4 partition-dedup PASS; jea_mega imports clean). |
| 0.96 / 0.94 | `jea_agda_bridge.{read_vouched,typecheck}` ↔ `jea_agda_dag.{read_vouched,typecheck}` | **FOLDED (Φ2 ✅).** The agda-subprocess + literal-read body now lives once in `jea_agda_voucher.{typecheck,read_vouched}(name)`; each bridge keeps a 2-line wrapper binding its default filename (Emit.agda / EmitDAG.agda), so every no-arg caller (`jea_agda_apex`, `jea_agda_dispatch`) is preserved. The filename was the only carrier-hole. |
| 0.95 | el-atlas `kirchhoff_nedge` nodal `solve` / `G_AND`/`G_OR` | **perspective-mapped (Φ1′ ✅ — see §⑤).** `jea_circuit` carries TWO coordinates of one governing law: `nodal_solve` (subtractive Gaussian) and `nodal_solve_subfree` (subtraction-free Matrix-Tree ratio). The carrier's subtraction-capability selects the COORDINATE, not which graphs are solvable — the sub-free wedge solves the irreducible Wheatstone too. `kirchhoff.solve` = the float instance of the subtractive coordinate. |
| 0.94 | `jea_generator_strat._lh` ↔ `jea_generator_unified._lh` | **FOLDED (Φ3 ✅).** Promoted byte-identical limb-split → `jea_core.lh` (both generators already import jea_core, which already carries cupy + the device ld/st counterpart); each keeps `_lh = jea_core.lh`. The 3 evolution/ copies are the FROZEN curriculum — left untouched. |
| 0.92 | `jea_carrier_solve.build_Eq` ↔ `jea_zsppf.build_Eq` | **LEFT (Φ3 — judged not net-positive).** Both are `__main__`-local test fixtures (carrier_solve tests memoization tiers, needs `truth`/`N`; zsppf tests radix-intern) building the same balanced-add-tree, but with NO shared home (carrier_solve→jea_sppf, zsppf standalone) and divergent returns — folding = a new dependency edge for test data. The **jea test-fixtures home now EXISTS** (`jea_check`, Π6), so the shared-home blocker is lifted; only RFS<3 (2 instances) remains — fold when a 3rd `build_Eq` appears (and consider hosting it / its fixture in `jea_check`). |
| 0.93 | `chassis_cap_test.cpu_worker` ↔ `power_probe_root.cpu` | **LEFT (Φ3).** A real 3-line matmul power-spinner dup, but inline measurement-workload is intentional for reproducibility (a probe should show its load); el-atlas-internal, not jea. NB `het_validate.cpu_work` was a FALSE grouping (different body — a horner_cpu call). |
| 0.91 | `radzdg-witness-pilot.{vadd,vsub}` ↔ `second-order-zd-pilot.{vadd,vsub}` | **LEFT (Φ3).** Trivial 1-liners (`tuple(p+q for …)`) in EXPLORATORY Cayley-Dickson zero-divisor pilots; fold cost (an import edge) > benefit. Already slightly divergent (vsub vs vneg). |

## ② INTENTIONAL PARALLEL — do NOT fold (validated / by-design)

| frac | pair | why it stays |
|---|---|---|
| 0.62–0.67 | `jea_onegraph.{operating_point_shunt,compute_bw_shunt}` ↔ el-atlas `live_dispatcher.{decide,binding_edge}` | jea **self-hosts** el-atlas's perf-graph in graded-ℚ and **validates against it** (W4/W5: `series_schur==g_eff`, `compute_bw_qgraph==compute_bw`). The parallel IS the demonstration + the oracle check — keep both. |
| 0.83–0.86 | `jea_circuit` internal (`series_schur`/`fstar`, `FractionCarrier`/`FloatCarrier`) | the carrier-parametric family from Π2 — by-design, not duplication. |

## ③ VERSIONED / WITHIN-FILE — supersession or local cleanup

| frac | pair | note |
|---|---|---|
| 0.92 | `el-atlas-depsort.py` ↔ `el-atlas-depsort-v3.py` (`t_PUR`/`t_PRO`, …) | a versioned rewrite — v3 supersedes v1; candidate to **retire v1**, not merge. |
| 0.91–0.95 | within `el-atlas-depsort-v3` (`inside`/`insideP`, `_rdw_ok`/`_nf_empty`, `t_RDW`/`t_ZDW`) | parallel helpers; local parameterization if touched. |

## ④ Tool supersession (Π3 ✅ CLOSED) — `jea_pysim`+`jea_agdai` subsumed `scripts/agda_similarity` (RETIRED)

`jea_pysim` (structural) subsumes `agda_similarity` (textual) in **method, surfaces, and precision** —
and corrects a bug the original still carries:

| `agda_similarity` (textual) | `jea_pysim` (structural) | relation |
|---|---|---|
| 4 cosine scales (char3/token/line/block), comment-stripped | depth-grades over the interned SPPF + the `S(g)` SHAPE | structural; the shape is a curve, not a per-scale scalar |
| `anonymize_text` (hand-written regex per orbit, e.g. `Z[2-9]→<Zn>`) | **exact** α-equivalence (role-lowering, automatic) | exact + automatic ⊇ heuristic + manual |
| verdict = **MAX** shared-ratio across scales (STRONG 0.80) | the SHAPE classifier (NOT max) | **fixes the bug**: the token scale saturates ~0.999 for *any* two Python files → max-verdict says STRONG for unrelated pairs (measured) |
| shared n-grams (textual coincidence) | interned fan-in (exact shared subtrees) | no false-positives on comments / names / whitespace |
| file-level cosine + template | unit-level (def/class) + recursive typehole tree | finer granularity, recursive |

**Coverage gap — the toolchain blocker is now REMOVED (Φ4 ✅); one integration step remains.**
`agda_similarity` tokenizes *text*, so it handles **Agda**; `jea_pysim` parses *Python AST*, so it
handles **Python only** — it cannot read `.agda`. The structural method is strictly better but did not
cover Agda. **The core-intern shim is now BUILT**: `jea/metalanguage/agdai_shim.hs` (~80 lines, ghc
-package Agda) decodes a `.agdai` with Agda 2.8.0's OWN deserialiser (`decodeInterface`, no hand-decoded
tag table — Agda's types ARE the segmentation), walks each definition's `defType` over the real
`Term`/`Elim'` ADTs, and emits the JSON-lines schema `jea_agdai.intern_signature` consumes.
`jea_agdai.core_intern_agdai` drives it end-to-end → the FULL parent→child core DAG. VALIDATED:
Emit.agdai → 62 core nodes → interned 20 (3.1×, full edges); EmitDAG.agdai → 118 → 26. (Contract: the
`.agdai` must be current-toolchain — a stale interface decodes to Nothing → rebuild; the shim runs from
the interface's own dir, Agda's decode context being project-relative.)

So Agda core now interns into the same forest as Python — `jea_pysim`+`jea_agdai` ⊇ `agda_similarity` in
method AND (core) coverage. **Φ4b ✅ — the Agda-corpus mode is BUILT:** `jea_pysim` routes `.agdai` files
through `agdai_shim` (now emitting `{"unit":qname,"root":id}` per definition) → `core_intern_agdai` →
one `Unit` per definition's elaborated type, in the SAME forest. Every readout (clusters, typehole, S(g),
`--shape`, cohomology) is front-end-agnostic and runs on Agda core unchanged (Agda nodes carry
`kind="AgdaCore"`, `op`=constructor/qname, `role`=de-Bruijn; the typeholer keys on `op` as it keys on Python
`kind`). VALIDATED on the emit corpus: 3 `.agdai` → 58 units → cross-file `--shape` candidates
(`Emit.term-serialises ✕ term-evaluates` frac 0.83; `Emit.Term.lf ✕ EmitDAG.Node.nmul` frac 0.8 cross-file
— precisely the structural cross-module signal a textual tool misses). Python path unregressed; `.py`/`.agdai`
mixable in one corpus.

**Retirement of `agda_similarity` — capability achieved; ONE nuance to weigh (user call).** Nothing live
depends on it (no gate/hook/importer; only docstrings + scratch figures). The structural tool is strictly
better *for built code*. The single residual: `agda_similarity` reads `.agda` SOURCE TEXT (no build), while
the structural path needs the `.agdai` (build first). For this fully-built repo that niche is marginal —
retire it (git-recoverable) — but the decision is the user's since it removes the only *unbuilt-source* text
comparator. **Deepened (Φ4b+):** the shim now also walks `theDef`'s `FunctionDefn` clause bodies — each unit
is a synthetic `Defn` root over [type, clause-bodies…] (keyed structurally; qname rides the unit marker), so
the unit captures PROOF/PROGRAM content, exactly what `agda_similarity`'s text saw. Emit corpus: 62→190 core
nodes; `--shape` now finds true cross-module near-duplicates (`Emit.eval ✕ EmitBig.eval` frac 0.98 hole@d2 —
same algorithm, carrier literals differ; `render` 0.96; `evalStr` 0.93 cross-file) — which textual n-grams
miss (different literals). So the structural tool covers `agda_similarity`'s signal AND beats it.

## ⑤ Φ1′ — kirchhoff is a COORDINATE of one law (subtraction-capability selects the chart, not the graphs)

Π2 unified two circuit-solve instances — `jea_onegraph` (graded-ℚ) and `jea_picircuit` (Fraction) — via
`jea_circuit`'s pluggable carrier. The Π4 sweep flagged el-atlas `kirchhoff_nedge`'s `G_AND`/`G_OR` (0.95)
as a third instance. That map is **correct** — and the perspective-difference ("`G_AND` primitive" vs
"nodal `solve` primitive") is itself a mappable axis, not a reason to keep them apart. *Mapping perspectives
is what the `--shape` instrument does.* (My first pass rejected the fold by privileging kirchhoff's
"nodal-primitive" perspective — the exact G9 failure: leading with my judgment over the instrument's mapped
output. Corrected.)

**The axis is the carrier's subtraction-capability — but it selects the COORDINATE, not the solvable graphs
(Φ1′ correction):** the governing law has TWO coordinates, both in `jea_circuit`:
- `nodal_solve` = the **subtractive** coordinate — Kirchhoff nodal analysis by Gaussian elimination over the
  Laplacian; needs a **subtraction-having** carrier (the Laplacian's negative off-diagonals + elimination).
  `kirchhoff.solve` is its float instance. (witnesses w7/w8: nodal == series_schur / parallel on reducible
  graphs; w9: balanced Wheatstone resolves to 1.)
- `nodal_solve_subfree` = the **subtraction-free** coordinate — by the **Matrix-Tree theorem**, G_eff is a
  RATIO of two positive sums-of-products of edge conductances (spanning-tree polynomial T over spanning-
  2-forest polynomial F_st). Only add/mul/div touch the carrier, **no `.sub`** — so the graded-ℚ wedge runs
  it on **any** graph, irreducible ones included (w11/w13: it solves the IRREDUCIBLE Wheatstone, exactly, and
  agrees with `nodal_solve`). The float realization is the log/division/exp route (products→log-sums, the
  ratio→subtraction-of-logs=division, exp on readout — the exp⊣log retraction).
- `series_schur`/`parallel` = the closed-form projection for series-parallel-**reducible** graphs.

So the instances are ONE conductance-eval over **carrier value-type** (graded-ℚ / Fraction / float) and a
**coordinate choice** (subtractive Gaussian vs subtraction-free Matrix-Tree) that the carrier's subtraction-
capability *selects* — it does NOT bound which graphs are solvable. **(Φ1′ correction:** an earlier rung froze
"sub-free ⟹ closed form only / cannot solve irreducible graphs" and raised `TypeError` to enforce it — a
collapsed scalar coordinate mistaken for the geometry. The governing law is coordinate-free; subtraction was
only the Gaussian chart. Removed — the coordinate→geometry discipline: build the subsuming subtraction-free
solve, the closed form is its reducible-graph degenerate output.) `kirchhoff.solve` is the float instance of
the subtractive coordinate; jea carries its own solves (validatable the way `jea_onegraph` self-hosts el-atlas
— a homing choice, no cross-project import/cycle).
