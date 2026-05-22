------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.AsPresented
--
-- GL(3, F₂) as a PresentedGroup with 3 generators (the multi-route
-- arc's Sylow witnesses: swap01-GL, cycle3-GL, singer-GL). Each
-- generator's Sylow-membership witness is constructively provided
-- (via Fin index + iterateG identity at index 1).
--
-- Y3 of the 10-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Provides the generator data needed by Y4's joint-gen discharge
-- via Y2's pipeline.
--
-- KEY STRUCTURAL CONTENT:
--
--   Each generator IS a Sylow element by construction:
--     swap01-GL is in Sylow-2 (= ⟨swap01-GL⟩, index 1 in Fin 2)
--     cycle3-GL is in Sylow-3 (= ⟨cycle3-GL⟩, index 1 in Fin 3)
--     singer-GL is in Sylow-7 (= ⟨singer-GL⟩, index 1 in Fin 7)
--
--   These witnesses + Y2's pipeline + a representation function
--   discharge joint-gen for any concrete GL3F2 element.
--
-- The representation function (= "every GL3F2 element has a word in
-- the 3 generators") is Y4's content; this slice provides the
-- generator-side data.
--
-- Per [[universal-property-discipline]] + [[expose-generator-not-orbit]]:
-- this is the substrate's right framing of GL(3, F₂)'s structure —
-- 3 generators expose the group; the 168-element orbit is the
-- consequence, not the primitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.AsPresented where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.GL3F2
  using (GL3F2; _·G_; id-GL; applyG; iterateG)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance
  using (swap01-GL; cycle3-GL; singer-GL)
open import Substrate.Algebra.GL3F2.SylowDecomposition
  using (Sylow-predicates; in-cyclic-of; _≈G_)

------------------------------------------------------------------------
-- 1. The generator alphabet: Fin 3 indexing (swap01, cycle3, singer).
------------------------------------------------------------------------

Gen : Set
Gen = Fin 3

-- Named aliases for readability.
gen-swap01 gen-cycle3 gen-singer : Gen
gen-swap01 = zero
gen-cycle3 = suc zero
gen-singer = suc (suc zero)

------------------------------------------------------------------------
-- 2. The generator-to-GL3F2 mapping.
------------------------------------------------------------------------

gen-to-GL3F2 : Gen → GL3F2
gen-to-GL3F2 zero             = swap01-GL
gen-to-GL3F2 (suc zero)       = cycle3-GL
gen-to-GL3F2 (suc (suc zero)) = singer-GL

------------------------------------------------------------------------
-- 3. Each generator's Sylow witness.
--
-- For each generator g ∈ Gen, we construct (i, proof) where i : Fin 3
-- is the Sylow index and proof : Sylow i (gen-to-GL3F2 g).
--
-- The Sylow predicate for index i is "g ∈ ⟨gen-of-Sylow-i⟩", and
-- each generator is at index k=1 in its own cyclic Sylow subgroup
-- (= 1 application of iterateG, which gives the generator itself
-- via iterate-1-is-id).
--
-- Actually, more cleanly: g = iterateG 1 g pointwise, so the
-- Sylow membership witness is (Fin-1, refl-via-applicative-pointwise).
------------------------------------------------------------------------

-- swap01-GL ∈ Sylow-2 at index 1.
swap01-in-Sylow-2 : Sylow-predicates zero swap01-GL
swap01-in-Sylow-2 = suc zero , (λ v → refl)
  -- (the witness: index 1 in Fin 2; equality is iterateG 1 swap01-GL
  --  applied to v = applyG swap01-GL (applyG id-GL v) = applyG swap01-GL v
  --  reduces definitionally on each Vector input)

-- cycle3-GL ∈ Sylow-3 at index 1.
cycle3-in-Sylow-3 : Sylow-predicates (suc zero) cycle3-GL
cycle3-in-Sylow-3 = suc zero , (λ v → refl)

-- singer-GL ∈ Sylow-7 at index 1.
singer-in-Sylow-7 : Sylow-predicates (suc (suc zero)) singer-GL
singer-in-Sylow-7 = suc zero , (λ v → refl)

------------------------------------------------------------------------
-- 4. The gen-to-Sylow mapping (= which Sylow each generator inhabits).
------------------------------------------------------------------------

gen-to-sylow : (g : Gen) → Σ (Fin 3) (λ i → Sylow-predicates i (gen-to-GL3F2 g))
gen-to-sylow zero             = zero , swap01-in-Sylow-2
gen-to-sylow (suc zero)       = suc zero , cycle3-in-Sylow-3
gen-to-sylow (suc (suc zero)) = suc (suc zero) , singer-in-Sylow-7

------------------------------------------------------------------------
-- 5. Capstone — generator data for GL(3, F₂) in place.
--
-- Y3 of the 10-slice arc. With Y3 + Y2 (FromPresented) + Y1
-- (FromWord), the substrate has everything needed to discharge
-- GL(3, F₂)'s joint-gen — for any g ∈ GL3F2 with a representation
-- in this generator alphabet, Y4 produces the InGenerated witness.
--
-- The remaining piece is the representation function:
--   represent : GL3F2 → List Gen
-- such that evaluating represent(g) returns g. For GL(3, F₂),
-- this representation exists by Schreier-Sims-style decomposition
-- (or direct construction via the 168-element table). Y4 takes
-- the representation as input (parametric or constructed).
--
-- Per [[expose-generator-not-orbit]]: Y3 is the GENERATOR side of
-- the substrate's GL(3, F₂) story. The 168-orbit is the
-- consequence, derived via Y4's representation function.
------------------------------------------------------------------------
