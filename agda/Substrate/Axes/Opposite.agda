------------------------------------------------------------------------
-- Substrate.Axes.Opposite
--
-- Defines: partner
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.Opposite where

open import Substrate.Groups.V4.Operations using (_·₄_)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.ActAxis using (act-axis)


------------------------------------------------------------------------
-- `partner s t` — the axis paired WITH `s` under the unique V₄ matching
-- that puts {s,t} together. The other two axes form the OPPOSITE pair,
-- from which a witness must be drawn.
--
-- ⚑ DERIVED FROM THE V₄ ACTION, NOT ENUMERATED — and my first cut WAS the
-- enumeration: sixteen hand-written cases, one per (axis, axis) pair,
-- reproducing `meta_protocol.PAIRINGS`' three frozensets by hand (user:
-- *"the answer to that is in the witness tower"*). Every piece was already
-- present: `v-of-axis` (Axis → V₄, `D↦e C↦α S↦β W↦γ` — the SAME labels as
-- the Python's `PAIRINGS` keys), `act-axis` (the transported action), and
-- `_·_` on V₄.
--
-- The composite `v-of-axis s ·₄ v-of-axis t` IS the matching that pairs s
-- with t: V₄'s group law sends the pair to the double-transposition
-- swapping them, and acting with it on `s` returns `t`'s partner. So the
-- 16 cases collapse to one line, and it is correct BY THE GROUP rather
-- than by sixteen coincidences a reader must check.
--
-- ⚑ AND THE DIAGONAL IS NOW HONEST BY CONSTRUCTION. `partner a a` composes
-- `v ·₄ v = e`, so it returns `a` — not because a fallback clause says so,
-- but because the identity fixes every point. An edge needs distinct
-- endpoints; `Substrate.Axes.Signature` carries that as a field and never
-- reaches this case.
------------------------------------------------------------------------

partner : Axis → Axis → Axis
partner s t = act-axis (v-of-axis s ·₄ v-of-axis t) s
