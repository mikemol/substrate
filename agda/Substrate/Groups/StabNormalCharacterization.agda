------------------------------------------------------------------------
-- Substrate.Groups.StabNormalCharacterization  (⟹ — the satisfiability iff)
--
-- WHEN is Stab(X)'s member-normal obligation satisfiable? The honest answer,
-- and a correction to the earlier "⟺ orbit(X) = {X}" framing in
-- Substrate.Groups.Subgroup (which was an OVERCLAIM — see below).
--
-- The member-normal obligation
--     member-normal X = ∀ g n, Stab X n → Stab X ((g · n) · g⁻¹)
-- is EQUIVALENT to
--     stab-fixes-orbit X = ∀ g n, Stab X n → Stab (apply g X) n
-- i.e. "every element of Stab(X) fixes every point of the orbit of X". The
-- two are the SAME fact viewed through the conjugation identity
--     (g·n·g⁻¹) ∈ Stab(X)  ⟺  n ∈ Stab(g⁻¹·X),
-- so neither direction needs more than the action laws (inv-r) and the
-- definitional facts  apply (a·b) = apply a ∘ apply b  and  apply (g⁻¹)⁻¹ =
-- apply g.
--
-- WHY "orbit(X) = {X}" was an overclaim (the correction). "X is a global
-- fixed point" is SUFFICIENT (fixed→fixes-orbit below) but NOT NECESSARY:
-- in a regular action Stab(X) = {ε} is (trivially) normal while the orbit is
-- the whole group. The error in the old note was "distinct conjugates of
-- Stab(X) are parameterised by orbit(X), so distance = |orbit X|": the orbit
-- → stabiliser map (Y ↦ Stab Y) is SURJECTIVE but not injective — distinct
-- orbit points can share a stabiliser. Normality is "all conjugates EQUAL",
-- which is "Stab(X) fixes the orbit pointwise", NOT "the orbit is a point".
-- (For the S₄ axis-action the map happens to be injective — distinct axes
-- give distinct S₃'s — so there |orbit| does track the distance; that is a
-- feature of THIS action, not the general law. The action is transitive with
-- no fixed point, so member-normal X is in fact UNSATISFIABLE for every X —
-- StabNotNormal.StabD-not-normal witnesses it at D — and dually Stab(X) does
-- NOT fix its whole orbit.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.StabNormalCharacterization where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Axes using (Axis)
open import Substrate.Groups.S4 using (Permutation; _·_; _⁻¹; apply; invₐ; inv-r)
open import Substrate.Groups.SemidirectProduct using (Stab)

------------------------------------------------------------------------
-- The two conditions.
------------------------------------------------------------------------

-- The member-normal obligation for Stab(X) (the S₄-NormalSubgroup field over
-- Stab-Subgroup X, ∀-quantified explicitly so it composes through the
-- definitions below — same `apply`-projection reason as stab-fixes-orbit).
member-normal : Axis → Set
member-normal X = (g n : Permutation) → Stab X n → Stab X ((g · n) · (g ⁻¹))

-- Every element of Stab(X) fixes every point of the orbit of X. (g, n are
-- explicit: this is a ∀-statement applied at concrete witnesses downstream,
-- and the implicit form can't be instantiated through this abbreviation —
-- `apply`-projection inference blocks it.)
stab-fixes-orbit : Axis → Set
stab-fixes-orbit X = (g n : Permutation) → Stab X n → Stab (apply g X) n

------------------------------------------------------------------------
-- The equivalence. Both directions are the conjugation identity in one
-- algebraic move; `apply (g⁻¹)⁻¹ = apply g` reduces definitionally.
------------------------------------------------------------------------

-- ⟹  member-normal ⟹ Stab(X) fixes the orbit. Instantiate the obligation
-- at the conjugator g⁻¹: it places (g⁻¹·n·g) in Stab(X); transporting by g
-- (inv-r) reads off that n fixes apply g X.
member-normal→fixes-orbit : ∀ {X} → member-normal X → stab-fixes-orbit X
member-normal→fixes-orbit {X} mn g n sn =
  trans (sym (inv-r g (apply n (apply g X)))) (cong (apply g) (mn (g ⁻¹) n sn))

-- ⟸  Stab(X) fixing the orbit ⟹ member-normal. The conjugate (g·n·g⁻¹)
-- fixes X iff n fixes g⁻¹·X, which orbit-fixing supplies.
fixes-orbit→member-normal : ∀ {X} → stab-fixes-orbit X → member-normal X
fixes-orbit→member-normal {X} fo g n sn =
  trans (cong (apply g) (fo (g ⁻¹) n sn)) (inv-r g X)

------------------------------------------------------------------------
-- The old sufficient condition recovered: a GLOBAL fixed point makes
-- Stab(X) fix the orbit trivially (every orbit point IS X), hence normal —
-- this is exactly Subgroup.Stab-normal-when-fixed, factored through the
-- characterization. Sufficient, not necessary (see header).
------------------------------------------------------------------------

fixed→fixes-orbit :
  ∀ {X} → ((h : Permutation) → apply h X ≡ X) → stab-fixes-orbit X
fixed→fixes-orbit {X} fixed g n sn =
  trans (cong (apply n) (fixed g)) (trans sn (sym (fixed g)))

fixed→member-normal :
  ∀ {X} → ((h : Permutation) → apply h X ≡ X) → member-normal X
fixed→member-normal {X} fixed g n sn =
  fixes-orbit→member-normal {X} (fixed→fixes-orbit {X} fixed) g n sn
