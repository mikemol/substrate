------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewriteSnRig
--
-- ⟡pyrig-rebuild-semantics-rig (the RECORD) — the genuine non-trivial pyast
-- RigAlgebra: the python-meaningful semantics of a rewrite is the PERMUTATION it
-- denotes, carried by the tower's funext-free Sₙ (`Σ Perm Iso`, the two-sided-inverse
-- witness — a mere-prop WITHOUT funext, unlike `Σ Perm IsPerm`). `interp = foldR SnRig`
-- then lands a genuine Sₙ element: the reordering the pipeline applies to operands.
--
--   SnRig : RigAlgebra (λ n → Σ (Perm n) Iso)
--   interp = foldR SnRig     -- decode-with-witness: a rewrite ↦ its permutation
--
-- EVERY law reduces through `decode` to a DEFINITIONAL LehmerPath identity — the
-- "derived from a LehmerAlgebra, shown equivalent to it" made total:
--   ⊕ᶜ-base   ← blockSum(id-perm 0) τ ≡ τ                    (blockSum-raise, raise 0 = id)
--   ⊕ᶜ-step   ← blockSum(insert-at p σ)τ ≡ insert-at(inject+ p)(blockSum σ τ)
--               via decode-⊕ + the DEFINITIONAL (lσ◂p)⊕lτ = (lσ⊕lτ)◂inject
--   ⊗ᶜ-absorb ← (id-perm 0) ⊗ τ ≡ id-perm 0                  (Perm 0 singleton)
--   ⊗ᶜ-step   ← perm-⊗ᶜ-step-decode (PyAstRewritePermRig), lifted through decode-encode
-- and the Σ-equalities collapse to their Perm component via Iso-prop (`snEq`).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewriteSnRig where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; Σ-≡,≡→≡)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.FirstAppearance using (id-perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; IsPerm-[]; insert-at-preserves)
open import Substrate.WitnessTower.Wedge.OrientationDistributor using (blockSum; blockSum-raise)
open import Substrate.WitnessTower.Wedge.OrientationSumDecode using (decode-⊕)
open import Substrate.WitnessTower.Wedge.IsoDecodeLift using (on-iso; on-iso₂)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductPerm using (⊗-is-perm)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural using (offsetDigit)
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym using (Iso; Iso-prop; IsPerm→Iso; Iso→IsPerm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatSymUP using (iso-blockSum)
open import Substrate.WitnessTower.Wedge.OrientationUniversal using (LehmerAlgebra; fold)
open import Substrate.WitnessTower.Wedge.OrientationRigInitial using (RigAlgebra; foldR)
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal using (replayᶜ)
open import Substrate.WitnessTower.Wedge.PyAstRewritePermRig
  using (permAlg; fold-permAlg≡decode; perm-⊗ᶜ-step-decode)

------------------------------------------------------------------------
-- 0. THE CARRIER: the funext-free Sₙ (permutation + two-sided-inverse witness).
------------------------------------------------------------------------
Sₙ : ℕ → Set
Sₙ n = Σ (Perm n) Iso

-- reduce an Sₙ-equality to its Perm component (Iso-prop kills the witness — funext-free).
snEq : ∀ {n} {a b : Sₙ n} → proj₁ a ≡ proj₁ b → a ≡ b
snEq {a = a} {b = b} e = Σ-≡,≡→≡ (e , Iso-prop {σ = proj₁ b} _ _)

------------------------------------------------------------------------
-- 1. THE PERM-LEVEL LAWS. decode-⊕ (decode is a ⊕-hom) is reused from the tower
--    (OrientationSumDecode); the decode-input lemmas lift to any Iso element via
--    IsoDecodeLift's on-iso / on-iso₂ (decode-density). ⊗ᶜ-step is the imported heart.
------------------------------------------------------------------------
-- ⊕ᶜ-base: 0-block is a left unit for blockSum.
blockSum-idˡ : ∀ {n} (τ : Perm n) → blockSum (id-perm 0) τ ≡ τ
blockSum-idˡ τ = lookup-ext _ _ (λ k → blockSum-raise (id-perm 0) τ k)

-- ⊗ᶜ-absorb: 0 · n = 0, so the product is the unique Perm 0.
⊗-absorb0 : ∀ {n} (τ : Perm n) → (id-perm 0) ⊗ τ ≡ id-perm 0
⊗-absorb0 τ = lookup-ext _ _ (λ ())

-- ⊕ᶜ-step, on decode-inputs: the DEFINITIONAL (lσ◂p)⊕lτ = (lσ⊕lτ)◂inject, read through decode-⊕.
blockSum-insert-decode : ∀ {m n} (lσ : LehmerPath m) (p : Fin (suc m)) (lτ : LehmerPath n) →
  blockSum (insert-at p (decode lσ)) (decode lτ)
    ≡ insert-at (inject+ n p) (blockSum (decode lσ) (decode lτ))
blockSum-insert-decode lσ p lτ =
  trans (sym (decode-⊕ (lσ ◂ p) lτ)) (cong (insert-at (inject+ _ p)) (decode-⊕ lσ lτ))

-- lift to any Sₙ element via on-iso₂ (decode-density: σ = decode (encode σ)).
blockSum-insertˡ : ∀ {m n} (σ : Perm m) (iσ : Iso σ) (p : Fin (suc m)) (τ : Perm n) (iτ : Iso τ) →
  blockSum (insert-at p σ) τ ≡ insert-at (inject+ n p) (blockSum σ τ)
blockSum-insertˡ {m} {n} σ iσ p τ iτ =
  on-iso₂ {P = λ σ' τ' → blockSum (insert-at p σ') τ' ≡ insert-at (inject+ n p) (blockSum σ' τ')}
          (λ lσ lτ → blockSum-insert-decode lσ p lτ) σ iσ τ iτ

-- ⊗ᶜ-step, lifted to any Sₙ element via on-iso.
perm-⊗ᶜ-step-iso : ∀ {m n} (σ : Perm m) (iσ : Iso σ) (p : Fin (suc m)) (l₂ : LehmerPath n) →
  replayᶜ permAlg p n l₂ (σ ⊗ decode l₂) ≡ (insert-at p σ ⊗ decode l₂)
perm-⊗ᶜ-step-iso {m} {n} σ iσ p l₂ =
  on-iso {P = λ σ' → replayᶜ permAlg p n l₂ (σ' ⊗ decode l₂) ≡ (insert-at p σ' ⊗ decode l₂)}
         (λ lx → perm-⊗ᶜ-step-decode lx p l₂) σ iσ

------------------------------------------------------------------------
-- 3. THE Sₙ LehmerAlgebra + Σ-naturality of fold / replayᶜ.
------------------------------------------------------------------------
snAlg : LehmerAlgebra Sₙ
snAlg = record
  { base = id-perm 0 , IsPerm→Iso (id-perm 0) IsPerm-[]
  ; step = λ x p → insert-at p (proj₁ x)
                 , IsPerm→Iso (insert-at p (proj₁ x)) (insert-at-preserves p (proj₁ x) (Iso→IsPerm (proj₁ x) (proj₂ x)))
  }

proj₁-fold : ∀ {n} (l : LehmerPath n) → proj₁ (fold snAlg l) ≡ decode l
proj₁-fold start   = refl
proj₁-fold (l ◂ p) = cong (insert-at p) (proj₁-fold l)

proj₁-replayᶜ : ∀ {m k} (p : Fin (suc m)) (n : ℕ) (l : LehmerPath k) (w : Sₙ (m * n)) →
  proj₁ (replayᶜ snAlg p n l w) ≡ replayᶜ permAlg p n l (proj₁ w)
proj₁-replayᶜ p n start   w = refl
proj₁-replayᶜ p n (l ◂ q) w = cong (insert-at (offsetDigit p n q)) (proj₁-replayᶜ p n l w)

------------------------------------------------------------------------
-- 4. THE RECORD — the genuine non-trivial pyast RigAlgebra.
------------------------------------------------------------------------
SnRig : RigAlgebra Sₙ
SnRig = record
  { alg       = snAlg
  ; _⊕ᶜ_      = λ x y → blockSum (proj₁ x) (proj₁ y) , iso-blockSum (proj₁ x) (proj₁ y) (proj₂ x) (proj₂ y)
  ; ⊕ᶜ-base   = λ y → snEq (blockSum-idˡ (proj₁ y))
  ; ⊕ᶜ-step   = λ x p y → snEq (blockSum-insertˡ (proj₁ x) (proj₂ x) p (proj₁ y) (proj₂ y))
  ; _⊗ᶜ_      = λ x y → proj₁ x ⊗ proj₁ y
                      , IsPerm→Iso (proj₁ x ⊗ proj₁ y)
                          (⊗-is-perm (proj₁ x) (proj₁ y) (Iso→IsPerm (proj₁ x) (proj₂ x)) (Iso→IsPerm (proj₁ y) (proj₂ y)))
  ; ⊗ᶜ-absorb = λ y → snEq (⊗-absorb0 (proj₁ y))
  ; ⊗ᶜ-step   = λ x p l₂ → snEq
      (trans (proj₁-replayᶜ p _ l₂ (proj₁ x ⊗ proj₁ (fold snAlg l₂) , _))
      (trans (cong (λ z → replayᶜ permAlg p _ l₂ (proj₁ x ⊗ z)) (proj₁-fold l₂))
      (trans (perm-⊗ᶜ-step-iso (proj₁ x) (proj₂ x) p l₂)
             (cong (λ z → insert-at p (proj₁ x) ⊗ z) (sym (proj₁-fold l₂))))))
  }

------------------------------------------------------------------------
-- 5. THE SEMANTICS: interp = foldR SnRig — a rewrite ↦ its permutation (with witness).
------------------------------------------------------------------------
interp : {n : ℕ} → LehmerPath n → Sₙ n
interp = foldR SnRig

-- the permutation a rewrite denotes IS its decode (the reordering applied to operands).
interp-is-decode : ∀ {n} (l : LehmerPath n) → proj₁ (interp l) ≡ decode l
interp-is-decode = proj₁-fold
