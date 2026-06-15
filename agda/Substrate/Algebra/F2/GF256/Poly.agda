------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Poly
--
-- GF(2⁸)[y] — the graded polynomial ring over GF(2⁸), instantiating the
-- generic `Graded.Over` at the GF(2⁸) `CommutativeRing`. This is the
-- coefficient level of the AES "column ring" GF(2⁸)[y]/(y⁴+1) (the quotient
-- is AI-17 B2/B3). It is also the FAITHFULNESS CHECK for the generic
-- construction: GF(2⁸) is a NON-F₂ coefficient ring, so the mere fact that
-- the abstract proofs instantiate here witnesses that no F₂-specific
-- assumption was baked into `Graded.Over`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Poly where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.GF256.CommRing using (GF256-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F

-- Poly n = Vec (Vector 8) n ; _*P_, nth-*P, *P-distribʳ/ˡ, *P-scalarˡ/ʳ, … all at GF(2⁸).
open F.Over GF256-CommRing public

-- explicit faithfulness witnesses (the bridge + a bilinear + a scalar law, at GF(2⁸)):
_ : (p q : Poly 4) (k : ℕ) → nth (p *P q) k ≡ convCoeff p q k
_ = nth-*P
_ : (p q r : Poly 4) → (p +P q) *P r ≡ (p *P r) +P (q *P r)
_ = *P-distribʳ
_ : (c : Vector 8) (p q : Poly 4) → (c ·c p) *P q ≡ c ·c (p *P q)
_ = *P-scalarˡ
