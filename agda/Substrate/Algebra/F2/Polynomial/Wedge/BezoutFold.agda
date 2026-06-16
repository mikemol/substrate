------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold  (B-EEA-FOLD-bez, part 1/2)
--
-- The polynomial Bézout fold over F₂[x] — the residual-fold (allegory ALG-6)
-- over `PolyEEATrace`, producing the (s, t) with s·a + t·b = g, whose g=𝟙 case
-- gives the GF(2⁸) inverse (B-EEA-INV → AI-8).  Faithful port of `Z/Bezout`
-- (the BezoutℤWitness / base-bezout / step-bezout / eea-fold archetype),
-- retyped for F₂[x].
--
-- FORMULATION (either/or RESOLVED by this compiling artifact): convCoeff/nth
-- form, NOT a truncation-ring + pad.  The naive invariant `s *P a +P t *P b ≡ g`
-- is ill-typed (`*P` is length-additive ⇒ the `+P` operands differ in length).
-- Stating it COEFFICIENT-WISE via `convCoeff` (which needs no length match) is
-- exactly the `recon-nth` method, and reuses that machinery directly
-- (`convCoeff-distrib`, `convCoeff-distribˡ`, `convCoeff-scalarˡ`, `nth-*P`).
--
-- DONE HERE (part 1): the witness type + the base case.
--   * `BezoutNthWitness a b g` = ∃ s t : QPoly, ∀k. convCoeff s a k + convCoeff t b k ≡ nth g k.
--   * `convCoeff-one` : convCoeff [𝟙] v ≡ nth v (the *P-identityˡ in convCoeff form).
--   * `base-bezout-poly` : gcd(a,0)=a, bridge 1·a + 0·0 = a.
--
-- REMAINING (part 2 — `step-bezout-poly` + `bezout-poly`): the back-substitution.
-- From a step `PolyEEATrace a (divisor-q d f-lo) g` built on the sub-trace
-- `PolyEEATrace (divisor-q d f-lo) (div-rem d f-lo a) g`, the recurrence is the
-- char-2 form of Z/Bezout's `(s',t') ↦ (t', s' − t'·q)`, i.e. (s',t') ↦
-- (t', s' +P t'*P (div-quot …)).  Proof obligation (convCoeff form, ∀k):
--   convCoeff t' a k + convCoeff (s' + t'·q) (divisor) k ≡ nth g k
-- from the sub-invariant  convCoeff s' (divisor) k + convCoeff t' (div-rem) k ≡ nth g k,
-- using `recon-nth` (a ≡ q·divisor + rem, coefficient-wise), `convCoeff-distrib`,
-- a convCoeff-associativity (convCoeff t' (q·X) = convCoeff (t'·q) X), and char-2
-- `x+x≡𝟘` to cancel the (t'·q)·divisor terms.  The new coefficient `s' + t'·q`
-- is formed with `pad-end` (zero-pad to align lengths; `nth-pad-end` invariant).
-- Then `bezout-poly = eea-fold-poly base-bezout-poly step-bezout-poly`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; trans)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
open F.Over F₂-CommRing
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly; zero-q)

-- convCoeff by the unit polynomial [𝟙] is nth (the *P-identityˡ, convCoeff form).
convCoeff-one : {n : ℕ} (v : Poly n) (k : ℕ) → convCoeff (𝟙 ∷ []) v k ≡ nth v k
convCoeff-one v zero    = *-identityˡ (nth v zero)
convCoeff-one v (suc k) = trans (+-identityʳ _) (*-identityˡ (nth v (suc k)))

-- the Bézout invariant, coefficient-wise (convCoeff form, avoiding the *P
-- length-mismatch — the recon-nth method): convCoeff s a + convCoeff t b = g, ∀k.
BezoutNthWitness : QPoly → QPoly → QPoly → Set
BezoutNthWitness a b g =
  Σ QPoly λ s → Σ QPoly λ t →
    (k : ℕ) → (convCoeff (proj₂ s) (proj₂ a) k + convCoeff (proj₂ t) (proj₂ b) k)
              ≡ nth (proj₂ g) k

-- base: gcd(a, 0) = a; bridge 1·a + 0·0 = a.
base-bezout-poly : (a : QPoly) → BezoutNthWitness a zero-q a
base-bezout-poly a =
  (suc zero , (𝟙 ∷ [])) , zero-q ,
  (λ k → trans (+-identityʳ _) (convCoeff-one (proj₂ a) k))
