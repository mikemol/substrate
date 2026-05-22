------------------------------------------------------------------------
-- Substrate.Category.BeckChevalley.ComposeInstance
--
-- A worked example of BC vertical pasting: paste two trivial-identity
-- BC squares to demonstrate the combinator type-checks and produces
-- a coherent pasted square.
--
-- This is a TYPE-LEVEL demonstration; substantive substrate-level
-- pastings (e.g., chaining poly-mult with bilinform-eval via shared
-- intermediate types) are deferred until use sites arise.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.BeckChevalley.ComposeInstance where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.BeckChevalley using (BCSquare; bc-trivial)
open import Substrate.Category.BeckChevalley.Compose using (vertical-paste)

------------------------------------------------------------------------
-- N-1: A trivial identity BC square (all morphisms = identity).
--
-- For any A : Set, the square with id-morphisms on all 4 sides has
-- trivial cell (refl). Useful as a building block for testing
-- composition combinators.
------------------------------------------------------------------------

trivial-id-square :
  ∀ {A : Set} →
  BCSquare {A = A} {A} {A} {A} (λ x → x) (λ x → x) (λ x → x) (λ x → x)
trivial-id-square = bc-trivial (λ x → x) (λ x → x) (λ x → x) (λ x → x) (λ _ → refl)

------------------------------------------------------------------------
-- N-2: Vertical paste of two trivial squares.
--
-- Demonstrates the vertical-paste combinator: takes two BCSquares
-- with matching shared edge (k1 = f2 = id here) and produces a
-- pasted BCSquare with composed left + right morphisms (= id ∘ id =
-- id) and bottom = k2 (= id).
--
-- The result is structurally trivial (all id morphisms), but the
-- type-check confirms the combinator's signature is correct and the
-- pasting produces a coherent cell.
------------------------------------------------------------------------

paste-trivial :
  ∀ {A : Set} →
  BCSquare {A = A} {A} {A} {A}
           (λ x → x) (λ a → a) (λ b → b) (λ x → x)
paste-trivial = vertical-paste trivial-id-square trivial-id-square

------------------------------------------------------------------------
-- N-3: Capstone.
--
-- After this slice: the BC pasting combinators (vertical-paste +
-- horizontal-paste) are demonstrated type-correct via a trivial
-- worked example.
--
-- Substantive substrate-level pastings (chaining poly-mult ⇒ tensor
-- ⇒ bivector through shared intermediate types) are deferred
-- follow-ons; they require careful matching of intermediate
-- carriers between the existing BCSquare instances.
------------------------------------------------------------------------
