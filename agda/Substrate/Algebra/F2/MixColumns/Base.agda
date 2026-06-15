{-# OPTIONS --safe --without-K #-}
-- AI-9 MixColumns (file-per-test, memory-bounded). Base: fully-generic structural
-- primitives (abstract gmul ⇒ no constant-gmul normalization) + the byte constants/values.
module Substrate.Algebra.F2.MixColumns.Base where
open import Substrate.Algebra.F2 using (𝟘; 𝟙) public
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; 𝟎ⱽ; +ⱽ-identityˡ; +ⱽ-identityʳ;
  +ⱽ-comm; +ⱽ-assoc) public
open import Substrate.Algebra.F2.GF256 using (gmul; gmul-distribˡ; gmul-distribʳ; gmul-assoc;
  gmul-identityˡ; gmul-identityʳ; gmul-zeroˡ; +ⱽ-rearrange) public
open import Substrate.Foundation.Vec using (Vec; []; _∷_) public
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂) public

c01 c02 c03 c09 c0b c0d c0e : Vector 8
c01 = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
c02 = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
c03 = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
c09 = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
c0b = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
c0d = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
c0e = 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b1c b12 b16 b1d b1a b17 b1b : Vector 8
b1c = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b12 = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b16 = 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b1d = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b1a = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b17 = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b1b = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []

-- fully-generic (no constant appears): cheap to check & to instantiate.
dot4 : (c0 c1 c2 c3 a0 a1 a2 a3 : Vector 8) → Vector 8
dot4 c0 c1 c2 c3 a0 a1 a2 a3 = (gmul c0 a0 +ⱽ gmul c1 a1) +ⱽ (gmul c2 a2 +ⱽ gmul c3 a3)
gmul-dot4 : (k c0 c1 c2 c3 a0 a1 a2 a3 : Vector 8) → gmul k (dot4 c0 c1 c2 c3 a0 a1 a2 a3)
          ≡ dot4 (gmul k c0) (gmul k c1) (gmul k c2) (gmul k c3) a0 a1 a2 a3
gmul-dot4 k c0 c1 c2 c3 a0 a1 a2 a3 =
  trans (gmul-distribˡ k (gmul c0 a0 +ⱽ gmul c1 a1) (gmul c2 a2 +ⱽ gmul c3 a3))
        (cong₂ _+ⱽ_ (trans (gmul-distribˡ k (gmul c0 a0) (gmul c1 a1))
                 (cong₂ _+ⱽ_ (sym (gmul-assoc k c0 a0)) (sym (gmul-assoc k c1 a1))))
          (trans (gmul-distribˡ k (gmul c2 a2) (gmul c3 a3))
                 (cong₂ _+ⱽ_ (sym (gmul-assoc k c2 a2)) (sym (gmul-assoc k c3 a3)))))
dot4-add : (p0 p1 p2 p3 q0 q1 q2 q3 a0 a1 a2 a3 : Vector 8)
         → dot4 p0 p1 p2 p3 a0 a1 a2 a3 +ⱽ dot4 q0 q1 q2 q3 a0 a1 a2 a3
         ≡ dot4 (p0 +ⱽ q0) (p1 +ⱽ q1) (p2 +ⱽ q2) (p3 +ⱽ q3) a0 a1 a2 a3
dot4-add p0 p1 p2 p3 q0 q1 q2 q3 a0 a1 a2 a3 =
  trans (+ⱽ-rearrange (gmul p0 a0 +ⱽ gmul p1 a1) (gmul p2 a2 +ⱽ gmul p3 a3)
                      (gmul q0 a0 +ⱽ gmul q1 a1) (gmul q2 a2 +ⱽ gmul q3 a3))
  (trans (cong₂ _+ⱽ_ (+ⱽ-rearrange (gmul p0 a0) (gmul p1 a1) (gmul q0 a0) (gmul q1 a1))
                     (+ⱽ-rearrange (gmul p2 a2) (gmul p3 a3) (gmul q2 a2) (gmul q3 a3)))
         (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (sym (gmul-distribʳ p0 q0 a0)) (sym (gmul-distribʳ p1 q1 a1)))
           (cong₂ _+ⱽ_ (sym (gmul-distribʳ p2 q2 a2)) (sym (gmul-distribʳ p3 q3 a3)))))
dot4-cong : (a0 a1 a2 a3 : Vector 8) {E0 E1 E2 E3 F0 F1 F2 F3 : Vector 8}
          → E0 ≡ F0 → E1 ≡ F1 → E2 ≡ F2 → E3 ≡ F3
          → dot4 E0 E1 E2 E3 a0 a1 a2 a3 ≡ dot4 F0 F1 F2 F3 a0 a1 a2 a3
dot4-cong a0 a1 a2 a3 q0 q1 q2 q3 =
  cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (cong (λ z → gmul z a0) q0) (cong (λ z → gmul z a1) q1))
             (cong₂ _+ⱽ_ (cong (λ z → gmul z a2) q2) (cong (λ z → gmul z a3) q3))

-- THE circulant equivariance kernel: rotating the inputs one step equals rotating the
-- coefficients one step the other way — a single 4-term +ⱽ abelian reassociation, abstract
-- over all 8 args. Every coordinate of mix/inv's rotation-equivariance is one instance.
dot4-cyc : (c0 c1 c2 c3 a0 a1 a2 a3 : Vector 8)
         → dot4 c0 c1 c2 c3 a3 a0 a1 a2 ≡ dot4 c1 c2 c3 c0 a0 a1 a2 a3
dot4-cyc c0 c1 c2 c3 a0 a1 a2 a3 = cyc4 (gmul c0 a3) (gmul c1 a0) (gmul c2 a1) (gmul c3 a2)
  where
    -- (w +ⱽ x) +ⱽ (y +ⱽ z) ≡ (x +ⱽ y) +ⱽ (z +ⱽ w): a one-step cyclic shift of a 4-XOR.
    cyc4 : (w x y z : Vector 8) → (w +ⱽ x) +ⱽ (y +ⱽ z) ≡ (x +ⱽ y) +ⱽ (z +ⱽ w)
    cyc4 w x y z =
      trans (+ⱽ-assoc w x (y +ⱽ z))
      (trans (cong (w +ⱽ_) (sym (+ⱽ-assoc x y z)))
      (trans (+ⱽ-comm w ((x +ⱽ y) +ⱽ z))
             (+ⱽ-assoc (x +ⱽ y) z w)))
