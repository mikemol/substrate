------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Species  (Ⓖ★ — the genus of the two zero-divisor species)
--
-- THE UNIFYING GENUS under the idempotent species (Ξ★.cⁿ CRT idempotents,
-- Ⓟ.3′/3″ the T²=I reflection) and the nilpotent species (Ξ★.g the degree-3
-- N-complex, Ⓛ★ the local ℤ/pᵉ degree-e). The construct-don't-classify move:
-- not a description "idempotent ∪ nilpotent", but the COMMON STRUCTURE they are
-- both refinements of, parametric over any MulDivStr.
--
-- THE GENUS (`Ortho`): a pair (a,b) whose PRODUCT is nilpotent — the cross term
-- vanishes under powers. This is exactly CrossMul.Coherent's spine (Coherent =
-- Nilpotent of the cross), the shared backbone of both species:
--   * CRT idempotents e₁,e₂ : e₁·e₂ ≡ 0          (cross vanishes at degree 0)
--   * an N-complex (η, η²)  : η·η² = η³ ≡ 0       (cross vanishes at degree d)
--
-- THE TWO SPECIES = the genus refined by the DIAGONAL a·a:
--   * STABLE     a·a ≡ a       — a is idempotent: the unit / disconnection facet
--                                (CRT split, Spec components, the +1/−1 eigen-
--                                projectors of an involution).
--   * VANISHING  Nilpotent a    — aᵈ ≡ 0: the infinitesimal / thickening facet
--                                (nilradical, non-reduced, the graded residue).
--
-- THE WEDGE NON-COLLAPSE (`species-disjoint`): an element that is BOTH stable and
-- vanishing must be the terminal z. So the two species are genuinely distinct
-- facets (they meet only at 0) — a general element carries both (the Fitting /
-- Jordan–Chevalley wedge: semisimple ⊕ nilpotent), never one collapsed onto the
-- other. This is [[feedback_duality_operator_is_either_or_trap]] /
-- [[feedback_cross_carrier_tie_is_crossmix]] made into one parametric statement.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Species where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.Wedge using (DivStr; C; z)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; base; mul; pow; Nilpotent)

------------------------------------------------------------------------
-- The genus: the cross of the pair vanishes under powers (Coherent's spine).
------------------------------------------------------------------------

Ortho : (M : MulDivStr) → C (base M) → C (base M) → Set
Ortho M a b = Nilpotent M (mul M a b)

------------------------------------------------------------------------
-- The diagonal discriminant — the two species.
------------------------------------------------------------------------

-- STABLE: a is idempotent (a² = a) — the idempotent / unit / disconnection facet.
Stable : (M : MulDivStr) → C (base M) → Set
Stable M a = mul M a a ≡ a

-- the two species = the genus Ortho refined by each diagonal.
IdempotentSpecies : (M : MulDivStr) → C (base M) → C (base M) → Set
IdempotentSpecies M a b = Ortho M a b × Stable M a

NilpotentSpecies : (M : MulDivStr) → C (base M) → C (base M) → Set
NilpotentSpecies M a b = Ortho M a b × Nilpotent M a

------------------------------------------------------------------------
-- A stable (idempotent) element is fixed by every power: aⁿ ≡ a.
------------------------------------------------------------------------

stable-pow : (M : MulDivStr) (a : C (base M)) → Stable M a → (n : ℕ) → pow M a n ≡ a
stable-pow M a st zero    = refl                                   -- pow a 0 = a
stable-pow M a st (suc n) = trans (cong (mul M a) (stable-pow M a st n)) st
  --  pow a (suc n) = a · pow a n ≡ a · a (cong, IH) ≡ a (st)

------------------------------------------------------------------------
-- THE WEDGE NON-COLLAPSE: stable ∧ vanishing ⟹ trivial. The two species are
-- distinct facets — they coincide only at the terminal z.
------------------------------------------------------------------------

species-disjoint : (M : MulDivStr) (a : C (base M)) →
                   Stable M a → Nilpotent M a → a ≡ z (base M)
species-disjoint M a st (d , nil) = trans (sym (stable-pow M a st d)) nil
  --  a ≡ pow a d (sym stable-pow) ≡ z (nil)
