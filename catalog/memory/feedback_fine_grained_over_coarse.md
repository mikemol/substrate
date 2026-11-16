---
name: fine-grained-over-coarse
description: "Override DBE's over-decomposition warning: prefer fine-grained primitives. Recomposition is mechanical/cheap; coarse-grained primitives create context-flood for rearrangement."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

The decompose-by-entailment skill warns against "over-decomposition" — extracting primitives with fewer than ≥3 sites or that are smaller than the composition machinery. **This warning is wrong for the substrate.**

**Rule:** Extract aggressively. Even 2-site primitives are extraction-worthy if they capture genuine structure. Don't decline extractions because they "would be over-decomposition".

**Why:** The asymmetry of mechanical work:

- **Recomposition from fine-grained primitives** is deterministic, mechanical, and cheap. Tooling (parametric modules, mechanical inlining, search-and-replace) can collapse fine-grained primitives into coarser forms when needed.
- **Re-decomposition of coarse-grained primitives** is context-bound, requires understanding, and creates context-flood when many sites must be rearranged. The work is permanent loss when context is lost.

The substrate's discipline is: pay the extraction cost up-front when it's cheap (1 site is enough); recomposition machinery exists or can be built; lost extractions cost more later.

**How to apply:**

- A 2-site primitive that captures a real structural pattern → extract.
- A template shared across N>=2 files with body differences only at orbit/index/parameter positions → extract a parametric module, even if the per-site savings is small.
- A "costructure without reuse" warning (DBE skill) is *not* sufficient grounds to decline — only decline if the costructure is *not real structure* (e.g., a renamed helper with no semantic content).

**Concretely flagged for re-examination (declined in prior turns under the wrong discipline):**

- `S1S2CubedOnE0` / `E1` / `E2` — 3 files sharing template + orbit-specific swap-lemma applications. Parametric "cubed-on-orbit" lemma extraction is warranted.
- `ChiralityAxis.agda` + `V4Plane.agda` post-KernelPredBridge — share 20 lines of skeleton; parametric `kernel-pred-bridge-module` taking (Pred, Selector, Selector-lookup-lemmas) is warranted.
- Any other "template-shared but body-different" patterns the typed-holes surfaced.

**Related:** [[cong-trans-extraction]] saturation-claim should be revisited under this discipline; "saturation" was an artefact of the wrong heuristic.
