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
| **0.95** | el-atlas `kirchhoff_nedge` `G_AND`/`G_OR` (series=`a·b/(a+b)`, parallel) | **a THIRD circuit-solve instance** — fold onto `jea_circuit` (extends Π2: onegraph + picircuit + kirchhoff = one solve, three carriers). |
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

## The standout finding

The **circuit-solve has three independent reimplementations** — `jea_onegraph` (graded-ℚ, Π2-folded),
`jea_picircuit` (Fraction, Π2-folded), and `kirchhoff_nedge` (float/nodal, NOT yet folded). Π2 unified
the first two via `jea_circuit`'s pluggable carrier; folding `kirchhoff_nedge` onto the same solve is
the natural Π2 extension (a float/nodal carrier — or its nodal `solve` is the carrier's `div`).
