------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Ekey
--
-- Defines: Tok, ekeySize
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Ekey where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List


------------------------------------------------------------------------
-- THE EKEY AS A TOKEN SEQUENCE — the codec's structural layer.
--
-- ⚑⚑⚑ THE PATTERN IS `TmDBGodel`'s, NOT A NEW ONE, AND FINDING THAT WAS THE
-- POINT OF ASKING. `Substrate.Category.UniversalProperty.TmDBGodel` already
-- carries a serializer proved as a retraction:
--
--     godel     : TmDB → List ℕ         constructor-tagged preorder tokens
--     parse-fuel : ℕ → List ℕ → TmDB × List ℕ
--     parse-godel : parse-fuel f (godel t ++ rest) ≡ (t , rest)   for size t ≤ f
--     godel-retract : ungodel (godel t) ≡ t
--     TmDB-Canonical = split-Canonical ungodel godel godel-retract
--
-- Three of its moves transfer verbatim and are why this module looks the way
-- it does:
--
--   1. THE PREFIX-CLOSED STATEMENT. The provable lemma is not
--      `parse (render x) ≡ x` but *"parsing `render x ++ rest` returns
--      `(x, rest)`"*. That is what makes the induction go through for a
--      CONCATENATIVE format — and an ekey's `"ch": [...]` array is exactly
--      that: a child list rendered by concatenation.
--   2. FUEL WITH A STRUCTURAL MEASURE, not `Acc`. TmDBGodel's note:
--      *"the fuel-accounting closes because `size (app f x) = suc (size f ℕ+
--      size x)`, so `size` IS the structural measure — no Acc plumbing."*
--   3. ⚑ THE DIRECTION, WHICH IS THE REVERSE OF THE NAIVE GUESS. Its header
--      states it outright: *"godel is INJECTIVE-not-surjective, so it is the
--      SECTION (s) and ungodel the retraction (F) — the reverse of a naive
--      `split-Canonical godel ungodel`."* RENDER is the section; PARSE is the
--      retraction. And injective-not-surjective is precisely the property
--      that protects a delete: if two distinct sources could render
--      identically, the store's byte comparison would pass while the
--      structural claim was false.
--
-- ⚑⚑ WHAT THIS MODULE DELIBERATELY DOES **NOT** MODEL, stated so the limit is
-- not mistaken for coverage. The store's ekey is
--
--     base64(utf8(  {"c": <json>, "ch": [<ints>], "i": <int|null>
--                    [, "l": <json>], "q": <json|null>}  ))
--
-- with postgres's `to_json` escaping, `", "` separators, an optional `"l"`
-- field present only when non-empty, `substr(role,3)` string surgery to
-- recover the de Bruijn index, and `encode(...,'base64')` line-wrapping that
-- the reader strips with `replace(…, E'\n', '')`. **Modelling THAT faithfully
-- means modelling postgres's JSON escaper and base64 wrapper**, which is a
-- large and brittle build whose failure mode is a proof about a format string
-- rather than about the data.
--
-- So this module models the STRUCTURAL layer — token-tagged fields, a
-- concatenative child list, prefix-closed parse — and the byte layer enters
-- as a NAMED HYPOTHESIS in the sibling that states the codec. That split is
-- the honest one: the structure is what the fold depends on, the bytes are
-- how the store CHECKS it, and conflating them is what would make the
-- theorem look stronger than it is.
--
-- ⚑ THE TAGS ARE THE SLOTS OF `NodeSig`, in the ekey's own field order —
-- `c`, `ch`, `i`, `l`, `q`. The order is load-bearing because the rendering
-- is a literal format string, not canonical JSON: two orderings are two
-- different byte strings for the same structure.
------------------------------------------------------------------------

-- A token: a constructor tag or a payload word. Tags mirror the ekey's
-- fields; payloads are the interned ids and indices, already ℕ-coded.
data Tok : Set where
  tagCtor  : Tok            -- "c"
  tagKids  : Tok            -- "ch"  — followed by a length, then that many ids
  tagIdx   : Tok            -- "i"
  tagLit   : Tok            -- "l"   — OPTIONAL in the rendering
  tagQname : Tok            -- "q"
  tagNull  : Tok            -- the `null` an absent nullable field renders as
  word     : ℕ → Tok        -- a payload

-- The structural measure: how many tokens a child list of length n costs.
-- ⚑ Mirrors `TmDBGodel.size`'s role — the measure the fuel accounting closes
-- on, so no `Acc` is needed.
ekeySize : List ℕ → ℕ
ekeySize []       = suc zero
ekeySize (_ ∷ ks) = suc (ekeySize ks)
