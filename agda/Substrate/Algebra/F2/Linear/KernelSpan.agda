------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.KernelSpan
--
-- Ⓕ.spectral — dissolving the "dimension needs Gaussian elimination" wall.
--
-- "Dimension of a subspace" is an INCOMPLETE type, because "subspace" is
-- an incomplete type — a typehole: a skeleton with a hole where the basis
-- goes. Completing it does NOT mean EXTRACTING a canonical basis (Gaussian
-- elimination); it means FILLING the hole with a basis the structure
-- already hands you (for the cycle operator: the orbit decomposition). The
-- change to that basis is a CrossMul by (dest-basis / source-basis) — the
-- cospan A → R ← B of Wedge.CrossMul, units cancelling.
--
-- This module proves the load-bearing half at the OPERATOR level (the way
-- spectral-kernel worked — no coordinates):
--
--   kernel-comb-in-ker : every linear combination of a SUPPLIED family of
--     kernel vectors stays in the kernel.
--
-- so a d-element kernel family `b : Fin d → Vector n` extends (via
-- FromImages — the basis is supplied, not extracted) to a linear map
-- F₂ᵈ → ker L. The proof is `linear-extensionality` (agree on basis ⟹
-- agree everywhere) against the zero map: NOTHING is solved for, nothing
-- is eliminated. The remaining half (the family is independent + spans ALL
-- of ker L, giving the iso F₂ᵈ ≅ ker L and hence dim = d) is supplied by
-- the concrete orbit basis in Ⓕ.spectral-bridge, with d = mult2/2·degΦ_p.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.KernelSpan where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply; _∘L_)
open import Substrate.Algebra.F2.Linear.Cyclotomic using (𝟘L)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)

------------------------------------------------------------------------
-- Any linear combination of a supplied family of kernel vectors is in the
-- kernel. Operator-level: the composite L ∘L (the family's linear span)
-- agrees with the zero map on every basis vector (each family member is in
-- ker L), hence everywhere (linear-extensionality). No coordinates solved.
------------------------------------------------------------------------

kernel-comb-in-ker :
  ∀ {d n m} (L : Linear n m) (b : Fin d → Vector n) →
  (∀ i → inKer L (b i)) →
  (x : Vector d) → inKer L (apply (linear-from-images b) x)
kernel-comb-in-ker L b b∈ker =
  linear-extensionality (L ∘L linear-from-images b) 𝟘L
    (λ i → trans (cong (apply L) (apply-linear-from-images-basis b i)) (b∈ker i))
