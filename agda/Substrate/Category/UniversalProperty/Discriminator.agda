------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Discriminator
--
-- GROUNDWORK for "make every bridge commute" (user, 2026-06-13): laying down the
-- interface is not claiming coherence the structure lacks — it is POSTULATING the
-- obligation, which the next arc discharges by filling the holes. Substrate-honest
-- form: a record whose FIELDS are the obligations (zero `postulate`s; an unfilled
-- bridge = no instance yet, a hole — not a falsehood).
--
-- The mechanism the AI proposal reached for, stated correctly: a (shape, cochain)
-- pair that is FAITHFUL — i.e. pins the element — turns "agrees on the
-- discriminator" into "equal", so parallel maps into it commute POINTWISE (no
-- funext). The CF/wedge instance is `shape` (the invariant) + the determinant sign
-- (`DetSign`, the ℤ/2 cochain); `faithful` there is trace shape-injectivity (det is
-- a function of shape, so it rides along) — the FIRST hole. Heterogeneous bridges
-- (Markov/Lens/Poly) are further holes; some may admit no faithful discriminator —
-- that is a NEGATIVE result, equally a deliverable.
--
-- What is PROVED here (the entailment, unconditional): faithful + agreement ⟹
-- pointwise commutativity. What is DEFERRED (the holes): the `Discriminated`
-- instances and the per-bridge agreement proofs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Discriminator where

open import Substrate.Foundation.Eq      using (_≡_)
open import Substrate.Foundation.Product using (_×_; _,_)

------------------------------------------------------------------------
-- A discriminated structure: a carrier with an invariant (Sh, e.g. CF shape) and a
-- cochain (Dt, e.g. the ℤ/2 determinant sign) whose PAIR is FAITHFUL — it pins the
-- element. `faithful` is the obligation each instance must discharge.
------------------------------------------------------------------------

record Discriminated (A : Set) : Set₁ where
  field
    Sh  : Set
    sh  : A → Sh
    Dt  : Set
    dt  : A → Dt
    faithful : (x y : A) → sh x ≡ sh y → dt x ≡ dt y → x ≡ y

open Discriminated public

------------------------------------------------------------------------
-- THE ENTAILMENT (unconditional): two parallel maps into a discriminated target
-- that AGREE on the discriminator (pointwise on sh and dt) are pointwise EQUAL.
-- This is "the square commutes", derived from `faithful` — no funext, no postulate.
-- Filling a diagram = providing the `Discriminated` targets + these agreements.
------------------------------------------------------------------------

module _ {A C : Set} (DC : Discriminated C) where

  AgreeDisc : (g h : A → C) → Set
  AgreeDisc g h =
    ((t : A) → sh DC (g t) ≡ sh DC (h t)) × ((t : A) → dt DC (g t) ≡ dt DC (h t))

  commute-via-discriminator :
    (g h : A → C) → AgreeDisc g h → (t : A) → g t ≡ h t
  commute-via-discriminator g h (sh-ag , dt-ag) t =
    faithful DC (g t) (h t) (sh-ag t) (dt-ag t)
