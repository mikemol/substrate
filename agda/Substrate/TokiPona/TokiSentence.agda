------------------------------------------------------------------------
-- Substrate.TokiPona.TokiSentence
--
-- T5 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]].
--
-- The Toki Pona sentence structure as a record: subject, predicate,
-- and (optional) object vectors. Interpretation = feature-bag
-- pooling via ⊕ — the simplest faithful F₂ semantics.
--
-- "Optional object" without a Maybe import: use ∅ as the absent
-- marker. Avoids stdlib's Data.Maybe per
-- [[feedback-minimize-stdlib-deps]] strengthening. The ∅-as-absent
-- convention is honest because the substrate's ⊕-identityʳ guarantees
-- attaching ∅ is a semantic no-op.
--
-- Sister slice: Lojban L5 Bridi (n-ary morphism application). Lojban
-- preserves positional structure via Vec Sumti n; Toki Pona collapses
-- to feature-bag pooling. The structural distinction is re-introduced
-- by T6's particles (li, e) at the marker layer.
--
-- Per [[feedback-grothendieck-coherence-rule]]: post-composition on
-- the semantic vector is functorial; the interpret-postcompose
-- coherence is provided as the L5-analog functoriality handle that
-- T7 consumes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.TokiSentence where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; sym)

open import Substrate.TokiPona.SemanticSpace
  using (SemVec; ∅; _⊕_; ⊕-assoc; ⊕-comm;
         ⊕-identityˡ; ⊕-identityʳ)

private
  variable
    m : ℕ

------------------------------------------------------------------------
-- 1. The TokiSentence record.
--
-- subject + predicate + object as semantic vectors. object = ∅
-- means no object attached (the ⊕-identity behaviour makes this
-- semantically transparent).
------------------------------------------------------------------------

record TokiSentence (m : ℕ) : Set where
  constructor mkSentence
  field
    subject   : SemVec m
    predicate : SemVec m
    object    : SemVec m

open TokiSentence public

------------------------------------------------------------------------
-- 2. Semantic interpretation: feature-bag pooling.
--
-- The sentence's meaning is the ⊕-pooled vector of its parts.
-- T6's particles will refine this for richer linguistic markers,
-- but at this layer the interpretation is the simple commutative
-- pooling.
------------------------------------------------------------------------

interpret : TokiSentence m → SemVec m
interpret s = (subject s ⊕ predicate s) ⊕ object s

------------------------------------------------------------------------
-- 3. Constructors for sentences with / without an object.
--
-- Object-less sentences use ∅ in the object slot.
------------------------------------------------------------------------

intransitive : SemVec m → SemVec m → TokiSentence m
intransitive subj pred = mkSentence subj pred ∅

transitive : SemVec m → SemVec m → SemVec m → TokiSentence m
transitive subj pred obj = mkSentence subj pred obj

------------------------------------------------------------------------
-- 4. Intransitive sentences interpret as subject ⊕ predicate.
------------------------------------------------------------------------

intransitive-interpret :
  (subj pred : SemVec m) →
  interpret (intransitive subj pred) ≡ (subj ⊕ pred) ⊕ ∅
intransitive-interpret _ _ = refl

intransitive-interpret-clean :
  (subj pred : SemVec m) →
  interpret (intransitive subj pred) ≡ subj ⊕ pred
intransitive-interpret-clean subj pred = ⊕-identityʳ (subj ⊕ pred)

------------------------------------------------------------------------
-- 5. Post-composition on the semantic vector.
--
-- If h : SemVec m → SemVec m, post-composing on the predicate
-- yields a new sentence whose interpretation factors through h on
-- the predicate slot. Sister to Lojban L5's `bridi-postcompose`,
-- but here we lift via the structural slot (predicate) rather than
-- the bridi-as-whole.
------------------------------------------------------------------------

postcompose-predicate :
  (SemVec m → SemVec m) → TokiSentence m → TokiSentence m
postcompose-predicate h s = mkSentence (subject s) (h (predicate s)) (object s)

postcompose-object :
  (SemVec m → SemVec m) → TokiSentence m → TokiSentence m
postcompose-object h s = mkSentence (subject s) (predicate s) (h (object s))

------------------------------------------------------------------------
-- 6. Identity and composition for postcompose-predicate.
--
-- Identity on the predicate is identity on interpret; composition
-- composes — the standard functor laws T7 (Linearity) consumes.
------------------------------------------------------------------------

postcompose-predicate-id :
  (s : TokiSentence m) →
  interpret (postcompose-predicate (λ x → x) s) ≡ interpret s
postcompose-predicate-id _ = refl

postcompose-predicate-compose :
  (f g : SemVec m → SemVec m) (s : TokiSentence m) →
  interpret (postcompose-predicate (λ x → g (f x)) s) ≡
    interpret (postcompose-predicate g (postcompose-predicate f s))
postcompose-predicate-compose _ _ _ = refl
