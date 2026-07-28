------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Generic
--
-- F₂[x] via the GENERIC functor — `Polynomial.Graded.Over` instantiated at A=F₂.
--
-- WHAT THIS MECHANIZES (the `open` type-checks): the functor applies to F₂, i.e. a
-- graded-ring construction exists at A=F₂ with `_*P_` distrib + comm (`*P-comm`) +
-- assoc (`*P-assoc`) + unital, all from the one functor. With GF256/Poly (A=GF(2⁸)),
-- this is a second witness that the functor is faithful on a real coefficient ring.
--
-- WHAT THIS DOES NOT MECHANIZE: that this construction EQUALS F₂'s hand-built
-- `Polynomial.RingLaws`. They are parallel — this `_*P_` is the recursive `_+P_`/`_·c_`
-- build, F₂'s is the `_+ⱽ_`/`_*ₛ_` build, NOT definitionally equal — and GF256/Mul +
-- MulLaws consume the concrete one. Their equivalence is asserted, not proven; the
-- payment is to MECHANIZE `concrete _*P_ ≡ generic _*P_` (the faithfulness theorem,
-- AI-17 B-FAITH) — which is what would let a consumer use either, or safely unify them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Generic where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
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
