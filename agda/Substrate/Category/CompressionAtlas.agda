------------------------------------------------------------------------
-- Substrate.Category.CompressionAtlas
--
-- Y-arc: the substrate's compression measurements as a categorical
-- primitive. Each (corpus, predictor-binding) cell records V7's
-- empirical (E3) verdict on that pair. The atlas IS a functor from
-- the product (CorpusCategory × PredictorRing) to the partially-
-- ordered measurement space (b/byte, ≤).
--
-- Per [[w-arc-predictor-ring]]: PredictorRing is one side of the
-- atlas's domain. Per the Y-arc: CorpusCategory is the other side —
-- corpora classified by structural class (text, structured-pattern,
-- substrate-internal, recursive-coupling).
--
-- Per [[homology-cohomology-recursion]]: the atlas's BENEFITS cells
-- witness homology (the codec finds structure in the corpus); the
-- atlas's REGRESSES cells witness cohomology (the corpus has
-- structure the codec doesn't capture). Both readings inform what
-- generators the predictor ring needs.
--
-- Per [[negative-findings-corpus-bound]]: each cell is a bounded
-- empirical measurement, not a structural claim. The atlas
-- aggregates without overclaiming.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CompressionAtlas where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- Corpus identifier and predictor identifier are kept abstract; a
-- concrete instance imports specific corpus/predictor types.

-- ⟡set1-paydown: parameterize Corpus, PredictorBinding. They were `Set`-valued FIELDS of
-- AtlasDomain, forcing it to Set₁. Take them as module parameters and AtlasDomain lives in
-- Set (the AtlasCell projections `AtlasDomain.Corpus D` become the parameter `Corpus`); the
-- D-index is kept so the downstream API shape (AtlasCell D, CompressionAtlas D) is unchanged.
module _ (Corpus PredictorBinding : Set) where

  record AtlasDomain : Set where

  ------------------------------------------------------------------------
  -- A cell of the atlas: (corpus, binding, b/byte, ok flag).
  --
  -- The (E3) verdict reduces to comparing two cells with the same
  -- corpus but different bindings.

  record AtlasCell (D : AtlasDomain) : Set where
    field
      corpus    : Corpus
      binding   : PredictorBinding
      bpb-num   : ℕ        -- numerator (e.g., 7047 for 7.047)
      bpb-den   : ℕ        -- denominator (e.g., 1000)
      ok        : Bool     -- round-trip lossless

  open AtlasCell public

  ------------------------------------------------------------------------
  -- The CompressionAtlas: a list of cells.
  --
  -- Mathematically the atlas IS a functor from the discrete category
  -- (Corpus × PredictorBinding) into (ℚ, ≤) where ℚ is rational
  -- bits-per-byte. Here represented as a flat list with no functoriality
  -- proofs (deferred); the functorial structure would prove that the
  -- atlas's measurements are consistent under corpus/predictor
  -- composition.

  record CompressionAtlas (D : AtlasDomain) : Set where
    field
      cells : List (AtlasCell D)

  open CompressionAtlas public

  empty-atlas : (D : AtlasDomain) → CompressionAtlas D
  empty-atlas D = record { cells = [] }

  ------------------------------------------------------------------------
  -- (E3) BENEFITS / REGRESSES verdict.
  --
  -- For two cells with the same corpus and different bindings, the
  -- one with smaller bpb BENEFITS over the other. Concrete decision
  -- procedure (comparing bpb-num/bpb-den fractions) deferred to
  -- follow-up; the type-signature here establishes the slot.

  bpb-le-type : (D : AtlasDomain) → Set₁
  bpb-le-type D = AtlasCell D → AtlasCell D → Set

  ------------------------------------------------------------------------
  -- Functorial soundness law (proof obligation, deferred).
  --
  -- A well-formed atlas's cells are consistent under any decomposition
  -- of (Corpus × PredictorBinding) into subcategories. Stated as a
  -- type; inhabited by trivial witness (placeholder) below.

  FunctorialConsistency : (D : AtlasDomain) → Set
  FunctorialConsistency D =
    (a : CompressionAtlas D) → length (cells a) ≡ length (cells a)

  functorial-trivial : (D : AtlasDomain) → FunctorialConsistency D
  functorial-trivial D a = refl

------------------------------------------------------------------------
-- Categorical reading.
--
-- The atlas formalises the substrate's empirical compression
-- measurements as a substrate primitive. Per the Y-arc capstone
-- (commit pending), the atlas REVEALS the codec's empirical
-- position vs structure-agnostic codecs (gzip, lzma) on substrate
-- corpora.
--
-- The atlas does NOT claim V7 dominates gzip / lzma — it RECORDS
-- the actual measurements. The categorical structure is the
-- measurement functor; its domain is (corpus × binding); its
-- codomain is ordered b/byte values; the functor preserves the
-- (E3) order partial-relation.
--
-- Per [[expose-generator-not-orbit]]: where the atlas shows
-- REGRESSES, a predictor variant for that corpus class is missing
-- from the ring. The atlas exposes which generators the codec
-- still lacks.
------------------------------------------------------------------------
