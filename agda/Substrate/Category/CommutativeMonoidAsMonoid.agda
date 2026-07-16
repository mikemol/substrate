------------------------------------------------------------------------
-- Substrate.Category.CommutativeMonoidAsMonoid
--
-- Bridges the two PARALLEL "commutative monoid" representations the substrate
-- carries: the standalone `Category.CommutativeMonoid` record (R, +R, 0R, with
-- its own assoc/identity/comm laws) and the layered `Algebra.Monoid`
-- (Semigroup→Magma + ε + identity laws). A Category-side commutative monoid IS
-- an Algebra-side Monoid -- repackaging the same carrier/op/laws.
--
-- NOTE (test-the-wall, correcting an earlier note): the relation is FORGETFUL
-- (CommMonoid → Monoid), NOT an isomorphism — `Algebra.Monoid` has no
-- commutativity field, so the reverse needs an extra `+R-comm` the bare Monoid
-- cannot supply. So there is no `Monoid ≅ CommMonoid`; a comm monoid is a monoid.
--
-- Composing with `Delooping.deloop`, a Category.CommutativeMonoid is therefore
-- also on the categorical spine (its one-object delooping). A leaf bridge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeMonoidAsMonoid where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping using (deloop)

open CommutativeMonoid   -- opens the law projections (+R-assoc/+R-identityˡ/ʳ/comm); R/_+R_/0R are now params

-- the forgetful bridge: a commutative monoid is a monoid. ⟡set1-rp-commmonoid: the carrier
-- R / op _+R_ / unit 0R are now the record's PARAMETERS (inferred from C's type), not projections.
commMonoid→Monoid : {R : Set 0ℓ} {_+R_ : R → R → R} {0R : R}
                  → CommutativeMonoid R _+R_ 0R → Monoid R
commMonoid→Monoid {_} {_+R_} {0R} C = record
  { semigroup = record
      { magma   = record { _·_ = _+R_ }
      ; ·-assoc = +R-assoc C
      }
  ; ε       = 0R
  ; ε-left  = +R-identityˡ C
  ; ε-right = +R-identityʳ C
  }

-- ... hence on the categorical spine, via the Monoid delooping.
commMonoid→CategoryOf : {R : Set 0ℓ} {_+R_ : R → R → R} {0R : R}
                      → CommutativeMonoid R _+R_ 0R → CategoryOf
commMonoid→CategoryOf C = deloop (commMonoid→Monoid C)
