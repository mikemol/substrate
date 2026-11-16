------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.EkeyCodec
--
-- Defines: renderKids, parseKids
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.EkeyCodec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Lifecycle.Fragment.Ekey


------------------------------------------------------------------------
-- THE CHILD-LIST CODEC — the concatenative core of the ekey rendering.
--
-- ⚑⚑ THE CHILD LIST IS WHERE THE ROUND-TRIP CAN ACTUALLY FAIL, which is why
-- it is the part modelled here. The four scalar slots (`c`, `i`, `l`, `q`)
-- are single values with a fixed tag: their round-trip is immediate. The
-- `"ch": [...]` array is the only CONCATENATIVE part — a sequence whose
-- rendering runs together with whatever follows it — and concatenation is
-- exactly where a naive `parse (render x) ≡ x` statement fails to be provable
-- by induction. `TmDBGodel` hit the same wall at `app f x` and solved it the
-- same way.
--
-- ⚑ LENGTH-PREFIXED, NOT DELIMITED, AND THAT IS A REAL DIVERGENCE FROM THE
-- STORE. The store's rendering delimits with `", "` and closes with `]`;
-- recovering the list means scanning for a delimiter, which is only injective
-- if no payload can contain one. A LENGTH PREFIX makes the parse structural:
-- read n, then read exactly n words. This is a modelling choice, and it is
-- STRONGER than what the store does — so the round-trip proved here does not
-- by itself certify the store's delimiter-based reader. That gap is named in
-- the hypothesis this module's consumer states, not hidden.
--
-- ⚑ `parseKids` RETURNS `(value , rest)` — the prefix-closed shape, verbatim
-- from `TmDBGodel.parse-fuel`. Returning just the value would lose the
-- information the induction needs at the concatenation point.
--
-- ⚑ MALFORMED INPUT RETURNS THE EMPTY LIST AND THE REMAINING TOKENS, rather
-- than failing. `TmDBGodel` does the same (*"malformed input / out of fuel →
-- I"*). A total parser keeps the codec a plain function pair, which is what
-- `split-Canonical` consumes; a partial one would need the error case
-- threaded through every downstream statement for no gain, since the
-- retraction only ever claims something about WELL-FORMED input.
------------------------------------------------------------------------

-- Render a child list: a length, then the ids, in order.
renderKids : List ℕ → List Tok
renderKids ks = tagKids ∷ word (len ks) ∷ words ks
  where
    len : List ℕ → ℕ
    len []       = zero
    len (_ ∷ xs) = suc (len xs)

    words : List ℕ → List Tok
    words []       = []
    words (k ∷ xs) = word k ∷ words xs

-- Read exactly n payload words, returning them with what follows.
takeWords : ℕ → List Tok → List ℕ × List Tok
takeWords zero    ts             = [] , ts
takeWords (suc n) []             = [] , []
takeWords (suc n) (word k ∷ ts)  =
  let r = takeWords n ts in (k ∷ proj₁ r) , proj₂ r
takeWords (suc n) (t ∷ ts)       = [] , ts

-- Parse a rendered child list, prefix-closed: `(kids , rest)`.
parseKids : List Tok → List ℕ × List Tok
parseKids (tagKids ∷ word n ∷ ts) = takeWords n ts
parseKids ts                      = [] , ts
