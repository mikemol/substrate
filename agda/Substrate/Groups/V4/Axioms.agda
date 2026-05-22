------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms
--
-- The group axioms for V₄ via case-enumeration. Each axiom unfolds
-- the V₄ operation to its Coxeter image, which reduces to the
-- canonical word definitionally; refl closes each case.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms where

open import Substrate.Foundation.Eq using (_≡_; refl; _≢_)
open import Substrate.Foundation.Product using (_×_; _,_)

open import Substrate.Groups.V4.Operations public

------------------------------------------------------------------------
-- Identity / inverse / associativity / commutativity laws.
--
-- Type signatures inlined to avoid stdlib `Algebra.Definitions`.
------------------------------------------------------------------------

·-cong : {x y u v : V₄} → x ≡ y → u ≡ v → (x · u) ≡ (y · v)
·-cong refl refl = refl

ε-left : (x : V₄) → (ε · x) ≡ x
ε-left = v4-cover _ (refl , refl , refl , refl)

ε-right : (x : V₄) → (x · ε) ≡ x
ε-right = v4-cover _ (refl , refl , refl , refl)

ε-identity : ((x : V₄) → (ε · x) ≡ x) × ((x : V₄) → (x · ε) ≡ x)
ε-identity = ε-left , ε-right

inv-left : (x : V₄) → ((inv x) · x) ≡ ε
inv-left = v4-cover _ (refl , refl , refl , refl)

inv-right : (x : V₄) → (x · (inv x)) ≡ ε
inv-right = v4-cover _ (refl , refl , refl , refl)

inv-inverse :
  ((x : V₄) → ((inv x) · x) ≡ ε) × ((x : V₄) → (x · (inv x)) ≡ ε)
inv-inverse = inv-left , inv-right

·-assoc : (x y z : V₄) → ((x · y) · z) ≡ (x · (y · z))
·-assoc = v4×v4×v4-cover _
  ( ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  , ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  , ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  , ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  )

·-comm : (x y : V₄) → (x · y) ≡ (y · x)
·-comm = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )

------------------------------------------------------------------------
-- Derived cancellation identity.
------------------------------------------------------------------------

·-right-cancel-ε : (a b : V₄) → a · b ≡ b → a ≡ ε
·-right-cancel-ε = v4×v4-cover _
  ( ((λ _ → refl) , (λ _ → refl) , (λ _ → refl) , (λ _ → refl))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  )
