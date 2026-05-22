------------------------------------------------------------------------
-- Substrate.TokiPona.Linearity
--
-- T7 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]].
--
-- Sister slice to Lojban L7 Functoriality. Packages the coherence
-- obligations the arc's entailment demands on the **linear side**:
--
--   FreeLinearization(NimiSpace) → BilinearComposition(ModifierBilinear)
--     ⊢ ∀ (s : TokiSentence). WellTyped s × Linear ⟦ s ⟧
--
-- This module discharges the **structural-coherence** half:
--
--   (Mod-id)     modify ∅ on either side is identity
--   (Mod-comm)   modify is commutative
--   (Mod-assoc)  modify is associative
--   (Chain-++)   modifier-chain respects Coxeter-Word concatenation
--   (Sent-id)    sentence postcompose with identity is identity
--   (Sent-comp)  sentence postcompose composes
--   (Markers-id) merge-markers with no-markers is identity
--
-- T8 (LinearAlgebra) closes the other half (FreeLinearization
-- universal property), giving the full entailment.
--
-- Per [[feedback-grothendieck-coherence-rule]]: the bundled
-- `TokiLinearity` record below is the witness object downstream
-- consumers cite instead of unfolding individual lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Linearity where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; sym)

open import Substrate.Groups.Coxeter.Word using (Word)

open import Substrate.TokiPona.SemanticSpace
  using (SemVec; ∅; _⊕_)
open import Substrate.TokiPona.ModifierBilinear
  using (modify; modify-identityˡ; modify-identityʳ;
         modify-comm; modify-assoc; modify-self-inverse;
         modifier-chain; modifier-chain-[]; modifier-chain-++)
open import Substrate.TokiPona.TokiSentence
  using (TokiSentence; interpret;
         postcompose-predicate; postcompose-object;
         postcompose-predicate-id; postcompose-predicate-compose)
open import Substrate.TokiPona.Particles
  using (MarkerSet; no-markers; merge-markers;
         merge-no-markersˡ; merge-no-markersʳ;
         MarkedSentence)

------------------------------------------------------------------------
-- 1. The packaged TokiLinearity record.
--
-- A bundle of the linearity / commutative-monoid coherences for
-- export to T9/T10. Sister to Lojban's `BridiFunctoriality`.
------------------------------------------------------------------------

record TokiLinearity (m : ℕ) : Set where
  field
    mod-identityˡ :
      (n : SemVec m) → modify ∅ n ≡ n
    mod-identityʳ :
      (h : SemVec m) → modify h ∅ ≡ h
    mod-comm :
      (h n : SemVec m) → modify h n ≡ modify n h
    mod-assoc :
      (h n₁ n₂ : SemVec m) →
      modify (modify h n₁) n₂ ≡ modify h (modify n₁ n₂)
    chain-++ :
      (h : SemVec m) (ns₁ ns₂ : Word (SemVec m)) →
      modifier-chain h (Substrate.Groups.Coxeter.Word._++_ ns₁ ns₂) ≡
        modifier-chain (modifier-chain h ns₁) ns₂
    sent-id :
      (s : TokiSentence m) →
      interpret (postcompose-predicate (λ x → x) s) ≡ interpret s
    sent-compose :
      (f g : SemVec m → SemVec m) (s : TokiSentence m) →
      interpret (postcompose-predicate (λ x → g (f x)) s) ≡
        interpret (postcompose-predicate g (postcompose-predicate f s))
    markers-identityˡ :
      (ms : MarkerSet) → merge-markers no-markers ms ≡ ms
    markers-identityʳ :
      (ms : MarkerSet) → merge-markers ms no-markers ≡ ms

------------------------------------------------------------------------
-- 2. The canonical instance.
--
-- All lemmas are structural (refl or directly inherited from T1-T6).
-- No per-m proof obligation — the laws hold uniformly.
------------------------------------------------------------------------

canonical-linearity : {m : ℕ} → TokiLinearity m
canonical-linearity = record
  { mod-identityˡ       = modify-identityˡ
  ; mod-identityʳ       = modify-identityʳ
  ; mod-comm            = modify-comm
  ; mod-assoc           = modify-assoc
  ; chain-++            = modifier-chain-++
  ; sent-id             = postcompose-predicate-id
  ; sent-compose        = postcompose-predicate-compose
  ; markers-identityˡ   = merge-no-markersˡ
  ; markers-identityʳ   = merge-no-markersʳ
  }
