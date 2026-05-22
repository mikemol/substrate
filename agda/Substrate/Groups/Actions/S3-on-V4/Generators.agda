------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators
--
-- Generator-level structure for the dihedral decomposition of act-∙:
--   rotate, swap-αβ — V₄-automorphism generators
--   rot-pow, swap-pow — recursive power functions
--   rot-pow-append, swap-pow-append — append composes
--   rotate³-id, swap-αβ²-id — generator-order identities
--   rot-pow-normalize-eq, swap-pow-normalize-eq — power respects normalize
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

------------------------------------------------------------------------
-- Generators: rotate and swap-αβ extracted from act-on-canonical.
------------------------------------------------------------------------

rotate : V₄ → V₄
rotate e = e
rotate α = β
rotate β = γ
rotate γ = α

swap-αβ : V₄ → V₄
swap-αβ e = e
swap-αβ α = β
swap-αβ β = α
swap-αβ γ = γ

------------------------------------------------------------------------
-- Power functions.
------------------------------------------------------------------------

rot-pow : Word Z₃.Gen → V₄ → V₄
rot-pow []           v = v
rot-pow (Z₃.a ∷ w)   v = rotate (rot-pow w v)

swap-pow : Word Z₂.Gen → V₄ → V₄
swap-pow []         v = v
swap-pow (Z₂.a ∷ w) v = swap-αβ (swap-pow w v)

------------------------------------------------------------------------
-- Append composes (strict, by induction on first arg).
------------------------------------------------------------------------

rot-pow-append : (w₁ w₂ : Word Z₃.Gen) (v : V₄) →
                 rot-pow (w₁ ++ w₂) v ≡ rot-pow w₁ (rot-pow w₂ v)
rot-pow-append []           w₂ v = refl
rot-pow-append (Z₃.a ∷ w₁)  w₂ v = cong rotate (rot-pow-append w₁ w₂ v)

swap-pow-append : (w₁ w₂ : Word Z₂.Gen) (v : V₄) →
                  swap-pow (w₁ ++ w₂) v ≡ swap-pow w₁ (swap-pow w₂ v)
swap-pow-append []          w₂ v = refl
swap-pow-append (Z₂.a ∷ w₁) w₂ v = cong swap-αβ (swap-pow-append w₁ w₂ v)

------------------------------------------------------------------------
-- Generator-order identities.
------------------------------------------------------------------------

rotate³-id : (v : V₄) → rotate (rotate (rotate v)) ≡ v
rotate³-id e = refl
rotate³-id α = refl
rotate³-id β = refl
rotate³-id γ = refl

swap-αβ²-id : (v : V₄) → swap-αβ (swap-αβ v) ≡ v
swap-αβ²-id e = refl
swap-αβ²-id α = refl
swap-αβ²-id β = refl
swap-αβ²-id γ = refl

------------------------------------------------------------------------
-- Power respects normalize.
------------------------------------------------------------------------

rot-pow-normalize-eq : (w : Word Z₃.Gen) (v : V₄) →
                       rot-pow w v ≡ rot-pow (Z₃.normalize w) v
rot-pow-normalize-eq []         v = refl
rot-pow-normalize-eq (Z₃.a ∷ w) v =
  trans (cong rotate (rot-pow-normalize-eq w v))
        (rot-step (Z₃.normalize-canonical w) v)
  where
    rot-step : ∀ {x} → Z₃.Canonical x → (v : V₄) →
               rotate (rot-pow x v) ≡ rot-pow (Z₃.insert Z₃.a x) v
    rot-step Z₃.c-ε  _ = refl
    rot-step Z₃.c-a  _ = refl
    rot-step Z₃.c-aa v = rotate³-id v

swap-pow-normalize-eq : (w : Word Z₂.Gen) (v : V₄) →
                        swap-pow w v ≡ swap-pow (Z₂.normalize w) v
swap-pow-normalize-eq []         v = refl
swap-pow-normalize-eq (Z₂.a ∷ w) v =
  trans (cong swap-αβ (swap-pow-normalize-eq w v))
        (swap-step (Z₂.normalize-canonical w) v)
  where
    swap-step : ∀ {x} → Z₂.Canonical x → (v : V₄) →
                swap-αβ (swap-pow x v) ≡ swap-pow (Z₂.insert Z₂.a x) v
    swap-step Z₂.c-ε _ = refl
    swap-step Z₂.c-a v = swap-αβ²-id v
