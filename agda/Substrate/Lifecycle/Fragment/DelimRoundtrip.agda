------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.DelimRoundtrip
--
-- Defines: split-join
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.DelimRoundtrip where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Empty.Bot
open import Substrate.Lifecycle.Fragment.Delim
open import Substrate.Lifecycle.Fragment.DelimCodec


------------------------------------------------------------------------
-- THE DELIMITER-DISJOINTNESS ROUND-TRIP.
--
-- ⚑⚑⚑ THIS IS THE OBLIGATION `EkeyRoundtrip` NAMED AND LEFT OPEN, now
-- discharged: a delimited field parses back to itself, with the following
-- symbols intact — PROVIDED the continuation does not begin with a payload
-- symbol. That proviso is not a weakness in the proof; it IS the
-- disjointness condition, made explicit and demanded at every use site.
--
-- ⚑⚑ AND IT IS EXACTLY WHY A DELIMITED ENCODING NEEDS A HYPOTHESIS WHERE A
-- LENGTH-PREFIXED ONE DOES NOT. `splitField` stops at `sep` or at end of
-- input; it cannot stop mid-run. So if `rest` began with `dig d`, that symbol
-- would be absorbed into THIS field and the parse would return more than was
-- written. `StartsClean` rules exactly that out — and in the store it holds
-- by construction, because a rendered field is always followed by `,` or by
-- the end of `ch`.
--
-- ⚑ WHAT THIS BUYS OVER ASSUMING IT. `obs_node.ch` is comma-joined DECIMAL
-- NUMERALS — measured live: `'1,2'`, `'0,3'`, `''`; 0 null, 536,014 empty,
-- 419,336 distinct over 956,336 rows. Digits and commas are disjoint
-- alphabets, so `StartsClean` is DISCHARGEABLE at each use rather than
-- assumed globally. Had a payload been able to contain a comma — a quoted
-- string, say — no proof about the parser would have helped: the ENCODING
-- would be ambiguous, and the drain's byte comparison would pass on two
-- distinct child lists that rendered identically. That is the failure this
-- module exists to make impossible to overlook.
--
-- ⚑ THE EMPTY FIELD IS THE INTERESTING BASE CASE, not a degenerate one. It
-- covers the 536,014 leaf rows whose `ch` is `''`, and it is where the
-- hypothesis does its real work: at `ks = []` the lemma says
-- `splitField rest ≡ ([] , rest)`, which is FALSE if `rest` starts with a
-- digit. So the leaves — the majority of the table — are precisely the rows
-- that need the condition.
------------------------------------------------------------------------

-- The continuation does not begin with a payload symbol.
-- ⚑ A `Set`, not a `Bool`: the consumer must SUPPLY a witness, so the
-- condition cannot be silently skipped the way a forgotten guard would be.
StartsClean : List Sym → Set
StartsClean []          = ⊤
StartsClean (sep ∷ _)   = ⊤
StartsClean (dig _ ∷ _) = ⊥

-- Reading back a rendered field returns it, with the continuation intact.
split-join :
  (ks : Field) (rest : List Sym) → StartsClean rest →
  splitField (joinField ks rest) ≡ (ks , rest)
split-join []       []          _  = refl
split-join []       (sep ∷ ss)  _  = refl
split-join []       (dig _ ∷ _) ()
split-join (k ∷ ks) rest        sc
  rewrite split-join ks rest sc = refl
