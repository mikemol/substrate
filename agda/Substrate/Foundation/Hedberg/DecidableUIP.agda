------------------------------------------------------------------------
-- Substrate.Foundation.Hedberg.DecidableUIP
--
-- Defines: Decidable⇒UIP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Hedberg; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Hedberg.DecidableUIP where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Hedberg.DecidableEquality
open import Substrate.Foundation.Hedberg.Private
-- ⚑⚑ `Substrate.Foundation.Eq.CongTrans` WAS IMPORTED HERE AND IS NOT. It exports a
-- `cong-trans` that is a NATURALITY-SQUARE combinator — `(f : A → B) → x ≡ y → f y ≡ z →
-- f x ≡ z`, f AND TWO proofs — while the `where`-local below is congruence on the right of a
-- FIXED `trans` and takes ONE proof. The call at :40 passes one argument, so it always meant
-- the LOCAL; the import supplied nothing this module used and produced [ClashingDefinition].
-- ⚑ Found by gcalculus's real typecheck against a pristine copy of this tree. NO CENSUS HERE
-- REPORTS IT: `--grep '^cong-trans$'` returns ONE name because a `where`-local is in no export
-- list, and `--unused-imports` keeps it because the name IS mentioned — neither can tell the
-- mention resolves to the local. Two blind spots, one line.



------------------------------------------------------------------------
-- Hedberg's theorem: any two proofs of x ≡ y are equal.
------------------------------------------------------------------------

Decidable⇒UIP :
  {A : Set} → DecidableEquality A →
  {x y : A} (p q : x ≡ y) → p ≡ q
Decidable⇒UIP {A} _≟_ {x} {y} p q =
  -- Want: p ≡ q
  -- via:  p ≡ trans (sym (stable refl)) (stable p)    [decompose]
  --       ≡ trans (sym (stable refl)) (stable q)    [cong via stable-const]
  --       ≡ q                                         [sym decompose]
  trans (decompose _≟_ p)
        (trans (cong-trans (stable-const _≟_ p q))
               (sym (decompose _≟_ q)))
  where
    -- Helper: cong on the right side of trans.
    cong-trans : {a b : x ≡ y} → a ≡ b →
                 trans (sym (stable _≟_ {x} {x} refl)) a
                 ≡ trans (sym (stable _≟_ {x} {x} refl)) b
    cong-trans refl = refl
