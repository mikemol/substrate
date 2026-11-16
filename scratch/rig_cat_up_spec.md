# ⟡rig-UP-cat-UP — the functor UP is Set₀ (spec, 2026-07-11). The 7th dissolution.

## The claim to settle (probe, don't introspect)
The cat-graded agent called the functor-UP "irreducibly Set₁" because it quantifies ∀ target with
Obj:ℕ→Set. That CONFLATES two things. foldF-free-unique (COMMITTED, --safe) quantifies `∀ {C : ℕ → Set}`
and is FINE: a ∀-over-carriers THEOREM has a large TYPE (Set₁) but that is POLYMORPHISM, not a held Set₁
object. The functor-UP is the same shape. PROOF = build it: RigFunctor at `: Set`, UP statement compiles
--safe.

## Build (incremental; --safe --without-K, zero postulates; green-or-honest). Module e.g.
   Substrate.WitnessTower.Wedge.OrientationRigCatUP  (record) + .Properties (the proven UP, if it uses
   proof modules — respect def/proof separation, split like OrientationRigCat did).
S1 (THE DISSOLUTION — the notion is Set₀):
   record RigFunctor {Obj₁ Hom₁ Obj₂ Hom₂}(S : GradedRigCat Obj₁ Hom₁)(T : GradedRigCat Obj₂ Hom₂) : Set
     field F-obj : {n} → Obj₁ n → Obj₂ n
           F-hom : {i j}{a : Obj₁ i}{b : Obj₁ j} → Hom₁ a b → Hom₂ (F-obj a)(F-obj b)
           -- preservation: F-idHom, F-∘, F-⊕obj (u,∧), F-⊗obj, F-braid⊕, F-braid⊗
   Confirm it type-checks AT `: Set` (Obj/Hom are params — NOT Set-valued fields). + id-RigFunctor +
   comp-RigFunctor (the category of GradedRigCats). This green record at `: Set` IS the dissolution.
S2 (the UP statement, --safe): a type `RigCatInitial (free : GradedRigCat …)` =
   `∀ {Obj Hom}(T : GradedRigCat Obj Hom)(chosen data) → Σ (F : RigFunctor free T) (uniqueness)`.
   Its TYPE is Set₁ (∀ over Obj:ℕ→Set) — FINE, exactly like foldF-free-unique. It COMPILING --safe is
   the concrete refutation of "irreducibly Set₁".
S3 (CONTENT — prove it for the skeletal free object): the committed `orientationRigCatₛ` (OrientationRig
   Cat.Properties) has objects Objₛ n = singleton ⋆ and morphisms Homₛ = (i ≡ j). A RigFunctor out:
   F-obj {n} ⋆ is FORCED by ⊕obj/⊗obj-preservation + the generator image (F-obj at i+j = F-obj i ∧_T
   F-obj j, recursion on grade) ⇒ UNIQUE; F-hom (i≡j → …) sends refl ↦ idHom ⇒ trivial. So initiality
   REDUCES to the object-monoid freeness — reuse foldF-free-unique / the GradedProductOver structure on
   objects. Deliver as much as lands (existence: F-obj by grade recursion; uniqueness: by the ∧-preservation).

## Honest bar
This is the DECATEGORIFIED (identity-morphism) functor-UP — legitimate and Set₀, and it SETTLES the
Set₁ question (the notion + statement are Set₀; the theorem is provable). The FULL symmetric version
(free object = the Perm rig category with permutation morphisms) is ⟡rig-UP-cat-perm-UP, needs
⟡rig-UP-cat-perm first. Do NOT claim the full categorified UP; claim "RigFunctor and the functor-UP are
Set₀ (7th dissolution), proven for the skeletal free cat."

## Reuse
OrientationRigCat (GradedRigCat + fields idHom/∘/⊕obj/⊗obj/braid⊕/⊗), OrientationRigCat.Properties
(orientationRigCatₛ, Objₛ, Homₛ), OrientationBimonoidal (GradedProductOver, _∧_, u), OrientationRigFreeUP
(foldF-free-unique — the object-level precedent + possible reuse). Nat (_+_,_*_), Eq.

---
## CORRECTION (2026-07-11) — NO Σ. Expose the functor, mirror foldF-free-unique.
The Σ in S2 above was a fallback to ∃-collapse — against the arc's own expose-don't-collapse invariant.
numpy (rig_functor.py) confirmed the functor is a CONSTRUCTION, determined by F(generator): objects =
grade-fold (n = n-fold ⊕ of the generator), morphisms = braiding-word image (every perm is a braiding-
word, verified n≤6). So state the UP EXACTLY like foldF-free-unique — a construction + a uniqueness
lemma, NO Σ:

S2' (the UP, no Σ):
   freeFunctor : ∀ {Obj Hom} (T : GradedRigCat Obj Hom) (chosen : <the generator's image data in T>)
               → RigFunctor orientationRigCatₛ T                       -- THE CONSTRUCTION (exposed)
   freeFunctor-unique : ∀ {Obj Hom} (T : GradedRigCat Obj Hom) (chosen) (F : RigFunctor orientationRig
               Catₛ T) → <F agrees with the chosen data on the generator> → RigFunctor≈ F (freeFunctor T chosen)
   (Uniqueness stated as pointwise agreement on F-obj/F-hom — mirror fold-unique; you may need a
    RigFunctor extensional-equality `_≈_` if the record isn't refl-comparable, like GradedHomOver's _≈_.)

S3' (skeletal content): build `freeFunctor T chosen` — F-obj by grade recursion (F-obj ⋆_{0} = the
   ⊕obj unit of T, F-obj ⋆_{suc n} = <generator> ⊗/⊕-composed; objects singleton so it's forced),
   F-hom (Homₛ = i≡j) sends refl ↦ idHom T. Prove freeFunctor-unique by the same grade recursion +
   the ∧-preservation (reuse the fold-unique / GradedProductOver freeness pattern). NO Σ anywhere.

The `: Set` of RigFunctor (S1) stays the dissolution. The construction+uniqueness (no Σ) is the
mission-aligned UP. The full Perm-morphism version is ⟡rig-UP-cat-perm-UP (separate).
