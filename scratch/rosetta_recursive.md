# Ⓒ.rosetta-recursive — `f090_2_rosetta` IS `jea_oneforest`, one level up

The cotype's `f090_2_rosetta` and the substrate's `jea/jea_oneforest.py` (the Ⓡ arc) are the SAME
correspondence machine at two levels. This note makes the recursion explicit + names the
fixed-point. Grounded in the live corpus (`scratch/cotype-ebnf-strictness/.../warrants.bib`) and the
oneforest commits (`correspondence()`, the quotient LADDER, `profile S(g)`, `quotient_to_shape`).

## The two objects

**`f090_2_rosetta`** (a `claim:` formality, §litsearch): mult(p,c) has FOUR renderings, "each a
language that makes one structure manifest and hides others":
- **M1** L-function — analytic factorization; sees the trivial character (`+1`) + conjugate L-pairs
  (`/2`); HIDES the simplex.
- **M2** equitable blocks — linear-algebraic kernels; sees the (p−1) sectors are EQUAL (a checkable
  matrix fact); HIDES the C(c,2) shape.
- **WitnessTower base/fiber** — simplicial skeleton; sees the f-vector geometry + the
  machine-checked-base / p-weighted-fiber split; HIDES the spectral content.
- **M3** orbit redundancy — orbit counting; sees the ambient space + explicit complement; HIDES the
  Φ_p isolation.
- **THE TRANSLATION-INVARIANT**: the `φ(p)/2` reality pairing appears in EVERY rendering. "The
  cross-language comparison IS the content, not re-narration to discount."

**`jea_oneforest`** (the Ⓡ verification gate): intern multiple arms (source/core/kernel) into ONE
forest; `correspondence()` = the SYMMETRIC mutual-best matching (a↔b iff each is the other's
most-shared partner) under the gauge the interner already quotients by; DISCOVERED, never declared.
`EXACT = cross-term degree 0` (orthogonal = same canonical node = realizes); ORPHANS = units the
symmetry leaves unpaired; the graded obstruction/residue says by how much and where. The recent
ladder: `quotient_to_shape` (CrossMul again at the shape rung), the quotient LADDER ("the generic
pair corresponds **across the vocabulary gap**"), `profile S(g)` (the correspondence is a TRUNCATABLE
GRADED CURVE, not a scalar).

## The structural isomorphism (theorem-renderings ARE oneforest arms)

| `f090_2_rosetta` (theorem level) | `jea_oneforest` (artifact level) |
|---|---|
| the four renderings M1/M2/WT/M3 | the arms (source/core/kernel/Agda-core) |
| "each language makes one structure manifest, hides others" | each arm's units; what one arm lacks = the others' ORPHANS |
| the translation-invariant `φ(p)/2` in EVERY rendering | the EXACT correspondence core (cross-term **degree 0** = shared canonical node) |
| what each rendering HIDES (M1 hides the simplex, …) | the graded OBSTRUCTION/RESIDUE + the orphans |
| "cross-language comparison IS the content" | "the correspondence is DISCOVERED, not declared" |
| four renderings as a comparison set | `profile S(g)` — the truncatable graded curve over the renderings |
| the renderings speak different mathematical LANGUAGES | the quotient LADDER "corresponds across the **vocabulary gap**" |

So `f090_2_rosetta` is not *like* oneforest — it is oneforest's exact output type (an exact shared
core + per-arm residue, discovered under a gauge), evaluated **one level up**: oneforest corresponds
CODE UNITS; the Rosetta corresponds whole THEOREM-RENDERING LANGUAGES. The "+1 level" is units →
languages; the machine is identical.

## The fixed-point (why it's RECURSIVE, not merely analogous)

`f090_2_rosetta` lists **"WitnessTower base/fiber"** as one of its four renderings. `jea_oneforest`'s
**Agda-core arm** (`jea_agdai.core_intern_agdai`) interns exactly that WitnessTower
(`WitnessTower.PhiMultiplicity`, the Ⓕ.spectral arc — the `f090_2_xref` Agda fill from Ⓒ.bibwiden).
So the WitnessTower is simultaneously:
- an **arm** of the artifact-level oneforest correspondence, AND
- a **rendering** in the theorem-level Rosetta.

The machinery that COMPUTES the correspondence (oneforest, via its Agda-core arm) is itself ONE OF
THE THINGS BEING CORRESPONDED (a Rosetta rendering). That self-reference is the recursion: the
prose↔probe↔proof Rosetta applies to itself, with the Agda WitnessTower as the shared node at both
levels. This is the same "intern is the fold, projection the unfold; the recursive law dissolves the
either/or" the cotype states at f029_5 — here the law dissolves the level distinction.

## The runnable follow-on (promote prose → oneforest readout)

`f090_2_rosetta` is currently a `claim:` (prose↔probe). To make it a oneforest READOUT: intern the
four renderings as arms (each rendering's defining formula/structure as a unit-set), run
`correspondence()`, and CHECK that the `φ(p)/2` reality-pairing is the EXACT (degree-0) shared core
across all four, with each rendering's "hidden structure" surfacing as its orphan/graded residue.
That converts "the translation-invariant appears in every rendering" from an asserted claim into a
discovered cross-term — the theorem-level Rosetta verified by the same gate that verifies the
artifact-level one. Scoped as a real build (needs a front-end interning the renderings); flagged, not
done here.

## Net

The Ⓒ arc closes on a self-similar center: Ⓒ.absent-sphere (Agda→cotype, hand-fed), Ⓒ.bibwiden (the
cotype's DAG centers on f090_2 + records the Agda fill), and Ⓒ.rosetta-recursive (f090_2_rosetta =
oneforest one level up, with WitnessTower the shared node) are three readings of ONE object — the
Φ_p-multiplicity correspondence — at three levels (campaign, DAG, theorem-rendering). The Rosetta is
recursive because its computing-machine is one of its renderings.
