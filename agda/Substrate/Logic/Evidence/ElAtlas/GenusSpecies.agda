------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.GenusSpecies  (Ⓖ★ — the genus, exhibited)
--
-- Exhibits the three el-atlas instances of the zero-divisor genus
-- (Algebra.Wedge.Species) as inhabitants of ONE common structure — the
-- construct-don't-classify resolution of "idempotent species ∪ nilpotent
-- species": not a bucket-union, but the SAME genus (`Ortho`: vanishing cross)
-- refined by the diagonal (`Stable` = idempotent vs `Nilpotent` = vanishing).
--
--   * IDEMPOTENT species — Ξ★.cⁿ: the CRT idempotents e₁,e₂ of ℤ/6. Cross
--     e₁·e₂ ≡ 0 (Ortho); diagonal e₁² ≡ e₁ (Stable). Lives purely in the
--     stable facet (e₁-not-nilpotent: it is NOT nilpotent — would force e₁≡0).
--   * NILPOTENT species — Ξ★.g: the N-complex (η, η²) of Three. Cross η·η² = η³
--     ≡ 0 (Ortho); diagonal η nilpotent (η³≡0). Lives purely in the vanishing
--     facet (η-not-stable: it is NOT idempotent).
--   * IDEMPOTENT species at the OPERATOR level — Ⓟ.3″: the involution T (T²=I)
--     of the rung-3 reflection. Its eigen-projectors P± = I ± T are orthogonal,
--     P+ ∘ P− = I − T² ≡ 0 — the vanishing-cross genus realized for T. P+ is
--     the static +1 line (w = ker B₃), P− the dynamic −1 line (d): the Ⓟ.3″
--     static⊕dynamic WEDGE IS this orthogonal-idempotent (CRT-type) split.
--
-- species-disjoint (the apex) certifies these are genuinely two facets: stable
-- ∧ vanishing ⟹ trivial, so no instance collapses onto the other.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.GenusSpecies where

open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_)
open import Substrate.Algebra.Wedge.Mul using (Nilpotent)
open import Substrate.Algebra.Wedge.Species
  using (Ortho; Stable; IdempotentSpecies; NilpotentSpecies; species-disjoint)
open import Substrate.Logic.Evidence.ElAtlas.CenterIsStarCRT
  using (ℤ6-mul; e₁; e₂; e₁-idempotent)
open import Substrate.Algebra.Wedge.NComplex
  using (three-mul; η; sq; η-degree-3)
open import Substrate.Logic.Evidence.ElAtlas.OrbitCloudRung3Wedge
  using (act-T; vsub)

------------------------------------------------------------------------
-- IDEMPOTENT species — Ξ★.cⁿ, the CRT idempotents of ℤ/6.
------------------------------------------------------------------------

-- cross e₁·e₂ ≡ 0 (Ortho, degree 0) ; diagonal e₁²≡e₁ (Stable).
crt-genus : IdempotentSpecies ℤ6-mul e₁ e₂
crt-genus = (0 , refl) , e₁-idempotent

-- it lives PURELY in the stable facet: e₁ is not nilpotent (else species-disjoint
-- forces e₁ ≡ 0, but e₁ = 3).
e₁-not-nilpotent : Nilpotent ℤ6-mul e₁ → ⊥
e₁-not-nilpotent nil with species-disjoint ℤ6-mul e₁ e₁-idempotent nil
... | ()

------------------------------------------------------------------------
-- NILPOTENT species — Ξ★.g, the N-complex (η, η²) of Three.
------------------------------------------------------------------------

-- cross η·η² = η³ ≡ 0 (Ortho, degree 2) ; diagonal η nilpotent.
nilpotent-genus : NilpotentSpecies three-mul η sq
nilpotent-genus = (0 , refl) , η-degree-3

-- it lives PURELY in the vanishing facet: η is not stable (η² = sq ≢ η).
η-not-stable : Stable three-mul η → ⊥
η-not-stable ()

------------------------------------------------------------------------
-- IDEMPOTENT species at the OPERATOR level — Ⓟ.3″, the involution T.
-- The eigen-projectors P± = I ± T are orthogonal: P+ ∘ P− = I − T² ≡ 0
-- (since T² = I). This is the vanishing-cross genus for T — the static (+1, w)
-- and dynamic (−1, d) lines of the Ⓟ.3″ wedge as orthogonal idempotents.
------------------------------------------------------------------------

V3 : Set
V3 = Vec ℤ 3

vadd : V3 → V3 → V3
vadd (a ∷ b ∷ c ∷ []) (x ∷ y ∷ z ∷ []) = (a +ℤ x) ∷ (b +ℤ y) ∷ (c +ℤ z) ∷ []

P- P+ : V3 → V3
P- v = vsub v (act-T v)        -- I − T  (projects onto the −1 / dynamic line, ×2)
P+ v = vadd v (act-T v)        -- I + T  (projects onto the +1 / static line, ×2)

𝟎₃ : V3
𝟎₃ = (+ 0) ∷ (+ 0) ∷ (+ 0) ∷ []

-- P+ ∘ P− ≡ 0 on the standard basis: (I+T)(I−T) = I − T² = 0.
ortho-e₁ : P+ (P- ((+ 1) ∷ (+ 0) ∷ (+ 0) ∷ [])) ≡ 𝟎₃
ortho-e₁ = refl
ortho-e₂ : P+ (P- ((+ 0) ∷ (+ 1) ∷ (+ 0) ∷ [])) ≡ 𝟎₃
ortho-e₂ = refl
ortho-e₃ : P+ (P- ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ [])) ≡ 𝟎₃
ortho-e₃ = refl
