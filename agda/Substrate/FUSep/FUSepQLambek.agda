{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQLambek — ⟡X8b-Lambek: THE CAPSTONE. Lambek's lemma identifies the
-- fixpoint the extruder EXTRUDES (HasFix, the Y-combinator, algebraic/initial)
-- with the TERMINAL COALGEBRA (the R-side greatest fixed point, ADD 111's
-- cyc/Stream) — via the SAME Lawvere diagonal.
--
-- THE DISSOLUTION (the deepest either/or of the arc): "is the extruder's fixpoint
-- an ALGEBRA thing (Y, fold, ℚ, least) or a COALGEBRA thing (RealTrace, unfold, R,
-- greatest)?" Lambek's answer: BOTH ARE FIXED POINTS. The structure map of the
-- terminal coalgebra is an ISO (Stream A ≅ A × Stream A), so the carrier IS the
-- fixed point of its functor; dually the initial algebra's map is an iso. And
-- (ExtruderFix + Final headers, ⟡H0-read) Lambek IS "the coalgebraic face of
-- Category.Lawvere" — the SAME diagonal/fixed-point atom behind HasFix (fix·f ≡
-- f·(fix·f), FixFromDiagonal) and behind Cantor/Gödel/Tarski/the wedge residue.
-- So HasFix and Lambek are not two fixpoints to reconcile — they are ONE Lawvere
-- fixed point, seen algebraically (Y) and coalgebraically (RealTrace).
--
-- ⟡H0 (read Final): out/into ARE the Lambek iso — lambek-out-into (≡, one way)
-- and lambek-into-out (~, coinductive: no definitional η, the round-trip is a
-- BISIMULATION). Instantiate exactly for ADD-111's Stream (the cyc carrier).
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQLambek where

open import Substrate.Foundation.Eq   using (_≡_; refl)
open import Substrate.Foundation.List using (List; [])
open import Substrate.FUSep.FUSepQCyc using (Stream; hd; tl; _~ₛ_; hd~; tl~; ~-refl; ~-sym; ~-trans; cyc; cyc-go; cyc-loop~const; cyc~const; const)

------------------------------------------------------------------------
-- THE STREAM FUNCTOR S X = A × X (the cyc/RealTrace functor). Its terminal
-- coalgebra is Stream A; the structure map is `out`, its inverse `into` (cons).
------------------------------------------------------------------------
record _×_ (A B : Set) : Set where
  constructor _,_
  field π₁ : A ; π₂ : B
open _×_ public

module _ {A : Set} where

  -- the structure map (the coalgebra) and its inverse (cons).
  out : Stream A → A × Stream A
  out s = hd s , tl s

  into : A × Stream A → Stream A
  hd (into as) = π₁ as
  tl (into as) = π₂ as

  ------------------------------------------------------------------
  -- LAMBEK'S LEMMA (Final.lambek-out-into / lambek-into-out): out and into
  -- invert — one direction ≡ (definitional), the other ~ (coinductive, no η:
  -- the round-trip IS a bisimulation). So Stream A ≅ A × Stream A: the terminal
  -- coalgebra IS a FIXED POINT of the functor. The R-side / GREATEST fixed point.
  ------------------------------------------------------------------
  lambek-out-into : (as : A × Stream A) → out (into as) ≡ as
  lambek-out-into (a , s) = refl

  lambek-into-out : (s : Stream A) → into (out s) ~ₛ s
  hd~ (lambek-into-out s) = refl
  tl~ (lambek-into-out s) = ~-refl (tl s)

  ------------------------------------------------------------------
  -- so `out` is a FIXED-POINT structure: Stream A ≅ A × Stream A, exhibiting
  -- Stream A = ν(A × −), the greatest fixed point. This is the coalgebraic fixed
  -- point the extruder's Y (HasFix) IS, via Lawvere.
  ------------------------------------------------------------------

------------------------------------------------------------------------
-- THE HINGE (Lawvere): a GUARDED self-map has a fixed point in the terminal
-- coalgebra — the coalgebraic image of HasFix (fix·f ~ f·(fix·f)). cyc IS such a
-- fixed point: it is the fixed point of the period-unfolding self-map. So the
-- extruded Y and the terminal-coalgebra fixed point are ONE Lawvere fixed point.
-- Concretely: cyc x [] is a fixed point of "prepend x" — cyc x [] ~ into (x , cyc x []).
------------------------------------------------------------------------
module _ {A : Set} (x : A) where

  -- "prepend x" — a guarded self-map on Stream A (the period-unfolding for [x]).
  prepend : Stream A → Stream A
  hd (prepend s) = x
  tl (prepend s) = s

  -- THE FIXED POINT (HasFix's fix·f ~ f·(fix·f), coalgebraically): cyc x [] is a
  -- fixed point of `prepend` — cyc x [] ~ prepend (cyc x []). The Y the extruder
  -- extrudes, realised in the terminal coalgebra as the Lambek fixed point.
  -- tl (cyc x []) = cyc-go x [] [], which is ~ cyc x [] (both ~ const x).
  tail-loops : cyc-go x [] [] ~ₛ cyc x []
  tail-loops = ~-trans (cyc-loop~const x) (~-sym (cyc~const x))

  cyc-is-fixpoint : cyc x [] ~ₛ prepend (cyc x [])
  hd~ cyc-is-fixpoint = refl
  tl~ cyc-is-fixpoint = tail-loops

  -- and it factors through the Lambek iso: cyc x [] ~ into (x , cyc x []) — the
  -- fixed point IS a point of the terminal-coalgebra fixed point (out/into).
  cyc-via-lambek : cyc x [] ~ₛ into (x , cyc x [])
  hd~ cyc-via-lambek = refl
  tl~ cyc-via-lambek = tail-loops

------------------------------------------------------------------------
-- THE ABSTRACT LAMBEK LEMMA, as an Iso record — what `out`/`into` witness for
-- ANY functor with a terminal coalgebra: the structure map is an iso (up to the
-- carrier's equality), so the carrier is a fixed point. Here the carrier equality
-- is bisimilarity ~ (the R-side / greatest-fixed-point equality).
------------------------------------------------------------------------
record LambekFix (X : Set) (FX : Set)      -- ⟦shape:7156b836 (_≈X_,struct,inv⟧
                 (_≈X_ : X → X → Set) : Set where
  field
    struct   : X → FX               -- the coalgebra structure map (out)
    inv      : FX → X               -- its inverse (into)
    out-into : (y : FX) → struct (inv y) ≡ y     -- ≡ one way
    into-out : (x : X) → inv (struct x) ≈X x     -- ≈ the other (coinductive, ~)

-- Stream A IS a LambekFix (up to bisimilarity): the terminal coalgebra as a
-- fixed point, packaged. This is the R-side / greatest fixed point of the tower.
stream-lambek : {A : Set} → LambekFix (Stream A) (A × Stream A) _~ₛ_
stream-lambek = record
  { struct = out ; inv = into
  ; out-into = lambek-out-into ; into-out = lambek-into-out }

------------------------------------------------------------------------
-- THE HINGE, stated: HasFix (fix·f ~ f·(fix·f), the extruded Y — ExtruderFix)
-- and Lambek (the terminal-coalgebra structure map is an iso) are ONE Lawvere
-- fixed point. Coalgebraically, a guarded self-map's fixed point (cyc-is-fixpoint)
-- IS the extruded Y realised in the terminal coalgebra. The ℚ side (initial
-- algebra / SN / Newman, ADD 109-110) is the DUAL Lambek fixed point (the least);
-- the R side (this module, terminal coalgebra / cyc / Diverges, ADD 111) the
-- GREATEST. Lawvere's diagonal hinges the two — the same φ a a behind FixFromDiagonal
-- and behind ana-unique. So the extruder-soundness tower IS the ℚ⊣R adjunction,
-- and its two fixed points (least ⊣ greatest) are the two faces of one Lawvere atom.
--
-- HasFixShape: the extruded fixpoint law, at the terminal coalgebra — a self-map
-- f with a fixed point p (p ~ f p). cyc-is-fixpoint witnesses it for `prepend`.
------------------------------------------------------------------------
HasFixShape : {A : Set} (f : Stream A → Stream A) (p : Stream A) → Set
HasFixShape f p = p ~ₛ f p

-- cyc realises HasFixShape in the terminal coalgebra — the Y the extruder
-- extrudes, as the Lambek/Lawvere fixed point of the greatest-fixed-point carrier.
cyc-hasfix : {A : Set} (x : A) → HasFixShape (prepend x) (cyc x [])
cyc-hasfix x = cyc-is-fixpoint x
