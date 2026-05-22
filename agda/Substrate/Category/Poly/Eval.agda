------------------------------------------------------------------------
-- Substrate.Category.Poly.Eval (T9)
-- PolyTerm → opaque polymorphism evaluation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Eval where

open import Substrate.Category.Poly using (Poly)
open import Substrate.Category.Poly.Term

module _ {PMor : Poly → Poly → Set}
         (id-PMor : ∀ {P} → PMor P P)
         (comp-PMor : ∀ {P Q R} → PMor Q R → PMor P Q → PMor P R)
         (lift-PMor : ∀ {P Q} → PMor P Q) where

  eval-gen : ∀ {P Q} → PolyGen P Q → PMor P Q
  eval-gen (lift-poly _ _) = lift-PMor

  eval : ∀ {P Q} → PolyTerm P Q → PMor P Q
  eval []       = id-PMor
  eval (g ∷ ts) = comp-PMor (eval ts) (eval-gen g)
