------------------------------------------------------------------------
-- Substrate.Foundation.Hedberg
--
-- Hedberg's theorem: any type with decidable equality satisfies UIP
-- (uniqueness of identity proofs), i.e., is a set in the HoTT sense.
--
-- Substrate-native replacement for stdlib's
-- `Axiom.UniquenessOfIdentityProofs.Decidable⇒UIP`.
--
-- Holds under --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Hedberg where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)

------------------------------------------------------------------------
-- DecidableEquality.
------------------------------------------------------------------------

DecidableEquality : Set → Set
DecidableEquality A = (x y : A) → Dec (x ≡ y)

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

private
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
