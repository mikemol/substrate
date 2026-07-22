{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingGen — the MINIMAL generator lemmas.
--
-- The smallest reusable layer of ◆jac-gamma: the ℚ evaluator `E`/`eT`/`mv` at a
-- point plus the monomial VALUES and the four GENERATORS
--
--     gen-X : E R.X ≋ x     gen-Y : E R.Y ≋ y     gen-Z : E R.Z₁ ≋ z
--     gen-kP : (k : ℤ) → E (R.kP k) ≋ ℤ→ℚ k
--
-- and NOTHING heavier. This is the layer a det/component-literal consumer imports:
-- it deserializes ONLY these tiny proofs, NOT the `homAgree`/`*P`-hom machinery
-- (`JacobianEncodingHom`) nor the degree-9 γᵢ (`JacobianEncodingLiteral`). The
-- def/proof-separation memory mechanism (`scripts/check_def_proof_separation.sh`)
-- makes an import deserialize the FULL closure at ~40× — so the reusable pieces a
-- cheap consumer needs are kept in the SMALLEST module that supplies them.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingGen where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Z using (ℤ; 1ℤ)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)
open import Substrate.Algebra.Q.Properties.Field
  using (*ℚ-identityˡ; *ℚ-identityʳ; +ℚ-identityʳ)
open import Substrate.Algebra.Q.Properties.Congruence using (*ℚ-cong)

import Substrate.Algebra.Z.JacobianResidue as R
open R using (Mono; Term; MPoly; mono; term)

import Substrate.Algebra.Q.JacobianEvalNormalize as β

-- A loose-fixity synonym for the target equality, ONLY so `a *ℚ b ≋ c *ℚ d`
-- parses (both `_*ℚ_` and `_≈ℚ_` sit at level 20). A RELATION (codomain Set),
-- not a ℚ-carrier operator — it introduces no arithmetic op.
infix 0 _≋_
_≋_ : ℚ → ℚ → Set
_≋_ = _≈ℚ_

module Point (x y z : ℚ) where

  -- β's evaluator, threaded at this point (definitionally: E (t ∷ p) = eT t +ℚ E p).
  E : MPoly → ℚ
  E  = β.evalℚ x y z
  eT : Term → ℚ
  eT = β.evalT x y z
  mv : Mono → ℚ
  mv = β.monoval x y z

  monoval-100 : mv (mono 1 0 0) ≋ x
  monoval-100 =
    ≈ℚ-trans {(x *ℚ 1ℚ) *ℚ (1ℚ *ℚ 1ℚ)} {x *ℚ 1ℚ} {x}
      (*ℚ-cong {x *ℚ 1ℚ} {x} {1ℚ *ℚ 1ℚ} {1ℚ} (*ℚ-identityʳ x) (*ℚ-identityˡ 1ℚ))
      (*ℚ-identityʳ x)

  monoval-010 : mv (mono 0 1 0) ≋ y
  monoval-010 =
    ≈ℚ-trans {1ℚ *ℚ ((y *ℚ 1ℚ) *ℚ 1ℚ)} {(y *ℚ 1ℚ) *ℚ 1ℚ} {y}
      (*ℚ-identityˡ ((y *ℚ 1ℚ) *ℚ 1ℚ))
      (≈ℚ-trans {(y *ℚ 1ℚ) *ℚ 1ℚ} {y *ℚ 1ℚ} {y}
        (*ℚ-identityʳ (y *ℚ 1ℚ)) (*ℚ-identityʳ y))

  monoval-001 : mv (mono 0 0 1) ≋ z
  monoval-001 =
    ≈ℚ-trans {1ℚ *ℚ (1ℚ *ℚ (z *ℚ 1ℚ))} {1ℚ *ℚ (z *ℚ 1ℚ)} {z}
      (*ℚ-identityˡ (1ℚ *ℚ (z *ℚ 1ℚ)))
      (≈ℚ-trans {1ℚ *ℚ (z *ℚ 1ℚ)} {z *ℚ 1ℚ} {z}
        (*ℚ-identityˡ (z *ℚ 1ℚ)) (*ℚ-identityʳ z))

  monoval-000 : mv (mono 0 0 0) ≋ 1ℚ
  monoval-000 =
    ≈ℚ-trans {1ℚ *ℚ (1ℚ *ℚ 1ℚ)} {1ℚ *ℚ 1ℚ} {1ℚ}
      (*ℚ-identityˡ (1ℚ *ℚ 1ℚ)) (*ℚ-identityˡ 1ℚ)

  evalℚ-single : (m : Mono) (k : ℤ) → E (term m k ∷ []) ≋ (ℤ→ℚ k) *ℚ (mv m)
  evalℚ-single m k = +ℚ-identityʳ ((ℤ→ℚ k) *ℚ mv m)

  gen-X : E R.X ≋ x
  gen-X = ≈ℚ-trans {E R.X} {1ℚ *ℚ (mv (mono 1 0 0))} {x}
            (evalℚ-single (mono 1 0 0) 1ℤ)
            (≈ℚ-trans {1ℚ *ℚ (mv (mono 1 0 0))} {mv (mono 1 0 0)} {x}
              (*ℚ-identityˡ (mv (mono 1 0 0))) monoval-100)

  gen-Y : E R.Y ≋ y
  gen-Y = ≈ℚ-trans {E R.Y} {1ℚ *ℚ (mv (mono 0 1 0))} {y}
            (evalℚ-single (mono 0 1 0) 1ℤ)
            (≈ℚ-trans {1ℚ *ℚ (mv (mono 0 1 0))} {mv (mono 0 1 0)} {y}
              (*ℚ-identityˡ (mv (mono 0 1 0))) monoval-010)

  gen-Z : E R.Z₁ ≋ z
  gen-Z = ≈ℚ-trans {E R.Z₁} {1ℚ *ℚ (mv (mono 0 0 1))} {z}
            (evalℚ-single (mono 0 0 1) 1ℤ)
            (≈ℚ-trans {1ℚ *ℚ (mv (mono 0 0 1))} {mv (mono 0 0 1)} {z}
              (*ℚ-identityˡ (mv (mono 0 0 1))) monoval-001)

  gen-kP : (k : ℤ) → E (R.kP k) ≋ ℤ→ℚ k
  gen-kP k = ≈ℚ-trans {E (R.kP k)} {(ℤ→ℚ k) *ℚ (mv (mono 0 0 0))} {ℤ→ℚ k}
               (evalℚ-single (mono 0 0 0) k)
               (≈ℚ-trans {(ℤ→ℚ k) *ℚ (mv (mono 0 0 0))} {(ℤ→ℚ k) *ℚ 1ℚ} {ℤ→ℚ k}
                 (*ℚ-cong {ℤ→ℚ k} {ℤ→ℚ k} {mv (mono 0 0 0)} {1ℚ}
                          (≈ℚ-refl (ℤ→ℚ k)) monoval-000)
                 (*ℚ-identityʳ (ℤ→ℚ k)))
