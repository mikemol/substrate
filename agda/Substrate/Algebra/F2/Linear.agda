------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear
--
-- M-3 of the Cocycles structural-migration plan. F₂-linear maps
-- between fixed-length F₂-vector spaces, packaged as records bundling
-- the apply function with its linearity proofs.
--
-- This file's scope is the operational layer: Linear records,
-- identity, composition, derived preserves-𝟎. The extensionality
-- theorem ("two linear maps are equal iff they agree on basis
-- vectors") is M-3.5 (Substrate.Algebra.F2.Linear.Universal).
--
-- Convention: linear maps go between Vec F₂ n and Vec F₂ m for
-- arbitrary n, m. Linear maps to/from more general F₂-modules can
-- be added later if a consumer needs them; the present scope is
-- fixed to vectors to keep the API small.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Function using (id; _∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector

------------------------------------------------------------------------
-- F₂-linear map: record bundling apply + linearity proofs.
------------------------------------------------------------------------

record Linear (n m : ℕ) : Set where
  field
    apply         : Vector n → Vector m
    preserves-+   : (u v : Vector n) → apply (u +ⱽ v) ≡ apply u +ⱽ apply v
    preserves-*ₛ  : (c : F₂) (v : Vector n) → apply (c *ₛ v) ≡ c *ₛ apply v

open Linear public

------------------------------------------------------------------------
-- Derived: every linear map sends 𝟎ⱽ to 𝟎ⱽ.
--
-- Proof: 𝟎ⱽ ≡ 𝟘 *ₛ 𝟎ⱽ by absorption; apply respects *ₛ; 𝟘 *ₛ x ≡ 𝟎ⱽ.
------------------------------------------------------------------------

preserves-𝟎 : ∀ {n m} (L : Linear n m) → apply L 𝟎ⱽ ≡ 𝟎ⱽ
preserves-𝟎 L =
  trans (cong (apply L) (sym (*ₛ-absorbˡ 𝟎ⱽ)))
        (trans (preserves-*ₛ L 𝟘 𝟎ⱽ)
               (*ₛ-absorbˡ (apply L 𝟎ⱽ)))

------------------------------------------------------------------------
-- Identity linear map.
------------------------------------------------------------------------

id-L : ∀ {n} → Linear n n
id-L = record
  { apply        = id
  ; preserves-+  = λ _ _ → refl
  ; preserves-*ₛ = λ _ _ → refl
  }

------------------------------------------------------------------------
-- Composition: linear-map composition.
--
-- (L ∘L M) sends v to L (M v); inherits linearity from both factors.
-- Convention: L ∘L M is "M then L" (matches function composition).
------------------------------------------------------------------------

infixr 9 _∘L_

_∘L_ : ∀ {n m k} → Linear m k → Linear n m → Linear n k
L ∘L M = record
  { apply        = apply L ∘ apply M
  ; preserves-+  = λ u v →
      trans (cong (apply L) (preserves-+ M u v))
            (preserves-+ L (apply M u) (apply M v))
  ; preserves-*ₛ = λ c v →
      trans (cong (apply L) (preserves-*ₛ M c v))
            (preserves-*ₛ L c (apply M v))
  }

------------------------------------------------------------------------
-- Derived: composition with id-L.
------------------------------------------------------------------------

∘L-identityˡ : ∀ {n m} (L : Linear n m) (v : Vector n) →
               apply (id-L ∘L L) v ≡ apply L v
∘L-identityˡ _ _ = refl

∘L-identityʳ : ∀ {n m} (L : Linear n m) (v : Vector n) →
               apply (L ∘L id-L) v ≡ apply L v
∘L-identityʳ _ _ = refl

∘L-assoc : ∀ {n m k l}
           (L : Linear k l) (M : Linear m k) (N : Linear n m) (v : Vector n) →
           apply ((L ∘L M) ∘L N) v ≡ apply (L ∘L (M ∘L N)) v
∘L-assoc _ _ _ _ = refl
