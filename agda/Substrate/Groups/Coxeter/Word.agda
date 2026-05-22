------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Word
--
-- Self-contained Word type (= cons-list) for the Coxeter framework.
-- Avoids Data.List clashing-definition friction when Core re-exports
-- ++ alongside instance-local imports.
--
-- API surface: the four list atoms (Word, [], _∷_, _++_) plus the
-- one property the Coxeter framework actually uses (++-assoc). No
-- map/filter/length/etc. — if downstream code wants stdlib List
-- operations, convert via `to-list` / `from-list` (provided below).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.Word where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

------------------------------------------------------------------------
-- 1. The Word type (cons-list of generators).
------------------------------------------------------------------------

infixr 5 _∷_

data Word (Gen : Set) : Set where
  []  : Word Gen
  _∷_ : Gen → Word Gen → Word Gen

------------------------------------------------------------------------
-- 2. Concatenation.
------------------------------------------------------------------------

infixr 5 _++_

_++_ : {Gen : Set} → Word Gen → Word Gen → Word Gen
[]       ++ ys = ys
(x ∷ xs) ++ ys = x ∷ (xs ++ ys)

------------------------------------------------------------------------
-- 3. Associativity (the one ++ property the framework needs).
------------------------------------------------------------------------

++-assoc : {Gen : Set} (a b c : Word Gen) →
           (a ++ b) ++ c ≡ a ++ (b ++ c)
++-assoc []      b c = refl
++-assoc (x ∷ a) b c = cong (x ∷_) (++-assoc a b c)

------------------------------------------------------------------------
-- 4. Left/right identity for ++ (used by the Coxeter GroupAdapter
-- to discharge ε-left-++ / ε-right-++ obligations for ListPresentation
-- instances). Left is definitional; right needs induction.
------------------------------------------------------------------------

++-identity-left : {Gen : Set} (w : Word Gen) → [] ++ w ≡ w
++-identity-left _ = refl

++-identity-right : {Gen : Set} (w : Word Gen) → w ++ [] ≡ w
++-identity-right []      = refl
++-identity-right (x ∷ w) = cong (x ∷_) (++-identity-right w)

------------------------------------------------------------------------
-- 5. Interop with stdlib Data.List was REMOVED in Phase 2 to break
-- a transitive Relation.Binary.PropositionalEquality dependency
-- that conflicted with Substrate.Foundation.Eq's BUILTIN EQUALITY.
-- No consumer uses to-list / from-list (verified by grep);
-- substrate-native code uses Word directly.
--
-- If interop is ever needed again, build it via a separate
-- Substrate.Groups.Coxeter.Word.AsList submodule that downstream
-- consumers can OPTIONALLY import, keeping this base module
-- stdlib-free.
------------------------------------------------------------------------
