------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold  (B-EEA-FOLD-bez, parts 1+1.5/2)
--
-- The polynomial Bézout fold over F₂[x] — the residual-fold (allegory ALG-6)
-- over `PolyEEATrace`, producing the (s, t) with s·a + t·b = g, whose g=𝟙 case
-- gives the GF(2⁸) inverse (B-EEA-INV → AI-8).  Faithful port of `Z/Bezout`,
-- retyped for F₂[x].
--
-- FORMULATION (either/or RESOLVED by the build): convCoeff/nth form, NOT a
-- truncation-ring + pad.  The naive `s *P a +P t *P b ≡ g` is ill-typed (`*P`
-- length-additive ⇒ the `+P` operands differ in length).  Stated COEFFICIENT-
-- WISE via `convCoeff` (no length match needed) — the `recon-nth` method —
-- reusing that machinery (`convCoeff-distrib`, `nth-*P`, `*P-assoc`, …).
--
-- DONE (part 1): the witness type + base case.
-- DONE (part 1.5 — the step's reusable infrastructure):
--   * `+-self`              — char-2 self-cancellation x + x ≡ 𝟘.
--   * `convCoeff-cong-r`    — convCoeff congruent in arg 2 under pointwise nth-eq.
--   * `convCoeff-subst-l`   — subst on arg 1 is invisible to convCoeff.
--   * `convCoeff-replicate-zero`, `convCoeff-pad-endˡ` — zero/high-pad invisible to arg 1.
--   * `convCoeff-assoc`     — convCoeff t (q·B) ≡ convCoeff (t·q) B (via *P-assoc).
--
-- REMAINING (part 2 — `step-bezout-poly` + `bezout-poly`): the back-substitution
-- assembly.  Recurrence (char-2 of Z/Bezout's (s',t')↦(t',s'−t'·q)):
--   new s = t' ;  new t = s' +P (t' *P q)   [q = q-div (proj₂ a), via pad-end + a
--   length-comm subst on the t'·q summand so the +P operands align].
-- Obligation (∀k):  convCoeff t' a k + convCoeff (s'+t'·q) B k ≡ nth g k.
--   • split new-t via `convCoeff-distrib` + `convCoeff-pad-endˡ`/`convCoeff-subst-l`
--     ⇒ convCoeff s' B k + convCoeff (t'·q) B k.
--   • expand convCoeff t' a via `recon-nth` (a ≡ q·B + R coefficient-wise): build the
--     padded sum P_a = (q*P B) +P pad(R), use `convCoeff-cong-r` (nth P_a ≡ nth a),
--     `convCoeff-distribˡ`, `convCoeff-assoc` ⇒ convCoeff (t'·q) B k + convCoeff t' R k.
--   • the two convCoeff (t'·q) B k terms cancel by `+-self` (char 2); `+-comm` + the
--     sub-invariant `convCoeff s' B k + convCoeff t' R k ≡ nth g k` close it.
-- Then `bezout-poly = eea-fold-poly base-bezout-poly step-bezout-poly`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
open F.Over F₂-CommRing
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly; zero-q)

private variable n m l : ℕ

-- convCoeff by the unit polynomial [𝟙] is nth (the *P-identityˡ, convCoeff form).
convCoeff-one : (v : Poly n) (k : ℕ) → convCoeff (𝟙 ∷ []) v k ≡ nth v k
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

------------------------------------------------------------------------
-- the step's reusable infrastructure (part 1.5).
------------------------------------------------------------------------

-- char-2 self-cancellation.
+-self : (x : F2.F₂) → x + x ≡ 𝟘
+-self F2.𝟘 = refl
+-self F2.𝟙 = refl

-- convCoeff is congruent in its 2nd argument under pointwise nth-equality.
convCoeff-cong-r : (p : Poly n) {q : Poly m} {q' : Poly l}
                 → ((j : ℕ) → nth q j ≡ nth q' j)
                 → (k : ℕ) → convCoeff p q k ≡ convCoeff p q' k
convCoeff-cong-r []      h k       = refl
convCoeff-cong-r (a ∷ p) h zero    = cong (a *_) (h zero)
convCoeff-cong-r (a ∷ p) h (suc k) = cong₂ _+_ (cong (a *_) (h (suc k))) (convCoeff-cong-r p h k)

-- subst on the 1st argument is invisible to convCoeff.
convCoeff-subst-l : {n n' : ℕ} (eq : n ≡ n') (v : Poly n) (X : Poly m) (k : ℕ)
                  → convCoeff (subst Poly eq v) X k ≡ convCoeff v X k
convCoeff-subst-l refl v X k = refl

-- convCoeff by an all-zero first argument is 𝟘.
convCoeff-replicate-zero : (j : ℕ) (X : Poly m) (k : ℕ) → convCoeff (replicate j 𝟘) X k ≡ 𝟘
convCoeff-replicate-zero zero    X k       = refl
convCoeff-replicate-zero (suc j) X zero    = *-absorbˡ (nth X zero)
convCoeff-replicate-zero (suc j) X (suc k) =
  trans (cong₂ _+_ (*-absorbˡ (nth X (suc k))) (convCoeff-replicate-zero j X k)) (+-identityˡ 𝟘)

-- pad-end (high-zero padding) is invisible to convCoeff in the 1st argument.
convCoeff-pad-endˡ : (j : ℕ) (v : Poly n) (X : Poly m) (k : ℕ)
                   → convCoeff (pad-end j v) X k ≡ convCoeff v X k
convCoeff-pad-endˡ j []      X k       = convCoeff-replicate-zero j X k
convCoeff-pad-endˡ j (a ∷ v) X zero    = refl
convCoeff-pad-endˡ j (a ∷ v) X (suc k) = cong ((a * nth X (suc k)) +_) (convCoeff-pad-endˡ j v X k)

-- convCoeff associativity: t·(q·B) coefficients = (t·q)·B coefficients.
convCoeff-assoc : (t : Poly n) (q : Poly m) (B : Poly l) (k : ℕ)
                → convCoeff t (q *P B) k ≡ convCoeff (t *P q) B k
convCoeff-assoc {n} {m} {l} t q B k =
  trans (sym (nth-*P t (q *P B) k))
  (trans (cong (λ z → nth z k) (sym (*P-assoc t q B)))
  (trans (nth-subst (+ℕ-assoc n m l) ((t *P q) *P B) k)
         (nth-*P (t *P q) B k)))
