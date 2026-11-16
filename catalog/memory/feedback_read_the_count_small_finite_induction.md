---
name: feedback_read_the_count_small_finite_induction
description: "Don't COMPUTE a quantity (dimension/count/multiplicity) — set the structure up so the term algebra READS it at check time. Work in small finite spaces, then induct to open ones. The repo's <64MiB architecture."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

Two coupled architectural principles (user, 2026-06-24, grounding why all-but-3 substrate modules build in <64MiB):

**1. You don't need the count — you need to READ the count.** Don't write code that *computes* a dimension / count / multiplicity and then *matches* it to a target. Set the structure up so the **term algebra reduces the obligation at check time** — the answer falls out as `refl` (or one finite case-split), never a materialized number or matrix. Caught live (Ⓕ.spectral): `apply (Φ₃ σ) (𝟙∷𝟙∷𝟘∷[]) ≡ 𝟎ⱽ` needed NO proof — the augmentation operator reduced to `𝟎ⱽ` by `refl`; the whole `dim ker Φ₃(σ) = 2` witness (`KernelDim`) was `refl`/case-split, no Gaussian elimination, no `dim : Subspace → ℕ` function. This is why the repo never materializes large objects (`≡-from-lookup` reduces to O(n) lookups not 2ⁿ; `linear-extensionality` = n basis-checks; `Over` proves once parametrically; `opaque` seals dense compute). Reading-by-reduction is the dual of [[feedback_read_structure_dont_rebuild]].

**2. Small finite spaces, then constructive-proof-by-induction for the open ones.** Prove the CONCRETE small case (p=3, length-3 F₂ — refl-cheap, the term algebra does the work) as the BASE CASE; lift to general / open by induction (the same shape as `FaceCount`'s cone-step proving one rung → all rungs). p=3 is not a cop-out; it's the base. This is WHY we work exclusively in small finite spaces: there, the term algebra reduces everything; induction carries it to ∞.

**Why:** materializing/enumerating/computing blows RAM and check time and reads as "I solved it" when really the structure should solve it. A quantity that *reduces* is verified by construction and stays tiny.

**How to apply:** before computing a count/dimension/invariant, ask *can I arrange the definitions so Agda REDUCES this to refl in a small finite instance?* If yes, do that + induct. Don't build a function that computes the number and a proof that it matches — make the number a parameter the structure READS (the typehole filler — [[feedback_declaring_a_wall_is_the_rebuild_reflex]]). Reuse the existing count (FaceCount/mult2) by letting it reduce, not by recomputing.
