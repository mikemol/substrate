------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewritePermRig.LehmerOtimesCrux
--
-- Defines: lehmer-⊗ᶜ-crux
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.PyAstRewritePermRig; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewritePermRig.LehmerOtimesCrux where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.Wedge.OrientationProduct
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal
open import Substrate.WitnessTower.Wedge.OrientationRigInstance
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- 2. THE LehmerPath-LEVEL CRUX: replaying l₂'s offset-digits over (lx ⊗ˢ l₂) rebuilds
--    (lx ◂ p) ⊗ˢ l₂. This IS `lehmer-⊗ᶜ-step`, with fold idAlg collapsed to the
--    identity and replayᶜ collapsed to replay-aux (both proven in the tower).
------------------------------------------------------------------------
lehmer-⊗ᶜ-crux : ∀ {m n} (lx : LehmerPath m) (p : Fin (suc m)) (l₂ : LehmerPath n) →
                 replay-aux p n l₂ (lx ⊗ˢ l₂) ≡ ((lx ◂ p) ⊗ˢ l₂)
lehmer-⊗ᶜ-crux lx p l₂ =
  trans (sym (replayᶜ-id p _ l₂ (lx ⊗ˢ l₂)))
  (trans (cong (λ z → replayᶜ idAlg p _ l₂ (lx ⊗ˢ z)) (sym (fold-idAlg l₂)))
  (trans (lehmer-⊗ᶜ-step lx p l₂)
         (cong (λ z → (lx ◂ p) ⊗ˢ z) (fold-idAlg l₂))))
