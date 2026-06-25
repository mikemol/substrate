------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetReduce
--
-- CONNECTION LEAF (nodes 5 <-> 8): the HetQ / CrossMix / viaBridges codec
-- layer (Algebra.Q.HetBasis) meets the ℚ-setoid / reduce layer
-- (Algebra.Q.{Reduce, Reduction, Equiv}). Claim: ℚ reduction RESPECTS the
-- viaBridges codec structure — `reduce` lives entirely inside the
-- heterogeneous quotient HetQ ℤ ℕ (which ℚ definitionally IS, via
-- toHetQ/fromHetQ), so the same numerator-basis / denominator-basis split
-- and its cross-multiply ⊗ℚ = viaBridges (id) (+ suc ·) _*ℤ_ apply unchanged
-- to the reduced form. Three certified facts: (1) reduction commutes through
-- the HetQ↔ℚ bijection by refl (the bijection is definitional identity on
-- carriers); (2) ℚ's cross-multiply ⊗ℚ IS the viaBridges codec combinator at
-- the two bridge legs (refl), so the cross-equality of the reduced HetQ form
-- is computed by exactly the same bridge semantics; (3) reduction is
-- value-preserving in the HetQ cross-equality (reuses Q.Properties.Reduce's
-- ≈-canonical) — i.e. reduce preserves the bridge semantics, not just the
-- syntax. Reuse-not-rebuild: re-exports viaBridges / reduce / the HetQ
-- bijections; the only "real" content is one transport of the existing
-- soundness lemma, everything else is refl.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetReduce where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.Reduction using (is-reduced; gcd-of-ℚ)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-canonical)
-- HetBasis is imported UNRESTRICTED: it re-exports `HetQ` publicly and the
-- top-level `_⊗ℚ_` / `_≈Hℚ_` / `≈ℚ-is-cross` come from an `open CrossEq …`
-- (a parametrized submodule that cannot appear in a `using` list).
open import Substrate.Algebra.Q.HetBasis
-- `_≈Hℚ_` is a NON-public renamed-open inside HetBasis (not re-exported), so
-- re-create it here from the exported CrossEq + _⊗ℚ_.
open CrossEq _⊗ℚ_ _≡_ refl sym renaming (_≈H_ to _≈Hℚ_)

------------------------------------------------------------------------
-- 0. Re-exports of the two halves' machinery (the connection's vocabulary).
--    HetQ, toHetQ, fromHetQ, the bijections, viaBridges, _⊗ℚ_, _≈Hℚ_ all
--    arrive transitively from the unrestricted HetBasis import; reduce /
--    is-reduced from the setoid side above.
------------------------------------------------------------------------

-- (names available: HetQ, _//_, hnum, hden, toHetQ, fromHetQ,
--  htq-left-inverse, htq-right-inverse, viaBridges, _⊗ℚ_, _≈Hℚ_; reduce,
--  is-reduced, gcd-of-ℚ.)

------------------------------------------------------------------------
-- 1. Reduction as an endo-operation on the heterogeneous quotient. ℚ IS
--    HetQ ℤ ℕ, so `reduce` transported through the (definitional) bijection
--    is a HetQ ℤ ℕ → HetQ ℤ ℕ map. It stays inside the SAME pair of bases
--    (ℤ numerator, ℕ denominator) — that is the structural content of
--    "reduction respects the codec layer".
------------------------------------------------------------------------

reduceH : HetQ ℤ ℕ → HetQ ℤ ℕ
reduceH h = toHetQ (reduce (fromHetQ h))

-- reduceH commutes with reduce through the HetQ↔ℚ bijection, both ways, by
-- refl: htq-left-inverse / htq-right-inverse are definitional identities, so
-- the diagram closes with no transport cost.
reduceH-commutes : (q : ℚ) → reduceH (toHetQ q) ≡ toHetQ (reduce q)
reduceH-commutes q = refl

reduce-fromHetQ : (h : HetQ ℤ ℕ) → fromHetQ (reduceH h) ≡ reduce (fromHetQ h)
reduce-fromHetQ h = refl

------------------------------------------------------------------------
-- 2. ℚ's cross-multiply ⊗ℚ IS the viaBridges codec combinator at the two
--    bridge legs. codecA = identity (numerator already in ℤ), codecB =
--    ℕ↪ℤ embedding (+ suc ·), common product = _*ℤ_. This is the same
--    factorization HetCrossMix exhibits with actual Bridge codec legs
--    (CrossMul.cross ≡ viaBridges …); here we name the two codecs and show
--    ⊗ℚ = viaBridges of them, by refl.
------------------------------------------------------------------------

num-codec : ℤ → ℤ                 -- numerator leg: identity into the carrier ℤ
num-codec a = a

den-codec : ℕ → ℤ                 -- denominator leg: the ℕ ↪ ℤ inclusion (+ suc)
den-codec d = + suc d

⊗ℚ-is-viaBridges : (a : ℤ) (d : ℕ) →
  (a ⊗ℚ d) ≡ viaBridges num-codec den-codec _*ℤ_ a d
⊗ℚ-is-viaBridges a d = refl

------------------------------------------------------------------------
-- 3. THE CONNECTION: reduction RESPECTS the viaBridges codec semantics.
--    Because the reduced form is again a HetQ ℤ ℕ, the SAME bridge codecs
--    compute its cross term — i.e. the cross-equality of a HetQ value and
--    its reduction is evaluated by viaBridges num-codec den-codec _*ℤ_ on
--    both sides. The cross term of the reduced form, computed via the
--    bridges, agrees with ⊗ℚ on the reduced components (refl).
------------------------------------------------------------------------

reduce-respects-viaBridges : (h : HetQ ℤ ℕ) →
  (hnum (reduceH h) ⊗ℚ hden h)
    ≡ viaBridges num-codec den-codec _*ℤ_ (hnum (reduceH h)) (hden h)
reduce-respects-viaBridges h = refl

------------------------------------------------------------------------
-- 4. Reduction preserves the BRIDGE SEMANTICS (value), not merely the
--    syntactic basis-pair: in the HetQ cross-equality (the equality the
--    codec layer induces), a ℚ and its reduced form are equal. This is the
--    existing soundness lemma `≈-canonical : q ≈ℚ reduce q` transported
--    across `≈ℚ-is-cross` (refl) into the CrossEq layer and through
--    `reduceH-commutes` (refl). So reduce is value-preserving WHEN read
--    through the bridges — the cross-term residue is unchanged.
------------------------------------------------------------------------

reduce-preserves-cross : (q : ℚ) → toHetQ q ≈Hℚ reduceH (toHetQ q)
reduce-preserves-cross q = ≈-canonical q

-- Equivalent ℚ-side statement (definitionally `q ≈ℚ reduce q`): the reduced
-- HetQ form reconstructed back to ℚ has the same value.
reduce-preserves-value : (q : ℚ) → q ≈ℚ fromHetQ (reduceH (toHetQ q))
reduce-preserves-value q = ≈-canonical q
