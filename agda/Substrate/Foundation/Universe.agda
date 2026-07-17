{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Foundation.Universe — a small Tarski universe.
--
-- ⟡rc-tarski-universe (⟡rerank2-floor-dissolve): "the category of all Sets"
-- is NOT a genuine Set₁ floor. You cannot enumerate all Sets — but neither
-- can you enumerate all reals, and the substrate represents THOSE by
-- continued-fraction streams (RealTrace = νΦ). The honest object-universe is
-- REPRESENTED GENERATIVELY: a Set₀ type `U` of type-CODES + a decoder
-- `El : U → Set`, closed under exactly the operations the morphisms need
-- (here: function space, so `El (a ⌜⇒⌝ b) = El a → El b`). This sidesteps
-- Cantor entirely — you never code a function space into ℕ; the universe
-- GENERATES it as a `⌜⇒⌝` code. Modeled on the in-repo
-- `ExtrudeIOMonadRecord.Code/El` (closed under IO), with the constructor set
-- swapped to ⊤/Bool/×/⇒. `El` is strictly-positive (structural on U), so
-- --safe --without-K accepts it. This is the Set₀ carrier for Set-Category,
-- Rel-Allegory, Rel-TwoCategory (⟡pyrig-object-carrier, realized).
------------------------------------------------------------------------

module Substrate.Foundation.Universe where

open import Substrate.Foundation.Unit    using (⊤)
open import Substrate.Foundation.Bool    using (Bool)
open import Substrate.Foundation.Product using (_×_)

infixr 7 _⌜×⌝_
infixr 6 _⌜⇒⌝_

data U : Set where
  ⌜⊤⌝    : U
  ⌜bool⌝ : U
  _⌜×⌝_  : U → U → U
  _⌜⇒⌝_  : U → U → U

El : U → Set
El ⌜⊤⌝       = ⊤
El ⌜bool⌝    = Bool
El (a ⌜×⌝ b) = El a × El b
El (a ⌜⇒⌝ b) = El a → El b
