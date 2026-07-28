------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.xFreeCyclic
--
-- Tier 2 capability record for the Zₙ × FreeCyclic 2-D word algebra
-- (Substrate.Groups.Zn-x-FreeCyclic's parameter list).
--
-- After the canonical-is-fixed rename pass, all Zₙ field names are
-- uniform; `from-coxeter-data` takes only the per-Zₙ data. Per-Zₙ
-- witnesses are one-line applications.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.xFreeCyclic where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.Coxeter.Word using (Word; _++_)

------------------------------------------------------------------------
-- The capability record.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize the Set carrier (Zn-Word) AND the family
-- (Zn-Canonical : Zn-Word → Set) out of the record — both were `field`s
-- valued in Set, forcing the record to Set₁. As module parameters the record
-- lands in Set; consumers write `xFreeCyclicCapability Zn-Word Zn-Canonical`.
open import Substrate.Groups.Coxeter.Word using ([])
module _ (Zn-Word : Set) (Zn-Canonical : Zn-Word → Set) where

  record xFreeCyclicCapability : Set where
    field
      _Zn-++_              : Zn-Word → Zn-Word → Zn-Word
      Zn-ε                 : Zn-Word
      Zn-++-assoc          : (a b c : Zn-Word) →
                             (a Zn-++ b) Zn-++ c ≡ a Zn-++ (b Zn-++ c)
      Zn-normalize         : Zn-Word → Zn-Word
      Zn-normalize-canonical : (w : Zn-Word) → Zn-Canonical (Zn-normalize w)
      Zn-canonical-is-fixed  : {w : Zn-Word} → Zn-Canonical w → Zn-normalize w ≡ w
      Zn-normalize-distrib   : (a b : Zn-Word) →
                               Zn-normalize (a Zn-++ b) ≡
                               Zn-normalize (Zn-normalize a Zn-++ Zn-normalize b)

------------------------------------------------------------------------
-- from-coxeter-data: build the capability from a Coxeter instance.
------------------------------------------------------------------------


from-coxeter-data :
  (Gen : Set)
  (++-assoc : (a b c : Word Gen) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (Canonical : Word Gen → Set)
  (normalize : Word Gen → Word Gen)
  (normalize-canonical : (w : Word Gen) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w)
  (normalize-distrib : (a b : Word Gen) →
                       normalize (a ++ b) ≡
                       normalize (normalize a ++ normalize b)) →
  xFreeCyclicCapability (Word Gen) Canonical
from-coxeter-data Gen assoc Can norm norm-can can-fix distrib = record
  { _Zn-++_                = _++_
  ; Zn-ε                   = []
  ; Zn-++-assoc            = assoc
  ; Zn-normalize           = norm
  ; Zn-normalize-canonical = norm-can
  ; Zn-canonical-is-fixed  = can-fix
  ; Zn-normalize-distrib   = distrib
  }
