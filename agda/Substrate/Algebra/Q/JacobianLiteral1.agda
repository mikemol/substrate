{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianLiteral1 — literal₁ by the AES-Full pattern.
--
-- literal₁ : (x y z : ℚ) → evalℚ x y z R.f₁ ≋ C.f₁ x y z
--
-- f₁ = z·u³ + y²·u·v with u = 1+xy. The naive `γ₁ = homAgree e₁` forces the top
-- +-hom `evalℚ-++ (encode e₁A) (encode e₁B)` at the CONCRETE degree-9 sum — the
-- 8-step list induction builds the whole symbolic-ℚ evaluation (~850 MB). The
-- (1+xy)³ CUBE is what makes f₁ the outlier; f₂/f₃ stay light.
--
-- ⚑ ANTI-EXPLOSION, exactly as `AES.KAT.Full` / `MixColumns.Proof.G`: assemble the
-- +-hom recomposition inside a module ABSTRACT over the summand polynomials
-- (`pA pB`), where `evalℚ-++ pA pB` is STUCK (neutral) — so nothing is ever forced
-- during assembly. The concrete per-summand pins (γ₁A = z·u³, γ₁B = y²·u·v) come
-- from the SEPARATE cheap modules JacobianLiteral1A/1B (98/77 MB, cf. AES KAT.RoundN).
-- Instantiation is by `open` (NOT a type-annotated re-declaration), so the
-- substituted type transits the module boundary WITHOUT a conversion check —
-- Agda never re-normalises the +-hom over the concrete sum.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianLiteral1 where

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Equiv using (≈ℚ-trans; ≈ℚ-refl)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong)

import Substrate.Algebra.Z.JacobianResidue as R
open R using (MPoly; _+P_)

open import Substrate.Algebra.Q.JacobianEncodingGen
open import Substrate.Algebra.Q.JacobianEncodingHom
open import Substrate.Algebra.Q.JacobianEvalNormalize using (evalBridge₁)
open import Substrate.Algebra.Q.JacobianEncodingNormalize using (Cᴹf₁)
import Substrate.Algebra.Q.JacobianCollision as C
open import Substrate.Algebra.Q.JacobianExpr using (e₁A; e₁B; encode)
import Substrate.Algebra.Q.JacobianLiteral1A as A
import Substrate.Algebra.Q.JacobianLiteral1B as B

module _ (x y z : ℚ) where

  open Point  x y z
  open Point2 x y z

  -- The +-hom recomposition, ABSTRACT over the summand polynomials `pA pB`.
  -- `evalℚ-++ pA pB` is stuck here (pA/pB neutral) → no degree-9 eval is forced.
  module Assemble
    (pA pB fR : MPoly)
    (dA dB cf : ℚ)
    (γa : E pA ≋ dA) (γb : E pB ≋ dB)
    (eb : E fR ≋ E (pA +P pB))
    (dsum : (dA +ℚ dB) ≋ cf)
    where
    -- ≈ℚ endpoints given EXPLICITLY: `_≈ℚ_` unfolds to a cross-multiplication ≡,
    -- which erases its endpoints, so ≈ℚ-trans/+ℚ-cong implicits are not inferrable.
    -- All pins are abstract (pA/pB/…), so `evalℚ-++ pA pB` stays stuck.
    literal : E fR ≋ cf
    literal =
      ≈ℚ-trans {E fR} {E (pA +P pB)} {cf} eb
        (≈ℚ-trans {E (pA +P pB)} {dA +ℚ dB} {cf}
          (≈ℚ-trans {E (pA +P pB)} {E pA +ℚ E pB} {dA +ℚ dB}
            (evalℚ-++ pA pB)
            (+ℚ-cong {E pA} {dA} {E pB} {dB} γa γb))
          dsum)

  -- Instantiate by OPENING (no re-declaration ⇒ no conversion ⇒ no +-hom WHNF).
  open Assemble (encode e₁A) (encode e₁B) R.f₁
                (evalDirect e₁A) (evalDirect e₁B) (C.f₁ x y z)
                (A.γ₁A x y z) (B.γ₁B x y z)
                (evalBridge₁ x y z)
                (≈ℚ-refl (evalDirect e₁A +ℚ evalDirect e₁B))
    public renaming (literal to literal₁)
