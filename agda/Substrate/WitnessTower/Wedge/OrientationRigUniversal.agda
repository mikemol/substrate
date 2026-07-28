------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigUniversal
--
-- ⟡rig-UP-wreath (Step C) — the fold is a ⊗-HOMOMORPHISM, mirroring
-- OrientationUniversal.fold-⊕ EXACTLY. Together with fold-⊕, the unique
-- catamorphism `fold` out of the initial Lehmer algebra is SIMULTANEOUSLY the
-- additive and the multiplicative homomorphism — the single fold that IS the
-- symmetric-rig structure map (the wreath catamorphism).
--
-- Like fold-⊕, this is PURELY STRUCTURAL: it never touches `decode`. It takes an
-- algebra-level product `_⊗ᶜ_` with two laws (an absorbing base and a block-step
-- law) and proves `fold (l₁ ⊗ˢ l₂) ≡ fold l₁ ⊗ᶜ fold l₂` by induction on l₁, over
-- the fold-transparent `_⊗ˢ_` (OrientationProductStructural).
--
-- The one structural difference from fold-⊕: a ◂-rung of l₁ expands to a BLOCK of
-- n rungs (replaying l₂), so the block-step law is stated through the algebra-level
-- replay `replayᶜ` (the C-image of `replay-aux`). `fold-replay` shows `fold`
-- commutes with the replay (fold ∘ replay-aux ≡ replayᶜ ∘ fold) — the n-fold
-- `step` push-through — so the induction closes exactly as fold-⊕'s does.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigUniversal where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
  using (offsetDigit; replay-aux; replayOffset; _⊗ˢ_)

------------------------------------------------------------------------
-- 1. replayᶜ: the algebra-level replay — the C-image of `replay-aux`. Each rung
--    of the length-k fragment fires one `step` at the SAME offset digit.
------------------------------------------------------------------------

replayᶜ : ∀ {C} (alg : LehmerAlgebra C) {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ} →
          LehmerPath k → C (m * n) → C (k + m * n)
replayᶜ alg p n start   x = x
replayᶜ alg p n (l ◂ q) x = step alg (replayᶜ alg p n l x) (offsetDigit p n q)

------------------------------------------------------------------------
-- 2. fold COMMUTES with the replay: fold ∘ replay-aux ≡ replayᶜ ∘ fold. Both push
--    the same offset digits through the same `step`; induction on the fragment.
------------------------------------------------------------------------

fold-replay : ∀ {C} (alg : LehmerAlgebra C) {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ}
              (l : LehmerPath k) (b : LehmerPath (m * n)) →
              fold alg (replay-aux p n l b) ≡ replayᶜ alg p n l (fold alg b)
fold-replay alg p n start   b = refl
fold-replay alg p n (l ◂ q) b =
  cong (λ z → step alg z (offsetDigit p n q)) (fold-replay alg p n l b)

------------------------------------------------------------------------
-- 3. THE FOLD IS A ⊗-HOMOMORPHISM. Mirror of fold-⊕: an absorbing base
--    (0·n = 0, the multiplicative analog of ⊕ᶜ-base's 0+n=n) and a BLOCK-step law
--    `replayᶜ p n l₂ (x ⊗ᶜ y) ≡ (step x p) ⊗ᶜ y` (the n-rung analog of ⊕ᶜ-step's
--    single-rung `step (x ⊕ᶜ y) (inject+ n p)`). Induction on l₁; the ◂-step uses
--    fold-replay to expose the block, the IH under replayᶜ, then the step law.
------------------------------------------------------------------------

fold-⊗ : ∀ {C} (alg : LehmerAlgebra C)
         (_⊗ᶜ_ : ∀ {i j} → C i → C j → C (i * j))
         (⊗ᶜ-absorb : ∀ {n} (y : C n) → (base alg ⊗ᶜ y) ≡ base alg)
         -- ⊗ᶜ-step COUPLED: the multiplicand is `fold alg l₂` (the block's own image), not a free
         -- `y`. fold-⊗ only ever needs y = fold alg l₂, and coupling lets the canonical LehmerPath
         -- model (fold idAlg = id) satisfy it (⟡rig-UP-couple / OrientationRigInstance.LehmerRig).
         (⊗ᶜ-step : ∀ {m n} (x : C m) (p : Fin (suc m)) (l₂ : LehmerPath n) →
                    replayᶜ alg p n l₂ (x ⊗ᶜ fold alg l₂) ≡ (step alg x p ⊗ᶜ fold alg l₂)) →
         ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
         fold alg (l₁ ⊗ˢ l₂) ≡ (fold alg l₁ ⊗ᶜ fold alg l₂)
fold-⊗ alg _⊗ᶜ_ ab st start    l₂ = sym (ab (fold alg l₂))
fold-⊗ alg _⊗ᶜ_ ab st (l₁ ◂ p) l₂ =
  trans (fold-replay alg p _ l₂ (l₁ ⊗ˢ l₂))
        (trans (cong (replayᶜ alg p _ l₂) (fold-⊗ alg _⊗ᶜ_ ab st l₁ l₂))
               (st (fold alg l₁) p l₂))
