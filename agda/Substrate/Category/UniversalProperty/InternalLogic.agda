------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.InternalLogic
--
-- UP34 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The internal-logic surface of the UP-topos.
--
-- The Sieve-valued truth values form a Heyting algebra:
--   ⊤   = max-Sieve
--   ⊥   = empty sieve
--   ∧   = pointwise intersection of sieves
--   ∨   = pointwise union (cover-closure)
--   ⇒   = "extends to" operation
--   ¬   = pseudo-complement
--
-- The five connectives now LAND as real Sieve operations (⊤ = max-Sieve,
-- ⊥ = empty sieve, ∧ = intersection, ∨ = union, ⇒ = Heyting implication
-- via ++ᵤ-assoc, ¬ = ⇒ ⊥) — replacing the former `-stated : Set₁ = Set`
-- obligation stubs (⟡set1-ra-internallogic). The Heyting-algebra AXIOMS
-- (commutativity / absorption / distributivity of these operations) remain
-- the recorded obligation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.InternalLogic where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂; [_,_])
open import Substrate.Foundation.Eq using (_≡_; subst; sym)
open import Substrate.Category.UniversalProperty.Term using (UPTerm; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Category using (++ᵤ-assoc)
open import Substrate.Category.UniversalProperty.Sieve
  using (Sieve; max-Sieve; closure)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Logical-connective signatures at the sieve level.
  -- ⟡ta-upterm: objects are the Set₀ alphabet O; (O, Hom) via the section.
  -- ⟡rc-topos (⟡set1-rerank2): `member` is now a Sieve PARAMETER — every
  -- connective lifts its member predicate into the return type.
  ------------------------------------------------------------------------

  ⊤-sieve : (U : O) → Sieve O Hom U (λ _ → ⊤)
  ⊤-sieve U = max-Sieve O Hom U

  -- ⊥ : the empty sieve (nothing is a member); vacuously closed.
  ⊥-sieve : (U : O) → Sieve O Hom U (λ _ → ⊥)
  ⊥-sieve U = record { closure = λ _ _ () }

  -- ∧ : pointwise intersection of two sieves.
  ∧-sieve : (U : O) {mS mT : {V : O} → UPTerm O Hom V U → Set} →
            Sieve O Hom U mS → Sieve O Hom U mT → Sieve O Hom U (λ t → mS t × mT t)
  ∧-sieve U S T = record
    { closure = λ t u m → (closure S t u (proj₁ m) , closure T t u (proj₂ m))
    }

  -- ∨ : pointwise union of two sieves.
  ∨-sieve : (U : O) {mS mT : {V : O} → UPTerm O Hom V U → Set} →
            Sieve O Hom U mS → Sieve O Hom U mT → Sieve O Hom U (λ t → mS t ⊎ mT t)
  ∨-sieve U S T = record
    { closure = λ t u → [ (λ ms → inj₁ (closure S t u ms)) , (λ mt → inj₂ (closure T t u mt)) ]
    }

  -- ⇒ : Heyting implication ("extends to": every precomposition landing in S lands in T).
  ⇒-sieve : (U : O) {mS mT : {V : O} → UPTerm O Hom V U → Set} →
            Sieve O Hom U mS → Sieve O Hom U mT →
            Sieve O Hom U (λ {V} t → {W : O} (u : UPTerm O Hom W V) → mS (u ++ᵤ t) → mT (u ++ᵤ t))
  ⇒-sieve U {mS} {mT} S T = record
    { closure = λ t u f u' p →
        subst mT (++ᵤ-assoc u' u t)
              (f (u' ++ᵤ u) (subst mS (sym (++ᵤ-assoc u' u t)) p))
    }

  -- ¬ : pseudo-complement = ⇒ ⊥.
  ¬-sieve : (U : O) {mS : {V : O} → UPTerm O Hom V U → Set} → Sieve O Hom U mS →
            Sieve O Hom U (λ {V} t → {W : O} (u : UPTerm O Hom W V) → mS (u ++ᵤ t) → ⊥)
  ¬-sieve U S = ⇒-sieve U S (⊥-sieve U)

------------------------------------------------------------------------
-- 2. Capstone for UP34.
--
-- Internal-logic surface lands as obligations. UP35-UP40 close
-- the topos arc.
------------------------------------------------------------------------
