---
name: feedback_opaque_staging_bounds_dense_elaboration
description: "a dense CONCRETE type-level computation (normalize detJac, an AES round KAT) is NOT an intrinsic memory floor — opaque STAGING seals each intermediate so the peak = the max single stage; recover the recorded seal-method before declaring a floor"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-23T18:57:30.224Z
---

A heavy type-level elaboration that OOMs (`normalize R.detJac` at 317 MB, an AES round's concrete `= refl` KAT) is
**NOT an intrinsic memory floor.** I twice declared these cap-128 offenders "intrinsic — the proving module pays
once, needs a cheaper proof or an exemption." Both times the USER corrected me: **opaque STAGING** bounds the peak.

**Why:** the blowup is agda holding the WHOLE dense reduction at peak. But the computation decomposes — a
determinant is a **Leibniz sum over Sₙ** (`det M = Σ_{σ} sign σ · ∏ⱼ M[j,σj]`), an AES round is a **pipeline**
(SubBytes→ShiftRows→MixColumns→AddRoundKey). And `normalize` is a **homomorphism** over `+P`
(`normalize-distrib : normalize (a +P b) ≡ normalize (normalize a +P normalize b)`, `MPolyNormalizeCoxeter:36`).
So you **seal each stage's intermediate as a non-reducing token** (the opaque-TYPE seal, OrderOf template
`Foundation/Fin/Iterate.agda:40-60`) — the next stage consumes the sealed token, not the re-expansion — and the
peak drops to **max(one stage, the merge)**. It is the SAME proof, elaborated piecewise ("reflection + membudget
decomposition", CLAUDE.md).

**Empirical proof:** the STAGED Leibniz det (`Z/JacobianDetNative = LeibnizDet.det {3} JacMat`, with
`detNative-normal : detNative ≡ normalize detJac`) is **150 MB** in the buildtime ledger vs the monolithic
`normalize detJac` at **317** — staging alone halved it; per-summand sealing pushes it under 128.

**How to apply:** before concluding "floor / can't drop the cap / not worth it," **recover the RECORDED
seal-method** (`scratch/cap384_orderof_seal_plan.md`, CLAUDE.md's opacity discipline, the OrderOf template) — it was
written down and I declared a floor twice before reading it. Caveat: staging works only where the decomposition has
BOUNDED intermediates (normalize a hom, terms balanced) — determinants and pipelines have it; a large-module
CUMULATIVE peak (no single neutral) wants a module SPLIT instead. Widens [[declaring-wall-rebuild-reflex]],
[[read-structure-dont-rebuild]], [[opacity-blowup-routearound-freeup]], [[hunt-opacity-after-green]].
