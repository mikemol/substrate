------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.EEAFold  (AI-17 B-EEA-FOLD, recursor)
--
-- The PolyEEATrace recursor — a faithful copy of Nat/GCD/Fold.eea-fold, the
-- single reuse hinge: any target T over the trace is computed structurally
-- (the Bézout fold B-EEA-FOLD-bez is one such target). gcd-fold-poly = the
-- forgetful read (returns the gcd g).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.EEAFold where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; PolyEEATrace; base; step)

eea-fold-poly :
  {T : QPoly → QPoly → QPoly → Set}
  (bi : (a : QPoly) → T a zero-q a)
  (si : {a g : QPoly} (d : ℕ) (f-lo : Vec F₂ (suc d)) →
        T (divisor-q d f-lo) (div-rem d f-lo a) g → T a (divisor-q d f-lo) g) →
  {a b g : QPoly} → PolyEEATrace a b g → T a b g
eea-fold-poly {T} bi si (base a)        = bi a
eea-fold-poly {T} bi si (step d f-lo s) = si d f-lo (eea-fold-poly {T} bi si s)

gcd-fold-poly : {a b g : QPoly} → PolyEEATrace a b g → QPoly
gcd-fold-poly = eea-fold-poly {T = λ _ _ _ → QPoly} (λ a → a) (λ _ _ rec → rec)

gcd-fold-poly-correct : {a b g : QPoly} (t : PolyEEATrace a b g) → gcd-fold-poly t ≡ g
gcd-fold-poly-correct (base a)        = refl
gcd-fold-poly-correct (step d f-lo s) = gcd-fold-poly-correct s
