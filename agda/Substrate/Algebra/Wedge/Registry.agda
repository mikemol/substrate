------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Registry
--
-- THE GROUPOID'S REALITY ANCHOR — the Registry pattern (cf.
-- Category.UniversalProperty.Registry for the topos ring), now for the wedge
-- groupoid: a list of the carriers (objects) that live in it and the
-- correspondences (morphisms) between them. As before, compilation IS the
-- certification, and the list cannot be padded:
--   * an object is a DivStr — a genuine wedge-carrier;
--   * a morphism is a WedgeIso, which CARRIES its round-trip proofs, so a
--     non-invertible bridge cannot be registered as a correspondence. A
--     registered morphism is provably a groupoid iso (codomain = inverse of
--     domain, mediated by the wedge's (1,z) corner) — it cannot be faked.
--
-- Grow `objects`/`morphisms` to inhabit the groupoid: each entry compiling ⟹
-- it really lives there. The producer (wedge of two capstones → WedgeIso)
-- will populate `morphisms` with non-identity entries once it exists; until
-- then the honest content is the identities (reflexivity) and closure under
-- inversion (iso-sym) — the groupoid laws, made registry facts.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Registry where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (two-div)
open import Substrate.Algebra.Wedge.Iso using (WedgeIso; iso-id; iso-sym)

------------------------------------------------------------------------
-- 1. Objects: the carriers that live in the groupoid.
------------------------------------------------------------------------

objects : List DivStr
objects = ℕ-div          -- the Euclidean carrier (continued fractions)
        ∷ two-div        -- the square-zero / infinitesimal carrier
        ∷ []

------------------------------------------------------------------------
-- 2. Morphisms: correspondences. A WedgeIso can't be padded (round-trips
--    required) — registering one certifies a genuine groupoid iso.
------------------------------------------------------------------------

Morphism : Set₁
Morphism = Σ DivStr (λ A → Σ DivStr (λ B → WedgeIso A B))

morphisms : List Morphism
morphisms = (ℕ-div , ℕ-div , iso-id ℕ-div)
          ∷ (two-div , two-div , iso-id two-div)
          ∷ []

------------------------------------------------------------------------
-- 3. The groupoid laws, as registry facts (forced by typing).
------------------------------------------------------------------------

-- every object has its identity correspondence (reflexivity).
id-of : (D : DivStr) → Morphism
id-of D = D , D , iso-id D

-- the registry is closed under inversion: every morphism's inverse is a
-- morphism (codomain = inv domain, both ways).
inverse-of : Morphism → Morphism
inverse-of (A , B , c) = B , A , iso-sym c
