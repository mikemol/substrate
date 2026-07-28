{-# OPTIONS --safe --without-K #-}
-- ⟡cube-reflect-nc/-sum/-reflmatch: reflect BOTH sides of the ℤ cube identity as
-- ZE over ρ=[px,py,pz,+qxn,+qyn,+qzn], prove each reflection FAITHFUL, and refl-match
-- their canonical forms — the binomial expansion done by the reflective normalizer.
--   N_C (factored) side: bridgeN : ⟦ e-N ⟧ ≡ Cur.N_C x y z   (qq≡Q110 glue via Ux/Vx)
--   sumNum Cᶠ (expanded) side: bridgeR : ⟦ e-R ⟧ ≡ CD.sumNum … Cᶠ   (one +ℤ-identityʳ)
--   the identity: same : norm e-N ≡ norm e-R = refl              (make-or-break)
module Substrate.Algebra.Q.JacCubeNorm where
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _∸_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; 1ℤ)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-identityʳ)
open import Substrate.Algebra.Q using (ℚ; num; den-1; mkℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-trans; ≈ℚ-sym)
open import Substrate.Algebra.Q.JacobianEvalNormalize using (evalℚ; normalize-eval; ≡→≈ℚ)
import Substrate.Algebra.Q.JacobianEvalCDCurried as Cur
import Substrate.Algebra.Q.JacobianEvalCD as CD
import Substrate.Algebra.Q.JacCube as JC
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
import Substrate.Algebra.Z.JacobianResidue as R
import Substrate.Algebra.Q.JacobianCollision as C

module _ (x y z : ℚ) where
  -- ⟡public-policy: explicit signatures so `suc` disambiguates to ℕ's
  -- constructor (Fin's `suc` is also in scope from Foundation.Fin.Fin).
  qxn qyn qzn : ℕ
  qxn = suc (den-1 x)
  qyn = suc (den-1 y)
  qzn = suc (den-1 z)
  px = num x
  py = num y
  pz = num z

  open import Substrate.Algebra.Z.ZRingNorm 6
    (px ∷ py ∷ pz ∷ (+ qxn) ∷ (+ qyn) ∷ (+ qzn) ∷ [])
  open import Substrate.Algebra.Z.ZRingNorm.Sound 6
    (px ∷ py ∷ pz ∷ (+ qxn) ∷ (+ qyn) ∷ (+ qzn) ∷ [])

  v0 = var Fin.zero
  v1 = var (Fin.suc Fin.zero)
  v2 = var (Fin.suc (Fin.suc Fin.zero))
  v3 = var (Fin.suc (Fin.suc (Fin.suc Fin.zero)))
  v4 = var (Fin.suc (Fin.suc (Fin.suc (Fin.suc Fin.zero))))
  v5 = var (Fin.suc (Fin.suc (Fin.suc (Fin.suc (Fin.suc Fin.zero)))))

  -- a var-power tower, mirroring powℤ (base +1, step atom ⊗ tail).
  powE : ZE → ℕ → ZE
  powE a zero    = lit (+ 1)
  powE a (suc n) = a ⊗ powE a n

  ----------------------------------------------------------------------
  -- ⟡cube-reflect-nc : the factored side N_C = N1 +ℤ N2.
  ----------------------------------------------------------------------
  e-Ux e-Vx e-N1 e-N2 e-N : ZE
  e-Ux = (lit (+ 1) ⊗ (v3 ⊗ v4)) ⊕ ((v0 ⊗ v1) ⊗ lit (+ 1))
  e-Vx = (lit (+ 4) ⊗ (v3 ⊗ v4)) ⊕ ((lit (+ 3) ⊗ (v0 ⊗ v1)) ⊗ lit (+ 1))
  e-N1 = (v2 ⊗ (e-Ux ⊗ (e-Ux ⊗ e-Ux))) ⊗ v4
  e-N2 = ((((v1 ⊗ v1) ⊗ e-Ux) ⊗ e-Vx) ⊗ v3) ⊗ v5
  e-N  = e-N1 ⊕ e-N2

  bridgeUx : ⟦ e-Ux ⟧ ≡ Cur.Ux x y z
  bridgeUx = cong (λ w → ((+ 1) *ℤ w) +ℤ ((px *ℤ py) *ℤ (+ 1)))
                  (cong +_ (Cur.qq≡Q110 x y z))

  bridgeVx : ⟦ e-Vx ⟧ ≡ Cur.Vx x y z
  bridgeVx = cong (λ w → ((+ 4) *ℤ w) +ℤ (((+ 3) *ℤ (px *ℤ py)) *ℤ (+ 1)))
                  (cong +_ (Cur.qq≡Q110 x y z))

  bridgeN : ⟦ e-N ⟧ ≡ Cur.N_C x y z
  bridgeN = cong₂ _+ℤ_
    (cong (λ u → (pz *ℤ (u *ℤ (u *ℤ u))) *ℤ (+ qyn)) bridgeUx)
    (cong₂ (λ u v → ((((py *ℤ py) *ℤ u) *ℤ v) *ℤ (+ qxn)) *ℤ (+ qzn))
           bridgeUx bridgeVx)

  ----------------------------------------------------------------------
  -- ⟡cube-reflect-sum : the expanded side sumNum Cᶠ (padNum's 7-term tree).
  -- Each monomial (mono a b c) k → k · px^a py^b pz^c · qx^(3-a) qy^(4-b) qz^(1-c).
  ----------------------------------------------------------------------
  eR0 eR1 eR2 eR3 eR4 eR5 eR6 e-R : ZE
  eR0 = (lit (+ 1) ⊗ (powE v0 0 ⊗ (powE v1 0 ⊗ powE v2 1))) ⊗ (powE v3 3 ⊗ (powE v4 4 ⊗ powE v5 0))
  eR1 = (lit (+ 3) ⊗ (powE v0 1 ⊗ (powE v1 1 ⊗ powE v2 1))) ⊗ (powE v3 2 ⊗ (powE v4 3 ⊗ powE v5 0))
  eR2 = (lit (+ 3) ⊗ (powE v0 2 ⊗ (powE v1 2 ⊗ powE v2 1))) ⊗ (powE v3 1 ⊗ (powE v4 2 ⊗ powE v5 0))
  eR3 = (lit (+ 1) ⊗ (powE v0 3 ⊗ (powE v1 3 ⊗ powE v2 1))) ⊗ (powE v3 0 ⊗ (powE v4 1 ⊗ powE v5 0))
  eR4 = (lit (+ 4) ⊗ (powE v0 0 ⊗ (powE v1 2 ⊗ powE v2 0))) ⊗ (powE v3 3 ⊗ (powE v4 2 ⊗ powE v5 1))
  eR5 = (lit (+ 7) ⊗ (powE v0 1 ⊗ (powE v1 3 ⊗ powE v2 0))) ⊗ (powE v3 2 ⊗ (powE v4 1 ⊗ powE v5 1))
  eR6 = (lit (+ 3) ⊗ (powE v0 2 ⊗ (powE v1 4 ⊗ powE v2 0))) ⊗ (powE v3 1 ⊗ (powE v4 0 ⊗ powE v5 1))
  e-R = eR0 ⊕ (eR1 ⊕ (eR2 ⊕ (eR3 ⊕ (eR4 ⊕ (eR5 ⊕ eR6)))))

  bridgeR : ⟦ e-R ⟧ ≡ CD.sumNum x y z 3 4 1 JC.Cᶠ
  bridgeR = cong (⟦ eR0 ⟧ +ℤ_)
            (cong (⟦ eR1 ⟧ +ℤ_)
            (cong (⟦ eR2 ⟧ +ℤ_)
            (cong (⟦ eR3 ⟧ +ℤ_)
            (cong (⟦ eR4 ⟧ +ℤ_)
            (cong (⟦ eR5 ⟧ +ℤ_)
                  (sym (+ℤ-identityʳ ⟦ eR6 ⟧)))))))

  ----------------------------------------------------------------------
  -- ⟡cube-reflmatch : the binomial identity, by the normalizer's canonical form.
  ----------------------------------------------------------------------
  same : norm e-N ≡ norm e-R
  same = refl

  ----------------------------------------------------------------------
  -- ⟡cube-identity : the ℤ cube identity, from the norm-sound sandwich.
  --   sumNum Cᶠ ≡ ⟦e-R⟧ ≡ evalC(norm e-R) ≡ evalC(norm e-N) ≡ ⟦e-N⟧ ≡ N_C
  ----------------------------------------------------------------------
  cube : CD.sumNum x y z 3 4 1 JC.Cᶠ ≡ Cur.N_C x y z
  cube = trans (sym bridgeR)
         (trans (norm-sound e-R)
         (trans (cong evalC (sym same))
         (trans (sym (norm-sound e-N)) bridgeN)))

  ----------------------------------------------------------------------
  -- ⟡identify1 : the ℚ payoff.  evalℚ R.f₁ ≈ℚ C.f₁, via the common-denominator
  -- route — the 781 MB residue paid down through the reflective normalizer.
  --   evalℚ R.f₁ ≈ evalℚ(normalize R.f₁) ≡ evalℚ(normalize Cᶠ) ≈ evalℚ Cᶠ
  --            ≈ evalCD Cᶠ = mkℚ (sumNum Cᶠ) Dden ≡[cube] mkℚ N_C Dden ≈ C.f₁
  ----------------------------------------------------------------------
  identify₁ : evalℚ x y z R.f₁ ≈ℚ C.f₁ x y z
  identify₁ =
    ≈ℚ-trans {evalℚ x y z R.f₁} {evalℚ x y z JC.Cᶠ} {C.f₁ x y z}
      (≈ℚ-trans {evalℚ x y z R.f₁} {evalℚ x y z (normalize R.f₁)} {evalℚ x y z JC.Cᶠ}
        (normalize-eval x y z R.f₁)
        (≈ℚ-trans {evalℚ x y z (normalize R.f₁)} {evalℚ x y z (normalize JC.Cᶠ)}
                  {evalℚ x y z JC.Cᶠ}
          (≡→≈ℚ (cong (evalℚ x y z) JC.bridgeᶠ))
          (≈ℚ-sym {evalℚ x y z JC.Cᶠ} {evalℚ x y z (normalize JC.Cᶠ)}
                  (normalize-eval x y z JC.Cᶠ))))
      (≈ℚ-trans {evalℚ x y z JC.Cᶠ}
                {mkℚ (Cur.N_C x y z) (CD.Dden x y z 3 4 1 ∸ 1)} {C.f₁ x y z}
        (≈ℚ-trans {evalℚ x y z JC.Cᶠ} {CD.evalCD x y z 3 4 1 JC.Cᶠ}
                  {mkℚ (Cur.N_C x y z) (CD.Dden x y z 3 4 1 ∸ 1)}
          (CD.evalCD-sound x y z 3 4 1 JC.Cᶠ
             (CD.buildB x y z 3 4 1 JC.Cᶠ record {}))
          (≡→≈ℚ (cong (λ n → mkℚ n (CD.Dden x y z 3 4 1 ∸ 1)) cube)))
        (≈ℚ-sym {C.f₁ x y z} {mkℚ (Cur.N_C x y z) (CD.Dden x y z 3 4 1 ∸ 1)}
                (Cur.evalCD_C x y z)))
