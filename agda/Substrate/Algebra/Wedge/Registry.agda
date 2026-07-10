------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Registry
--
-- THE FOUNDATIONAL QUOTIENT ALGEBRA, MADE A REALITY ANCHOR — the Registry
-- pattern (cf. Category.UniversalProperty.Registry) for the wedge sphere.
-- Compilation IS certification; no list can be padded. Three layers, each
-- forced by typing:
--
--   * objects   — the wedge-FOUNDED roots (each a genuine `DivStr`): ℕ, F₂,
--                 ℤ, the free monoid `List A`, the square-zero carrier, and
--                 the monoidal unit ⊤-div.
--   * morphisms — the GROUPOID of `WedgeIso`s. A WedgeIso carries its
--                 round-trip proofs, so only genuine isos register; the
--                 associator/unitors (the monoidal structure maps) register
--                 here as non-identity isos.
--   * bridges   — the CATEGORY of `Bridge`s (structure-respecting homs, not
--                 necessarily invertible): the wedge-CONSTRUCTED cross-root
--                 edges parity (ℕ↠F₂) and inclusion (ℕ↪ℤ). These are the
--                 living geodesics — non-invertible, so they cannot be
--                 registered as morphisms; the distinction is forced by type.
--
-- The whole carries a COHERENT MONOIDAL structure: the tensor `_⊗ᴰ_`, the
-- unit `⊤-div`, the associator/unitors as natural isos, and the pentagon +
-- triangle coherence (Algebra.Wedge.Monoidal). That is the sphere: roots as
-- vertices, isos + bridges as edges, coherence closing it — the foundational
-- quotient algebra everything else rests on.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Registry where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (two-div)
open import Substrate.Algebra.Wedge.Cross using (_⊗ᴰ_)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; id-bridge)
open import Substrate.Algebra.Wedge.Iso using (WedgeIso; iso-id; iso-sym)
open import Substrate.Algebra.Wedge.Monoidal using (⊤-div; assocᴰ; unitᴸ; unitᴿ)
open import Substrate.Algebra.F2.Wedge using (F₂-div)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.List.Wedge using (List-div)
open import Substrate.Algebra.Fin.Wedge using (Cyc-div)
open import Substrate.Algebra.Wedge.ParityBridge using (parity-bridge)
open import Substrate.Algebra.Wedge.InclusionBridge using (include-ℕℤ)
open import Substrate.Algebra.Fin.Wedge.ModBridge using (modn-bridge)

------------------------------------------------------------------------
-- 1. Objects: the wedge-founded roots (vertices of the sphere).
------------------------------------------------------------------------

-- ⟡set1-paydown: an object now PACKAGES its carrier with its DivStr (Σ Set DivStr),
-- since DivStr : Set → Set is a family, not a Set. The collection legitimately stays
-- Set₁ (it enumerates carriers); the generic-not-materialized treatment is future work.
Obj : Set₁
Obj = Σ Set DivStr

objects : List Obj
objects = (_ , ℕ-div)      -- the Euclidean carrier (continued fractions)
        ∷ (_ , F₂-div)     -- the field F₂ (parity = mod 2)
        ∷ (_ , Cyc-div 2)  -- the cyclic quotient Z/3 (general-n parity, mod n)
        ∷ (_ , ℤ-div)      -- the integers (signed Bézout's operand)
        ∷ (_ , List-div ⊤) -- the free monoid (wedge's native carrier)
        ∷ (_ , two-div)    -- the square-zero / infinitesimal carrier
        ∷ (_ , ⊤-div)      -- the monoidal unit
        ∷ []

------------------------------------------------------------------------
-- 2. Morphisms: the GROUPOID of WedgeIsos (round-trips forced). The
--    associator/unitors register as genuine non-identity isos.
------------------------------------------------------------------------

Morphism : Set₁
Morphism = Σ Set (λ CA → Σ (DivStr CA) (λ A → Σ Set (λ CB → Σ (DivStr CB) (λ B → WedgeIso A B))))

morphisms : List Morphism
morphisms = (_ , ℕ-div , _ , ℕ-div , iso-id ℕ-div)
          ∷ (_ , F₂-div , _ , F₂-div , iso-id F₂-div)
          -- the left unitor: ⊤ ⊗ ℕ ≃ ℕ  (a structure map, non-identity)
          ∷ (_ , ⊤-div ⊗ᴰ ℕ-div , _ , ℕ-div , unitᴸ ℕ-div)
          -- the right unitor: F₂ ⊗ ⊤ ≃ F₂
          ∷ (_ , F₂-div ⊗ᴰ ⊤-div , _ , F₂-div , unitᴿ F₂-div)
          -- the associator: (ℕ⊗F₂)⊗ℤ ≃ ℕ⊗(F₂⊗ℤ)
          ∷ (_ , (ℕ-div ⊗ᴰ F₂-div) ⊗ᴰ ℤ-div , _ , ℕ-div ⊗ᴰ (F₂-div ⊗ᴰ ℤ-div)
             , assocᴰ ℕ-div F₂-div ℤ-div)
          ∷ []

------------------------------------------------------------------------
-- 3. Bridges: the CATEGORY of (not-necessarily-invertible) homs — the
--    wedge-constructed cross-root edges. Non-invertible, so they live here
--    and NOT in `morphisms`; the type enforces the distinction.
------------------------------------------------------------------------

BridgeEntry : Set₁
BridgeEntry = Σ Set (λ CA → Σ (DivStr CA) (λ A → Σ Set (λ CB → Σ (DivStr CB) (λ B → Bridge A B))))

bridges : List BridgeEntry
bridges = (_ , ℕ-div , _ , F₂-div , parity-bridge)        -- parity (mod 2): ℕ ↠ F₂
        ∷ (_ , ℕ-div , _ , Cyc-div 2 , modn-bridge 2)     -- mod 3: ℕ ↠ Z/3 (general-n)
        ∷ (_ , ℕ-div , _ , ℤ-div , include-ℕℤ)            -- inclusion: ℕ ↪ ℤ
        ∷ []

------------------------------------------------------------------------
-- 4. The category/groupoid laws, as registry facts (forced by typing).
------------------------------------------------------------------------

-- every object has its identity correspondence (reflexivity).
id-of : {C : Set} (D : DivStr C) → Morphism
id-of D = _ , D , _ , D , iso-id D

-- the groupoid is closed under inversion: every iso's inverse is an iso.
inverse-of : Morphism → Morphism
inverse-of (_ , A , _ , B , c) = _ , B , _ , A , iso-sym c

-- every iso is, in particular, a bridge — the groupoid embeds in the category.
forget-iso : Morphism → BridgeEntry
forget-iso (_ , A , _ , B , c) = _ , A , _ , B , WedgeIso.fwd c
