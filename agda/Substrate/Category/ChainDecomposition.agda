------------------------------------------------------------------------
-- Substrate.Category.ChainDecomposition
--
-- Q8 of the codec arc bridges back to substrate primitives: the codec's
-- per-Sylow chain decomposition (V₄ × S₃ semidirect at S₄, and more
-- generally any PrimeFactoredGauge instance) abstracts to a
-- categorical primitive.
--
-- A ChainDecomposition of an element g ∈ G is a (componentwise)
-- factoring of g into a tuple of Sylow-component elements, one per
-- prime in the gauge's factorization, plus a witness that the
-- product-in-prescribed-order equals g.
--
-- This generalises:
--   * S₄ chain (V₄, Z/3, Z/2-of-S₃) used by scratch/eliza's chain codec
--   * `MultiRouteEquivariance::gauge-element` + `sylow-chain`
--     (already present in the substrate as the EXISTENCE of the chain;
--     this primitive names the SHAPE of the chain itself)
--
-- Per [[opcode-vm-codec]] / [[codec-as-pfg-witness]]: the codec's
-- runtime chain decomposition is an INSTANCE of this primitive at
-- S₄. The decoder's per-emission unfolding IS the chain's structural
-- expansion.
--
-- Per [[expose-generator-not-orbit]]: the chain exposes the Sylow
-- generators that produced g, not the orbit of g.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ChainDecomposition where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.SylowDecomposition
  using (SylowDecomposition)

------------------------------------------------------------------------
-- 1. ChainDecomposition — the costructure.
--
-- For a SylowDecomposition of G with n primes, a chain decomposition
-- of g ∈ G is a vector (g₀, g₁, …, gₙ₋₁) where gᵢ ∈ Sylow_i, plus a
-- witness that g = g₀ · g₁ · … · gₙ₋₁ (in the fixed left-to-right
-- product order).
--
-- The ORDER is a chirality choice per [[ordering-is-chirality-choice]];
-- different orderings give different chains for the same g. We
-- parameterise by the prescribed order (here: ascending Sylow index).
------------------------------------------------------------------------

-- Product of components in ascending-index order. Defined outside
-- the record because Agda parses `where` clauses inside record-field
-- types restrictively.
reconstruct-chain :
  ∀ {ℓG : Level} {G : Set ℓG}
    {m : ℕ}
    (_·G_ : G → G → G) (εG : G)
    (xs : Vec G m) → G
reconstruct-chain _·G_ εG [] = εG
reconstruct-chain _·G_ εG (x ∷ xs) = x ·G reconstruct-chain _·G_ εG xs

record ChainDecomposition
  {ℓG ℓEG : Level}
  {G : Set ℓG}
  (_·G_ : G → G → G) (εG : G)
  {n : ℕ}
  -- ⟡set1-rp-pfg: SylowDecomposition's `Sylow` is a param now — bind the predicate here and
  -- apply it directly (the ex-projection `Sylow factorization i …` IS `Sylow i …`).
  {Sylow : Fin n → (G → Set ℓG)}
  (factorization : SylowDecomposition G _·G_ εG n Sylow)
  (_≈G_ : G → G → Set ℓEG)
  (g : G) : Set (ℓG ⊔ ℓEG) where
  constructor mkChain
  field
    components : Vec G n
    -- Each component lies in its respective Sylow.
    in-sylows  : (i : Fin n) → Sylow i (lookup components i)
    -- The product (left-to-right) equals g.
    reconstruct-witness : reconstruct-chain _·G_ εG components ≈G g

open ChainDecomposition public

------------------------------------------------------------------------
-- 2. The universal property.
--
-- For any PrimeFactoredGauge τ, between any two orbit points x, y ∈ X
-- there EXISTS a gauge element g connecting them (per the existing
-- `multi-route-equivariance`). ChainDecomposition gives the
-- structural FORM of that g: a vector of Sylow components.
--
-- The existence of a ChainDecomposition for every g ∈ G is implied
-- by SylowDecomposition's `joint-generated` predicate together with
-- a structural unfolding. The substrate's Y-arc (joint-gen via word
-- presentation) provides one explicit constructor; other constructors
-- (e.g., via repeated quotienting by Sylow normalisers) are valid
-- alternatives.
--
-- Per [[homology-cohomology-recursion]]:
--   observed = g (homology)
--   catalogued = its ChainDecomposition (cohomology)
-- The recursion: each component is itself in a Sylow subgroup which
-- may have its own SylowDecomposition (if the Sylow is composite —
-- though for prime-power Sylows the recursion terminates).
------------------------------------------------------------------------

-- The structural claim is implicit in the record type itself: any
-- inhabitant of ChainDecomposition factorization _≈G_ g witnesses
-- the existence of a chain for g. Per-group constructive instances
-- live in their respective modules:
--   * GL3F2.JointGenViaPresentation (Y-arc explicit constructor)
--   * scratch/eliza/eliza/sylow_chain.py (S₄ runtime instance)
--   * future: Monster.* via descent + Y-arc propagation
--
-- The substrate's --safe flag (per [[agda-cubical-extraction-discipline]])
-- forbids postulates; existence claims are made by INSTANCES.

------------------------------------------------------------------------
-- 3. Connection to the codec's runtime instance.
--
-- scratch/eliza/sylow_chain.py is a PYTHON realisation of this
-- primitive at G = S₄ with:
--   factorization = 24 = 2² · 3 · 2 (V₄ ⋊ S₃ split)
--   components : Vec G 3 = (V₄ component, Z/3 component, Z/2-of-S₃ component)
--   reconstruct-witness : (v ·G s3 ·G s2) ≡ g
-- The `build_chain` function in that module constructs this Vec for
-- every g ∈ S₄; the `ChainEquivarianceWitness` verifies round-trip.
--
-- That runtime instance EMPIRICALLY witnesses the structural claim this
-- Agda module formalises — as an INSTANCE, not a postulate. (There is NO
-- Agda postulate here: per §2 and the --safe discipline, existence is
-- carried by inhabitants of the record, not assumed. The earlier wording
-- "the Agda postulate is supported by …" referred to a postulate that does
-- not exist.) The codec's exhaustive 24-element check exhibits, for every
-- g ∈ S₄, ONE chain in the fixed ascending-index order; chains are NOT
-- unique in general — the order is a chirality choice (§1,
-- [[ordering-is-chirality-choice]]), so "unique chain" is not claimed.
--
-- For larger groups (GL(3, F₂) at 168 elements; Monster at ~10⁵⁴),
-- explicit ChainDecomposition is intractable as enumeration, but
-- the structural claim holds via Y-arc's joint-gen-via-word.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. Cross-references.
--
-- * `SylowDecomposition` (T0) — the substructure ChainDecomposition
--   factors over.
-- * `PrimeFactoredGauge` (T1) — bundles SylowDecomposition with a
--   torsor; chains arise as gauge-element witnesses.
-- * `MultiRouteEquivariance::multi-route-equivariance` (T5) — the
--   EXISTENCE of a chain-decomposable gauge element; this primitive
--   names the STRUCTURE of that element.
-- * `SylowDecomposition.FromWord` (Y1) — explicit Word → InGenerated
--   chain, which decomposes via word position into per-Sylow words.
-- * Codec runtime instance: `scratch/eliza/eliza/sylow_chain.py`
--   `build_chain : S₄ → ChainDecomposition` (exhaustive 24-element).
------------------------------------------------------------------------
