------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Warrant
--
-- The provenance grades (el-atlas §0): every claim carries an epistemic
-- grade — a WARRANT — recording HOW it is justified —
--
--   W  witnessed     — derived and confirmed; a witness is exhibited (BHK)
--   S  synthesis     — faithful assembly of witnessed pieces, where the
--                      assembly itself is new
--   C  conjecture    — proposed, with tests; not yet witnessed
--   U  undetermined  — no witness; neither asserted nor denied (§15)
--
-- (The type is named `Warrant` — warranted-assertibility — rather than
-- `Grade`, which the substrate already uses for the Clifford-algebra degree
-- record. The constructors keep el-atlas's [W]/[S]/[C] letters.)
--
-- These form a strength chain  W ⊒ S ⊒ C ⊒ U,  the epistemic shadow of the
-- shared realizability charter (constructible → reachable → observable →
-- coverable; Substrate.Realizability.Charter): the warrant records how far
-- up that ladder a claim's justification reaches.
--
-- A DERIVED claim is graded by its WEAKEST premise — the demotion
-- discipline: "claims beyond the witnessed part are downgraded to [C]"
-- (§0; spec line 1310). That combination is the meet `_⊓w_` (min in the
-- strength chain): one cannot be more certain than one's least-certain
-- input. The semilattice laws are in .Properties; warrants riding under the
-- verdict joiners are in `Substrate.Logic.Evidence.Graded`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Warrant where

data Warrant : Set where
  W S C U : Warrant   -- witnessed ⊒ synthesis ⊒ conjecture ⊒ undetermined

------------------------------------------------------------------------
-- Combination: a derived claim is as strong as its WEAKEST premise. With
-- W as the meet identity (a witnessed premise never weakens the result)
-- and U absorbing (any unwitnessed premise leaves the whole undetermined),
-- the two extreme rows are uniform in the second argument.
------------------------------------------------------------------------

infixr 7 _⊓w_
_⊓w_ : Warrant → Warrant → Warrant
W ⊓w y = y
S ⊓w W = S
S ⊓w S = S
S ⊓w C = C
S ⊓w U = U
C ⊓w W = C
C ⊓w S = C
C ⊓w C = C
C ⊓w U = U
U ⊓w y = U

-- bounds of the strength chain: W strongest (meet identity), U weakest
-- (meet zero / absorbing).
⊤w ⊥w : Warrant
⊤w = W
⊥w = U
