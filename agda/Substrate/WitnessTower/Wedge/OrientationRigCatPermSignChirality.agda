------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
--
-- ⟡sign-det-bridge — the permutation sign `sign : Perm n → Bool`
-- (OrientationRigCatPermSign) is the FIFTH GUISE of the one ℤ/2 that
-- Substrate.Algebra.R.Trace.ChiralityBridge already unifies.
--
-- HONEST FRAMING — the "det" of THIS module is NOT the permutation
-- determinant. ChiralityBridge's `det-sign` is the CONTINUED-FRACTION
-- convergent determinant sign ((−1)ⁿ per Euclidean step); the genuine bridge
-- here is by the SHARED CARRIER (sign σ = parity of the inversion count = the
-- CF-det chirality), not by a permutation determinant.
--
-- ⚑ UPDATED (⟡leibniz-det-of-perm-matrix). An earlier note here said
-- `det(P_σ) = sign(σ)` is "a NAME-COINCIDENCE… the substrate has NO permutation
-- matrix and NO Leibniz determinant… We do NOT build a fake permutation
-- determinant." That premise is now false, and NOT by a fake: the Leibniz
-- determinant is a genuine term (`WitnessTower.LeibnizDet.det`, the signed sum
-- of Leibniz monomials, ⟡leibniz-det-sum), `WitnessTower.PermMatrixDet.Pmat` is
-- a permutation matrix, and `det (P σ) ≡ sign σ` is VERIFIED there at n = 2, 3
-- by refl. So it is no longer a coincidence — it is a checked identity whose
-- ∀-n proof is now BUILT: `WitnessTower.LeibnizDetPerm.DetPerm.det-P`
-- (⟡leibniz-det-perm-general), plus the tower ◂-step `det-P-◂` exhibiting
-- det∘P∘decode as a parity character over the ordering tower. This module's own
-- bridge (guise 5, the shared-carrier parity) is unchanged.
--
-- The GENUINE bridge is by the SHARED CARRIER (a cross-domain bridge, NOT
-- a collapse): the permutation `sign σ` is the PARITY OF THE INVERSION
-- COUNT of σ's image vector, and `parity : ℕ → F₂` is exactly the ℤ/2 that
-- ChiralityBridge unifies. Via `Bool ↔ F₂` (`bool→F₂`), sign-in-F₂ IS the
-- CF-determinant chirality of the inversion count. So the FIVE GUISES of
-- the one ℤ/2 are:
--
--     1. V4-chirality           (V4Signature.Chirality, even/odd)
--     2. ε-parity / boundary-degree mod 2   (N-to-F2-Parity.parity)
--     3. CF-det-sign            (ChiralityBridge.det-sign, (−1)ⁿ per step)
--     4. parity : ℕ → F₂        (the arithmetic backbone all share)
--     5. permutation sign       (this module: bool→F₂ ∘ sign = parity ∘ invCount)
--
-- The chain of identities (all zero-postulate, GREEN, --safe --without-K):
--   parityLess-count : bool→F₂ (parityLess x xs) ≡ parity (countLess x xs)
--   sign-as-parity   : bool→F₂ (sign v)          ≡ parity (invCount v)
--   sign-is-chirality: bool→F₂ (sign σ)          ≡ det-sign (invCount σ)   [FIFTH GUISE]
--
-- This module declares NO data/record (pure proof side): it freely imports
-- the proof-carrying sign homomorphism and the ChiralityBridge. It carries
-- --guardedness only because ChiralityBridge (transitively) is compiled with
-- it (infective option); it still adds ZERO postulates and ZERO holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _xor_; boolToℕ)  -- ⟡A4: single source

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙) renaming (_+_ to _+F_)
open import Substrate.Algebra.F2.FromBool using (bool→F₂; bool→F₂-xor)
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Algebra.R.Trace.ChiralityBridge using (det-sign; det-sign-is-parity)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (sign; parityLess; finLt; sign-hom)

------------------------------------------------------------------------
-- 0. Bool → F₂ is a homomorphism xor → +F, and factors through parity.
------------------------------------------------------------------------

-- boolToℕ (1 for true, 0 for false) is imported from Foundation.Bool.Properties (single source, ⟡A4).

-- bool→F₂-xor (xor → +F) is the FOUNDATIONAL op-homomorphism, imported from Algebra.F2.FromBool
-- (single source — it sits beside bool→F₂-and and the ∨-as-xor-recon apex there). This module ADDS
-- the group-action context on top: the sign character = parity of the inversion count (below). That
-- is the WitnessTower↔Algebra relationship — group actions thread THROUGH the algebra, not around it.

-- a Bool in F₂ is the parity of its ℕ contribution.
bool→F₂-parity : (b : Bool) → bool→F₂ b ≡ parity (boolToℕ b)
bool→F₂-parity true  = refl
bool→F₂-parity false = refl

------------------------------------------------------------------------
-- 1. countLess / invCount — the ℕ inversion count matching parityLess/sign.
--    `countLess x xs` = number of tail entries strictly below x; it is the
--    ℕ count whose Bool-parity is exactly `parityLess x xs`. `invCount`
--    sums these along the vector, matching `sign`'s xor-fold.
------------------------------------------------------------------------

countLess : {m n : ℕ} → Fin m → Vec (Fin m) n → ℕ
countLess x []       = 0
countLess x (y ∷ ys) = boolToℕ (finLt y x) + countLess x ys

invCount : {m n : ℕ} → Vec (Fin m) n → ℕ
invCount []       = 0
invCount (x ∷ xs) = countLess x xs + invCount xs

------------------------------------------------------------------------
-- 2. The per-element bridge: parityLess IS the Bool-parity of countLess.
------------------------------------------------------------------------

parityLess-count : {m n : ℕ} (x : Fin m) (xs : Vec (Fin m) n) →
                   bool→F₂ (parityLess x xs) ≡ parity (countLess x xs)
parityLess-count x []       = refl
parityLess-count x (y ∷ ys) =
  trans (bool→F₂-xor (finLt y x) (parityLess x ys))
    (trans (cong₂ _+F_ (bool→F₂-parity (finLt y x)) (parityLess-count x ys))
           (sym (parity-+ (boolToℕ (finLt y x)) (countLess x ys))))

------------------------------------------------------------------------
-- 3. THE KEY LEMMA: the permutation sign, in F₂, IS the parity of the
--    inversion count.  bool→F₂ ∘ sign = parity ∘ invCount.
------------------------------------------------------------------------

sign-as-parity : {m n : ℕ} (v : Vec (Fin m) n) →
                 bool→F₂ (sign v) ≡ parity (invCount v)
sign-as-parity []       = refl
sign-as-parity (x ∷ xs) =
  trans (bool→F₂-xor (parityLess x xs) (sign xs))
    (trans (cong₂ _+F_ (parityLess-count x xs) (sign-as-parity xs))
           (sym (parity-+ (countLess x xs) (invCount xs))))

------------------------------------------------------------------------
-- 4. THE FIFTH-GUISE STATEMENT: the permutation sign in F₂ IS the
--    CF-determinant chirality (ChiralityBridge.det-sign) of its inversion
--    count — the same ℤ/2 as V4-chirality / ε-parity / boundary-degree.
--    Route: sign-as-parity, then ChiralityBridge BRIDGE-1 det-sign ≡ parity.
------------------------------------------------------------------------

sign-is-chirality : {n : ℕ} (σ : Perm n) →
                    bool→F₂ (sign σ) ≡ det-sign (invCount σ)
sign-is-chirality σ =
  trans (sign-as-parity σ) (sym (det-sign-is-parity (invCount σ)))

------------------------------------------------------------------------
-- 5. BONUS: the fifth guise is a ℤ/2-homomorphism on Sₙ — the proven
--    Bool multiplicativity `sign-hom` transported through bool→F₂ (its
--    xor becomes the F₂ sum), for genuine permutations σ, τ.
------------------------------------------------------------------------

sign-hom-F₂ : {n : ℕ} (σ τ : Perm n) → IsPerm σ → IsPerm τ →
              bool→F₂ (sign (compose σ τ)) ≡ bool→F₂ (sign σ) +F bool→F₂ (sign τ)
sign-hom-F₂ σ τ pfσ pfτ =
  trans (cong bool→F₂ (sign-hom σ τ pfσ pfτ))
        (bool→F₂-xor (sign σ) (sign τ))
