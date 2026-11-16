# ⟡rig-UP-cat-graded — the Set₀-graded rig CATEGORY (spec, 2026-07-11). Pursuing ⟡rig-UP-charter.

## The dissolution (6th of the arc, same move)
Category.SymmetricMonoidal is Set(lsuc …) ONLY because CategoryOf FIELDS `Obj : Set ℓO` (the
set1-carrier-always-parameterize trap). Category.Site already shows the fix: PARAMETERIZE Obj/Hom
(`(Obj : Set)(Hom : Obj → Obj → Set)` as module params, not fields). Apply it, GRADED: objects are
the grades, morphisms are the orderings/permutations. Then the rig category is Set₀ — the formalizable
(Set₀-graded) categorical UP, the last Set₁ the arc only demarcated, now built the same way as the rest.

## The object (canonical model = the orientation rig = the groupoid of finite orderings)
Obj = ℕ (grades) ; Hom i j = permutations (a groupoid of bijections): model Hom i j as
   Hom i j = (i ≡ j) × Perm i    (or Σ (i≡j) λ _ → Perm i) — Set₀.  id = 1#-ish ; ∘ = Perm compose.
⊕ on objects = _+_ , ⊗ on objects = _*_ ; on MORPHISMS = the committed GradedBifunctor (⊕map/⊗map);
braiding morphisms = GradedBraid (blockSwap/factorSwap); naturality = GradedBraidNatural; the monoidal
data = GradedSymMonoidal (committed, OrientationSymMonoidal ⊕-symmon/⊗-symmon).

## Steps (incremental; --safe --without-K, zero postulates; green-or-honest). New module e.g.
   Substrate.WitnessTower.Wedge.OrientationRigCat.
S1 (THE DISSOLUTION — highest value): a `GradedRigCat` record, Obj : ℕ → Set and Hom parameterized
   (module params, NOT fields — mirror Site.agda's CoverData), bundling: object-monoid (+,*), morphism
   category (Hom, id, ∘ with assoc/unit), the two monoidal structures on objects+morphisms, the
   braidings-as-morphisms. TYPE-CHECK IT AT `Set` (NOT lsuc) — that IS the dissolution. Keep the
   coherence field-set minimal first (assoc/unit/braid-involution); add Laplaza incrementally.
S2 (instantiate): `orientationRigCat : GradedRigCat …` for the tower — Obj n = the orderings (⊤ per
   grade, or LehmerPath n), Hom = Perm-morphisms, reusing OrientationSymMonoidal/GradedBraid/
   GradedBifunctor instances. Concrete Set₀ rig category. This VINDICATES the charter: rig category IS Set₀.
S3 (reach — the functor UP): the free-rig-CATEGORY UP = initiality among GradedRigCat's. On OBJECTS it
   is the committed free-rig-algebra fold; on MORPHISMS the braidings generate everything (⟡rig-UP-free
   reachability), so the functor is determined by the generator + braiding-preservation. Reuse
   foldF-free-unique (objects) + the braiding generation. Deep — deliver S1+S2 first; S3 if reachable.

## Reuse (do NOT reprove)
OrientationSymMonoidal (⊕-symmon, ⊗-symmon), OrientationBimonoidal (GradedProductOver, GradedBraid,
GradedBraidNatural, GradedBifunctor, GradedSymMonoidal), OrientationBimonoidal.Properties (⊕/⊗-braid,
⊕/⊗-braid-nat), OrientationBifunctor (⊕/⊗-bifunctor), OrientationProduct (_⊗_, 1#), Enumerate (Perm),
Category.Site (the parameterize-Obj/Hom TEMPLATE). Grep Category/ for an existing composition/id on Perm.

## Honest bar
The Set₀-graded categorical UP is a DIFFERENT theorem than the Set₁ (quantify-over-large-categories) one
— it is the FORMALIZABLE version. Do NOT claim "eliminated THE Set₁"; claim "the categorical structure
is Set₀ when the object-carrier is parameterized" (the arc's move, at the last site). S1's record
type-checking at `Set` is the concrete proof.
