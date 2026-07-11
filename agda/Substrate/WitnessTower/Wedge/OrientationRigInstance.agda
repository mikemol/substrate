{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigInstance
--
-- ⟡rig-UP-instance — inhabiting the RigAlgebra hypotheses (non-vacuity of fold-⊗).
--
--   * `replayᶜ-id` : on the identity LehmerAlgebra, replayᶜ IS replay-aux (a reusable lemma).
--   * `TrivRig`    : the one-point RigAlgebra — a MODEL exists, so the hypotheses are consistent.
--
-- PROBE FINDING (⟡rig-UP-couple). The CANONICAL model — the identity RigAlgebra on LehmerPath
-- (base=start, step=◂, ⊕ᶜ=⊕, ⊗ᶜ=⊗ˢ), whose fold is the identity — does NOT inhabit RigAlgebra as
-- stated. All fields are `refl` EXCEPT ⊗ᶜ-step, which demands
--     replayᶜ idAlg p n l₂ (x ⊗ˢ y)  ≡  (x ◂ p) ⊗ˢ y  =  replay-aux p n y (x ⊗ˢ y)
-- i.e. `replay-aux p n l₂ w ≡ replay-aux p n y w` — TYPE ERROR `l₂ != y`. RigAlgebra.⊗ᶜ-step
-- DECOUPLES the replay DRIVER PATH `l₂` from the multiplicand VALUE `y`, but they are the SAME
-- object: fold-⊗ only ever applies the law at `y = fold l₂`. The decoupled form is a fold-⊗
-- proof-convenience that overshoots what any fold-image model satisfies. ⟡rig-UP-couple = restate
-- ⊗ᶜ-step so `y` is tied to `l₂` (then the canonical LehmerPath model becomes an instance, the true
-- multiplicative twin of ⊕-over). The ⊕ side has no such issue (⊕ᶜ-step is `refl` on LehmerPath).
------------------------------------------------------------------------

module Substrate.WitnessTower.Wedge.OrientationRigInstance where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
  using (replay-aux; offsetDigit)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step)
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal using (replayᶜ)
open import Substrate.WitnessTower.Wedge.OrientationRigInitial using (RigAlgebra)

-- the identity algebra on LehmerPath (base=start, step=◂); its fold is the identity.
idAlg : LehmerAlgebra LehmerPath
idAlg = record { base = start ; step = _◂_ }

-- replayᶜ on the identity algebra IS replay-aux (step idAlg = ◂), by induction on the driver path.
-- A reusable bridge between the algebra-level replay and the LehmerPath-level one.
replayᶜ-id : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ}
             (l : LehmerPath k) (w : LehmerPath (m * n)) →
             replayᶜ idAlg p n l w ≡ replay-aux p n l w
replayᶜ-id p n start   w = refl
replayᶜ-id p n (l ◂ q) w = cong (_◂ offsetDigit p n q) (replayᶜ-id p n l w)

-- The one-point RigAlgebra: every carrier is ⊤, so every law field is refl (⊤ has η). A model
-- exists ⇒ the RigAlgebra / fold-⊗ hypotheses are CONSISTENT (non-vacuous).
TrivRig : RigAlgebra (λ _ → ⊤)
TrivRig = record
  { alg       = record { base = tt ; step = λ _ _ → tt }
  ; _⊕ᶜ_      = λ _ _ → tt
  ; ⊕ᶜ-base   = λ _ → refl
  ; ⊕ᶜ-step   = λ _ _ _ → refl
  ; _⊗ᶜ_      = λ _ _ → tt
  ; ⊗ᶜ-absorb = λ _ → refl
  ; ⊗ᶜ-step   = λ _ _ _ _ → refl
  }
