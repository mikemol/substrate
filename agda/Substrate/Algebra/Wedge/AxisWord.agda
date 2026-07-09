------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord
--
-- THE HONEST (NEVER-ANNIHILATE) GRADED WEDGE OVER A FINITE AXIS SET — the
-- common structure of which an exterior algebra Λ(V) and a k-d tree are the
-- two one-sided FORGETS.
--
-- Take k axes (Fin k) as the alphabet. A word `Vec (Fin k) n` is a length-n
-- (= grade-n) sequence of axis choices; the wedge product is concatenation
-- (Algebra.Wedge.Product.vec-product), degrees add, and — crucially — IT
-- NEVER ANNIHILATES. Where the exterior algebra writes `eᵢ ∧ eᵢ = 0`, the
-- honest wedge writes the genuine grade-2 word `i ∷ i ∷ []` and ACKNOWLEDGES
-- THE RESIDUE: the repeated axis bumps the per-axis multiplicity (`count`).
--
-- The exterior "0" is not a law here — it is a FORGETFUL PROJECTION that
-- throws the multiplicity-residue away (sends every word with a repeated
-- axis to the zero object, capping each axis at one use). The k-d tree is
-- the COMPLEMENTARY forget: it keeps the multiplicity (the refinement depth
-- along each axis = how many times the cyclic schedule `depth mod k` revisits
-- that axis) but uses the trivial reorder cocycle (a fixed axis schedule =
-- Morton/Z-order, no sign). The honest wedge keeps BOTH residues; exterior
-- forgets the multiplicity (keeps the sign), the k-d tree forgets the sign
-- (keeps the multiplicity). See [[project_commuting_sphere]] #3/#4/#6.
--
-- THE RESIDUE IS THE PATCH. We never transport (no `subst`) along an
-- equality to coerce one reading into another; the wedge GENERATES the
-- correction. The patch from the exterior basis element (one use per axis) to
-- the honest q-fold word is the residue the wedge sheds, and its size along
-- axis i is exactly q — the wedge QUOTIENT (Algebra.Wedge.power-replicate:
-- q copies = the q-deep ∧-term). So the multiplicity exterior forgets, the
-- k-d depth keeps, and the wedge quotient are one number, and the equation
-- that says so (`mult-of-power`) IS the patch. (quote = quotient = grade.)
--
-- This slice founds the lossless carrier + the multiplicity residue + the
-- quotient=multiplicity patch. The reorder/sign cocycle (the OTHER residue,
-- the one exterior keeps and the k-d tree forgets) is the next brick.
--
-- LAYER (Dent §3/§8, scratch/dent_system_primer.md): this is the CARRIER
-- wedge — free, it NEVER annihilates (`i ∧ i = i ∷ i ∷ []`, count 2). The
-- exterior `a ∧ a = 0` is NOT a law here; it is the DETECTOR reading — a
-- measurement over these terms (self-pairing forces no new distinction). The
-- two layers are bridged by a grade homomorphism whose kernel is exactly the
-- retained-but-non-distinguishing content (e.g. self-pairings). `count` is a
-- carrier multiplicity (it records), NOT the detector grade (which measures);
-- the detector grade map + its injectivity-on-distinctions (faithfulness, A2)
-- is the next brick, and needs the alphabet to carry the discriminator.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; _≟_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; _++_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; vec-product; power; power-replicate; _∧_)

------------------------------------------------------------------------
-- 1. The carrier: words over k axes, with concatenation as the wedge.
--    This is exactly `vec-product (Fin k)` — reused, not re-founded.
------------------------------------------------------------------------

-- ⟡set1-paydown: GradedProduct's carrier family is now its param (Vec (Fin k)).
axis-word : (k : ℕ) → GradedProduct (Vec (Fin k))
axis-word k = vec-product (Fin k)

------------------------------------------------------------------------
-- 2. NEVER ANNIHILATE. Wedging an axis with itself gives the genuine
--    grade-2 word — by refl. (Where exterior writes 0.)
------------------------------------------------------------------------

self-wedge : {k : ℕ} (i : Fin k) →
             _∧_ (axis-word k) (i ∷ []) (i ∷ []) ≡ i ∷ i ∷ []
self-wedge i = refl

------------------------------------------------------------------------
-- 3. The multiplicity residue: `count i w` = how many times axis i is used
--    in w. This is the residue exterior forgets and the k-d tree keeps.
------------------------------------------------------------------------

count : {k n : ℕ} → Fin k → Vec (Fin k) n → ℕ
count i []       = zero
count i (x ∷ xs) with i ≟ x
... | yes _ = suc (count i xs)
... | no  _ = count i xs

-- DEGREES ADD, per axis: the wedge (concatenation) adds multiplicities.
count-++ : {k m n : ℕ} (i : Fin k) (v : Vec (Fin k) m) (w : Vec (Fin k) n) →
           count i (v ++ w) ≡ count i v + count i w
count-++ i []       w = refl
count-++ i (x ∷ xs) w with i ≟ x
... | yes _ = cong suc (count-++ i xs w)
... | no  _ = count-++ i xs w

------------------------------------------------------------------------
-- 4. QUOTE = QUOTIENT = GRADE, on the axis. The multiplicity of the q-fold
--    self-wedge of an axis is exactly q — the wedge quotient. This equation
--    IS the patch from the exterior basis (one use) to the honest word; the
--    wedge generates it, we do not transport along it.
------------------------------------------------------------------------

count-replicate-self : {k : ℕ} (i : Fin k) (q : ℕ) →
                       count i (replicate q i) ≡ q
count-replicate-self i zero    = refl
count-replicate-self i (suc q) with i ≟ i
... | yes _  = cong suc (count-replicate-self i q)
... | no  ¬p = ⊥-elim (¬p refl)

-- THE LANDING: count of the q-deep ∧-term of axis i = q. The multiplicity
-- exterior forgets, the k-d depth keeps, and the wedge quotient, are one.
mult-of-power : {k : ℕ} (i : Fin k) (q : ℕ) →
                count i (power (axis-word k) (i ∷ []) q) ≡ q
mult-of-power {k} i q =
  trans (cong (count i) (power-replicate (Fin k) i q))
        (count-replicate-self i q)

------------------------------------------------------------------------
-- 5. The two reads, named. The honest word carries both; each algebra is a
--    one-sided forget, and the wedge generates the patch between them.
------------------------------------------------------------------------

-- The k-d read KEEPS the multiplicity: the refinement depth along axis i
-- (how many times the cyclic schedule revisits axis i).
kd-depth : {k n : ℕ} → Fin k → Vec (Fin k) n → ℕ
kd-depth = count

-- The patch exterior forgets and the k-d tree keeps, named at the self-wedge:
-- exterior collapses `i ∷ i ∷ []` to 0; the honest reading retains 2 — the
-- quotient. The residue (here, 2) is the wedge-generated correction.
self-wedge-multiplicity : {k : ℕ} (i : Fin k) → count i (i ∷ i ∷ []) ≡ 2
self-wedge-multiplicity i = mult-of-power i 2
