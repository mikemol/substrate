------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Exists
--
-- Decide a quantified predicate over a finite index set `Fin k`, given
-- a pointwise decision procedure.  The existential decider `Fin-∃?` is
-- the engine of finite search (e.g. the finite simplicity recognizer
-- in Substrate.Category.ConjugationCoalgebra.Simplicity); `Fin-∀?` is
-- its dual, kept as the chirality pair per [[chirality-pair-completeness]].
--
-- Gap-filler: the Foundation list/fin layer otherwise has no Any/All or
-- decidable-quantifier machinery.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Exists where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin) renaming (zero to fzero; suc to fsuc)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Product using (∃-syntax; _,_)

-- Decide ∃ over Fin k: returns a witness with its proof, or a refutation.
Fin-∃? : {k : ℕ} (P : Fin k → Set)
       → ((i : Fin k) → Dec (P i)) → Dec (∃[ i ] P i)
Fin-∃? {zero}  P dec = no (λ { (() , _) })
Fin-∃? {suc k} P dec with dec fzero
... | yes p₀ = yes (fzero , p₀)
... | no ¬p₀ with Fin-∃? (λ i → P (fsuc i)) (λ i → dec (fsuc i))
...   | yes (i , pᵢ) = yes (fsuc i , pᵢ)
...   | no ¬tail = no (λ { (fzero  , p) → ¬p₀ p
                        ; (fsuc i , p) → ¬tail (i , p) })

-- Dual: decide ∀ over Fin k (the chirality pair of Fin-∃?).
Fin-∀? : {k : ℕ} (P : Fin k → Set)
       → ((i : Fin k) → Dec (P i)) → Dec ((i : Fin k) → P i)
Fin-∀? {zero}  P dec = yes (λ ())
Fin-∀? {suc k} P dec with dec fzero
... | no ¬p₀ = no (λ all → ¬p₀ (all fzero))
... | yes p₀ with Fin-∀? (λ i → P (fsuc i)) (λ i → dec (fsuc i))
...   | no ¬tail = no (λ all → ¬tail (λ i → all (fsuc i)))
...   | yes tail = yes (λ { fzero → p₀ ; (fsuc i) → tail i })
