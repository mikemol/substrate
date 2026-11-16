------------------------------------------------------------------------
-- Substrate.Foundation.Hedberg.Private
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Hedberg; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Hedberg.Private where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Hedberg.DecidableEquality



------------------------------------------------------------------------
-- Hedberg's theorem.
--
-- Strategy:
--   1. From decidable equality, define a "stable" map
--      stable : x ≡ y → x ≡ y that depends only on x and y, not on
--      the proof — so it's CONSTANT (stable p ≡ stable q for any p, q).
--   2. Any path p : x ≡ y satisfies
--      p ≡ trans (sym (stable refl-at-x)) (stable p)
--      via J-induction (path-induction on p).
--   3. Then for any p, q : x ≡ y,
--      p ≡ trans (sym (stable refl)) (stable p)
--         ≡ trans (sym (stable refl)) (stable q)   (by constancy of stable)
--         ≡ q.
------------------------------------------------------------------------

module _ {A : Set} (_≟_ : DecidableEquality A) where

  -- The stable map. By case on x ≟ y: if yes-decidable returns the
  -- (chosen) witness; if no-decidable returns the absurd-branch
  -- (input proof rules out the no-branch).
  stable : {x y : A} → x ≡ y → x ≡ y
  stable {x} {y} p with x ≟ y
  ... | yes q = q
  ... | no  ¬p with ¬p p
  ...           | ()

  -- stable is CONSTANT.
  stable-const :
    {x y : A} (p q : x ≡ y) → stable p ≡ stable q
  stable-const {x} {y} p q with x ≟ y
  ... | yes _ = refl
  ... | no ¬p with ¬p p
  ...          | ()

  -- trans (sym p) p ≡ refl, by path induction.
  trans-sym-id : {x y : A} (p : x ≡ y) → trans (sym p) p ≡ refl
  trans-sym-id refl = refl

  -- The decomposition lemma. For any p, the path
  -- p = trans (sym (stable refl)) (stable p) holds.
  -- Proof by J-induction on p: when p = refl, we need
  --   refl ≡ trans (sym (stable refl)) (stable refl)
  -- which is sym (trans-sym-id (stable refl)).
  decompose : {x y : A} (p : x ≡ y) →
              p ≡ trans (sym (stable {x} {x} refl)) (stable p)
  decompose refl = sym (trans-sym-id (stable refl))
