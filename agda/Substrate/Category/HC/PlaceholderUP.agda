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
open import Substrate.Category.UniversalProperty using (UPArrow)

placeholder : UPArrow
placeholder = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }
