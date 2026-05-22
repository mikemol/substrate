------------------------------------------------------------------------
-- Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment
--
-- D7 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Sister slice to D6 (Lojban). Provides the retroactive alignment
-- on the Toki Pona side: the AsLinearBridge's "shared parent
-- extraction deferred" note (line 28-35 of
-- Substrate.TokiPona.AsLinearBridge, written before the
-- Classification arc) is superseded — the parent primitive
-- Substrate.Category.FreeOverBasis now exists, and the Toki Pona
-- Bridge is structurally an instance of it via tokipona-witness
-- from C3.
--
-- Per [[feedback-comments-dont-overclaim]]: the AsLinearBridge
-- file's original prose is preserved. The alignment is supplied
-- as fresh Agda content here.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)

open import Substrate.TokiPona.Nimi using (Nimi; nimi-count)
open import Substrate.TokiPona.SemanticSpace using (SemVec)
open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)
open import Substrate.TokiPona.AsLinearBridge using (module Bridge)
open import Substrate.TokiPona.AsFreeOverBasis
  using (tokipona-witness; tokipona-free-structure)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; LanguageWitness; η;
         WitnessName; TokiPona;
         FreeConstructionClass; Free-F2-module;
         name; class)

------------------------------------------------------------------------
-- 1. η of the TokiPona FreeOverBasis IS the `nimi-as-vector`
-- one-hot embedding.
--
-- Connects the Classification arc's basis embedding to the T1
-- SemanticSpace basis (each nimi → its corresponding basis vector
-- in SemVec nimi-count).
------------------------------------------------------------------------

tokipona-η-is-nimi-as-vector :
  (n : Nimi) → η tokipona-free-structure n ≡ nimi-as-vector n
tokipona-η-is-nimi-as-vector _ = refl

------------------------------------------------------------------------
-- 2. The AsLinearBridge's `program` agrees with the basis-action
-- on single-nimi words.
--
-- For any V + per-nimi operation, the Bridge program applied to a
-- single-nimi word IS the basis operation. The FreeOverBasis
-- η-coherence at the program layer (Toki Pona side).
------------------------------------------------------------------------

program-on-single-is-op :
  (V : Set) (_⊞_ : V → V → V) (e : V) (nimi-image : Nimi → V) →
  (n : Nimi) (s : V) →
  Bridge.program V _⊞_ e nimi-image (n ∷ []) s ≡ (s ⊞ nimi-image n)
program-on-single-is-op V _⊞_ e nimi-image n s = refl

------------------------------------------------------------------------
-- 3. Witness identity.
------------------------------------------------------------------------

tokipona-witness-class : class tokipona-witness ≡ Free-F2-module
tokipona-witness-class = refl

tokipona-witness-name : name tokipona-witness ≡ TokiPona
tokipona-witness-name = refl

------------------------------------------------------------------------
-- 4. Capstone.
--
-- The "shared parent extraction is deferred" note from T10
-- AsLinearBridge is SUPERSEDED on the Toki Pona side. Together
-- with D6 (the Lojban side), the parent primitive's coverage of
-- both arcs is now substrate-witnessed at the alignment-lemma
-- level.
--
-- D8 unifies D6 + D7 into a single substrate-internal
-- RetroactiveAlignment record.
------------------------------------------------------------------------
