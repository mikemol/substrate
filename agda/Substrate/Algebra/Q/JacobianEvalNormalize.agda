{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEvalNormalize — ◆jac-eval-respects-normalize (β).
--
-- THE LITERAL-ℚ BRIDGE, and a NEW ROSETTA-STONE DIMENSION: the ≈ℚ wall is
-- INFERENCE, not composition. Hand-composed ≈ℚ with INFERRED endpoints walls
-- universally (eta-ℚ unfolds every operand to `mkℚ`, so reading an endpoint off
-- an ≈ℚ sub-proof loses it). But with EVERY implicit PINNED
-- (`+ℚ-cong {a}{a′}{b}{b′}`, `≈ℚ-trans {a}{b}{c}`), the ADDITIVE reassoc chain
-- lands — and `normalize` is sorted-insert over `+`, so β is exactly that shape.
-- The fully-pinned term is what a synthesizer/extruder produces: endpoints
-- supplied, no inference left to fail.
--
--     β :  evalℚ p  ≈ℚ  evalℚ (normalize p)
--
-- With C2's `bridgeᵢ : normalize R.fᵢ ≡ normalize Cᴹfᵢ`, β lifts the rigid
-- polynomial identification to the literal ℚ evaluator:
--   evalℚ R.fᵢ ≈ℚ evalℚ(normalize R.fᵢ) ≡[cong evalℚ bridgeᵢ] evalℚ(normalize Cᴹfᵢ) ≈ℚ evalℚ Cᴹfᵢ
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEvalNormalize where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; sym)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Negation using (yes; no)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Z using (ℤ; +_; 0ℤ; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-identityʳ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)
open import Substrate.Algebra.Q.Properties.Field
  using (+ℚ-comm; +ℚ-assoc; +ℚ-identityˡ; zero-absorbˡ; distribʳ)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)
open import Substrate.Algebra.Z.MPolyNormalize
  using (normalize; insertT; consNZ; triM; ltM; eqM≡; gtM)
open import Substrate.Algebra.Z.JacobianResidue
  using (MPoly; Mono; mono; Term; term; f₁; f₂; f₃)
open import Substrate.Algebra.Q.JacobianEncodingNormalize
  using (Cᴹf₁; Cᴹf₂; Cᴹf₃; bridge₁; bridge₂; bridge₃)

-- ≡ ⇒ ≈ℚ (the rigid identification crosses into the setoid).
≡→≈ℚ : {a b : ℚ} → a ≡ b → a ≈ℚ b
≡→≈ℚ {a} refl = ≈ℚ-refl a

------------------------------------------------------------------------
-- The evaluator (given a point x y z). Non-opaque: β is over an ABSTRACT p,
-- so nothing distributes.
------------------------------------------------------------------------

powℚ : ℚ → ℕ → ℚ
powℚ w zero    = 1ℚ
powℚ w (suc n) = w *ℚ powℚ w n

module _ (x y z : ℚ) where

  monoval : Mono → ℚ
  monoval (mono a b c) = powℚ x a *ℚ (powℚ y b *ℚ powℚ z c)

  evalT : Term → ℚ
  evalT (term m k) = ℤ→ℚ k *ℚ monoval m

  evalℚ : MPoly → ℚ
  evalℚ []      = 0ℚ
  evalℚ (t ∷ p) = evalT t +ℚ evalℚ p

  ----------------------------------------------------------------------
  -- Atomic ≈ℚ facts (fully-pinned).
  ----------------------------------------------------------------------

  -- ℤ→ℚ is a +-hom: ℤ→ℚ (k +ℤ l) ≈ℚ ℤ→ℚ k +ℚ ℤ→ℚ l.  Both are mkℚ …; cross-mult.
  ℤ→ℚ-+ℚ-hom : (k l : ℤ) → ℤ→ℚ (k +ℤ l) ≈ℚ (ℤ→ℚ k +ℚ ℤ→ℚ l)
  ℤ→ℚ-+ℚ-hom k l =
    cong (_*ℤ (+ 1)) (cong₂ _+ℤ_ (sym (*ℤ-identityʳ k)) (sym (*ℤ-identityʳ l)))

  -- a zero-coefficient term evaluates to 0ℚ.
  evalT-zero : (m : Mono) → evalT (term m 0ℤ) ≈ℚ 0ℚ
  evalT-zero m = zero-absorbˡ (monoval m)

  -- like monomials combine: evalT(m,k) + evalT(m,d) ≈ evalT(m, k+d).
  coeff-combine : (m : Mono) (k d : ℤ) →
                  (evalT (term m k) +ℚ evalT (term m d)) ≈ℚ evalT (term m (k +ℤ d))
  coeff-combine m k d =
    ≈ℚ-trans {evalT (term m k) +ℚ evalT (term m d)}
             {(ℤ→ℚ k +ℚ ℤ→ℚ d) *ℚ monoval m}
             {evalT (term m (k +ℤ d))}
      (≈ℚ-sym {(ℤ→ℚ k +ℚ ℤ→ℚ d) *ℚ monoval m}
              {(ℤ→ℚ k *ℚ monoval m) +ℚ (ℤ→ℚ d *ℚ monoval m)}
              (distribʳ (ℤ→ℚ k) (ℤ→ℚ d) (monoval m)))
      (*ℚ-cong {ℤ→ℚ k +ℚ ℤ→ℚ d} {ℤ→ℚ (k +ℤ d)} {monoval m} {monoval m}
               (≈ℚ-sym {ℤ→ℚ (k +ℤ d)} {ℤ→ℚ k +ℚ ℤ→ℚ d} (ℤ→ℚ-+ℚ-hom k d))
               (≈ℚ-refl (monoval m)))

  ----------------------------------------------------------------------
  -- consNZ respects eval: evalℚ (consNZ m k p) ≈ℚ evalT(m,k) + evalℚ p.
  ----------------------------------------------------------------------

  consNZ-eval : (m : Mono) (k : ℤ) (p : MPoly) →
                evalℚ (consNZ m k p) ≈ℚ (evalT (term m k) +ℚ evalℚ p)
  consNZ-eval m k p with k ≟ℤ 0ℤ
  ... | yes refl =
    ≈ℚ-sym {evalT (term m 0ℤ) +ℚ evalℚ p} {evalℚ p}
      (≈ℚ-trans {evalT (term m 0ℤ) +ℚ evalℚ p} {0ℚ +ℚ evalℚ p} {evalℚ p}
        (+ℚ-cong {evalT (term m 0ℤ)} {0ℚ} {evalℚ p} {evalℚ p}
                 (evalT-zero m) (≈ℚ-refl (evalℚ p)))
        (+ℚ-identityˡ (evalℚ p)))
  ... | no  _    = ≈ℚ-refl (evalT (term m k) +ℚ evalℚ p)

  ----------------------------------------------------------------------
  -- insertT respects eval — the key lemma (fully-pinned additive chains).
  ----------------------------------------------------------------------

  insertT-eval : (m : Mono) (k : ℤ) (q : MPoly) →
                 evalℚ (insertT m k q) ≈ℚ (evalT (term m k) +ℚ evalℚ q)
  insertT-eval m k []              = consNZ-eval m k []
  insertT-eval m k (term n d ∷ p) with triM m n
  ... | ltM  _    = consNZ-eval m k (term n d ∷ p)
  ... | eqM≡ refl =
    ≈ℚ-trans {evalℚ (consNZ m (k +ℤ d) p)}
             {evalT (term m (k +ℤ d)) +ℚ evalℚ p}
             {evalT (term m k) +ℚ (evalT (term m d) +ℚ evalℚ p)}
      (consNZ-eval m (k +ℤ d) p)
      (≈ℚ-sym {evalT (term m k) +ℚ (evalT (term m d) +ℚ evalℚ p)}
              {evalT (term m (k +ℤ d)) +ℚ evalℚ p}
        (≈ℚ-trans {evalT (term m k) +ℚ (evalT (term m d) +ℚ evalℚ p)}
                  {(evalT (term m k) +ℚ evalT (term m d)) +ℚ evalℚ p}
                  {evalT (term m (k +ℤ d)) +ℚ evalℚ p}
          (≈ℚ-sym {(evalT (term m k) +ℚ evalT (term m d)) +ℚ evalℚ p}
                  {evalT (term m k) +ℚ (evalT (term m d) +ℚ evalℚ p)}
            (+ℚ-assoc (evalT (term m k)) (evalT (term m d)) (evalℚ p)))
          (+ℚ-cong {evalT (term m k) +ℚ evalT (term m d)} {evalT (term m (k +ℤ d))}
                   {evalℚ p} {evalℚ p}
                   (coeff-combine m k d) (≈ℚ-refl (evalℚ p)))))
  ... | gtM  _    =
    ≈ℚ-trans {evalT (term n d) +ℚ evalℚ (insertT m k p)}
             {evalT (term n d) +ℚ (evalT (term m k) +ℚ evalℚ p)}
             {evalT (term m k) +ℚ (evalT (term n d) +ℚ evalℚ p)}
      (+ℚ-cong {evalT (term n d)} {evalT (term n d)}
               {evalℚ (insertT m k p)} {evalT (term m k) +ℚ evalℚ p}
               (≈ℚ-refl (evalT (term n d))) (insertT-eval m k p))
      (≈ℚ-trans {evalT (term n d) +ℚ (evalT (term m k) +ℚ evalℚ p)}
                {(evalT (term n d) +ℚ evalT (term m k)) +ℚ evalℚ p}
                {evalT (term m k) +ℚ (evalT (term n d) +ℚ evalℚ p)}
        (≈ℚ-sym {(evalT (term n d) +ℚ evalT (term m k)) +ℚ evalℚ p}
                {evalT (term n d) +ℚ (evalT (term m k) +ℚ evalℚ p)}
          (+ℚ-assoc (evalT (term n d)) (evalT (term m k)) (evalℚ p)))
        (≈ℚ-trans {(evalT (term n d) +ℚ evalT (term m k)) +ℚ evalℚ p}
                  {(evalT (term m k) +ℚ evalT (term n d)) +ℚ evalℚ p}
                  {evalT (term m k) +ℚ (evalT (term n d) +ℚ evalℚ p)}
          (+ℚ-cong {evalT (term n d) +ℚ evalT (term m k)}
                   {evalT (term m k) +ℚ evalT (term n d)} {evalℚ p} {evalℚ p}
                   (+ℚ-comm (evalT (term n d)) (evalT (term m k))) (≈ℚ-refl (evalℚ p)))
          (+ℚ-assoc (evalT (term m k)) (evalT (term n d)) (evalℚ p))))

  ----------------------------------------------------------------------
  -- β: eval respects normalize.
  ----------------------------------------------------------------------

  normalize-eval : (p : MPoly) → evalℚ p ≈ℚ evalℚ (normalize p)
  normalize-eval []              = ≈ℚ-refl 0ℚ
  normalize-eval (term m k ∷ p)  =
    ≈ℚ-trans {evalT (term m k) +ℚ evalℚ p}
             {evalT (term m k) +ℚ evalℚ (normalize p)}
             {evalℚ (insertT m k (normalize p))}
      (+ℚ-cong {evalT (term m k)} {evalT (term m k)}
               {evalℚ p} {evalℚ (normalize p)}
               (≈ℚ-refl (evalT (term m k))) (normalize-eval p))
      (≈ℚ-sym {evalℚ (insertT m k (normalize p))}
              {evalT (term m k) +ℚ evalℚ (normalize p)}
        (insertT-eval m k (normalize p)))

  ----------------------------------------------------------------------
  -- THE PAYOFF: the two encodings of F agree WHEN EVALUATED. β lifts C2's
  -- rigid polynomial identification `bridgeᵢ` across the evaluator:
  --   evalℚ R.fᵢ ≈ℚ evalℚ(normalize R.fᵢ) ≡[cong evalℚ bridgeᵢ] evalℚ(normalize Cᴹfᵢ) ≈ℚ evalℚ Cᴹfᵢ
  ----------------------------------------------------------------------

  evalBridge₁ : evalℚ f₁ ≈ℚ evalℚ Cᴹf₁
  evalBridge₁ =
    ≈ℚ-trans {evalℚ f₁} {evalℚ (normalize f₁)} {evalℚ Cᴹf₁}
      (normalize-eval f₁)
      (≈ℚ-trans {evalℚ (normalize f₁)} {evalℚ (normalize Cᴹf₁)} {evalℚ Cᴹf₁}
        (≡→≈ℚ (cong evalℚ bridge₁))
        (≈ℚ-sym {evalℚ Cᴹf₁} {evalℚ (normalize Cᴹf₁)} (normalize-eval Cᴹf₁)))

  evalBridge₂ : evalℚ f₂ ≈ℚ evalℚ Cᴹf₂
  evalBridge₂ =
    ≈ℚ-trans {evalℚ f₂} {evalℚ (normalize f₂)} {evalℚ Cᴹf₂}
      (normalize-eval f₂)
      (≈ℚ-trans {evalℚ (normalize f₂)} {evalℚ (normalize Cᴹf₂)} {evalℚ Cᴹf₂}
        (≡→≈ℚ (cong evalℚ bridge₂))
        (≈ℚ-sym {evalℚ Cᴹf₂} {evalℚ (normalize Cᴹf₂)} (normalize-eval Cᴹf₂)))

  evalBridge₃ : evalℚ f₃ ≈ℚ evalℚ Cᴹf₃
  evalBridge₃ =
    ≈ℚ-trans {evalℚ f₃} {evalℚ (normalize f₃)} {evalℚ Cᴹf₃}
      (normalize-eval f₃)
      (≈ℚ-trans {evalℚ (normalize f₃)} {evalℚ (normalize Cᴹf₃)} {evalℚ Cᴹf₃}
        (≡→≈ℚ (cong evalℚ bridge₃))
        (≈ℚ-sym {evalℚ Cᴹf₃} {evalℚ (normalize Cᴹf₃)} (normalize-eval Cᴹf₃)))
