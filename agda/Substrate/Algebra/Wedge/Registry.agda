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

open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Product using (_,_; _×_)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.Z using (ℤ)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (Two; two-div)
open import Substrate.Algebra.Wedge.Cross using (_⊗ᴰ_)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
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
-- ⟡set1-paydown (the carrier is QUOTIENTED, not bundled — no Code/El, no Set₁).
--
-- A DivStr over C is a "torsor+C": the wedge torsor PLUS its carrier. Bundling
-- that carrier as data — `Σ Set DivStr`, or a code universe with a decoder
-- `El : Code → Set` — is the ONLY thing that was forcing Set₁, and it is
-- unnecessary: the carrier is a coordinate to QUOTIENT away, and the quotient
-- torsor+C ⇒ torsor is already realized as the Bridge / CrossMix cospan
-- (`embA : Bridge A (base R)` gives `translate embA : CA → Cr`, the carrier map
-- into a common target; `cross` computes at that quotient level). So:
--   * a `List` demands a HOMOGENEOUS element type ⇒ it must pack the carrier ⇒ Set₁;
--   * a heterogeneous PRODUCT of KNOWN-typed facts is Set₀ (`_×_ : Set→Set→Set`),
--     packs nothing, and — since these collections are never folded, only
--     certified by compilation — is exactly the right shape.
--   * the category/groupoid LAWS are stated at the TORSOR level (carrier-generic,
--     `{C : Set}`), which IS "derive the torsor from torsor+C" — the quotient.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 1. Objects: the wedge-founded roots (vertices), each at its own carrier —
--    a Set₀ heterogeneous product (no carrier packed as data).
------------------------------------------------------------------------

objects :  DivStr ℕ × DivStr F₂ × DivStr (Fin 3) × DivStr ℤ
         × DivStr (List ⊤) × DivStr Two × DivStr ⊤
objects = ℕ-div        -- the Euclidean carrier (continued fractions)
        , F₂-div       -- the field F₂ (parity = mod 2)
        , Cyc-div 2    -- the cyclic quotient Z/3 (general-n parity, mod n)
        , ℤ-div        -- the integers (signed Bézout's operand)
        , List-div ⊤   -- the free monoid (wedge's native carrier)
        , two-div      -- the square-zero / infinitesimal carrier
        , ⊤-div        -- the monoidal unit

------------------------------------------------------------------------
-- 2. Morphisms: the groupoid of WedgeIsos; the unitors/associator register
--    as genuine non-identity isos (their endpoints ARE tensors, stated
--    directly — no code needed to name a tensor object).
------------------------------------------------------------------------

morphisms :  WedgeIso ℕ-div ℕ-div
           × WedgeIso F₂-div F₂-div
           × WedgeIso (⊤-div ⊗ᴰ ℕ-div) ℕ-div                                    -- left unitor
           × WedgeIso (F₂-div ⊗ᴰ ⊤-div) F₂-div                                   -- right unitor
           × WedgeIso ((ℕ-div ⊗ᴰ F₂-div) ⊗ᴰ ℤ-div) (ℕ-div ⊗ᴰ (F₂-div ⊗ᴰ ℤ-div)) -- associator
morphisms = iso-id ℕ-div
          , iso-id F₂-div
          , unitᴸ ℕ-div
          , unitᴿ F₂-div
          , assocᴰ ℕ-div F₂-div ℤ-div

------------------------------------------------------------------------
-- 3. Bridges: the (not-nec-invertible) cross-root homs — each a carrier-
--    QUOTIENT map (a Bridge A B is `translate : CA → CB`, the torsor+C ⇒
--    torsor+C' coordinate change; the CrossMix cospan is two of these into a
--    common target). Non-invertible, so distinct from `morphisms` by type.
------------------------------------------------------------------------

bridges :  Bridge ℕ-div F₂-div          -- parity (mod 2): ℕ ↠ F₂
         × Bridge ℕ-div (Cyc-div 2)     -- mod 3: ℕ ↠ Z/3 (general-n)
         × Bridge ℕ-div ℤ-div           -- inclusion: ℕ ↪ ℤ
bridges = parity-bridge , modn-bridge 2 , include-ℕℤ

------------------------------------------------------------------------
-- 4. The category/groupoid laws, stated GENERICALLY at the torsor level
--    (carrier-quotiented — they range over every object, so no enumeration
--    or code to quantify over is needed).
------------------------------------------------------------------------

-- every object has its identity iso.
id-iso : {C : Set} (D : DivStr C) → WedgeIso D D
id-iso = iso-id

-- the groupoid is closed under inversion: every iso's inverse is an iso.
inv-iso : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → WedgeIso A B → WedgeIso B A
inv-iso = iso-sym

-- every iso is, in particular, a bridge — the groupoid embeds in the category.
iso→bridge : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → WedgeIso A B → Bridge A B
iso→bridge = WedgeIso.fwd
