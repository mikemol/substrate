{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEvalCDCurried — ⟡jac-lit1-cd-curried (Route 2).
--
-- The DUAL common-denominator evaluator: a memory-cheap FACTORED normal form
-- for the CURRIED ℚ map `C.f₁ = z·(1+xy)³ + y²·(1+xy)·(4+3xy)`, over the SAME
-- fixed denominator `Dden = qx³·qy⁴·qz` that `JacobianEvalCD.evalCD` uses for
-- the sparse `MPoly` side (box (3,4,1)).
--
--   evalCD_C : (x y z : ℚ) → C.f₁ x y z ≈ℚ mkℚ (N_C x y z) (Dden ∸ 1)
--
-- ⚑ WHY IT IS CHEAP.  `C.f₁ x y z` reduces, as a whole, to a ℚ pair whose top
-- `_+ℚ_` cross-multiplies the two subterm denominators (qx⁵qy⁷qz-scale) and then
-- `_≈ℚ_` cross-multiplies AGAIN — the ~730 MB blow-up of the AES-Full route.
-- Here every `_*ℚ_` node is contracted to ONE ℤ product (`≡mkℚ-*`), every
-- `_+ℚ_` to `fixed-D-add` (numerator-wise over the fixed Dden), and the whole
-- thing stays a chain of STUCK-NEUTRAL ≈ℚ congruences over the ~10-node tree.
-- The cube `Ux³` is KEPT AS A PRODUCT (never expanded).  MEASURED: 99 MB
-- (vs 781 MB for `JacobianLiteral1`), general in the point (x,y,z).
--
-- Denominators are tracked as `Qn a b c = qx^a·qy^b·qz^c`; `Qn-mul` makes a
-- product an exponent-addition, so box padding is a single-exponent bump.
-- `evalCD_C` typechecking is the PROOF that `N_C` (`= N1 +ℤ N2`, the factored
-- numerator over Dden) is the correct common-denominator numerator of C.f₁.
--
-- ⚑ THE RESIDUE (⟡jac-lit1-cd-curried step 4, THE load-bearing finding).
-- Composing with `JacobianEvalCD.evalCD-sound R.f₁ Bounded-f₁` (leg 1, the
-- MPoly side, `evalℚ R.f₁ ≈ℚ mkℚ (sumNum R.f₁) Dden`) would land the
-- ∀-quantified `identify₁ : evalℚ R.f₁ ≈ℚ C.f₁` IFF the ℤ identity
--
--   sumNum R.f₁ ≡ N_C                                        -- (over one Dden)
--
-- is proven.  This is NOT `refl` (MEASURED: fails at 97 MB with a structural
-- first-term mismatch `+ (1*1*1*1) != num z`).  Both sides are DISTINCT STUCK
-- ℤ trees — the EXPANDED 204-monomial padded sum on the R side vs the FACTORED
-- `pz·Ux³·qy + …` on the C side — and `_*ℤ_` does not auto-distribute over the
-- symbolic `Ux = qx·qy + px·py`, so proving them equal is the genuine BINOMIAL
-- EXPANSION of `Ux³` in ℤ (a 6-variable ℤ ring identity in px,py,pz,qx,qy,qz).
--
-- So Route 2 STRIPS the ℚ-eta + `_+ℚ_`-cross-multiplication overhead (both
-- endpoints are ~99 MB) and LOCALIZES the irreducible core of the 781 MB to a
-- single, precisely-stated ℤ polynomial identity — but does NOT eliminate the
-- cube-binomial.  Its proof needs genuine ring reasoning (a 6-variable ℤ
-- normalizer, or a large hand expansion); its cost is UNMEASURED (no proof is
-- constructed here — refl is not it).  The residue is CHARACTERIZED, not paid.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEvalCDCurried where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _*_; _^_; _∸_; _≤_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-identityˡ; *-identityʳ; swap-mul; quad)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; 1ℤ)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-assoc)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-trans)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)
open import Substrate.Algebra.Q.JacobianEvalNormalize using (≡→≈ℚ)
import Substrate.Algebra.Q.JacobianEvalCD as CD
import Substrate.Algebra.Q.JacobianCollision as C

------------------------------------------------------------------------
-- General helpers (point-independent).
------------------------------------------------------------------------

-- ℕ power adds exponents.
powℕ-add : (m a d : ℕ) → m ^ (a + d) ≡ m ^ a * m ^ d
powℕ-add m zero    d = sym (*-identityˡ (m ^ d))
powℕ-add m (suc a) d =
  trans (cong (m *_) (powℕ-add m a d)) (sym (*-assoc m (m ^ a) (m ^ d)))

-- product of two clean mkℚ (over da/db, positive) = clean mkℚ over da*db.
≡mkℚ-* : (A B : ℤ) (da db : ℕ) → 1 ≤ da → 1 ≤ db →
         mkℚ A (da ∸ 1) *ℚ mkℚ B (db ∸ 1) ≡ mkℚ (A *ℤ B) (da * db ∸ 1)
≡mkℚ-* A B da db 1da 1db =
  cong (λ w → mkℚ (A *ℤ B) (w ∸ 1))
       (cong₂ _*_ (CD.sucpred da 1da) (CD.sucpred db 1db))

-- pad a clean mkℚ from denominator d up to pad·d (multiply num by pad).
≈mkℚ-pad : (A : ℤ) (d pad : ℕ) → 1 ≤ d → 1 ≤ pad →
           mkℚ A (d ∸ 1) ≈ℚ mkℚ (A *ℤ (+ pad)) (pad * d ∸ 1)
≈mkℚ-pad A d pad 1d 1pad =
  trans (cong (λ w → A *ℤ (+ w)) (CD.sucpred (pad * d) (CD.1≤* 1pad 1d)))
        (trans (sym (*ℤ-assoc A (+ pad) (+ d)))
               (cong (λ w → (A *ℤ (+ pad)) *ℤ (+ w)) (sym (CD.sucpred d 1d))))

-- pad, then rewrite the denominator to a named target D′.
padT : (A : ℤ) (d pad D′ : ℕ) → 1 ≤ d → 1 ≤ pad → pad * d ≡ D′ →
       mkℚ A (d ∸ 1) ≈ℚ mkℚ (A *ℤ (+ pad)) (D′ ∸ 1)
padT A d pad D′ 1d 1pad eq =
  ≈ℚ-trans {mkℚ A (d ∸ 1)} {mkℚ (A *ℤ (+ pad)) (pad * d ∸ 1)}
           {mkℚ (A *ℤ (+ pad)) (D′ ∸ 1)}
    (≈mkℚ-pad A d pad 1d 1pad)
    (≡→≈ℚ (cong (λ w → mkℚ (A *ℤ (+ pad)) (w ∸ 1)) eq))

-- product node: two clean-target ≈'s compose to a clean product target.
mul-node : (m n : ℚ) (A B : ℤ) (da db : ℕ) → 1 ≤ da → 1 ≤ db →
           m ≈ℚ mkℚ A (da ∸ 1) → n ≈ℚ mkℚ B (db ∸ 1) →
           (m *ℚ n) ≈ℚ mkℚ (A *ℤ B) (da * db ∸ 1)
mul-node m n A B da db 1da 1db em en =
  ≈ℚ-trans {m *ℚ n} {mkℚ A (da ∸ 1) *ℚ mkℚ B (db ∸ 1)}
           {mkℚ (A *ℤ B) (da * db ∸ 1)}
    (*ℚ-cong {m} {mkℚ A (da ∸ 1)} {n} {mkℚ B (db ∸ 1)} em en)
    (≡→≈ℚ (≡mkℚ-* A B da db 1da 1db))

------------------------------------------------------------------------
-- Per-point construction.
------------------------------------------------------------------------

module _ (x y z : ℚ) where
  qxn = suc (den-1 x)
  qyn = suc (den-1 y)
  qzn = suc (den-1 z)
  px = num x
  py = num y
  pz = num z

  Dden = CD.Dden x y z 3 4 1

  -- monomial denominator qxn^a · qyn^b · qzn^c.
  Qn : ℕ → ℕ → ℕ → ℕ
  Qn a b c = qxn ^ a * (qyn ^ b * qzn ^ c)

  1≤Qn : (a b c : ℕ) → 1 ≤ Qn a b c
  1≤Qn a b c =
    CD.1≤* (CD.1≤pow (den-1 x) a)
           (CD.1≤* (CD.1≤pow (den-1 y) b) (CD.1≤pow (den-1 z) c))

  -- Qn multiplies by adding exponents (quad interchange + powℕ-add ×3).
  Qn-mul : (a b c d e f : ℕ) → Qn a b c * Qn d e f ≡ Qn (a + d) (b + e) (c + f)
  Qn-mul a b c d e f =
    trans (quad (qxn ^ a) (qyn ^ b * qzn ^ c) (qxn ^ d) (qyn ^ e * qzn ^ f))
    (trans (cong ((qxn ^ a * qxn ^ d) *_)
                 (quad (qyn ^ b) (qzn ^ c) (qyn ^ e) (qzn ^ f)))
           (cong₂ _*_ (sym (powℕ-add qxn a d))
                      (cong₂ _*_ (sym (powℕ-add qyn b e)) (sym (powℕ-add qzn c f)))))

  ----------------------------------------------------------------------
  -- Leaf ℕ identities (qxn·qyn = Qn110, qzn = Qn001, qyn·qyn = Qn020).
  ----------------------------------------------------------------------

  qq≡Q110 : qxn * qyn ≡ Qn 1 1 0
  qq≡Q110 = sym (cong₂ _*_ (*-identityʳ qxn)
                           (trans (*-identityʳ (qyn * 1)) (*-identityʳ qyn)))

  qzn≡Q001 : qzn ≡ Qn 0 0 1
  qzn≡Q001 = sym (trans (*-identityˡ (qyn ^ 0 * qzn ^ 1))
                        (trans (*-identityˡ (qzn ^ 1)) (*-identityʳ qzn)))

  qyy≡Q020 : qyn * qyn ≡ Qn 0 2 0
  qyy≡Q020 = sym (trans (*-identityˡ (qyn * (qyn * 1) * 1))
                        (trans (*-identityʳ (qyn * (qyn * 1)))
                               (cong (qyn *_) (*-identityʳ qyn))))

  ----------------------------------------------------------------------
  -- Padding ℕ identities (all clean single-exponent bumps).
  ----------------------------------------------------------------------

  pad1id : qyn * Qn 3 3 1 ≡ Dden
  pad1id = trans (swap-mul qyn (qxn ^ 3) (qyn ^ 3 * qzn ^ 1))
                 (cong (qxn ^ 3 *_) (sym (*-assoc qyn (qyn ^ 3) (qzn ^ 1))))

  bumpX : qxn * Qn 2 4 0 ≡ Qn 3 4 0
  bumpX = sym (*-assoc qxn (qxn ^ 2) (qyn ^ 4 * qzn ^ 0))

  bumpZ : qzn * Qn 3 4 0 ≡ Dden
  bumpZ = trans (swap-mul qzn (qxn ^ 3) (qyn ^ 4 * qzn ^ 0))
                (cong (qxn ^ 3 *_) (swap-mul qzn (qyn ^ 4) (qzn ^ 0)))

  ----------------------------------------------------------------------
  -- The tree, node by node.  u = 1+xy, v = 4+3xy.
  ----------------------------------------------------------------------

  Ux : ℤ
  Ux = (1ℤ *ℤ (+ Qn 1 1 0)) +ℤ ((px *ℤ py) *ℤ (+ 1))

  Vx : ℤ
  Vx = ((+ 4) *ℤ (+ Qn 1 1 0)) +ℤ (((+ 3) *ℤ (px *ℤ py)) *ℤ (+ 1))

  xy≈ : (x *ℚ y) ≈ℚ mkℚ (px *ℤ py) (Qn 1 1 0 ∸ 1)
  xy≈ = ≡→≈ℚ (cong (λ w → mkℚ (px *ℤ py) (w ∸ 1)) qq≡Q110)

  u≈ : (1ℚ +ℚ (x *ℚ y)) ≈ℚ mkℚ Ux (Qn 1 1 0 ∸ 1)
  u≈ = ≈ℚ-trans {1ℚ +ℚ (x *ℚ y)}
                {1ℚ +ℚ mkℚ (px *ℤ py) (Qn 1 1 0 ∸ 1)}
                {mkℚ Ux (Qn 1 1 0 ∸ 1)}
    (+ℚ-cong {1ℚ} {1ℚ} {x *ℚ y} {mkℚ (px *ℤ py) (Qn 1 1 0 ∸ 1)} (≈ℚ-refl 1ℚ) xy≈)
    (≡→≈ℚ (cong (λ w → mkℚ Ux (w ∸ 1)) (*-identityˡ (Qn 1 1 0))))

  3xy≈ : (C.3ℚ *ℚ (x *ℚ y)) ≈ℚ mkℚ ((+ 3) *ℤ (px *ℤ py)) (Qn 1 1 0 ∸ 1)
  3xy≈ = ≡→≈ℚ (cong (λ w → mkℚ ((+ 3) *ℤ (px *ℤ py)) (w ∸ 1))
                    (trans (*-identityˡ (qxn * qyn)) qq≡Q110))

  v≈ : (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y))) ≈ℚ mkℚ Vx (Qn 1 1 0 ∸ 1)
  v≈ = ≈ℚ-trans {C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y))}
                {C.4ℚ +ℚ mkℚ ((+ 3) *ℤ (px *ℤ py)) (Qn 1 1 0 ∸ 1)}
                {mkℚ Vx (Qn 1 1 0 ∸ 1)}
    (+ℚ-cong {C.4ℚ} {C.4ℚ} {C.3ℚ *ℚ (x *ℚ y)}
             {mkℚ ((+ 3) *ℤ (px *ℤ py)) (Qn 1 1 0 ∸ 1)} (≈ℚ-refl C.4ℚ) 3xy≈)
    (≡→≈ℚ (cong (λ w → mkℚ Vx (w ∸ 1)) (*-identityˡ (Qn 1 1 0))))

  -- u³ = u·(u·u).
  uu≈ : ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y)))
          ≈ℚ mkℚ (Ux *ℤ Ux) (Qn 2 2 0 ∸ 1)
  uu≈ = ≈ℚ-trans {(1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y))}
                 {mkℚ (Ux *ℤ Ux) (Qn 1 1 0 * Qn 1 1 0 ∸ 1)}
                 {mkℚ (Ux *ℤ Ux) (Qn 2 2 0 ∸ 1)}
    (mul-node (1ℚ +ℚ (x *ℚ y)) (1ℚ +ℚ (x *ℚ y)) Ux Ux (Qn 1 1 0) (Qn 1 1 0)
              (1≤Qn 1 1 0) (1≤Qn 1 1 0) u≈ u≈)
    (≡→≈ℚ (cong (λ w → mkℚ (Ux *ℤ Ux) (w ∸ 1)) (Qn-mul 1 1 0 1 1 0)))

  uuu≈ : ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y))))
           ≈ℚ mkℚ (Ux *ℤ (Ux *ℤ Ux)) (Qn 3 3 0 ∸ 1)
  uuu≈ = ≈ℚ-trans {(1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y)))}
                  {mkℚ (Ux *ℤ (Ux *ℤ Ux)) (Qn 1 1 0 * Qn 2 2 0 ∸ 1)}
                  {mkℚ (Ux *ℤ (Ux *ℤ Ux)) (Qn 3 3 0 ∸ 1)}
    (mul-node (1ℚ +ℚ (x *ℚ y)) ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y)))
              Ux (Ux *ℤ Ux) (Qn 1 1 0) (Qn 2 2 0)
              (1≤Qn 1 1 0) (1≤Qn 2 2 0) u≈ uu≈)
    (≡→≈ℚ (cong (λ w → mkℚ (Ux *ℤ (Ux *ℤ Ux)) (w ∸ 1)) (Qn-mul 1 1 0 2 2 0)))

  z≈ : z ≈ℚ mkℚ pz (Qn 0 0 1 ∸ 1)
  z≈ = ≡→≈ℚ (cong (λ w → mkℚ pz (w ∸ 1)) qzn≡Q001)

  -- T1 = z·u³, natural denominator Qn331.
  T1≈nat : (z *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y)))))
             ≈ℚ mkℚ (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) (Qn 3 3 1 ∸ 1)
  T1≈nat = ≈ℚ-trans
    {z *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y))))}
    {mkℚ (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) (Qn 0 0 1 * Qn 3 3 0 ∸ 1)}
    {mkℚ (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) (Qn 3 3 1 ∸ 1)}
    (mul-node z ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y))))
              pz (Ux *ℤ (Ux *ℤ Ux)) (Qn 0 0 1) (Qn 3 3 0)
              (1≤Qn 0 0 1) (1≤Qn 3 3 0) z≈ uuu≈)
    (≡→≈ℚ (cong (λ w → mkℚ (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) (w ∸ 1)) (Qn-mul 0 0 1 3 3 0)))

  N1 : ℤ
  N1 = (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) *ℤ (+ qyn)

  T1≈D : (z *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y)))))
           ≈ℚ mkℚ N1 (Dden ∸ 1)
  T1≈D = ≈ℚ-trans
    {z *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y))))}
    {mkℚ (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) (Qn 3 3 1 ∸ 1)}
    {mkℚ N1 (Dden ∸ 1)}
    T1≈nat
    (padT (pz *ℤ (Ux *ℤ (Ux *ℤ Ux))) (Qn 3 3 1) qyn Dden
          (1≤Qn 3 3 1) (s≤s z≤n) pad1id)

  -- T2 = y²·u·v.
  yy≈ : (y *ℚ y) ≈ℚ mkℚ (py *ℤ py) (Qn 0 2 0 ∸ 1)
  yy≈ = ≡→≈ℚ (cong (λ w → mkℚ (py *ℤ py) (w ∸ 1)) qyy≡Q020)

  yyu≈ : ((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y)))
           ≈ℚ mkℚ ((py *ℤ py) *ℤ Ux) (Qn 1 3 0 ∸ 1)
  yyu≈ = ≈ℚ-trans {(y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))}
                  {mkℚ ((py *ℤ py) *ℤ Ux) (Qn 0 2 0 * Qn 1 1 0 ∸ 1)}
                  {mkℚ ((py *ℤ py) *ℤ Ux) (Qn 1 3 0 ∸ 1)}
    (mul-node (y *ℚ y) (1ℚ +ℚ (x *ℚ y)) (py *ℤ py) Ux (Qn 0 2 0) (Qn 1 1 0)
              (1≤Qn 0 2 0) (1≤Qn 1 1 0) yy≈ u≈)
    (≡→≈ℚ (cong (λ w → mkℚ ((py *ℤ py) *ℤ Ux) (w ∸ 1)) (Qn-mul 0 2 0 1 1 0)))

  T2≈nat : (((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))) *ℚ (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y))))
             ≈ℚ mkℚ (((py *ℤ py) *ℤ Ux) *ℤ Vx) (Qn 2 4 0 ∸ 1)
  T2≈nat = ≈ℚ-trans
    {((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))) *ℚ (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y)))}
    {mkℚ (((py *ℤ py) *ℤ Ux) *ℤ Vx) (Qn 1 3 0 * Qn 1 1 0 ∸ 1)}
    {mkℚ (((py *ℤ py) *ℤ Ux) *ℤ Vx) (Qn 2 4 0 ∸ 1)}
    (mul-node ((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))) (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y)))
              ((py *ℤ py) *ℤ Ux) Vx (Qn 1 3 0) (Qn 1 1 0)
              (1≤Qn 1 3 0) (1≤Qn 1 1 0) yyu≈ v≈)
    (≡→≈ℚ (cong (λ w → mkℚ (((py *ℤ py) *ℤ Ux) *ℤ Vx) (w ∸ 1)) (Qn-mul 1 3 0 1 1 0)))

  N2 : ℤ
  N2 = (((py *ℤ py) *ℤ Ux) *ℤ Vx) *ℤ (+ qxn) *ℤ (+ qzn)

  T2≈D : (((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))) *ℚ (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y))))
           ≈ℚ mkℚ N2 (Dden ∸ 1)
  T2≈D = ≈ℚ-trans
    {((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))) *ℚ (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y)))}
    {mkℚ (((py *ℤ py) *ℤ Ux) *ℤ Vx) (Qn 2 4 0 ∸ 1)}
    {mkℚ N2 (Dden ∸ 1)}
    T2≈nat
    (≈ℚ-trans {mkℚ (((py *ℤ py) *ℤ Ux) *ℤ Vx) (Qn 2 4 0 ∸ 1)}
              {mkℚ ((((py *ℤ py) *ℤ Ux) *ℤ Vx) *ℤ (+ qxn)) (Qn 3 4 0 ∸ 1)}
              {mkℚ N2 (Dden ∸ 1)}
      (padT (((py *ℤ py) *ℤ Ux) *ℤ Vx) (Qn 2 4 0) qxn (Qn 3 4 0)
            (1≤Qn 2 4 0) (s≤s z≤n) bumpX)
      (padT ((((py *ℤ py) *ℤ Ux) *ℤ Vx) *ℤ (+ qxn)) (Qn 3 4 0) qzn Dden
            (1≤Qn 3 4 0) (s≤s z≤n) bumpZ))

  ----------------------------------------------------------------------
  -- THE dual evaluator.  C.f₁ x y z ≈ℚ mkℚ (N1 +ℤ N2) (Dden ∸ 1).
  ----------------------------------------------------------------------

  N_C : ℤ
  N_C = N1 +ℤ N2

  evalCD_C : C.f₁ x y z ≈ℚ mkℚ N_C (Dden ∸ 1)
  evalCD_C = ≈ℚ-trans
    {C.f₁ x y z}
    {mkℚ N1 (Dden ∸ 1) +ℚ mkℚ N2 (Dden ∸ 1)}
    {mkℚ N_C (Dden ∸ 1)}
    (+ℚ-cong {z *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ ((1ℚ +ℚ (x *ℚ y)) *ℚ (1ℚ +ℚ (x *ℚ y))))}
             {mkℚ N1 (Dden ∸ 1)}
             {((y *ℚ y) *ℚ (1ℚ +ℚ (x *ℚ y))) *ℚ (C.4ℚ +ℚ (C.3ℚ *ℚ (x *ℚ y)))}
             {mkℚ N2 (Dden ∸ 1)}
             T1≈D T2≈D)
    (CD.fixed-D-add x y z 3 4 1 N1 N2 (Dden ∸ 1))
