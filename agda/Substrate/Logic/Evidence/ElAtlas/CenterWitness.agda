------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterWitness  (Ξ★.1 — MECHANIZE-STAR rung 1)
--
-- The --safe Agda witness for the rung-3 layer of the point-cloud / Hodge-★ /
-- witness structure (AI-Π0's POINT_CLOUD_HODGE_FORMALIZATION, the SymPy-exact
-- rung below this one). Rung 3 is "the clearest signature": the complete graph
-- K₄, cycle space ℚ³, carrying the cycle-space antisymmetric (Kirchhoff loop)
-- form B₃. Everything here is over ℤ (the form is integer-valued; ℤ ⊂ ℚ), so
-- every statement reduces by `refl` — it is an exact computation that CAN fail.
--
-- B₃ = ⎡ 0  2  2⎤   (extracted exact from jea_strictify_gcalc.cycle_form_exact(4);
--      ⎢-2  0  2⎥    rank 2, kernel 1-dimensional — odd cyc-dim forces the witness,
--      ⎣-2 -2  0⎦    §3.4. The witness is the kernel direction w = (1,−1,1).)
--
-- Mechanized here (the doc's §3.1/3.4, §5.1, §6.1):
--   * witness-in-kernel  — THE WITNESS IS THE KERNEL: B₃·w ≡ 0.
--   * rep-is-image       — the representable plane IS the image of B₃ (its basis
--                          is B₃ applied to the standard basis).
--   * witness-⟂-rep      — CENTER = WITNESS LINE: w is orthogonal to the
--                          representable image (rep-projection of w vanishes), so
--                          the log-polar centre (|image|→0) is exactly the witness.
--   * self-annihilation  — vᵀB₃v ≡ 0 even for a REPRESENTABLE basis vector e₁
--                          (annihilation is the antisymmetry of B₃, not a kernel
--                          accident, §6.1).
--
-- NOT yet here (later rungs of MECHANIZE-STAR / Ξ★):
--   Ξ★.2  ★ = G_NOT: tie this witness/center to GValueAsQ.G_NOT (the reciprocal
--         /swap involution, the series↔parallel fold) — needs the ℤ↪ℚ bridge.
--   Ξ★.3  the single center-is-★ identity (§7.1): the G→0 open-circuit corner IS
--         the G_NOT-fixed witness locus IS the centre.
--   Also the UNIVERSAL self-annihilation ∀v. vᵀB₃v ≡ 0 (= antisymmetry, the
--         R-strictify content) is a ring-algebra proof, not `refl`; deferred.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterWitness where

open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- Cycle space at rung 3 = ℤ³, with the dot product.
------------------------------------------------------------------------

V3 : Set
V3 = Vec ℤ 3

𝟎 : V3
𝟎 = (+ 0) ∷ (+ 0) ∷ (+ 0) ∷ []

dot : V3 → V3 → ℤ
dot (a ∷ b ∷ c ∷ []) (x ∷ y ∷ z ∷ []) = (a *ℤ x) +ℤ ((b *ℤ y) +ℤ (c *ℤ z))

------------------------------------------------------------------------
-- B₃ : the rung-3 cycle-space antisymmetric form (rows r₀ r₁ r₂), and its
-- action B₃·v (the matrix-vector product, dot against each row).
------------------------------------------------------------------------

r₀ r₁ r₂ : V3
r₀ = (+ 0)      ∷ (+ 2)      ∷ (+ 2) ∷ []
r₁ = (-ℤ (+ 2)) ∷ (+ 0)      ∷ (+ 2) ∷ []
r₂ = (-ℤ (+ 2)) ∷ (-ℤ (+ 2)) ∷ (+ 0) ∷ []

apply-B₃ : V3 → V3
apply-B₃ v = dot r₀ v ∷ dot r₁ v ∷ dot r₂ v ∷ []

------------------------------------------------------------------------
-- The witness (kernel direction), the representable basis, and the
-- standard basis vectors whose B₃-images are the representable basis.
------------------------------------------------------------------------

w : V3                                  -- the witness = kernel of B₃
w = (+ 1) ∷ (-ℤ (+ 1)) ∷ (+ 1) ∷ []

rep₁ rep₂ : V3                          -- the representable (image) plane basis
rep₁ = (+ 0) ∷ (-ℤ (+ 2)) ∷ (-ℤ (+ 2)) ∷ []
rep₂ = (+ 2) ∷ (+ 0)      ∷ (-ℤ (+ 2)) ∷ []

e₁ e₂ : V3                              -- standard basis (representable, not witness)
e₁ = (+ 1) ∷ (+ 0) ∷ (+ 0) ∷ []
e₂ = (+ 0) ∷ (+ 1) ∷ (+ 0) ∷ []

------------------------------------------------------------------------
-- §3.1 / §3.4 — THE WITNESS IS THE KERNEL: B₃·w ≡ 0.
------------------------------------------------------------------------

witness-in-kernel : apply-B₃ w ≡ 𝟎
witness-in-kernel = refl

------------------------------------------------------------------------
-- The representable plane IS the image of B₃: its basis is B₃ applied to the
-- standard basis (rep₁ = B₃·e₁, rep₂ = B₃·e₂).
------------------------------------------------------------------------

rep-is-image : (apply-B₃ e₁ ≡ rep₁) × (apply-B₃ e₂ ≡ rep₂)
rep-is-image = refl , refl

------------------------------------------------------------------------
-- §5.1 — CENTER = WITNESS LINE: w is orthogonal to the representable image
-- (the rep-projection of w vanishes). The log-polar centre, where the
-- representable magnitude → 0, is exactly the witness direction.
------------------------------------------------------------------------

witness-⟂-rep : (dot rep₁ w ≡ + 0) × (dot rep₂ w ≡ + 0)
witness-⟂-rep = refl , refl

------------------------------------------------------------------------
-- §6.1 — SELF-ANNIHILATION IS EVERYWHERE: vᵀB₃v ≡ 0 even for the
-- representable basis vector e₁ (not just the kernel) — the antisymmetry of B₃
-- made concrete (rotation-out, not a special corner event).
------------------------------------------------------------------------

self-annihilation-e₁ : dot e₁ (apply-B₃ e₁) ≡ + 0
self-annihilation-e₁ = refl

self-annihilation-w : dot w (apply-B₃ w) ≡ + 0
self-annihilation-w = refl
