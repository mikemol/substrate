---
name: adjunction-is-the-wedge-residue-counit
description: "The wedge a = recon q b r IS a Free⊣Forgetful adjunction; the residue r is the counit-defect wearing every name (remainder, Lehmer digit, orientation, Lawvere δ, CRT combine-correction)."
metadata:
  node_type: memory
  type: reference
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

The wedge equation `a = recon q b r` is not just division — it IS the encoding of a
**Free ⊣ Forgetful adjunction**, and the residue `r` is its **counit-defect**. This is
keystone #1 ("residue = adjoint correction") and it unifies the substrate's spine.

**The two adjoints (order-sensitive vs order-insensitive), witnessed at the witness tower:**
- FORGETFUL = drop the residue: `a ↦ b`. The order-INsensitive nerve side — faces `delAt`
  (`SimplicialBoundary.simplicial : dᵢd_{suc j}=dⱼdᵢ`), everything commutes, the final simplex.
- FREE = build with a choice: `(b, r) ↦ recon q b r`. The order-SENSITIVE Lehmer step
  `insert-at` (`WitnessTower.LehmerPath`) — the `n!` orderings = permutohedron `P_{n-1}` = `Sₙ`
  (edges = adjacent transpositions = Coxeter generators). NOTHING commutes; its
  non-commutation IS the permutohedron. (`insert-at` satisfying `δⱼδᵢ=δᵢδⱼ₋₁` is an
  UNINHABITED proposition — an attempt walls; you can't prove a false thing in constructive TT.)
- The (co)unit is the WEDGE: `a ≡ recon b r` = "`FU a` recovers `a` up to the residue `r`".

**One object, every name.** `r` = the wedge remainder = the graded `GradedWedge.rem`/`gcell`
= the Lehmer digit = the permutohedron edge = the Coxeter-word step = the **relative
orientation** between two towers = the Lawvere diagonal defect `δ` (`diag∘promote = δ ≠ id`)
= the CRT combine/Bézout correction (split=diagonal is trivial; combine carries the content).

**How to apply:** the existing `Algebra.Wedge.Graded.Adjunction` (`geval = recon` forgetful,
`from` free, `gtriangle`, `geval-eq`) IS this adjunction; instantiate it (e.g.
`WitnessTower.Wedge.Adjunction` at `C=Perm, R=Fin∘suc`) and label `r` the orientation — then
"the wedge of distinction is the counit-defect" is literally a typechecked lemma. Don't
re-derive the adjunction; name the wedge as it. See [[wedge-projection]], [[free-universal-property]],
[[def-proof-separation-lever]].
