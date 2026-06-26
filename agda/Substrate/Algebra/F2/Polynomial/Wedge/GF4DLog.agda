------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GF4DLog
--
-- Ⓐ.gfinv-dlog — the DISCRETE-LOG face of the field inverse, WITNESSED at
-- GF(4) = F₂[x]/(x²+x+1). The first real consumer of `Algebra.ExpLogCodec`'s
-- recip↔neg theorem (`codec-inverse`): the multiplicative inverse of a field
-- element is the ADDITIVE NEGATION of its discrete log, transported by exp.
--
--   • exponent group L = ℤ/3 (the multiplicative group GF(4)* is cyclic of
--     order 3, primitive element x);  expL = the antilog g^· : ℤ/3 → GF(4)*.
--   • The codec laws (exp(a⊕b) ≡ exp a · exp b, exp 0 ≡ 1) are FINITE refls
--     (GF(4) has 4 elements; *Q computes).
--   • `codec-inverse` then GIVES the inverse, no EEA/Bézout: a⁻¹ = g^(neg(log a)).
--
-- This is the SECOND face of the field inverse (cf. the EEA-Bézout face in
-- `SBoxFaces`/`Inverse`/`GF16Inverse`) — the two compute the one inverse
-- (Cryptographic-Total-Space). Mechanism witnessed minimally; GF(2⁴)/GF(2⁸)
-- follow the same shape via structural induction (g^(a+b)=gᵃ·gᵇ) + g^(2ⁿ-1)=1.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GF4DLog where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.ExpLogCodec as ELC using (ExpLogCodec)
import Substrate.Algebra.Polynomial.Graded.Div as D

-- GF(4) = F₂[x]/(x²+x+1): low coeffs (x⁰,x¹) = (1,1), the leading x² implicit (d=1).
m-lo₂ : Vec F2.F₂ 2
m-lo₂ = F2.𝟙 ∷ F2.𝟙 ∷ []

open D.Over F₂-CommRing 1 m-lo₂ using (Poly; _*Q_; oneC)

-- the three nonzero field elements: 1, x, x+1  (Poly 2 = Vec F₂ 2, degree < 2).
ex  : Poly 2      -- x
ex  = F2.𝟘 ∷ F2.𝟙 ∷ []
ex1 : Poly 2      -- x+1
ex1 = F2.𝟙 ∷ F2.𝟙 ∷ []

------------------------------------------------------------------------
-- L = ℤ/3, the exponent group (GF(4)* is cyclic of order 3).
------------------------------------------------------------------------

data Exp3 : Set where z0 z1 z2 : Exp3

_⊕₃_ : Exp3 → Exp3 → Exp3
z0 ⊕₃ b  = b
z1 ⊕₃ z0 = z1
z1 ⊕₃ z1 = z2
z1 ⊕₃ z2 = z0
z2 ⊕₃ z0 = z2
z2 ⊕₃ z1 = z0
z2 ⊕₃ z2 = z1

neg₃ : Exp3 → Exp3
neg₃ z0 = z0
neg₃ z1 = z2
neg₃ z2 = z1

-- the antilog g^· : the powers of the primitive element x.
expL₃ : Exp3 → Poly 2
expL₃ z0 = oneC      -- x⁰ = 1
expL₃ z1 = ex        -- x¹ = x
expL₃ z2 = ex1       -- x² = x+1  (mod x²+x+1)

------------------------------------------------------------------------
-- The codec laws — finite refls (GF(4) multiplication computes).
------------------------------------------------------------------------

-- exp(a ⊕ b) ≡ exp a · exp b : the antilog is a homomorphism ℤ/3 → GF(4)*.
exp-⊕₃ : (a b : Exp3) → expL₃ (a ⊕₃ b) ≡ (expL₃ a *Q expL₃ b)
exp-⊕₃ z0 z0 = refl
exp-⊕₃ z0 z1 = refl
exp-⊕₃ z0 z2 = refl
exp-⊕₃ z1 z0 = refl
exp-⊕₃ z1 z1 = refl   -- x·x = x+1
exp-⊕₃ z1 z2 = refl   -- x·(x+1) = 1
exp-⊕₃ z2 z0 = refl
exp-⊕₃ z2 z1 = refl   -- (x+1)·x = 1
exp-⊕₃ z2 z2 = refl   -- (x+1)·(x+1) = x

gf4-codec : ExpLogCodec _*Q_ oneC _≡_
gf4-codec = record
  { L = Exp3 ; _⊕_ = _⊕₃_ ; 𝟘 = z0 ; expL = expL₃
  ; exp-⊕ = exp-⊕₃ ; exp-𝟘 = refl }

-- the L-space inverse law: a ⊕ neg a ≡ 0 (ℤ/3 is a group) — finite refls.
invˡ₃ : (a : Exp3) → (a ⊕₃ neg₃ a) ≡ z0
invˡ₃ z0 = refl
invˡ₃ z1 = refl
invˡ₃ z2 = refl

------------------------------------------------------------------------
-- THE DISCRETE-LOG INVERSE: codec-inverse fires (≈ is ≡ here, so the
-- equivalence ops are sym / trans / id). a⁻¹ = g^(neg(log a)), derived from
-- additive negation in the exponent group — no EEA, no Bézout.
------------------------------------------------------------------------

open ELC.Inverse {G = Poly 2} {_*Q_} {oneC} {_≡_}
  sym trans (λ p → p) gf4-codec neg₃ invˡ₃

-- the inverse of g^k is g^(neg k):
dlog-inv : Exp3 → Poly 2
dlog-inv k = expL₃ (neg₃ k)

-- THE INVERSE LAW, via the codec grounding (the recip↔neg theorem itself):
dlog-inv-law : (k : Exp3) → (expL₃ k *Q dlog-inv k) ≡ oneC
dlog-inv-law = codec-inverse
