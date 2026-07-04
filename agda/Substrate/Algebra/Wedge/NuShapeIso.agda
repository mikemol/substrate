{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NuShapeIso — ⟡nu-shape-iso: the up-to-shape iso of the
-- ν-half (ADD 160) made precise. RealTrace is the ℕ-STREAM of CF digits = the SHAPE
-- (the quotient stream) of the νΦ-step wedge-coalgebra unfold. So the ℕ-stream IS
-- the quotient stream: shape(νΦ-step) lands in RealTrace via `ana`, CANONICALLY
-- (unique by ana-unique). This is the up-to-shape statement — NOT νΦ-step ≅ RealTrace
-- (shape forgets the positional fill b + witnesses, exactly as Wedge.Shape does
-- finitely); it is shape(νΦ-step) = RealTrace, the ℕ-stream = the quotient stream.
--
-- The finite mirror (Wedge.Shape, ADD 149): shape (Trace) = List (C D), the quotient
-- SEQUENCE. Here, coinductively: shape (νΦ-step over ℕ-div) = RealTrace, the quotient
-- STREAM. Same shape-projection, finite (List) ↦ infinite (RealTrace stream).
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NuShapeIso where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge using (DivStr; C; z; quot; rem; ℕ-div)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg; divide)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana; ana-head; ana-tail; ana-unique)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)

------------------------------------------------------------------------
-- ① THE QUOTIENT-COALGEBRA over ℕ-div. A wedge-coalgebra's unfold, at state (a,b),
-- produces a Wedge whose quot : ℕ (the CF digit) and residual rem. The SHAPE reads
-- the quotient and recurses on (b, rem) — a Coalg (ℕ × ℕ) = St → ℕ × St. This is
-- the ℕ-stream functor coalgebra whose ana IS the shape stream.
------------------------------------------------------------------------
QState : Set
QState = C ℕ-div × C ℕ-div            -- the (a, b) unfold state (both ℕ for ℕ-div)

quotient-coalg : WedgeCoalg ℕ-div → Coalg QState
quotient-coalg co (a , b) =
  quot (divide co a b) ,               -- emit the CF digit (the quotient)
  (b , rem (divide co a b))            -- recurse: next state (b, residual)

------------------------------------------------------------------------
-- ② THE SHAPE STREAM = ana of the quotient-coalgebra. This is the SHAPE of the
-- νΦ-step unfold, realized AS a RealTrace (the ℕ-stream of quotients). shape(νΦ-step)
-- = this RealTrace.
------------------------------------------------------------------------
shape-stream : WedgeCoalg ℕ-div → QState → RealTrace
shape-stream co = ana (quotient-coalg co)

------------------------------------------------------------------------
-- ③ THE OBSERVABLE ISO CONTENT: head (shape-stream) = the quotient (the CF digit IS
-- the wedge quotient), and tail (shape-stream) = shape-stream of the residual — the
-- coinductive step. These ARE the ana head/tail squares, so the shape stream's
-- observations are exactly the quotient stream.
------------------------------------------------------------------------
-- the first CF digit IS the first wedge quotient (the shape's head = quot):
head-is-quot : (co : WedgeCoalg ℕ-div) (a b : C ℕ-div) →
               head (shape-stream co (a , b)) ≡ quot (divide co a b)
head-is-quot co a b = ana-head (quotient-coalg co) (a , b)

-- the tail IS the shape stream of the residual state (b, rem) — the coinductive
-- unfold of the shape (the quotient stream continues on the residual):
tail-is-residual-shape : (co : WedgeCoalg ℕ-div) (a b : C ℕ-div) →
    tail (shape-stream co (a , b)) ≡ shape-stream co (b , rem (divide co a b))
tail-is-residual-shape co a b = ana-tail (quotient-coalg co) (a , b)

------------------------------------------------------------------------
-- ④ CANONICITY (ana-unique): the shape stream is THE UNIQUE coalgebra morphism from
-- the quotient-coalgebra into RealTrace. So RealTrace is the TERMINAL home of the
-- quotient stream — ANY map h agreeing with the quotient-coalgebra's head/tail
-- squares IS bisimilar to the shape stream. This is the up-to-shape iso's uniqueness.
------------------------------------------------------------------------
shape-is-canonical : (co : WedgeCoalg ℕ-div) (h : QState → RealTrace)
    → (∀ s → head (h s) ≡ proj₁ (quotient-coalg co s))
    → (∀ s → tail (h s) ≡ h (proj₂ (quotient-coalg co s)))
    → ∀ s → h s ~ shape-stream co s
shape-is-canonical co = ana-unique (quotient-coalg co)

-- the shape stream is self-bisimilar (the ν endpoint's reflexivity):
shape-self : (co : WedgeCoalg ℕ-div) (s : QState) → shape-stream co s ~ shape-stream co s
shape-self co s = ~-refl (shape-stream co s)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the up-to-shape iso, HONESTLY): RealTrace IS the
-- SHAPE of the νΦ-step wedge-coalgebra unfold — the ℕ-stream of CF digits = the
-- quotient stream. The quotient-coalgebra (from divide: emit quot, recurse on the
-- residual) has ana into RealTrace as its shape stream, with head = quot (the CF
-- digit IS the wedge quotient) and tail = the residual's shape, and by ana-unique
-- this is THE canonical map. So shape(νΦ-step) = RealTrace. This is the up-to-shape
-- statement — NOT νΦ-step ≅ RealTrace (shape forgets the positional fill b, exactly
-- as Wedge.Shape does finitely: shape(Trace) = List (C D) drops fill). The finite/
-- infinite mirror: shape(μΦ-step = Trace) = List (quotient SEQUENCE); shape(νΦ-step)
-- = RealTrace (quotient STREAM). The "RealTrace vs νΦ-step" either/or dissolves: they
-- agree UP TO SHAPE (the quotient stream), the fill being the scoped difference. The
-- FULL νΦ-step (with fill) is the wedge-coalgebra (ADD 160); RealTrace is its shape.
------------------------------------------------------------------------
