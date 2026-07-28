------------------------------------------------------------------------
-- Substrate.Groups.V4.IsHomomorphism.Compose
--
-- IsHomomorphism is closed under composition and contains the identity.
-- Generic infrastructure: with these, a V₄-endo built by composing
-- generator-automorphisms is a homomorphism structurally — no per-case
-- Cayley table. (The structural collapse of the S3-on-V4 hom cluster:
-- act-on-canonical n h ≡ rot-pow n ∘ swap-pow h, each an iterate of one
-- generator, so its homomorphism property follows from the generators'.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.IsHomomorphism.Compose where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)

-- The identity is a homomorphism.
id-IsHom : IsHomomorphism (λ v → v)
id-IsHom _ _ = refl

-- Homomorphisms compose: (f ∘ g) preserves · when f and g do.
--   (f∘g)(v₁·v₂) = f (g (v₁·v₂)) ≡ f (g v₁ · g v₂)   [g hom, cong f]
--                ≡ f (g v₁) · f (g v₂)               [f hom]
∘-IsHom : {f g : V₄ → V₄} →
          IsHomomorphism f → IsHomomorphism g →
          IsHomomorphism (λ v → f (g v))
∘-IsHom {f} {g} f-hom g-hom v₁ v₂ =
  trans (cong f (g-hom v₁ v₂)) (f-hom (g v₁) (g v₂))
