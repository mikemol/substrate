{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderBraidRealigned — ⟡tower-realign-braid: the
-- TWO ad-hoc braiding modules (FUSepQConfluence, FUSepQHexagon) collapse to
-- INSTANCES of ONE center: Wedge.Monoidal (the symmetric-monoidal braiding).
--
-- Rosetta (ADD 123):
--   FUSepQConfluence.braided-diamond / σ / σ-self-inverse / packed  →  Wedge.Monoidal.braidᴰ / braid-involutive
--   FUSepQHexagon.braid-nat / hexagon / functorial-diamond          →  Wedge.Monoidal.hexagon / assoc-nat
--
-- The two modules re-derived the WedgeIso braiding (all refl on the product
-- carrier by Σ-η). The SPPF confluence "two indexes categorically braided" IS
-- the monoidal braiding σ : A⊗B ≅ B⊗A; the diamonds tiling coherently IS the
-- hexagon; the naturality (diamond commutes with further rewriting) IS assoc-nat.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderBraidRealigned where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Cross using (_⊗ᴰ_)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; id-bridge)
open import Substrate.Algebra.Wedge.Correspondence using (_⊚_)
open import Substrate.Algebra.Wedge.Iso using (WedgeIso)
open import Substrate.Algebra.Wedge.Monoidal
  using (_⊗ᵇ_; braid→; braidᴰ; braid-involutive; hexagon; assoc→; assoc-nat)

------------------------------------------------------------------------
-- ① FUSepQConfluence.σ / braided-diamond / σ-self-inverse IS the monoidal
-- braiding. My "two SPPF indexes categorically braided" (one peel, one reduce)
-- is σ : A⊗B ≅ B⊗A = braidᴰ; my "σ∘σ ≡ id" (self-inverse, the twist's two
-- directions cancel) is braid-involutive. One-line corollaries:
------------------------------------------------------------------------
σ : {CA CB : Set} (A : DivStr CA) (B : DivStr CB) → WedgeIso (A ⊗ᴰ B) (B ⊗ᴰ A)
σ = braidᴰ                          -- the braided diamond IS the monoidal braiding

σ-self-inverse : {CA CB : Set} (A : DivStr CA) (B : DivStr CB) (x : CA × CB)
               → translate (braid→ B A ⊚ braid→ A B) x ≡ x
σ-self-inverse = braid-involutive   -- my σ∘σ≡id IS braid-involutive

------------------------------------------------------------------------
-- ② FUSepQHexagon.hexagon / functorial-diamond IS the monoidal hexagon +
-- naturality. My "3-way Yang-Baxter (the diamonds tile)" is the hexagon; my
-- "functorial-diamond (naturality: the diamond commutes with further rewriting)"
-- is assoc-nat. One-line corollaries:
------------------------------------------------------------------------
hex : {CA CB CC : Set} (A : DivStr CA) (B : DivStr CB) (C : DivStr CC) (x : (CA × CB) × CC)
    → translate (assoc→ B C A ⊚ (braid→ A (B ⊗ᴰ C) ⊚ assoc→ A B C)) x
    ≡ translate ((id-bridge B ⊗ᵇ braid→ A C)
                 ⊚ (assoc→ B A C ⊚ (braid→ A B ⊗ᵇ id-bridge C))) x
hex = hexagon                        -- my 3-way Yang-Baxter IS the hexagon

functorial-diamond : {CA CA′ CB CB′ CC CC′ : Set}
    {A : DivStr CA} {A′ : DivStr CA′} {B : DivStr CB} {B′ : DivStr CB′} {C : DivStr CC} {C′ : DivStr CC′}
    (f : Bridge A A′) (g : Bridge B B′) (h : Bridge C C′)
    (x : (CA × CB) × CC)
    → translate (assoc→ A′ B′ C′ ⊚ ((f ⊗ᵇ g) ⊗ᵇ h)) x
    ≡ translate ((f ⊗ᵇ (g ⊗ᵇ h)) ⊚ assoc→ A B C) x
functorial-diamond = assoc-nat       -- my naturality IS assoc-nat (associator square)

------------------------------------------------------------------------
-- THE COLLAPSE: the SPPF-confluence braiding (FUSepQConfluence ADD 107) +
-- coherent tiling (FUSepQHexagon ADD 108) IS Wedge.Monoidal's symmetric-monoidal
-- structure. σ = braidᴰ, σ-self-inverse = braid-involutive, hexagon = hexagon,
-- functorial-diamond = assoc-nat. Two ad-hoc modules → one named center, all refl.
------------------------------------------------------------------------
