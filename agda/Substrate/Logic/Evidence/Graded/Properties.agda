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

open import Substrate.Foundation.Eq using (_≡_; cong₂)

open import Substrate.Logic.Evidence.Verdict using (Evidence; _∧E_; _∨E_)
open import Substrate.Logic.Evidence.Verdict.Properties using (∧E-comm; ∨E-comm)
open import Substrate.Logic.Evidence.Warrant using (Warrant; _⊓w_)
open import Substrate.Logic.Evidence.Warrant.Properties using (⊓w-comm)
open import Substrate.Logic.Evidence.Graded

∧G-comm : (x y : GradedEvidence) → x ∧G y ≡ y ∧G x
∧G-comm (a at g) (b at h) = cong₂ _at_ (∧E-comm a b) (⊓w-comm g h)

∨G-comm : (x y : GradedEvidence) → x ∨G y ≡ y ∨G x
∨G-comm (a at g) (b at h) = cong₂ _at_ (∨E-comm a b) (⊓w-comm g h)
