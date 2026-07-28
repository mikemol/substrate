------------------------------------------------------------------------
-- Substrate.WitnessTower.SnAbCharacterBridge
--
-- ◆ip-cap-concrete-bridge (b) + ⟡cap-parity-coapex — the "show-equality"
-- character coincidence: the two Z/2's that the abelianization arc produces
-- are the SAME map.
--
-- Route C (the PRESENTED Sₙ^ab ≅ Z/2, SnAbelianizationZ2) computes its
-- character as `quotient = foldW z2-monoid (λ _ → 𝟙)` = word-length parity.
-- The α-spine (SignGrade2Generated) computes the sign parity of a Coxeter
-- derivation via `signW`, and `signW-flatten` already ties it to the
-- flattened word's count-parity `wpar`. This module closes the last link:
--
--   χ-coincidence :  bool→F₂ (signW g)  ≡  quotient n (flatten g)
--
-- i.e. Route-C's presented character, pulled back along the flatten
-- surjection CoxGen ↠ Word, IS the sign. Both routes' Z/2 = the sign =
-- word-length parity — exhibited as ONE map on `Word (Fin (suc n))`.
--
-- It collapses to two steps over PROVEN pieces:
--   Step A = signW-flatten g       (SignGrade2Generated; carries the whole
--                                    xor ↔ + / count-parity content)
--   Step B = quotient-is-wpar      (the ONE new lemma below: quotient IS
--                                    wpar, pointwise-definitional)
--
-- ⟡cap-parity-coapex = the generic `foldW-const-𝟙` at an arbitrary
-- generator alphabet {Gen}; `quotient-is-wpar` is its specialization at
-- Gen = Fin (suc n). Both are the same 2-clause induction: 𝟘 ≡ parity 0
-- at [], and `cong (𝟙 +_)` at the cons (z2-monoid's ∙ = F₂ + = parity's +,
-- and parity (suc n) = 𝟙 + parity n — so NO parity-+ / bool→F₂-xor glue is
-- needed; signW-flatten already did that work).
--
-- HONEST BOUNDARY: this needs only the flatten SURJECTION direction (a
-- proven term), NOT the presented-monoid ≅ Perm n completeness (Matsumoto,
-- genuinely absent). It shows the two CHARACTERS agree; it does NOT show
-- the two Z/2's are the same OBJECT.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnAbCharacterBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Algebra.F2 using (F₂; 𝟙; _+_)
open import Substrate.Algebra.F2.FromBool using (bool→F₂)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid using (foldW)
open import Substrate.Category.PresentedUniversalProperty.SnAbelianizationZ2
  using (z2-monoid; quotient)
open import Substrate.Algebra.ParityKernel.Universal using (wpar)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral using (CoxGen)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (signW)
open import Substrate.WitnessTower.SignGrade2Generated using (flatten; signW-flatten)

------------------------------------------------------------------------
-- 1. ⟡cap-parity-coapex — the generic co-apex: the Route-C fold-into-F₂
--    (every generator ↦ 𝟙) over ANY alphabet IS the count-parity `wpar`.
--    z2-monoid is n-independent, so it is taken at grade `zero`.
------------------------------------------------------------------------

foldW-const-𝟙 : {Gen : Set} (w : Word Gen) →
                foldW Gen (z2-monoid zero) (λ _ → 𝟙) w ≡ wpar w
foldW-const-𝟙 []      = refl
foldW-const-𝟙 (g ∷ w) = cong (𝟙 +_) (foldW-const-𝟙 w)

------------------------------------------------------------------------
-- 2. Step B — `quotient IS wpar` at Gen = Fin (suc n): the bridge's own
--    specialization (same 2-clause induction, at the presentation's grade).
------------------------------------------------------------------------

quotient-is-wpar : {n : ℕ} (w : Word (Fin (suc n))) → quotient n w ≡ wpar w
quotient-is-wpar []      = refl
quotient-is-wpar (a ∷ w) = cong (𝟙 +_) (quotient-is-wpar w)

------------------------------------------------------------------------
-- 3. ◆ip-cap-concrete-bridge (b) — THE character coincidence.
--    Route-C's presented character (quotient ∘ flatten) = the α-spine's
--    Bool sign, as ONE F₂-valued map on the flattened Coxeter derivation.
------------------------------------------------------------------------

χ-coincidence : {n : ℕ} {τ : Perm (suc n)} (g : CoxGen τ) →
                bool→F₂ (signW g) ≡ quotient n (flatten g)
χ-coincidence g = trans (signW-flatten g) (sym (quotient-is-wpar (flatten g)))
