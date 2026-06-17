# Consolidation map (Π4) — the codebase's shared-shell + carrier-hole pairs

A **regenerable snapshot** produced by the `jea_pysim --shape` instrument (Π1), now trusted (Π5
controlled-perturbation validation) and proven (Π2 used it to fold the circuit-solve). Each entry is
a pair of units that share a structural *shell* with the difference isolated as *typed holes* at
specific depths — i.e. a candidate for one carrier-/parameter-parametric definition. Triaged: not
every high-similarity pair should be folded (intentional parallels, by-design families, versioned
rewrites). **This goes stale as code changes — regenerate, don't trust the line numbers.**

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
| 0.96 / 0.94 | `jea_agda_bridge.{read_vouched,typecheck}` ↔ `jea_agda_dag.{read_vouched,typecheck}` | near-identical (only the emitted filename differs); extract ONE agda-bridge helper parameterized by filename. The cleanest jea/ win. |
| 0.95 | el-atlas `kirchhoff_nedge` nodal `solve` / `G_AND`/`G_OR` | **perspective-mapped (Φ1 ✅ — see §⑤).** `jea_circuit` now carries `nodal_solve` (the governing law); `series_schur`/`parallel` are its subtraction-free reducible projection; the carrier's subtraction-capability is the mapped axis. `kirchhoff.solve` = the float instance (validatable, no cross-project import). |
| 0.94 | `jea_generator_strat._lh` ↔ `jea_generator_unified._lh` | identical limb-split helper; promote to one home. |
| 0.92 | `jea_carrier_solve.build_Eq` ↔ `jea_zsppf.build_Eq` | duplicated; one definition. |
| 0.93 | `chassis_cap_test.cpu_worker` ↔ `power_probe_root.cpu` | duplicated power-probe worker. |
| 0.91 | `radzdg-witness-pilot.{vadd,vsub}` ↔ `second-order-zd-pilot.{vadd,vsub}` | vector add/sub duplicated across pilots. |

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

## ④ Tool supersession (Π3) — `jea_pysim` ⊇ `scripts/agda_similarity`, retirement GATED

`jea_pysim` (structural) subsumes `agda_similarity` (textual) in **method, surfaces, and precision** —
and corrects a bug the original still carries:

| `agda_similarity` (textual) | `jea_pysim` (structural) | relation |
|---|---|---|
| 4 cosine scales (char3/token/line/block), comment-stripped | depth-grades over the interned SPPF + the `S(g)` SHAPE | structural; the shape is a curve, not a per-scale scalar |
| `anonymize_text` (hand-written regex per orbit, e.g. `Z[2-9]→<Zn>`) | **exact** α-equivalence (role-lowering, automatic) | exact + automatic ⊇ heuristic + manual |
| verdict = **MAX** shared-ratio across scales (STRONG 0.80) | the SHAPE classifier (NOT max) | **fixes the bug**: the token scale saturates ~0.999 for *any* two Python files → max-verdict says STRONG for unrelated pairs (measured) |
| shared n-grams (textual coincidence) | interned fan-in (exact shared subtrees) | no false-positives on comments / names / whitespace |
| file-level cosine + template | unit-level (def/class) + recursive typehole tree | finer granularity, recursive |

**But the retirement is BLOCKED — coverage gap.** `agda_similarity` tokenizes *text* (Agda-tuned but
language-general), so it handles **Agda**; `jea_pysim` parses *Python AST*, so it handles **Python only**
— it cannot read `.agda`. The structural method is strictly better, but it does not yet cover
`agda_similarity`'s actual domain. **Retirement is gated on `jea_agdai`'s core-intern shim** (the
Agda-2.8.0 `readInterface` JSON, currently a stub): once Agda core interns into the same forest,
`jea_pysim`+`jea_agdai` ⊇ `agda_similarity` in *both* method AND coverage (and structurally, beating its
textual n-grams). Until then `agda_similarity` STAYS — the only Agda-capable similarity tool.

## ⑤ Φ1 — kirchhoff is the nodal PERSPECTIVE, mapped (the carrier's subtraction-axis)

Π2 unified two circuit-solve instances — `jea_onegraph` (graded-ℚ) and `jea_picircuit` (Fraction) — via
`jea_circuit`'s pluggable carrier. The Π4 sweep flagged el-atlas `kirchhoff_nedge`'s `G_AND`/`G_OR` (0.95)
as a third instance. That map is **correct** — and the perspective-difference ("`G_AND` primitive" vs
"nodal `solve` primitive") is itself a mappable axis, not a reason to keep them apart. *Mapping perspectives
is what the `--shape` instrument does.* (My first pass rejected the fold by privileging kirchhoff's
"nodal-primitive" perspective — the exact G9 failure: leading with my judgment over the instrument's mapped
output. Corrected.)

**The axis is the carrier's subtraction-capability:**
- `series_schur`/`parallel` = the **subtraction-free** closed form; runs on a sub-free carrier (the graded-ℚ
  wedge, jea's charter), exact on series-parallel-**reducible** graphs.
- `nodal_solve` (Φ1, added to `jea_circuit`) = the **governing law** — Kirchhoff nodal analysis, general
  (handles irreducible graphs: shared resource, Wheatstone bridge); needs a **subtraction-having** carrier
  (Fraction/float). The closed form **emerges** from it exactly (witnesses w7/w8: nodal == series_schur /
  parallel on reducible graphs; w9: a balanced Wheatstone resolves).

So the three instances are ONE conductance-eval over two perspective axes — **carrier value-type**
(graded-ℚ / Fraction / float) and **carrier subtraction-capability** (sub-free → closed form only;
sub → nodal). `kirchhoff.solve` is the float instance of `nodal_solve`; jea carries its own (validatable
against el-atlas's the way `jea_onegraph` self-hosts it — a homing choice, no cross-project import/cycle).
The series-parallel reduction is the sub-free **projection** of the governing law — governing-law-before-
special-case, with both perspectives now in one module.
