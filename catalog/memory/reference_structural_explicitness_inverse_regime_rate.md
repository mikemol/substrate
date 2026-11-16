---
name: reference_structural_explicitness_inverse_regime_rate
description: "A proof's STATIC structural explicitness (jea_pysim interned forest_size) is an INVERSE proxy for its DYNAMIC regime-rate r = CheckRHS_ms/cmp_reduce (normalization cost per conversion). Explicit structural proofs trade many-shallow conversions (low r) for the terse-reflection regime's few-deep normalizations (high r); CheckRHS = cmp_reduce × r. So forest_size pre-build predicts r — the proof-regime oracle's structural predictor."
metadata:
  node_type: memory
  type: reference
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**Measured 2026-06-26 (Ⓟ.cmp-reduce-structural — `proofcost.py --structural`, joining the jea_pysim ANALYZER
to the profiler ledger), over 3 regimes of the SAME GF dlog theorem:**

| module | jea_pysim forest_size (static) | cmp_reduce | r = CheckRHS/cmp_reduce (dynamic) |
|---|---|---|---|
| GF16DLog (terse, `refl` on *Q) | **62** | 156 | **7.36** ms/cmp |
| GF16TwoFaces | 135 | 123 | 0.52 |
| DLogHom (explicit structural hom) | **395** | 302 | **0.48** |

**`forest_size ↑ ⇒ r ↓`** — and *inversely to naive intuition*, the SMALLEST interned term has the HIGHEST
per-conversion cost. Mechanism: an EXPLICIT structural proof (big forest) pushes the work into MANY SHALLOW
symbolic conversions (`trans`/`cong`, low r, high cmp_reduce); a TERSE reflection proof (tiny forest — the
inverse-laws are bare `refl`) leaves it to FEW DEEP normalizations (high r). The cost is the product:
`CheckRHS_ms = cmp_reduce × r` ([[reference… proof-regime-oracle]] / proofcost.py). The structural proof wins
because its r is ~15× lower — the explicit structure is cheaper than deep normalization (DLogHom 146ms vs
GF16DLog 1148ms CheckRHS, same theorem).

**Why it matters / how to apply.** This is the jea_cost "read counts off the op-graph" step for proofs: the
ANALYZER's *static* size proxies the PROFILER's *dynamic* regime-rate, so a regime's CheckRHS is predictable
PRE-BUILD: `forest_size → r (inverse) → CheckRHS = cmp_reduce × r`. The dominant factor r is DYNAMIC
(normalization depth — not pinnable from static size, only its regime is); forest_size gives the regime
signal. Practical pull: **prefer explicit structural proofs over terse reflection** — terse `refl`-on-a-deep-
computation is the high-r trap that OOMs (cf. [[oom-load-bound-finding]]: *Q-reflection exponential in depth;
the division/structural regime is the route-around). The exact regression sharpens as the always-on profiling
ledger (`.agda-profile.tsv`, opt-out at the agda shim) accumulates samples. Connects the profiler ↔ analyzer ↔
the strategy-selection charts (tropical/logsumexp/conductance).
