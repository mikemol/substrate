------------------------------------------------------------------------
-- Substrate.Algebra.Bijection
--
-- In-tree replacement for `Function.Bundles._↔_` over propositional
-- equality. The substrate's Cardinality / V4Signature.Codeword files
-- only ever instantiate stdlib's bundled `_↔_` at `_≡_` on both sides;
-- this module captures exactly that case without dragging in
-- `Function.Bundles` and `Function.Properties.Inverse`.
--
-- The field names (`to`, `from`, `to-from`, `from-to`) and the
-- constructor argument order of `mk↔ₛ′` match the stdlib calling
-- convention so that existing call sites migrate by import-swap only.
--
-- ⟡Ⓒ.bijection (which bijection do I use?): this is the Set₀, stdlib-
-- compatible form with the richer combinator suite (mk↔ₛ′, ↔-sym,
-- ↔-trans, _×-↔_). Its universe-POLYMORPHIC sibling is
-- Substrate.Foundations.Bijection.Bijection (same four fields; use it
-- when A/B live above Set₀ — the M-12 bridge shape). `_↔_ A B` is
-- exactly `Bijection {lzero} {lzero} A B`; the two are NOT merged (each
-- has its own combinators + dependent set — a low-value/moderate-risk
-- migration). For a bijection whose round-trips are up to a SETOID or
-- extensional equality (NOT `≡` on both sides), neither fits: see the
-- deliberately-bespoke Stab≃S₃ / TotalSpace≃S₄ / Live≃Permutation, and
-- memory feedback_bijection_parallel_false_positive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Bijection where

open import Substrate.Foundation.Eq using (_≡_; refl; sym)

------------------------------------------------------------------------
-- 1. The bijection record.
------------------------------------------------------------------------

infix 4 _↔_

record _↔_ (A B : Set) : Set where
  field
    to      : A → B
    from    : B → A
    to-from : (b : B) → to (from b) ≡ b
    from-to : (a : A) → from (to a) ≡ a

open _↔_ public

------------------------------------------------------------------------
-- 2. Stdlib-compatible constructor.
--
-- Argument order matches `Function.Bundles.mk↔ₛ′`:
--   mk↔ₛ′ to from to-from from-to
------------------------------------------------------------------------

mk↔ₛ′ :
  {A B : Set} →
  (f : A → B) →
  (g : B → A) →
  ((b : B) → f (g b) ≡ b) →
  ((a : A) → g (f a) ≡ a) →
  A ↔ B
mk↔ₛ′ f g tf ft = record
  { to      = f
  ; from    = g
  ; to-from = tf
  ; from-to = ft
  }

------------------------------------------------------------------------
-- 3. Symmetry: flip the bijection.
------------------------------------------------------------------------

↔-sym : {A B : Set} → A ↔ B → B ↔ A
↔-sym i = record
  { to      = from i
  ; from    = to i
  ; to-from = from-to i
  ; from-to = to-from i
  }

------------------------------------------------------------------------
-- 4. Transitivity.
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (cong; cong₂; trans)

↔-trans : {A B C : Set} → A ↔ B → B ↔ C → A ↔ C
↔-trans f g = record
  { to      = λ a → to g (to f a)
  ; from    = λ c → from f (from g c)
  ; to-from = λ c → trans (cong (to g) (to-from f (from g c))) (to-from g c)
  ; from-to = λ a → trans (cong (from f) (from-to g (to f a))) (from-to f a)
  }

------------------------------------------------------------------------
-- 5. Product on bijections.
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (_×_; _,_)

_×-↔_ : {A B C D : Set} → A ↔ C → B ↔ D → (A × B) ↔ (C × D)
f ×-↔ g = record
  { to      = λ { (a , b) → to f a , to g b }
  ; from    = λ { (c , d) → from f c , from g d }
  ; to-from = λ { (c , d) → cong₂ _,_ (to-from f c) (to-from g d) }
  ; from-to = λ { (a , b) → cong₂ _,_ (from-to f a) (from-to g b) }
  }

------------------------------------------------------------------------
-- Note on `fin-product : Fin m × Fin n ↔ Fin (m * n)`:
-- Not yet provided in-tree; consumers (`Substrate.Cardinality.Product`)
-- still go through `Data.Fin.Properties.*↔×`. Migrating that bijection
-- requires an actual combine/divide round-trip proof, which is its
-- own arc — not a single slice.
------------------------------------------------------------------------
