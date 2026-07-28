------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.CoxeterGroup
--
-- Tier 2 capability record for the Coxeter-as-Group lift
-- (Substrate.Groups.Coxeter.GroupAdapter's parameter list).
--
-- Every Coxeter Word instance shares the Word / _++_ / [] /
-- ++-identity-left / ++-identity-right machinery. Only Gen,
-- ++-assoc, Canonical, c-ε, normalize + normalize-canonical +
-- canonical-is-fixed + normalize-distrib, and the inv quartet
-- (inv, inv-canonical, inv-left-canonical, inv-right-canonical) vary
-- per Zₙ. `from-coxeter-data` packages the shape; per-Zₙ witnesses
-- are one-line applications.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.CoxeterGroup where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.Coxeter.Word using (Word; _++_; [])

------------------------------------------------------------------------
-- The capability record.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize the Set carrier (Gen) AND the family
-- (Canonical : Word Gen → Set) out of the record — both were `field`s valued
-- in Set, forcing the record to Set₁. As module parameters the record lands
-- in Set; consumers write `CoxeterGroupCapability Gen Canonical`.
module _ (Gen : Set) (Canonical : Word Gen → Set) where

  record CoxeterGroupCapability : Set where
    field
      c-ε                : Canonical []
      ++-assoc           : (a b c : Word Gen) → (a ++ b) ++ c ≡ a ++ (b ++ c)
      normalize          : Word Gen → Word Gen
      normalize-canonical : (w : Word Gen) → Canonical (normalize w)
      canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
      normalize-distrib  : (a b : Word Gen) →
                           normalize (a ++ b) ≡
                           normalize (normalize a ++ normalize b)
      inv                : Word Gen → Word Gen
      inv-canonical      : {w : Word Gen} → Canonical w → Canonical (inv w)
      inv-left-canonical : {w : Word Gen} → Canonical w → normalize (inv w ++ w) ≡ []
      inv-right-canonical : {w : Word Gen} → Canonical w → normalize (w ++ inv w) ≡ []
