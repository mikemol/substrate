---
name: feedback-composable-primitives-over-flat-enumeration
description: "Prefer composable primitives over flat enumeration even when line count grows. Compositionality benefits LLM context efficiency: each shadow fits in a single attention window; errors localize; trans-chains-of-shadows substitute for global proof obligations. Cost the parameters of the abstract interface, not the line count of the file."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Rule:** When refactoring complex theorem-heavy modules, choose composable abstractions even when the line count is larger than a flat enumeration would be. The cognitive locality gain matters more than the line count.

**Why:** Observed empirically during the Coxeter framework refactor (Slices 1-4). The Coxeter framework totaled ~997 lines vs ~632 lines for the equivalent flat V₄ + V4-Generic + V4-Index + V4-Normality.V₄-4-product implementation. Despite +365 lines, the Coxeter version was:

1. **Cognitively easier to build** — each shadow (Word, Core, ListPresentation, DirectProduct, Z2-Coxeter, V4-Coxeter, V4-as-Z2xZ2) fits in a single attention window. The user observed: "it was cognitively easier to build because it broke down into more composable primitives. This is good for LLM context efficiency."

2. **Error-local** — when V4-as-Z2xZ2 had a `_++_` clash with Data.List, the diagnosis was 2 lines of root-cause (`Core parameter vs stdlib import`), not a tangled report across 6 files.

3. **Composition-as-correctness** — the trans-chain of shadows IS the proof; each shadow's interface obligation makes per-instance verification a local fact.

**How to apply:**

* When a single file holds multiple non-trivial theorems sharing dense local helpers (where-clauses, private modules), and those helpers can be LIFTED to top-level with abstract interfaces, the refactor is worth doing even if total line count grows.
* **Rule of thumb**: cost the *parameters of the abstract interface*, not the line count of the file. An interface with 5-10 well-typed parameters is a small cognitive cost regardless of how many lines its body has.
* When projecting refactor scope, count: (1) what cognitive locality does each shadow provide? (2) what tasks can future sessions tackle in isolation that previously required loading the whole file?

**Candidates for this pattern (as of 2026-05-17)** — files in the substrate where applying this principle would help:
* `Substrate.Groups.SemidirectProduct` (~300 lines, mixes v-of-axis / s-for-anchor / factorisation / uniqueness).
* `Substrate.Cocycles.V4Signature.S4Iso` (~700 lines, stab-permutations + orbit-key dispatch + S₄ ↔ TotalSpace).
* `Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection` (~400 lines, codeword ↔ S₄ round-trip).

Each could decompose into 4-6 shadows of ≤ 100 lines, with abstract interfaces costed as 5-10 parameters at module boundaries.

**Connection to existing memories:** complements [[feedback-v4-typeclass-architecture]] (which advocates parametric modules at the V₄ level) by extending the principle to "even when the parametric version is bigger, do it." Replaces the implicit assumption that "smaller file = better refactor."

**Don't apply to:**
* Files under ~150 lines that are already self-contained.
* Cases where the abstract interface would itself have > 15 parameters (over-decomposition; the cognitive cost moves to the interface).
* One-off ad-hoc proofs where there's no anticipated second consumer.
