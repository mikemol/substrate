---
name: project-torsion-element-universal
description: "The 3+1 parity universal generalizes to a torsion-element-of-automorphism universal — at every subspace supporting a finite-order automorphism γ with γ^k = id, the local Z/k cyclic group gives a k+1 split with the \"+1\" being the torsion identity (γ^0 = e). Hodge ★ at order 2 and Coxeter braid (sᵢsⱼ)^p = e at order p are facets of one ambient object."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's [[project-3plus1-parity-universal]] (3:1 splits at every 2-dim F₂-subspace, with "+1" carrying the chirality / Hodge dual) is a special case of a more general structural recurrence: **torsion-element-of-automorphism universal**.

**Ambient object:** a finite-order automorphism γ on some carrier X (i.e., `iterate k γ ≡ id-end` for some k ≥ 1).

**Multi-reading aspects (per [[feedback-multi-reading-ambient-discipline]]):**

| Reading | γ | X | k |
|---|---|---|---|
| Hodge involution at variable dim | ★ (Hodge dual) | Λᵏ(F₂ⁿ) | 2 |
| Coxeter braid as Fermat-like | sᵢsⱼ (Coxeter braid) | W(A_n) (Weyl group) | p (Coxeter matrix entry mᵢⱼ) |
| Hodge as modular structure | ★ | structure space | order(★) = 2 |
| "Fermat for dimensional spaces" | any finite-order γ | dimensional space | order of γ |

**Why all three readings are the same object:**

`HasOrder γ k` (= γ^k = id-end pointwise) is the structural statement. The reading "Hodge involution" picks γ = ★ with k = 2; "Coxeter braid as FLT" picks γ = sᵢsⱼ with k = p; "Hodge as modulus" picks the quotient X/⟨γ⟩ as the orbit-modular structure. All three are aspects of the same finite-order endomap.

**Why this generalizes the 3+1 parity universal:**

The "+1" in every 2-dim F₂-subspace's 3:1 split is the IDENTITY element of the local Z/2 (= ⟨★⟩) cyclic group — i.e., the unit / fixed point under iteration. At each scale where a finite-order γ exists, the "+1" generalizes to "γ^0 = e", and the "k" generalizes to "the other (k-1) elements of ⟨γ⟩."

For Hodge ★ at every 2-dim subspace: k = 2, gives 1:1 split with "+1" = identity, but combined with the 2-element basis subspace, gives the 3+1 pattern. For Coxeter (sᵢsⱼ)^p = e at every 3-dim subspace supporting it: k = p, gives the k+1 split structure.

**FLT for dimensional spaces — the structural statement:**

Classical FLT: `a^p ≡ a (mod p)` where p is prime. The dimensional-space analog: `iterate k γ ≡ id-end` for an order-k automorphism γ. The "modulus" IS γ (or the cyclic subgroup ⟨γ⟩ it generates); applying γ k times returns identity, just as raising to p mod p returns the original.

The Hodge dual is the order-2 instance of this — the simplest non-trivial torsion-element-of-automorphism — and serves as the universal "+1" / identity of the local Z/2 modular structure.

**Substrate touchpoints:**

- [[project-3plus1-parity-universal]] — the original observation; this memory generalizes it.
- [[feedback-categorical-name-first]] — the categorical name for the ambient is "torsion-element-of-automorphism" or equivalently "finite-order endomap"; the substrate primitive lives at `Substrate.Category.Coalgebra.FiniteOrder`.
- [[project-tetrative-metacircularity]] — each meta-level instantiates the torsion-element universal; the Hodge dual at level L_n is the order-2 torsion element at level L_{n+1}.
- Substrate's existing `FixedPoint` primitive is the **k=1 case** of `HasOrder`.
- Substrate's `CoxeterRelations` (s₁², s₂², braid) are concrete `HasOrder` instances at orders 2 and 3.

**Implications:**

The substrate's recurrence of "3+1" at multiple scales isn't really about parity (Z/2 specifically). It's about whatever torsion-element-of-automorphism is locally available. At each scale:
- The local symmetry group has a torsion subgroup
- The torsion subgroup generates the "modular" structure
- The identity element of the torsion subgroup IS the "+1" of the local split
- The (order - 1) non-identity elements give the rest of the split

The Hodge dual is the substrate's universal order-2 instance (the simplest non-trivial torsion). Coxeter braid relations give order-p instances at each prime p. The unification is structural.
