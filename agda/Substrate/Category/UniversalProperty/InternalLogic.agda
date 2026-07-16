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

open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂; [_,_])
open import Substrate.Foundation.Eq using (_≡_; subst; sym)
open import Substrate.Category.UniversalProperty.Term using (UPTerm; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Category using (++ᵤ-assoc)
open import Substrate.Category.UniversalProperty.Sieve
  using (Sieve; max-Sieve; member; closure)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Logical-connective signatures at the sieve level.
  -- ⟡ta-upterm: objects are the Set₀ alphabet O; (O, Hom) via the section.
  ------------------------------------------------------------------------

  ⊤-sieve : (U : O) → Sieve O Hom U
  ⊤-sieve U = max-Sieve O Hom U

  -- ⊥ : the empty sieve (nothing is a member); vacuously closed.
  ⊥-sieve : (U : O) → Sieve O Hom U
  ⊥-sieve U = record { member = λ _ → ⊥ ; closure = λ _ _ () }

  -- ∧ : pointwise intersection of two sieves.
  ∧-sieve : (U : O) → Sieve O Hom U → Sieve O Hom U → Sieve O Hom U
  ∧-sieve U S T = record
    { member  = λ t → member S t × member T t
    ; closure = λ t u m → (closure S t u (proj₁ m) , closure T t u (proj₂ m))
    }

  -- ∨ : pointwise union of two sieves.
  ∨-sieve : (U : O) → Sieve O Hom U → Sieve O Hom U → Sieve O Hom U
  ∨-sieve U S T = record
    { member  = λ t → member S t ⊎ member T t
    ; closure = λ t u → [ (λ ms → inj₁ (closure S t u ms)) , (λ mt → inj₂ (closure T t u mt)) ]
    }

  -- ⇒ : Heyting implication ("extends to": every precomposition landing in S lands in T).
  ⇒-sieve : (U : O) → Sieve O Hom U → Sieve O Hom U → Sieve O Hom U
  ⇒-sieve U S T = record
    { member  = λ {V} t → {W : O} (u : UPTerm O Hom W V) → member S (u ++ᵤ t) → member T (u ++ᵤ t)
    ; closure = λ t u f u' mS →
        subst (member T) (++ᵤ-assoc u' u t)
              (f (u' ++ᵤ u) (subst (member S) (sym (++ᵤ-assoc u' u t)) mS))
    }

  -- ¬ : pseudo-complement = ⇒ ⊥.
  ¬-sieve : (U : O) → Sieve O Hom U → Sieve O Hom U
  ¬-sieve U S = ⇒-sieve U S (⊥-sieve U)

------------------------------------------------------------------------
-- 2. Capstone for UP34.
--
-- Internal-logic surface lands as obligations. UP35-UP40 close
-- the topos arc.
------------------------------------------------------------------------
