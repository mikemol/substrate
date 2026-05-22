------------------------------------------------------------------------
-- Substrate.Geometry.HodgeDim3
--
-- N-5 (capstone) of M-11.dim3. The Hodge-complement identification
-- in F₂³: the V₄-plane (2-dim subspace `⟨e₁, e₂⟩`) and the chirality-
-- axis (1-dim subspace `⟨e₃⟩`) are *orthogonal* under the standard
-- bilinear form, and together span F₂³ as a direct sum.
--
-- This is the FIRST concrete proof in Agda of the chirality-as-Hodge-
-- dual unification (per memory `project_3plus1_parity_universal`), at
-- the smallest non-degenerate scale n=3.
--
-- Connections (documented; not formally proven here):
--
--   * **To M-9 Fano**: the V₄-plane IS the Fano line `line-1-2-3`
--     (collinearity of p₁, p₂, p₃ = e₁, e₂, e₁+e₂ sums to 𝟎ⱽ
--     precisely because they span the V₄-subspace). The chirality-
--     axis vector e₃ IS Fano point `p₄`. So the specific
--     V₄-line ↔ e₃-point pairing here is the prototype of the
--     full Fano line-point duality (deferred to M-11.fano).
--
--   * **To M-12 N-5 OrbitKey**: OrbitKey ↪ F₂³ as the 6 nonzero
--     vectors NOT on the chirality-axis, i.e., as
--     V4-Nonzero × Chirality. The "missing 2" sections from F₂³'s 8
--     = ⟨e₃⟩ (= chirality-axis here). M-12's `OrbitKey ↔
--     V4-Nonzero × F₂` is consistent with this Fano embedding.
--
--   * **To M-12 N-4 Chirality**: the chirality-axis is iso to F₂ via
--     the obvious bridge (the 1-dim subspace has 2 elements, ≅ F₂).
--     This is the structural justification for M-12 N-4's
--     `Chirality ↔ F₂` bijection: at n=3, the canonical chirality F₂
--     IS the Hodge-dual subspace.
--
-- Lifts (separate slices):
--
--   * **M-11.dim5**: same record at n=5, where the 2-dim V₄-coords
--     plane `⟨e₃, e₄⟩` is Hodge-complementary to the 3-dim subspace
--     `⟨e₀, e₁, e₂⟩` = Axes × Chirality. The Reserved-Selector of
--     M-10A (planned) IS this V₄-projection.
--
--   * **M-11.fano**: generalises to all 7 Fano lines ↔ 7 Fano points.
--
--   * **M-11.dim8**: ext-Hamming parity bit IS chirality at n=8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.HodgeDim3 where

open import Substrate.Foundation.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct
open import Substrate.Algebra.F2.Code
open import Substrate.Geometry.HodgeDim3.V4Plane
  using (V4-Plane; V4-Plane-Pred; pred→kernel)
open import Substrate.Geometry.HodgeDim3.ChiralityAxis
  using (ChiralityAxis; ChiralityAxis-Pred)
  renaming (pred→kernel to chir-pred→kernel)
open import Substrate.Geometry.HodgeDim3.Orthogonality
  using (v4-chir-orthogonal)

-- File-per-lemma child re-exported here so consumers see the
-- HodgeDim3 surface through one import.
open import Substrate.Geometry.HodgeDim3.Fano public

-- File-per-lemma child re-exported here so consumers see the
-- HodgeDim3 surface through one import. Per [[s3-on-v4-file-per-lemma]]
-- the child stays in its own file.
open import Substrate.Geometry.HodgeDim3.Fano public

------------------------------------------------------------------------
-- The capstone record.
------------------------------------------------------------------------

record HodgeComplement-Dim3 : Set where
  field
    v4-plane    : KernelCode 3 1
    chir-axis   : KernelCode 3 2

    orthogonal  : (v w : Vector 3) →
                  In-Kernel v4-plane v →
                  In-Kernel chir-axis w →
                  v ·F w ≡ 𝟘

    decompose   : (u : Vector 3) →
                  Σ (Vector 3) (λ v →
                  Σ (Vector 3) (λ w →
                    In-Kernel v4-plane v
                  × In-Kernel chir-axis w
                  × u ≡ v +ⱽ w))

------------------------------------------------------------------------
-- The concrete instance.
--
-- Decomposition for u = (a ∷ b ∷ c ∷ []):
--   v = (a ∷ b ∷ 𝟘 ∷ [])   in V₄-plane (chirality bit zeroed)
--   w = (𝟘 ∷ 𝟘 ∷ c ∷ [])  in chirality-axis (V₄-coords zeroed)
--   v +ⱽ w = (a+𝟘) ∷ (b+𝟘) ∷ (𝟘+c) ∷ [] ≡ u via F₂ identities.
------------------------------------------------------------------------

hodge-complement-dim3 : HodgeComplement-Dim3
hodge-complement-dim3 = record
  { v4-plane   = V4-Plane
  ; chir-axis  = ChiralityAxis
  ; orthogonal = v4-chir-orthogonal
  ; decompose  = decomp
  }
  where
    decomp : (u : Vector 3) → _
    decomp (a ∷ b ∷ c ∷ []) =
      (a ∷ b ∷ 𝟘 ∷ []) , (𝟘 ∷ 𝟘 ∷ c ∷ []) ,
      pred→kernel (a ∷ b ∷ 𝟘 ∷ []) refl ,
      chir-pred→kernel (𝟘 ∷ 𝟘 ∷ c ∷ []) (refl , refl) ,
      sum-eq
      where
        -- Goal: a ∷ b ∷ c ∷ [] ≡ (a + 𝟘) ∷ (b + 𝟘) ∷ (𝟘 + c) ∷ []
        -- Note: 𝟘 + c reduces to c definitionally; only a, b need lifting.
        sum-eq : (a ∷ b ∷ c ∷ []) ≡
                 ((a ∷ b ∷ 𝟘 ∷ []) +ⱽ (𝟘 ∷ 𝟘 ∷ c ∷ []))
        sum-eq = trans (cong (λ k → k ∷ b ∷ c ∷ []) (sym (+-identityʳ a)))
                       (cong (λ k → (a + 𝟘) ∷ k ∷ c ∷ []) (sym (+-identityʳ b)))
