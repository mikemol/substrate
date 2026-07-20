------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism
--
-- ◆AI-3-pkg-twisted-lehmer — the twisted route to signF-as-morphism, over the
-- UN-Σ graded LehmerPath tower (NOT the Σ-typed divᴸ).
--
-- BACKGROUND. The untwisted attempt (signF : Perm n → F₂ as a
-- GradedDivStrMorphism out of tower-graded) is BOUNDED OUT: respects-recon needs
-- the digit-contribution parityLess p (map (punchIn p) σ), which FOLDS OVER the
-- base σ, while the interface's map-R sees only the digit. signF is a base-
-- TWISTED cocycle; the twist is the orientation-residue axis-swap (the reorder
-- cost of the insertion).
--
-- THE TWISTED ROUTE. LehmerPath : ℕ → Set (un-Σ, ≅ graded Sₙ) internalises the
-- reorder into its digit: _◂_ : LehmerPath k → Fin (suc k) → LehmerPath (suc k)
-- is a graded recon, and decode (l ◂ p) = insert-at p (decode l). So:
--
--   (1) lehmer-graded : GradedDivStr LehmerPath (λ n → Fin (suc n)) EXISTS
--       (recon = _◂_) — the Lehmer tower as a graded div-structure.
--   (2) decode IS a GradedDivStrMorphism lehmer-graded → tower-graded, with
--       map-C = decode, map-R = id, respects-recon = refl (decode's defining
--       equation). This is the CLEAN, PROVEN core: the reorder-history tower
--       maps to the permutation tower by a graded morphism.
--
-- The twist is now INTERNAL to the Lehmer digit: on a Lehmer path the insertion
-- parity is a function of the digit p ALONE (the factoradic digit = the
-- inversion count), where on the raw Perm carrier it was base-dependent. This is
-- exactly why the twisted route succeeds where the untwisted failed — the twist
-- became the coordinate.
--
-- THE OBLIGATION — NOW DISCHARGED (◆tighten-insertion-parity, 2026-07-19). The
-- FULL twisted sign-morphism needs the general law
--     signF (decode (l ◂ p)) ≡ finParity p + signF (decode l)
-- (the factoradic-digit ↔ inversion-count-parity fact). It is PROVEN
-- unconditionally in Substrate.WitnessTower.InsertionParity (Route B
-- insertion-parity-B / Route A insertion-parity-A), and the discharge is a
-- CHECKABLE TERM in Substrate.WitnessTower.LehmerTowerMorphismDischarged
-- (obligation-discharged : this-parameter's-type = insertion-parity-B;
-- twisted-lehmer-sign-morphism : the unconditional morphism). The
-- `insertion-parity` parameter below is KEPT as the reusable interface (the
-- conditional construction); InsertionParity supplies the witness. (No import
-- here — that would cycle; the tie lives in the downstream Discharged module.)
--
-- --safe --without-K, no Σ / Set₁. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)
open import Substrate.Algebra.Wedge.Graded.Morphism using (GradedDivStrMorphism)

------------------------------------------------------------------------
-- (1) the Lehmer tower as a graded div-structure. recon = _◂_ (append a digit).
------------------------------------------------------------------------

lehmer-graded : GradedDivStr LehmerPath (λ n → Fin (suc n))
lehmer-graded = record { recon = λ n l p → l ◂ p }

------------------------------------------------------------------------
-- (2) THE PROVEN CORE: decode is a graded morphism lehmer-graded → tower-graded.
-- map-C = decode, map-R = id, respects-recon = refl (decode (l ◂ p) = insert-at
-- p (decode l) definitionally). The reorder-history tower maps to the perm
-- tower by a graded morphism, no twist needed at THIS level — the recon shapes
-- match on the nose.
------------------------------------------------------------------------

decode-morphism : GradedDivStrMorphism lehmer-graded tower-graded
decode-morphism = record
  { map-C          = decode
  ; map-R          = λ p → p
  ; respects-recon = λ n l p → refl
  }

------------------------------------------------------------------------
-- the digit parity (the factoradic digit's contribution to the sign).
------------------------------------------------------------------------

finParity : {n : ℕ} → Fin n → F₂
finParity zero          = 𝟘
finParity (suc zero)    = 𝟙
finParity (suc (suc p)) = finParity p

------------------------------------------------------------------------
-- the F₂ target: grade-additive recon (r + b), the sign cocycle's home.
------------------------------------------------------------------------

F₂-target : GradedDivStr (λ _ → F₂) (λ _ → F₂)
F₂-target = record { recon = λ n b r → r + b }

------------------------------------------------------------------------
-- CONCRETE COCYCLE WITNESSES (the general law holds definitionally on paths).
-- signF (decode (l ◂ p)) ≡ finParity p + signF (decode l) — verified for a
-- grade-2 path across all three insertion digits. Not vacuous.
------------------------------------------------------------------------

private
  l₂ : LehmerPath 2
  l₂ = start ◂ zero ◂ suc zero

  witness-0 : signF (decode (l₂ ◂ zero)) ≡ (finParity {3} zero + signF (decode l₂))
  witness-0 = refl

  witness-1 : signF (decode (l₂ ◂ suc zero)) ≡ (finParity {3} (suc zero) + signF (decode l₂))
  witness-1 = refl

  witness-2 : signF (decode (l₂ ◂ suc (suc zero))) ≡ (finParity {3} (suc (suc zero)) + signF (decode l₂))
  witness-2 = refl

------------------------------------------------------------------------
-- (3) THE FULL TWISTED SIGN-MORPHISM, conditional on the one open lemma. Given
-- the insertion-parity law (insertion-inversion-parity = digit parity on
-- decoded perms), signF ∘ decode is a GradedDivStrMorphism lehmer-graded →
-- F₂-target. The lemma is a module parameter — the obligation isolated, the
-- construction otherwise complete. (The witnesses above show the parameter is
-- satisfiable; a general proof needs the factoradic-digit ↔ inversion-count-
-- parity fact, the single open obligation of ◆AI-3-pkg-twisted-lehmer.)
------------------------------------------------------------------------

module _
  (insertion-parity :
    {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
    signF (decode (l ◂ p)) ≡ (finParity p + signF (decode l)))
  where

  sign-lehmer-morphism : GradedDivStrMorphism lehmer-graded F₂-target
  sign-lehmer-morphism = record
    { map-C          = λ l → signF (decode l)
    ; map-R          = finParity
    ; respects-recon = λ n l p → insertion-parity l p
    }
