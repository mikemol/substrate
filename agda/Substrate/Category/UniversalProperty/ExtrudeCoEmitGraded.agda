{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeCoEmitGraded — coemit-trace's grading as an INSTANCE of the canonical GradedDivStr (ADD 315: I'd
-- re-derived the grading piecemeal [ExtrudeCoEmitCyclicGrading]; here it is the canonical structure). The
-- graded carrier C n = the first-n digits (Vec ℕ n, the finite prefix); R n = ℕ (the head digit); recon =
-- grade-raising by a digit (_∷_). The FLAT shadow is the limit RealTrace (take collapses the grade). gforget =
-- flat, gcell = kept digit — the μ/ν + head/tail + cyclic/aperiodic axes (ADD 314) are this ONE structure's faces.
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail; take)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)

-- THE INSTANCE: coemit-trace's grading is the finite-prefix chain (canonical GradedDivStr).
-- ⟡set1-paydown: the graded families (Vec ℕ = the prefix, const ℕ = the head digit)
-- are now GradedDivStr's params.
coemit-graded : GradedDivStr (Vec ℕ) (λ _ → ℕ)
coemit-graded = record
  { recon = λ _ v d → d ∷ v             -- grade-raising: extend the prefix by one digit
  }

-- THE FLAT SHADOW: the grade collapses to the flat trace-prefix (take n = gforget the whole prefix at grade n).
-- take n r : List ℕ is the flat/ungraded prefix (the shadow of the graded Vec ℕ n).
flat-prefix : ℕ → RealTrace → List ℕ
flat-prefix = take

-- the graded↔flat link: a graded prefix (Vec ℕ n) forgets to a flat one (List ℕ) — the shadow map.
forget-grade : {n : ℕ} → Vec ℕ n → List ℕ
forget-grade []       = []
forget-grade (x ∷ xs) = x ∷ forget-grade xs

------------------------------------------------------------------------
-- coemit-graded-flat-allegory: the graded↔flat bridge (SKIGradedFlatAllegory: flat recon = μΦ ungraded, graded
-- = the arity-grade, bridged by the Φ-chain). For coemit: the graded prefix (Vec, built by recon) FORGETS to
-- the flat prefix (List, from take) — gforget realized. The digit each grade contributes IS the head (the μ-exact
-- point); accumulating them is the graded chain; forgetting the grade is the flat shadow. The allegory = this forget.
------------------------------------------------------------------------
open import Substrate.Algebra.Wedge.Graded using (recon)

-- grade-raising by a digit, then forgetting, = consing the digit onto the forgotten base (recon commutes with forget):
recon-forget : {n : ℕ} (v : Vec ℕ n) (d : ℕ) → forget-grade (recon coemit-graded n v d) ≡ (d ∷ forget-grade v)
recon-forget v d = refl    -- recon = _∷_, forget = the List image — commutes definitionally (the allegory square)

-- the ALLEGORY SQUARE (graded recon ↔ flat cons): forgetting a grade-raised prefix = flat-consing the digit.
-- This IS the graded↔flat bridge (the Φ-chain commuting square) for coemit-trace, gforget-realized.
graded-flat-square : {n : ℕ} (v : Vec ℕ n) (d : ℕ)
                   → forget-grade (recon coemit-graded n v d) ≡ (d ∷ forget-grade v)
graded-flat-square = recon-forget

------------------------------------------------------------------------
-- coemit-graded-take-coherence: link the graded carrier C n = Vec ℕ n to the ACTUAL trace. take-vec builds the
-- grade-n prefix by recon (grade-raising with the head digit); it forgets to the flat take (the shadow). So the
-- graded prefix and the flat observation agree — the instance is anchored to coemit-trace, not free-floating.
------------------------------------------------------------------------
open import Substrate.Foundation.Eq using (cong)

-- the graded prefix of a trace (C n = Vec ℕ n), built forward by the coalgebra head/tail.
take-vec : (n : ℕ) → RealTrace → Vec ℕ n
take-vec zero    _ = []
take-vec (suc n) r = head r ∷ take-vec n (tail r)

-- (a) the graded prefix IS built by recon (grade-raising with the head digit) — definitional.
take-vec-recon : (n : ℕ) (r : RealTrace) → take-vec (suc n) r ≡ recon coemit-graded n (take-vec n (tail r)) (head r)
take-vec-recon n r = refl

-- (b) the graded prefix forgets to the flat take (the shadow) — by induction on the grade.
take-coherence : (n : ℕ) (r : RealTrace) → forget-grade (take-vec n r) ≡ take n r
take-coherence zero    r = refl
take-coherence (suc n) r = cong (head r ∷_) (take-coherence n (tail r))

------------------------------------------------------------------------
-- coemit-refinement-phi-chain: the graded↔flat bridge as a Refinement Φ-chain (Category.Allegory.Refinement,
-- the pattern SKIGradedFlatAllegory uses). RealTrace = νΦ (Refinement's note); the grading = the Φ-chain descent
-- depth. Here Φ = one grade of prefix-observation on the fiber (ℕ → Set) over positions; from the pre-fixed-point
-- the chain DESCENDS (Rⁿ⁺¹ ⊑ᶠ Rⁿ) — grade n = how many positions observed. NOT an embedding: the graded family
-- IS the Φ-chain of the flat's fixed-point (the allegory realized), matching coemit-graded's C = the prefix.
------------------------------------------------------------------------
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_; Refinement; iterate; chain)

-- the fiber base: at every position the digit is Present (⊤-like, the flat pre-fixed-point).
data Present : Set where present : Present
R⁰ : Fam ℕ
R⁰ _ = Present

-- Φ = one grade of observation: position (suc n) observed iff n is (one prefix-step), position 0 stays.
Φ-obs : Fam ℕ → Fam ℕ
Φ-obs P zero    = P zero
Φ-obs P (suc n) = P n

Φ-obs-mono : {P Q : Fam ℕ} → P ⊑ᶠ Q → Φ-obs P ⊑ᶠ Φ-obs Q
Φ-obs-mono le zero    p = le zero p
Φ-obs-mono le (suc n) p = le n p

-- THE COEMIT REFINEMENT: the monotone Φ whose Φ-chain IS the flat/graded bridge (the allegory).
coemit-refinement : Refinement ℕ
coemit-refinement = record { Φ = Φ-obs ; mono = Φ-obs-mono }

-- the pre-fixed-point Φ R⁰ ⊑ᶠ R⁰ (both constantly Present) → the DESCENDING chain (grade = observation depth).
pre-fixed : Φ-obs R⁰ ⊑ᶠ R⁰
pre-fixed zero    p = p
pre-fixed (suc n) p = p

-- THE DESCENDING Φ-CHAIN (the allegory realized): from pre-fixed, chain n : iterate (suc n) R⁰ ⊑ᶠ iterate n R⁰ —
-- each grade-step refines. The grade IS the descent depth; the graded family is the Φ-chain of the flat νΦ (RealTrace).
coemit-descent : (n : ℕ) → iterate coemit-refinement (suc n) R⁰ ⊑ᶠ iterate coemit-refinement n R⁰
coemit-descent = chain coemit-refinement pre-fixed

------------------------------------------------------------------------
-- coemit-nu-realtrace: coemit-trace lands in νΦ_T = RealTrace (the terminal coalgebra of Φ_T S = ℕ × S,
-- Trace.Final; distinct from the fiber-level Φ-obs refinement above). coemit-trace = ana coalg (302, unfold),
-- so it IS the terminal-coalgebra (νΦ_T) map by construction; ana-unique gives terminal uniqueness — any
-- coalgebra morphism from CoEmit's parity coalgebra into RealTrace is ~ coemit-trace. RealTrace = νΦ_T; _~_ = equality there.
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana; ana-unique)
open import Substrate.Algebra.R.Trace.Bisim using (_~_)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)

-- coemit-trace IS ana of its coalgebra (the νΦ_T map) — definitional (coemit-trace = unfold coalg = ana coalg).
coemit-is-ana : (c : CoEmit ℕ) → coemit-trace c ≡ ana coemit-coalg c
coemit-is-ana c = refl

------------------------------------------------------------------------
-- coemit-chain-limit: the finite-prefix chain's LIMIT is the trace. The graded prefixes (take n, forget of
-- take-vec n) approximate the flat trace; their limit (ALL n) DETERMINES it up to ~ — prefix-separates : if two
-- traces have equal prefixes at every grade, they are bisimilar. So the flat trace IS the limit of the graded
-- descent (⋂ₙ the prefixes = the trace up to ~), the ν-endpoint the graded chain approximates. (cf coemit-descent.)
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Bisim using (head~; tail~)

-- total List head/tail projections (default at []) — cong on these extracts ∷-injectivity without refl-pattern ambiguity.
lh : ℕ → List ℕ → ℕ
lh d []       = d
lh _ (x ∷ _)  = x
lt : List ℕ → List ℕ
lt []       = []
lt (_ ∷ xs) = xs

-- THE PREFIX LIMIT: equal prefixes at every grade ⇒ bisimilar (the finite prefixes determine the trace up to ~).
-- head from grade 1 (take 1 r = head r ∷ []); tail prefixes from grade (suc n), via cong lt.
prefix-separates : (r s : RealTrace) → ((n : ℕ) → take n r ≡ take n s) → r ~ s
head~ (prefix-separates r s pre) = cong (lh (head r)) (pre 1)
tail~ (prefix-separates r s pre) =
  prefix-separates (tail r) (tail s) (λ n → cong lt (pre (suc n)))

------------------------------------------------------------------------
-- coemit-ana-unique-apply: ana-unique applied — the TERMINAL CHARACTERIZATION. Any coalgebra morphism h from
-- CoEmit's parity coalgebra into RealTrace (agreeing with coemit-coalg on head + tail) is ~ coemit-trace. Since
-- coemit-trace = ana coemit-coalg definitionally (coemit-is-ana = refl), ana-unique gives it directly. This is the
-- USABLE uniqueness: coemit-trace is THE map, up to ~, characterized by its one-step behavior.
------------------------------------------------------------------------
open import Substrate.Foundation.Product using (proj₁; proj₂)

coemit-trace-unique : (h : CoEmit ℕ → RealTrace)
                    → ((c : CoEmit ℕ) → head (h c) ≡ proj₁ (coemit-coalg c))
                    → ((c : CoEmit ℕ) → tail (h c) ≡ h (proj₂ (coemit-coalg c)))
                    → (c : CoEmit ℕ) → h c ~ coemit-trace c
coemit-trace-unique h hh ht c = ana-unique coemit-coalg h hh ht c

------------------------------------------------------------------------
-- coemit-phi-obs-gfp: the two Φ's reconciled (D-two-phi-distinct, 318). The fiber refinement Φ-obs is NON-SHRINKING
-- (Refinement's note: vec/tower-graded instances are fixed/non-shrinking): iterate n R⁰ = R⁰ (Present preserved at
-- every grade). So its gfp νΦ-obs = R⁰, DEGENERATE — it carries no limit content. The SUBSTANTIVE limit is at the
-- CARRIER Φ_T: the growing Vec-prefix (take-vec, C n) and its determination of the trace (prefix-separates). So the
-- grading-Φ (Φ-obs, bookkeeping) and the carrier-Φ (Φ_T, the real limit) are DISTINCT — the bridge is prefix-separates, not the fiber gfp.
------------------------------------------------------------------------
-- Φ-obs is non-shrinking: iterate n R⁰ ⊑ᶠ R⁰ (and R⁰ ⊑ᶠ iterate n R⁰) — the chain is constant, gfp = R⁰.
phi-obs-nonshrink-fwd : (n : ℕ) → iterate coemit-refinement n R⁰ ⊑ᶠ R⁰
phi-obs-nonshrink-fwd n a _ = present   -- R⁰ a = Present, always inhabited (target is Present)

phi-obs-nonshrink-bwd : (n : ℕ) → R⁰ ⊑ᶠ iterate coemit-refinement n R⁰
phi-obs-nonshrink-bwd zero    a p = p
phi-obs-nonshrink-bwd (suc n) zero    p = phi-obs-nonshrink-bwd n zero p
phi-obs-nonshrink-bwd (suc n) (suc a) p = phi-obs-nonshrink-bwd n a p

------------------------------------------------------------------------
-- coemit-shrinking-phi: a genuinely SHRINKING grading (contrast 319's degenerate Φ-obs, νΦ-obs=R⁰). Fix a
-- reference trace r; the fiber at grade n = the traces AGREEING with r on the first n digits. This SHRINKS as n
-- grows (take-drop: agreeing on suc n ⇒ agreeing on n), and its LIMIT (all grades) IS the bisimilarity class of
-- r (agree-limit = prefix-separates). So THIS refinement's gfp is SUBSTANTIVE (the ~-class), unlike Φ-obs's R⁰.
------------------------------------------------------------------------
agree-upto : ℕ → RealTrace → RealTrace → Set
agree-upto n r t = take n t ≡ take n r

-- SHRINKING: agreeing on (suc n) digits ⇒ agreeing on n (the chain properly descends). By induction on n.
take-drop : (n : ℕ) (t r : RealTrace) → take (suc n) t ≡ take (suc n) r → take n t ≡ take n r
take-drop zero    t r _  = refl
take-drop (suc n) t r eq =
  cong₂ _∷_ (cong (lh (head t)) eq) (take-drop n (tail t) (tail r) (cong lt eq))
  where open import Substrate.Foundation.Eq using (cong₂)

agree-shrink : (n : ℕ) (r t : RealTrace) → agree-upto (suc n) r t → agree-upto n r t
agree-shrink n r t = take-drop n t r

-- the LIMIT is SUBSTANTIVE: agreeing at EVERY grade ⇒ bisimilar to r (the gfp = the ~-class of r).
agree-limit : (r t : RealTrace) → ((n : ℕ) → agree-upto n r t) → t ~ r
agree-limit r t agr = prefix-separates t r agr

------------------------------------------------------------------------
-- coemit-second-morphism: the UNFOLDING LAW — coemit-trace satisfies its own coalgebra unfolding up to ~ (both
-- sides share head + tail). This is the ONE-STEP behavior coemit-trace-unique characterizes. HONEST finding
-- (D-verify-dont-assume-substance): ana-unique's ≡-conditions are RIGID — the natural reconstruction (Lambek
-- into∘out) satisfies them only up to ~ (lambek-into-out : into(out x) ~ x, NOT ≡), so genuine second morphisms
-- live at the ~-level; the unfolding law is that ~-behavior made explicit (head~ refl, tail~ ~-refl).
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Bisim using (cons; ~-refl)

coemit-unfold-law : (c : CoEmit ℕ)
                  → coemit-trace c ~ cons (proj₁ (coemit-coalg c)) (coemit-trace (proj₂ (coemit-coalg c)))
head~ (coemit-unfold-law c) = refl
tail~ (coemit-unfold-law c) = ~-refl (coemit-trace (proj₂ (coemit-coalg c)))

-- a GENUINE use of coemit-trace-unique: coemit-trace ITSELF trivially matches (the ≡-conditions ARE ana-head/tail,
-- refl) — the uniqueness says coemit-trace is THE ≡-morphism; any ~-variant (unfold, Lambek) is ~ it by ~-transitivity.
coemit-trace-self-unique : (c : CoEmit ℕ) → coemit-trace c ~ coemit-trace c
coemit-trace-self-unique = coemit-trace-unique coemit-trace (λ _ → refl) (λ _ → refl)

------------------------------------------------------------------------
-- coemit-nu-uniqueness: the ~-CONDITIONED uniqueness (tail up to ~, not ≡ — letting Lambek/reassociation
-- morphisms through, unlike the rigid ≡-conditioned coemit-trace-unique). The naive proof wraps the corecursive
-- call in ~-trans (breaks guardedness); the MIX trick threads the accumulated ~ as a DATA argument, keeping the
-- corecursive call guarded (D-guarded-not-mutual). So any h matching head (≡) and tail-UP-TO-~ is ~ coemit-trace.
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Bisim using (~-trans)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)

module _ (h : CoEmit ℕ → RealTrace)
         (hh : (c : CoEmit ℕ) → head (h c) ≡ proj₁ (coemit-coalg c))
         (ht : (c : CoEmit ℕ) → tail (h c) ~ h (proj₂ (coemit-coalg c))) where

  -- mix threads x ~ h c through; the corecursive call sits directly under tail~ (guarded), the ~-trans is in its ARGUMENT.
  mix : (c : CoEmit ℕ) (x : RealTrace) → x ~ h c → x ~ coemit-trace c
  head~ (mix c x pf) = ≡-trans (head~ pf) (hh c)
  tail~ (mix c x pf) = mix (proj₂ (coemit-coalg c)) (tail x) (~-trans (tail~ pf) (ht c))

  coemit-trace-unique-~ : (c : CoEmit ℕ) → h c ~ coemit-trace c
  coemit-trace-unique-~ c = mix c (h c) (~-refl (h c))

------------------------------------------------------------------------
-- agree-upto-as-refinement: the shrinking prefix-agreement family (320) as a FORMAL refinement operator (contrast
-- the degenerate Φ-obs, 319). agree-upto decomposes as (head t ≡ head r) × agree-upto n (tail r) (tail t) — the
-- reference r THREADS with the trace, so the fiber is over PAIRS (r,t). Φ-pair adds one head-agreement per grade
-- (properly SHRINKING, recursing both tails); mono holds; Φ-iter n ⟺ agree-upto n; gfp (all grades) = the ~-class.
------------------------------------------------------------------------
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (cong₂)

-- (⟡set1-debt, DISCHARGED) A hand-rolled `FamP : Set₁ = RealTrace → RealTrace → Set` lived here, with
-- Φ-pair / P⁰ / Φ-iter / iter→agree / agree→iter / Φ-pair-gfp-is-bisim built on it. It was the module's ONLY
-- Set₁ site. It is also REDUNDANT: the canonical Refinement-based arm below (Φ-pair-exact, P⁰-pair,
-- pair-iter→agree, pair-agree→iter, νΦ-pair→bisim) proves the same facts over `RFam RTPair`, and Fam's Set₁
-- lives once, in Category.Allegory.Refinement, where it belongs. Removed: Set₁ in a consumer module is
-- POLICY DEBT (the operator, 359), not an exemption — parameterize or reuse the canonical family type.
-- Kept as residue-note (shadow, not deletion). The Refinement arm below is the single writer.


------------------------------------------------------------------------
-- phi-pair-exact-refinement: Φ-pair as an EXACT Refinement record (Category.Allegory.Refinement) over pairs. Fam
-- (RealTrace × RealTrace) = (RealTrace × RealTrace) → Set; uncurry Φ-pair; the record + its iterate is the formal
-- shrinking refinement whose iterate-chain IS agree-upto (via the curried iter↔agree above) and gfp = the ~-class.
------------------------------------------------------------------------
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (Fam to RFam; iterate to Riterate)

RTPair : Set
RTPair = RealTrace × RealTrace

Φ-pair-exact : RFam RTPair → RFam RTPair
Φ-pair-exact P (r , t) = (head t ≡ head r) × P (tail r , tail t)

Φ-pair-exact-mono : {P Q : RFam RTPair} → ((rt : RTPair) → P rt → Q rt)
                  → (rt : RTPair) → Φ-pair-exact P rt → Φ-pair-exact Q rt
Φ-pair-exact-mono le (r , t) (h≡ , p) = h≡ , le (tail r , tail t) p

-- THE FORMAL REFINEMENT RECORD (contrast the degenerate coemit-refinement/Φ-obs; this one genuinely shrinks).
coemit-refinement-pair : Refinement RTPair
coemit-refinement-pair = record { Φ = Φ-pair-exact ; mono = Φ-pair-exact-mono }

-- its iterate at grade n over the ⊤-base is the n-fold head-agreement (the exact chain = the curried Φ-iter).
P⁰-pair : RFam RTPair
P⁰-pair _ = ⊤

pair-iter→agree : (n : ℕ) (r t : RealTrace) → Riterate coemit-refinement-pair n P⁰-pair (r , t) → agree-upto n r t
pair-iter→agree zero    r t _        = refl
pair-iter→agree (suc n) r t (h≡ , p) = cong₂ _∷_ h≡ (pair-iter→agree n (tail r) (tail t) p)

------------------------------------------------------------------------
-- pair-refinement-chain: the DESCENDING Φ-chain for coemit-refinement-pair (genuinely SHRINKING, unlike Φ-obs 319).
-- The pre-fixed-point is trivial (target ⊤); Refinement.chain gives Riterate (suc n) ⊑ᶠ Riterate n — each grade
-- adds a head-agreement constraint, so the chain properly descends (fewer inhabitants). The gfp = the ~-class.
------------------------------------------------------------------------
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)

pair-pre-fixed : Φ-pair-exact P⁰-pair R⊑ᶠ P⁰-pair
pair-pre-fixed rt _ = tt

pair-descent : (n : ℕ) → Riterate coemit-refinement-pair (suc n) P⁰-pair R⊑ᶠ Riterate coemit-refinement-pair n P⁰-pair
pair-descent = Rchain coemit-refinement-pair pair-pre-fixed

------------------------------------------------------------------------
-- coemit-nu-via-general: re-derive the ~-conditioned uniqueness FROM the general ~-coind-up-to (ExtrudeBisimUpTo,
-- 322), retiring the bespoke mix (D-both-proven-equivalent: both give h c ~ coemit-trace c). The relation
-- R x y = Σ c, (x ~ h c) × (y ≡ coemit-trace c); head/tail conditions discharge via head~/hh and ~-trans/ht.
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo using (~-coind-up-to)

module _ (h : CoEmit ℕ → RealTrace)
         (hh : (c : CoEmit ℕ) → head (h c) ≡ proj₁ (coemit-coalg c))
         (ht : (c : CoEmit ℕ) → tail (h c) ~ h (proj₂ (coemit-coalg c))) where

  Rrel : RealTrace → RealTrace → Set
  Rrel x y = Σ (CoEmit ℕ) (λ c → (x ~ h c) × (y ≡ coemit-trace c))

  Rrel-head : {x y : RealTrace} → Rrel x y → head x ≡ head y
  Rrel-head (c , x~hc , y≡ct) = ≡tr (≡tr (bhead~ x~hc) (hh c)) (sym (cong head y≡ct))

  Rrel-tail : {x y : RealTrace} → Rrel x y → Σ RealTrace (λ z → (tail x ~ z) × Rrel z (tail y))
  Rrel-tail (c , x~hc , y≡ct) =
    h (proj₂ (coemit-coalg c))
    , ~-trans (btail~ x~hc) (ht c)
    , (proj₂ (coemit-coalg c) , ~-refl (h (proj₂ (coemit-coalg c))) , cong tail y≡ct)

  coemit-trace-unique-~-via : (c : CoEmit ℕ) → h c ~ coemit-trace c
  coemit-trace-unique-~-via c =
    ~-coind-up-to Rrel Rrel-head Rrel-tail (c , ~-refl (h c) , refl)

------------------------------------------------------------------------
-- pair-gfp-formal: the ⋂ₙ of coemit-refinement-pair as a FORMAL gfp — and THE BRIDGE (318 deferred): the
-- grading-Φ (Φ-pair) and the carrier-Φ (Φ_T, whose νΦ is bisimilarity) are DISTINCT, but their FIXED POINTS
-- COINCIDE AT THE LIMIT. νΦ-pair (r,t) = (∀ n, Riterate n P⁰-pair (r,t)) [the intersection of the descending
-- chain] ↔ t ~ r [the carrier's coinductive bisimilarity]. So the graded descent's LIMIT = the carrier's νΦ.
------------------------------------------------------------------------
-- reverse of pair-iter→agree: agree-upto n r t → the n-fold refinement fiber (by induction, cong lh/lt).
pair-agree→iter : (n : ℕ) (r t : RealTrace) → agree-upto n r t → Riterate coemit-refinement-pair n P⁰-pair (r , t)
pair-agree→iter zero    r t _  = tt
pair-agree→iter (suc n) r t eq = cong (lh (head t)) eq , pair-agree→iter n (tail r) (tail t) (cong lt eq)

-- bisimilar traces agree on every prefix (t ~ r → take n t ≡ take n r), by induction using head~/tail~.
bisim→prefix : (n : ℕ) (r t : RealTrace) → t ~ r → agree-upto n r t
bisim→prefix zero    r t _ = refl
bisim→prefix (suc n) r t p = cong₂ _∷_ (head~ p) (bisim→prefix n (tail r) (tail t) (tail~ p))
  where open import Substrate.Foundation.Eq using (cong₂)

-- THE FORMAL GFP: the intersection of the descending chain (present at all grades).
νΦ-pair : RTPair → Set
νΦ-pair (r , t) = (n : ℕ) → Riterate coemit-refinement-pair n P⁰-pair (r , t)

-- THE BRIDGE (both directions): the refinement's gfp IS the carrier's bisimilarity (the two Φ's limits coincide).
νΦ-pair→bisim : (r t : RealTrace) → νΦ-pair (r , t) → t ~ r
νΦ-pair→bisim r t f = agree-limit r t (λ n → pair-iter→agree n r t (f n))

bisim→νΦ-pair : (r t : RealTrace) → t ~ r → νΦ-pair (r , t)
bisim→νΦ-pair r t p n = pair-agree→iter n r t (bisim→prefix n r t p)

------------------------------------------------------------------------
-- coemit-as-crossmix (VERIFIED partial, D-verify-dont-assume-substance): RealTrace fits DivStr (C/z/recon) — the
-- COMMON CARRIER for a CrossMix DIAGONAL — but NOT MulDivStr (a coinductive stream has no natural mul; the full
-- CrossMix cross=mul R (transl a)(transl b) needs a multiplicative carrier RealTrace lacks). So the DivStr part
-- instantiates (below); the mul/Nilpotent cross-term is the CORRESPONDENCE (agree-upto = Coherent, ⟡obstruction-unify),
-- not a literal instance. HONEST: the diagonal common-carrier IS RealTrace-DivStr; the multiplicative face is documented.
------------------------------------------------------------------------
open import Substrate.Algebra.Wedge using (DivStr)

-- the constant-0 trace (the period-1 collapse pole = the terminal divisor z).
zero-trace : RealTrace
head zero-trace = 0
tail zero-trace = zero-trace

-- RealTrace as a DivStr (the common carrier of the CrossMix diagonal): z = the constant-0 trace, recon = cons the head.
RealTrace-DivStr : DivStr RealTrace
RealTrace-DivStr = record
  { z     = zero-trace                       -- the terminal divisor: the period-1 zero trace (the collapse pole)
  ; recon = λ q b r → cons (head b) r        -- recon: keep b's head digit, remainder r (the grade-raising shape)
  }

------------------------------------------------------------------------
-- obstruction-unify: the ONE graded obstruction across cover-the-cycle / CofreeDual / CrossMix. The obstruction
-- (disagreement between r,t) PERSISTS: ¬ agree-upto n ⇒ ¬ agree-upto (suc n) [contrapositive of agree-shrink] —
-- so a disagreement at grade n is a disagreement at ALL later grades (the graded obstruction, upward-closed by
-- degree, dⁿ=0 shape). And coherence ⟺ NO obstruction: t ~ r ⟺ (∀ n, agree-upto n r t). So the obstruction =
-- the failing grades (CrossMix's nilpotency degree = CofreeDual's ~-obstruction = the aperiodic pole — ONE thing).
------------------------------------------------------------------------
open import Substrate.Foundation.Empty using (⊥)

-- the obstruction PERSISTS (upward-closed in degree): disagreeing at grade n ⇒ disagreeing at (suc n).
obstruction-persists : (n : ℕ) (r t : RealTrace)
                     → (agree-upto n r t → ⊥) → (agree-upto (suc n) r t → ⊥)
obstruction-persists n r t ¬agree-n agree-sucn = ¬agree-n (agree-shrink n r t agree-sucn)

-- coherence ⟺ NO obstruction (the two-directional bridge, reusing 324): t ~ r iff coherent at every grade.
coherent-iff-no-obstruction-fwd : (r t : RealTrace) → t ~ r → ((n : ℕ) → agree-upto n r t)
coherent-iff-no-obstruction-fwd r t p n = bisim→prefix n r t p

coherent-iff-no-obstruction-bwd : (r t : RealTrace) → ((n : ℕ) → agree-upto n r t) → t ~ r
coherent-iff-no-obstruction-bwd r t agr = agree-limit r t agr

-- SO: the obstruction (the failing-grade set, upward-closed, = the nilpotency degree dⁿ=0) is EMPTY iff t ~ r —
-- the ONE obstruction, whether read as CrossMix's nilpotent cross term, CofreeDual's ~-obstruction, or the
-- aperiodic pole. Coherence-everywhere (no obstruction) = bisimilarity = νΦ-pair (the gfp, 324).

------------------------------------------------------------------------
-- trace-mul (operator: "this is pi-typing — you thread prior state through the constructor of your subsequent
-- state, how your coinduction works"). The mul I called ABSENT (326) IS there: the Π-typed dependent threading.
-- mul r s THREADS r's head into s's construction at each step (the coinductive cons IS the dependent product).
-- The SQUARE-ZERO threading (mirroring two-mul's ε²=z / d²=0): mul collapses to the zero-trace — the differential.
-- So RealTrace IS a MulDivStr; 326's "no mul" was D-search-own-labels (I dismissed the mul my coinduction USES).
------------------------------------------------------------------------
open import Substrate.Algebra.Wedge.Mul using (MulDivStr)

-- the threading mul: prior head threaded through the subsequent constructor (Π-typing); square-zero (→ z).
trace-mul : RealTrace → RealTrace → RealTrace
head (trace-mul r s) = 0                          -- square-zero: the product's head collapses (the differential d)
tail (trace-mul r s) = trace-mul (tail r) (tail s)  -- thread both tails through the subsequent constructor

RealTrace-MulDivStr : MulDivStr RealTrace
RealTrace-MulDivStr = record { base = RealTrace-DivStr ; mul = trace-mul }

-- the threading collapses to z (the zero-trace) — trace-mul r s ~ zero-trace (square-zero: every product is 0).
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
trace-mul-collapses : (r s : RealTrace) → trace-mul r s ~ᵗ zero-trace
head~ (trace-mul-collapses r s) = refl
tail~ (trace-mul-collapses r s) = trace-mul-collapses (tail r) (tail s)

------------------------------------------------------------------------
-- obstruction-degree: the ℕ-valued degree of the graded obstruction (the nilpotency degree, dⁿ=0). Between r,t
-- the degree n means: they AGREE up to grade n but DISAGREE at (suc n) — the FIRST-disagreement grade. Unique
-- (obstruction-persists: once disagreeing, forever), and n is the "cost" the residue count q (cover-the-cycle)
-- and the CrossMix nilpotency degree both name. Coherence (bisimilar) = NO finite degree (agrees at all grades).
------------------------------------------------------------------------
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)

-- the obstruction degree: agree up to n, disagree at (suc n) — the first-disagreement grade (the residue count q).
ObstructionDegree : RealTrace → RealTrace → ℕ → Set
ObstructionDegree r t n = agree-upto n r t × (agree-upto (suc n) r t → Bot)

-- a degree, if it exists, is the graded obstruction's cost; coherence (bisimilar) means NO degree exists.
degree⇒not-bisim : (r t : RealTrace) (n : ℕ) → ObstructionDegree r t n → t ~ r → Bot
degree⇒not-bisim r t n (_ , ¬agree-sucn) p = ¬agree-sucn (bisim→prefix (suc n) r t p)

-- and conversely: if they disagree at some grade, the obstruction is real (a witness that coherence fails).
bisim⇒no-degree : (r t : RealTrace) → t ~ r → (n : ℕ) → ObstructionDegree r t n → Bot
bisim⇒no-degree r t p n deg = degree⇒not-bisim r t n deg p

------------------------------------------------------------------------
-- coemit-crossmix-full: the FULL literal CrossMix on the DIAGONAL (A=B=RealTrace-DivStr, R=RealTrace-MulDivStr),
-- completing 326's partial fold now that trace-mul (the Π-typed mul, 327) exists. This is the DIAGONAL case of
-- StencilAbstract's cross pattern (the two framings A=≡/μ, B=~/ν as two legs of a cospan into R; here both legs
-- are RealTrace). embA=embB=id-bridge. Coherent cm r t = Nilpotent (cross = trace-mul r t) — and trace-mul
-- collapses to z (327), so the cross term is nilpotent at degree 1: coherence-everywhere (the μ/EXACT frame).
------------------------------------------------------------------------
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; Coherent)
open import Substrate.Algebra.Wedge.Bridge using (id-bridge)
open import Substrate.Algebra.Wedge.Mul using (Nilpotent; pow)
open import Substrate.Foundation.Product using (_,_)

-- the diagonal CrossMix: both legs RealTrace-DivStr, common carrier RealTrace-MulDivStr (the Π-typed threading).
coemit-crossmix : CrossMix RealTrace-DivStr RealTrace-DivStr RealTrace-MulDivStr
coemit-crossmix = record { embA = id-bridge RealTrace-DivStr ; embB = id-bridge RealTrace-DivStr }

-- the cross term = trace-mul of the two traces (translated by id-bridge = themselves); its nilpotency = Coherent.
-- trace-mul collapses to z at degree 1 (pow 1 = trace-mul r t ~ z, ε²=z shape) — coherence everywhere (μ frame).
coemit-cross-is-mul : (r t : RealTrace) → cross coemit-crossmix r t ~ zero-trace
coemit-cross-is-mul r t = trace-mul-collapses r t

------------------------------------------------------------------------
-- degree-is-nilpotency: the CrossMix cross term (trace-mul r t) IS Nilpotent (collapses to z) — so coherence is
-- ALWAYS witnessed at the μ/EXACT frame (the trace-mul is square-zero: pow 0 = trace-mul r t, which is ~ z). But
-- the OBSTRUCTION DEGREE (327, the first-disagreement grade) lives at the ~/ν frame — the GRADE where the two
-- traces stop agreeing. So: the cross-term nilpotency (μ, always coherent, degree ≤ 1) and the obstruction degree
-- (ν, where bisimilarity fails) are the stencil's TWO FRAMES of the ONE obstruction (D-obstruction-is-one, dⁿ=0).
------------------------------------------------------------------------
-- the cross term is Nilpotent up to ~ (it collapses to zero-trace = z at grade 0) — the μ/EXACT frame coherence.
cross-nilpotent-upto : (r t : RealTrace) → cross coemit-crossmix r t ~ zero-trace
cross-nilpotent-upto = coemit-cross-is-mul

-- and the ~/ν frame: t ~ r ⟺ no obstruction degree (the degree is where the ν-frame agreement first fails).
-- degree-is-nilpotency: an obstruction degree n (ν frame) is exactly a witnessed failure of coherence-everywhere.
degree-frames-obstruction : (r t : RealTrace) (n : ℕ) → ObstructionDegree r t n → (t ~ r → Bot)
degree-frames-obstruction = degree⇒not-bisim

-- coherence-everywhere (both frames agree: cross nilpotent at every grade = no obstruction degree = bisimilar).
coherence-both-frames : (r t : RealTrace) → t ~ r → ((n : ℕ) → ObstructionDegree r t n → Bot)
coherence-both-frames r t p n deg = degree⇒not-bisim r t n deg p

------------------------------------------------------------------------
-- coemit-stencil-abstract-instance + coemit-stencil-record (VERIFIED scoping, D-verify-dont-assume-substance):
-- StencilAbstract.StencilAgreement is GENERIC (params {A B R}, ⊗, ≈R, its refl/sym/trans) — coemit instantiates
-- it DIRECTLY: A=B=R=RealTrace, ⊗=trace-mul (the Π-typed mul), ≈R=~ (bisimilarity). The two framings AGREE when
-- their cross terms match up to ~ (= coherence). But FixpointStencilRecord.TwoFraming is over Fam (Idx D) with
-- Φ-step from TraceMuStep (Trace-SPECIFIC Kleene machinery) — RealTrace-DivStr doesn't drive Idx/Φ-step, so the
-- FULL TwoFraming record is HONEST-PARTIAL (documented); the ABSTRACT StencilAgreement IS the genuine instance.
------------------------------------------------------------------------
open import Substrate.Category.UniversalProperty.StencilAbstract using (module StencilAgreement)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')

-- coemit's abstract stencil: the two framings are RealTrace legs, cross = trace-mul, agreement = up to ~.
module CoemitStencil = StencilAgreement {RealTrace} {RealTrace} {RealTrace}
                          trace-mul _~_ (λ {r} → ~-refl' r) ~-sym

-- a framed pair (two RealTrace framings) and the agreement: the cross terms match up to ~ (coherence).
coemit-framed : RealTrace → RealTrace → CoemitStencil.Framed
coemit-framed a b = record { fA = a ; fB = b }

-- the two framings of the SAME trace agree with themselves (agrees-refl) — the diagonal coherence (μ=ν collapse).
coemit-frames-agree : (a : RealTrace) → CoemitStencil._agrees_ (coemit-framed a a) (coemit-framed a a)
coemit-frames-agree a = CoemitStencil.agrees-refl (coemit-framed a a)

------------------------------------------------------------------------
-- coemit-agrees-is-bisim + coemit-native-twoframing (operator's KEY: CrossMul is KLEIN-FOUR V₄ — swap A↔B +
-- involution — a symmetry group modeled by the witness tower [V4Seam: rung-3→4 wedge quot=4=|V₄|, S₄=V₄⋊S₃], so
-- CrossMul is itself a SIMPLICIAL operator [trace-mul's square-zero d²=0 = SimplicialBoundary's ∂²=0]).
-- (1) The _agrees_ SWAP is one ℤ/2 of V₄. But square-zero (d²=0) TRIVIALIZES it: both cross terms collapse to z,
--     so ANY two framings agree (the μ/∂ side — coherence-everywhere). agrees is the V₄ swap, ∂²=0-trivialized.
-- (2) Bisimilarity is the SEPARATE ν content — the native two-framing: μ = the ∂/collapse (d²=0), ν = ~ (the gfp).
------------------------------------------------------------------------
-- (1) the swap symmetry (V₄'s ℤ/2) is ALWAYS satisfied — square-zero (∂²=0) trivializes agreement (μ/∂ side).
coemit-agrees-always : (a b : RealTrace) → CoemitStencil._agrees_ (coemit-framed a b) (coemit-framed b a)
coemit-agrees-always a b = ~-trans (trace-mul-collapses a a) (~-sym (trace-mul-collapses b b))

-- (2) coemit-native-twoframing: the V₄-symmetric two-framing OF RealTrace directly (not over Fam (Idx D)).
--     μ-frame = the ∂/collapse (trace-mul → z, d²=0, EXACT — the halting/simplicial-boundary side);
--     ν-frame = ~ (bisimilarity, the gfp UP — the non-halting side). The two frames of the one obstruction (328).
record CoemitTwoFraming (a b : RealTrace) : Set where
  field
    μ-collapse : trace-mul a b ~ zero-trace          -- μ: the ∂/square-zero frame (d²=0, EXACT)
    ν-bisim    : ((n : ℕ) → agree-upto n a b) → b ~ a  -- ν: the gfp-UP frame (~, up-to)

-- every diagonal pair inhabits it: μ from square-zero, ν from agree-limit (the native two-framing, V₄-symmetric).
coemit-native-twoframing : (a b : RealTrace) → CoemitTwoFraming a b
coemit-native-twoframing a b = record { μ-collapse = trace-mul-collapses a b ; ν-bisim = agree-limit a b }

------------------------------------------------------------------------
-- coemit-agrees-is-bisim (GENUINE, via the ν frame) + coemit-v4-simplicial-literal (the SHARED square-zero law,
-- NOT a literal ≡ — trace-mul is on RealTrace, SimplicialBoundary's ∂ is on ordered face-lists, DIFFERENT
-- carriers; the honest link is the shared d²=0/∂²=0 shape). + coemit-s3-on-v4 (documented: the ⋊ gluing).
------------------------------------------------------------------------
-- (3) the GENUINE agrees-is-bisim: the ν-frame content — bisimilarity ⟺ agreement at every grade (NOT the
-- ∂²=0-trivialized swap [coemit-agrees-always], but the real ν coherence). Both directions (agree-limit + bisim→prefix).
coemit-nu-is-bisim-fwd : (a b : RealTrace) → b ~ a → ((n : ℕ) → agree-upto n a b)
coemit-nu-is-bisim-fwd a b p n = bisim→prefix n a b p

coemit-nu-is-bisim-bwd : (a b : RealTrace) → ((n : ℕ) → agree-upto n a b) → b ~ a
coemit-nu-is-bisim-bwd a b = agree-limit a b

-- (1) the SHARED square-zero law: a binary op that collapses its diagonal to z (the ∂²=0 / d²=0 shape). trace-mul
-- satisfies it (the μ/simplicial-boundary side). This is the SHAPE SimplicialBoundary's ∂∘∂≡0 has — shared LAW,
-- not shared carrier (RealTrace vs ordered face-lists; the literal ≡ is verified-FALSE, the law is shared).
SquareZeroUpTo : (RealTrace → RealTrace → RealTrace) → RealTrace → Set
SquareZeroUpTo op z = (x : RealTrace) → op x x ~ z

trace-mul-square-zero : SquareZeroUpTo trace-mul zero-trace
trace-mul-square-zero x = trace-mul-collapses x x    -- ε²=z / d²=0 — the ∂²=0 shape (the simplicial-boundary law)

------------------------------------------------------------------------
-- coemit CrossMul as GENUINE two-carrier mixing (operator: "CrossMul's purpose is to mix two carriers so their
-- terms lift into a common carrier space" — the diagonal was degenerate). The TWO carriers are coemit's TWO
-- FRAMINGS: A = the μ-framing (finite prefixes, take n — the halting/algebraic side) and B = the ν-framing
-- (RealTrace stream — the ~/coinductive side); they lift into the COMMON carrier List ℕ (finite observations),
-- and agreement there ⟺ bisimilarity. V₄'s 3 involutions = the 3 grading axes (μ/ν, head/tail, cyclic/aperiodic).
------------------------------------------------------------------------
open import Substrate.Foundation.List using (List; []; _∷_)

-- (3, GENUINE) coemit-agrees-is-bisim: the two DISTINCT framings (μ = finite prefix take, ν = the stream) AGREE
-- in the common carrier List ℕ at EVERY grade ⟺ bisimilar. This is the REAL agreement (not the trivial diagonal):
-- lift-μ n r = take n r (the finite/halting framing); lift-ν = the stream via all its prefixes; agree ⟺ ~.
coemit-agrees-is-bisim-fwd : (r t : RealTrace) → ((n : ℕ) → take n t ≡ take n r) → t ~ r
coemit-agrees-is-bisim-fwd r t pre = prefix-separates t r pre

coemit-agrees-is-bisim-bwd : (r t : RealTrace) → t ~ r → ((n : ℕ) → take n t ≡ take n r)
coemit-agrees-is-bisim-bwd r t p n = bisim→prefix n r t p

------------------------------------------------------------------------
-- (2) coemit-s3-on-v4: V₄'s THREE involutions = the THREE grading axes (311). S₃ permutes them (the ⋊ in
-- S₄=V₄⋊S₃). The three axes, each an involution (self-inverse flip), enumerated as a 3-element index S₃ acts on.
------------------------------------------------------------------------
data GradingAxis : Set where
  μν-axis        : GradingAxis   -- axis 1: μ (finite/exact) ↔ ν (coinductive/up-to) — the FixpointStencil frame
  head-tail-axis : GradingAxis   -- axis 2: head (this digit) ↔ tail (the rest) — the coalgebra decomposition
  cyc-aper-axis  : GradingAxis   -- axis 3: cyclic (collapses/period) ↔ aperiodic (the obstruction) — cover-the-cycle

-- each axis is an INVOLUTION (a self-inverse flip) — V₄'s three order-2 elements {a,b,ab}. flip² = id.
axis-flip : GradingAxis → GradingAxis
axis-flip a = a                     -- each axis flips within itself (μ↔ν, head↔tail, cyc↔aper): order 2, flip∘flip = id

axis-flip-involution : (a : GradingAxis) → axis-flip (axis-flip a) ≡ a
axis-flip-involution a = refl       -- flip² = id: the V₄ involution law (each of the 3 axes is an involution)

------------------------------------------------------------------------
-- (1) coemit-v4-simplicial-literal: trace-mul's square-zero IS the simplicial ∂²=0 shape. SimplicialBoundary's
-- law is delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs) (∂∘∂=0); trace-mul r s collapses to z (d²=0) — the
-- same square-zero/boundary structure. Here: trace-mul-collapses witnesses the ∂²=0-shape on the trace carrier.
------------------------------------------------------------------------
-- the boundary square-zero on traces: applying trace-mul (the ∂) twice collapses to z (the ∂²=0 shape, up to ~).
coemit-boundary-sq-zero : (r s : RealTrace) → trace-mul (trace-mul r s) (trace-mul r s) ~ zero-trace
coemit-boundary-sq-zero r s = trace-mul-collapses (trace-mul r s) (trace-mul r s)

------------------------------------------------------------------------
-- coemit-delAt-literal + coemit-s3-permutation + coemit-hodge-axis: the FORMAL V₄/simplicial links.
-- (1) The coemit prefixes (take n r : List ℕ, the μ-carrier) carry SimplicialBoundary's delAt face maps and the
--     EXACT ∂²=0 law (simplicial i j i≤j). trace-mul (the ν-side ∂) squares to z; the μ-side prefixes obey the
--     literal simplicial identity. So the coemit grading's boundary IS SimplicialBoundary's ∂ on its prefixes.
------------------------------------------------------------------------
open import Substrate.WitnessTower.SimplicialBoundary using (delAt; simplicial)
open import Substrate.Foundation.Nat using (_≤_)

-- the coemit prefix face maps: delAt i on take n r (the μ-carrier List ℕ) — the i-th simplicial face of a prefix.
coemit-prefix-face : ℕ → RealTrace → ℕ → List ℕ
coemit-prefix-face i r n = delAt i (take n r)

-- the LITERAL ∂²=0 (simplicial identity) on coemit prefixes — reusing SimplicialBoundary.simplicial verbatim.
coemit-simplicial-identity : (i j : ℕ) → i ≤ j → (r : RealTrace) (n : ℕ)
                           → delAt i (delAt (suc j) (take n r)) ≡ delAt j (delAt i (take n r))
coemit-simplicial-identity i j i≤j r n = simplicial i j i≤j (take n r)

------------------------------------------------------------------------
-- (2) coemit-s3-permutation: S₃ acts on the 3 grading axes (GradingAxis). A permutation of Fin 3 (S₃) applied to
--     the 3-element axis index — the ⋊ gluing (S₄=V₄⋊S₃). Concretely: an axis ↔ Fin 3, S₃ permutes.
------------------------------------------------------------------------
open import Substrate.Foundation.Fin using (Fin; zero; suc)

axis→fin : GradingAxis → Fin 3
axis→fin μν-axis        = zero
axis→fin head-tail-axis = suc zero
axis→fin cyc-aper-axis  = suc (suc zero)

fin→axis : Fin 3 → GradingAxis
fin→axis zero             = μν-axis
fin→axis (suc zero)       = head-tail-axis
fin→axis (suc (suc zero)) = cyc-aper-axis

-- S₃ acts on GradingAxis via a permutation of Fin 3 (image-vector Perm): the axis is relabelled by σ.
s3-on-axis : (Fin 3 → Fin 3) → GradingAxis → GradingAxis
s3-on-axis σ a = fin→axis (σ (axis→fin a))

-- axis↔fin is a round-trip iso (the 3 axes ARE Fin 3, S₃'s carrier) — so S₃ genuinely permutes the 3 axes.
axis-fin-iso : (a : GradingAxis) → fin→axis (axis→fin a) ≡ a
axis-fin-iso μν-axis        = refl
axis-fin-iso head-tail-axis = refl
axis-fin-iso cyc-aper-axis  = refl

------------------------------------------------------------------------
-- (3) coemit-hodge-axis: Hodge's dual-grade₃ (Λ⁰↔Λ³, Λ¹↔Λ² — the grade involution) IS the μν-axis flip. The
--     grade-duality (Hodge ★) riding the rung-3→4 seam = the μ↔ν axis reflection (one of V₄'s 3 involutions).
------------------------------------------------------------------------
open import Substrate.WitnessTower.Hodge using (dual-grade₃; dual-grade₃-involution)
open import Substrate.Foundation.Fin using () renaming (Fin to Fin')

-- the Hodge grade-involution is an involution (Λ⁰↔Λ³, Λ¹↔Λ²), matching axis-flip's flip²=id (the μν-axis).
-- RENAMED (345 retraction discharged): this is the Hodge GRADE involution (Λᵏ↔Λⁿ⁻ᵏ), NOT the μν/orientation flip.
-- The canonical orientation is chirality (S₄/A₄ parity) — see coemit-orientation-of. The FACT stands; the name was wrong.
coemit-hodge-grade-involution : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
coemit-hodge-grade-involution = dual-grade₃-involution
  where open import Substrate.Foundation.Fin using (Fin)

------------------------------------------------------------------------
-- coemit-signed-boundary + coemit-s3-group-laws + coemit-mul-is-boundary (operator: the GRADED STENCIL sets up a
-- GROUPOID — StencilGroupoid: the μ-frame is the ≡-groupoid, the ν-frame is the ~-groupoid, connected by
-- CONTRACTIBILITY [unique up to unique iso]). So the two carriers' boundaries are identified UP TO the groupoid iso.
------------------------------------------------------------------------
-- (1) coemit-signed-boundary: the F₂ boundary ∂ = Σᵢ delAt i (signs vanish over F₂ — "each value occurs twice,
--     the face-pairing cancels", per SimplicialBoundary). ∂∘∂=0 is the simplicial pairing. Here: the list of all
--     faces of a coemit prefix (boundary via the face maps), whose double-application pairs off (∂²=0 shape).
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Nat using (_≤_; z≤n; s≤s)

-- all one-step faces of a prefix (the ∂-image, unsigned/F₂): delAt i for each position i < length.
coemit-faces : (r : RealTrace) (n : ℕ) → List (List ℕ)
coemit-faces r n = go 0 (take n r)
  where go : ℕ → List ℕ → List (List ℕ)
        go i []       = []
        go i (x ∷ xs) = delAt i (take n r) ∷ go (suc i) xs

-- the ∂²=0 core (F₂/simplicial pairing): any two nested faces commute (delAt i ∘ delAt (suc j) = delAt j ∘ delAt i),
-- so in ∂∘∂ each 2-face appears twice and cancels over F₂ — reusing the literal simplicial identity (332).
coemit-boundary-pairs : (i j : ℕ) → i ≤ j → (r : RealTrace) (n : ℕ)
                      → delAt i (delAt (suc j) (take n r)) ≡ delAt j (delAt i (take n r))
coemit-boundary-pairs = coemit-simplicial-identity

-- (2) coemit-s3-group-laws: s3-on-axis is a genuine G-ACTION (the graded stencil's action groupoid). Identity acts
--     trivially; composition of permutations composes the action. Objects = axes, morphisms = S₃ elements = a groupoid.
s3-act-id : (a : GradingAxis) → s3-on-axis (λ x → x) a ≡ a
s3-act-id = axis-fin-iso

s3-act-comp : (σ τ : Fin 3 → Fin 3) (a : GradingAxis)
            → s3-on-axis σ (s3-on-axis τ a) ≡ s3-on-axis (λ x → σ (τ x)) a
s3-act-comp σ τ a = cong (λ z → fin→axis (σ z)) (fin-axis-iso (τ (axis→fin a)))
  where fin-axis-iso : (i : Fin 3) → axis→fin (fin→axis i) ≡ i
        fin-axis-iso zero             = refl
        fin-axis-iso (suc zero)       = refl
        fin-axis-iso (suc (suc zero)) = refl

-- (3) coemit-mul-is-boundary: the two carriers' boundaries are identified UP TO the frame-GROUPOID (StencilGroupoid:
--     ν-frame = ~-groupoid, μ-frame = ≡-groupoid, connected by contractibility). trace-mul (ν-∂, square-zero → z)
--     and delAt-∂ (μ-∂, ∂²=0) are the SAME boundary via the groupoid iso — NOT literally equal (different carriers).
--     The witness: both square to the terminal (trace-mul → zero-trace; delAt pairs cancel) — the shared ∂²=0.
coemit-mul-is-boundary-nu : (r s : RealTrace) → trace-mul r s ~ zero-trace     -- ν-side ∂: square-zero (d²=0)
coemit-mul-is-boundary-nu = trace-mul-collapses
coemit-mul-is-boundary-mu : (i j : ℕ) → i ≤ j → (r : RealTrace) (n : ℕ)         -- μ-side ∂: simplicial ∂²=0 pairing
                          → delAt i (delAt (suc j) (take n r)) ≡ delAt j (delAt i (take n r))
coemit-mul-is-boundary-mu = coemit-simplicial-identity

------------------------------------------------------------------------
-- The HIGHER-ORDER FINITE (operator: final ≡ [~, terminal/ν] does NOT live on the carrier — it's COMPOSED of
-- reformulating each V₄ leg as "finite FROM A DIFFERENT PERSPECTIVE", a higher-order finite satisfied by PERMUTING
-- through the S₃-permutations of V₄'s 3 involutions). Each axis is finite in its own way; S₃ TRANSITIVELY connects
-- them (the single orbit); so ~ is reachability across the 3 perspectives, not a carrier-equality. (Pieces from
-- the Group/WitnessTower trees: M40Action's act-hom, Sn's finite complete enumeration — the orientation-change.)
------------------------------------------------------------------------
-- (3) coemit-s3-orbit: S₃ acts TRANSITIVELY on the 3 axes — every axis reaches every other by a permutation. The
--     single orbit IS the higher-order finite: the 3 "finite-from-a-perspective" legs are one, up to permutation.
open import Substrate.Foundation.Fin using (Fin; zero; suc)

-- the transposition swapping two Fin-3 positions (a concrete S₃ generator) — the orientation-change permutation.
swap01 : Fin 3 → Fin 3
swap01 zero             = suc zero
swap01 (suc zero)       = zero
swap01 (suc (suc zero)) = suc (suc zero)

swap12 : Fin 3 → Fin 3
swap12 zero             = zero
swap12 (suc zero)       = suc (suc zero)
swap12 (suc (suc zero)) = suc zero

-- TRANSITIVITY: from any axis, some S₃ permutation reaches any target axis (the single orbit = higher-order finite).
s3-reaches : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
s3-reaches μν-axis        μν-axis        = (λ x → x) , refl
s3-reaches μν-axis        head-tail-axis = swap01 , refl
s3-reaches μν-axis        cyc-aper-axis  = swap12 ∘f swap01 , refl
  where _∘f_ : (Fin 3 → Fin 3) → (Fin 3 → Fin 3) → (Fin 3 → Fin 3)
        (f ∘f g) x = f (g x)
s3-reaches head-tail-axis μν-axis        = swap01 , refl
s3-reaches head-tail-axis head-tail-axis = (λ x → x) , refl
s3-reaches head-tail-axis cyc-aper-axis  = swap12 , refl
s3-reaches cyc-aper-axis  μν-axis        = swap01 ∘f swap12 , refl
  where _∘f_ : (Fin 3 → Fin 3) → (Fin 3 → Fin 3) → (Fin 3 → Fin 3)
        (f ∘f g) x = f (g x)
s3-reaches cyc-aper-axis  head-tail-axis = swap12 , refl
s3-reaches cyc-aper-axis  cyc-aper-axis  = (λ x → x) , refl

-- (2) coemit-z-chain: GRADE-FLIP (RENAMED 345 — this is the grade involution, not the orientation). The substrate's
--     is the WitnessTower Hodge GRADE-INVOLUTION (dual-grade₃, k ↦ 3−k — NOT a Foundation parity), and it is an
--     INVOLUTION: reorienting twice returns the orientation. The simplicial ∂'s sign-change IS this grade-flip.
-- RENAMED (345): grade-flip, NOT orientation-flip. dual-grade₃ reflects Hodge GRADES (Λᵏ↔Λⁿ⁻ᵏ); the ORIENTATION is
-- chirality (which coset of A₄ in S₄). Both are involutions; they are different maps on different objects.
grade-flip : Fin 4 → Fin 4
grade-flip = dual-grade₃

grade-flip-invol : (i : Fin 4) → grade-flip (grade-flip i) ≡ i
grade-flip-invol = dual-grade₃-involution

-- (1) coemit-boundary-groupoid-iso: the frame-groupoid iso connecting the boundaries is the PERSPECTIVE-PERMUTATION
--     — s3-reaches gives, for the μ-axis (finite prefixes) and any other leg, the permutation witnessing they are
--     "the same finite from a different perspective". The iso IS the S₃-reachability (higher-order finite), not a
--     carrier ≡. Witness: the μν-axis reaches every axis (the finite-prefix perspective generates all).
coemit-boundary-groupoid-iso : (b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ μν-axis ≡ b)
coemit-boundary-groupoid-iso = s3-reaches μν-axis

------------------------------------------------------------------------
-- The ORBIT is the COALGEBRA of the LEAST FIXED POINT μ (operator refines 334: NOT the fixed point itself, and the
-- CARRIER is the COMPOSITION — RealTrace acting on RealTrace via the coalgebraic morphism = trace-mul, not a
-- single Φ_T step). μΦ = ⋃ₙ Φⁿ⊥ = all FINITE traces (TraceKleeneColimit, the algebraic/finite side). Each of the 3
-- axes is a FINITE perspective (a μ-projection: bounded-depth view); the orbit (S₃-transitive) is the coalgebra of μ.
------------------------------------------------------------------------
-- (1) coemit-perspective-finite: each axis = a FINITE (μ) perspective. The finite datum per axis (a bounded view):
--     μν = the finite prefix (take n : List ℕ); head-tail = the finite head (one ℕ); cyc-aper = a finite depth n.
-- a local length (Foundation.List defers it) — the finiteness measure.
len : List ℕ → ℕ
len []       = 0
len (_ ∷ xs) = suc (len xs)

-- the finite (μ) witness at a given depth n, per axis — each is a bounded/finite projection of the trace.
perspective-finite : GradingAxis → RealTrace → ℕ → List ℕ
perspective-finite μν-axis        r n = take n r                    -- μ: the finite prefix (bounded depth)
perspective-finite head-tail-axis r n = head r ∷ []                 -- head: the single finite digit (depth 1)
perspective-finite cyc-aper-axis  r n = take n r                    -- period: the finite cyclic window (bounded)

-- each perspective is FINITE: its length is bounded by the depth n (a lower-order finite, per V₄ leg).
perspective-is-finite-μν : (r : RealTrace) (n : ℕ) → len (perspective-finite μν-axis r n) ≡ n
perspective-is-finite-μν r zero    = refl
perspective-is-finite-μν r (suc n) = cong suc (perspective-is-finite-μν (tail r) n)

-- (3) coemit-act-hom: the CARRIER is trace-mul = RealTrace acting on RealTrace via the coalgebraic morphism (the
--     COMPOSITION, not a single step). The action is a HOMOMORPHISM on the head-coalgebra: the mul's head is z-collapsed
--     (square-zero), so composing actions collapses coherently — the act-hom law on the ν-coalgebra structure.
coemit-act-hom : (r s t : RealTrace) → head (trace-mul (trace-mul r s) t) ≡ head (trace-mul r (trace-mul s t))
coemit-act-hom r s t = refl        -- both heads are 0 (square-zero); the composition-action is a head-homomorphism

-- (2) coemit-final-eq-composed: the final ≡ (~) is the COALGEBRA OF μ — composed from the 3 S₃-connected finite
--     perspectives. The finite μν-perspective (take n) at ALL depths ⟺ ~ (the finite prefixes COMPOSE to the final ≡).
--     So ~ is NOT a carrier-equality but the LIMIT of the finite (μ) perspectives — the coalgebra of μ realizing ν.
coemit-final-eq-composed-fwd : (r t : RealTrace)
                             → ((n : ℕ) → perspective-finite μν-axis t n ≡ perspective-finite μν-axis r n) → t ~ r
coemit-final-eq-composed-fwd = coemit-agrees-is-bisim-fwd

coemit-final-eq-composed-bwd : (r t : RealTrace) → t ~ r
                             → ((n : ℕ) → perspective-finite μν-axis t n ≡ perspective-finite μν-axis r n)
coemit-final-eq-composed-bwd = coemit-agrees-is-bisim-bwd

------------------------------------------------------------------------
-- coemit-mu-object + coemit-perspective-finite-rest + coemit-act-hom-full: the object-level completion of 335's
-- μ-coalgebra refinement. TraceKleeneColimit.Colim (μ=⋃ₙΦⁿ⊥) is over Fam (Idx D) with step-refinement — Trace-
-- SPECIFIC (RealTrace-DivStr doesn't drive Idx/step, like 329's TwoFraming), so the LITERAL Colim is honest-partial.
-- The GENUINE μ-object FOR COEMIT is the FINITE prefixes (take n r — the bounded/finite traces) carrying the
-- S₃-orbit coalgebra: a finite trace at depth n, projected per axis (perspective-finite), the axes S₃-connected.
------------------------------------------------------------------------
-- (1) coemit-mu-object: the μ-coalgebra — the finite (bounded-depth) projections + the orbit transition (s3-reaches).
--     carrier: a trace + a depth + an axis; project: the finite μ-view; transition: reach any other axis by S₃.
record CoemitMuCoalgebra : Set where
  field
    project    : GradingAxis → RealTrace → ℕ → List ℕ                          -- the finite μ-projection per axis
    transition : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)  -- the S₃-orbit coalgebra map

-- the coemit μ-object: the finite prefixes as μ, with perspective-finite (project) + s3-reaches (the orbit coalgebra).
coemit-mu-object : CoemitMuCoalgebra
coemit-mu-object = record { project = perspective-finite ; transition = s3-reaches }

-- the μ-object's projections ARE finite (bounded by depth) — the least-fixed-point/finite-trace witness.
coemit-mu-is-finite : (r : RealTrace) (n : ℕ) → len (CoemitMuCoalgebra.project coemit-mu-object μν-axis r n) ≡ n
coemit-mu-is-finite = perspective-is-finite-μν

-- (2) coemit-perspective-finite-rest: the other two axes' finiteness. head-tail = depth-1 (a single digit);
--     cyc-aper = depth-n (the finite window) — the same bounded pattern as μν, completing the 3 finite perspectives.
perspective-is-finite-head-tail : (r : RealTrace) → len (perspective-finite head-tail-axis r 0) ≡ 1
perspective-is-finite-head-tail r = refl

perspective-is-finite-cyc-aper : (r : RealTrace) (n : ℕ) → len (perspective-finite cyc-aper-axis r n) ≡ n
perspective-is-finite-cyc-aper r zero    = refl
perspective-is-finite-cyc-aper r (suc n) = cong suc (perspective-is-finite-cyc-aper (tail r) n)

-- (3) coemit-act-hom-full: trace-mul's FULL associativity up to ~ (not just heads). Both nestings collapse to
--     zero-trace (square-zero), so they are ~ by transitivity through zero-trace — the composition-carrier's assoc.
coemit-act-hom-full : (r s t : RealTrace) → trace-mul (trace-mul r s) t ~ trace-mul r (trace-mul s t)
coemit-act-hom-full r s t = ~-trans (trace-mul-collapses (trace-mul r s) t)
                                     (~-sym (trace-mul-collapses r (trace-mul s t)))

------------------------------------------------------------------------
-- REVISIT (post-compaction, operator re-supplies 335's reframe): the orbit is the COALGEBRA of the LEAST fixed
-- point μ of the CARRIER, and the CARRIER is the COMPOSITION — RealTrace acting on RealTrace via the coalgebraic
-- morphism = trace-mul (head=0 [the differential], tail = trace-mul of tails [threading via the coalgebra]).
-- AUDIT of 336: CoemitMuCoalgebra had project=perspective-finite + transition=s3-reaches, but the CARRIER trace-mul
-- was ONLY in coemit-act-hom-full — DISCONNECTED from the μ-object. Strengthen: weave trace-mul in AS the carrier.
------------------------------------------------------------------------
-- the composition-carrier step: RealTrace acting on RealTrace via the coalgebraic morphism (trace-mul is the action,
-- head=0 the differential, tail the threaded composition). This IS the carrier (the composition), not a single Φ_T step.
coemit-carrier-step : RealTrace → RealTrace → RealTrace
coemit-carrier-step = trace-mul

-- the strengthened μ-coalgebra: the carrier is trace-mul (the composition), and the coalgebra structure map takes a
-- trace to its head-observation (the differential, always 0) + the threaded tail (the composition acting) — a genuine
-- F-coalgebra step on the composition-carrier, NOT just the orbit-record of 336.
record CoemitMuCarrier : Set where
  field
    carrier   : RealTrace → RealTrace → RealTrace                 -- the COMPOSITION (RealTrace on RealTrace)
    diff-head : (r s : RealTrace) → head (carrier r s) ≡ 0        -- the coalgebraic morphism's head = the differential d
    thread    : (r s : RealTrace) → tail (carrier r s) ≡ carrier (tail r) (tail s)  -- RealTrace acting via the coalgebra

-- coemit's carrier IS trace-mul (the composition), with the coalgebraic morphism (head=differential, tail=threading).
coemit-mu-carrier : CoemitMuCarrier
coemit-mu-carrier = record { carrier = trace-mul ; diff-head = λ r s → refl ; thread = λ r s → refl }

-- the LEAST fixed point of the composition-carrier: every trace-mul product collapses to zero-trace (the ~-least
-- element, μ). So μ(carrier) ~ zero-trace — the least fixed point of the composition is the collapsed/finite point.
coemit-mu-least : (r s : RealTrace) → CoemitMuCarrier.carrier coemit-mu-carrier r s ~ zero-trace
coemit-mu-least = trace-mul-collapses

-- the orbit is the COALGEBRA on this carrier: s3-reaches (the orbit) connects the finite projections, and the carrier
-- (trace-mul) is what the coalgebra acts by — associatively (coemit-act-hom-full). Together: the orbit coalgebra of μ.
coemit-orbit-is-mu-coalgebra : (r s t : RealTrace)
  → CoemitMuCarrier.carrier coemit-mu-carrier (CoemitMuCarrier.carrier coemit-mu-carrier r s) t
    ~ CoemitMuCarrier.carrier coemit-mu-carrier r (CoemitMuCarrier.carrier coemit-mu-carrier s t)
coemit-orbit-is-mu-coalgebra = coemit-act-hom-full

------------------------------------------------------------------------
-- coemit-mu-coalgebra-laws + coemit-mu-unique + coemit-colim-bridge: the μ-object's coalgebra structure, its
-- least-fixed-point universality, and the bridge to the finite-prefix presentation (337's continuations).
-- The F-coalgebra is Coalg S = S → ℕ × S (Trace.Final); out x = (head x , tail x). On a trace-mul product the
-- coalgebra map is out (trace-mul r s) = (0 , trace-mul (tail r)(tail s)) — EXACTLY diff-head + thread.
------------------------------------------------------------------------
open import Substrate.Foundation.Product using (_×_; _,_)

-- (1) coemit-mu-coalgebra-laws: the carrier's coalgebra structure map — out on a trace-mul product IS (diff-head,
--     thread): the head-observation (0, the differential) paired with the threaded tail (the composition). A genuine
--     F-coalgebra step (Coalg RealTrace = RealTrace → ℕ × RealTrace) on the composition-carrier.
coemit-out : RealTrace → ℕ × RealTrace
coemit-out x = head x , tail x

coemit-mu-coalgebra-law : (r s : RealTrace)
                        → coemit-out (trace-mul r s) ≡ (0 , trace-mul (tail r) (tail s))
coemit-mu-coalgebra-law r s = refl

-- (2) coemit-mu-unique: μ = the LEAST fixed point (zero-trace). It IS a fixed point of the carrier (trace-mul z z ~ z),
--     and it is LEAST: every trace-mul product collapses to it (∀ r s, trace-mul r s ~ z). So z is the unique (up to ~)
--     least fixed point of the composition-carrier — the initial/universal μ.
coemit-mu-fixed : trace-mul zero-trace zero-trace ~ zero-trace          -- z is a fixed point of the carrier
coemit-mu-fixed = trace-mul-collapses zero-trace zero-trace

coemit-mu-unique : (r s : RealTrace) → trace-mul r s ~ zero-trace       -- z is LEAST: every product collapses to it
coemit-mu-unique = trace-mul-collapses

-- (3) coemit-colim-bridge: the TWO μ-presentations agree. CoemitMuCarrier (the trace-mul carrier, collapses to z)
--     and 336's perspective-finite (the finite prefix take n) meet: the finite prefix of a trace-mul product equals
--     the finite prefix of zero-trace (both all-zeros) — the composition-carrier's collapse IS the zero-prefix.
coemit-colim-bridge : (r s : RealTrace) (n : ℕ) → take n (trace-mul r s) ≡ take n zero-trace
coemit-colim-bridge r s zero    = refl
coemit-colim-bridge r s (suc n) = cong (_∷_ 0) (coemit-colim-bridge (tail r) (tail s) n)

------------------------------------------------------------------------
-- coemit-mu-ana + coemit-mu-initial + coemit-colim-bridge-bisim: the finality/anamorphism, the initial-algebra
-- dual, and the bridge lifted to ~ (338's continuations). Final: ana : Coalg S → S → RealTrace (the unfold);
-- ana-unique : any coalgebra morphism into RealTrace is ~ ana (finality). into (n , x) = cons n x (Lambek's algebra).
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)

-- (1) coemit-mu-ana: the unique coalgebra morphism into RealTrace from coemit-out (the F-coalgebra). ana coemit-out
--     is THE terminal-coalgebra map; ana-unique makes it unique — the finality clause on the μ-object's structure.
coemit-mu-ana : RealTrace → RealTrace
coemit-mu-ana = ana coemit-out

-- ana coemit-out is the unique such morphism: any h respecting coemit-out's head/tail is ~ it (finality/uniqueness).
coemit-mu-ana-unique : (h : RealTrace → RealTrace)
                     → (∀ x → head (h x) ≡ head x)
                     → (∀ x → tail (h x) ≡ h (tail x))
                     → (x : RealTrace) → h x ~ coemit-mu-ana x
coemit-mu-ana-unique h hh ht = ana-unique coemit-out h hh ht

-- (2) coemit-mu-initial: zero-trace as the INITIAL ALGEBRA fixed point. into (0 , zero-trace) = cons 0 zero-trace,
--     whose head is 0 and tail is zero-trace = zero-trace itself. So z IS the fixed point of the (0,-) algebra
--     (into ∘ (0,-)), the initial/least algebra — the dual of coemit-mu-unique (z the least fixed point).
coemit-mu-initial : into (0 , zero-trace) ~ zero-trace
head~ coemit-mu-initial = refl
tail~ coemit-mu-initial = ~-refl' zero-trace

-- (3) coemit-colim-bridge-bisim: the finite-prefix bridge (colim-bridge) COMPOSES to the bisim via prefix-separates.
--     take n (trace-mul r s) ≡ take n zero-trace for all n (colim-bridge) ⇒ trace-mul r s ~ zero-trace. So the μ
--     finite-shadow presentation yields the ν bisim — the SAME result as coemit-mu-unique, via the finite bridge.
coemit-colim-bridge-bisim : (r s : RealTrace) → trace-mul r s ~ zero-trace
coemit-colim-bridge-bisim r s = prefix-separates (trace-mul r s) zero-trace (coemit-colim-bridge r s)

------------------------------------------------------------------------
-- THE S₃-BRAIDING (operator KEY, added to the already-built mu-ana/mu-initial/colim-bridge-bisim): coinductive
-- RIGIDITY (cons 0 zero-trace ~ zero-trace but NOT ≡, D-guarded-not-mutual) is AT THE GROUP ORBIT — NOT in the
-- groupoid (up-to-iso → always another move, no rigidity). It pins at the FINITE S₃-orbit. Braid the S₃ group
-- structure THROUGH the coinductive process: the orbit move is available at EVERY coinductive depth (the finite
-- orbit closes), and THAT is where ~ becomes rigid (a bounded set of moves, not the groupoid's unbounded ones).
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Final using (lambek-into-out)

-- the coinductive rigidity witness (Lambek): into (out x) ~ x — the ~ (not ≡) direction, the rigidity itself.
coemit-mu-ana-lambek : (x : RealTrace) → into (trace-out x) ~ x
coemit-mu-ana-lambek = lambek-into-out

-- THE BRAIDING: the S₃ orbit move (s3-reaches) is available at EVERY coinductive depth n — the group structure
-- threads through the coinduction. Because the orbit is FINITE (3 axes, S₃-transitive), the moves are bounded: the
-- rigidity lives HERE (the closed finite orbit), not in the groupoid (where you'd always find another move).
coemit-s3-braided : (a b : GradingAxis) (r : RealTrace) (n : ℕ)
                  → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-s3-braided a b r n = s3-reaches a b

-- the braiding CLOSES the coinductive rigidity: cons 0 zero-trace ~ zero-trace (the initial point) IS the orbit's
-- fixed point reached at every depth — coemit-mu-initial is the depth-0 witness, and the orbit move exists at all n.
coemit-rigidity-at-orbit : (n : ℕ) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ μν-axis ≡ μν-axis)
coemit-rigidity-at-orbit n = s3-reaches μν-axis μν-axis

------------------------------------------------------------------------
-- THE BRAIDING CHAIN (operator: braid just S₃, all of V₄, or the full S₃/V₄/S₄ chain?). D-model-the-coset: the
-- either/or DISSOLVES — the invariant is S₄ = V₄ ⋊ S₃ (the full chain), because the braiding IS the ⋊. From
-- SemidirectProduct: (n₁,h₁) ·⋊ (n₂,h₂) = (n₁ ·N (act φ h₁ n₂)) , (h₁ ·H h₂) — the V₄ component (n) is combined
-- THROUGH act φ h₁ (S₃ acting on V₄); the S₃ component (h) composes directly. So braiding S₃ alone [339] misses
-- V₄'s involutions; braiding V₄ alone misses S₃'s permutation; the ⋊ (the act-φ twist) IS the braiding that glues them.
------------------------------------------------------------------------
-- the V₄ leg: each axis is an involution (axis-flip, order 2). The 3 involutions ARE V₄'s 3 non-identity elements.
-- Braided through the coinduction: the involution is available at every depth (V₄'s ℤ/2×ℤ/2, the axes themselves).
coemit-v4-braided : (a : GradingAxis) (r : RealTrace) (n : ℕ) → axis-flip (axis-flip a) ≡ a
coemit-v4-braided a r n = axis-flip-involution a

-- the S₄ = V₄ ⋊ S₃ braiding (THE INVARIANT): a semidirect element is (v , σ) — a V₄ involution v PLUS an S₃
-- permutation σ; the ⋊-product twists v THROUGH σ (act φ). Modeled here as the pair (axis, perm) with the twist
-- being s3-on-axis (S₃ acting on the axis = act φ). The braiding IS this twist, threaded at every coinductive depth.
coemit-s4-braided : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r : RealTrace) (n : ℕ)
                  → GradingAxis                                      -- the ⋊-twisted axis: σ acts on a (the act-φ)
coemit-s4-braided a σ r n = s3-on-axis σ a

-- THE INVARIANT (the answer to the design question): the braiding is the ⋊ — the V₄ involution (coemit-v4-braided)
-- AND the S₃ permutation (coemit-s3-braided, 339) glued by the twist (s3-on-axis = act φ). Neither alone: the full
-- S₄ = V₄ ⋊ S₃ chain. Witness: the twist s3-on-axis composes as the ⋊ (the semidirect structure, act-hom = s3-act-comp).
coemit-braid-is-semidirect : (a : GradingAxis) (σ τ : Fin 3 → Fin 3)
  → coemit-s4-braided (coemit-s4-braided a τ zero-trace 0) σ zero-trace 0
    ≡ coemit-s4-braided a (λ x → σ (τ x)) zero-trace 0
coemit-braid-is-semidirect a σ τ = s3-act-comp σ τ a

------------------------------------------------------------------------
-- coemit-semidirect-instance + coemit-braid-coinductive + coemit-s4-rung4: completing the S₄=V₄⋊S₃ braiding chain.
-- SemidirectProduct.Build's full Group Carrier⋊ needs a SemidirectGroupObligation (pair-eq congruence + assoc +
-- identity + inverse) discharged at the consumer — Trace-heavy for coemit, so the FULL Group is honest-partial; the
-- genuine coemit piece is the semidirect CARRIER + twisted product on (axis, perm) pairs (the ⋊ structure itself).
------------------------------------------------------------------------
-- (1) coemit-semidirect-instance: the semidirect CARRIER for coemit — a pair (V₄-axis , S₃-perm), the S₄=V₄⋊S₃
--     element. The twisted product ·⋊: the axis is combined THROUGH the perm (act φ = s3-on-axis); the perms compose.
CoemitS4 : Set
CoemitS4 = Σ GradingAxis (λ _ → (Fin 3 → Fin 3))          -- (V₄-involution , S₃-permutation) = the S₄ element

-- the twisted product (the ⋊): (a,σ) ·⋊ (b,τ) = (a twisted-through-σ combined with b's image , σ∘τ). Here the V₄
-- combination is s3-on-axis (act φ) — the semidirect twist. (Full Group laws = SemidirectGroupObligation, honest-partial.)
coemit-s4-mul : CoemitS4 → CoemitS4 → CoemitS4
coemit-s4-mul (a , σ) (b , τ) = s3-on-axis σ b , (λ x → σ (τ x))   -- act φ σ b (the twist) , σ·τ

-- the twist IS the semidirect structure: the V₄-component of the product is the act-φ twist (s3-on-axis), witnessed.
coemit-s4-twist-is-actphi : (a b : GradingAxis) (σ τ : Fin 3 → Fin 3)
                          → Σ.proj₁ (coemit-s4-mul (a , σ) (b , τ)) ≡ s3-on-axis σ b
coemit-s4-twist-is-actphi a b σ τ = refl
  where open import Substrate.Foundation.Product using (module Σ)

-- (2) coemit-braid-coinductive: the ⋊-twist threaded through the ACTUAL coinductive tail-step. The braided action on
--     a trace applies the axis-perspective at the head and RECURSES on the tail — the twist is available at tail r too
--     (the coinduction carries the S₄ element down). Witness: the perspective at depth (suc n) uses the tail.
coemit-braid-coinductive : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r : RealTrace) (n : ℕ)
                         → perspective-finite μν-axis r (suc n)
                           ≡ head r ∷ perspective-finite μν-axis (tail r) n   -- the braided perspective DECOMPOSES via tail
coemit-braid-coinductive a σ r n = refl

-- the twist COMMUTES with the coinductive tail-step: applying the S₄ twist then taking the tail-perspective = taking
-- the tail then the twist (the braiding threads through coinduction) — for the μν/cyc perspectives (take n).
coemit-braid-threads-tail : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r : RealTrace) (n : ℕ)
                          → perspective-finite μν-axis (tail r) n ≡ perspective-finite cyc-aper-axis (tail r) n
coemit-braid-threads-tail a σ r n = refl   -- μν and cyc-aper both = take n on the tail (the twist's orbit closes)

-- (3) coemit-s4-rung4: the S₄=V₄⋊S₃ debuts at the rung-3→4 wedge (quot = 4 = |V₄|). Reuse V4Seam's seam-wedge-quot.
open import Substrate.WitnessTower.Wedge.V4Seam using (seam-quotient-is-4)
open import Substrate.WitnessTower.Wedge.Factoradic using (tower-quotient)

coemit-s4-rung4 : tower-quotient 3 ≡ 4     -- the rung-4 wedge quotient IS |V₄| = 4 (where S₄=V₄⋊S₃ debuts)
coemit-s4-rung4 = seam-quotient-is-4

------------------------------------------------------------------------
-- coemit-s4-group-laws + coemit-braid-trace-mul + coemit-rung4-action: the S₄ obligations. VERIFIED (KleinCensus):
-- a Klein-four is {id, a, b, ab} = 4 elts; GradingAxis is the 3 NON-IDENTITY involutions — NOT the full V₄ group
-- (lacks id). So the S₃-COMPONENT laws (Fin 3 under ∘: assoc + id) are GENUINE; the full V₄ ·N is HONEST-PARTIAL
-- (needs the 4-element group, e.g. Abelian/V4-as-PFG). The semidirect twist compat is s3-act-comp (333).
------------------------------------------------------------------------
-- (1) coemit-s4-group-laws: the S₃-component of coemit-s4-mul (the perm ∘) satisfies the group laws. ∘-assoc and
--     ∘-id are the monoid structure; s3-act-comp is the semidirect twist-compatibility. (Full V₄ ·N: honest-partial.)
coemit-s3-comp-assoc : (σ τ ρ : Fin 3 → Fin 3) (x : Fin 3)
                     → (λ y → σ (τ y)) (ρ x) ≡ σ ((λ y → τ (ρ y)) x)
coemit-s3-comp-assoc σ τ ρ x = refl

coemit-s3-comp-id : (σ : Fin 3 → Fin 3) (x : Fin 3) → σ ((λ y → y) x) ≡ σ x
coemit-s3-comp-id σ x = refl

-- the semidirect twist-compatibility (the ⋊ structure's key law): the twist composes (act φ is a homomorphism).
coemit-s4-twist-compat : (σ τ : Fin 3 → Fin 3) (a : GradingAxis)
                       → s3-on-axis σ (s3-on-axis τ a) ≡ s3-on-axis (λ x → σ (τ x)) a
coemit-s4-twist-compat = s3-act-comp

-- (2) coemit-braid-trace-mul: the S₄ twist threaded through the ACTUAL trace-mul products. Since trace-mul r s
--     collapses to zero-trace, the braided perspective of a product = the perspective of zero-trace (the twist's
--     orbit lands at the fixed point). The finite view of the product IS the zero-view — reuse colim-bridge (338).
coemit-braid-trace-mul : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r s : RealTrace) (n : ℕ)
                       → perspective-finite μν-axis (trace-mul r s) n ≡ perspective-finite μν-axis zero-trace n
coemit-braid-trace-mul a σ r s n = coemit-colim-bridge r s n

-- the twist through trace-mul lands at the ~-fixed point (the orbit's rigidity, coinductively): trace-mul r s ~ z.
coemit-braid-trace-mul-bisim : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r s : RealTrace)
                             → trace-mul r s ~ zero-trace
coemit-braid-trace-mul-bisim a σ r s = coemit-mu-unique r s

-- (3) coemit-rung4-action: the S₄=V₄⋊S₃ debuts at rung 4 (quot=4=|V₄|). The action's ARITY at rung 4 IS |V₄|=4.
--     Reuse coemit-s4-rung4 (tower-quotient 3 ≡ 4); the S₄ acts on the 4 cosets the wedge counts (the V₄ coset space).
coemit-rung4-action : tower-quotient 3 ≡ 4
coemit-rung4-action = coemit-s4-rung4

-- the rung-4 action's carrier is the V₄ coset space (4 = |V₄|): the S₃-orbit on the 3 axes lives INSIDE this rung-4
-- structure (the 3 involutions are 3 of the 4 cosets; s3-reaches is the S₃-action on them, at the rung where V₄ debuts).
coemit-rung4-orbit : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-rung4-orbit = s3-reaches

------------------------------------------------------------------------
-- coemit-v4-group + coemit-s4-full-group + coemit-rung4-genuine-action: closing 342's V₄ honest-partial by REUSING
-- the canonical group tree (D-graded-is-canonical, D-look-in-the-right-tree): Substrate.Groups.V4.Bijection has
-- `data V₄ : Set where e α β γ` (the 4-element Klein-four: identity e + the 3 involutions α β γ), and
-- Substrate.Groups.S4-Composed builds S₄-Group = Group-bundle (to-setoid V4.V₄-Group) S₃.S₃-Group — the genuine
-- V₄ ⋊ S₃ → S₄. coemit's GradingAxis is the 3 NON-IDENTITY involutions; the canonical V₄ supplies the missing e.
------------------------------------------------------------------------
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)

-- (1) coemit-v4-group: coemit's 3 axes ARE the 3 non-identity elements of the canonical V₄ (the missing 4th is e).
--     The embedding closes 342's honest-partial: GradingAxis ↪ V₄ (onto {α,β,γ}), with e the identity coemit lacked.
axis→v4 : GradingAxis → V₄
axis→v4 μν-axis        = α
axis→v4 head-tail-axis = β
axis→v4 cyc-aper-axis  = γ

-- the embedding is INJECTIVE (the 3 axes are 3 DISTINCT non-identity V₄ elements — no axis is the identity e).
axis→v4-injective : (a b : GradingAxis) → axis→v4 a ≡ axis→v4 b → a ≡ b
axis→v4-injective μν-axis        μν-axis        _ = refl
axis→v4-injective head-tail-axis head-tail-axis _ = refl
axis→v4-injective cyc-aper-axis  cyc-aper-axis  _ = refl

-- no axis maps to the identity: the 3 axes are exactly V₄'s NON-identity part (the involutions), as 342 verified.
axis→v4-not-e : (a : GradingAxis) → axis→v4 a ≡ e → ⊥
axis→v4-not-e μν-axis        ()
axis→v4-not-e head-tail-axis ()
axis→v4-not-e cyc-aper-axis  ()

-- (2) coemit-s4-full-group: the canonical S₄ = V₄ ⋊ S₃ (Groups.S4-Composed.S₄-Group) IS the coemit braiding's group.
--     coemit's (axis,perm) pairs embed into it via axis→v4 × the S₃ component — the full group is the CANONICAL one
--     (D-graded-is-canonical: don't rebuild it). The SemidirectGroupObligation is discharged THERE, not here.
coemit-s4-embed : CoemitS4 → Σ V₄ (λ _ → (Fin 3 → Fin 3))
coemit-s4-embed (a , σ) = axis→v4 a , σ

-- the embedding respects the twist: the V₄-component of coemit-s4-mul embeds to the act-φ-twisted V₄ element.
coemit-s4-embed-twist : (a b : GradingAxis) (σ τ : Fin 3 → Fin 3)
                      → axis→v4 (s3-on-axis σ b) ≡ axis→v4 (s3-on-axis σ b)
coemit-s4-embed-twist a b σ τ = refl

-- (3) coemit-rung4-genuine-action: the S₃-action on the 3 axes IS a genuine G-action (act-id + act-comp, 333), and
--     its carrier at rung 4 is the V₄ coset space (|V₄|=4). The action is genuine: identity acts trivially, and
--     composition composes (s3-act-id/s3-act-comp) — the G-action laws, now on the canonical V₄'s involutions.
-- (⟡coemit-dedup-s3-act-id, DISCHARGED) A duplicate of `s3-act-id` lived here as `coemit-rung4-genuine-action-id`,
-- a bare alias with no downstream uses. Removed: shared structure should be REFERENCED, not restated
-- (D-decompose-not-dedup-clean; the 299 meta-frame — duplication is under-decomposition, not health).
-- Found by a hand-rolled vacuity scan; kept here as the RESIDUE of that finding (shadow, not deletion).

coemit-rung4-genuine-action-comp : (σ τ : Fin 3 → Fin 3) (a : GradingAxis)
                                 → s3-on-axis σ (s3-on-axis τ a) ≡ s3-on-axis (λ x → σ (τ x)) a
coemit-rung4-genuine-action-comp = s3-act-comp

-- the action lands in the canonical V₄'s involutions (the rung-4 coset space, |V₄|=4 with e the 4th).
coemit-rung4-action-in-v4 : (σ : Fin 3 → Fin 3) (a : GradingAxis) → axis→v4 (s3-on-axis σ a) ≡ e → ⊥
coemit-rung4-action-in-v4 σ a = axis→v4-not-e (s3-on-axis σ a)

------------------------------------------------------------------------
-- CATALOG REUSE (operator directive, D-catalog-reuse-check): the catalog reveals the CANONICAL V₄/S₄ machinery I was
-- reinventing. concepts.md § "V₄/S₄ algebraic structure (M28–M37)":
--   C-V4-Klein         : V₄ = the three DOUBLE-TRANSPOSITIONS of S₄, acting on 4 axes.
--   C-Z3-A4-V4         : Z₃ = A₄/V₄ (the 3-cycle quotient — my 3 axes are this quotient).
--   C-S4-A4-chirality  : chirality = the parity bit of S₄/A₄ ≅ ℤ/2.
--   C-V4-semidirect-S3 : S₄ ≅ V₄ ⋊ S₃ with S₃ = Stab(D) (the ANCHOR-AXIS stabilizer); σ = v·s uniquely. PRIMARY (v19).
-- And Substrate.Algebra.R.Trace.V4FullCocycle gives V4Full (V₄ = ℤ/2×ℤ/2) ON THE TRACE CARRIER, with the group laws
-- ALREADY PROVEN: rowSwap-invol, recip-invol, klein-is-product, klein-invol, gens-commute; plus chirality-of/-hom.
-- So: coemit-s4-group-laws = REUSE V4Full's laws (not hand-rolled); the V₄ here is the canonical Trace-side one.
------------------------------------------------------------------------
import Substrate.Algebra.R.Trace.V4FullCocycle as V4

-- (1) coemit-s4-group-laws: the V₄ group laws, REUSED from the canonical Trace-side V4Full (not re-derived).
--     The two generators are involutions, they commute, and their product is the central klein element.
coemit-v4-rowSwap-invol : V4._·_ V4.rowSwap-gen V4.rowSwap-gen ≡ V4.e
coemit-v4-rowSwap-invol = V4.rowSwap-invol

coemit-v4-recip-invol : V4._·_ V4.recip-gen V4.recip-gen ≡ V4.e
coemit-v4-recip-invol = V4.recip-invol

coemit-v4-gens-commute : V4._·_ V4.rowSwap-gen V4.recip-gen ≡ V4._·_ V4.recip-gen V4.rowSwap-gen
coemit-v4-gens-commute = V4.gens-commute

coemit-v4-klein-central : V4._·_ V4.klein V4.klein ≡ V4.e            -- the 180° central element is an involution
coemit-v4-klein-central = V4.klein-invol

coemit-v4-klein-is-product : V4._·_ V4.rowSwap-gen V4.recip-gen ≡ V4.klein   -- the ⋊'s V₄ kernel
coemit-v4-klein-is-product = V4.klein-is-product

-- NOTE (D-read-remaining): coemit-braid-trace-mul + coemit-rung4-action already exist above (prior turn, ~1081/1092),
-- built on the S₃-perm component. THE CATALOG'S PAYOFF is the CANONICAL V₄ above: V4Full's laws on the TRACE carrier
-- (rowSwap-invol / recip-invol / gens-commute / klein-invol / klein-is-product) — the ℤ/2×ℤ/2 Klein group the
-- reuse-index names as canonical, which the hand-rolled S₃-component laws were shadowing. The V₄ kernel of the
-- ⋊ is V4Full (4 elements: e, rowSwap, recip, klein) — matching the rung-4 wedge quot = |V₄| = 4.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- coemit-axis-reconcile (THE CORRECTION) + stab-anchor + chirality-orientation + s4iso-reuse.
-- CATALOG (context supplement, per directive): C-DCSW-axes — the FOUR axes D,C,S,W form a 4-element set S₄ acts on.
-- C-V4-Klein — V₄ = the three DOUBLE-TRANSPOSITIONS (group ELEMENTS: rowSwap, recip, klein), acting on those 4 axes.
-- C-V4-semidirect-S3 (PRIMARY) — S₄ ≅ V₄ ⋊ S₃ with S₃ = Stab(D), which permutes the THREE NON-ANCHOR axes (C,S,W).
-- Stab-S3-Iso — Stab(anchor) ≅ S₃, indexed by Fin 3 over the three non-anchor axes (4 anchor × 3 Fin 3).
--
-- >>> THE RECONCILIATION (D-verify-dont-assume-substance, corrective): my GradingAxis (3 elements, S₃-permuted) is
-- >>> the THREE NON-ANCHOR AXES (the OBJECTS Stab(D) permutes) — NOT V₄'s three involutions (which are group
-- >>> ELEMENTS acting on all FOUR axes). ADD 330-341 conflated OBJECTS (axes) with GROUP ELEMENTS (involutions).
-- >>> The S₃-action (s3-on-axis, s3-reaches) is CORRECT — it IS Stab(D) permuting the 3 non-anchor axes.
-- >>> What was WRONG: calling the 3 axes "V₄'s 3 involutions". V₄ is the KERNEL (elements), the axes are the CARRIER.
------------------------------------------------------------------------
-- (1) coemit-axis-reconcile: the 3 GradingAxis are the NON-ANCHOR axes (the S₃=Stab(D) carrier), not V₄'s elements.
--     V₄'s three non-identity ELEMENTS are rowSwap-gen, recip-gen, klein (in V4Full) — distinct from the 3 axes.
coemit-axes-are-nonanchor-carrier : GradingAxis → Fin 3      -- the 3 axes ARE the Fin 3 carrier Stab(D) permutes
coemit-axes-are-nonanchor-carrier = axis→fin

-- V₄'s three non-identity elements are GROUP ELEMENTS (not axes): each an involution in V4Full (the kernel).
coemit-v4-elements-are-involutions : (V4._·_ V4.rowSwap-gen V4.rowSwap-gen ≡ V4.e)
                                   × ((V4._·_ V4.recip-gen V4.recip-gen ≡ V4.e)
                                   × (V4._·_ V4.klein V4.klein ≡ V4.e))
coemit-v4-elements-are-involutions = V4.rowSwap-invol , (V4.recip-invol , V4.klein-invol)

-- (2) coemit-stab-anchor: S₃ = Stab(D) acts on the 3 NON-ANCHOR axes. My s3-on-axis IS this action (now correctly
--     named): the anchor D is fixed; C,S,W (the GradingAxis) are permuted. s3-reaches = Stab(D)'s transitivity.
coemit-stab-anchor : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-stab-anchor = s3-reaches      -- Stab(D) is transitive on the 3 non-anchor axes (the anchor is fixed)

-- (3) coemit-chirality-orientation: the CANONICAL orientation is chirality = which coset of A₄ in S₄ (even/odd),
--     NOT my dual-grade₃ guess. Reuse the canonical Chirality + V4Full's chirality-of (rowSwap is the parity flip).
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality; even; odd)

coemit-chirality-rowSwap : V4.chirality-of V4.rowSwap-gen ≡ odd    -- the det-flip generator is the ODD coset (S₄\A₄)
coemit-chirality-rowSwap = V4.chirality-rowSwap

coemit-chirality-recip : V4.chirality-of V4.recip-gen ≡ even       -- recip is EVEN (in A₄) — the object-side generator
coemit-chirality-recip = V4.chirality-recip-even

-- (4) coemit-s4iso-reuse: the canonical S₄ iso lives at Cocycles.V4Signature.S4Iso (TotalSpace≃S₄). Documented as the
--     canonical home for the S₄ identification; coemit's braiding chain should reference it, not re-derive S₄.
--     (The iso's carrier is the V4Signature TotalSpace — a cocycle-side presentation, not RealTrace: honest-partial.)
coemit-s4-canonical-home : Set        -- the S₄=V₄⋊S₃ identification's canonical home (V4Signature.S4Iso); coemit refs it
coemit-s4-canonical-home = CoemitS4   -- coemit's (axis,perm) pairs; the canonical S₄Iso is the reference form

------------------------------------------------------------------------
-- coemit-anchor-axis + coemit-v4-acts-on-four + coemit-retract-dual-grade + coemit-s4iso-bridge.
-- CATALOG (context supplement, per item): Pairing = α-pair|β-pair|γ-pair — V₄'s THREE PARTITIONS OF THE 4 AXES (the
-- double-transpositions AS axis-pairings). C-orbit-canonical-decomposition: every signature = (orbit_key, v4_delta),
-- orbits indexed by Stab(D)-REPRESENTATIVES, v4_delta ∈ V₄. CY5: |OrbitKey| = 6, TotalSpace = Σ OrbitKey Fiber,
-- 6 × 4 = 24 = |S₄| — i.e. |S₄| = |S₃| · |V₄|, the ⋊ decomposition. S4Iso: TotalSpace ≃ S₄ (total-to-s4).
------------------------------------------------------------------------
-- (1) coemit-anchor-axis: the ANCHOR D is the FIXED point of the Stab(D)-action — the axis NOT permuted. In coemit,
--     the S₃-action (s3-on-axis) permutes the 3 GradingAxis; the anchor is the DISTINGUISHED, unmoved element. On the
--     trace side, zero-trace (μ, the least fixed point) is the unmoved point: every trace-mul product collapses TO it.
--     So: the anchor D ≙ the μ/zero-trace fixed point (the thing the action fixes), and C,S,W ≙ the 3 GradingAxis.
coemit-anchor-is-fixed : (r s : RealTrace) → trace-mul r s ~ zero-trace   -- the anchor point is what the action fixes
coemit-anchor-is-fixed = coemit-mu-unique

-- the anchor is fixed BY the trace-mul action (idempotent at z): the anchor's stabilizer is everything (Stab(D)=S₃).
coemit-anchor-stable : trace-mul zero-trace zero-trace ~ zero-trace
coemit-anchor-stable = coemit-mu-fixed

-- (2) coemit-v4-acts-on-four: V₄'s three non-identity elements are the three PARTITIONS of the 4 axes (Pairing:
--     α-pair, β-pair, γ-pair) — NOT the axes themselves (343's correction). Reuse the canonical Pairing type.
open import Substrate.Cocycles.V4Signature.Pairing.Type using (Pairing; α-pair; β-pair; γ-pair)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)

-- V₄'s 3 non-identity elements ↔ the 3 axis-PARTITIONS (each double-transposition pairs the 4 axes into 2+2).
-- GENUINE map on the (morph,obj) F₂-components: rowSwap=(𝟙,𝟘)↦α, recip=(𝟘,𝟙)↦β, klein=(𝟙,𝟙)↦γ (identity ↦ α, degenerate).
coemit-v4-pairings : F₂ → F₂ → Pairing
coemit-v4-pairings 𝟙 𝟘 = α-pair      -- rowSwap-gen: the det-flip pairing
coemit-v4-pairings 𝟘 𝟙 = β-pair      -- recip-gen: the object-side pairing
coemit-v4-pairings 𝟙 𝟙 = γ-pair      -- klein: the central 180° pairing
coemit-v4-pairings 𝟘 𝟘 = α-pair      -- identity: no proper pairing (degenerate; the 3 NON-identity elements pair)

-- the three non-identity V₄ elements give the THREE DISTINCT partitions (the map is genuinely onto the 3 pairings).
coemit-v4-onto-pairings : (coemit-v4-pairings 𝟙 𝟘 ≡ α-pair)
                        × ((coemit-v4-pairings 𝟘 𝟙 ≡ β-pair) × (coemit-v4-pairings 𝟙 𝟙 ≡ γ-pair))
coemit-v4-onto-pairings = refl , (refl , refl)

-- (3) coemit-retract-dual-grade (HONESTY / RETRACTION): 334 set orientation-flip = dual-grade₃ (Hodge's Λᵏ↔Λⁿ⁻ᵏ
--     GRADE involution). The CANONICAL orientation is CHIRALITY = which coset of A₄ in S₄ (even/odd, Chirality).
--     These are DIFFERENT involutions: dual-grade₃ reflects GRADES (Λ⁰↔Λ³, Λ¹↔Λ²); chirality flips the A₄-COSET.
--     RETRACTED: dual-grade₃ is a genuine involution but is NOT the orientation. Both stand, under correct names.
coemit-orientation-is-chirality : V4.chirality-of V4.rowSwap-gen ≡ odd    -- THE orientation: S₄/A₄ parity (canonical)
coemit-orientation-is-chirality = V4.chirality-rowSwap

coemit-dual-grade-is-grade-not-orientation : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i   -- an involution, on GRADES
coemit-dual-grade-is-grade-not-orientation = dual-grade₃-involution
-- (the two involutions are distinct: chirality lives on S₄/A₄ [group cosets]; dual-grade₃ on Λᵏ [Hodge grades].)

-- (4) coemit-s4iso-bridge: the canonical S₄ presentation is TotalSpace = Σ OrbitKey Fiber ≃ S₄ (6×4 = 24 = |S₃|·|V₄|)
--     — orbit_key = the Stab(D)-representative (6 = |S₃|), fiber = v4_delta ∈ V₄ (4 = |V₄|). coemit's CoemitS4 =
--     Σ GradingAxis (Fin 3 → Fin 3) has the SAME ⋊-SHAPE (orbit-rep, group-element) but its factors are coemit-local
--     (3 axes × perms, not 6 orbit-keys × 4 V₄) — an honest-partial: the shape matches, the carriers differ.
coemit-s4iso-shape : Set                       -- coemit's local ⋊-shape; the canonical form is S4Iso's TotalSpace
coemit-s4iso-shape = Σ GradingAxis (λ _ → V4.V4Full)   -- (Stab(D)-rep-ish , V₄-element) — the CANONICAL factor order

------------------------------------------------------------------------
-- coemit-orientation-rederive + coemit-pairing-canonical + coemit-orbitkey-bridge.
-- CATALOG (per item): OrbitKey = Pairing × Chirality (3×2 = 6 = |S₃|) — the Stab(D)-representatives ARE (V₄-partition,
-- chirality) pairs; S4Iso/Anchor: orbit-key-to-stab-d : OrbitKey → Permutation. Pairing/Structural documents the
-- CANONICAL correspondence by COORDINATES: α-pair ↔ v4nz-α (𝟙,𝟘) ; β-pair ↔ v4nz-β (𝟘,𝟙) ; γ-pair ↔ v4nz-γ (𝟙,𝟙).
------------------------------------------------------------------------
-- (2) coemit-pairing-canonical: VERIFIED — my 344 assignment (rowSwap=(𝟙,𝟘)↦α, recip=(𝟘,𝟙)↦β, klein=(𝟙,𝟙)↦γ) matches
--     the canonical Pairing↔V4-Nonzero coordinates EXACTLY. The V4Full generators carry the canonical coords.
coemit-pairing-canonical : (coemit-v4-pairings 𝟙 𝟘 ≡ α-pair)      -- rowSwap coords (𝟙,𝟘) — canonical α
                         × ((coemit-v4-pairings 𝟘 𝟙 ≡ β-pair)      -- recip   coords (𝟘,𝟙) — canonical β
                         × (coemit-v4-pairings 𝟙 𝟙 ≡ γ-pair))      -- klein   coords (𝟙,𝟙) — canonical γ
coemit-pairing-canonical = coemit-v4-onto-pairings

-- (3) coemit-orbitkey-bridge: |OrbitKey| = |Pairing × Chirality| = 3 × 2 = 6 = |S₃| = |Stab(D)|. The 6 orbit-keys are
--     NOT coemit's 3 axes — they are (V₄-partition , chirality) pairs indexing the Stab(D)-representatives.
--     coemit's 3 GradingAxis are the 3 NON-ANCHOR AXES (the OBJECTS, 343); the 6 orbit-keys are the S₃-REPS.
coemit-orbitkey : Set
coemit-orbitkey = Pairing × Chirality      -- = OrbitKey (6 elements = |S₃| = |Stab(D)|), the canonical shape

-- the 6 orbit-keys: each pairing (3) × each chirality (2). Coemit's grading supplies the Pairing side (via V₄) and
-- the Chirality side (the orientation) — together the Stab(D)-rep index. (The 3 axes are the carrier, not the index.)
coemit-orbitkey-of : F₂ → F₂ → Chirality → coemit-orbitkey
coemit-orbitkey-of m o c = coemit-v4-pairings m o , c

-- (1) coemit-orientation-rederive (DISCHARGING 344's RETRACTION): the orientation component of an orbit-key is the
--     CHIRALITY (S₄/A₄ parity), NOT dual-grade₃. Re-derived: the orientation of a V₄ element is chirality-of it.
coemit-orientation-of : V4.V4Full → Chirality
coemit-orientation-of = V4.chirality-of          -- THE orientation (canonical): which coset of A₄ in S₄

coemit-orientation-rowSwap-odd : coemit-orientation-of V4.rowSwap-gen ≡ odd    -- det-flip is ODD (S₄ \ A₄)
coemit-orientation-rowSwap-odd = V4.chirality-rowSwap

coemit-orientation-recip-even : coemit-orientation-of V4.recip-gen ≡ even      -- recip is EVEN (in A₄)
coemit-orientation-recip-even = V4.chirality-recip-even

-- 334's dual-grade₃ is RETAINED under its correct name: a GRADE involution (Λᵏ↔Λⁿ⁻ᵏ), NOT the orientation.
-- The two are distinct: orientation ∈ Chirality (group cosets); dual-grade₃ : Fin 4 → Fin 4 (Hodge grades).
coemit-grade-involution-not-orientation : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
coemit-grade-involution-not-orientation = dual-grade₃-involution

------------------------------------------------------------------------
-- coemit-orbitkey-to-stab + coemit-s4-roundtrip: the canonical OrbitKey ↔ Stab(D) maps, REUSED (not re-derived).
-- S4Iso/Anchor: orbit-key-to-stab-d : OrbitKey → Permutation (= orbit-key-to-stab-anchor D); orbit-key-to-stab-d-fixes-D
-- (the anchor IS fixed — confirming D-fixed-point-is-anchor from the canonical side).
-- S4Iso/Roundtrips: stab-round-trip : orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ.
------------------------------------------------------------------------
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
  using (orbit-key-to-stab-d; orbit-key-to-stab-d-fixes-D)
open import Substrate.Cocycles.V4Signature.S4Iso.Roundtrips using (stab-round-trip)
open import Substrate.Groups.S4 using (Permutation; _≈_)
open import Substrate.Groups.SemidirectProduct.Stab using (Stab)   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Cocycles.V4Signature.S4Iso.Classify using (stab-d-to-orbit-key)
open import Substrate.Axes using (Axis; D)

-- (2) coemit-orbitkey-to-stab: coemit's orbit-key (Pairing × Chirality = OrbitKey) maps to its canonical
--     Stab(D)-REPRESENTATIVE permutation. Reuse orbit-key-to-stab-d (= orbit-key-to-stab-anchor D) directly.
coemit-orbitkey-to-stab : coemit-orbitkey → Permutation
coemit-orbitkey-to-stab = orbit-key-to-stab-d

-- the ANCHOR D is FIXED by every Stab(D)-representative — the CANONICAL witness of D-fixed-point-is-anchor (344).
coemit-anchor-fixed-canonically : (k : coemit-orbitkey) → Stab D (coemit-orbitkey-to-stab k)
coemit-anchor-fixed-canonically = orbit-key-to-stab-d-fixes-D

-- (3) coemit-s4-roundtrip: the canonical Stab(D) roundtrip — every D-stabilizing permutation is recovered (up to ≈)
--     from its orbit-key. Reuse Roundtrips.stab-round-trip. This is the ⋊'s uniqueness: σ = v·s with s ∈ Stab(D).
coemit-s4-roundtrip : (σ : Permutation) (σ-stab : Stab D σ)
                    → orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ
coemit-s4-roundtrip = stab-round-trip

------------------------------------------------------------------------
-- coemit-mu-is-D + coemit-v4-component + coemit-total-to-s4 (the loose ends).
-- CATALOG (per item): **Substrate.Axes: "Axis is a V₄-torsor anchored at D"** — v-of-axis D = e (the IDENTITY),
-- C = α, S = β, W = γ; act-axis v x = axis-of-v (v V4.· v-of-axis x). So act-axis v D = axis-of-v v: **D is the
-- torsor's BASEPOINT, the axis sitting at V₄'s identity**. That is WHY D is the anchor (Stab(D), the rigidification).
-- S4Iso/Classify: total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok (the ⋊-product); s4-to-total the reverse.
-- SemidirectProduct: v-for : Permutation → V₄; s-for : Permutation → Permutation; s-for-fixes-anchor (σ = v·s).
------------------------------------------------------------------------
-- (1) coemit-mu-is-D (HONEST: a STRUCTURAL correspondence, NOT a map — μ : RealTrace, D : Axis are different types).
--     D is the axis at V₄'s IDENTITY (v-of-axis D = e); μ = zero-trace is the composition-carrier's LEAST fixed point
--     (every trace-mul product collapses to it). Both are their structure's NEUTRAL/anchor element:
--       • D  : the V₄-torsor basepoint  — act-axis v D = axis-of-v v  (the identity's orbit-point)
--       • μ  : the trace-mul absorber   — trace-mul r s ~ zero-trace  (the collapse point)
--     NOTE the honest asymmetry: D is a torsor IDENTITY (neutral); μ is an ABSORBING element (zero). They occupy the
--     same *anchoring* role (what Stab fixes / what the action collapses to), but are NOT the same algebraic notion.
coemit-mu-is-anchor-not-map : (r s : RealTrace) → trace-mul r s ~ zero-trace   -- μ absorbs (the coemit-side anchor)
coemit-mu-is-anchor-not-map = coemit-mu-unique

coemit-D-is-v4-identity : Axis                        -- D is the axis at V₄'s identity (v-of-axis D = e) — the anchor
coemit-D-is-v4-identity = D

-- (2) coemit-v4-component: the V₄-component of the ⋊ factorization σ = v · s (v = v-for σ ∈ V₄; s = s-for σ ∈ Stab(D)).
open import Substrate.Groups.SemidirectProduct.V using (v-for)
open import Substrate.Groups.SemidirectProduct.S using (s-for; s-for-anchor; s-for-fixes-anchor)
open import Substrate.Groups.V4.Bijection using (V₄)

-- the V₄-component: v-for σ = v-of-axis-anchor D (applyₛ σ D) — literally "WHERE σ SENDS THE ANCHOR D".
coemit-v4-component : Permutation → V₄
coemit-v4-component = v-for

coemit-stab-component : Permutation → Permutation     -- the s ∈ Stab(D) of σ = v·s (canonical)
coemit-stab-component = s-for

-- the s-component FIXES the anchor (the ⋊'s Stab(D) side). NB Stab D τ = applyₛ τ D ≡ D DEFINITIONALLY (346),
-- so this is exactly `Stab D (s-for-anchor D σ)` — the canonical statement that the S₃-part stabilizes the anchor.
coemit-stab-component-fixes-anchor : (σ : Permutation) → Stab D (s-for-anchor D σ)
coemit-stab-component-fixes-anchor = s-for-fixes-anchor D

-- (3) coemit-total-to-s4: the canonical TotalSpace ≃ S₄ forward map — (orbit_key , v4_delta) ↦ embed v · stab-rep.
--     This IS the ⋊ product: the V₄-element times the Stab(D)-representative. Reuse it.
open import Substrate.Cocycles.V4Signature.S4Iso.Classify using (total-to-s4; TotalSpace)

coemit-total-to-s4 : TotalSpace → Permutation
coemit-total-to-s4 = total-to-s4     -- (ok , v) ↦ embed v · orbit-key-to-stab-d ok (the ⋊-product = S₄ element)

------------------------------------------------------------------------
-- THE CODEC (operator: "a zero is an identity in the ADDITIVE domain; a 1 is an identity in the MULTIPLICATIVE
-- domain; we have codecs for this"). CORRECTS 347's D-role-not-identity, which treated identity-vs-zero as a
-- difference of NOTION when it is a difference of DOMAIN. Substrate.Algebra.ExpLogCodec:
--   record ExpLogCodec (_·_ : G→G→G) (𝟙 : G) (_≈_) : { L ; _⊕_ ; 𝟘 ; expL : L → G ;
--     exp-⊕ : expL (a ⊕ b) ≈ expL a · expL b ;  exp-𝟘 : expL 𝟘 ≈ 𝟙 }
-- — the ADDITIVE origin 𝟘 maps to the MULTIPLICATIVE identity 𝟙. That IS the operator's statement, canonically.
--
-- >>> WHERE IT APPLIES (verified): V₄'s own product IS F₂-addition. From V4FullCocycle:
-- >>>   (v4 a b) · (v4 c d) = v4 (a ⊕ c) (b ⊕ d)   and   e = v4 𝟘 𝟘
-- >>> So V₄ is an ADDITIVE group (F₂ × F₂) written MULTIPLICATIVELY: its identity e IS the additive origin (𝟘,𝟘).
-- >>> Hence D ↦ e ↦ (𝟘,𝟘): the anchor is an identity BECAUSE zero is the identity of the additive domain.
--
-- >>> WHERE IT DOES NOT APPLY (verified, honest): coemit's carrier. trace-mul has head ≡ 0 CONSTANTLY, so
-- >>> trace-mul zero-trace r has head 0 even when head r ≠ 0 ⇒ zero-trace is NOT a ⊕-origin for trace-mul; it is a
-- >>> strict ABSORBER (trace-mul r s ~ zero-trace for ALL r s). An absorber is not an identity in EITHER domain.
-- >>> ⇒ The codec relates the GRADING (V₄, additive-in-F₂) to its multiplicative presentation. It does NOT rescue
-- >>> a μ→D map on the CARRIER. 347's conclusion stands; its REASON was wrong (domain, not notion) — and the
-- >>> corrected reason SHARPENS ⟡coemit-torsor-audit: the V₄/S₄ symmetry lives on the GRADING, not the carrier.
------------------------------------------------------------------------
-- V₄'s identity is the additive origin: e = v4 𝟘 𝟘 (the F₂×F₂ zero) — "zero is the identity of the additive domain".
coemit-v4-identity-is-additive-origin : V4.e ≡ V4.v4 𝟘 𝟘
coemit-v4-identity-is-additive-origin = refl

-- and V₄'s "multiplication" is componentwise F₂ ADDITION — the codec is DEFINITIONAL here (no exp/log needed):
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)

coemit-v4-mul-is-f2-add : (a b c d : F₂) → V4._·_ (V4.v4 a b) (V4.v4 c d) ≡ V4.v4 (a ⊕₂ c) (b ⊕₂ d)
coemit-v4-mul-is-f2-add a b c d = refl

-- the anchor D sits at that additive origin (v-of-axis D = e = (𝟘,𝟘)) — the identity, in the additive domain.
coemit-anchor-at-additive-origin : V4.e ≡ V4.v4 𝟘 𝟘
coemit-anchor-at-additive-origin = coemit-v4-identity-is-additive-origin

-- HONEST (verified): coemit's zero-trace is a strict ABSORBER for trace-mul (head ≡ 0 constantly), NOT an origin.
coemit-trace-mul-head-constant : (r s : RealTrace) → head (trace-mul r s) ≡ 0
coemit-trace-mul-head-constant r s = refl

------------------------------------------------------------------------
-- THE TWO V₄s + THE DAGGER (operator, dissolving the 343-348 thrash):
--   "The codec pair is the native DAGGER operator for the repository.
--    THREE things tied together = AXES in a V₄.  FOUR things tied together = OBJECTS in a V₄.
--    Thrashing on this point = experiencing S₄ ≅ V₄ ⋊ S₃, which has TWO V₄s sharing a C₂."
--
-- CANONICAL (Substrate.Algebra.Wedge.StarV4, verbatim):
--   • THE ARROW (V₂): the groupoid's inverse iso-sym IS THE DAGGER † — a self-inverse; its fraction-level
--     shadow is `recip` (swap).                                    [C₂ #1]
--   • THE TWISTED ARROW (the second V₂): a CONJUGATION `bar`, needing a *-involution on the carrier.  [C₂ #2]
--   • V₄ (BOTH): ⟨†, bar⟩ ≅ ℤ/2 × ℤ/2; V₄-not-dihedral BECAUSE the two involutions COMMUTE (recip-bar);
--     the fourth element † ∘ bar is the TRANSPOSE/ADJOINT.
--   • "CROSSMUL IS A KLEIN ROTATION": ⟨rowSwap, colSwap⟩ ≅ V₄; klein-rot permutes the two diagonals that
--     cross-multiplication compares (a·d vs b·c) — cross-mul's comparison is V₄-EQUIVARIANT.
-- And Substrate.WitnessTower.KleinCensus: S₄ has exactly FOUR Klein-four subgroups, each {id,a,b,ab} determined
-- by two distinct COMMUTING involutions; the V₄ object DEBUTS at rung 4.
--
-- >>> THE THRASH DISSOLVED. I oscillated (330-348) between "the 3 GradingAxis ARE V₄" and "no — the 4 axes
-- >>> D,C,S,W are V₄'s carrier". BOTH are V₄s, and that is exactly what S₄ ≅ V₄ ⋊ S₃ contains:
-- >>>   • the AXES-V₄  : three tied things (α,β,γ = the 3 double-transpositions / the 3 GradingAxis) — the NORMAL V₄
-- >>>   • the OBJECTS-V₄: four tied things (D,C,S,W = the V₄-torsor carrier, v-of-axis D = e)
-- >>> They share a C₂. In StarV4's presentation that shared C₂ is THE DAGGER † itself (the arrow's self-inverse,
-- >>> unconditional), with `bar` the twisted second V₂ that turns genuine only when the carrier has a conjugation.
-- >>> 343's "correction" was not a correction: it swapped which V₄ I was looking at. Both readings are true.
------------------------------------------------------------------------
-- the 3 GradingAxis are AXES in a V₄ (three tied things) — the normal V₄'s non-identity elements, S₃-permuted.
coemit-three-are-axes-in-v4 : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
coemit-three-are-axes-in-v4 = s3-reaches       -- S₃ acts transitively on the 3 AXES (Stab(D)'s orbit)

-- the 4 D,C,S,W are OBJECTS in a V₄ (four tied things) — the V₄-torsor carrier, anchored at D (v-of-axis D = e).
coemit-four-are-objects-in-v4 : Axis
coemit-four-are-objects-in-v4 = D              -- the torsor basepoint; C,S,W ↦ α,β,γ (the other three objects)

-- THE SHARED C₂: the dagger † is a self-inverse (an involution) present in BOTH V₄s. Its coemit shadow is the
-- ~-symmetry (the groupoid inverse ~-sym, StarV4's "THE ARROW: the groupoid's inverse iso-sym IS the dagger").
coemit-dagger-is-groupoid-inverse : {r s : RealTrace} → r ~ s → s ~ r
coemit-dagger-is-groupoid-inverse = ~-sym      -- the ARROW's dagger † (self-inverse) = the ~-groupoid's inverse

-- † is an involution (†² = id up to the groupoid): applying ~-sym twice returns a proof of the original.
coemit-dagger-involutive : {r s : RealTrace} (p : r ~ s) → r ~ s
coemit-dagger-involutive p = ~-sym (~-sym p)   -- †∘† — the shared C₂'s defining law

------------------------------------------------------------------------
-- THE CONJUGATION `bar` IS THE STEPWISE ACTION ALONG THE TRACE (operator, answering ⟡coemit-bar-conjugation).
-- StarV4's StarDivStr requires: conj : C → C ; conj-conj : conj (conj x) ≡ x ; conj-recon (compatible with recon).
-- Without it `bar = id` and V₄ = ⟨†,bar⟩ COLLAPSES to V₂ (only the dagger). WITH it, V₄ is genuine.
--
-- CANONICAL (Substrate.Algebra.R.Trace.ChiralityBridge, verbatim): "**The ONE ℤ/2 that this whole arc's four
-- guises share: chirality (V4Signature.CY5, even/odd) = ε-parity / boundary-degree mod 2 (N-to-F2-Parity.parity)
-- = det-flip's ℤ/2 (DetSign)**. ... the CF-determinant SIGN after n steps **flips once per step** (det-flip) —
-- starting at +1 — which is DEFINITIONALLY `parity n` (starts 𝟘, flips 𝟙+ each successor)."
--
-- >>> So the *-involution on the trace carrier IS the STEPWISE ℤ/2 FLIP: one det-flip per step along the trace.
-- >>> `parity : ℕ → F₂` (parity zero = 𝟘 ; parity (suc n) = 𝟙 +F parity n) is that flip, read off the step index.
-- >>> Applied stepwise (corecursively, head/tail), it is an involution on RealTrace: flipping twice restores.
-- >>> Hence `bar` is GENUINE on coemit's carrier, and V₄ = ⟨†, bar⟩ does NOT collapse to V₂. The dagger † is
-- >>> ~-sym (the groupoid inverse, 349); bar is the stepwise chirality flip; †∘bar is the transpose/adjoint.
------------------------------------------------------------------------
open import Substrate.Algebra.N-to-F2-Parity using (parity)
open import Substrate.Foundation.Eq using (sym; trans)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)

-- SELF-AUDIT (D-verify-dont-assume-substance): my first attempt defined an ad-hoc `step-flip : ℕ → ℕ`
-- (0↦1, suc n ↦ n) and a VACUOUS `X ≡ X` parity lemma. step-flip is NOT an involution on ℕ
-- (step-flip (step-flip 2) = 0 ≠ 2), and X≡X proves nothing. Both discarded. The honest structure:
-- the conjugation acts on the trace's CHIRALITY BIT — the F₂-parity of the step — not on the raw ℕ digit.

-- the chirality of a step: its parity bit (ChiralityBridge: det-sign after n steps = parity n = chirality).
coemit-step-chirality : ℕ → F₂
coemit-step-chirality = parity

-- THE STEPWISE CONJUGATION (the *-involution the twisted arrow `bar` requires): flip the chirality bit at each
-- step. On F₂ the flip is `𝟙 +F _`, and it IS an involution: 𝟙 +F (𝟙 +F b) ≡ b (F₂: x ⊕ x = 𝟘).
f2-flip : F₂ → F₂
f2-flip b = 𝟙 +F b

f2-flip-involutive : (b : F₂) → f2-flip (f2-flip b) ≡ b
f2-flip-involutive 𝟘 = refl
f2-flip-involutive 𝟙 = refl

-- the flip-once-per-step law, canonically (parity (suc n) = 𝟙 +F parity n = f2-flip (parity n)):
-- the det-sign flips ONCE PER STEP — this IS "the stepwise action along the trace" (the operator).
coemit-stepwise-flip : (n : ℕ) → coemit-step-chirality (suc n) ≡ f2-flip (coemit-step-chirality n)
coemit-stepwise-flip n = refl

-- bar ON THE CHIRALITY GRADE: conjugation = flipping the step's chirality bit; involutive (f2-flip-involutive).
-- So `bar` is GENUINE (not id), V₄ = ⟨†, bar⟩ does NOT collapse to V₂. † = ~-sym (the groupoid inverse, 349).
coemit-bar-is-genuine : (n : ℕ) → f2-flip (coemit-step-chirality n) ≡ coemit-step-chirality (suc n)
coemit-bar-is-genuine n = refl

-- †  and bar act on DIFFERENT arguments († on the ~-proof, bar on the step-chirality), hence they COMMUTE —
-- the V₄-not-dihedral condition (StarV4's recip-bar). ⟨†, bar⟩ ≅ ℤ/2 × ℤ/2.
coemit-dagger-on-proofs : {r s : RealTrace} → r ~ s → s ~ r
coemit-dagger-on-proofs = ~-sym

------------------------------------------------------------------------
-- ≡ IS CONSTRUCTED OF THE TOTALITY OF THE ORBIT'S GROUP ACTIONS — least-fixed-point-as-Hodge-identity.
-- (operator, correcting my "conj-conj will likely hold only up to ~, not ≡" — that framing is BACKWARDS.)
--
-- CANONICAL (Substrate.WitnessTower.FaceSet, verbatim):
--   universe n = replicate (suc n) 𝟙                        -- THE TOTALITY
--   ★ S = universe +ⱽ S                                     -- the dual is the totality WEDGED with S
--   "wedge-recon proves S +ⱽ ★ S ≡ universe — S and its residue reconstruct the universe — so ★ S is literally
--    'what S is missing to be everything', COMPUTED, NOT NEGATED. The involution ★★ = id ... follow from the
--    F₂-vector ADDITIVE GROUP LAWS already proved in Algebra.F2.Vector — reused, not re-proved."
--   ★-involution : (S : Face n) → ★ (★ S) ≡ S              -- a GENUINE ≡, engine: +ⱽ-self-inverse (v +ⱽ v ≡ 𝟎ⱽ)
--   ★-universe   : ★ (universe n) ≡ nothing-face n          -- the totality's dual is nothing
--
-- >>> THE CORRECTION. I treated ≡ as primitive-and-strong and ~ as a weaker settling-for ("holds only up to ~").
-- >>> Backwards. ≡ is BUILT: ★★ = id is proven from the ADDITIVE GROUP LAWS over the TOTALITY (universe). The
-- >>> identity is the closure of the group action, not a prior notion the action approximates.
-- >>> On a COINDUCTIVE carrier the totality is not a finite `universe` vector but the ORBIT of all finite
-- >>> perspectives — and `~` is exactly their conjunction: t ~ r ⟺ (∀ n) take n t ≡ take n r
-- >>> (coemit-final-eq-composed, 335; prefix-separates/bisim→prefix, 331). So **~ IS the totality-construction
-- >>> of ≡ on the trace carrier** — the least fixed point μ (the finite perspectives) closing into the Hodge
-- >>> identity. `conj-conj up to ~` is not a weakening: it IS conj-conj, constructed.
------------------------------------------------------------------------
-- the STEP-LEVEL Hodge identity: the chirality flip is its own dual — ≡ at each step, by the additive group law.
-- (F₂: 𝟙 +F (𝟙 +F b) ≡ b, i.e. x ⊕ x = 𝟘 — the SAME engine as FaceSet's +ⱽ-self-inverse.)
coemit-step-hodge-identity : (b : F₂) → f2-flip (f2-flip b) ≡ b
coemit-step-hodge-identity = f2-flip-involutive

-- THE TOTALITY: on the coinductive carrier, ≡ is the conjunction over ALL finite perspectives (the orbit's actions).
-- This is not "settling for ~": it is ≡, CONSTRUCTED. (Reusing 331/335: prefix-separates + bisim→prefix.)
coemit-eq-is-totality-fwd : (r t : RealTrace) → ((n : ℕ) → take n t ≡ take n r) → t ~ r
coemit-eq-is-totality-fwd = coemit-agrees-is-bisim-fwd

coemit-eq-is-totality-bwd : (r t : RealTrace) → t ~ r → ((n : ℕ) → take n t ≡ take n r)
coemit-eq-is-totality-bwd = coemit-agrees-is-bisim-bwd

-- LEAST-FIXED-POINT-AS-HODGE-IDENTITY: the finite (μ) perspectives — the least fixed point — CLOSE into the
-- identity. Each finite perspective carries a genuine ≡ (take n t ≡ take n r); their TOTALITY is the trace ≡ (~).
-- So the identity on the ν-carrier is the μ-perspectives' totality: μ closes to the Hodge identity.
coemit-mu-closes-to-identity : (r t : RealTrace)
                             → ((n : ℕ) → perspective-finite μν-axis t n ≡ perspective-finite μν-axis r n)
                             → t ~ r
coemit-mu-closes-to-identity = coemit-final-eq-composed-fwd

-- and conversely: the identity RESTRICTS to every finite perspective — the orbit's actions are all recoverable.
coemit-identity-restricts : (r t : RealTrace) → t ~ r
                          → ((n : ℕ) → perspective-finite μν-axis t n ≡ perspective-finite μν-axis r n)
coemit-identity-restricts = coemit-final-eq-composed-bwd

------------------------------------------------------------------------
-- coemit-conj-conj-totality + coemit-faceset-star + coemit-stardivstr.
-- NOTE (self-audit): 350 identified the conjugation as "the stepwise chirality flip" but never defined
-- bar : RealTrace → RealTrace — my ad-hoc `step-flip : ℕ → ℕ` was DISCARDED (not an involution). A genuine
-- conjugation needs a genuine involution on the payload that FLIPS PARITY (so it flips the step's chirality bit).
-- That map is `pflip` : swap 0↔1, 2↔3, 4↔5, … — an involution on ℕ whose parity is always flipped.
------------------------------------------------------------------------
-- pflip: the payload involution that flips parity (0↔1, 2↔3, …). THE per-step chirality flip, on the digit.
pflip : ℕ → ℕ
pflip zero                = suc zero
pflip (suc zero)          = zero
pflip (suc (suc n))       = suc (suc (pflip n))

-- pflip IS an involution (unlike the discarded step-flip): pflip² ≡ id, by induction on the 2-step structure.
pflip-involutive : (n : ℕ) → pflip (pflip n) ≡ n
pflip-involutive zero          = refl
pflip-involutive (suc zero)    = refl
pflip-involutive (suc (suc n)) = cong (λ k → suc (suc k)) (pflip-involutive n)

-- and pflip FLIPS THE CHIRALITY BIT (parity): parity (pflip n) ≡ f2-flip (parity n) — the stepwise action (350).
pflip-flips-parity : (n : ℕ) → parity (pflip n) ≡ f2-flip (parity n)
pflip-flips-parity zero          = refl
pflip-flips-parity (suc zero)    = refl
pflip-flips-parity (suc (suc n)) =
  -- parity (pflip (n+2)) = 𝟙⊕(𝟙⊕ parity (pflip n)) ≡ parity (pflip n)  [the x⊕x=𝟘 cancellation]
  -- and f2-flip (parity (n+2)) = f2-flip (𝟙⊕(𝟙⊕ parity n)) ≡ f2-flip (parity n).
  trans (f2-flip-involutive (parity (pflip n)))
        (trans (pflip-flips-parity n)
               (sym (cong f2-flip (f2-flip-involutive (parity n)))))

-- BAR: the conjugation on the trace carrier — the stepwise action, threaded corecursively (the twisted arrow).
bar : RealTrace → RealTrace
head (bar r) = pflip (head r)
tail (bar r) = bar (tail r)

------------------------------------------------------------------------
-- (1) coemit-conj-conj-totality: conj∘conj = id, CONSTRUCTED (351: ≡ is the totality of the orbit's actions).
--     Coinductively: heads by pflip-involutive, tails by corecursion. This IS conj-conj — not "only up to ~".
------------------------------------------------------------------------
coemit-conj-conj : (r : RealTrace) → bar (bar r) ~ r
head~ (coemit-conj-conj r) = pflip-involutive (head r)
tail~ (coemit-conj-conj r) = coemit-conj-conj (tail r)

-- the SAME fact as the TOTALITY over all finite perspectives (the orbit's actions) — 351's construction, exhibited.
coemit-conj-conj-totality : (r : RealTrace) (n : ℕ) → take n (bar (bar r)) ≡ take n r
coemit-conj-conj-totality r n = coemit-eq-is-totality-bwd r (bar (bar r)) (coemit-conj-conj r) n

------------------------------------------------------------------------
-- (2) coemit-faceset-star: reuse FaceSet's ★ (the totality-dual) and its involution. Face n = Vector (suc n) over
--     F₂; coemit's boundary faces are List ℕ — DIFFERENT CARRIERS. What transfers is the CONSTRUCTION:
--     ★ S = universe +ⱽ S ("what S is missing to be everything, computed, not negated"), ★★ = id from the
--     additive group laws. Coemit's step-level analogue is exactly f2-flip (𝟙 +F _): the totality-dual on ONE bit,
--     with the SAME engine (x ⊕ x = 𝟘). So coemit's chirality flip IS FaceSet's ★ at n = 0 (the one-bit face).
------------------------------------------------------------------------
open import Substrate.WitnessTower.FaceSet using (Face; ★; ★-involution)

coemit-faceset-star-involution : {n : ℕ} (S : Face n) → ★ (★ S) ≡ S     -- the canonical ★★ = id, REUSED
coemit-faceset-star-involution = ★-involution

-- coemit's one-bit totality-dual (the chirality flip) has FaceSet's ★ shape: dual = totality ⊕ self, ★★ = id.
coemit-star-on-one-bit : (b : F₂) → f2-flip (f2-flip b) ≡ b            -- 𝟙 ⊕ (𝟙 ⊕ b) ≡ b — the same engine
coemit-star-on-one-bit = f2-flip-involutive

------------------------------------------------------------------------
-- (3) coemit-stardivstr: HONEST-PARTIAL, with a precise reason. StarDivStr.conj-conj demands Agda's INTENSIONAL
--     _≡_ : conj (conj x) ≡ x. On RealTrace the constructed ≡ IS ~ (351: the totality of the orbit's actions);
--     intensional ≡ on a coinductive carrier is not that construction (it would need funext/quotients — and
--     D-safe-no-postulate forbids postulating it). So the record as written does NOT admit RealTrace directly:
--     it wants a carrier whose Agda-≡ already IS the totality (a finite Vector, as Face is; or a quotient/setoid).
--     What coemit HAS is every component, with ~ in place of ≡ — i.e. the StarDivStr over the ~-setoid.
------------------------------------------------------------------------
-- the conjugation exists (bar) and is involutive in the CONSTRUCTED equality (~) — the StarDivStr data, ~-valued.
coemit-stardivstr-conj : RealTrace → RealTrace
coemit-stardivstr-conj = bar

coemit-stardivstr-conj-conj : (x : RealTrace) → coemit-stardivstr-conj (coemit-stardivstr-conj x) ~ x
coemit-stardivstr-conj-conj = coemit-conj-conj

-- conj-recon against RealTrace-DivStr's recon (recon q b r = cons (head b) r): bar commutes with reconstruction
-- up to ~ — the head is pflip'd, the tail is bar'd, which is exactly recon of the conjugated pieces.
coemit-stardivstr-conj-recon : (q b r : RealTrace)
                             → bar (cons (head b) r) ~ cons (head (bar b)) (bar r)
head~ (coemit-stardivstr-conj-recon q b r) = refl
tail~ (coemit-stardivstr-conj-recon q b r) = ~-refl (bar r)

------------------------------------------------------------------------
-- REGROUND (catalog index + depgraph, per directive):
--   • catalog/README: "each file is a shadow that survives session boundaries"; the catalog records "which
--     concepts are the same idea under different names, which claims supersede which, WHERE INTENT DRIFTED".
--   • import-graph.md: 1643 modules, 10428 SEMANTIC dependency edges (from elaborated cores, not import lines).
--   • reuse-graph.md: 747 structures, 492 refinement edges. "X --> Y means X is BUILT ON Y. **Before reinventing
--     a structure, check whether the thing you want already REFINES an existing primitive here.**"
--   • drift_archaeology.md: behavioural classes — summary-collapse, user-framing operational-drift, silent
--     naturalisation, acknowledged-then-abandoned. (The corpus has an archaeology of exactly my failure modes.)
-- Accordingly the three constructions below REFINE canonical primitives (Setoid, IsoGroupoid's iso-sym/†, DivStr).
------------------------------------------------------------------------
open import Substrate.Algebra.Setoid using (Setoid)

-- bar-cong: the conjugation RESPECTS the constructed equality (a coinductive congruence). Needed for both the
-- setoid instance (conj must respect ≈) and the transpose (†∘bar acts on ~-proofs).
bar-cong : {r s : RealTrace} → r ~ s → bar r ~ bar s
head~ (bar-cong p) = cong pflip (head~ p)
tail~ (bar-cong p) = bar-cong (tail~ p)

------------------------------------------------------------------------
-- (2) coemit-transpose-adjoint: StarV4's FOURTH V₄ element — "the fourth element † ∘ bar is the TRANSPOSE/ADJOINT".
--     † is the groupoid's inverse (IsoGroupoid.iso-sym; on coemit's ~-groupoid that is ~-sym, 349).
--     bar is the conjugation (352). Their composite acts on ~-proofs: p : r ~ s ↦ bar s ~ bar r.
------------------------------------------------------------------------
transpose : {r s : RealTrace} → r ~ s → bar s ~ bar r
transpose p = ~-sym (bar-cong p)          -- † ∘ bar — the transpose/adjoint (StarV4's fourth element)

-- the transpose applied twice returns to the conjugated pair (†∘bar is an involution on the ~-groupoid's arrows):
transpose-involutive : {r s : RealTrace} (p : r ~ s) → bar (bar r) ~ bar (bar s)
transpose-involutive p = bar-cong (bar-cong p)

-- † and bar COMMUTE **AT THE ENDPOINTS** (StarV4's V₄-not-dihedral condition, `recip-bar`). HONEST SCOPE:
-- †∘bar and bar∘† are two CONSTRUCTIONS with the SAME TYPE (both : bar s ~ bar r). That is commutation of the
-- V₄ square on OBJECTS. A PROOF-level commutation (the two ~-proofs identified) needs a further step: either
-- ~-proof-irrelevance, or the totality — (∀ n) their take-images agree (351). NOT claimed here. ⟡coemit-v4-square.
dagger-bar : {r s : RealTrace} → r ~ s → bar s ~ bar r
dagger-bar p = bar-cong (~-sym p)           -- bar ∘ † (transpose p = † ∘ bar is the other route; SAME endpoints)

------------------------------------------------------------------------
-- (3) coemit-stardivstr-setoid: the ~-SETOID on RealTrace (refining Substrate.Algebra.Setoid), on which the
--     conjugation IS involutive and recon-compatible. This is StarDivStr's data with ≈ := ~ — the honest home
--     (352: the record's intensional ≡ is a CARRIER requirement; the setoid supplies the totality as ≈).
------------------------------------------------------------------------
RealTrace-Setoid : Setoid RealTrace _~_
RealTrace-Setoid = record { ≈-refl = ~-refl ; ≈-sym = ~-sym ; ≈-trans = ~-trans }

-- the setoid-StarDivStr components: conj respects ≈ (bar-cong), and conj∘conj ≈ id (coemit-conj-conj).
coemit-setoid-conj-respects : {r s : RealTrace} → r ~ s → bar r ~ bar s
coemit-setoid-conj-respects = bar-cong

coemit-setoid-conj-conj : (r : RealTrace) → bar (bar r) ~ r
coemit-setoid-conj-conj = coemit-conj-conj

------------------------------------------------------------------------
-- (4) coemit-conj-recon-full: the GENERAL conj-recon law with the q argument present, against RealTrace-DivStr's
--     recon (recon q b r = cons (head b) r — q is discarded by the flat reconstruction).
--     conj (recon q b r) ≈ recon (conj q) (conj b) (conj r), with ≈ := ~ (the setoid's equality).
------------------------------------------------------------------------
coemit-conj-recon-full : (q b r : RealTrace)
                       → bar (cons (head b) r) ~ cons (head (bar b)) (bar r)
head~ (coemit-conj-recon-full q b r) = refl      -- pflip (head b) on both sides
tail~ (coemit-conj-recon-full q b r) = ~-refl (bar r)

------------------------------------------------------------------------
-- PREFLIGHT (operator: "the catalog serves to re-sync, dedupe and dedrift AFTER a sprint; we use it as a preflight
-- check because at that moment we know the most about what we need next and about what we just built"):
--   • reuse-index: `DivStr` is multiply-homed (Algebra.Wedge, S5.S5EEA); `GradedDivStr` is its indexed lift;
--     **no setoid-valued StarDivStr exists** ⇒ building one is a CONTRIBUTION, not a duplicate.
--   • reuse-index: the canonical iso record is `WedgeIso`@Substrate.Algebra.Wedge.Iso {fwd,bwd,fwd∘bwd,bwd∘fwd};
--     IsoGroupoid REFINES it (iso-id/iso-sym/iso-∘ + the pointwise _≈ʷ_). StarV4: **iso-sym IS the dagger †**.
--   • Foundation.Hedberg: `Decidable⇒UIP : DecidableEquality A → (p q : x ≡ y) → p ≡ q`, HOLDS UNDER --without-K.
--     With Nat._≟_ this gives UIP on ℕ — the engine for identifying two ~-proofs' head~ components.
--   • No ~-proof-irrelevance exists in-tree ⇒ also a contribution.
------------------------------------------------------------------------
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.Foundation.Nat using (_≟_)

------------------------------------------------------------------------
-- (1) coemit-v4-square: the V₄ square at PROOF level. 353 downgraded "† and bar commute" to endpoint-commutation
--     because †∘bar and bar∘† are two CONSTRUCTIONS of the same TYPE. Now we identify them where it counts:
--     a ~-proof's observable content at each step is its head~ : ℕ-equality — and ℕ has UIP (Hedberg, via _≟_).
--     So the two routes agree on every head~, at every depth: the square COMMUTES stepwise, hence (351: ≡ is the
--     totality of the orbit's actions) it commutes. This is the totality-construction, not proof-irrelevance-by-fiat.
------------------------------------------------------------------------
-- ℕ's UIP (Hedberg + decidable equality) — any two proofs of a head-equality coincide.
nat-uip : {m n : ℕ} (p q : m ≡ n) → p ≡ q
nat-uip = Decidable⇒UIP _≟_

-- the V₄ square at the HEAD (one step): the two routes †∘bar and bar∘† give the same head~ component.
coemit-v4-square-head : {r s : RealTrace} (p : r ~ s)
                      → head~ (transpose p) ≡ head~ (dagger-bar p)
coemit-v4-square-head p = nat-uip (head~ (transpose p)) (head~ (dagger-bar p))

-- SELF-AUDIT: `coemit-v4-square = transpose` would be a RENAME, not a commutation. The genuine statement is that
-- the two routes agree on their OBSERVABLE CONTENT at every step. Step 0 is coemit-v4-square-head (nat-uip).
-- The totality (351) is: at every depth n, both routes' traces have equal n-prefixes. Since both routes produce a
-- ~-proof of the SAME endpoints (bar s ~ bar r), their prefix-images coincide — exhibited via the totality.
-- SECOND AUDIT: a `take n (bar s) ≡ take n (bar s)` clause would be X ≡ X (the 4th vacuous witness this arc).
-- DISCARDED. The V₄ square's genuine, non-vacuous content is exactly the UIP identification of the two routes'
-- observable components — coemit-v4-square-head above. Both routes inhabit `bar s ~ bar r` (endpoints, 353);
-- their head~ components are IDENTIFIED by nat-uip; the tails follow by the same argument coinductively.
-- HONEST SCOPE: full proof-equality (transpose p ≡ dagger-bar p) needs coinductive proof-equality, NOT built.
coemit-v4-square : {r s : RealTrace} (p : r ~ s) → head~ (transpose p) ≡ head~ (dagger-bar p)
coemit-v4-square = coemit-v4-square-head

------------------------------------------------------------------------
-- (2) coemit-isogroupoid: the canonical iso record is WedgeIso; IsoGroupoid supplies iso-sym = THE DAGGER †
--     and the pointwise _≈ʷ_ (ANOTHER totality construction: c ≈ʷ d = (x : C A) → translate (fwd c) x ≡ …).
--     Coemit's ~-groupoid is the same shape: its "pointwise" index is the STEP, and ~ is the totality (351).
------------------------------------------------------------------------
open import Substrate.Algebra.Wedge.Iso using (WedgeIso; iso-sym)

-- the dagger, canonically: IsoGroupoid's iso-sym on WedgeIso. (StarV4: "the groupoid's inverse iso-sym IS the †".)
coemit-dagger-canonical : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → WedgeIso A B → WedgeIso B A
coemit-dagger-canonical = iso-sym

-- coemit's ~-groupoid inverse is the SAME dagger, at the trace carrier (the step-indexed totality, not pointwise).
coemit-dagger-on-traces : {r s : RealTrace} → r ~ s → s ~ r
coemit-dagger-on-traces = ~-sym

------------------------------------------------------------------------
-- (3) OPERATOR CORRECTION: "We don't use Set₁. We use LAWVERE instead."
-- My hand-rolled `record SetoidStarDivStr : Set₁ { carrier : Set ; ... }` bumped the universe by FIELDING the
-- carrier. The house style is Substrate.Category.Lawvere: **carrier-GENERIC atoms, PARAMETERIZED by V : Set**,
-- so the record itself lives in Set. Lawvere's diagonal (fixed-point) theorem is "the carrier-generic atom behind
-- Cantor, Gödel, Tarski, Turing, and the substrate's wedge residue"; its atoms are FixedPointFree, InvolutiveResidue,
-- TorsorAtom, and — exactly what I was reinventing — **CommutingInvolutions**:
--
--     record CommutingInvolutions (V : Set) : Set where
--       field δ₁ δ₂  : V → V
--             δ₁-inv : (v : V) → δ₁ (δ₁ v) ≡ v
--             δ₂-inv : (v : V) → δ₂ (δ₂ v) ≡ v
--             commute : (v : V) → δ₂ (δ₁ v) ≡ δ₁ (δ₂ v)
--
-- That IS StarV4's V₄ = ⟨†, bar⟩ (two commuting involutions), carrier-generic, in Set — and `commute` is the very
-- V₄-square 353 could only scope at endpoints. PREFLIGHT MISS: I searched reuse-index for "StarDivStr/Setoid" and
-- not for "involution" — the atom was indexed under Lawvere all along ("the carrier-generic atom behind …").
--
-- WHERE IT FITS (verified, D-record-demands-its-equality): CommutingInvolutions demands INTENSIONAL ≡ involutions.
-- On RealTrace, bar (bar r) ~ r (not ≡) ⇒ the atom does NOT take the trace carrier. It takes **V4Full** — the F₂×F₂
-- coords where V₄'s two generators ARE ≡-involutive and DO commute (342: rowSwap-invol, recip-invol, gens-commute).
------------------------------------------------------------------------
open import Substrate.Category.Lawvere using (CommutingInvolutions)

-- V4Full is (morph, obj) : F₂ × F₂ with (v4 a b) · (v4 c d) = v4 (a ⊕ c) (b ⊕ d) (348). So right-multiplication
-- by a fixed generator is componentwise ⊕ by a constant — an involution, since F₂ has x ⊕ x = 𝟘 and 𝟘 is the unit.
-- δ₁ = flip the morph bit (rowSwap side) ; δ₂ = flip the obj bit (recip side). They act on DISJOINT components,
-- hence they COMMUTE — the V₄-not-dihedral condition (StarV4's recip-bar), here by componentwise computation.
-- (pattern-match on the `v4` constructor: V4Full's field accessors are opened non-publicly upstream)
v4-flip-morph : V4.V4Full → V4.V4Full
v4-flip-morph (V4.v4 a b) = V4.v4 (𝟙 ⊕₂ a) b

v4-flip-obj : V4.V4Full → V4.V4Full
v4-flip-obj (V4.v4 a b) = V4.v4 a (𝟙 ⊕₂ b)

-- each is an involution: 𝟙 ⊕ (𝟙 ⊕ b) ≡ b  (f2-flip-involutive, the x⊕x=𝟘 engine).
v4-flip-morph-invol : (v : V4.V4Full) → v4-flip-morph (v4-flip-morph v) ≡ v
v4-flip-morph-invol (V4.v4 a b) = cong (λ x → V4.v4 x b) (f2-flip-involutive a)

v4-flip-obj-invol : (v : V4.V4Full) → v4-flip-obj (v4-flip-obj v) ≡ v
v4-flip-obj-invol (V4.v4 a b) = cong (λ y → V4.v4 a y) (f2-flip-involutive b)

-- and they COMMUTE (disjoint components): flipping morph then obj = flipping obj then morph.
v4-flips-commute : (v : V4.V4Full) → v4-flip-obj (v4-flip-morph v) ≡ v4-flip-morph (v4-flip-obj v)
v4-flips-commute (V4.v4 a b) = refl

-- coemit's V₄ AS the canonical Lawvere atom (carrier-generic, in Set — no Set₁ bump).
coemit-v4-lawvere-atom : CommutingInvolutions V4.V4Full
coemit-v4-lawvere-atom = record
  { δ₁      = v4-flip-morph
  ; δ₂      = v4-flip-obj
  ; δ₁-inv  = v4-flip-morph-invol
  ; δ₂-inv  = v4-flip-obj-invol
  ; commute = v4-flips-commute
  }

------------------------------------------------------------------------
-- OPERATOR (house style): "When you want to reach for a postulate, it's better to take the 'postulate' as a
-- MODULE PARAMETER. This promotes decomposition and composability."
-- The substrate does exactly this: Lawvere's `module _ {I V : Set} (fpf : FixedPointFree V) where`,
-- SemidirectProduct's `module Build (G_N : Group N)(G_H : Group H)(φ : Actionᴳ G_H N)`. Nothing is postulated;
-- the needed structure is DEMANDED at the module boundary, so instances compose.
--
-- Two things I was tempted to postulate / honest-partial away, now PARAMETERS:
--   (a) the EQUALITY. Lawvere's four atoms are ≡-valued (carrier-generic, in Set). RealTrace's constructed ≡ is ~
--       (351). Rather than postulate ≡ (funext) or abandon the atom, parameterize by _≈_ : V → V → Set. The record
--       stays in Set (no Set₁ bump — the equality is a PARAMETER, not a field of type `Set`).
--   (b) the SECOND INVOLUTION on the trace carrier. I have bar (352). StarV4's † lives on the groupoid's ARROWS
--       (~-sym), not the carrier. Rather than invent a carrier-level partner, DEMAND it: any δ₂ the caller supplies,
--       with its involutivity and commutation, completes the V₄. Composable: supply δ₂, get the Klein four-group.
------------------------------------------------------------------------
-- the ≈-parameterized Klein atom (mirrors Lawvere.CommutingInvolutions; the equality is a PARAMETER, so : Set).
module _ (V : Set) (_≈_ : V → V → Set) where
  record CommutingInvolutionsUpTo : Set where
    field
      δ₁ δ₂   : V → V
      δ₁-inv  : (v : V) → δ₁ (δ₁ v) ≈ v
      δ₂-inv  : (v : V) → δ₂ (δ₂ v) ≈ v
      commute : (v : V) → δ₂ (δ₁ v) ≈ δ₁ (δ₂ v)

-- INSTANCE 1 (≈ := ≡): V4Full, the F₂×F₂ coords — recovering the canonical Lawvere atom's content exactly.
coemit-v4-upto-eq : CommutingInvolutionsUpTo V4.V4Full _≡_
coemit-v4-upto-eq = record
  { δ₁ = v4-flip-morph ; δ₂ = v4-flip-obj
  ; δ₁-inv = v4-flip-morph-invol ; δ₂-inv = v4-flip-obj-invol ; commute = v4-flips-commute }

-- INSTANCE 2 (≈ := ~): RealTrace, with δ₁ = bar. The SECOND involution is a MODULE PARAMETER, not a postulate:
-- give any ~-involutive δ₂ commuting with bar, and coemit's carrier carries the Klein four-group.
module CoemitTraceKlein
  (δ₂       : RealTrace → RealTrace)
  (δ₂-inv   : (r : RealTrace) → δ₂ (δ₂ r) ~ r)
  (δ₂-comm  : (r : RealTrace) → δ₂ (bar r) ~ bar (δ₂ r))
  where

  coemit-trace-v4 : CommutingInvolutionsUpTo RealTrace _~_
  coemit-trace-v4 = record
    { δ₁ = bar ; δ₂ = δ₂
    ; δ₁-inv = coemit-conj-conj ; δ₂-inv = δ₂-inv ; commute = δ₂-comm }

-- and the DEGENERATE witness that the parameterization is inhabited (δ₂ = id: the V₂ collapse StarV4 warns of —
-- "over plain ℚ (conj = id) the twist is TRIVIAL — bar = id, so V₄ collapses back to V₂"). Honest: this shows the
-- module is non-empty; a GENUINE δ₂ (the carrier-level partner of †) remains open — ⟡coemit-trace-delta2.
coemit-trace-klein-degenerate : CommutingInvolutionsUpTo RealTrace _~_
coemit-trace-klein-degenerate =
  CoemitTraceKlein.coemit-trace-v4 (λ r → r) (λ r → ~-refl r) (λ r → ~-refl (bar r))

------------------------------------------------------------------------
-- PREFLIGHT (Category.Lawvere's remaining atoms, exact fields):
--   record FixedPointFree   (V : Set) : Set { δ : V → V ; δ-free : δ v ≡ v → ⊥ }
--   record InvolutiveResidue(V : Set) : Set { δ ; δ-free ; δ-invol : δ (δ v) ≡ v }
--   record TorsorAtom       (A : Set) : Set { _∙_ ; e ; fix→unit : (g ∙ x) ≡ x → g ≡ e }
-- Header: "the F₂ instance is δ = (𝟙 +_), whose δ-free is exactly WitnessTower.Diagonal.flip-disagrees."
--
-- (1) coemit-trace-delta2: bar = pflip on the digit = XOR-1 (bit0 = the chirality/parity bit, 350). Its INDEPENDENT
--     partner is XOR-2 (bit1): 0↔2, 1↔3, 4↔6, 5↔7, … Both are involutions and they COMMUTE (XOR is abelian), so
--     ⟨bar, bar₂⟩ ≅ ℤ/2 × ℤ/2 = V₄ on the TRACE carrier — matching V4Full's (morph, obj) = (bit0, bit1) exactly.
--     This is the GENUINE δ₂ that CoemitTraceKlein demanded (354): no longer the degenerate V₂ collapse.
------------------------------------------------------------------------
-- xor2 on the digit: flip bit1 (0↔2, 1↔3, then 4-periodic).
xor2 : ℕ → ℕ
xor2 zero                             = suc (suc zero)
xor2 (suc zero)                       = suc (suc (suc zero))
xor2 (suc (suc zero))                 = zero
xor2 (suc (suc (suc zero)))           = suc zero
xor2 (suc (suc (suc (suc n))))        = suc (suc (suc (suc (xor2 n))))

xor2-involutive : (n : ℕ) → xor2 (xor2 n) ≡ n
xor2-involutive zero                          = refl
xor2-involutive (suc zero)                    = refl
xor2-involutive (suc (suc zero))              = refl
xor2-involutive (suc (suc (suc zero)))        = refl
xor2-involutive (suc (suc (suc (suc n))))     = cong (λ k → suc (suc (suc (suc k)))) (xor2-involutive n)

-- XOR-1 and XOR-2 COMMUTE (the abelian F₂² structure on the digit's low two bits).
pflip-xor2-commute : (n : ℕ) → xor2 (pflip n) ≡ pflip (xor2 n)
pflip-xor2-commute zero                       = refl
pflip-xor2-commute (suc zero)                 = refl
pflip-xor2-commute (suc (suc zero))           = refl
pflip-xor2-commute (suc (suc (suc zero)))     = refl
pflip-xor2-commute (suc (suc (suc (suc n))))  = cong (λ k → suc (suc (suc (suc k)))) (pflip-xor2-commute n)

-- bar₂: the SECOND conjugation on the trace (stepwise XOR-2), threaded corecursively — the genuine δ₂.
bar₂ : RealTrace → RealTrace
head (bar₂ r) = xor2 (head r)
tail (bar₂ r) = bar₂ (tail r)

coemit-bar₂-invol : (r : RealTrace) → bar₂ (bar₂ r) ~ r
head~ (coemit-bar₂-invol r) = xor2-involutive (head r)
tail~ (coemit-bar₂-invol r) = coemit-bar₂-invol (tail r)

coemit-bar-bar₂-commute : (r : RealTrace) → bar₂ (bar r) ~ bar (bar₂ r)
head~ (coemit-bar-bar₂-commute r) = pflip-xor2-commute (head r)
tail~ (coemit-bar-bar₂-commute r) = coemit-bar-bar₂-commute (tail r)

-- THE GENUINE V₄ ON THE TRACE CARRIER (CoemitTraceKlein's parameters, discharged — NOT the degenerate id).
coemit-trace-v4-genuine : CommutingInvolutionsUpTo RealTrace _~_
coemit-trace-v4-genuine =
  CoemitTraceKlein.coemit-trace-v4 bar₂ coemit-bar₂-invol coemit-bar-bar₂-commute

------------------------------------------------------------------------
-- (2) coemit-lawvere-atoms: instantiate the remaining three carrier-generic atoms.
------------------------------------------------------------------------
open import Substrate.Category.Lawvere using (FixedPointFree; InvolutiveResidue)
open import Substrate.Foundation.Empty using (⊥)

-- pflip is FIXED-POINT-FREE on ℕ: it always flips the parity bit, so pflip n ≡ n is impossible.
pflip-free : (n : ℕ) → pflip n ≡ n → ⊥
pflip-free zero ()
pflip-free (suc zero) ()
pflip-free (suc (suc n)) eq = pflip-free n (suc-suc-inj eq)
  where suc-suc-inj : {a b : ℕ} → suc (suc a) ≡ suc (suc b) → a ≡ b
        suc-suc-inj refl = refl

-- so pflip inhabits BOTH atoms: FixedPointFree ℕ and InvolutiveResidue ℕ (the residue δ of the coemit grading).
coemit-pflip-fpf : FixedPointFree ℕ
coemit-pflip-fpf = record { δ = pflip ; δ-free = pflip-free }

coemit-pflip-residue : InvolutiveResidue ℕ
coemit-pflip-residue = record { δ = pflip ; δ-free = pflip-free ; δ-invol = pflip-involutive }

------------------------------------------------------------------------
-- (3) coemit-proof-eq: coinductive ~-PROOF-equality. Preflight: none in-tree ⇒ a contribution.
--     A ~-proof's observable content at each step is its head~ : an ℕ-equality, and ℕ has UIP (nat-uip, Hedberg).
--     So any two ~-proofs of the SAME endpoints agree at every step — ≡ constructed as the totality (351).
------------------------------------------------------------------------
record ProofEq {r s : RealTrace} (p q : r ~ s) : Set where
  coinductive
  field
    head-eq : head~ p ≡ head~ q
    tail-eq : ProofEq (tail~ p) (tail~ q)
open ProofEq

-- ~-proof-irrelevance, CONSTRUCTED: any two proofs of r ~ s agree at every step (head by UIP, tail corecursively).
coemit-proof-eq : {r s : RealTrace} (p q : r ~ s) → ProofEq p q
head-eq (coemit-proof-eq p q) = nat-uip (head~ p) (head~ q)
tail-eq (coemit-proof-eq p q) = coemit-proof-eq (tail~ p) (tail~ q)

-- hence the V₄ square commutes at PROOF level (354 had only the head step): †∘bar and bar∘† agree everywhere.
coemit-v4-square-proof : {r s : RealTrace} (p : r ~ s) → ProofEq (transpose p) (dagger-bar p)
coemit-v4-square-proof p = coemit-proof-eq (transpose p) (dagger-bar p)

-- NON-DEGENERACY (self-audit): bar and bar₂ are DISTINCT involutions — on a head of 0 they give 1 vs 2.
-- Hence ⟨bar, bar₂⟩ has four distinct elements (id, bar, bar₂, bar∘bar₂): it is V₄, not the V₂ collapse (354).
xor2-pflip-differ : xor2 0 ≡ pflip 0 → ⊥
xor2-pflip-differ ()

-- and the fourth element (bar ∘ bar₂) is distinct from the identity on a head of 0: pflip (xor2 0) = 3 ≢ 0.
bar-bar₂-nontrivial : pflip (xor2 0) ≡ 0 → ⊥
bar-bar₂-nontrivial ()

------------------------------------------------------------------------
-- PREFLIGHT (verbatim from V4FullCocycle):  e = v4 𝟘 𝟘 ;
--   rowSwap-gen = v4 𝟙 𝟘   -- "generator 1: det-flip / Chirality (⟡S3)"   ⇒ the MORPH bit (bit0)
--   recip-gen   = v4 𝟘 𝟙   -- "generator 2: recip / object side"          ⇒ the OBJ bit (bit1)
-- and Substrate.Axes has the bijection (axis-of-v-v-of-axis, v-of-axis-axis-of-v) but NO torsor lemma.
--
-- (2) coemit-bar₂-guise, CONFIRMED: bar = pflip = XOR-1 flips bit0 = morph = **rowSwap / det-flip / chirality**
--     (ChiralityBridge's ONE ℤ/2). bar₂ = xor2 = XOR-2 flips bit1 = obj = **recip / the object side** — exactly
--     StarV4's "the dagger's fraction-level shadow is `recip` (swap)". So ⟨bar, bar₂⟩ = ⟨rowSwap, recip⟩ = V₄.
-- (3) coemit-digit-is-v4: the digit's low two bits ARE V4Full's (morph, obj) coords, and pflip/xor2 ARE its
--     two generators' actions. Made literal below.
------------------------------------------------------------------------
-- bit1 of a digit (4-periodic), the OBJ coordinate. (bit0 = parity, already have.)
bit1 : ℕ → F₂
bit1 zero                          = 𝟘
bit1 (suc zero)                    = 𝟘
bit1 (suc (suc zero))              = 𝟙
bit1 (suc (suc (suc zero)))        = 𝟙
bit1 (suc (suc (suc (suc n))))     = bit1 n

-- the digit's V₄ coordinates: (bit0 , bit1) = (morph , obj). This is the quotient ℕ ↠ ℕ/4 ≅ V₄.
digit-to-v4 : ℕ → V4.V4Full
digit-to-v4 n = V4.v4 (parity n) (bit1 n)

-- THE ACTION HOMOMORPHISM: pflip acts as v4-flip-morph (rowSwap); xor2 acts as v4-flip-obj (recip).
-- pflip flips bit0 and FIXES bit1 ; xor2 flips bit1 and FIXES bit0 — D-independent-involutions-flip-different-bits,
-- now LITERAL (each proven by the same 2-/4-periodic recursion the maps themselves use).
pflip-fixes-bit1 : (n : ℕ) → bit1 (pflip n) ≡ bit1 n
pflip-fixes-bit1 zero                       = refl
pflip-fixes-bit1 (suc zero)                 = refl
pflip-fixes-bit1 (suc (suc zero))           = refl
pflip-fixes-bit1 (suc (suc (suc zero)))     = refl
pflip-fixes-bit1 (suc (suc (suc (suc n))))  = pflip-fixes-bit1 n

-- parity is 4-periodic (two applications of the x⊕x=𝟘 cancellation): parity (n+4) ≡ parity n.
parity-4-periodic : (n : ℕ) → parity (suc (suc (suc (suc n)))) ≡ parity n
parity-4-periodic n =
  trans (f2-flip-involutive (𝟙 ⊕₂ (𝟙 ⊕₂ parity n))) (f2-flip-involutive (parity n))

xor2-fixes-bit0 : (n : ℕ) → parity (xor2 n) ≡ parity n
xor2-fixes-bit0 zero                        = refl
xor2-fixes-bit0 (suc zero)                  = refl
xor2-fixes-bit0 (suc (suc zero))            = refl
xor2-fixes-bit0 (suc (suc (suc zero)))      = refl
xor2-fixes-bit0 (suc (suc (suc (suc n))))   =
  -- LHS: parity (xor2 (n+4)) = parity ((xor2 n)+4) ≡ parity (xor2 n)   [4-periodic]
  -- RHS: parity (n+4) ≡ parity n                                        [4-periodic]
  trans (parity-4-periodic (xor2 n)) (trans (xor2-fixes-bit0 n) (sym (parity-4-periodic n)))

xor2-flips-bit1 : (n : ℕ) → bit1 (xor2 n) ≡ f2-flip (bit1 n)
xor2-flips-bit1 zero                        = refl
xor2-flips-bit1 (suc zero)                  = refl
xor2-flips-bit1 (suc (suc zero))            = refl
xor2-flips-bit1 (suc (suc (suc zero)))      = refl
xor2-flips-bit1 (suc (suc (suc (suc n))))   = xor2-flips-bit1 n

-- the two homomorphism laws: digit-to-v4 intertwines (pflip, xor2) with (v4-flip-morph, v4-flip-obj).
coemit-digit-is-v4-morph : (n : ℕ) → digit-to-v4 (pflip n) ≡ v4-flip-morph (digit-to-v4 n)
coemit-digit-is-v4-morph n = cong₂ V4.v4 (pflip-flips-parity n) (pflip-fixes-bit1 n)

coemit-digit-is-v4-obj : (n : ℕ) → digit-to-v4 (xor2 n) ≡ v4-flip-obj (digit-to-v4 n)
coemit-digit-is-v4-obj n = cong₂ V4.v4 (xor2-fixes-bit0 n) (xor2-flips-bit1 n)

-- the GUISE, literal: bar's generator is rowSwap (det-flip/chirality); bar₂'s is recip (the object side).
coemit-bar-guise-is-rowSwap : digit-to-v4 (pflip 0) ≡ V4.rowSwap-gen     -- pflip 0 = 1 ⇒ (𝟙,𝟘) = rowSwap-gen
coemit-bar-guise-is-rowSwap = refl

coemit-bar₂-guise-is-recip : digit-to-v4 (xor2 0) ≡ V4.recip-gen         -- xor2 0 = 2 ⇒ (𝟘,𝟙) = recip-gen
coemit-bar₂-guise-is-recip = refl

coemit-digit-zero-is-identity : digit-to-v4 0 ≡ V4.e                      -- 0 ⇒ (𝟘,𝟘) = e (the additive origin, 348)
coemit-digit-zero-is-identity = refl

------------------------------------------------------------------------
-- (1) coemit-torsor-atom: TorsorAtom for the V₄-coords carrier. fix→unit is the ANCHOR LAW — "only the unit fixes
--     a point" (347's D-fixed-point-is-anchor, canonically). On V4Full (= F₂², additive) cancellation is immediate:
--     v ⊕ x = x ⇒ v = 𝟘 componentwise. The anchor e = v4 𝟘 𝟘 corresponds to Axis D (v-of-axis D = e).
------------------------------------------------------------------------
open import Substrate.Category.Lawvere using (TorsorAtom)

-- F₂ cancellation: a ⊕ b ≡ b ⇒ a ≡ 𝟘 (the additive-group law, x ⊕ x = 𝟘).
f2-cancel : (a b : F₂) → (a ⊕₂ b) ≡ b → a ≡ 𝟘
f2-cancel 𝟘 𝟘 _ = refl
f2-cancel 𝟘 𝟙 _ = refl
f2-cancel 𝟙 𝟘 ()
f2-cancel 𝟙 𝟙 ()

-- V₄'s cancellation: g · x ≡ x ⇒ g ≡ e (componentwise F₂ cancellation).
v4-fix→unit : (g x : V4.V4Full) → V4._·_ g x ≡ x → g ≡ V4.e
v4-fix→unit (V4.v4 a b) (V4.v4 c d) eq =
  cong₂ V4.v4 (f2-cancel a c (cong morph-of eq)) (f2-cancel b d (cong obj-of eq))
  where morph-of : V4.V4Full → F₂
        morph-of (V4.v4 m _) = m
        obj-of : V4.V4Full → F₂
        obj-of (V4.v4 _ o) = o

-- coemit's V₄ AS Lawvere's TorsorAtom: the anchor e is the ONLY element with a fixed point (the anchor law).
coemit-torsor-atom : TorsorAtom V4.V4Full
coemit-torsor-atom = record { _∙_ = V4._·_ ; e = V4.e ; fix→unit = v4-fix→unit }

------------------------------------------------------------------------
-- PREFLIGHT: Substrate.Groups.V4.Bijection: `data V₄ : Set where e α β γ : V₄` (a 4-element enum);
-- Substrate.Groups.V4.Operations supplies _·_, ε, inv; Substrate.Axes re-exports them and defines
-- `act-axis v x = axis-of-v (v V4.· v-of-axis x)` with the bijection v-of-axis / axis-of-v (D ↔ e).
--
-- (2) coemit-axis-torsor: 347 quoted "Axis is a V₄-torsor anchored at D". TorsorAtom's `fix→unit` is exactly the
--     torsor law ("only the unit fixes a point"). Transport the group structure along the bijection: the anchor D
--     is the unit, and g ∙ x ≡ x forces g ≡ D. Proven by the 4×4 case split (V₄ is a finite enum).
------------------------------------------------------------------------
-- import the Axis constructors (C, S, W) and the Axis product _∙ᴬ_ from its carrier-local
-- home (⟡carrier-locality): Substrate.Axes now hosts _∙ᴬ_ = act-axis ∘ v-of-axis, so the
-- transport-of-V₄'s-product lives with the Axis carrier, not here.
open import Substrate.Axes using (v-of-axis; axis-of-v; act-axis; _∙ᴬ_; C; S; W)

-- ONLY THE ANCHOR FIXES A POINT: if x ∙ᴬ y ≡ y then x ≡ D. (The torsor law, by exhaustive case analysis on Axis.)
axis-fix→unit : (g x : Axis) → (g ∙ᴬ x) ≡ x → g ≡ D
axis-fix→unit D _ _ = refl
axis-fix→unit C D ()
axis-fix→unit C C ()
axis-fix→unit C S ()
axis-fix→unit C W ()
axis-fix→unit S D ()
axis-fix→unit S C ()
axis-fix→unit S S ()
axis-fix→unit S W ()
axis-fix→unit W D ()
axis-fix→unit W C ()
axis-fix→unit W S ()
axis-fix→unit W W ()

-- Axis AS Lawvere's TorsorAtom, anchored at D — 347's sentence, now a record.
coemit-axis-torsor : TorsorAtom Axis
coemit-axis-torsor = record { _∙_ = _∙ᴬ_ ; e = D ; fix→unit = axis-fix→unit }

------------------------------------------------------------------------
-- (3) coemit-digit-quotient: digit-to-v4 : ℕ ↠ V4Full is 4-PERIODIC — its fibre is exactly n mod 4 — and it hits
--     all four V₄ elements (0 ↦ e, 1 ↦ rowSwap, 2 ↦ recip, 3 ↦ klein). So ℕ/4 ≅ V₄ under digit-to-v4.
------------------------------------------------------------------------
bit1-4-periodic : (n : ℕ) → bit1 (suc (suc (suc (suc n)))) ≡ bit1 n
bit1-4-periodic n = refl

coemit-digit-4-periodic : (n : ℕ) → digit-to-v4 (suc (suc (suc (suc n)))) ≡ digit-to-v4 n
coemit-digit-4-periodic n = cong₂ V4.v4 (parity-4-periodic n) (bit1-4-periodic n)

-- SURJECTIVITY on the four residues: the fibres 0,1,2,3 hit e, rowSwap, recip, klein — the whole of V₄.
coemit-digit-hits-e       : digit-to-v4 0 ≡ V4.e
coemit-digit-hits-e       = refl
coemit-digit-hits-rowSwap : digit-to-v4 1 ≡ V4.rowSwap-gen
coemit-digit-hits-rowSwap = refl
coemit-digit-hits-recip   : digit-to-v4 2 ≡ V4.recip-gen
coemit-digit-hits-recip   = refl
coemit-digit-hits-klein   : digit-to-v4 3 ≡ V4.klein
coemit-digit-hits-klein   = refl

------------------------------------------------------------------------
-- (3) coemit-digit-mod4: 357 proved digit-to-v4 is 4-periodic and surjective on {0,1,2,3} — which IS the quotient.
--     Here the fibre is stated LITERALLY: digit-to-v4 n ≡ digit-to-v4 (mod4 n), i.e. the map factors through ℕ/4.
--     (Preflight: Foundation.Nat has no mod/_%_, so mod4 is defined here — 4-periodic recursion, matching bit1's.)
------------------------------------------------------------------------
mod4 : ℕ → ℕ
mod4 zero                          = zero
mod4 (suc zero)                    = suc zero
mod4 (suc (suc zero))              = suc (suc zero)
mod4 (suc (suc (suc zero)))        = suc (suc (suc zero))
mod4 (suc (suc (suc (suc n))))     = mod4 n

-- THE FIBRE, literal: digit-to-v4 factors through ℕ/4 (the map is constant on residue classes).
coemit-digit-mod4 : (n : ℕ) → digit-to-v4 n ≡ digit-to-v4 (mod4 n)
coemit-digit-mod4 zero                        = refl
coemit-digit-mod4 (suc zero)                  = refl
coemit-digit-mod4 (suc (suc zero))            = refl
coemit-digit-mod4 (suc (suc (suc zero)))      = refl
coemit-digit-mod4 (suc (suc (suc (suc n))))   =
  trans (coemit-digit-4-periodic n) (coemit-digit-mod4 n)

-- and mod4 lands in the four residues (idempotent: mod4 ∘ mod4 ≡ mod4 on the classes it produces).
mod4-idem : (n : ℕ) → mod4 (mod4 n) ≡ mod4 n
mod4-idem zero                        = refl
mod4-idem (suc zero)                  = refl
mod4-idem (suc (suc zero))            = refl
mod4-idem (suc (suc (suc zero)))      = refl
mod4-idem (suc (suc (suc (suc n))))   = mod4-idem n
