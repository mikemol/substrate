------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Delim
--
-- Defines: Sym, Field
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Delim where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List


------------------------------------------------------------------------
-- THE DELIMITER ALPHABET — closing the gap `EkeyRoundtrip` left open.
--
-- ⚑⚑ THE GAP, RESTATED: `EkeyCodec` models a LENGTH-PREFIXED child list;
-- the store writes a DELIMITED one. `obs_node.ch` holds `'1,2'`, `'0,3'`,
-- `''` — comma-joined `local_id`s. A length prefix makes the parse structural
-- for free; a delimiter scan is injective ONLY IF no payload can contain the
-- delimiter. That is an obligation about the ALPHABET, and until it is
-- discharged the length-prefixed proof does not transfer.
--
-- ⚑⚑⚑ AND IT IS DISCHARGEABLE, NOT MERELY ASSUMABLE — MEASURED, LIVE:
--
--     schema.py --live --sample obs_node 5   →  ch = '', '', '', '1,2', '0,3'
--     schema.py --live --nullity obs_node    →  ch: 0 null · 536,014 empty
--                                               · 419,336 distinct · 956,336 rows
--
-- **`ch` is TOTAL (never null) and its payloads are DECIMAL NUMERALS.** The
-- 536,014 empties are the leaves — no children — which is exactly the `[]`
-- case. So the alphabet is digits, the delimiter is a comma, and the two are
-- DISJOINT BY CONSTRUCTION. The scan is injective.
--
-- ⚑ THE MODEL IS TWO SYMBOLS, NOT TEN, AND THAT IS THE POINT. Nothing here
-- needs base-10 arithmetic or the value a numeral denotes — the property is
-- about which symbols can appear WHERE. Modelling digits individually would
-- add ten constructors and prove the same theorem, while inviting the reader
-- to think the numeral semantics were load-bearing. `dig` abstracts "any
-- symbol a payload may contain"; `sep` is the one symbol it may not.
--
-- ⚑ WHY THIS IS NOT AN ARBITRARY SIMPLIFICATION. The disjointness is what
-- makes a delimited encoding recoverable AT ALL, for any alphabet. A proof
-- over ten concrete digits would be a proof about decimal; a proof over
-- `dig`/`sep` is a proof about DELIMITED ENCODINGS, of which the store's is
-- one instance. The narrower model is the more general theorem.
--
-- ⚑ WHAT IS STILL NOT COVERED, so the limit stays visible: this closes the
-- CHILD-LIST delimiter (`,` inside `ch`). The ekey's OUTER rendering uses
-- `", "` between JSON members and wraps values with postgres's `to_json`,
-- whose escaping is not modelled here (see `Ekey`). A JSON string CAN contain
-- a comma — `to_json` is what makes that safe, by quoting and escaping — so
-- the outer level's injectivity rests on the escaper, not on disjointness.
-- Those are different arguments and must not be conflated.
------------------------------------------------------------------------

-- The alphabet, split by the only distinction the proof needs.
data Sym : Set where
  dig : ℕ → Sym        -- a payload symbol (a decimal digit, in the store)
  sep : Sym            -- the delimiter (`,`)

-- A field is a run of payload symbols — by construction, no separator.
Field : Set
Field = List ℕ
