---
name: ""
metadata: 
  node_type: memory
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Two exercises (read-only) per user "fan-in-is-Impact + find where fan-in
COULD be had but isn't yet" (the cong-trans-before-it-was-named pattern;
"willing to cross boundaries currently presumed off-limits").

**EXERCISE 1 (refresh — current fan-in × improvement signal, post-seals):**
The dense-transparent hits (Permutation.* cluster, HodgeStar, Fano, etc.)
are now mostly FALSE POSITIVES — they consume the sealed linear-from-images
/ cyclic-Linear, the heuristic just sees the name. Genuine signals left:
- Algebra.F2 (fan-in 322) — refl-heavy. The F₂ base; needs an AUDIT
  (user expects real fixes here).
- Groups.V4.Axioms (fan-in 131) — 103 refls, but these are the
  v4×v4×v4-cover tuples (already minimal per generators-catalog); likely
  fine, confirm don't assume.

**EXERCISE 2 (LATENT fan-in — idioms not yet extracted), via the repo's
own scripts/agda_similarity.py --cluster (the right tool; skeleton mode
for the shape):**

Cluster 1, size 20, mean 0.57 — the AsFunctor / AsNaturalTransformation /
AsCartanType / AsRootSystem family. **INITIAL READ WAS A FALSE POSITIVE,
CORRECTED ON INSPECTION:** these are NOT unextracted clones. 12 of 17
checked ALREADY project from the existing `Category.Functor.AsNamed`
(open + rename — the cone is built and adopted; its header lists these as
its legs, per [[project_named_categorical_structure_skeletons]]). The
0.57 score meant "correctly share a base skeleton," NOT "duplicate" — true
unextracted clones score ~0.95. LESSON: a MODERATE cluster score (~0.5–0.6)
signals shared-base-done-right; do not read it as duplication. Verify with
`grep AsNamed` before proposing extraction.

The 5 non-projecting members are mostly genuinely distinct:
RootSystem.AsCartanType / CartanType.AsRootSystem name Root→Cartan /
Cartan→Root inline (could project, but 2 files); YonedaEmbedding,
GrothendieckOfAut are their own constructions.

REAL (small) residue: there is NO `NaturalTransformation.AsNamed` sibling,
while Functor/Dagger/SymmetricMonoidal .AsNamed all exist. 2 files
(*.AsNaturalTransformation, incl HodgeStar) re-spell NT-naming inline. A
genuine "fan-in could be had" but only ~2 legs — a completeness-of-the-
AsNamed-family gap (chirality-pair-completeness discipline), not a headline.

Other clusters (lower priority, mostly known):
- Cluster 2 (18): Raven Poem StanzaI..XVIII — pure data instances, a
  StanzaTemplate would collapse them (cosmetic, low fan-in value).
- Cluster 3 (10): Coxeter.Core.HigherArity Quad/Quint/Sext/Sept — the
  n-ary associativity ladder; candidate for one parametric arity lemma.

**Method note:** the home-grown skeleton/grep idiom miner (/tmp/idioms.py)
was too coarse (collapsing args destroys the signal). USE
scripts/agda_similarity.py --cluster then --skeleton --typed-holes — it is
the substrate's purpose-built instrument ([[discipline/feedback_similarity_not_grep]]).

**Status:** ANALYSIS ONLY, nothing changed. Ranked latent-fan-in targets:
(1) AsFunctor family → instantiate Functor.AsNamed (20 files, cross-
boundary, highest latent fan-in); (2) refl-heavy F₂ audit; (3) HigherArity
arity-ladder; (4) Raven StanzaTemplate (cosmetic). Each its own arc.
