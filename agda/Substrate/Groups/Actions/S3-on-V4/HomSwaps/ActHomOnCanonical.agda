------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical
--
-- act-hom-on-canonical : for canonical n, h, the action act-on-canonical
-- n h is a V₄-homomorphism.
--
-- STRUCTURAL PROOF (replaces the former 6-way dispatch onto per-canonical
-- 16-refl tables — HomId/HomRot/HomRot²/HomSwap{AB,AG,BG}). Since
--   act-on-canonical n h ≡ rot-pow n ∘ swap-pow h          (act-equals-pow)
-- and rot-pow = iter-pow rotate, swap-pow = iter-pow swap-αβ are iterates
-- of the two generators — each a homomorphism (rotate-IsHom, swap-αβ-IsHom)
-- — the composite is a homomorphism by ∘-IsHom + iter-pow-IsHom, for ANY
-- n,h. The homomorphism property is thus the COMBINATORICS of two
-- generator facts, not 6 Cayley tables. The 6 leaf hom-* files are no
-- longer needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical where

import Substrate.Groups.V4.Operations as V4
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong₂)

open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.V4.IsHomomorphism.Compose using (∘-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow using (swap-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateIsHom using (rotate-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapABIsHom using (swap-αβ-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Generators.IterPowIsHom using (iter-pow-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Twist.ActEqualsPow using (act-equals-pow)

act-hom-on-canonical :
  ∀ {n h} (c-n : Z₃E.Canonical-ex n) (c-h : Z₂E.Canonical-ex h) →
  ∀ v₁ v₂ →
  act-on-canonical n h (v₁ V4.· v₂) ≡
  act-on-canonical n h v₁ V4.· act-on-canonical n h v₂
act-hom-on-canonical {n} {h} c-n c-h v₁ v₂ =
  trans (act-equals-pow c-n c-h (v₁ V4.· v₂))
  (trans (pow-hom v₁ v₂)
         (sym (cong₂ V4._·_ (act-equals-pow c-n c-h v₁)
                            (act-equals-pow c-n c-h v₂))))
  where
    -- rot-pow n ∘ swap-pow h is a homomorphism: iterate of rotate after
    -- iterate of swap-αβ, both generator-homs.
    pow-hom : IsHomomorphism (λ v → rot-pow n (swap-pow h v))
    pow-hom = ∘-IsHom {f = rot-pow n} {g = swap-pow h}
                      (iter-pow-IsHom rotate-IsHom n)
                      (iter-pow-IsHom swap-αβ-IsHom h)
