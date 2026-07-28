------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.Injective
--
-- Bijection-helper lemmas: σ-injective and Axis-constructor
-- distinctness lemmas (C≢D, S≢D, W≢D, C≢S, C≢W, S≢W, and reverses).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.Injective where

open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Groups.Symmetric.Injective Axis

------------------------------------------------------------------------
-- apply σ is injective.
--
-- Ⓓ: σ-injective is the GENERIC Symmetric.σ-injective — Symmetric is
-- instantiated at Axis and re-exported by S4, and the local proof here was
-- byte-identical. Imported + re-exported; the Axis-distinctness lemmas below
-- are this module's own content.
------------------------------------------------------------------------

-- Axis-constructor distinctness (nine obvious lemmas).
------------------------------------------------------------------------

C≢D : C ≡ D → ⊥
C≢D ()
S≢D : S ≡ D → ⊥
S≢D ()
W≢D : W ≡ D → ⊥
W≢D ()
C≢S : C ≡ S → ⊥
C≢S ()
C≢W : C ≡ W → ⊥
C≢W ()
S≢W : S ≡ W → ⊥
S≢W ()
S≢C : S ≡ C → ⊥
S≢C ()
W≢C : W ≡ C → ⊥
W≢C ()
W≢S : W ≡ S → ⊥
W≢S ()
