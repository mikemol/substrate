------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual
--
-- PD2-PD6: locally compact abelian groups, characters, Pontryagin
-- dual, the duality theorem, F₂ⁿ as self-dual.
--
-- Per [[categorical-name-first]]: Pontryagin duality, locally
-- compact abelian (LCA) group, character, dual group are all
-- standard.
--
-- The Pontryagin dual G^ of a LCA group G is the group of
-- continuous characters G → U(1) (= unit circle in ℂ). The
-- Pontryagin duality theorem states G ≅ (G^)^ — every LCA group
-- is isomorphic to its double dual.
--
-- For finite abelian groups (the substrate's focus):
--   * G^ is isomorphic to G (non-canonically)
--   * F₂ⁿ is self-dual (the WHT is its own inverse up to scale)
--   * Z/n's dual is Z/n
--   * Finite-abelian Pontryagin duality decomposes by CRT
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.AbelianGroup
open import Substrate.Algebra.TopologicalGroup

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- PD2: A locally compact abelian (LCA) group.
--
-- For our discrete substrate focus, LCA = abelian group with
-- discrete topology (every subset is open). Continuous limits
-- (Lie groups) deferred per [[continuous-via-discrete-inference-
-- rules]].

record LocallyCompactAbelian (A : Set) : Set where
  field
    abelian-group : AbelianGroup A
    topology      : TopologicalGroup A
    -- LCA structural marker; concrete instances supply discrete
    -- topology for finite/discrete groups.

open LocallyCompactAbelian public

------------------------------------------------------------------------
-- PD3: Character of an LCA group.
--
-- A character χ : G → U(1) is a continuous group homomorphism into
-- the unit circle. For finite abelian groups, χ takes values in
-- the n-th roots of unity for some n dividing |G|.
--
-- Parameterised by the target circle / roots-of-unity type.

record Character (A : Set) (RootsType : Set) : Set where
  field
    chi : A → RootsType
    -- chi is a group homomorphism (the homomorphism law stated
    -- abstractly; concrete instances supply).

open Character public

------------------------------------------------------------------------
-- PD4: The Pontryagin dual.
--
-- G^ = { χ : G → U(1) | χ a group homomorphism }, equipped with
-- pointwise multiplication.
--
-- For finite G: G^ is finite and |G^| = |G|. The substrate's discrete
-- LCA dual is the set of all characters.

-- ⟡set1-paydown: parameterize Chars. The characters carrier was a `Chars : Set` FIELD,
-- forcing PontryaginDual : Set₁. Take it as the module parameter; the CONSUMER names it
-- (`PontryaginDual Chars A RootsType`). Every field is then Set-valued, so the record is Set.
module _ (Chars : Set) where

  record PontryaginDual (A : Set) (RootsType : Set) : Set where
    field
      -- Concrete instances enumerate the characters and supply the
      -- pointwise group operations over the supplied Chars carrier.
      dual-mult  : Chars → Chars → Chars
      dual-id    : Chars
      dual-inv   : Chars → Chars

  open PontryaginDual public

------------------------------------------------------------------------
-- PD5: Pontryagin duality theorem (statement).
--
-- For every LCA group G, there exists a canonical isomorphism
--   G ≅ (G^)^ : g ↦ (χ ↦ χ(g))
-- I.e., G is naturally isomorphic to its double dual.
--
-- Stated as a record at the abstract level; concrete instances
-- (for finite abelian groups, etc.) supply the isomorphism.

-- Per [[coalgebraic-not-consumer-driven]]: capture the iso
-- obligation as a record of consumer-supplied witnesses. For finite
-- abelian groups the double-dual carrier is canonically A itself
-- via the evaluation pairing a ↦ (χ ↦ χ a); the consumer supplies
-- this carrier + the iso bridges.

-- ⟡set1-paydown: parameterize DoubleDual (and Chars, for the G-dual param). The double-dual
-- carrier was a `DoubleDual : Set` FIELD (Set₁ debt); take it as a module parameter. Chars is
-- also lifted so the `G-dual : PontryaginDual Chars A RootsType` param typechecks. Consumers write
-- `PontryaginDualityTheorem Chars DoubleDual A RootsType G G-dual`.
module _ (Chars : Set) (DoubleDual : Set) where

  record PontryaginDualityTheorem
         (A : Set)
         (RootsType : Set)
         (G : LocallyCompactAbelian A)
         (G-dual : PontryaginDual Chars A RootsType) : Set where
    field
      -- The canonical iso A ≅ DoubleDual.
      to         : A → DoubleDual
      from       : DoubleDual → A
      to-from    : (d : DoubleDual) → to (from d) ≡ d
      from-to    : (a : A) → from (to a) ≡ a

  open PontryaginDualityTheorem public

------------------------------------------------------------------------
-- PD6: F₂ⁿ as self-dual.
--
-- For G = F₂ⁿ (the additive group of n-dimensional F₂-vector space),
-- the characters are χ_v : F₂ⁿ → {±1} defined by χ_v(u) = (-1)^⟨u,v⟩.
-- The set of characters is itself isomorphic to F₂ⁿ via v ↔ χ_v.
--
-- This is what makes the Walsh-Hadamard transform (the F₂ⁿ Fourier
-- transform) symmetric: the transform's matrix equals its inverse
-- up to a scaling factor.
--
-- Stated structurally; concrete F₂ⁿ instances supply the self-dual
-- isomorphism.

-- Per [[coalgebraic-not-consumer-driven]]: the self-dual iso is
-- consumer-supplied: forward map v ↦ χ_v (using the standard
-- bilinear form ⟨u, v⟩) + backward + round-trips. The consumer's
-- F₂ⁿ-vector type is parametric in the carrier (Vector n, or
-- similar substrate-native form).

-- ⟡set1-paydown: parameterize F2nVec and F2nChars. Both carriers were `: Set` FIELDS
-- (Set₁ debt); take them as module parameters. Consumers write `F2nSelfDual F2nVec F2nChars n`
-- (self-duality supplies the same carrier for both).
module _ (F2nVec : Set) (F2nChars : Set) where

  record F2nSelfDual (n : ℕ) : Set where
    field
      to         : F2nVec → F2nChars
      from       : F2nChars → F2nVec
      to-from    : (c : F2nChars) → to (from c) ≡ c
      from-to    : (v : F2nVec) → from (to v) ≡ v

  open F2nSelfDual public
