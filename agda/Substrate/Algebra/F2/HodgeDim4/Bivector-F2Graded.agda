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

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec using (Vec; []; _∷_; zipWith)

open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2-CommutativeMonoid using (F₂-CommMonoid)
open import Substrate.Category.RGradedMonoid
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.CongTrans

------------------------------------------------------------------------
-- N-1: weight-parity — XOR of all entries.
------------------------------------------------------------------------

weight-parity : ∀ {n} → Vector n → F₂
weight-parity []      = 𝟘
weight-parity (x ∷ v) = x +F weight-parity v

------------------------------------------------------------------------
-- N-2: weight-parity is additive over +ⱽ.
--
-- weight-parity (u +ⱽ v) ≡ weight-parity u +F weight-parity v
--
-- Proof: structural induction on Vec, plus F₂ +-assoc +F +-comm
-- shuffle.
------------------------------------------------------------------------

shuffle :
  (x y a b : F₂) →
  (x +F y) +F (a +F b) ≡ (x +F a) +F (y +F b)
shuffle x y a b =
  trans (+-assoc x y (a +F b))
  (cong-trans (x +F_) (sym (+-assoc y a b))
  (cong-trans (λ z → x +F (z +F b)) (+-comm y a)
  (cong-trans (x +F_) (+-assoc a y b)
         (sym (+-assoc x a (y +F b))))))
  where
    open import Substrate.Foundation.Eq.Sym

weight-parity-+ⱽ :
  ∀ {n} (u v : Vector n) →
  weight-parity (u +ⱽ v) ≡ weight-parity u +F weight-parity v
weight-parity-+ⱽ []      []      = refl
weight-parity-+ⱽ (x ∷ u) (y ∷ v) =
  cong-trans ((x +F y) +F_) (weight-parity-+ⱽ u v)
             (shuffle x y (weight-parity u) (weight-parity v))

------------------------------------------------------------------------
-- N-3: Bivector as F₂-graded monoid.
------------------------------------------------------------------------

Bivector-F2Graded : RGradedMonoid F₂-CommMonoid Bivector
Bivector-F2Graded = record
  { _·_         = _+ⱽ_
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
