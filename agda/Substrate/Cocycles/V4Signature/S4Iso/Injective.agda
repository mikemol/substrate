------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.Injective
--
-- Bijection-helper lemmas: σ-injective and Axis-constructor
-- distinctness lemmas (C≢D, S≢D, W≢D, C≢S, C≢W, S≢W, and reverses).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.Injective where

open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4
  using (Permutation; inv-l)
  renaming (apply to applyₛ; invₐ to invₐₛ)

------------------------------------------------------------------------
-- apply σ is injective.
------------------------------------------------------------------------

σ-injective :
  (σ : Permutation) (x y : Axis) →
  applyₛ σ x ≡ applyₛ σ y → x ≡ y
σ-injective σ x y eq =
  let
    p₁ : x ≡ invₐₛ σ (applyₛ σ x)
    p₁ = sym (inv-l σ x)
    p₂ : invₐₛ σ (applyₛ σ x) ≡ invₐₛ σ (applyₛ σ y)
    p₂ = cong (invₐₛ σ) eq
    p₃ : invₐₛ σ (applyₛ σ y) ≡ y
    p₃ = inv-l σ y
  in trans p₁ (trans p₂ p₃)

------------------------------------------------------------------------
-- Axis-constructor distinctness (nine obvious lemmas).
------------------------------------------------------------------------

C≢D : C ≡ D → ⊥
C≢D ()
S≢D : S ≡ D → ⊥
S≢D ()
W≢D : W ≡ D → ⊥
W≢D ()
C≢S : C ≡ S → ⊥
C≢S ()
C≢W : C ≡ W → ⊥
C≢W ()
S≢W : S ≡ W → ⊥
S≢W ()
S≢C : S ≡ C → ⊥
S≢C ()
W≢C : W ≡ C → ⊥
W≢C ()
W≢S : W ≡ S → ⊥
W≢S ()
