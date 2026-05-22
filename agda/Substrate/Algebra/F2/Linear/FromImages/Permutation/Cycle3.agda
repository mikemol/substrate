------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
--
-- The substrate's first concrete order-3 (non-involution) torsion
-- instance: the 3-cycle σ₃ : Fin 3 → Fin 3 lifted via
-- basis-permutation-Linear.
--
-- σ₃ permutes the three basis elements of F₂³ as 0 → 1 → 2 → 0.
-- The induced Linear cycle3-Linear : Linear 3 3 has order 3 as an
-- endomap of Vector 3, witnessed via HasOrder-from-perm.
--
-- Slice 5 of 5 in the order-k arc. After slices 1-4 named the
-- order-k machinery + retrofitted hodge-star (order 2), this slice
-- demonstrates the machinery handling a fundamentally different order.
--
-- Per [[project-torsion-element-universal]]: this is the substrate's
-- first NON-INVOLUTION torsion element. Connects to:
--   * Substrate.Groups.Z3-Coxeter (the abstract Z₃ Coxeter system)
--   * Future generic Z/k-cyclic actions on Vector n
--   * S₃ stabiliser work (S₃ = ⟨σ₃, transposition⟩; the 3-cycle here
--     is the generator of the cyclic A₃ ⊂ S₃ subgroup)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

------------------------------------------------------------------------
-- N-1: σ₃ — the 3-cycle on Fin 3 (0 → 1 → 2 → 0).
------------------------------------------------------------------------

σ₃ : Fin 3 → Fin 3
σ₃ zero                = suc zero
σ₃ (suc zero)          = suc (suc zero)
σ₃ (suc (suc zero))    = zero

------------------------------------------------------------------------
-- N-2: σ₃ has order 3 as a permutation — σ₃³ = id pointwise.
--
-- Direct check on each of the three inhabitants of Fin 3. Each case
-- reduces to refl after three applications of σ₃ defining clauses.
------------------------------------------------------------------------

σ₃-HasOrderPerm : HasOrderPerm σ₃ 3
σ₃-HasOrderPerm zero                = refl
σ₃-HasOrderPerm (suc zero)          = refl
σ₃-HasOrderPerm (suc (suc zero))    = refl

------------------------------------------------------------------------
-- N-3: cycle3-Linear — the linear endomap induced by σ₃.
--
-- Permutes basis vectors of F₂³ as 0 → 1 → 2 → 0.
------------------------------------------------------------------------

cycle3-Linear : Linear 3 3
cycle3-Linear = basis-permutation-Linear σ₃

------------------------------------------------------------------------
-- N-4: HasOrder-cycle3 — substrate's first order-3 HasOrder instance.
--
-- Mechanically derived via HasOrder-from-perm applied to
-- σ₃-HasOrderPerm. No per-instance proof required; the lift handles
-- the basis-level induction + linear-extensionality automatically.
------------------------------------------------------------------------

HasOrder-cycle3 : HasOrder (apply cycle3-Linear) 3
HasOrder-cycle3 = HasOrder-from-perm σ₃ 3 σ₃-HasOrderPerm

------------------------------------------------------------------------
-- N-5: Capstone — order-k arc complete.
--
-- The 5-slice arc:
--   #1 σ-iterate + HasOrderPerm           — foundational data
--   #2 basis-permutation-order-k          — basis-level combinator
--   #3 HasOrder-from-perm                 — lift via linear-extensionality
--   #4 retrofit HasOrder-hodge-star       — order-2 instance via the lift
--   #5 cycle3-Linear + HasOrder-cycle3    — first order-3 instance
--
-- After this slice, the substrate has:
--
--   * A uniform "FLT-for-dimensional-spaces" machinery for any basis-
--     permutation-Linear instance at any order k.
--   * Two concrete instances at distinct orders (★ at order 2;
--     cycle3 at order 3), demonstrating the machinery scales.
--   * The first non-involution torsion-element instance in the
--     substrate's HasOrder primitive.
--
-- Per [[project-torsion-element-universal]]: the substrate now hosts
-- the basis-permutation-Linear → HasOrder pipeline as a universal
-- machinery. Any future cyclic / dihedral / symmetric-group element
-- acting via basis permutation lands its HasOrder witness for free
-- once HasOrderPerm is supplied.
--
-- Deferred follow-ons:
--
--   * **HasLagrangeOrder generalization**: lift HasLagrangePerm
--     (composite-order witness via Euler-Fermat) to HasLagrangeOrder.
--   * **Generic Z/k-cycle on Fin n**: σₖ : Fin n → Fin n (cyclic
--     shift) + HasOrderPerm σₖ k for any k ≤ n.
--   * **Dihedral instance**: combine cycle3 with a reflection to
--     instantiate D₃ = S₃ acting on Vector 3.
--   * **Connection to Substrate.Groups.Z3-Coxeter**: the abstract
--     Z₃ Coxeter element corresponds to σ₃ via this lift.
------------------------------------------------------------------------
