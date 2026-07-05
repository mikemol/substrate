------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.V4
--
-- The V₄ residue carried by ComposedReference's action algebra.
--
-- Ⓒ.v4 (2026-07-05): this WAS a local `data V₄` — the comment claimed it was
-- "kept local to keep this primitive dependency-light (no group-axiom
-- infrastructure needed here)", but that residue is a genuine V₄ GROUP element
-- (the compensating σ) produced elsewhere by the group operation; a private
-- carrier meant those residues could not interoperate across subsystems. It now
-- RE-EXPORTS the canonical Groups.V4 carrier, so the residue IS the one V₄
-- (dependents open it unchanged — constructors e α β γ preserved).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.V4 where

open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ) public
