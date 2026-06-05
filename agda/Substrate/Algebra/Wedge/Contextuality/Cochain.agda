------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality.Cochain
--
-- The connecting map `_⊕ᶜ_` on parity constraints is an ABELIAN GROUP — the
-- F₂ vector space of 1-cochains. This is what makes the obstruction a genuine
-- cohomology element rather than a one-off witness: constraints add (XOR),
-- with `𝟬ᶜ = (𝟎ⱽ, 𝟘)` the zero cochain, every cochain its own inverse
-- (characteristic 2), and satisfaction a group action read.
--
-- All laws lift the F₂ / Vector laws componentwise (cong₂ con), so each is one
-- line. Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality.Cochain where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2
  using (F₂; 𝟘; _+_; +-identityˡ; +-identityʳ; +-comm; +-assoc; +-self-inverse)
open import Substrate.Algebra.F2.Vector
  using (Vector; 𝟎ⱽ; _+ⱽ_; +ⱽ-identityˡ; +ⱽ-identityʳ; +ⱽ-comm; +ⱽ-assoc; +ⱽ-self-inverse)
open import Substrate.Algebra.Wedge.Contextuality
  using (Constraint; con; lhs; rhs; _⊕ᶜ_; satisfies; inner-zero)

------------------------------------------------------------------------
-- 1. The zero cochain.
------------------------------------------------------------------------

𝟬ᶜ : ∀ {n} → Constraint n
𝟬ᶜ = con 𝟎ⱽ 𝟘

------------------------------------------------------------------------
-- 2–6. Abelian group laws (componentwise lifts).
------------------------------------------------------------------------

⊕ᶜ-identityˡ : ∀ {n} (c : Constraint n) → (𝟬ᶜ ⊕ᶜ c) ≡ c
⊕ᶜ-identityˡ c = cong₂ con (+ⱽ-identityˡ (lhs c)) (+-identityˡ (rhs c))

⊕ᶜ-identityʳ : ∀ {n} (c : Constraint n) → (c ⊕ᶜ 𝟬ᶜ) ≡ c
⊕ᶜ-identityʳ c = cong₂ con (+ⱽ-identityʳ (lhs c)) (+-identityʳ (rhs c))

⊕ᶜ-comm : ∀ {n} (c₁ c₂ : Constraint n) → (c₁ ⊕ᶜ c₂) ≡ (c₂ ⊕ᶜ c₁)
⊕ᶜ-comm c₁ c₂ = cong₂ con (+ⱽ-comm (lhs c₁) (lhs c₂)) (+-comm (rhs c₁) (rhs c₂))

⊕ᶜ-assoc : ∀ {n} (c₁ c₂ c₃ : Constraint n) →
           ((c₁ ⊕ᶜ c₂) ⊕ᶜ c₃) ≡ (c₁ ⊕ᶜ (c₂ ⊕ᶜ c₃))
⊕ᶜ-assoc c₁ c₂ c₃ =
  cong₂ con (+ⱽ-assoc (lhs c₁) (lhs c₂) (lhs c₃))
            (+-assoc (rhs c₁) (rhs c₂) (rhs c₃))

-- characteristic 2: every cochain is its own inverse.
⊕ᶜ-self-inverse : ∀ {n} (c : Constraint n) → (c ⊕ᶜ c) ≡ 𝟬ᶜ
⊕ᶜ-self-inverse c = cong₂ con (+ⱽ-self-inverse (lhs c)) (+-self-inverse (rhs c))

------------------------------------------------------------------------
-- 7–9. Consequences: cancel-the-double, and left/right cancellation.
------------------------------------------------------------------------

⊕ᶜ-double : ∀ {n} (c d : Constraint n) → ((c ⊕ᶜ d) ⊕ᶜ d) ≡ c
⊕ᶜ-double c d =
  trans (⊕ᶜ-assoc c d d)
        (trans (cong (c ⊕ᶜ_) (⊕ᶜ-self-inverse d)) (⊕ᶜ-identityʳ c))

⊕ᶜ-cancelˡ : ∀ {n} (c a b : Constraint n) → (c ⊕ᶜ a) ≡ (c ⊕ᶜ b) → a ≡ b
⊕ᶜ-cancelˡ c a b eq =
  trans (sym (⊕ᶜ-identityˡ a))
  (trans (cong (_⊕ᶜ a) (sym (⊕ᶜ-self-inverse c)))
  (trans (⊕ᶜ-assoc c c a)
  (trans (cong (c ⊕ᶜ_) eq)
  (trans (sym (⊕ᶜ-assoc c c b))
  (trans (cong (_⊕ᶜ b) (⊕ᶜ-self-inverse c))
         (⊕ᶜ-identityˡ b))))))

⊕ᶜ-cancelʳ : ∀ {n} (c a b : Constraint n) → (a ⊕ᶜ c) ≡ (b ⊕ᶜ c) → a ≡ b
⊕ᶜ-cancelʳ c a b eq =
  ⊕ᶜ-cancelˡ c a b (trans (⊕ᶜ-comm c a) (trans eq (⊕ᶜ-comm b c)))

------------------------------------------------------------------------
-- 10. The zero cochain is satisfied by every assignment (the group acts).
------------------------------------------------------------------------

𝟬ᶜ-satisfied : ∀ {n} (s : Vector n) → satisfies s 𝟬ᶜ
𝟬ᶜ-satisfied s = inner-zero s
