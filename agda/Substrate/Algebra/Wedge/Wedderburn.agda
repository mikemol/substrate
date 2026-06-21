------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Wedderburn  (Ⓦᵤ — the noncommutative corner of the genus)
--
-- The genus Ⓖ★ (Algebra.Wedge.Species) was exhibited over COMMUTATIVE carriers
-- (ℤ/6, the N-complex), where orthogonal idempotents are CENTRAL and the CRT
-- factors don't interfere. Wedderburn–Artin's signature is the NONCOMMUTATIVE
-- case: a semisimple ring is a product of matrix rings Mₙ(D), whose diagonal
-- matrix units eᵢᵢ are orthogonal idempotents that are NOT central — they are
-- glued by the off-diagonal NILPOTENT corners eᵢⱼ (i≠j). Here the smallest such
-- ring, M₂(F₂), realizes BOTH species of the genus in ONE ring, PLUS the
-- noncommutativity the commutative exhibits could not show.
--
--   * IDEMPOTENT species: e₁₁, e₂₂ — orthogonal idempotents (e₁₁·e₂₂ = 0,
--     eᵢᵢ² = eᵢᵢ), complete (e₁₁ + e₂₂ = I). IdempotentSpecies via Ⓖ★.
--   * NILPOTENT species:  e₁₂, e₂₁ — the corners, e₁₂² = 0. NilpotentSpecies via Ⓖ★.
--   * THE CORNER (Peirce): e₁₂ lives in e₁₁·R·e₂₂ (e₁₁·e₁₂·e₂₂ = e₁₂); the corners
--     multiply back to idempotents: e₁₂·e₂₁ = e₁₁, e₂₁·e₁₂ = e₂₂.
--   * NONCOMMUTATIVITY (the Wedderburn witness, invisible in Ⓖ★):
--     e₁₂·e₂₁ = e₁₁ ≠ e₂₂ = e₂₁·e₁₂.
--
-- M₂(F₂) is itself simple (= M₂(D) with D = F₂, a 1×1 Wedderburn block), so it is
-- the irreducible noncommutative atom the theorem decomposes semisimple rings into.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Wedderburn where

open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_; 𝟙≢𝟘)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; base; mul; pow; Nilpotent; Annihilator)
open import Substrate.Algebra.Wedge.Species
  using (Stable; IdempotentSpecies; NilpotentSpecies; species-disjoint)

------------------------------------------------------------------------
-- M₂(F₂) as a MulDivStr. A matrix [[a,b],[c,d]] is the vector a∷b∷c∷d∷[].
------------------------------------------------------------------------

M2 : Set
M2 = Vec F₂ 4

M2-mul : M2 → M2 → M2
M2-mul (a ∷ b ∷ c ∷ d ∷ []) (e ∷ f ∷ g ∷ h ∷ []) =
  (a · e + b · g) ∷ (a · f + b · h) ∷ (c · e + d · g) ∷ (c · f + d · h) ∷ []

M2-add : M2 → M2 → M2
M2-add (a ∷ b ∷ c ∷ d ∷ []) (e ∷ f ∷ g ∷ h ∷ []) = (a + e) ∷ (b + f) ∷ (c + g) ∷ (d + h) ∷ []

𝟎 I e₁₁ e₁₂ e₂₁ e₂₂ : M2
𝟎   = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
I   = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []
e₁₁ = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
e₁₂ = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []
e₂₁ = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []
e₂₂ = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []

M2-div : DivStr
M2-div = record { C = M2 ; z = 𝟎 ; recon = λ _ _ r → r }

M2-mul-str : MulDivStr
M2-mul-str = record { base = M2-div ; mul = M2-mul }

------------------------------------------------------------------------
-- The matrix-unit (Peirce) relations — all by refl over F₂.
------------------------------------------------------------------------

e₁₁-idem : M2-mul e₁₁ e₁₁ ≡ e₁₁
e₁₁-idem = refl
e₂₂-idem : M2-mul e₂₂ e₂₂ ≡ e₂₂
e₂₂-idem = refl

complete : M2-add e₁₁ e₂₂ ≡ I                        -- a complete set of idempotents
complete = refl

e₁₁-e₂₂-ortho : M2-mul e₁₁ e₂₂ ≡ 𝟎                   -- orthogonal idempotents
e₁₁-e₂₂-ortho = refl

e₁₂-nilpotent : M2-mul e₁₂ e₁₂ ≡ 𝟎                   -- the corner squares to 0
e₁₂-nilpotent = refl
e₂₁-nilpotent : M2-mul e₂₁ e₂₁ ≡ 𝟎
e₂₁-nilpotent = refl

corner-12 : M2-mul (M2-mul e₁₁ e₁₂) e₂₂ ≡ e₁₂         -- e₁₂ ∈ e₁₁·R·e₂₂ (the (1,2) corner)
corner-12 = refl

corners-glue-11 : M2-mul e₁₂ e₂₁ ≡ e₁₁               -- corners multiply back to idempotents
corners-glue-11 = refl
corners-glue-22 : M2-mul e₂₁ e₁₂ ≡ e₂₂
corners-glue-22 = refl

------------------------------------------------------------------------
-- THE WEDDERBURN WITNESS: noncommutativity. e₁₂·e₂₁ = e₁₁ ≠ e₂₂ = e₂₁·e₁₂.
-- This is exactly what the commutative genus (Ⓖ★) cannot see.
------------------------------------------------------------------------

head : M2 → F₂
head (x ∷ _) = x

noncommutative : M2-mul e₁₂ e₂₁ ≡ M2-mul e₂₁ e₁₂ → ⊥
noncommutative eq with cong head eq            -- head e₁₁ = 𝟙, head e₂₂ = 𝟘
... | h = 𝟙≢𝟘 h

------------------------------------------------------------------------
-- BOTH species of the genus Ⓖ★, in this ONE noncommutative ring.
------------------------------------------------------------------------

-- idempotent species: (e₁₁, e₂₂) — orthogonal cross (0) + stable diagonal.
m2-idempotent-species : IdempotentSpecies M2-mul-str e₁₁ e₂₂
m2-idempotent-species = (0 , refl) , refl

-- nilpotent species: e₁₂ — cross e₁₂·e₁₂ = 0 (Ortho) + e₁₂ nilpotent (e₁₂² = 0).
m2-nilpotent-species : NilpotentSpecies M2-mul-str e₁₂ e₁₂
m2-nilpotent-species = (0 , refl) , (1 , refl)

-- the two facets are genuinely distinct here too (species-disjoint, the Ⓖ★ apex):
-- e₁₁ is stable but not nilpotent (else it would be 𝟎, but head e₁₁ = 𝟙).
e₁₁-not-nilpotent : Nilpotent M2-mul-str e₁₁ → ⊥
e₁₁-not-nilpotent nil with cong head (species-disjoint M2-mul-str e₁₁ e₁₁-idem nil)
... | h = 𝟙≢𝟘 h

------------------------------------------------------------------------
-- ⊙ conjecture #5: NILPOTENT-NOT-ANNIHILATING ⟹ NO DEAD-END. e₁₂ is a nonzero
-- nilpotent (e₁₂-nilpotent: e₁₂² = 𝟎, a graded degree-2 obstruction), yet it does
-- NOT annihilate: e₁₂·e₂₁ = e₁₁ ≠ 𝟎 (corners-glue-11) — the corner multiplies back
-- to a LIVE idempotent. So the nilpotent residue deforms the product (graded), it
-- never KILLS the structure. "Kill can't happen" — the obstruction is tracked by
-- degree, not a collapse (intuitionistic; ties #1, the wedge correction survives).
------------------------------------------------------------------------

e₁₂-not-annihilating : Annihilator M2-mul-str e₁₂ → ⊥
e₁₂-not-annihilating ann = 𝟙≢𝟘 (cong head (ann e₂₁))
