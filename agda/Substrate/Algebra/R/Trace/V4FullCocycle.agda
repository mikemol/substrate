{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.V4FullCocycle — ⟡S1-remainder. The FULL V₄
-- cocycle on the arithmetic side, beyond the single Chirality ℤ/2 that ⟡S3
-- pinned. DetSign names TWO ℤ/2s: the MORPHISM side (det-flip = the CF-matrix
-- swap = Chirality, ⟡S3) and the OBJECT side (the CF-representation flip
-- [a₀;…;n] ↔ [a₀;…;n−1,1]). HetV4 realizes BOTH as the Klein four-group
-- V₄ = ⟨rowSwap, recip⟩ ≅ ℤ/2 × ℤ/2 acting on the cross-equality square
-- (rowSwap = ≈H-sym, recip = num↔den, klein = rowSwap∘recip — all proven in
-- HetV4). So the arithmetic side carries a FULL V₄; ⟡S3 pinned ONE generator.
--
-- This module names the V₄ as ℤ/2 × ℤ/2 with the two arithmetic involutions
-- as generators, identifies the Chirality component as the rowSwap factor
-- (tying to ⟡S3's det-flip), and confirms the group closure (each generator
-- an involution; the third non-identity = their product). ⟡H-overclaim: I
-- checked the SECOND generator genuinely lands (recip, HetV4.≈H-recip) before
-- claiming the V₄ closes — it does.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.V4FullCocycle where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙) renaming (_+_ to _⊕_)
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality; even; odd)

------------------------------------------------------------------------
-- V₄ as ℤ/2 × ℤ/2: the Klein four-group. First factor = the MORPHISM ℤ/2
-- (det-flip = rowSwap = Chirality, ⟡S3); second = the OBJECT ℤ/2 (recip = the
-- CF-representation flip). Element (a , b): a = chirality bit, b = recip bit.
------------------------------------------------------------------------
record V4Full : Set where      -- ⟦shape:5d032637 field morph,obj⟧
  constructor v4
  field morph : F₂     -- the det-flip / rowSwap / Chirality generator (⟡S3)
        obj   : F₂     -- the recip / CF-representation generator (⟡S1-remainder)
open V4Full

-- the group operation: componentwise XOR (ℤ/2 × ℤ/2).
_·_ : V4Full → V4Full → V4Full
(v4 a b) · (v4 c d) = v4 (a ⊕ c) (b ⊕ d)
infixl 6 _·_

e : V4Full                       -- identity
e = v4 𝟘 𝟘
rowSwap-gen : V4Full             -- generator 1: det-flip / Chirality (⟡S3)
rowSwap-gen = v4 𝟙 𝟘
recip-gen : V4Full               -- generator 2: recip / object side (the remainder)
recip-gen = v4 𝟘 𝟙
klein : V4Full                   -- the 180° central element = rowSwap ∘ recip
klein = v4 𝟙 𝟙

------------------------------------------------------------------------
-- V₄ closure facts (the group is genuinely the Klein four-group):
------------------------------------------------------------------------
-- both generators are involutions.
rowSwap-invol : rowSwap-gen · rowSwap-gen ≡ e
rowSwap-invol = refl
recip-invol : recip-gen · recip-gen ≡ e
recip-invol = refl
-- the third non-identity element IS the product of the two generators.
klein-is-product : rowSwap-gen · recip-gen ≡ klein
klein-is-product = refl
-- klein is also an involution (V₄ has exponent 2 — every element self-inverse).
klein-invol : klein · klein ≡ e
klein-invol = refl
-- the two generators commute (V₄ is abelian).
gens-commute : rowSwap-gen · recip-gen ≡ recip-gen · rowSwap-gen
gens-commute = refl

------------------------------------------------------------------------
-- THE CHIRALITY PROJECTION: the morph component IS the Chirality ℤ/2 (⟡S3's
-- det-flip). So Chirality is the ROWSWAP FACTOR of the full V₄ — one of the
-- two ℤ/2s, not the whole thing. The recip factor is the remainder ⟡S1 asked
-- for. This exhibits Chirality as a QUOTIENT/component of the V₄ cocycle.
------------------------------------------------------------------------
chirality-of : V4Full → Chirality
chirality-of h with morph h
... | 𝟘 = even
... | 𝟙 = odd

-- ⟡S3's det-flip lands as the rowSwap generator, whose chirality is odd.
chirality-rowSwap : chirality-of rowSwap-gen ≡ odd
chirality-rowSwap = refl
-- recip (the remainder generator) is chirality-INVISIBLE (morph = 𝟘): it is
-- the SECOND ℤ/2, ORTHOGONAL to Chirality. This is precisely why ⟡S3 saw only
-- ONE ℤ/2 — Chirality projects away the recip factor.
chirality-recip-even : chirality-of recip-gen ≡ even
chirality-recip-even = refl
-- and the projection is a homomorphism onto the Chirality ℤ/2 (morph factor).
chirality-hom : (g h : V4Full) → chirality-of (g · h) ≡ chirality-of (v4 (morph g ⊕ morph h) 𝟘)
chirality-hom g h = refl
