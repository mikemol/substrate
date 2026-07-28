------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar
--
-- N-3 + N-4 of M-11.dim4. The Hodge ★ operator at grade 2 in F₂⁴,
-- and its involution property (★² = id).
--
-- Hodge ★ : Linear 6 6 — sends each basis 2-blade `e_i ∧ e_j` to its
-- complement `e_k ∧ e_l` (where {i,j,k,l} = {0,1,2,3}). Built via
-- `linear-from-images (λ i → basis (complement i))` (universal-property
-- discipline).
--
-- The involution proof uses M-3.5 linear-extensionality: ★² agrees
-- with id-L on all 6 basis 2-blades; by extensionality, equal on all
-- bivectors. The per-basis step uses `apply-linear-from-images-basis`
-- (foundational primitive from M-11.fano N-1) twice + complement-
-- involution (from Bivector.agda) once.
--
-- This is the first F₂-linear operator in the substrate that has
-- non-trivial Hodge content: at grade 1 (M-11.dim3, M-11.fano), Hodge
-- reduces to subspace orthogonality; at grade 2 in F₂⁴, it's an actual
-- involution operator on bivectors.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.HodgeStar where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Involution using (basis-permutation-involution)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear using (basis-permutation-Linear)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order using (HasOrder-from-perm)
open import Substrate.Foundation.Fin.Iterate using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.Universal
  using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim4.Bivector

------------------------------------------------------------------------
-- Hodge ★ basis-images: each basis 2-blade ↦ its complement basis.
-- Kept for backwards-compatibility with sites citing the images
-- directly (e.g., apply-linear-from-images-basis hodge-star-images).
-- Definitionally equal to `basis ∘ complement`.
------------------------------------------------------------------------

open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
hodge-star-images : Fin 6 → Vector 6
hodge-star-images i = basis (complement i)

------------------------------------------------------------------------
-- Hodge ★ as an F₂-linear map on bivectors.
--
-- Named at the universal-property level: Hodge ★ IS the
-- basis-permutation-Linear induced by the complement involution on
-- the 6 basis 2-blade indices. The `linear-from-images` infrastructure
-- + `complement-involution` give ★² = id mechanically.
------------------------------------------------------------------------

hodge-star : Linear 6 6
hodge-star = basis-permutation-Linear complement

------------------------------------------------------------------------
-- Involution on basis 2-blades: ★(★(e_i)) ≡ e_i.
--
-- One-line application of the `basis-permutation-involution`
-- universal-property combinator at σ = complement (which satisfies
-- σ² = id via `complement-involution`).
------------------------------------------------------------------------

hodge-involution-basis :
  (i : Fin 6) →
  apply hodge-star (apply hodge-star (basis i)) ≡ basis i
hodge-involution-basis = basis-permutation-involution complement complement-involution

------------------------------------------------------------------------
-- Involution on all bivectors: ★² = id.
--
-- By M-3.5 linear-extensionality: two Linears that agree on basis
-- vectors agree on all vectors. Here L = hodge-star ∘L hodge-star
-- (= apply ★ then apply ★, with apply (L ∘L M) reducing definitionally
-- to apply L ∘ apply M) and M = id-L (apply id-L = id).
------------------------------------------------------------------------

hodge-involution :
  (ω : Vector 6) →
  apply hodge-star (apply hodge-star ω) ≡ ω
hodge-involution =
  linear-extensionality (hodge-star ∘L hodge-star) id-L hodge-involution-basis

------------------------------------------------------------------------
-- Retrofit — Hodge ★ as a HasOrder instance of the FiniteOrder primitive.
--
-- Connects this Hodge ★ to Substrate.Category.Coalgebra.FiniteOrder.
-- `HasOrder (apply hodge-star) 2` IS the involution `★² = id` lifted
-- to the categorical primitive's universal property.
--
-- Now derived structurally via the order-k lift: complement is an
-- involution on Fin 6 (witnessed by complement-involution); the lift
-- HasOrder-from-perm transports this to HasOrder (apply L) 2 where
-- L = basis-permutation-Linear complement = hodge-star.
--
-- Per [[project-torsion-element-universal]]: this is the canonical
-- order-2 instance of HasOrder in the substrate. The Hodge dual is
-- the structural "+1" of every torsion-element-of-automorphism site
-- at order 2 — the simplest non-trivial torsion element acting on
-- bivectors at dim 4.
--
-- Per `feedback_categorical_name_first`: HasOrder is the categorical
-- handle; the retrofit derives it from the universal permutation-order
-- lift rather than from the per-instance involution proof.
------------------------------------------------------------------------


-- Hodge ★ as an endomap of Vector 6 (= Bivector at dim 4).
hodge-star-endo : Endomap (Vector 6)
hodge-star-endo = apply hodge-star

-- complement, packaged as a HasOrderPerm witness at order 2.
complement-HasOrderPerm : HasOrderPerm complement 2
complement-HasOrderPerm = complement-involution

-- Hodge ★ has order 2 — the FLT-for-dimensional-spaces analog at the
-- substrate's canonical involution, derived structurally via the lift.
HasOrder-hodge-star : HasOrder hodge-star-endo 2
HasOrder-hodge-star = HasOrder-from-perm complement 2 complement-HasOrderPerm
