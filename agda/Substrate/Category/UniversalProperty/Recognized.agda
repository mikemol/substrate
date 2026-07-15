------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Recognized
--
-- Gating the universal-property recognizer on the vacuity recognizer: a
-- RecognizedUP is a UPArrow that CARRIES its non-vacuity certificate
-- (a Contentful proof). So "this is a real universal property" is no longer
-- an assertion — you cannot build a RecognizedUP without exhibiting a
-- problem that some candidate fails. The ⊤-collapse is provably NOT
-- recognizable; equality-witnessed UPs (the shape of every real wedge —
-- bezout s·a+t·b≡g, the CRT mod-system, the mod-homs) ARE.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Recognized where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Category.UniversalProperty using (UPArrowP; mkUP; trivial-UPP)
open import Substrate.Category.UniversalProperty.Vacuity
  using (Vacuous; Contentful; contentful→¬vacuous; trivial-vacuous;
         eq-UP; eq-contentful)

------------------------------------------------------------------------
-- 1. The gate: a recognized UP carries its non-vacuity certificate.
--    ⟡UPArrow-dissolve: FIELD→INDEX. The stored `arrow : UPArrow` (the
--    Set₁ cause) becomes the carrier PARAMS (S T W); the record fields
--    only the Set₀ content certificate, so RecognizedUP S T W : Set₀.
------------------------------------------------------------------------

record RecognizedUP (S T : Set) (W : S → T → Set) : Set where
  field
    content : Contentful (mkUP {S} {T} {W})

open RecognizedUP public

------------------------------------------------------------------------
-- 2. The ⊤-collapse is NOT recognizable (the false-positive shape is gated
--    out): it is vacuous, so it cannot carry a content certificate.
------------------------------------------------------------------------

trivial-not-recognizable : ¬ Contentful trivial-UPP
trivial-not-recognizable c = contentful→¬vacuous trivial-UPP c trivial-vacuous

------------------------------------------------------------------------
-- 3. Real, equality-witnessed UPs ARE recognizable.
------------------------------------------------------------------------

-- the bare equality UP (Witness = _≡_ on ℕ).
eq-recognized : RecognizedUP ℕ ℕ _≡_
eq-recognized = record { content = eq-contentful }

-- a CRT-shaped UP for moduli (3,5): a residue pair (a₁,a₂) is "solved" by
-- any x congruent to a₁ mod 3 and a₂ mod 5. Contentful because (1,2) is NOT
-- solved by 0 (0 ≢ 1 mod 3).
crt-W : (ℕ × ℕ) → ℕ → Set
crt-W p x = (x mod-suc 2 ≡ proj₁ p mod-suc 2)
          × (x mod-suc 4 ≡ proj₂ p mod-suc 4)

crt-UP : UPArrowP (ℕ × ℕ) ℕ crt-W
crt-UP = mkUP

crt-recognized : RecognizedUP (ℕ × ℕ) ℕ crt-W
crt-recognized = record
  { content = (1 , 2) , 0 , λ { (() , _) } }
