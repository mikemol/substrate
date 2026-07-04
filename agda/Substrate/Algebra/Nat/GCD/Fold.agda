------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.Fold
--
-- EEATrace as a free term algebra: `eea-fold` is its universal eval. It
-- needs only an interpretation of the base case and the wedge step in some
-- target T — "EEATrace doesn't care what it operates over, so long as the
-- target supports the step." Different targets = different number-theoretic
-- extractions of the SAME free trace:
--   * gcd-fold     — the forgetful (annihilating) fold: returns the value g.
--   * bezout-ℤ     — the wedge fold: returns the Bézout bridge (Z.Bezout).
--   * CRT, Euler   — further targets ("change the type again").
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.Fold where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Algebra.Nat.GCD.Wedge using (remainder) renaming (Wedge to Wedge⟦b7e6a995⟧)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)

-- the universal fold (= EEATrace's recursor, named so targets are swappable).
eea-fold :
  {T : ℕ → ℕ → ℕ → Set}
  (base-interp : (a : ℕ) → T a 0 a)
  (step-interp : {a g : ℕ} (b : ℕ) (w : Wedge⟦b7e6a995⟧ a (suc b)) →
                 T (suc b) (remainder w) g → T a (suc b) g) →
  {a b g : ℕ} → EEATrace a b g → T a b g
eea-fold {T} bi si (base a)       = bi a
eea-fold {T} bi si (step b w sub) = si b w (eea-fold {T} bi si sub)

-- the FORGETFUL fold: collapse the trace to the gcd value (the residue).
gcd-fold : {a b g : ℕ} → EEATrace a b g → ℕ
gcd-fold t = eea-fold {T = λ _ _ _ → ℕ} (λ a → a) (λ _ _ rec → rec) t

-- it returns exactly the trace's gcd index — the annihilating quotient.
gcd-fold-correct : {a b g : ℕ} (t : EEATrace a b g) → gcd-fold t ≡ g
gcd-fold-correct (base a)       = refl
gcd-fold-correct (step b w sub) = gcd-fold-correct sub

------------------------------------------------------------------------
-- THE UNIVERSAL PROPERTY (making the header's "universal eval" a theorem,
-- Ⓤ.eea-fold-freeup). EEATrace is the INITIAL ALGEBRA of the (base/step)
-- functor; `eea-fold bi si` is the UNIQUE algebra morphism out — any `h` that
-- agrees with `bi` on `base` and with `si` on `step` IS `eea-fold bi si`.
--
-- This is the ∃! that grounds the groupoid-distance claim: the interconnect's
-- HUB (the fold-table) is a universal arrow. It is the INDEXED-initial-algebra
-- sibling of the Set-basis `Category.FreeUniversalProperty.FreeUP` (free monoid
-- etc.) and the exact DUAL of the terminal-coalgebra `R.Trace.Final.ana-unique`
-- (RealTrace) — induction here, corecursion there. (eea-fold is NOT a FreeUP
-- instance: FreeUP is free-over-a-Set-basis; eea-fold recurses an indexed
-- family. Same universality, different shape.)
------------------------------------------------------------------------

eea-fold-unique :
  {T : ℕ → ℕ → ℕ → Set}
  (base-interp : (a : ℕ) → T a 0 a)
  (step-interp : {a g : ℕ} (b : ℕ) (w : Wedge⟦b7e6a995⟧ a (suc b)) →
                 T (suc b) (remainder w) g → T a (suc b) g)
  (h : {a b g : ℕ} → EEATrace a b g → T a b g)
  (h-base : (a : ℕ) → h (base a) ≡ base-interp a)
  (h-step : {a g : ℕ} (b : ℕ) (w : Wedge⟦b7e6a995⟧ a (suc b))
            (sub : EEATrace (suc b) (remainder w) g) →
            h (step b w sub) ≡ step-interp b w (h sub)) →
  {a b g : ℕ} (t : EEATrace a b g) → h t ≡ eea-fold {T} base-interp step-interp t
eea-fold-unique bi si h h-base h-step (base a)       = h-base a
eea-fold-unique {T} bi si h h-base h-step {a = a} {g = g} (step b w sub) =
  trans (h-step b w sub)
        (cong (si {a} {g} b w) (eea-fold-unique {T} bi si h h-base h-step sub))
