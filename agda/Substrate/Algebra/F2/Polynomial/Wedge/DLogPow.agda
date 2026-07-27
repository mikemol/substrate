------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DLogPow
--
-- GF(2ⁿ)/GF(2⁴)/GF(2⁸) discrete-log inverse, the STRUCTURAL way (scales where
-- the GF(4) enumeration in GF4DLog cannot). The antilog g^· is built by iterated
-- multiplication; its homomorphism `g^(a+b) = gᵃ·gᵇ` is a clean INDUCTION (no
-- 2ⁿ²-case table), and the only per-field reflection is `g^(2ⁿ-1) = 1`.
--
--   • `gpow` / `gpow-hom`  — the antilog ℕ → GF(2ⁿ)* and its monoid homomorphism.
--   • `gpow-codec`         — instantiates the generic `Algebra.ExpLogCodec` at the
--                            field over L = ℕ: GF(2ⁿ) multiplication IS exp of
--                            ℕ-addition (the first AES-field codec instance).
--   • `dlog-inv-law`       — the discrete-log inverse: `gᵏ · gʲ ≡ 1` whenever
--                            `k+j = order`, via `gpow-hom` + `g^order = 1`. The
--                            inverse of gᵏ is g^(order−k) — additive negation in
--                            the exponent, no EEA/Bézout.
--
-- Generic over (d, modulus, primitive g). GF(2⁴) codec instantiated here
-- (x⁴+x+1, x primitive). The CONCRETE inverse needs `g^(2ⁿ-1) ≡ 1` as input:
-- that fact is reflection-feasible only for SMALL fields (the deep-nested *Q
-- reflection blows up super-linearly — x⁴ is instant, x¹⁵ does not terminate in
-- practice, x²⁵⁵ is hopeless); generally it is the field multiplicative-ORDER
-- theorem (x^(2ⁿ-1)=1 ∀ nonzero x, Lagrange). So `dlog-inv-law` is a SCHEMA
-- parametric on that proof; supplying it for GF(2⁴)/GF(2⁸) is the order-theorem
-- arc (rostered). GF(4)'s concrete inverse is already done by enumeration
-- (`GF4DLog`/`GF4TwoFaces`). Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DLogPow where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.ExpLogCodec using (ExpLogCodec)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D

------------------------------------------------------------------------
-- The structural antilog, generic over the field and primitive element.
------------------------------------------------------------------------

module Over (d : ℕ) (m-lo : Vec F2.F₂ (suc d)) (gx : F.Over.Poly F₂-CommRing (suc d)) where
  open F.Over F₂-CommRing using (Poly)
  open M.Over F₂-CommRing d m-lo using (oneC)
  open Q.Over F₂-CommRing d m-lo using (_*Q_; *Q-assoc; *Q-identityˡ)

  -- the antilog g^· : ℕ → GF(2ⁿ)*, iterated multiplication by the primitive g.
  gpow : ℕ → Poly (suc d)
  gpow zero    = oneC
  gpow (suc n) = gx *Q gpow n

  -- g^(a+b) = gᵃ · gᵇ : the homomorphism, by induction (NOT a 2ⁿ²-case table).
  gpow-hom : (a b : ℕ) → gpow (a + b) ≡ (gpow a *Q gpow b)
  gpow-hom zero    b = sym (*Q-identityˡ (gpow b))
  gpow-hom (suc a) b =
    trans (cong (gx *Q_) (gpow-hom a b))
          (sym (*Q-assoc gx (gpow a) (gpow b)))

  -- the generic codec at this field, over L = ℕ: GF(2ⁿ) mult IS exp of ℕ-add.
  gpow-codec : ExpLogCodec ℕ _*Q_ oneC _≡_
  gpow-codec = record
    { _⊕_ = _+_ ; 𝟘 = zero ; expL = gpow
    ; exp-⊕ = gpow-hom ; exp-𝟘 = refl }

  -- THE DISCRETE-LOG INVERSE: gᵏ · gʲ ≡ 1 whenever k+j = order. The inverse of gᵏ
  -- is g^(order−k) — additive negation in the exponent, transported by exp.
  dlog-inv-law : (ord : ℕ) → gpow ord ≡ oneC →
                 (k j : ℕ) → k + j ≡ ord → (gpow k *Q gpow j) ≡ oneC
  dlog-inv-law ord g k j kj =
    trans (sym (gpow-hom k j)) (trans (cong gpow kj) g)

------------------------------------------------------------------------
-- GF(2⁴) = F₂[x]/(x⁴+x+1), primitive g = x, multiplicative order 15.
------------------------------------------------------------------------

m-lo₄ : Vec F2.F₂ 4
m-lo₄ = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []

gx₄ : F.Over.Poly F₂-CommRing 4
gx₄ = F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []          -- x

module GF16 = Over 3 m-lo₄ gx₄
open M.Over F₂-CommRing 3 m-lo₄ using (oneC)
open Q.Over F₂-CommRing 3 m-lo₄ using (_*Q_)

-- THE AES NIBBLE-FIELD CODEC: GF(2⁴) multiplication IS exp of ℕ-addition — the
-- first AES-field instance of the generic `ExpLogCodec` (structural, no reflection).
gf16-codec : ExpLogCodec ℕ _*Q_ oneC _≡_
gf16-codec = GF16.gpow-codec

-- The GF(2⁴) discrete-log inverse law is `GF16.dlog-inv-law 15 g15`, awaiting
-- `g15 : GF16.gpow 15 ≡ oneC` — the order fact (reflection blows up; needs the
-- field-order theorem). The SCHEMA `GF16.dlog-inv-law` is ready; only that input
-- is open. (At GF(4) the inverse is done concretely in GF4DLog/GF4TwoFaces.)
