------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewriteAct
--
-- ⟡pyrig-rebuild-act — the rewrite ACTION on the object carrier. This SURVIVES the
-- SPPF-built-wrong correction unchanged: the correction was that the RIG (morphisms)
-- is LehmerPath, not SPPF — but the OBJECT carrier IS SPPF over operand positions
-- (`Objpy = SPPF (Fin n)`, PyAstRig), and a rewrite acts on it by DECODE-THEN-APPLY:
--
--   actR l = act (decode l)   -- decode the rewrite to its permutation, apply it
--
-- This is exactly `PyAstRig.pyRecon` transposed (`pyRecon rep r = act (decode r) rep`)
-- — the reconstruction map, read as the action. Its functoriality is PyAstRig's OWN
-- `act-id` / `act-∘` (the free functoriality of `mapSPPF` over `apply`'s group-
-- homomorphy), reused verbatim; nothing new to prove. And it is the action of the
-- permutation a rewrite DENOTES under the SnRig semantics (`interp`): `actR-interp`.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewriteAct where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (proj₁)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath using (decode)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.Wedge.PyAstRig using (Objpy; act; act-id; act-∘; pyRecon)
open import Substrate.WitnessTower.Wedge.PyAstRewrite using (PyRewrite)
open import Substrate.WitnessTower.Wedge.PyAstRewriteSnRig using (interp; interp-is-decode)

-- THE REWRITE ACTION: decode-then-apply. A rewrite reorders a term's operand positions.
actR : {n : ℕ} → PyRewrite n → Objpy n → Objpy n
actR l = act (decode l)

-- it IS PyAstRig's pyRecon, transposed — the reconstruction map read as the action (definitional).
actR-is-pyRecon : {n : ℕ} (l : PyRewrite n) (rep : Objpy n) → actR l rep ≡ pyRecon rep l
actR-is-pyRecon l rep = refl

-- FUNCTORIALITY, inherited through decode from PyAstRig's act-∘ (semantics-preserving by construction):
-- composing the actions = acting by the composed permutation.
actR-∘ : {n : ℕ} (l l' : PyRewrite n) (t : Objpy n) →
         act (compose (decode l) (decode l')) t ≡ actR l (actR l' t)
actR-∘ l l' t = act-∘ (decode l) (decode l') t

-- IDENTITY: any rewrite whose permutation is the identity acts trivially (act-id through decode).
actR-id : {n : ℕ} (l : PyRewrite n) (t : Objpy n) → decode l ≡ id-perm n → actR l t ≡ t
actR-id l t eq = trans (cong (λ σ → act σ t) eq) (act-id t)

-- THE ACTION IS BY THE DENOTED PERMUTATION: a rewrite acts as its SnRig interpretation.
actR-interp : {n : ℕ} (l : PyRewrite n) (t : Objpy n) → actR l t ≡ act (proj₁ (interp l)) t
actR-interp l t = cong (λ σ → act σ t) (sym (interp-is-decode l))
