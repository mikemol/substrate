------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Graded.Properties
--
-- The graded joiners inherit their laws componentwise: GradedEvidence is
-- the PRODUCT of the evidence semilattice (Verdict.Properties) and the
-- warrant semilattice (Warrant.Properties), so each law of `_∧G_` / `_∨G_`
-- is the pairing (cong₂ _at_) of the corresponding evidence law and warrant
-- law. Commutativity is shown here as the representative; associativity and
-- idempotence follow the identical product pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Graded.Properties where

open import Substrate.Foundation.Eq using (_≡_; trans; cong₂)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)

open import Substrate.Logic.Evidence.Verdict using (Evidence; _∧E_; _∨E_; ⊤t; ⊥t)
open import Substrate.Logic.Evidence.Verdict.Properties
  using (∧E-comm; ∨E-comm; ∧E-assoc; ∨E-assoc; ∧E-identityʳ; ∨E-identityʳ)
open import Substrate.Logic.Evidence.Warrant using (Warrant; _⊓w_; ⊤w)
open import Substrate.Logic.Evidence.Warrant.Properties using (⊓w-comm; ⊓w-assoc; ⊓w-identityʳ)
open import Substrate.Logic.Evidence.Graded

∧G-comm : (x y : GradedEvidence) → x ∧G y ≡ y ∧G x
∧G-comm (a at g) (b at h) = cong₂ _at_ (∧E-comm a b) (⊓w-comm g h)

∨G-comm : (x y : GradedEvidence) → x ∨G y ≡ y ∨G x
∨G-comm (a at g) (b at h) = cong₂ _at_ (∨E-comm a b) (⊓w-comm g h)

∧G-assoc : (x y z : GradedEvidence) → (x ∧G y) ∧G z ≡ x ∧G (y ∧G z)
∧G-assoc (a at g) (b at h) (c at k) = cong₂ _at_ (∧E-assoc a b c) (⊓w-assoc g h k)

∨G-assoc : (x y z : GradedEvidence) → (x ∨G y) ∨G z ≡ x ∨G (y ∨G z)
∨G-assoc (a at g) (b at h) (c at k) = cong₂ _at_ (∨E-assoc a b c) (⊓w-assoc g h k)

-- units: the product of each factor's unit — ∧G ↦ (⊤t at ⊤w), ∨G ↦ (⊥t at ⊤w).
∧G-identityʳ : (x : GradedEvidence) → x ∧G (⊤t at ⊤w) ≡ x
∧G-identityʳ (a at g) = cong₂ _at_ (∧E-identityʳ a) (⊓w-identityʳ g)

∨G-identityʳ : (x : GradedEvidence) → x ∨G (⊥t at ⊤w) ≡ x
∨G-identityʳ (a at g) = cong₂ _at_ (∨E-identityʳ a) (⊓w-identityʳ g)

------------------------------------------------------------------------
-- GROUNDED: each graded joiner IS a `Category.CommutativeMonoid` — the
-- PRODUCT of the evidence factor and the warrant factor (GradedEvidence =
-- Evidence × Warrant). identityˡ = comm ∘ identityʳ.
------------------------------------------------------------------------

∧G-CommutativeMonoid : CommutativeMonoid _
∧G-CommutativeMonoid = record
  { R = GradedEvidence ; _+R_ = _∧G_ ; 0R = ⊤t at ⊤w
  ; +R-assoc = ∧G-assoc
  ; +R-identityˡ = λ x → trans (∧G-comm (⊤t at ⊤w) x) (∧G-identityʳ x)
  ; +R-identityʳ = ∧G-identityʳ ; +R-comm = ∧G-comm }

∨G-CommutativeMonoid : CommutativeMonoid _
∨G-CommutativeMonoid = record
  { R = GradedEvidence ; _+R_ = _∨G_ ; 0R = ⊥t at ⊤w
  ; +R-assoc = ∨G-assoc
  ; +R-identityˡ = λ x → trans (∨G-comm (⊥t at ⊤w) x) (∨G-identityʳ x)
  ; +R-identityʳ = ∨G-identityʳ ; +R-comm = ∨G-comm }
