{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOMonadNT — ⟡extrude-io-monad-nt: the monad structure of IO as
-- η = ret, μ = join, with their NATURALITY and the MONAD COHERENCE laws — all POINTWISE at ≡ on IO-VALUES, so
-- NO funext (the operator's frame: use ≡/bisimilarity on values, not function-extensionality). This is the
-- (T, η, μ) content of the repo's Category.Monad, grounded at the value level (the NaturalTransformation
-- record's function-level naturality is the pointwise witnesses bundled — provided here pointwise, the
-- non-funext form).
--
--   η = ret,  μ = join
--   η-natural : map f (ret a) ≡ ret (f a)                       (η is natural — pointwise)
--   μ-natural : map f (join m) ≡ join (map (map f) m)           (μ is natural — pointwise)
--   μ∘η   : join (ret m) ≡ m                                    (left unit,  μ ∘ η_T = id)
--   μ∘Tη  : join (map ret m) ≡ m                                (right unit, μ ∘ T η = id)
--   μ∘μ   : join (join m) ≡ join (map join m)                   (associativity, μ ∘ μ_T = μ ∘ T μ)
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY η/μ (= ret/join) and the five
-- laws above, all at ≡ on IO-values (structural inductions, cong (emit o)). The framing ('the (T,η,μ) monad
-- structure, pointwise, no funext') is (prose: Category.Monad + 285; the NaturalTransformation RECORD bundling
-- needs pointwise→function eq, discharged by these pointwise witnesses or bisimilarity — the record scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeIOMonadNT (O : Set) where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Category.UniversalProperty.ExtrudeIO O
  using (IO; ret; emit; map; _>>=_; join; map-id; map-∘; >>=-assoc)

private variable A B C : Set

-- η and μ (the unit and multiplication):
η : {A : Set} → A → IO A
η = ret

μ : {A : Set} → IO (IO A) → IO A
μ = join

------------------------------------------------------------------------
-- ① NATURALITY (pointwise, at ≡ on values — no funext):
------------------------------------------------------------------------
η-natural : (f : A → B) (a : A) → map f (η a) ≡ η (f a)
η-natural f a = refl

μ-natural : (f : A → B) (m : IO (IO A)) → map f (μ m) ≡ μ (map (map f) m)
μ-natural f (ret m)    = refl
μ-natural f (emit o k) = cong (emit o) (μ-natural f k)

------------------------------------------------------------------------
-- ② THE MONAD COHERENCE LAWS (pointwise, at ≡ on values — the (T,η,μ) triangle+square, no funext):
------------------------------------------------------------------------
-- left unit: μ ∘ η_T = id  (join (ret m) = m):
μ∘η : (m : IO A) → μ (η m) ≡ m
μ∘η m = refl

-- right unit: μ ∘ T η = id  (join (map ret m) = m):
μ∘Tη : (m : IO A) → μ (map η m) ≡ m
μ∘Tη (ret a)    = refl
μ∘Tη (emit o k) = cong (emit o) (μ∘Tη k)

-- associativity: μ ∘ μ_T = μ ∘ T μ  (join (join m) = join (map join m)):
μ∘μ : (m : IO (IO (IO A))) → μ (μ m) ≡ μ (map μ m)
μ∘μ (ret m)    = refl
μ∘μ (emit o k) = cong (emit o) (μ∘μ k)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — IO's monad structure is η=ret, μ=join with naturality + the coherence laws,
-- all POINTWISE at ≡ on VALUES, NO funext): the repo's Category.Monad is (T, η, μ) with η/μ NaturalTrans-
-- formations. This grounds that content at the value level: η=ret, μ=join (①), η/μ natural pointwise (map f ∘
-- η = η ∘ f and map f ∘ μ = μ ∘ map (map f), pointwise), and the monad coherences (②: μ∘η=id left unit, μ∘Tη=id
-- right unit, μ∘μ associativity). Every law is a structural induction on IO (cong (emit o)) at ≡ on VALUES —
-- NO funext, NO Set₁. The NaturalTransformation RECORD's function-level naturality is exactly these pointwise
-- witnesses bundled (which needs pointwise→function eq, via these witnesses or bisimilarity — not funext); so
-- the monad structure is grounded, the record packaging scoped to the non-funext bundling. IO is a lawful
-- monad in the repo's sense, at the value level. Chain: 285 (the emit-monad + its laws) → 286b (η/μ + the
-- monad coherences, pointwise).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = η/μ (= ret/join), η-natural/μ-natural (pointwise), μ∘η/μ∘Tη/μ∘μ
-- (the monad coherence laws), all at ≡ on values, NO funext. SCOPED: bundling into the repo's
-- NaturalTransformation + Monad RECORDS needs the pointwise witnesses lifted to function-≡ — via bisimilarity
-- (ExtrudeBisimRun._≈_) or a setoid-enriched category, NOT funext (⟡extrude-io-monad-record). What's grounded:
-- the full (T,η,μ) monad structure of IO at the value level — pointwise naturality + the coherence laws, no
-- funext, the operator's non-funext frame realized.
------------------------------------------------------------------------
