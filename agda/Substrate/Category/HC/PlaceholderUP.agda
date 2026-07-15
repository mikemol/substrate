------------------------------------------------------------------------
-- Substrate.Category.HC.PlaceholderUP
--
-- The substrate-honest "trivial UPArrow" template: Source / Target =
-- ⊤, Witness = λ _ _ → ⊤. Used by HC1-HC40 as the placeholder body
-- while each concept's structural content is still TBD.
--
-- Per [[expose-generator-not-orbit]]: the HC/* family was a 36-file
-- orbit where each module's body was the same trivial record. This
-- module IS the body, exported once. When a per-concept UPArrow gets
-- non-trivial content, that file simply replaces `placeholder` with
-- the new record literal.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.PlaceholderUP where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrowP; mkUP)

-- ⟡UPArrow-dissolve: the Set₀ placeholder carrier. Source = Target = ⊤,
-- Witness ≡ ⊤ are now TYPE PARAMS (not fields), so `placeholder` is a
-- Set₀ term (uncounted), replacing the old `placeholder : UPArrow` (Set₁).
-- The pre-typed alias is exported so the 36 HC aliases need not re-import ⊤.
PlaceholderUPArrow : Set
PlaceholderUPArrow = UPArrowP ⊤ ⊤ (λ _ _ → ⊤)

placeholder : PlaceholderUPArrow
placeholder = mkUP
