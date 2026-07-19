------------------------------------------------------------------------
-- Substrate.WitnessTower.FactorisationApex
--
-- ◆AI-3''' — the COMMON-STRUCTURE APEX the whole sign/coord arc was building
-- toward. Two session constructions read the SAME semidirect factorisation of
-- S₄ but OPPOSITE halves:
--
--     factorisation :  σ ≈ embed (v-for σ) · s-for σ      (every S₄ elt = V₄ · Stab)
--
--   · coord (ParityCoordIsoApex, ◆AI-2b) reads the V₄ / v-for half — the
--     Z/2×Z/2 coordinate of the V₄ factor.
--   · sign-of (SignStabTotal, ◆AI-3) reads the Stab / s-for half — sign factors
--     through s-for, constant on V₄-cosets.
--
-- So the either/or "is this arc about sign, or about the V₄-coordinate iso?"
-- resolves: BOTH — they are the TWO COORDINATES of S₄ ≅ V₄ ⋊ Stab, read off the
-- one factorisation. sign = the Stab-coordinate; coord = the V₄-coordinate.
--
-- This apex is a WIRED TERM (read-parts), not a prose observation: it splits σ
-- and reads both halves, with the complementarity proven — the sign-half is
-- exactly sign-of σ (sign sees ONLY the Stab factor), and the V₄-half is the
-- coord of v-for σ (the V₄ factor). The two halves are independent readings of
-- the one decomposition.
--
-- CO-APEX ABOVE (◆AI-3'''-cite): the full recovery iso this apex projects from
-- ALREADY EXISTS in the repo — Cocycles.V4Signature.S4Iso.TotalSpace≃S₄-bijection
-- : TotalSpace ≃ S₄, where TotalSpace = OrbitKey × V₄ (the 24 = 6 Stab-keys × 4
-- V₄, "the 24 ARE S₄" under V₄ ⋊ S₃ ≅ S₄). Its `from : Permutation → OrbitKey ×
-- V₄` recovers the FULL factorisation data. read-parts here is the LOSSY
-- COORDINATE-READING of that recovery: it applies coord to the V₄ component and
-- sign-of (one bit) to the Stab/orbit-key component. So read-parts is NOT an iso
-- (sign discards most of the Stab data) — it is the sign/coord PROJECTION of the
-- pre-existing full bijection. (Cited, not wired: TotalSpace is a Σ-type; the
-- session code stays existential-free, so this connection is stated in prose
-- rather than threaded as a Σ-typed term.)
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FactorisationApex where

open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Groups.S4 using (Permutation)
open import Substrate.Groups.V4 using (V₄)
open import Substrate.Groups.SemidirectProduct.V using (v-for)
open import Substrate.Groups.SemidirectProduct.S using (s-for)
open import Substrate.WitnessTower.ParityCoordIsoApex using (coord)
open import Substrate.WitnessTower.SignStabTotal
  using (sign-of; sign-factors-through-s-for; sign-of-stable)

------------------------------------------------------------------------
-- THE APEX: read both coordinates of σ's semidirect factorisation. The V₄
-- coordinate (coord ∘ v-for) and the sign/Stab coordinate (sign-of ∘ s-for).
------------------------------------------------------------------------

read-parts : Permutation → (Bool × Bool) × Bool
read-parts σ = (coord (v-for σ) , sign-of (s-for σ))

-- the two projections, named:
v4-coordinate : Permutation → Bool × Bool
v4-coordinate σ = coord (v-for σ)

sign-coordinate : Permutation → Bool
sign-coordinate σ = sign-of (s-for σ)

------------------------------------------------------------------------
-- COMPLEMENTARITY. The two coordinates are the two halves, each depending only
-- on its own factor.
------------------------------------------------------------------------

-- (1) the SIGN coordinate recovers the full sign of σ: sign reads ONLY the Stab
-- half, so pulling it from s-for σ loses nothing. sign-of (s-for σ) ≡ sign-of σ.
-- (This is sign-factors-through-s-for read on the apex: the Stab-coordinate IS
-- the sign.)
sign-coordinate-is-sign : (σ : Permutation) → sign-coordinate σ ≡ sign-of σ
sign-coordinate-is-sign σ = sym (sign-factors-through-s-for σ)

-- (2) the sign coordinate is STABLE under re-anchoring (s-for idempotent-on-
-- sign): the V₄ freedom is fully quotiented — re-stripping V₄ changes nothing.
sign-coordinate-stable :
  (σ : Permutation) → sign-coordinate (s-for σ) ≡ sign-coordinate σ
sign-coordinate-stable σ = sym (sign-of-stable σ)

------------------------------------------------------------------------
-- THE READING, restated as the resolution of the either/or: read-parts σ pairs
-- the V₄-coordinate (coord of the v-for factor) with the sign (= the s-for
-- factor's parity). sign and the V₄-coord-iso are one decomposition, two halves.
-- read-parts is definitionally (v4-coordinate σ , sign-coordinate σ).
------------------------------------------------------------------------

read-parts-is-both :
  (σ : Permutation) → read-parts σ ≡ (v4-coordinate σ , sign-coordinate σ)
read-parts-is-both σ = refl
