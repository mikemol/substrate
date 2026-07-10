------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.FixedPointSequentToBrick
--
-- fixed-point-sequent→Brick: lift a SequentFixed into a Brick.
-- step iterates the derivation until canonical (within the step
-- bound), then outputs the canonical form (or nothing if the bound
-- was exceeded). The brick admits the next input only after the
-- previous reached canonical form on D-out.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.FixedPointSequentToBrick where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Maybe using (Maybe)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Pipeline.Brick
open import Substrate.Pipeline.Sequent.SequentRule using (SequentRule)
open import Substrate.Pipeline.Sequent.CanonicalSpec using (CanonicalSpec)
open import Substrate.Pipeline.Sequent.SequentFixed using (SequentFixed)
open import Substrate.Pipeline.Sequent.IterateToCanonical using (iterate-to-canonical)

-- ⟡set1-paydown: cascades from CanonicalSpec/SequentFixed — thread the canonical
-- predicate `Canonical` as an implicit param; `s : SequentFixed A Canonical` and
-- `decide` returns `Maybe (Canonical a)` (was `CanonicalSpec.Canonical (…spec s) a`).
fixed-point-sequent→Brick
  : ∀ {A : Set} {Canonical : A → Set}
  → (s : SequentFixed A Canonical)
  → (decide : (a : A) → Maybe (Canonical a))
  → ℕ
  -- ⟡set1-paydown: edges are Brick's implicit indices; supply them explicitly, tag is `record {}`.
  → Brick {A} {Maybe A} {⊤} {⊤} (record {})
fixed-point-sequent→Brick s decide n = record
  { witnesses = D⇒S
  ; step      = λ (a , _) → iterate-to-canonical (SequentFixed.spec s) decide
                              (SequentFixed.derivation s) n a , tt
  ; homomorphism-tag = SequentRule
  }
