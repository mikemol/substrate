------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.IterPow
--
-- Generic word-indexed iteration of a V₄-endomap. iter-pow f w v
-- applies f once per generator letter in w. Each Z_n.a letter
-- contributes one application of f; the constructor identity of the
-- letter is irrelevant.
--
-- rot-pow and swap-pow are the two existing instances; both collapse
-- to thin renamings of iter-pow with the underlying generator pinned.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.IterPow where

open import Substrate.Groups.V4 using (V₄)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

iter-pow : {Gen : Set} → (V₄ → V₄) → Word Gen → V₄ → V₄
iter-pow f []      v = v
iter-pow f (_ ∷ w) v = f (iter-pow f w v)
