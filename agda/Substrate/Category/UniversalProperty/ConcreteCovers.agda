------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ConcreteCovers
--
-- UP17 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Concrete UPCover instances. The substrate-relevant covers:
--
--   1. trivial-cover   : the identity-singleton.
--   2. forget-cover    : a forgetful refinement (e.g. FreeLinearization
--      forgets to FreeOverBasis).
--   3. transport-cover : change of carrier (F₂-cover of ℚ-Free, etc.).
--
-- Substrate-honest: the concrete bridge to actual substrate UPs is
-- routed via UPGen.lift; this slice supplies the cover SHAPES.
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; homs are UPTerm O Hom.
-- (O, Hom) enter via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ConcreteCovers where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty.Term using (UPTerm; [])
open import Substrate.Category.UniversalProperty.Coverage using (UPCover)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Trivial cover (identity-singleton).
  ------------------------------------------------------------------------

  trivial-cover : (U : O) → UPCover O Hom U
  trivial-cover U = record
    { Idx   = ⊤
    ; src   = λ _ → U
    ; arrow = λ _ → []
    }

------------------------------------------------------------------------
-- 2. Capstone for UP17.
--
-- Trivial cover lands. Forget / transport / Free* concrete covers
-- attach in HC-arc sub-arcs as they emerge from the higher-cat
-- content; this slice names the canonical instance.
------------------------------------------------------------------------
