------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigFreeUP
--
-- ⟡rig-UP-free-UP — the GENERIC free-rig-algebra universal property, where a
-- homomorphism respects ONLY ⊕ / ⊗ / rotation(braid) / one — NOT the generating
-- insertion move ◂ directly. ◂ is then respected BECAUSE it is DERIVED:
--
--   ◂  =  rotation ∘ (one ⊕ ·)              (OrientationRigFree: ◂ = ρ_p ∘ (X⊕·))
--
-- Three steps, each green before the next, all reuse of the committed core:
--
--   S1 (THE CRUX):  rotᴸ p : LehmerPath(suc n) → LehmerPath(suc n) and
--                   ◂-as-rot : (l ◂ p) ≡ rotᴸ p (X ⊕ l)     — at the path level.
--   S2:  FreeRigAlgebra record (DERIVED step stepᶜ x p = rotᶜ p (one ⊕ᶜ x)),
--        its LehmerAlgebra, foldF, and foldF-⊕ / foldF-⊗.
--   S3:  foldF-free-unique — a map respecting ⊕ᶜ / rotᶜ / one respects stepᶜ
--        (via S1), hence = foldF by fold-unique. The UP where homs never mention ◂.
--
-- Zero postulates, zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigFreeUP where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Vec using (Vec; map)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; lookup-map)
open import Substrate.WitnessTower.LehmerPath
  using (LehmerPath; start; _◂_; decode; encode; decode-is-perm; decode-encode)
open import Substrate.WitnessTower.Wedge.OrientationFixedPoint using (decode-injective)
open import Substrate.WitnessTower.Wedge.OrientationRigFree
  using (ρ; ρ-injective; decode-◂-rot; X)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural using (_⊗ˢ_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-unique; fold-⊕)
open import Substrate.WitnessTower.Wedge.OrientationRigUniversal using (replayᶜ; fold-⊗)

------------------------------------------------------------------------
-- S1 — THE CRUX. The path-level rotation rotᴸ p and the dissolution of ◂ into it.
--
-- The IMAGE-vector rotation map (ρ p) preserves the permutation property: ρ p is
-- injective (ρ-injective), so mapping it over an injective image vector stays
-- injective. This is the witness rotᴸ needs to re-encode the rotated image.
------------------------------------------------------------------------

map-ρ-perm : ∀ {n} (p : Fin (suc n)) (v : Perm (suc n)) →
             IsPerm v → IsPerm (map (ρ p) v)
map-ρ-perm p v v-perm i j eq =
  v-perm i j
    (ρ-injective p
      (trans (sym (lookup-map (ρ p) v i))
             (trans eq (lookup-map (ρ p) v j))))

-- rotᴸ p : the path-level rotation. Decode to the image vector, rotate the head
-- into rank p via ρ p (pointwise), and re-encode. It is the transport of ρ p
-- through the decode/encode iso — a genuine endo of LehmerPath (suc n).
rotᴸ : ∀ {n} → Fin (suc n) → LehmerPath (suc n) → LehmerPath (suc n)
rotᴸ p σ = encode (map (ρ p) (decode σ))
                  (map-ρ-perm p (decode σ) (decode-is-perm σ))

-- THE CRUX: ◂ IS the rotation of the generator block-sum, at the path level.
--   decode (l ◂ p)         ≡ map (ρ p) (decode (X ⊕ l))          (decode-◂-rot)
--   decode (rotᴸ p (X⊕l))  ≡ map (ρ p) (decode (X ⊕ l))          (decode-encode)
-- so both decode equally; decode-injective closes the path equality.
◂-as-rot : ∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
           (l ◂ p) ≡ rotᴸ p (X ⊕ l)
◂-as-rot l p =
  decode-injective (l ◂ p) (rotᴸ p (X ⊕ l))
    (trans (decode-◂-rot l p)
           (sym (decode-encode (map (ρ p) (decode (X ⊕ l)))
                               (map-ρ-perm p (decode (X ⊕ l))
                                           (decode-is-perm (X ⊕ l))))))

------------------------------------------------------------------------
-- S2 — the DERIVED-STEP braided free-rig-algebra. A graded carrier with base,
-- one, ⊕ᶜ, ⊗ᶜ, and a rotation rotᶜ. The tower step is NOT fielded — it is DERIVED:
--
--   stepᶜ x p := rotᶜ p (one ⊕ᶜ x)
--
-- The coherence fields are exactly the fold-⊕ / fold-⊗ hypotheses read through
-- this derived step — the genuinely-new rotation-compat laws.
------------------------------------------------------------------------

record FreeRigAlgebra (C : ℕ → Set) : Set where
  field
    zeroᶜ : C 0
    oneᶜ  : C 1
    _⊕ᶜ_  : ∀ {i j} → C i → C j → C (i + j)
    _⊗ᶜ_  : ∀ {i j} → C i → C j → C (i * j)
    rotᶜ  : ∀ {n} → Fin (suc n) → C (suc n) → C (suc n)

  -- the DERIVED tower step and its LehmerAlgebra (manifest fields).
  stepᶜ : ∀ {n} → C n → Fin (suc n) → C (suc n)
  stepᶜ x p = rotᶜ p (oneᶜ ⊕ᶜ x)

  algᶜ : LehmerAlgebra C
  algᶜ = record { base = zeroᶜ ; step = stepᶜ }

  field
    -- ⊕ coherence: absorbing base + the rotation-compat additive step law
    -- (fold-⊕'s ⊕ᶜ-base / ⊕ᶜ-step with step = stepᶜ).
    ⊕ᶜ-base : ∀ {n} (y : C n) → (zeroᶜ ⊕ᶜ y) ≡ y
    ⊕ᶜ-step : ∀ {m n} (x : C m) (p : Fin (suc m)) (y : C n) →
              (stepᶜ x p ⊕ᶜ y) ≡ stepᶜ (x ⊕ᶜ y) (inject+ n p)
    -- ⊗ coherence: absorbing base + the rotation-compat multiplicative block-step
    -- law (fold-⊗'s ⊗ᶜ-absorb / ⊗ᶜ-step with step = stepᶜ, through replayᶜ).
    ⊗ᶜ-absorb : ∀ {n} (y : C n) → (zeroᶜ ⊗ᶜ y) ≡ zeroᶜ
    ⊗ᶜ-step   : ∀ {m n} (x : C m) (p : Fin (suc m)) (l₂ : LehmerPath n) →
                replayᶜ algᶜ p n l₂ (x ⊗ᶜ fold algᶜ l₂) ≡ (stepᶜ x p ⊗ᶜ fold algᶜ l₂)

open FreeRigAlgebra public

------------------------------------------------------------------------
-- The free-rig fold and its rig-homomorphy: foldF is the ◂-catamorphism on the
-- derived LehmerAlgebra, and it respects ⊕ᶜ and ⊗ᶜ by fold-⊕ / fold-⊗ on the
-- coherence fields (which are DEFINITIONALLY the fold-⊕/⊗ hypotheses).
------------------------------------------------------------------------

foldF : ∀ {C} (F : FreeRigAlgebra C) → ∀ {n} → LehmerPath n → C n
foldF F = fold (algᶜ F)

foldF-⊕ : ∀ {C} (F : FreeRigAlgebra C) {m n}
          (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
          foldF F (l₁ ⊕ l₂) ≡ (_⊕ᶜ_ F (foldF F l₁) (foldF F l₂))
foldF-⊕ F = fold-⊕ (algᶜ F) (_⊕ᶜ_ F) (⊕ᶜ-base F) (⊕ᶜ-step F)

foldF-⊗ : ∀ {C} (F : FreeRigAlgebra C) {m n}
          (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
          foldF F (l₁ ⊗ˢ l₂) ≡ (_⊗ᶜ_ F (foldF F l₁) (foldF F l₂))
foldF-⊗ F = fold-⊗ (algᶜ F) (_⊗ᶜ_ F) (⊗ᶜ-absorb F) (⊗ᶜ-step F)

------------------------------------------------------------------------
-- S3 — THE FREE-RIG-ALGEBRA UNIVERSAL PROPERTY. A map g respecting one, ⊕ᶜ, and
-- the rotation rotᶜ (via the path-level rotᴸ) automatically respects the derived
-- step stepᶜ — BECAUSE ◂ = rotᴸ ∘ (X ⊕ ·) (S1). Hence g IS foldF, by fold-unique.
-- The homomorphism conditions NEVER mention the generating move ◂.
--
--   g (l ◂ p) = g (rotᴸ p (X ⊕ l))          -- ◂-as-rot
--             = rotᶜ p (g (X ⊕ l))           -- g respects rotᴸ
--             = rotᶜ p (g X ⊕ᶜ g l)          -- g respects ⊕
--             = rotᶜ p (one ⊕ᶜ g l)          -- g respects one
--             = stepᶜ (g l) p                -- definition of stepᶜ
------------------------------------------------------------------------

foldF-free-unique :
  ∀ {C} (F : FreeRigAlgebra C) (g : ∀ {n} → LehmerPath n → C n) →
  (g start ≡ zeroᶜ F) →
  (g X ≡ oneᶜ F) →
  (∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
     g (l₁ ⊕ l₂) ≡ (_⊕ᶜ_ F (g l₁) (g l₂))) →
  (∀ {n} (p : Fin (suc n)) (σ : LehmerPath (suc n)) →
     g (rotᴸ p σ) ≡ rotᶜ F p (g σ)) →
  ∀ {n} (l : LehmerPath n) → g l ≡ foldF F l
foldF-free-unique F g g-zero g-one g-⊕ g-rot =
  fold-unique (algᶜ F) g g-zero g-step
  where
    g-step : ∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
             g (l ◂ p) ≡ stepᶜ F (g l) p
    g-step l p =
      trans (cong g (◂-as-rot l p))
      (trans (g-rot p (X ⊕ l))
      (trans (cong (rotᶜ F p) (g-⊕ X l))
             (cong (λ z → rotᶜ F p (_⊕ᶜ_ F z (g l))) g-one)))
