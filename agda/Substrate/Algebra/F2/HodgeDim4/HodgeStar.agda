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

open import Data.Fin using (Fin)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal
  using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim4.Bivector

------------------------------------------------------------------------
-- Hodge ★ basis-images: each basis 2-blade ↦ its complement basis.
------------------------------------------------------------------------

hodge-star-images : Fin 6 → Vector 6
hodge-star-images i = basis (complement i)

------------------------------------------------------------------------
-- Hodge ★ as an F₂-linear map on bivectors.
------------------------------------------------------------------------

hodge-star : Linear 6 6
hodge-star = linear-from-images hodge-star-images

------------------------------------------------------------------------
-- Involution on basis 2-blades: ★(★(e_i)) ≡ e_i.
--
-- Chain (each step uses one universal-property lemma):
--   apply hodge-star (apply hodge-star (basis i))
--     ≡ apply hodge-star (basis (complement i))        [apply-basis on inner]
--     ≡ basis (complement (complement i))              [apply-basis on outer]
--     ≡ basis i                                        [complement-involution]
------------------------------------------------------------------------

hodge-involution-basis :
  (i : Fin 6) →
  apply hodge-star (apply hodge-star (basis i)) ≡ basis i
hodge-involution-basis i =
  trans (cong (apply hodge-star)
              (apply-linear-from-images-basis hodge-star-images i))
  (trans (apply-linear-from-images-basis hodge-star-images (complement i))
         (cong basis (complement-involution i)))

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
