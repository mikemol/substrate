------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Generic
--
-- F₂[x] via the GENERIC functor — the A=F₂ instance of `Polynomial.Graded.Over`
-- (AI-17). The mere fact that this `open` type-checks witnesses that F₂'s
-- hand-built `Polynomial.RingLaws` IS the generic graded-ring construction at
-- A=F₂: `_*P_` here is distrib + comm (`*P-comm`) + assoc (`*P-assoc`) + unital,
-- all from the one functor.
--
-- This is the NON-DESTRUCTIVE half of AI-17 B1-SPLIT's "supersede F₂ RingLaws":
-- it exhibits the A=F₂ instance WITHOUT swapping the concrete F₂.RingLaws (whose
-- `_*P_` is the `_+ⱽ_`/`_*ₛ_` build, not definitionally this recursive one, and
-- which GF256/Mul + MulLaws depend on). The generic copy is the REUSABLE artifact
-- (it also gives GF(2⁸)[y] etc.); the concrete F₂ copy stays as the optimized one.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Generic where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Eq using (_≡_; subst)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F

-- Poly n = Vec F₂ n ; _*P_, the ring laws (*P-comm, *P-assoc, …) all at A = F₂.
open F.Over F₂-CommRing public

-- the full graded ring laws land at A=F₂ (witnesses, parallel to GF256/Poly):
_ : (p q : Poly 3) (k : ℕ) → nth (p *P q) k ≡ convCoeff p q k
_ = nth-*P
_ : (p q : Poly 2) → p *P q ≡ subst Poly (+ℕ-comm 2 2) (q *P p)
_ = *P-comm
_ : (p q r : Poly 2) → subst Poly (+ℕ-assoc 2 2 2) ((p *P q) *P r) ≡ p *P (q *P r)
_ = *P-assoc
