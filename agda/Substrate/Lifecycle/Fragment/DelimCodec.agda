------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.DelimCodec
--
-- Defines: joinField, splitField
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.DelimCodec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Lifecycle.Fragment.Delim


------------------------------------------------------------------------
-- THE DELIMITED CODEC — one field, prefix-closed.
--
-- ⚑ THE SHAPE IS `EkeyCodec`'s, AND DELIBERATELY SO: `splitField` returns
-- `(value , rest)` rather than just the value, for the same reason
-- `TmDBGodel.parse-fuel` does — the induction at the concatenation point
-- needs to know what followed. A codec that returned only the value would
-- prove the bare round-trip and fail to compose across fields.
--
-- ⚑⚑ NO FUEL, AND THE REASON IS THE ALPHABET RATHER THAN THE GRAMMAR.
-- `EkeyCodec` needed none because its list was FLAT; this one needs none
-- because `splitField` recurses on the SYMBOL LIST, which shrinks
-- structurally at every step. Both are total by construction; neither
-- inherits `TmDBGodel`'s `parse-fuel`, which exists only because `app f x`
-- nests to unknown depth.
--
-- ⚑ `joinField` EMITS NO TRAILING SEPARATOR, matching the store: `'1,2'`, not
-- `'1,2,'`. That choice is what makes the empty list render as `''` and read
-- back as `[]` — the 536,014 leaf rows measured live. A trailing separator
-- would render `[]` and `[x]` distinguishably but make `''` ambiguous between
-- "no children" and "one empty child", which is precisely the ambiguity the
-- disjointness argument exists to rule out.
--
-- ⚑ A SEPARATOR AT THE HEAD TERMINATES THE FIELD, returning what follows. So
-- a field is exactly a maximal run of payload symbols — the definition the
-- injectivity argument needs, expressed as the parser's own structure rather
-- than as a side condition someone must remember to check.
------------------------------------------------------------------------

-- Render one field, then whatever follows it.
joinField : Field → List Sym → List Sym
joinField []       rest = rest
joinField (d ∷ ds) rest = dig d ∷ joinField ds rest

-- Read a maximal run of payload symbols, prefix-closed.
splitField : List Sym → Field × List Sym
splitField []            = [] , []
splitField (sep ∷ ss)    = [] , sep ∷ ss
splitField (dig d ∷ ss)  =
  let r = splitField ss in (d ∷ proj₁ r) , proj₂ r
