------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.AsAction
--
-- THE apex of the S₃-on-V₄ cluster: the bundled SetoidGroup-Action
-- witnessing that S₃ acts on V₄.
--
-- Every lemma in this arc — act (Dispatch), act-ε (Axioms.ActEpsilon),
-- act-∙ (Composition.ActDot, lifted from the per-block canonical proofs
-- via Coxeter normalize-canonical), and the homomorphism law act-hom —
-- was proved on behalf of THIS object: S₃ acts on V₄. They existed as
-- free-floating laws; this collects the action laws into the
-- Substrate.Algebra.SetoidGroup.Action record so downstream code can
-- consume "S₃ acts on V₄" as one value rather than re-citing the pieces.
--
-- (act-hom is the further fact that each S₃ element acts by a V₄-group-
-- homomorphism — i.e. the action is BY AUTOMORPHISMS. It is not a field
-- of the bare Action record; it remains available as
-- HomSwaps.ActHom.act-hom and upgrades this Action to an action by
-- automorphisms.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.AsAction where

open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.S3 as S₃
open import Substrate.Algebra.SetoidGroup.Action using (Action)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon using (act-ε)
open import Substrate.Groups.Actions.S3-on-V4.Composition.ActDot using (act-∙)

-- S₃ acts on V₄: the bundled action. Fields are exactly the arc's lemmas.
S₃-acts-on-V₄ : Action S₃.Carrier S₃._≈_ S₃.S₃-Group V₄
S₃-acts-on-V₄ = record
  { act    = act
  ; act-id = act-ε
  ; act-∙  = act-∙
  }
