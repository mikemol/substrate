------------------------------------------------------------------------
-- Substrate.Category.Lawvere
--
-- LAWVERE'S DIAGONAL (FIXED-POINT) THEOREM — the carrier-generic atom behind
-- Cantor, Gödel, Tarski, Turing, and the substrate's wedge residue. This is
-- the common substructure of three things WitnessTower.Diagonal found equal
-- at F₂ (the diagonal, the grade ★'s fixed-point-freeness, the cone apex/base
-- distinction): they are all the SET INSTANCE of this one theorem.
--
-- THE ATOM, generic. `FixedPointFree V` is a value type V with an endo δ that
-- never agrees with its input (δ v ≢ v). The F₂ instance is δ = (𝟙 +_), whose
-- δ-free is exactly WitnessTower.Diagonal.flip-disagrees; the wedge supplies
-- such a δ as its RESIDUE (translate by the distinction). Making that δ
-- CANONICAL over an arbitrary carrier — the certified residue r<b — is the
-- keystone (Algebra.Wedge scopes r<b out for now); FixedPointFree is the
-- interface that the keystone will populate generically, so every wedge-
-- carrier inherits the diagonal argument at once.
--
-- THE THEOREM, BOTH DIRECTIONS.
--   * POSITIVE (lawvere-fixed-point): if a point a : A is SURJECTIVE onto Aᴬ→V
--     (every map g : A → V is some point's row φ a), then every endo f : V → V
--     has a fixed point. A reflexive object forces fixed points.
--   * CONTRAPOSITIVE (diag-not-in-family): if V carries a fixed-point-free endo
--     then NO such point-surjection exists — the diagonal twist witnesses a
--     missed map. This is the generic Cantor/diagonal.
-- Cantor = (V = Bool/F₂, diagonal); Gödel/Tarski = (V = truth values, M = the
-- provability/satisfaction matrix); the substrate's cell ★ = (V = F₂, δ = the
-- residue). One theorem, every diagonal — and every self-reference.
--
-- RELATION TO Category.UniversalProperty.FixedPoint (it is NOT unrelated — the
-- two files are the two halves of THIS theorem). That module exhibits
-- (ι : UPArrow² → UPArrow, promote : UPArrow → UPArrow²): the meta level (the
-- arrow-of-arrows, the exponential-like UPArrow²) retracts into the base. That
-- section/retraction IS a reflexive-object structure = the HYPOTHESIS of
-- `lawvere-fixed-point`; so "the tower IS its own fixed point" is the POSITIVE
-- Lawvere conclusion, and this module's diagonal is its contrapositive. The
-- substrate's METACIRCULARITY (self-reference, the UP-tower fixed point) and its
-- DIAGONALIZATION (Cantor / the wedge residue) are therefore ONE structure,
-- hinged by Lawvere. (Wiring (ι, promote) as a literal PointSurjective instance
-- needs the UPArrow-as-exponential identification + its equality — deferred;
-- the relationship is exhibited here, the literal instance is the next bridge.)
--
-- ARE THEY INVERSE? (FixedPoint = ι/promote vs this diagonal.) NO, and the
-- proof is the residue. collapse (diag / ι) and lift (promote-row / promote)
-- compose to δ, not id (diag-promote); a true inverse would force δ to have a
-- fixed point (diag-promote-not-id), refuted by δ-free. So they are NOT an
-- isomorphism — they are a Free⊣Forgetful-style ADJOINT pair whose (co)unit
-- defect is exactly the wedge residue δ. "Inverse up to the residue" IS the
-- wedge equation a = recon q b r; the residue is the adjoint correction
-- (keystone #1). The correct categorical name is adjunction, not inverse.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Lawvere where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_)

------------------------------------------------------------------------
-- 1. THE ATOM. A fixed-point-free endomap on values: the residue that
--    never equals its source. Carrier-generic flip-disagrees.
------------------------------------------------------------------------

record FixedPointFree (V : Set) : Set where
  field
    δ      : V → V
    δ-free : (v : V) → δ v ≡ v → ⊥

-- (not opened publicly: InvolutiveResidue below also has a field δ; we keep
-- the projections qualified to avoid an overload clash.)

------------------------------------------------------------------------
-- 2. LAWVERE'S DIAGONAL THEOREM (Set instance). The diagonal twist of a
--    family is absent from the family — the generic Cantor argument.
------------------------------------------------------------------------

module _ {I V : Set} (fpf : FixedPointFree V) where

  -- the diagonal twist of a family of maps: at i, flip the i-th map's i-th
  -- value. (For I = positions, V = bits, this is Cantor's anti-diagonal.)
  diag : (I → I → V) → (I → V)
  diag M i = FixedPointFree.δ fpf (M i i)

  -- the diagonal twist is in NO row: it differs from every M i (at i).
  -- So no family I → (I → V) is onto — the generic diagonalization.
  diag-not-in-family : (M : I → I → V) (i : I) → diag M ≡ M i → ⊥
  diag-not-in-family M i eq = FixedPointFree.δ-free fpf (M i i) (cong (λ f → f i) eq)

  -- ARE diag (collapse, meta→base = FixedPoint.ι) and a lift (base→meta =
  -- FixedPoint.promote) INVERSE? No — and the residue is exactly why.
  -- `promote-row` lifts a row to a square (constant in the diagonal-free slot).
  promote-row : (I → V) → (I → I → V)
  promote-row g = λ _ j → g j

  -- the composite diag ∘ promote-row is NOT the identity: it is δ ∘ g. The
  -- DEFECT from identity is precisely the residue δ — collapse and lift are
  -- inverse UP TO δ, never on the nose.
  diag-promote : (g : I → V) (i : I) → diag (promote-row g) i ≡ FixedPointFree.δ fpf (g i)
  diag-promote g i = refl

  -- so the lift is NOT a section of the collapse (no true inverse): a genuine
  -- diag ∘ promote = id would force δ to fix every value, refuted by δ-free.
  -- The failure of invertibility IS the diagonal. This is the keystone shape:
  -- the residue is the adjoint correction measuring the gap from inverse, i.e.
  -- the r in the wedge a = recon q b r — "inverse up to residue".
  diag-promote-not-id : (g : I → V) (i : I) → diag (promote-row g) i ≡ g i → ⊥
  diag-promote-not-id g i eq = FixedPointFree.δ-free fpf (g i) eq

------------------------------------------------------------------------
-- 3. LAWVERE, POSITIVE DIRECTION. A point-surjection forces fixed points —
--    the reflexive-object half (the hypothesis FixedPoint.agda's (ι, promote)
--    realises for UPCategory). Dual to diag-not-in-family.
------------------------------------------------------------------------

module _ {A V : Set} where

  -- A is point-surjective onto (A → V) via φ: every map g is some point's row.
  PointSurjective : (A → A → V) → Set
  PointSurjective φ = (g : A → V) → Σ A (λ a → φ a ≡ g)

  -- a point-surjection ⟹ every endo of V has a fixed point. The diagonal of
  -- "do φ then f" is represented by a point whose value f fixes.
  lawvere-fixed-point :
    (φ : A → A → V) → PointSurjective φ → (f : V → V) → Σ V (λ v → f v ≡ v)
  lawvere-fixed-point φ surj f with surj (λ a → f (φ a a))
  ... | (a , p) = φ a a , sym (cong (λ h → h a) p)

------------------------------------------------------------------------
-- 4. THE THING SEEN FROM BOTH DIRECTIONS — the graded flip. promote and diag
--    are not inverse (round-trip = δ, §2). But when δ is an INVOLUTION
--    (δ² = id) — a fixed-point-free FLIP — the round-trip is its OWN inverse:
--    ^-1^-1 = id. The object containing both ends is the Z/2 the involution
--    generates: degree 1 = δ (the FLIP = Lawvere's diagonal); degree 0 = δ² =
--    id (the RETURN = FixedPoint's reflexive fixed point). One involution,
--    seen from both directions — the thing that contains the two ends.
--
--    WHY THIS IS LEM-FAITHFUL IN A CONSTRUCTIVE SHOP (user). Classical Cantor
--    flips with ¬ and leans on ¬¬P = P — a LEM-equivalent axiom. Here the flip
--    is δ, and δ² = id is a GREEN THEOREM (δ-invol), not an axiom — the
--    constructive avatar of double-negation-elimination, earned exactly on the
--    decidable carrier (F₂, where the residue 𝟙 +_ is provably involutive). So
--    we get the BEHAVIOUR of the classical diagonal (flip disagrees, flip-flip
--    returns) WITHOUT LEM: the involution earns constructively what LEM
--    postulates. The graded flip is double-negation made into a theorem.
------------------------------------------------------------------------

-- a residue that is a fixed-point-free INVOLUTION: the constructive flip.
record InvolutiveResidue (V : Set) : Set where
  field
    δ       : V → V
    δ-free  : (v : V) → δ v ≡ v → ⊥
    δ-invol : (v : V) → δ (δ v) ≡ v

  -- the fixed-point-free endo underneath, so diag / the diagonal apply as is.
  asFixedPointFree : FixedPointFree V
  asFixedPointFree = record { δ = δ ; δ-free = δ-free }

module _ {I V : Set} (ir : InvolutiveResidue V) where

  fpf : FixedPointFree V
  fpf = InvolutiveResidue.asFixedPointFree ir

  -- the collapse∘lift round-trip on rows (diag ∘ promote-row of §2 = δ ∘ g).
  round-trip : (I → V) → (I → V)
  round-trip g = diag fpf (promote-row fpf g)

  -- ^-1^-1 = id : the round-trip is its OWN inverse. promote/diag are not
  -- inverse, but applying the round-trip TWICE returns the identity — the
  -- graded flip = the constructive double-negation (δ² = id, green).
  round-trip-involution : (g : I → V) (i : I) → round-trip (round-trip g) i ≡ g i
  round-trip-involution g i = InvolutiveResidue.δ-invol ir (g i)

  -- the two grades never coincide: degree 1 (flip) ≠ degree 0 (return) at every
  -- value — the flip and the return are genuinely the two ends of the Z/2.
  round-trip-no-fixpoint : (g : I → V) (i : I) → round-trip g i ≡ g i → ⊥
  round-trip-no-fixpoint g i eq = InvolutiveResidue.δ-free ir (g i) eq

------------------------------------------------------------------------
-- 5. TWO FLIPS MAKE A V₄ — the first Klein four (user). A single graded flip
--    is Z/2 (§4). TWO COMMUTING flips generate V₄ = Z/2 × Z/2:
--    {id, δ₁, δ₂, δ₁∘δ₂}. The crux is that the COMPOSITE of two commuting
--    involutions is again an involution (δ₁₂-inv), so the set CLOSES — Klein
--    four. Instantiated at V = F₂² (the tetrahedron's 4 vertices), δ₁/δ₂ are
--    the two coordinate translations: this is the first V₄ that manifests in
--    the witness tower (rung 3→4, WitnessTower.V4Seam). The three nonidentity
--    elements {δ₁, δ₂, δ₁₂} are the three involutions, each generating a Z/2 —
--    the "shared V₂" by which two V₄'s overlap (a common flip). S₃ = Aut(V₄)
--    permutes the three. (Literal iso to the Coxeter-backed V₄ / V4Seam's
--    klein-pairs, and the F₂² instance with its freeness, are the next bridge.)
------------------------------------------------------------------------

record CommutingInvolutions (V : Set) : Set where
  field
    δ₁ δ₂   : V → V
    δ₁-inv  : (v : V) → δ₁ (δ₁ v) ≡ v
    δ₂-inv  : (v : V) → δ₂ (δ₂ v) ≡ v
    commute : (v : V) → δ₂ (δ₁ v) ≡ δ₁ (δ₂ v)

  -- the third involution: the composite flip — the "both" element of V₄.
  δ₁₂ : V → V
  δ₁₂ v = δ₁ (δ₂ v)

  -- the composite of two commuting involutions is itself an involution, so
  -- {id, δ₁, δ₂, δ₁₂} closes under composition — Klein four (V₄).
  δ₁₂-inv : (v : V) → δ₁₂ (δ₁₂ v) ≡ v
  δ₁₂-inv v =
    trans (cong δ₁ (commute (δ₂ v)))
    (trans (cong (λ w → δ₁ (δ₁ w)) (δ₂-inv v))
           (δ₁-inv v))
