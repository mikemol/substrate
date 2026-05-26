------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector-F2Graded
--
-- Bivector (= Vector 6) packaged as an F₂-graded monoid via the
-- weight-parity grading.
--
-- weight-parity of a Vec F₂ 6 = XOR of all 6 entries = number of 𝟙s
-- mod 2. This is the "even-weight" vs "odd-weight" split (Z/2-grading
-- on the binary code).
--
-- Per [[project-3plus1-as-graded-cocycle]]: the Bivector's natural
-- F₂-grading. The self-dual subspace and anti-self-dual axis at F₂
-- are NOT this grading (they're the Hodge ★ involution's orbit
-- decomposition); weight-parity is a separate F₂-grading.
--
-- This is the substrate's first F₂-graded structure outside the
-- Coxeter-Word family. Demonstrates that the GradedMonoid /
-- RGradedMonoid records apply to arbitrary F₂-algebraic structures,
-- not just word algebras.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector-F2Graded where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; zipWith)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong; cong₂; cong-trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2-CommutativeMonoid using (F₂-CommMonoid)
open import Substrate.Category.RGradedMonoid

------------------------------------------------------------------------
-- N-1: weight-parity — XOR of all entries.
------------------------------------------------------------------------

weight-parity : ∀ {n} → Vector n → F₂
weight-parity []      = 𝟘
weight-parity (x ∷ v) = x + weight-parity v

------------------------------------------------------------------------
-- N-2: weight-parity is additive over +ⱽ.
--
-- weight-parity (u +ⱽ v) ≡ weight-parity u + weight-parity v
--
-- Proof: structural induction on Vec, plus F₂ +-assoc + +-comm
-- shuffle.
------------------------------------------------------------------------

shuffle :
  (x y a b : F₂) →
  (x + y) + (a + b) ≡ (x + a) + (y + b)
shuffle x y a b =
  trans (+-assoc x y (a + b))
  (cong-trans (x +_) (sym (+-assoc y a b))
  (cong-trans (λ z → x + (z + b)) (+-comm y a)
  (cong-trans (x +_) (+-assoc a y b)
         (sym (+-assoc x a (y + b))))))
  where
    open import Substrate.Foundation.Eq using (sym)

weight-parity-+ⱽ :
  ∀ {n} (u v : Vector n) →
  weight-parity (u +ⱽ v) ≡ weight-parity u + weight-parity v
weight-parity-+ⱽ []      []      = refl
weight-parity-+ⱽ (x ∷ u) (y ∷ v) =
  cong-trans ((x + y) +_) (weight-parity-+ⱽ u v)
             (shuffle x y (weight-parity u) (weight-parity v))

------------------------------------------------------------------------
-- N-3: Bivector as F₂-graded monoid.
------------------------------------------------------------------------

Bivector-F2Graded : RGradedMonoid F₂-CommMonoid _
Bivector-F2Graded = record
  { M           = Bivector
  ; _·_         = _+ⱽ_
  ; ε           = 𝟎ⱽ
  ; ·-assoc     = +ⱽ-assoc
  ; ·-identityˡ = +ⱽ-identityˡ
  ; ·-identityʳ = +ⱽ-identityʳ
  ; degree      = weight-parity
  ; degree-ε    = refl
  ; degree-·    = weight-parity-+ⱽ
  }

------------------------------------------------------------------------
-- N-4: Capstone.
--
-- After this slice, Bivector is the substrate's first F₂-graded
-- vector-space-like structure (not a Coxeter word). The weight-parity
-- grading splits Bivector as "even-weight" (degree 𝟘) vs "odd-weight"
-- (degree 𝟙) — the standard binary-code parity split.
--
-- The Hodge ★ involution and self-dual decomposition are a SEPARATE
-- F₂-structure (orbit decomposition under ★) not captured by weight-
-- parity. They would be a different RGradedMonoid instance, or a
-- non-graded structural decomposition.
--
-- Per [[project-3plus1-as-graded-cocycle]]: Bivector's natural
-- F₂-grading is weight-parity; the 3+1 self-dual structure is
-- carrier-set decomposition under ★, not weight-parity.
------------------------------------------------------------------------
