{-# OPTIONS --safe --without-K #-}
-- EL-Atlas proof tier, W13. Self-contained: no library imports.
-- Contents: the dual-rail carrier in miniature (Bool x Bool), the
-- four-corner verdict map, the rail-swap involution (S5), the
-- verdict-level dual, the crossbar intertwining square (S4), and the
-- S3 prohibition in miniature: the verdict map factors through NO
-- single-Boolean quotient of the carrier.
module VerdictCrossbar where

data Bool : Set where
  tt ff : Bool

data ⊥ : Set where

data _≡_ {A : Set} (x : A) : A → Set where
  refl : x ≡ x
infix 4 _≡_

sym : {A : Set} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl refl = refl

record Evidence : Set where
  constructor ⟨_,_⟩
  field pos : Bool   -- the positive rail E+
        neg : Bool   -- the negative rail E-
open Evidence

data Verdict : Set where
  P F U V : Verdict  -- pass / fail / undetermined(both) / vacuous(neither)

verdict : Evidence → Verdict
verdict ⟨ tt , ff ⟩ = P
verdict ⟨ ff , tt ⟩ = F
verdict ⟨ tt , tt ⟩ = U
verdict ⟨ ff , ff ⟩ = V

-- S5: the rail-swap involution on the carrier
swapE : Evidence → Evidence
swapE ⟨ p , n ⟩ = ⟨ n , p ⟩

-- the verdict-level dual: P and F exchange; U and V are self-dual
swapV : Verdict → Verdict
swapV P = F
swapV F = P
swapV U = U
swapV V = V

swapE-involutive : (e : Evidence) → swapE (swapE e) ≡ e
swapE-involutive ⟨ p , n ⟩ = refl

swapV-involutive : (v : Verdict) → swapV (swapV v) ≡ v
swapV-involutive P = refl
swapV-involutive F = refl
swapV-involutive U = refl
swapV-involutive V = refl

-- S4, the crossbar: the verdict map intertwines the two involutions.
intertwine : (e : Evidence) → verdict (swapE e) ≡ swapV (verdict e)
intertwine ⟨ tt , ff ⟩ = refl
intertwine ⟨ ff , tt ⟩ = refl
intertwine ⟨ tt , tt ⟩ = refl
intertwine ⟨ ff , ff ⟩ = refl

-- verdict distinctness (constructor disjointness)
P≢F : P ≡ F → ⊥
P≢F ()
P≢U : P ≡ U → ⊥
P≢U ()
F≢U : F ≡ U → ⊥
F≢U ()

-- the three probe points
eP eF eU : Evidence
eP = ⟨ tt , ff ⟩
eF = ⟨ ff , tt ⟩
eU = ⟨ tt , tt ⟩

-- S3 in miniature: there is NO quotient of the dual-rail carrier onto
-- a single Boolean through which the verdict map factors. Any q with
-- a decoder d sends three points needing three distinct verdicts into
-- a two-element set; pigeonhole, fully case-checked.
no-single-rail-quotient :
  (q : Evidence → Bool) (d : Bool → Verdict)
  → ((e : Evidence) → d (q e) ≡ verdict e) → ⊥
no-single-rail-quotient q d h
  with q eP | q eF | q eU | h eP | h eF | h eU
... | tt | tt | _  | hP | hF | _  = P≢F (trans (sym hP) hF)
... | ff | ff | _  | hP | hF | _  = P≢F (trans (sym hP) hF)
... | tt | ff | tt | hP | _  | hU = P≢U (trans (sym hP) hU)
... | tt | ff | ff | _  | hF | hU = F≢U (trans (sym hF) hU)
... | ff | tt | ff | hP | _  | hU = P≢U (trans (sym hP) hU)
... | ff | tt | tt | _  | hF | hU = F≢U (trans (sym hF) hU)
