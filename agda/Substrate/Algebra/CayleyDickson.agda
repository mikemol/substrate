------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson
--
-- THE CAYLEY–DICKSON DOUBLING GENERATOR — and it does NOT "stop at the octonions".
--
-- "I don't want to keep getting told 'oh, this stops at the octonions' when what's
--  really meant is 'oh, there's zero divisors, that's hard'." (user, 2026-06-12)
-- Exactly the session's theme: a NAMED, handleable structure (a zero divisor)
-- dressed up as a WALL. The doubling is a GENERATOR; like `Free`, like `unfold`,
-- it runs forever. What "stops" is a PROPERTY surviving the doubling (Hurwitz:
-- only ℝ,ℂ,ℍ,𝕆 are normed division algebras), and each loss is a tracked RESIDUE,
-- not a halt:
--   ℝ → ℂ : lose self-conjugacy (ℝ's conj = id; ℂ's does not)
--   ℂ → ℍ : lose COMMUTATIVITY
--   ℍ → 𝕆 : lose ASSOCIATIVITY
--   𝕆 → 𝕊 : lose ALTERNATIVITY — "zero divisors appear". But a zero divisor is
--           NOT annihilation; it is a multiplicative MODULO where we COLLAPSED the
--           state to 0 instead of keeping the remainder (user, 2026-06-12). The
--           doubling product has a residue (the level-n sub-products); the value
--           cancels (acP − dbP = 0) only because acP ≈ dbP, and the kept remainder
--           acP = e₁ᴼ·e₄ᴼ = e₅ᴼ is a NONZERO unit octonion. Keep the generator
--           state (the rational sub-products), exactly as el-atlas keeps the
--           just-prior-to-zero-divisor vector + the zero-divisor space, rather than
--           collapsing to 0 ([[feedback_never_discard_residue]],
--           [[feedback_wedge_not_projection]]). The "wall" is a discarded residue;
--           the generator keeps doubling 𝕊 → 𝕋(trigintaduonions) → … unobstructed.
--
-- The construction here makes "doesn't stop" LITERAL: `Carrier : ℕ → Set` and every
-- operation is TOTAL in the level `n`, by structural recursion — `Carrier 5`,
-- `Carrier 100` are as constructible as `ℂ`. The tower is over ℚ (the constructive
-- base *-ring, conj = id): ℂ = ℚ(i) is the Gaussian rationals. (ℂ over the
-- constructive ℝ = `RealTrace` is blocked only by the open Gosper +/× — a separate
-- engineering item, [[project_substrate_real_arc]], not a wall here.)
--
-- Equality is the pointwise ℚ-setoid `≈#` (the carrier is nested ℚ pairs); the
-- imaginary unit squares to −1 by it. Zero postulates, --safe --without-K.
--
-- THE STEP IS ONE STEP, RECURSED (user): "it's a multiplication and conjugation
-- that takes you from real to complex; everything higher is that same precise step,
-- applied structurally recursively — the same principle as the carrier-doubling in
-- nedge." Exactly: `Carrier (suc n) = Carrier n × Carrier n`, with `mul`/`conj`
-- recursing. And it IS the nedge carrier-doubling: the Evidence carrier
-- `Logic.Evidence.Verdict.Evidence = ⟨ pos , neg ⟩` is `Bool` doubled, and its
-- involutions are this conjugation — `negNeg ⟨p,n⟩ = ⟨p, ¬n⟩` negates the new
-- (imaginary) half, exactly `conj (a,b) = (a, −b)`; `negBoth` is the −1 antipode
-- (`Verdict.Phase.negBoth-invol`), the involutions forming V₄. SAME doubling
-- principle; the base differs (ℚ here vs Bool/F₂ there) and CD additionally carries
-- the TWISTED product below (the normed-algebra face), where nedge takes the
-- lattice/involution face. (Layering: Evidence sits above Algebra, so it is
-- referenced, not imported.)
--
-- (Sphere.agda flagged "Cayley-Dickson NOT in substrate (build)"; this is that
-- build. Relates to [[project_commuting_sphere]] Morton≅Cayley-Dickson cocycle and
-- [[feedback_octonion_loop_expressivity_limit]] — the doubling here is the ALGEBRA
-- generator; `MultiscaleOctonionLoop` is the orthogonal SCALE/rotation generator.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Empty   using (⊥)

open import Substrate.Algebra.Q       using (ℚ; 0ℚ; 1ℚ; -1ℚ)
open import Substrate.Algebra.Q.Add   using (_+ℚ_)
open import Substrate.Algebra.Q.Mul   using (_*ℚ_)
open import Substrate.Algebra.Q.Neg   using (-ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- The carrier tower: Carrier n = the 2ⁿ-dimensional algebra over ℚ. The recursion
-- is the GENERATOR — total for every n, so there is no last level.
------------------------------------------------------------------------

Carrier : ℕ → Set
Carrier zero    = ℚ
Carrier (suc n) = Carrier n × Carrier n

-- The named levels (each is just `Carrier k` — the generator at a stage).
ℝ# : Set ; ℝ# = Carrier 0    -- ℚ here (the constructive base)
ℂ# : Set ; ℂ# = Carrier 1    -- Gaussian rationals ℚ(i)
ℍ# : Set ; ℍ# = Carrier 2    -- quaternions /ℚ
𝕆# : Set ; 𝕆# = Carrier 3    -- octonions /ℚ
𝕊# : Set ; 𝕊# = Carrier 4    -- sedenions /ℚ — past the "wall", still constructible
𝕋# : Set ; 𝕋# = Carrier 5    -- trigintaduonions /ℚ — the generator has not stopped

------------------------------------------------------------------------
-- Constants and the additive structure — doubled coordinatewise.
------------------------------------------------------------------------

zero# : (n : ℕ) → Carrier n
zero# zero    = 0ℚ
zero# (suc n) = zero# n , zero# n

one# : (n : ℕ) → Carrier n
one# zero    = 1ℚ
one# (suc n) = one# n , zero# n

add : (n : ℕ) → Carrier n → Carrier n → Carrier n
add zero    x y       = x +ℚ y
add (suc n) (a , b) (c , d) = add n a c , add n b d

neg : (n : ℕ) → Carrier n → Carrier n
neg zero    x       = -ℚ x
neg (suc n) (a , b) = neg n a , neg n b

sub : (n : ℕ) → Carrier n → Carrier n → Carrier n
sub n x y = add n x (neg n y)

------------------------------------------------------------------------
-- Conjugation — the involution the doubling needs. ℝ (ℚ) is self-conjugate; each
-- doubling negates the new imaginary half: (a,b)* = (a*, −b).
------------------------------------------------------------------------

conj : (n : ℕ) → Carrier n → Carrier n
conj zero    x       = x
conj (suc n) (a , b) = conj n a , neg n b

------------------------------------------------------------------------
-- THE DOUBLED MULTIPLICATION (Cayley–Dickson):
--   (a,b)(c,d) = (a·c − d*·b ,  d·a + b·c*).
-- The recursion at level n uses multiplication AND conjugation at level n−1 — the
-- residue-keeping spine ([[feedback_never_discard_residue]]): the conjugate is the
-- residue the doubling threads through.
------------------------------------------------------------------------

mul : (n : ℕ) → Carrier n → Carrier n → Carrier n
mul zero    x y = x *ℚ y
mul (suc n) (a , b) (c , d) =
  sub n (mul n a c) (mul n (conj n d) b) ,
  add n (mul n d a) (mul n b (conj n c))

------------------------------------------------------------------------
-- THE PRODUCT WITH ITS RESIDUE (the never-discard-residue spine,
-- [[feedback_never_discard_residue]] — and the el-atlas zero-divisor handling the
-- user named: keep the just-prior-to-collapse state, don't collapse to 0).
--
-- One doubling product has FOUR level-n sub-products before the two cancellations:
--   left  coord = acP − dbP   (acP = a·c,  dbP = d*·b)
--   right coord = daP + bcP   (daP = d·a,  bcP = b·c*)
-- `mul (suc n)` keeps only the cancelled VALUE; `mulW` keeps the residue. They are
-- tied by `mul ≡ value ∘ mulW` (refl) — exactly the gcd-ℕ = proj₁ ∘ compute-trace
-- pattern (the collapsed op is the projection of the trace).
------------------------------------------------------------------------

record Prod (n : ℕ) : Set where
  constructor prod
  field acP dbP daP bcP : Carrier n

mulW : (n : ℕ) → Carrier (suc n) → Carrier (suc n) → Prod n
mulW n (a , b) (c , d) =
  prod (mul n a c) (mul n (conj n d) b) (mul n d a) (mul n b (conj n c))

value : (n : ℕ) → Prod n → Carrier (suc n)
value n (prod ac db da bc) = sub n ac db , add n da bc

mul≡value : (n : ℕ) (x y : Carrier (suc n)) → mul (suc n) x y ≡ value n (mulW n x y)
mul≡value n (a , b) (c , d) = refl

------------------------------------------------------------------------
-- Pointwise ℚ-setoid equality on the tower (the carrier is nested ℚ pairs; use
-- the value equality `≈ℚ`, not representation `≡`).
------------------------------------------------------------------------

≈# : (n : ℕ) → Carrier n → Carrier n → Set
≈# zero    x y       = x ≈ℚ y
≈# (suc n) (a , b) (c , d) = ≈# n a c × ≈# n b d

------------------------------------------------------------------------
-- ℂ: the imaginary unit i = (0,1), and i² = −1 — by the doubled multiplication,
-- pointwise over ℚ.
------------------------------------------------------------------------

i : ℂ#
i = 0ℚ , 1ℚ

i²≈−1 : ≈# 1 (mul 1 i i) (neg 1 (one# 1))
i²≈−1 = refl , refl

------------------------------------------------------------------------
-- 𝕆 → 𝕊: the "wall" that isn't one — and the COLLAPSE that hides the residue.
--
-- The classic sedenion zero divisor, in our basis: (e₁ + e₁₀)(e₄ − e₁₅), i.e. in
-- 𝕊 = 𝕆 × 𝕆 the pair (e₁ᴼ, e₂ᴼ) "annihilating" (e₄ᴼ, −e₇ᴼ). Both factors nonzero.
------------------------------------------------------------------------

xZD yZD : 𝕊#
xZD = ((((0ℚ , 1ℚ) , (0ℚ , 0ℚ)) , ((0ℚ , 0ℚ) , (0ℚ , 0ℚ))) , (((0ℚ , 0ℚ) , (1ℚ , 0ℚ)) , ((0ℚ , 0ℚ) , (0ℚ , 0ℚ))))
yZD = ((((0ℚ , 0ℚ) , (0ℚ , 0ℚ)) , ((1ℚ , 0ℚ) , (0ℚ , 0ℚ))) , (((0ℚ , 0ℚ) , (0ℚ , 0ℚ)) , ((0ℚ , 0ℚ) , (0ℚ , -1ℚ))))

1ℚ≉0ℚ : 1ℚ ≈ℚ 0ℚ → ⊥
1ℚ≉0ℚ ()

xZD≢0 : ≈# 4 xZD (zero# 4) → ⊥
xZD≢0 z = 1ℚ≉0ℚ (proj₂ (proj₁ (proj₁ (proj₁ z))))

yZD≢0 : ≈# 4 yZD (zero# 4) → ⊥
yZD≢0 z = 1ℚ≉0ℚ (proj₁ (proj₁ (proj₂ (proj₁ z))))

------------------------------------------------------------------------
-- THE COLLAPSED LOOK: the product VALUE is 0. This is the LOSSY projection —
-- `value` throws the residue away ([[feedback_wedge_not_projection]]).
------------------------------------------------------------------------

zd-value-0 : ≈# 4 (mul 4 xZD yZD) (zero# 4)
zd-value-0 = ((((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl))) , (((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl))))

------------------------------------------------------------------------
-- THE RESIDUE WE KEEP (the substrate's point, not the textbook's). A "zero
-- divisor" is a multiplicative MODULO: the left coordinate `acP − dbP` collapses
-- to 0 only because acP ≈ dbP — and the kept remainder acP = a·c = e₁ᴼ·e₄ᴼ = e₅ᴼ
-- is a NONZERO unit octonion. We hold the generator state (the level-3 octonion
-- sub-products), exactly as el-atlas holds the just-prior-to-zero-divisor vector,
-- instead of collapsing to 0. The "annihilation" is `acP ≈ dbP`, not nothing.
------------------------------------------------------------------------

zdW : Prod 3
zdW = mulW 3 xZD yZD

-- the multiplicative modulo: the two sub-products coincide (so the value cancels):
zd-residue-coincides : ≈# 3 (Prod.acP zdW) (Prod.dbP zdW)
zd-residue-coincides = (((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl)))

-- but the kept remainder is a NONZERO unit (e₅ᴼ) — the residue, not 0:
zd-residue-nonzero : ≈# 3 (Prod.acP zdW) (zero# 3) → ⊥
zd-residue-nonzero z = 1ℚ≉0ℚ (proj₂ (proj₁ (proj₂ z)))
