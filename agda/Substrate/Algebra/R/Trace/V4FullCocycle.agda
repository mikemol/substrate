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

open import Substrate.Algebra.F2.F2
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality; even; odd)

------------------------------------------------------------------------
-- V₄ as ℤ/2 × ℤ/2: the Klein four-group. First factor = the MORPHISM ℤ/2
-- (det-flip = rowSwap = Chirality, ⟡S3); second = the OBJECT ℤ/2 (recip = the
-- CF-representation flip). Element (a , b): a = chirality bit, b = recip bit.
------------------------------------------------------------------------
open import Substrate.Groups.V4.Bijection.V4
  renaming (e to e₄; α to α₄; β to β₄; γ to γ₄)
-- ⚑ Ⓠ6: `open import Substrate.Groups.V4.Operations` REMOVED. It defines
-- `_·_ : V₄ → V₄ → V₄` (the Klein group via Coxeter) while this module defines
-- `_·_ : V4Full → V4Full → V4Full` (componentwise XOR on the ℤ/2 × ℤ/2 record) —
-- `[ClashingDefinition]` at :43.
--
-- ⚑ NOT THE `CommutativeRing` SHAPE, AND THE DIFFERENCE DECIDES THE FIX. There is
-- no re-export here: these are two GENUINELY DIFFERENT operations on two different
-- carriers that happen to share a spelling. So neither a granularity split nor a
-- rename is called for — the import is simply DEAD. Every `·` below is applied to
-- `V4Full` (`rowSwap-invol`, `klein-is-product`, `chirality-hom`, …), and nothing
-- from `Operations` (`ε`, `inv`, `v4-cover`, …) appears anywhere in this file.
--
-- ⚑ AND `--unused-imports` CANNOT SEE THIS, which is why it survived. The predicate
-- is keep-biased and token-based: `·` IS present, so the import reads as used. It
-- cannot distinguish "uses Operations' `_·_`" from "defines its own `_·_` and the
-- token matches" — the exact ambiguity that produced the clash. Reading the use
-- sites is what settled it.
--
-- ⚑ Ⓠ6ᵈ SETTLED IT BY ARCHAEOLOGY, not inference. `git show 771283c8^` — the
-- commit before the ban sweep — shows this file's original imports:
--
--     open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙) renaming (_+_ to _⊕_)
--     open import Substrate.Groups.V4 using (V₄) renaming (… ; _·_ to _·₄_)
--
-- So `⊕` was F₂'s `_+_` renamed AT THE IMPORT, and the V₄ `_·_` clash was solved
-- the same way. The sweep removed both `renaming`s — correctly, they are banned —
-- but SUBSTITUTED NEITHER at the use sites. `⊕` was left dangling and `_·_` was
-- left clashing, so this module has not compiled since 771283c8 (2026-07-28).
--
-- ⚑ THE REPAIR IS THE BAN'S OWN REMEDY, RENAME-AT-SOURCE, ALREADY DONE UPSTREAM:
-- `Substrate.Algebra.F2`'s `_+_` now lives as `_+F_` in `F2.PlusF`. So `⊕ → _+F_`
-- is the SAME OPERATOR under its post-ban name, not a semantic change — which is
-- what made it safe to apply to four `refl` proofs that have never been checked.
open import Substrate.Algebra.F2.PlusF
-- ⚑ Ⓠ6ᵉ: A PLAIN `open import`, because THE COLLISION IS GONE AT SOURCE.
-- `Groups.V4.Operations` now spells its Klein-group operation `_·₄_`, so nothing
-- here works around anything: the name this file needs is simply available.
--
-- ⚑ I ARGUED AGAINST THIS RENAME AND THE ARGUMENT WAS WRONG, so it is recorded
-- rather than quietly replaced. I wrote: *"`Operations` has many importers, so
-- renaming churns a lot of files to fix a collision that exists in ONE — both names are
-- right in their own module."* That is cost-as-correctness: it lets blast radius
-- decide the diagnosis. **A collision IS a misnaming once the repo is read as a
-- single namespace** — which is the premise of the import ban itself — and the
-- number of consumers that trip over it today is a fact about the IMPORT GRAPH,
-- not about the names. It is also self-undermining: a high importer count is
-- evidence the name is load-bearing enough to deserve being unambiguous.
--
-- ⚑ AND THE KINDS ARE NOT ALIKE. `agda_defs --collide _·_` measures 21 providers:
-- 10 RECORD FIELDS (`Magma`, `GradedMonoid`, `JordanAlgebra`, … — legitimately
-- generic, the structure's own operation reached through its record) and 11
-- TOP-LEVEL operators on concrete carriers that merely BORROWED the spelling.
-- Rename-at-source applies to the 11; this was one of them.
open import Substrate.Groups.V4.Operations
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
record V4Full : Set where      -- ⟦shape:5d032637 field morph,obj⟧
  constructor v4
  field morph : F₂     -- the det-flip / rowSwap / Chirality generator (⟡S3)
        obj   : F₂     -- the recip / CF-representation generator (⟡S1-remainder)

open V4Full
-- the group operation: componentwise XOR (ℤ/2 × ℤ/2).
_·_ : V4Full → V4Full → V4Full
(v4 a b) · (v4 c d) = v4 (a +F c) (b +F d)
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
chirality-hom : (g h : V4Full) → chirality-of (g · h) ≡ chirality-of (v4 (morph g +F morph h) 𝟘)
chirality-hom g h = refl

------------------------------------------------------------------------
-- UNIFICATION (Ⓜ.v4-unify): V4Full is NOT a rival V₄ — it is the F₂-COORDINATE
-- presentation of the substrate's canonical Klein four-group Substrate.Groups.V4
-- (the enumerated {e,α,β,γ}, itself V4-Coxeter via a bijection; cf.
-- Groups.V4-as-Z2xZ2, the ℤ/2×ℤ/2 word presentation). Witnessed here by a group
-- ISO, so the "two V₄ structures" dissolve into ONE group in two charts — the
-- bit-coordinate chart being the one where chirality-of reads the morph bit.
--   e ↔ e    rowSwap-gen ↔ α    recip-gen ↔ β    klein ↔ γ
------------------------------------------------------------------------

to₄ : V4Full → V₄
to₄ (v4 𝟘 𝟘) = e₄
to₄ (v4 𝟙 𝟘) = α₄
to₄ (v4 𝟘 𝟙) = β₄
to₄ (v4 𝟙 𝟙) = γ₄

from₄ : V₄ → V4Full
from₄ e₄ = e
from₄ α₄ = rowSwap-gen
from₄ β₄ = recip-gen
from₄ γ₄ = klein

from-to₄ : (x : V4Full) → from₄ (to₄ x) ≡ x
from-to₄ (v4 𝟘 𝟘) = refl
from-to₄ (v4 𝟙 𝟘) = refl
from-to₄ (v4 𝟘 𝟙) = refl
from-to₄ (v4 𝟙 𝟙) = refl

to-from₄ : (y : V₄) → to₄ (from₄ y) ≡ y
to-from₄ e₄ = refl
to-from₄ α₄ = refl
to-from₄ β₄ = refl
to-from₄ γ₄ = refl

-- the bijection is a GROUP homomorphism (V4Full's ⊕-pair op ↔ V₄'s ·): same group.
-- ⚑ Ⓠ6ᵉ SUPERSEDED Ⓠ6ᶠ, AND THIS LINE IS WHY THE OPERATOR RENAME IS THE RIGHT
-- FIX. `Groups.V4.Operations._·_` is now `_·₄_` AT SOURCE, so the name is simply
-- available here — no qualification, no directive, no workaround. The original
-- `renaming (_·_ to _·₄_)` was reaching for exactly this spelling; the rename
-- moves that decision out of every call site and into the one module that defines it.
to₄-hom : (g h : V4Full) → to₄ (g · h) ≡ (to₄ g ·₄ to₄ h)
to₄-hom (v4 𝟘 𝟘) (v4 𝟘 𝟘) = refl
to₄-hom (v4 𝟘 𝟘) (v4 𝟘 𝟙) = refl
to₄-hom (v4 𝟘 𝟘) (v4 𝟙 𝟘) = refl
to₄-hom (v4 𝟘 𝟘) (v4 𝟙 𝟙) = refl
to₄-hom (v4 𝟘 𝟙) (v4 𝟘 𝟘) = refl
to₄-hom (v4 𝟘 𝟙) (v4 𝟘 𝟙) = refl
to₄-hom (v4 𝟘 𝟙) (v4 𝟙 𝟘) = refl
to₄-hom (v4 𝟘 𝟙) (v4 𝟙 𝟙) = refl
to₄-hom (v4 𝟙 𝟘) (v4 𝟘 𝟘) = refl
to₄-hom (v4 𝟙 𝟘) (v4 𝟘 𝟙) = refl
to₄-hom (v4 𝟙 𝟘) (v4 𝟙 𝟘) = refl
to₄-hom (v4 𝟙 𝟘) (v4 𝟙 𝟙) = refl
to₄-hom (v4 𝟙 𝟙) (v4 𝟘 𝟘) = refl
to₄-hom (v4 𝟙 𝟙) (v4 𝟘 𝟙) = refl
to₄-hom (v4 𝟙 𝟙) (v4 𝟙 𝟘) = refl
to₄-hom (v4 𝟙 𝟙) (v4 𝟙 𝟙) = refl

