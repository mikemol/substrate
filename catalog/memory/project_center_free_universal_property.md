---
name: project_center_free_universal_property
description: "The substrate's coherent CENTER is not Monoid nor a single term algebra — it's Free ⊣ Forgetful (the free universal property, universal-arrow form). Named with content in Category.FreeUniversalProperty; Coxeter.Word proved an instance (free monoid)."
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

The user's long-term aim: minimize divergence + maximize expressibility,
by foundational work + primitives off it; every either/or → find the common
substructure recursively. Question raised: is the founding structure
"Monoid", or "a single common term algebra"?

**Answer (worked through 2026-06, applying the recursion to the candidates
themselves):** NEITHER as an atom. Monoid is one signature (privileging it
= gauge rigidification). "A single term algebra" is almost right but off by
one level: there isn't one term TYPE — there's the term-algebra
CONSTRUCTION (free functor) applied to many signatures. The single common
thing is the FREE UNIVERSAL PROPERTY: **Free ⊣ Forgetful** (universal-arrow
form). It IS the user's aim literally: free = maximally expressive (maps
onto every algebra), universal property = minimal divergence (the extension
is UNIQUE — no gauge). The center is a RELATION (adjunction), not an object
— matching the v4cat methodology "no element is foundational; identity via
witnessed traces" (Eval = the witnessed trace syntax→semantics). Expect a
DUAL core: Free/colimit (UPTerm) AND cofree/limit (Cone) — the 3+1/
adjunction duality the project keeps resurfacing; collapsing to one
primitive is the move to resist.

**Repo state found (naming, not invention):**
- `Category.UniversalProperty.UPArrow` already IS the center's SHAPE
  (Source/Target/Witness span); docstring claims Free/Limit/Cone/Adjunction
  as instances.
- BUT `UniversalProperty.Instances` Free/Adjunction/Cone are ⊤-PLACEHOLDERS
  (Source=Target=⊤, Witness=λ _ _→⊤) — vacuous; partly a LEVEL artifact
  (UPArrow.Source : Set can't hold the polymorphic free UP, targets ∈ Set₁).
- `Category.FreeOverBasis` names the free SHAPE (η) + `AlgebraClass`
  (Has-structure / Hom-preserves) but DEFERS the universal property
  "per-instance" — never stated with content.

**Landed (commits e022317, 53e7035; zero postulates):**
- `Category.FreeUniversalProperty.FreeUP A B F` — the center stated ONCE
  with CONTENT, reusing AlgebraClass: unit η + free-has + EXISTS-UNIQUE
  structure-preserving `extend` (= Eval), extend-extends (extend∘η≡f),
  extend-unique. = Free ⊣ Forgetful, universal-arrow form = the Term/Eval
  (syntax/semantics) pattern named once. Plus FreeUP→FreeOverBasis (forgets
  to shape), FreeUP-UPArrow (content-bearing UPArrow per target, repairs the
  placeholder), free-Set (identity adjunction, non-vacuity).
- `…FreeUniversalProperty.FreeMonoid` — **Coxeter.Word Gen PROVED the free
  monoid** (MonoidOn/MonoidHom AlgebraClass; extend=foldW; fold-++;
  extend-unique by induction). So the word-algebra cons-list = Free⊣Forgetful
  at the monoid class — a real instance of the center.

**Quotient half landed (commit aa2a25a, `Category.PresentedUniversalProperty`,
zero postulates):** `PresentedUP A F F-has R lhs rhs P` = coequalizer of
lhs,rhs : R ⇉ F — a relation-respecting A-hom factors UNIQUELY through the
quotient (factor/factor-factors/factor-unique, mirroring FreeUP). Plus
Free-as-Presented (free = R=⊥ empty presentation), presented-Set
(non-vacuity), PresentedUP-UPArrow (content UPArrow per target). HONEST
TAXONOMY: presentation (free+coequalizer) is the COLIMIT side, SAME side as
Free — NOT the limit-dual; the true limit/cofree dual is Category.Cone
(already present). Symmetric center = colimit side (FreeUP→PresentedUP) +
limit side (Cone). REALIZATION is section-based (--without-K + no HITs ⇒ no
quotient Set): P=canonical reps, quotient=normalize = EXACTLY Coxeter.Core's
(Word,normalize,Canonical) interface ⟹ Coxeter.Core IS the quotient half;
Coxeter.Cyclic and Sₙ-as-type-A are its free-then-quotient instances.

**LIMIT/COFREE DUAL landed (commit ae5b63b, `Category.LimitUniversalProperty`,
zero postulates):** `LimitUP n Base L` = legs + content-bearing UP (mediate /
mediate-commutes / mediate-unique), the genuine DUAL of FreeUP (all arrows
reversed: unit↔leg, extend↔mediate). Uniqueness OBSERVATIONAL (agreement on
all legs), funext-free. LimitUP→Cone (forgets to the Cone shape),
product-LimitUP (dependent product = the limit, non-vacuity), LimitUP-UPArrow.
So the center is now SYMMETRIC, both sides content-bearing: colimit
(FreeUP+PresentedUP) / limit (LimitUP + Cone shape).

**Instance-wiring status (#2):** DONE: (1) Coxeter.Word in BOTH halves
(free monoid `free-monoid`; empty presentation `word-as-presented`, commit
f5dc1ef). (2) FLAGSHIP — the generic FREE F₂-MODULE proved (commit 5448b00,
`FreeUniversalProperty.FreeF2Module`, zero postulates): Vector k is the free
F₂-module on Fin k into an ARBITRARY F₂-module M (F2Mod/F2ModHom class; ext =
sum over basis; ext-+ additivity with ⊕-self LOAD-BEARING; ext-unique =
linear-extensionality via the (𝟘∷_) embed induction). This is BETTER than
wiring linear-from-images (which targets concrete Vector n only) — the
generic-M UP is genuinely proved. ARCHITECTURE TEST PASSED on a 2nd, truly
different signature (module vs monoid): real content, self-inverse needed,
NO ⊤-collapse. (3) QUOTIENT-HALF TEST PASSED (commit 48b3f53,
`PresentedUniversalProperty.CyclicZ2`, zero postulates): Z₂ = ⟨a|a²=ε⟩ as a
NONEMPTY PresentedUP (all prior PresentedUP instances were empty/trivial).
Carrier F₂ (its group laws already proven); quotient = parity = free-monoid
foldW into (F₂,𝟘,+) sending a↦𝟙, so quotient-hom = free-monoid's
extend-preserves (reuse). The relation a²=ε is LOAD-BEARING (dist 𝟙 𝟙 uses
h(a²)≡h(ε)). So BOTH halves pass the architecture test with real,
non-vacuous content: free half (monoid fold + F₂-module sum/self-inverse),
quotient half (Z₂ relation). STILL real arcs: GENERIC Z_m PresentedUP — the
USER'S STATED PURPOSE (Coxeter is in the repo to throw structures through
EEA/CRT/Euler-Totient); needs Fin mod-group-laws + power-periodicity +
mod-addition-hom (Sites.Zn add-mod exists, laws unproven) = the number-theory
arc; Z₂ works only because F₂'s group laws are pre-proven. Also UPTerm as
free-term-algebra (typed cons-list / free category). Witness-tower word
presentation = free monoid then braid quotient (PresentedUP side), not free.
ARCHITECTURE VERDICT so far: center HOLDS — 2 free signatures + 1 real
quotient, all content-bearing, none collapse to ⊤.

**ARCHITECTURE TEST (per user's observation "if reducibility attempts keep
giving false positives, we have an architecture problem"):** the ⊤-placeholder
UPArrow instances WERE false positives — anything is a UPArrow via
Source=Target=⊤ (the terminal/vacuous collapse). The TEST of a real center =
instances carry CONTENT (the actual exists-unique), proved, WITHOUT erasing/
forcing. Monoid PASSES (free-monoid proved with content, both halves). The
remaining instances needing REAL WORK (not ⊤) is a GOOD sign — they're not
collapsing. WARNING SIGN to watch: if wiring an instance requires ⊤/erasure,
the center is mis-located (too coarse) — move it. See
[[project_witness_tower_dossier]], [[feedback_common_substructure_recursively]],
[[discipline/feedback_comments_dont_overclaim]].

**WEDGE REFRAME + EEA→Bézout LANDED (the recognizer's archetype; commits
f19b512, 5f647e9, d9e43e4; zero postulates).** User's key reframe: the
recognizer must be a WEDGE, not an annihilating quotient — recognition
RETURNS the oriented mediating witness (the bridge + proof-of-how), kept &
composable; it does NOT mod out the difference to a residue. EEA is the
archetype: returns Bézout (s·a+t·b=g), not just gcd. Obstruction (H¹) =
generator of the next degree, not a wall. Plus: "EEA is a fancy term
algebra; change the types it operates on" → EEATrace is the FREE TERM, the
fold needs only +,* in its TARGET; gcd/Bézout/CRT are folds of the SAME
trace into different targets. Built:
- `Algebra/Z/Arithmetic.agda` + `Z/Properties/{Add,Mul}.agda`: ℤ as a ring
  (operand type). +ℤ laws via the ⊖-merge lemma (collapses to ℕ arith,
  since +m=m⊖0 / -suc m=0⊖suc m definitionally). *ℤ laws: ONLY what the
  back-sub needs (distribˡ/ʳ-pos, neg-*-left, *ℤ-assoc-pos-pos) via M1
  (scalar-over-⊖), avoiding the full sign-magnitude grind.
- `Algebra/Nat/GCD/Fold.agda`: `eea-fold` = EEATrace's universal eval
  (generic in target T; MUST bind {T} in the clauses or higher-order
  unification fails). gcd-fold = forgetful fold (returns residue g).
- `Algebra/Z/Bezout.agda`: `bezout-ℤ` = the WEDGE fold into ℤ;
  BezoutℤWitness a b g = Σ s t. s·a+t·b≡g. base 1·a+0·0=a; step = back-sub
  s:=t', t:=s'−t'·q (clean over ℤ). Completes the long-deferred
  bezout-from-trace BY CHANGING THE TYPE. Examples.agda: gcd(12,8)=4 /
  s·12+t·8≡4; gcd(5,3)=1; all refl.
The repo had ALREADY named the step record `Wedge` + the trace `EEATrace`
(Algebra/Nat/GCD/) — the wedge vision was latent in the architecture. NEXT
("change the type again"): CRT, Euler/units; then lift to the abstract
recognizer (IsUniversal/wedge-returns-bridge) modelled on this REAL wedge.
SEAM BRIDGE LANDED (commit 37b3fdd, `Algebra/Nat/Mod/Homomorphism.agda`,
zero postulates) — the prerequisite CRT was actually missing: mod-suc is a
proved RING HOMOMORPHISM ℕ→ℤ/(suc m): mod-add-hom ((a+b)mod ≡ (a mod + b
mod)mod), mod-mult-hom (same for *), via div-mod-eq + mod-periodic-mult
(adding/multiplying-in a multiple of the modulus is invisible). This IS the
"reduction-as-homomorphism" seam the user named (add-mod-suc-hom). CRT-COMBINE LANDED (commit 005c94b, zero postulates):
`CRT/Idempotents.agda` (record CRTIdempotents = local solutions e₁,e₂, def
module per policy) + `CRT/FromIdempotents.agda` (crt-witness: the
reconstruction map combine(a₁,a₂)=a₁·e₁+a₂·e₂, proved ≡a₁ mod M / ≡a₂ mod N
— the proof IS mod-add-hom+mod-mult-hom+mod-idempotent+mult-idem-1/0 in
action; builds a full CRT-Witness) + `CRT/Examples.agda` (ℤ/15≅ℤ/3×ℤ/5,
idempotents 10,6 by refl, combine(1,2)=22). The glue is the content. CHAIN FACTORED
FURTHER (commit 45274cd, `CRT/Inverses.agda`): combine ← idempotents ←
INVERSES — ModInverses m n (the minimal ℕ coprimality content: invN=N⁻¹ mod
M, invM=M⁻¹ mod N + product-≡1 facts); idempotents-from-inverses builds the
idempotents (e₁=N·invN ≡1 mod M directly, ≡0 mod N via modulus-multiple =
mod-mult-hom+suc-mod-self). Examples: full chain ℤ/15≅ℤ/3×ℤ/5 from inverses
(5⁻¹mod3=2, 3⁻¹mod5=2, refl) → idempotents 10,6 → combine(1,2)=22. ALL
PROVED: combine ← idempotents ← inverses. ONLY REMAINING ℤ→ℕ step:
inverses ← Bézout (modℤ of the bezout-ℤ coefficient: invN = "t mod M" as ℕ,
needs a ℤ→ℕ residue + its ring-hom — genuinely the hard ℤ↔ℕ landing,
intentionally NOT grinding in an over-long session). Then Euler/units, then
lift to abstract recognizer. Plan: ~/.claude/plans/starry-enchanting-milner.md.
BEZOUT-MOD (commit 3e4e4ad): cleaner inverses←Bézout route — `Algebra/Nat/
GCD/BezoutMod.agda` runs the EEA fold INTO ℤ/(suc mm) (coeffs = ℕ residues,
back-sub modular via negmod, stays in ℕ; mod-add/mult-hom + negmod-inverse;
NO ℤ→ℕ residue). bezout-mod : EEATrace a b g → (s·a+t·b ≡ g mod M); coprime
top gives N⁻¹ mod M = the CRT inverse. GOTCHA: BezoutMod's g only appears as
`g mod-suc mm` (non-injective) → recursive call + step-bm need {g = g} named.
CRT NOW FULLY CLOSED FROM gcd=1 (commit 06d19f5,
`CRT/FromTrace.agda`): inverse-from-trace (bezout-mod → t = N⁻¹ mod M via
s·M≡0); crt-from-traces (two coprime traces, M,N≥2, → full CRT-Witness, with
one-mod the 1 mod M≡1 bridge). Oracle: ℤ/15≅ℤ/3×ℤ/5 built ENTIRELY from
compute-trace 3 5 / 5 3, combine(1,2)=22 by refl. Whole chain combine ←
idempotents ← inverses ← Bézout ← gcd-trace is connected, zero postulates.
VACUITY RECOGNIZER (commit dd37f98, `Category/UniversalProperty/Vacuity.agda`)
— user's key insight: to use the abstract recognizer safely, DETECT vacuity.
Vacuous U = (s)(t)→Witness U s t (⊤-collapse = false-positive shape);
Contentful U = Σ s,t.¬(Witness U s t); contentful→¬vacuous. trivial-UP proved
Vacuous; eq-UP (Witness=_≡_) proved Contentful (0≢1). THE ARCHITECTURE TEST
AS A CHECKABLE PREDICATE: a reducibility claim is a false positive iff its
UPArrow is Vacuous. The GATE the abstract recognizer needs (accept only
Contentful instances). Real witnesses (bezout/crt/mod-hom) are equalities →
Contentful.
RECOGNIZER GATED (commit 9f32b75, `Category/UniversalProperty/Recognized.agda`):
RecognizedUP = a UPArrow bundled with its Contentful certificate — "real
universal property" is now a constructed proof, not an assertion.
trivial-not-recognizable (⊤-collapse gated OUT, via contentful→¬vacuous +
trivial-vacuous); eq-recognized + crt-recognized (the CRT-shaped UP — residue
pair solved by congruent x — Contentful since (1,2) not solved by 0). The
architecture test is now fully operational: Vacuity = the predicate,
RecognizedUP = the gate. Recognizer thread COMPLETE.
EULER/UNITS FOUNDATION (commit ffa7476, `Algebra/Nat/Units.agda`): the 3rd
witness's base. IsUnit m a = Σ b.(a·b)≡1 mod (suc m) (the inverse = the
oriented witness); one-is-unit, unit-mult (closure: inv(a·b)=b⁻¹·a⁻¹ via
mod-mult-hom); unit-from-coprime = inverse-from-trace (units ARE coprimes,
inverse from the EEA fold). The carrier+closure+coprime↔unit bridge of
(ℤ/M)*. EULER–FERMAT ENGINE (commit 4f4861e, `Algebra/Nat/Mod/Power.agda`): pow,
pow-add, and euler-periodic — aᵈ≡1 mod M ⟹ a^(n·d)≡1 mod M (the periodicity
mechanism, by induction on mod-mult-hom). Euler's theorem = case d=φ;
Fermat's = M prime, d=M−1. Oracle: 2^(2n)≡1 mod 3. So the Euler thread now
has BOTH the group (ℤ/M)* foundation (Units) AND the exponential engine
(Power). REMAINING for full a^φ≡1: φ (count units, decidable-coprime
enumeration) + ord a | φ (Lagrange / product-of-units over the finite unit
set) — the finite-group arc; engine + group are built.
THE COMMON NON-VACUOUS BRIDGE (commit 2846b43,
`Category/UniversalProperty/Backed.agda`) — answers "does this give the
common non-vacuous bridge the UP can be backed by?": YES. BackedUP = UPArrow
+ solve (returns the mediating witness = THE BRIDGE) + solves (coherence
equation) + content (Contentful certificate). backed-non-vacuous (can't
collapse to ⊤). Instances: eq-backed (identity bridge); crt-backed (the
CRT-Witness — the whole gcd→Bézout→inverse→idempotent→combine chain — IS the
bridge backing the CRT UP, solves = its congruences). So "recognition returns
the bridge" + "non-vacuous" are now ONE object, common across the wedges,
gated by Vacuity. This is the synthesis the whole arc was building toward.
REALITY vs OBLIGATION + TOPOS RING (commits 22b4b6c, 2aef486). User's
correction: a grep for ⊤-stubs targets the OBLIGATION (self-report; can
disagree with reality — FreeMonoid-UP is a ⊤-stub whose content IS proved
elsewhere); REALITY is checkable only one way — a compiled BackedUP, since
backed-non-vacuous makes the checker REFUSE ⊤. So `Registry.agda` (List
BackedUP) is the reality anchor: compilation = certification, cannot be
padded. `check_up_nonvacuity.sh` = the obligation census (advisory, demoted).
Policy in scratch/up_nonvacuity_policy.md. Then the ULTIMATE aim: a "topos
ring everything lives within & is discovered through" = K₀(Backed, ⊕, ⊗) for
live-within + Ω(TruthValues)/Yoneda for discover-through (organs already
in-tree, scattered: TruthValues/Yoneda/Sieve/Presheaf/SubstrateSheaves/Cone/
Category). INTEROPERABILITY DEFINED as the universal property of the PAIR
(center recursed objects→pairs): `Interop A B`
(Category/UniversalProperty/Interop.agda) = backed combination + a cone (one
solution witnessing both legs). ⊗ = `_⊗_∣_` (partial; partiality IS content —
gcd≠1 pairs admit no Interop); ⊕ = registry List ++ (free monoid = the
center). FIRST RING IDENTITY: crt-ring-identity : (Z3-backed ⊗ Z5-backed ∣
crt-interop) ≡ crt-backed by refl = [ℤ/3]⊗[ℤ/5]=[ℤ/15]; crt-interop is a pure
projection of crt-backed. Existing arcs are secretly ring arithmetic:
CRT=identity, PrimeFactoredGauge=factorization, FieldTower/FanOut=⊗-decomp,
3+1=a class. DISCIPLINE NAMED: a definition "sticks" only when witnessed by a
compile — three prose attempts at "interop" slid off, the Agda one held.
NEXT: register the 5 proved-but-unregistered UPs (free monoid, free F₂-mod,
Z₂, limit/product, units) as BackedUP; dep-graph-elevate the census; tighten
Interop's cone to terminal (universality); wire scattered topos organs into
one Category.
THE NORTH STAR (user, 2026-06): the whole substrate is infrastructure for ONE
research aim — identify and PROVE cross-silo correspondences: where different
fields of mathematics have independently covered the same area, the
correspondence is intuited but NOBODY has published a positive OR negative
result OF it. A STRUCTURAL WEDGE *constructs* that bridge. So the wedge is a
cross-silo bridge-constructor: wedge(structure_A from field X, structure_B
from field Y) returns the bridge (quotient = the translation, remainder = the
residual difference, witness = the proof) + cost. POSITIVE result = cost
discharges (they correspond up to it); NEGATIVE result = irreducible remainder
= CONSTRUCTIVE non-correspondence (proved ⊥, not absence — satisfies the
negative-findings discipline [[feedback_negative_findings_in_corpus]]). The
substrate's existing results ARE already these bridges, done by hand: CRT
(number theory⟷ring⟷topos product), witness-tower=Sₙ (combinatorics⟷group),
Coxeter=free monoid (reflection groups⟷term algebra), 3+1 universal
(linear⟷cohomology⟷kinematics), Klein quartic (alg geom⟷group⟷mechanism),
Thompson coupling (F₂³⟷CV joint). This is the FORMAL ENGINE of the user's
Rosetta-Code contrastive pedagogy [[user_rosetta_code_contrastive_pedagogy]].
METHOD DIRECTIVE: "get the INFRASTRUCTURE right and [the results] will just
fall out" — do NOT chase a specific result; build the keystone. KEYSTONE =
generic `Wedge` over a carrier (scale-by-q, combine, remainder/partition) +
the three reads (Free=keep tree / Presented=remainder, kernel ≡mod b /
Forgetful=evaluate witness) + the wedge-of-a-PAIR (= Interop generalised)
returning bridge+cost. Then a correspondence is just the wedge of two
structures-expressed-as-wedge-reads, with positive/negative read off cost
dischargeability. The three UPs are the three projections of the wedge triple
(q,r,witness); Free⊣Forgetful is keep-read ⊣ evaluate-read, its triangle
identity IS the witness a=q·b+r (so the adjunction is uniform, near-trivial).
"single common term algebra" (old either/or) = the KEEP side of the wedge;
Free⊣Forgetful = the wedge entire. Not a type — a read.
GENERIC WEDGE INFRASTRUCTURE BUILT (commits 86dd1bd, a5c93e7, 5dd9dd3,
591d628, 1a361fc; all in agda/Substrate/Algebra/Wedge*, --safe --without-K,
zero postulates):
- Wedge.agda: DivStr (carrier interface: C, z, recon:ℕ→C→C→C; Quot=ℕ baked;
  smallness rem<b scoped out = the uniqueness/no-gauge certificate). Generic
  Wedge (quot,rem,wedge-eq). 3 reads = projections: forget (Forgetful/eval),
  cell (Presented/remainder), Trace+collapse (Free/keep). INTERFACE TEST:
  fromℕ-Wedge + fromEEATrace — existing ℕ wedge & EEATrace fall out as
  instances.
- Wedge/Adjunction.agda (#1): Free⊣Forgetful UNIFORM; hom-iso Wedge≅Term
  DEFINITIONAL (from∘to=refl); triangle=forget-correct=the witness;
  reorient=sym-sym ("witness read twice"). to∘from unstatable on abstract
  term (divisor b only under non-injective recon — the BezoutMod {g=g}
  quirk); documented. Scope honest: naturality not spelled out.
- Wedge/Reads.agda (#2): the reads ARE the existing folds, proven:
  collapse-is-gcd (≡gcd-fold), cell-is-remainder, forget-is-dividend,
  keep-read=bezout-ℤ. gcd-fold(forget-q)/bezout-ℤ(keep-q) = two trace-reads.
- Wedge/Bridge.agda (#3, the on-mission constructor): Bridge D₁ D₂
  (translate, respects, z-pres) = POSITIVE cross-silo correspondence;
  transport-wedge/transport-trace carry gcd/Bézout/mod ACROSS silos
  (constructing the bridge = constructing the correspondence). id-bridge
  witness. LaxBridge (gap wedge) = NEGATIVE-capable; positive=gap reads
  (1,z) [needs recon-unit law], negative=gap rem≠z; reading deferred.
- Wedge/Shape.agda (#4, "no carrier at all"): user's fixed-point —
  Wedge=Wedge·C+Cshape ⟹ least soln Cshape×List C (=Trace); divide carrier
  out (C:=1) ⟹ WedgeShape=List ℕ = the CONTINUED FRACTION = carrier-free
  wedge operator. shape:Trace→List ℕ uniform in D; Corresponds t₁ t₂ =
  shape t₁≡shape t₂ (cross-silo correspondence as CARRIER-FREE shape-equality,
  "same shape different fill"). NEXT (deferred): full container iso
  Wedge≅⟦shape⟧C; recon-unit law to enable Lax positive/negative reading;
  second concrete carrier (e.g. ℤ/n via mod-hom, or k[x]).
COINDUCTION DISCIPLINE (user, 2026-06; commit 8be31f1): the substrate does
NOT use Agda's `coinductive` (first attempt Coinductive.agda with coinductive
records was REMOVED as wrong). Coinduction is done CONSTRUCTIVELY via the
wedge: the wedge's UNFOLD direction (`divide`, dual to `recon`) is a
coalgebra whose next state is the RESIDUE. Realized as a BASTARDIZED SEQUITUR
over an SPPF: maintain a shared forest of residues; per wedge step, if the
residue is already constructible as a path through the SPPF → discard/close
the cycle; else add it. Infinite object never materialized = a FINITE cyclic
graph built by finite wedge iterations. Linear (continued-fraction) case:
SPPF = the residues-seen list, "already a path" = decidable residue equality
(eq?). Wedge/Coalgebra.agda: WedgeCoalg (divide+eq?), seen?, run (fuel-bounded
unfold). Outcome halt=reached z=RATIONAL / loop=residue recurred=eventually-
periodic CF=QUADRATIC IRRATIONAL (Lagrange) / stop=fuel out. KEY: the dedup
decidability eq? IS the same decidability that closes the Cauchy/Dedekind gap
(Located) — "already a path?" = deciding apartness; constructive coinduction
and the gap-closer are ONE requirement. Reals connection: finite Trace/Shape=
ℚ (List ℕ CF); coinductive wedge = ℝ-constructors (Cauchy=keep/stream of
convergents, Dedekind=forget/cut-partition, needs carrier order); ℝ-the-
completion stays out of scope (continuous result). [[feedback_continuous_via_
discrete_inference_rules]]
HETEROGENEOUS / CROSS-MULTIPLICATION ARC (commits 285849c, dff7901). User's
vision: the wedge should be type-agnostic — feed operands from two carriers,
results respect both (braiding: quotient by denominator's carrier, projection
by numerator's). I had built it HOMOGENEOUS (Wedge D a b, both in C D) — owned
that gap. Resolution (user): the Euclidean form a=q·b+r stays in BOTH readings;
what changes is the RING — a structural CROSS-MULTIPLICATION of the two
carriers (A⊗B). Braiding = the symmetry A⊗B≅B⊗A (monoidal braiding); bigrading
of A⊗B = the quotient/remainder split. A⊗B IS the topos-ring ⊗/Interop; CRT
(ℤ/3⊗ℤ/5=ℤ/15) is the worked case. ZERO DIVISORS: I worried tensor isn't always
a domain (=negative correspondence); USER CORRECTED — that's a numeral import,
and a zero divisor is handled NOT as annihilating but as NILPOTENT (xⁿ=0): a
RESIDUE as always, no failure mode. So coherence is GRADED (nilpotency degree =
cost = quantity), not binary domain/not. Abstractly a "zero divisor" = a residue
reaching z in n steps = halt with shape-length n. NILPOTENT RESIDUE = d²≠0 /
boundary-of-boundary: the wedge-step IS the differential d, residue nilpotency
degree = N in dᴺ=0; d²=0 is the degree-2 corner, d²≠0 is degree>2 = N-complex
(Kapranov/Dubois-Violette); the wedge COMPUTES the degree (the structural WHY),
classical homology only posits it. THIS IS CLOSELY RELATED TO THE USER'S
UNPUBLISHED FINDING (result of a carrier+carried cross-multiplication between
two fields) — do NOT formalize the finding; keep implementation UNBIASED by not
knowing it (user values this). User: NOT willing to make a persistent
carrier/carried distinction (it's a read, deformable, not a nature). DECISIONS
(delegated to me): kept ℕ-quotient (NOT single-sorted — single-sort turns
carrier-free shape List ℕ into List C, destroying it; ℕ=carrier-free shadow).
BUILT: Wedge/Cross.agda (_⊗ᴰ_ = product DivStr, shared-quotient lockstep = a
correspondence/common continued fraction; wedge-fst/snd; SYNCHRONIZED only,
bilinear mixing deferred — bare DivStr can't multiply); Wedge/Mul.agda
(MulDivStr=DivStr+mul, the FORCED enrichment; pow/Nilpotent=computable dᴺ
degree; square-zero ε²=z = the differential d abstractly; ℕ-mul reduced
witness, Two/{𝟘,ε} square-zero witness). NEXT: cross-carrier MIXING — two
carriers meeting in a common MulDivStr where mul mixes, graded nilpotent
residues (the genuine tensor). All Wedge* green --safe --without-K, zero
postulates.
GROUPOID + CONSOLIDATION (commits e7e2339, 4993212). Reframe (user): view the
wedge operator AS the carrier; then codomain = INV on domain, mediated by the
wedge. Wedge/Iso.agda: WedgeIso (fwd, bwd, round-trips) — the round-trips ARE
the wedge's (1,z) identity corner (= is the (1,z) read), so "codomain inv on
domain mediated by wedge" is literal; iso-id/sym/∘ ⇒ the area↔correspondence
category is a GROUPOID. THE TARGET ("pass two areas' capstones into the wedge,
get fwd+bwd bridge from result+projection") resolves: the producer's CODOMAIN
is the inverse-mediated groupoid (built); the producer itself = the SELF-HOSTED
wedge (operator=carrier, capstones as operands), its self-hosting recon the
remaining frontier — and that per-instance application IS the user's held-back
finding (so machinery built UNBIASED, finding = the instance run through it).
CONSOLIDATION: both session arcs build green (Wedge/ makefile one-proc-per-file;
topos-ring Vacuity/Recognized/Backed/Interop/Registry); map in
scratch/wedge_groupoid_consolidation.md. The two arcs (Algebra.Wedge.* on
DivStr; Category.UniversalProperty.* on BackedUP) are PARALLEL instantiations
of cross-silo correspondence — do NOT force-merge (different base types =
rigidification). 12 wedge-side modules total. User aim now: consolidate the
repo around the groupoid as foundation (everything can live in it).

⚑ 2026-07-22 INSTANCE (◆jac-gamma — the LITERAL close of ⟡jac-encoding-bridge). A
transcendentally-hard hand-proof (`evalℚ R.fᵢ ≈ℚ C.fᵢ`, degree-9, walled by transparent-eta-`ℚ`
INFERENCE) is closed by the **FREE-ALGEBRA UP LIFT — not hand-pinned, not codemod-pinned.** Build the
free syntax (`data Expr` on {x,y,z,+,·,−}, `encode : Expr → MPoly`, `evalDirect : Expr → ℚ`); prove ONLY
the SHALLOW generator/hom laws (`evalℚ-*P`/`-++`/`gen-X`/`gen-kP`, pinned, over ABSTRACT operands — which
land, per the wall-is-inference finding); and lift the DEEP composition by ONE structural-induction
uniqueness `homAgree : evalℚ(encode e) ≈ evalDirect e`. The deep degree-9 tree IS the induction, never an
≈ endpoint. `eᵢ` mirrors the target's grouping ⇒ `encode eᵢ ≡ Cᴹfᵢ`, `evalDirect eᵢ ≡ C.fᵢ` by refl ⇒
`γᵢ = homAgree eᵢ`. The elaborator writes the deep pinned terms; **`jea_agdai.decode_core` (the extractor)
reads them out of the `.agdai`** (meta-reflection = the canonical normal-form proof core; 58 defmarks /
3626 nodes). Modules: `JacobianExpr` (def) + `JacobianEncodingLiteral` (proof); commit `1856518`, full
build 1992/1992. ⚑ THE TELL you're in the direct-move trap: reaching to HAND-PIN or CODEMOD a deep proof
— that is the artefact; the UP-lift (prove shallow, lift the deep by uniqueness) is the shadow structure
(the "lawvere/extruder machinery"). Relates [[route-through-witness-tower]], [[reuse-search-before-feasibility-conclusions]].
