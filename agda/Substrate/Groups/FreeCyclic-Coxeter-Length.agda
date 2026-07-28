------------------------------------------------------------------------
-- Substrate.Groups.FreeCyclic-Coxeter-Length
--
-- The bijection between FreeCyclic-Coxeter's Word/Canonical-Free structure
-- and ℕ via word length.
--
-- FreeCyclic has no relations; every word `(a ∷ a ∷ ... ∷ [])` of
-- length n corresponds to the natural number n. This module makes
-- the bijection explicit, plus a few utility lemmas needed by the
-- 2-D word algebra (cycle-counter axis = FreeCyclic = ℕ).
--
-- Note on Group structure: FreeCyclic is a monoid (free on one
-- generator), not a group — there's no inverse without adding a⁻¹
-- as a second generator. We work at the monoid level here; the
-- 2-D word algebra uses FreeCyclic's Coxeter Core (which doesn't
-- require inversion).
--
-- Per [[feedback-categorical-name-first]]: FreeCyclic ≅ ℕ (additive
-- monoid). The Coxeter framing surfaces ℕ within the substrate's
-- word algebra, making it composable via DirectProduct.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.FreeCyclic-Coxeter-Length where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; trans)

import Substrate.Groups.FreeCyclic-Coxeter as F
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

------------------------------------------------------------------------
-- N-1: length-of-word — extract the ℕ value from a FreeCyclic word.
------------------------------------------------------------------------

length-of-word : Word F.Gen → ℕ
length-of-word []       = zero
length-of-word (x ∷ w)  = suc (length-of-word w)

------------------------------------------------------------------------
-- N-2: word-of-length — build a FreeCyclic word from a ℕ value.
------------------------------------------------------------------------

word-of-length : ℕ → Word F.Gen
word-of-length zero    = []
word-of-length (suc n) = F.a ∷ word-of-length n

------------------------------------------------------------------------
-- N-3: Roundtrips.
------------------------------------------------------------------------

length-of-word-of-length :
  (n : ℕ) → length-of-word (word-of-length n) ≡ n
length-of-word-of-length zero    = refl
length-of-word-of-length (suc n) = cong suc (length-of-word-of-length n)

word-of-length-of-word :
  (w : Word F.Gen) → word-of-length (length-of-word w) ≡ w
word-of-length-of-word []          = refl
word-of-length-of-word (F.a ∷ w)   = cong (F.a ∷_) (word-of-length-of-word w)

------------------------------------------------------------------------
-- N-4: Compatibility with insert.
--
-- `insert a w` = `a ∷ w` corresponds to "suc the length":
--   length-of-word (insert a w) ≡ suc (length-of-word w)
--
-- This is the structural identity that FreeCyclic's `insert a` IS
-- the ℕ successor operation lifted to the word representation.
------------------------------------------------------------------------

insert-as-suc-length :
  (w : Word F.Gen) →
  length-of-word (F.insert F.a w) ≡ suc (length-of-word w)
insert-as-suc-length w = refl

------------------------------------------------------------------------
-- N-5: Capstone — FreeCyclic ↔ ℕ bijection lands.
--
-- After this slice:
--
--   * length-of-word : Word F.Gen → ℕ
--   * word-of-length : ℕ → Word F.Gen
--   * length-of-word-of-length : roundtrip on ℕ
--   * word-of-length-of-word   : roundtrip on Word
--   * insert-as-suc-length     : insert a ≡ suc at the length level
--
-- The bijection makes the "FreeCyclic = ℕ" identification structural.
-- For the 2-D word algebra arc: the cycle-counter axis IS ℕ, and
-- this module surfaces the identification.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: ℕ within the
-- Coxeter framework. FreeCyclic's Word + canonical-is-fixed
-- (slice 1) + this length bijection give substrate-native access
-- to ℕ as a Coxeter-style monoid.
------------------------------------------------------------------------
