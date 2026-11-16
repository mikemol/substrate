------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewritePermRig.PermOtimesStepDecode
--
-- Defines: perm-⊗ᶜ-step-decode
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.PyAstRewritePermRig; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewritePermRig.PermOtimesStepDecode where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.Wedge.OrientationProduct
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
open import Substrate.WitnessTower.Wedge.OrientationProductStructuralDecode
open import Substrate.WitnessTower.Wedge.OrientationUniversal
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal
open import Substrate.WitnessTower.Wedge.PyAstRewritePermRig.PermAlg
open import Substrate.WitnessTower.Wedge.PyAstRewritePermRig.FoldPermAlgEqdecode
open import Substrate.WitnessTower.Wedge.PyAstRewritePermRig.LehmerOtimesCrux
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- 3. THE ⊗ᶜ-STEP for the permutation carrier, on every decode-input. The block-step
--    coherence that makes the Perm-valued fold a rig ⊗-homomorphism.
------------------------------------------------------------------------
perm-⊗ᶜ-step-decode :
  ∀ {m n} (lx : LehmerPath m) (p : Fin (suc m)) (l₂ : LehmerPath n) →
  replayᶜ permAlg p n l₂ (decode lx ⊗ decode l₂)
    ≡ (insert-at p (decode lx) ⊗ decode l₂)
perm-⊗ᶜ-step-decode lx p l₂ =
  trans (cong (replayᶜ permAlg p _ l₂) (sym (decode-⊗ˢ lx l₂)))
  (trans (cong (replayᶜ permAlg p _ l₂) (sym (fold-permAlg≡decode (lx ⊗ˢ l₂))))
  (trans (sym (fold-replay permAlg p _ l₂ (lx ⊗ˢ l₂)))
  (trans (fold-permAlg≡decode (replay-aux p _ l₂ (lx ⊗ˢ l₂)))
  (trans (cong decode (lehmer-⊗ᶜ-crux lx p l₂))
         (decode-⊗ˢ (lx ◂ p) l₂)))))
