------------------------------------------------------------------------
-- Eliza.Transducer
--
-- The per-symbol transducer interface. Every layer of the pipeline
-- (Router, Manifold-walker, OrbitMap) is a Transducer between two
-- alphabets, lifted to a Word transformer by mapping.
--
-- Two flavours:
--
--   * `Transducer α β` (stateless): α → β. Lifts to Word α → Word β
--     via Word.map. The Router and the Chamber→Orbit map are stateless.
--
--   * `StatefulTransducer α S β` (parametric coalgebra step): the
--     `Substrate.Category.Coalgebra` ParamEndomap pattern. Given a
--     state S and input α, produces a new state and an output β. The
--     Manifold-walker is a StatefulTransducer Gen Chamber Chamber
--     (where the new chamber is both the next state AND the output).
--
-- These two patterns are what compose the eliza pipeline. The Engine
-- chains them: char ─Router→ gen ─Walker→ chamber ─OrbitMap→ orbit.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Transducer where

open import Eliza.Prelude using (_×_; _,_; fst; snd)
open import Eliza.Word    using (Word; []; _∷_; map)

------------------------------------------------------------------------
-- 1. Stateless transducer = function on symbols. Lifts to Word by map.
------------------------------------------------------------------------

Transducer : Set → Set → Set
Transducer α β = α → β

run : {α β : Set} → Transducer α β → Word α → Word β
run f = map f

------------------------------------------------------------------------
-- 2. Stateful transducer = ParamEndomap-style step. The substrate's
-- coalgebra primitive, specialised to per-symbol consumption.
--
-- step : input × state → state × output
--
-- For our manifold walker the state IS the chamber and the output IS
-- the same chamber after applying the generator. The decomposition
-- between state and output is kept general to support layers where
-- they differ (e.g., the Recorder, where state is the database and
-- output is per-turn diagnostics).
------------------------------------------------------------------------

record StatefulTransducer (α S β : Set) : Set where
  field
    s₀   : S
    step : S → α → S × β

------------------------------------------------------------------------
-- 3. Running a StatefulTransducer over a Word produces a final state
-- and a Word of outputs. The fundamental fold the pipeline uses.
------------------------------------------------------------------------

runStateful : {α S β : Set} → StatefulTransducer α S β →
              Word α → S × Word β
runStateful {α} {S} {β} T = go (StatefulTransducer.s₀ T)
  where
    go : S → Word α → S × Word β
    go s []       = s , []
    go s (x ∷ xs) with StatefulTransducer.step T s x
    ... | s' , y  with go s' xs
    ...   | s'' , ys = s'' , y ∷ ys

------------------------------------------------------------------------
-- 4. Composition. Two transducers chain to give one. This is the
-- algebraic content of "layer composition" in the Engine.
------------------------------------------------------------------------

_∘T_ : {α β γ : Set} → Transducer β γ → Transducer α β → Transducer α γ
(g ∘T f) x = g (f x)
