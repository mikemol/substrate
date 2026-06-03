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
open import Substrate.Category.UniversalProperty using (UPArrow; trivial-UP)
open import Substrate.Category.UniversalProperty.Vacuity
  using (Vacuous; Contentful; contentful→¬vacuous; trivial-vacuous;
         eq-UP; eq-contentful)

------------------------------------------------------------------------
-- 1. The gate: a recognized UP carries its non-vacuity certificate.
------------------------------------------------------------------------

record RecognizedUP : Set₁ where
  field
    arrow   : UPArrow
    content : Contentful arrow

open RecognizedUP public

------------------------------------------------------------------------
-- 2. The ⊤-collapse is NOT recognizable (the false-positive shape is gated
--    out): it is vacuous, so it cannot carry a content certificate.
------------------------------------------------------------------------

trivial-not-recognizable : ¬ Contentful trivial-UP
trivial-not-recognizable c = contentful→¬vacuous trivial-UP c trivial-vacuous

------------------------------------------------------------------------
-- 3. Real, equality-witnessed UPs ARE recognizable.
------------------------------------------------------------------------

-- the bare equality UP (Witness = _≡_ on ℕ).
eq-recognized : RecognizedUP
eq-recognized = record { arrow = eq-UP ; content = eq-contentful }

-- a CRT-shaped UP for moduli (3,5): a residue pair (a₁,a₂) is "solved" by
-- any x congruent to a₁ mod 3 and a₂ mod 5. Contentful because (1,2) is NOT
-- solved by 0 (0 ≢ 1 mod 3).
crt-UP : UPArrow
crt-UP = record
  { Source  = ℕ × ℕ
  ; Target  = ℕ
  ; Witness = λ p x → (x mod-suc 2 ≡ proj₁ p mod-suc 2)
                    × (x mod-suc 4 ≡ proj₂ p mod-suc 4)
  }

crt-recognized : RecognizedUP
crt-recognized = record
  { arrow   = crt-UP
  ; content = (1 , 2) , 0 , λ { (() , _) }
  }
