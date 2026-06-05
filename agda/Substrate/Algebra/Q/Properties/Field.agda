------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Field
--
-- The ℚ field laws, discharged over the SEMANTIC equality `_≈ℚ_`
-- (cross-multiplication; Substrate.Algebra.Q.Equiv). Over `≈ℚ` the inverse
-- laws are TRUE (they are syntactically false on the unreduced `_≡_`: 0/b² ≢
-- 0/1). The numerator arithmetic uses the canonical ℤ ring laws
-- (Z.Properties.{Mul,MulFull}); denominators are products of `suc _`, whose
-- `(_ ∸ 1)` un-truncates by refl. Carriers matched as `mkℚ` so num/den-1 are
-- concrete (no record-eta stalls).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Field where

open import Substrate.Foundation.Nat using (suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-comm; *-assoc; *-identityˡ; *-identityʳ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left; *ℤ-comm)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-identityˡ; *ℤ-identityʳ; *ℤ-zeroˡ; *ℤ-zeroʳ)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-comm; +ℤ-identityˡ; +ℤ-identityʳ; +ℤ-inverseˡ; +ℤ-inverseʳ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Arithmetic using (_+ℚ_; _*ℚ_; -ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- Commutativity.
------------------------------------------------------------------------

+ℚ-comm : (a b : ℚ) → (a +ℚ b) ≈ℚ (b +ℚ a)
+ℚ-comm (mkℚ na da₋) (mkℚ nb db₋) =
  cong₂ _*ℤ_
    (+ℤ-comm (na *ℤ (+ suc db₋)) (nb *ℤ (+ suc da₋)))
    (cong +_ (*-comm (suc db₋) (suc da₋)))

*ℚ-comm : (a b : ℚ) → (a *ℚ b) ≈ℚ (b *ℚ a)
*ℚ-comm (mkℚ na da₋) (mkℚ nb db₋) =
  cong₂ _*ℤ_ (*ℤ-comm na nb) (cong +_ (*-comm (suc db₋) (suc da₋)))

------------------------------------------------------------------------
-- Multiplicative associativity.
------------------------------------------------------------------------

*ℚ-assoc : (a b c : ℚ) → ((a *ℚ b) *ℚ c) ≈ℚ (a *ℚ (b *ℚ c))
*ℚ-assoc (mkℚ na da₋) (mkℚ nb db₋) (mkℚ nc dc₋) =
  cong₂ _*ℤ_
    (*ℤ-assoc na nb nc)
    (cong +_ (sym (*-assoc (suc da₋) (suc db₋) (suc dc₋))))

------------------------------------------------------------------------
-- Identity.
------------------------------------------------------------------------

+ℚ-identityˡ : (a : ℚ) → (0ℚ +ℚ a) ≈ℚ a
+ℚ-identityˡ (mkℚ na da₋) =
  cong₂ _*ℤ_
    (trans (+ℤ-identityˡ (na *ℤ (+ 1))) (*ℤ-identityʳ na))
    (cong +_ (sym (*-identityˡ (suc da₋))))

+ℚ-identityʳ : (a : ℚ) → (a +ℚ 0ℚ) ≈ℚ a
+ℚ-identityʳ (mkℚ na da₋) =
  cong₂ _*ℤ_
    (trans (+ℤ-identityʳ (na *ℤ (+ 1))) (*ℤ-identityʳ na))
    (cong +_ (sym (*-identityʳ (suc da₋))))

*ℚ-identityˡ : (a : ℚ) → (1ℚ *ℚ a) ≈ℚ a
*ℚ-identityˡ (mkℚ na da₋) =
  cong₂ _*ℤ_ (*ℤ-identityˡ na) (cong +_ (sym (*-identityˡ (suc da₋))))

*ℚ-identityʳ : (a : ℚ) → (a *ℚ 1ℚ) ≈ℚ a
*ℚ-identityʳ (mkℚ na da₋) =
  cong₂ _*ℤ_ (*ℤ-identityʳ na) (cong +_ (sym (*-identityʳ (suc da₋))))

------------------------------------------------------------------------
-- Zero absorption.
------------------------------------------------------------------------

zero-absorbˡ : (a : ℚ) → (0ℚ *ℚ a) ≈ℚ 0ℚ
zero-absorbˡ (mkℚ na da₋) = cong (_*ℤ (+ 1)) (*ℤ-zeroˡ na)

zero-absorbʳ : (a : ℚ) → (a *ℚ 0ℚ) ≈ℚ 0ℚ
zero-absorbʳ (mkℚ na da₋) = cong (_*ℤ (+ 1)) (*ℤ-zeroʳ na)

------------------------------------------------------------------------
-- Additive inverses (TRUE over ≈ℚ; syntactically false over ≡).
------------------------------------------------------------------------

+ℚ-inverseˡ : (a : ℚ) → ((-ℚ a) +ℚ a) ≈ℚ 0ℚ
+ℚ-inverseˡ (mkℚ na da₋) =
  cong (_*ℤ (+ 1))
    (trans (cong (_+ℤ (na *ℤ (+ suc da₋))) (neg-*-left na (+ suc da₋)))
           (+ℤ-inverseˡ (na *ℤ (+ suc da₋))))

+ℚ-inverseʳ : (a : ℚ) → (a +ℚ (-ℚ a)) ≈ℚ 0ℚ
+ℚ-inverseʳ (mkℚ na da₋) =
  cong (_*ℤ (+ 1))
    (trans (cong ((na *ℤ (+ suc da₋)) +ℤ_) (neg-*-left na (+ suc da₋)))
           (+ℤ-inverseʳ (na *ℤ (+ suc da₋))))

------------------------------------------------------------------------
-- REMAINING (3 of 14): the long nested cross-multiplication identities.
--   +ℚ-assoc, distribˡ, distribʳ.
-- Each is provable over ≈ℚ from the canonical ℤ ring laws (*ℤ-distribˡ/ʳ-+,
-- *ℤ-assoc, *ℤ-comm, +ℤ-assoc) + ℕ *-assoc/*-comm — same recipe as above but a
-- multi-step ℤ-algebra chain (numerator is a nested +ℤ of *ℤ products,
-- denominators are triple `suc _` products that un-truncate by refl). Deferred
-- as a focused follow-on; the 11 above (incl. the inverses, false over `≡`)
-- are the load-bearing wins of the ≈ℚ move.
------------------------------------------------------------------------
