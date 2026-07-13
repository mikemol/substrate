------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewritePermRig
--
-- ⟡pyrig-rebuild-semantics-rig — the MATHEMATICAL HEART of a non-trivial pyast
-- RigAlgebra: the python-meaningful semantics of a rewrite is the PERMUTATION it
-- denotes (`decode` — the actual reordering the pipeline applies to operands), and
-- this reading RESPECTS the rig ⊗ — i.e. it is a rig homomorphism, DERIVED from the
-- tower's LehmerRig and shown EQUIVALENT to it (decode is the LehmerPath ≅ Perm iso).
--
-- The crux of any RigAlgebra is the `⊗ᶜ-step` coherence
--   replayᶜ alg p n l₂ (x ⊗ᶜ fold alg l₂) ≡ step alg x p ⊗ᶜ fold alg l₂
-- (the block-step law — the multiplicative analog of ⊕ᶜ-step). For the permutation
-- carrier (alg = {[], insert-at}, fold = decode, ⊗ᶜ = the Perm product ⊗) this is
-- PROVEN here for every decode-input, by REDUCTION to the tower's own
-- `lehmer-⊗ᶜ-step`:
--
--   replayᶜ permAlg p n l₂ (decode lx ⊗ decode l₂)
--     ≡ decode (replay-aux p n l₂ (lx ⊗ˢ l₂))     [decode-⊗ˢ; fold-replay; fold≡decode]
--     ≡ decode ((lx ◂ p) ⊗ˢ l₂)                   [lehmer-⊗ᶜ-crux = lehmer-⊗ᶜ-step]
--     ≡ insert-at p (decode lx) ⊗ decode l₂        [decode-⊗ˢ; decode(l◂p) def]
--
-- LOAD-BEARING (the structural content the reduction SURFACES, not papers over):
-- the input must be a decode-image — a genuine PERMUTATION. On raw `Perm n` (the
-- transformation monoid Tₙ, arbitrary vectors) the identity is NOT available by this
-- route; the `IsPerm` witness is essential. So the honest carrier of the full
-- RigAlgebra is `Sₙ = Σ Perm IsPerm` (where every `x = decode (encode x)`), and this
-- module is its ⊗ᶜ-step obligation, discharged. (The remaining Σ-carrier packaging —
-- the other three definitional laws + IsPerm-preservation of the ops — is
-- ⟡pyrig-rebuild-semantics-rig-record.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewritePermRig where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; _◂_; start; decode)
open import Substrate.WitnessTower.FirstAppearance using (id-perm)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural using (_⊗ˢ_; replay-aux)
open import Substrate.WitnessTower.Wedge.OrientationProductStructuralDecode using (decode-⊗ˢ)
open import Substrate.WitnessTower.Wedge.OrientationUniversal using (LehmerAlgebra; fold)
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal using (replayᶜ; fold-replay)
open import Substrate.WitnessTower.Wedge.OrientationRigInstance
  using (idAlg; fold-idAlg; replayᶜ-id; lehmer-⊗ᶜ-step)

------------------------------------------------------------------------
-- 1. THE PERMUTATION ALGEBRA: base = the empty perm, step = insert-at. Its fold IS
--    `decode` — the LehmerAlgebra underlying the permutation-carrier RigAlgebra.
------------------------------------------------------------------------
permAlg : LehmerAlgebra Perm
permAlg = record { base = id-perm 0 ; step = λ x p → insert-at p x }

-- fold permAlg ≡ decode: the "derived from a LehmerAlgebra, shown equivalent" — the
-- permutation reading is exactly the tower's decode.
fold-permAlg≡decode : ∀ {n} (l : LehmerPath n) → fold permAlg l ≡ decode l
fold-permAlg≡decode start   = refl
fold-permAlg≡decode (l ◂ p) = cong (insert-at p) (fold-permAlg≡decode l)

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
