{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.Present
--
-- The ⊤-like BASE FIBER of a Refinement Φ-chain: at every grade the element is
-- still present, so R⁰ = λ _ → Present is the pre-fixed-point the chain descends
-- from. Homed here, beside Refinement itself, because it belongs to the Φ-chain
-- vocabulary rather than to either consumer: SKIGradedFlatAllegory (the SKI arity
-- fiber) and ExtrudeCoEmitGraded (the prefix-observation fiber) had DECLARED IT
-- TWICE, one copy each. A duplicate `data` is debt the sumtype ratchet refuses;
-- both now import this one declaration.
------------------------------------------------------------------------

module Substrate.Category.Allegory.Refinement.Present where

data Present : Set where present : Present
