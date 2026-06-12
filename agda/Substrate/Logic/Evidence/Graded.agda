------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Graded
--
-- A graded verdict: evidence paired with the WARRANT of its justification.
-- The verdict joiners (Verdict.∧E / ∨E) lift to graded joiners that combine
-- the evidence by the connective and the warrant by the meet `_⊓w_` — so
-- the warrant RIDES UNDER the joiner: a combined claim is graded by its
-- weakest premise (el-atlas §0 demotion), automatically, as it is built.
-- The projection laws below witness exactly that the two components track
-- independently (the carrier is the product Evidence × Warrant).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Graded where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Logic.Evidence.Verdict using (Evidence; _∧E_; _∨E_)
open import Substrate.Logic.Evidence.Warrant using (Warrant; _⊓w_)

infix 4 _at_

record GradedEvidence : Set where
  constructor _at_
  field
    ev : Evidence   -- the evidence content
    gr : Warrant    -- the warrant of its justification

open GradedEvidence public

------------------------------------------------------------------------
-- The graded joiners: content by the verdict connective, warrant by the
-- weakest-dominates meet.
------------------------------------------------------------------------

infixr 6 _∧G_ _∨G_

_∧G_ : GradedEvidence → GradedEvidence → GradedEvidence
(a at g) ∧G (b at h) = (a ∧E b) at (g ⊓w h)

_∨G_ : GradedEvidence → GradedEvidence → GradedEvidence
(a at g) ∨G (b at h) = (a ∨E b) at (g ⊓w h)

------------------------------------------------------------------------
-- The warrant rides under the joiner: the warrant of a combination is the
-- meet of the warrants, and the content is the connective of the contents.
-- Both by refl — the two axes never interfere.
------------------------------------------------------------------------

gr-∧G : (x y : GradedEvidence) → gr (x ∧G y) ≡ gr x ⊓w gr y
gr-∧G (a at g) (b at h) = refl

ev-∧G : (x y : GradedEvidence) → ev (x ∧G y) ≡ ev x ∧E ev y
ev-∧G (a at g) (b at h) = refl

gr-∨G : (x y : GradedEvidence) → gr (x ∨G y) ≡ gr x ⊓w gr y
gr-∨G (a at g) (b at h) = refl

ev-∨G : (x y : GradedEvidence) → ev (x ∨G y) ≡ ev x ∨E ev y
ev-∨G (a at g) (b at h) = refl
