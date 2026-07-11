{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigInstance
--
-- ⟡rig-UP-instance / ⟡rig-UP-couple — inhabiting the RigAlgebra hypotheses, with the CANONICAL
-- model now an instance (after ⊗ᶜ-step was coupled: the multiplicand is `fold alg l₂`, tied to
-- the driver path l₂, not a free `y`).
--
--   LehmerRig : RigAlgebra LehmerPath   — the IDENTITY rig-algebra (base=start, step=◂, ⊕ᶜ=⊕,
--               ⊗ᶜ=⊗ˢ), whose fold is the identity. THE multiplicative twin of ⊕-over: LehmerPath
--               with its own ⊕/⊗ˢ is a model of its own universal property.
--   TrivRig   : RigAlgebra (λ _ → ⊤)    — the one-point model (hypotheses independently consistent).
--   replayᶜ-id, fold-idAlg — the two supporting lemmas.
--
-- HISTORY (⟡rig-UP-couple, resolved). Before the coupling, ⊗ᶜ-step decoupled the driver path l₂
-- from the multiplicand value y and LehmerRig FAILED with `l₂ != y` (fold-⊗ only ever used it at
-- y = fold l₂). Tying y := fold alg l₂ lets the canonical model satisfy it: with fold idAlg = id,
-- ⊗ᶜ-step becomes replayᶜ idAlg … ≡ (◂-of-x) ⊗ˢ l₂ = replay-aux …, closed by replayᶜ-id.
------------------------------------------------------------------------

module Substrate.WitnessTower.Wedge.OrientationRigInstance where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
  using (_⊗ˢ_; replay-aux; offsetDigit)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold)
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal using (replayᶜ)
open import Substrate.WitnessTower.Wedge.OrientationRigInitial using (RigAlgebra)

-- the identity algebra on LehmerPath (base=start, step=◂).
idAlg : LehmerAlgebra LehmerPath
idAlg = record { base = start ; step = _◂_ }

-- its fold is the identity (by induction — step idAlg = ◂ reconstructs the path).
fold-idAlg : ∀ {n} (l : LehmerPath n) → fold idAlg l ≡ l
fold-idAlg start   = refl
fold-idAlg (l ◂ p) = cong (_◂ p) (fold-idAlg l)

-- replayᶜ on the identity algebra IS replay-aux (step idAlg = ◂), by induction on the driver path.
replayᶜ-id : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ}
             (l : LehmerPath k) (w : LehmerPath (m * n)) →
             replayᶜ idAlg p n l w ≡ replay-aux p n l w
replayᶜ-id p n start   w = refl
replayᶜ-id p n (l ◂ q) w = cong (_◂ offsetDigit p n q) (replayᶜ-id p n l w)

-- the coupled ⊗ᶜ-step for the canonical model: fold idAlg l₂ ≡ l₂ (rewrite), then replayᶜ-id
-- ((x ◂ p) ⊗ˢ l₂ = replayOffset p l₂ (x ⊗ˢ l₂) = replay-aux p n l₂ (x ⊗ˢ l₂), definitionally).
lehmer-⊗ᶜ-step : ∀ {m n} (x : LehmerPath m) (p : Fin (suc m)) (l₂ : LehmerPath n) →
                 replayᶜ idAlg p n l₂ (x ⊗ˢ fold idAlg l₂) ≡ ((x ◂ p) ⊗ˢ fold idAlg l₂)
lehmer-⊗ᶜ-step x p l₂ rewrite fold-idAlg l₂ = replayᶜ-id p _ l₂ (x ⊗ˢ l₂)

-- THE canonical instance: LehmerPath with ⊕ / ⊗ˢ is a model of the rig UP. Additive fields are
-- refl (⊕ᶜ-base/⊕ᶜ-step definitional); the multiplicative block-step is lehmer-⊗ᶜ-step.
LehmerRig : RigAlgebra LehmerPath
LehmerRig = record
  { alg       = idAlg
  ; _⊕ᶜ_      = _⊕_
  ; ⊕ᶜ-base   = λ y → refl
  ; ⊕ᶜ-step   = λ x p y → refl
  ; _⊗ᶜ_      = _⊗ˢ_
  ; ⊗ᶜ-absorb = λ y → refl
  ; ⊗ᶜ-step   = lehmer-⊗ᶜ-step
  }

-- the one-point model: every carrier ⊤, every law refl (⊤ has η). Independent consistency witness.
TrivRig : RigAlgebra (λ _ → ⊤)
TrivRig = record
  { alg       = record { base = tt ; step = λ _ _ → tt }
  ; _⊕ᶜ_      = λ _ _ → tt
  ; ⊕ᶜ-base   = λ _ → refl
  ; ⊕ᶜ-step   = λ _ _ _ → refl
  ; _⊗ᶜ_      = λ _ _ → tt
  ; ⊗ᶜ-absorb = λ _ → refl
  ; ⊗ᶜ-step   = λ _ _ _ → refl
  }
