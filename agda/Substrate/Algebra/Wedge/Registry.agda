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
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.Z using (ℤ)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (Two; two-div)
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

-- ⟡set1-paydown (generic-not-materialized, the Lawvere follow-up to the DivStr
-- TorsorAtom form). Packing a carrier `Set` as data (`Σ Set DivStr`) is what forced
-- Set₁; a MATERIALIZED heterogeneous-carrier list has nowhere else to put the carrier.
-- The Tarski route-around: a CODE universe `ObjCode : Set` naming the objects, with ONE
-- decoder `El : ObjCode → Set` — the whole heterogeneity concentrates into that single
-- level-1 function (a `Fam : Set → Set₁`-shaped decoder, the honest floor), and every
-- collection below becomes a Set₀ `List` of codes. `ObjCode` is the FREE MONOID on the
-- founded roots (generators) with unit `⊤'` and tensor `_⊗'_` — the object monoid of the
-- monoidal sphere; `El` / `objDivStr` are its unique monoid-hom extensions into (Set,×,⊤)
-- / the DivStr tensor. Morphism endpoints (unitors/associator) are tensors, so the code
-- must be ⊗-closed; that closure IS why a bare root-enumeration doesn't suffice.
data ObjCode : Set where
  ℕ' F₂' Z3' ℤ' List⊤' two' ⊤' : ObjCode   -- the founded roots + the monoidal unit
  _⊗'_ : ObjCode → ObjCode → ObjCode        -- tensor closure (free-monoid multiplication)

El : ObjCode → Set                          -- the ONE decoder (concentrates the Set₁)
El ℕ'       = ℕ
El F₂'      = F₂
El Z3'      = Fin 3
El ℤ'       = ℤ
El List⊤'   = List ⊤
El two'     = Two
El ⊤'       = ⊤
El (a ⊗' b) = El a × El b

objDivStr : (c : ObjCode) → DivStr (El c)   -- the coded object's DivStr (hom extension)
objDivStr ℕ'       = ℕ-div
objDivStr F₂'      = F₂-div
objDivStr Z3'      = Cyc-div 2
objDivStr ℤ'       = ℤ-div
objDivStr List⊤'   = List-div ⊤
objDivStr two'     = two-div
objDivStr ⊤'       = ⊤-div
objDivStr (a ⊗' b) = objDivStr a ⊗ᴰ objDivStr b

-- An object of the sphere IS its code (Set₀, no carrier packed).
Obj : Set
Obj = ObjCode

objects : List ObjCode
objects = ℕ'      -- the Euclidean carrier (continued fractions)
        ∷ F₂'     -- the field F₂ (parity = mod 2)
        ∷ Z3'     -- the cyclic quotient Z/3 (general-n parity, mod n)
        ∷ ℤ'      -- the integers (signed Bézout's operand)
        ∷ List⊤'  -- the free monoid (wedge's native carrier)
        ∷ two'    -- the square-zero / infinitesimal carrier
        ∷ ⊤'      -- the monoidal unit
        ∷ []

------------------------------------------------------------------------
-- 2. Morphisms: the GROUPOID of WedgeIsos (round-trips forced). The
--    associator/unitors register as genuine non-identity isos.
------------------------------------------------------------------------

-- Set₀ now: both endpoints are CODES; the iso is over their decoded DivStrs.
Morphism : Set
Morphism = Σ ObjCode (λ a → Σ ObjCode (λ b → WedgeIso (objDivStr a) (objDivStr b)))

morphisms : List Morphism
morphisms = (ℕ' , ℕ' , iso-id ℕ-div)
          ∷ (F₂' , F₂' , iso-id F₂-div)
          -- the left unitor: ⊤ ⊗ ℕ ≃ ℕ  (a structure map, non-identity)
          ∷ (⊤' ⊗' ℕ' , ℕ' , unitᴸ ℕ-div)
          -- the right unitor: F₂ ⊗ ⊤ ≃ F₂
          ∷ (F₂' ⊗' ⊤' , F₂' , unitᴿ F₂-div)
          -- the associator: (ℕ⊗F₂)⊗ℤ ≃ ℕ⊗(F₂⊗ℤ)
          ∷ ((ℕ' ⊗' F₂') ⊗' ℤ' , ℕ' ⊗' (F₂' ⊗' ℤ') , assocᴰ ℕ-div F₂-div ℤ-div)
          ∷ []

------------------------------------------------------------------------
-- 3. Bridges: the CATEGORY of (not-necessarily-invertible) homs — the
--    wedge-constructed cross-root edges. Non-invertible, so they live here
--    and NOT in `morphisms`; the type enforces the distinction.
------------------------------------------------------------------------

-- Set₀ now: coded endpoints, bridge over their decoded DivStrs.
BridgeEntry : Set
BridgeEntry = Σ ObjCode (λ a → Σ ObjCode (λ b → Bridge (objDivStr a) (objDivStr b)))

bridges : List BridgeEntry
bridges = (ℕ' , F₂' , parity-bridge)        -- parity (mod 2): ℕ ↠ F₂
        ∷ (ℕ' , Z3' , modn-bridge 2)        -- mod 3: ℕ ↠ Z/3 (general-n)
        ∷ (ℕ' , ℤ' , include-ℕℤ)            -- inclusion: ℕ ↪ ℤ
        ∷ []

------------------------------------------------------------------------
-- 4. The category/groupoid laws, as registry facts (forced by typing).
------------------------------------------------------------------------

-- every object has its identity correspondence (reflexivity).
id-of : (c : ObjCode) → Morphism
id-of c = c , c , iso-id (objDivStr c)

-- the groupoid is closed under inversion: every iso's inverse is an iso.
inverse-of : Morphism → Morphism
inverse-of (a , b , c) = b , a , iso-sym c

-- every iso is, in particular, a bridge — the groupoid embeds in the category.
forget-iso : Morphism → BridgeEntry
forget-iso (a , b , c) = a , b , WedgeIso.fwd c
