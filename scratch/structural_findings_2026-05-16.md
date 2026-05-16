# Structural findings — substrate Agda codebase

**Date:** 2026-05-16
**Method:** Cuthill-McKee reordering + Hough-style voting + path-2 mediator-overlap (Jaccard) + Weisfeiler-Lehman color refinement on the module dependency graph.
**Scripts:** `naturality_squares.py`, `path2_analysis.py`, `def_level_squares.py`.

## Methodology

The analysis treats `agda/Substrate/**/*.agda` as a directed graph (modules = nodes, `open import` / `import` statements = edges). Three layers of analysis:

1. **Module-level edge analysis (CM + Hough voting):** First-pass detector. Surfaces dependency clusters and high-vote "missing edges" — but these are categorical morphisms living in intermediate modules (per `[[feedback-hough-resolution]]`), not structural gaps.

2. **Path-2 mediator-overlap analysis:** For each cell `A²[X,Y] ≥ 2`, compute the pairwise Jaccard similarity of mediators' out-neighborhoods. High Jaccard = mediators are doing the same role; the codebase is expressing one structural fact through two paths.

3. **WL color refinement:** Each node colored by its in/out-neighborhood signature. Refined iteratively. Stable equivalence classes = role-isomorphic modules.

## Key findings

### 1. Identical-mediator pairs (Jaccard = 1.00)

| Cell | Mediator pair | Reading |
|---|---|---|
| `Subgroup ⟶ {V4-Embedding, S4, V4, Axes}` | `SemidirectProduct ⇄ V4-Normality` | **Rigidification candidate.** Two modules with identical out-neighborhoods, jointly expressing "V₄ ⊳ S₄ + V₄ ⋊ Stab(D)". |
| `Stab-S3-Iso ⟶ {Stab-S3, SFin, S4, Axes}` | `Stab-S3-Extend ⇄ Stab-S3-Restrict` | **Duality — but parameterization candidate.** Both instances of `transport-perm : (A ↔ B) → Permutation A → Permutation B` with bijection going opposite directions. One parametric definition could replace both. |
| `LiveS4Bijection ⟶ Axes` | `Codeword ⇄ S4` | Suspicious. Semantically very different modules but identical dep network. Further investigation needed. |

### 2. WL singleton high-Jaccard pairs (broken parallels)

| Jaccard | Pair | Reading |
|---|---|---|
| 0.92 | `Stab-S3-Iso ⇄ Stab-S3-Hom` | Set iso (slice 14d) + group hom (14e) at two levels of the same structure |
| 0.81 | `V4-Cosets ⇄ S4GroupIso` | Both lift bijections to group structures (different scales) |
| **0.76** | **`V4-Embedding ⇄ SemidirectProduct`** | **The anchor-asymmetry lives here.** D-pinned `embed` + D-pinned `Stab-D` are mutually-defined. |
| 0.75 | `KRule, F2CubedPuncturing ⇄ Substrate` | Parallel cocycle instances (correct) |

### 3. The naturality square trying to manifest

The analysis localizes the parametric/D-anchor asymmetry to three modules:

```
                D-anchored bottom triangle               Parametric Stab cluster
                (Jaccard 0.76–1.00 inside)               (Jaccard 1.00 for E⇄R)
                                                                
                  V4-Embedding                          Stab-S3
                  (D-pinned act-axis, embed)            (parametric)
                       │                                    │
                       │                                    │
                  SemidirectProduct                     Stab-S3-Extend
                  (Stab-D)        ⇄=⇄                       ⇄=⇄
                       │       (Jaccard 1.00)            Stab-S3-Restrict
                       │                                    │
                  V4-Normality                          Stab-S3-Iso
                                                            │
                                                        Stab-S3-Hom

      ◇──────────── bottom row missing ────────────────────◇
                         (anchor-parametric V4 ⋊ Stab(anchor)
                          cocycle structure)
```

The parametric Stab cluster (slice 14) was completed but the bottom row of the naturality square — a parametric V4-Embedding / SemidirectProduct — does not exist. The cocycle's D-pinning is what prevents closure.

### 4. Hough vote at module-level (mediated morphisms)

The high-vote "missing edges" at module level are NOT gaps; they're heavily-used categorical morphisms mediated through translation layers:

| Votes | Missing edge | Translation layer |
|---|---|---|
| 45 | S4 → V4 | V4-Embedding.embed |
| 43 | V4 → Axes | V4-Embedding.act-axis |
| 35 | Axes → S4 | SemidirectProduct.v-of-axis |
| 26 | V4 → S4 | V4-Embedding.embed (composition route) |
| 12 | SFin → Axes | Stab-S3.fin3-to-non-anchor (parametric — correct!) |

The SFin→Axes case is the **correct** translation-layer pattern: parametric in anchor. The V4-Embedding bundle is the rigidification: 88+ vote-weighted dependents all going through D-pinned constructions.

## Proposed next slice

**Anchor-parametrize V4-Embedding + SemidirectProduct** (~3 modules touched, mediator-overlap analysis suggests the cascade is bounded by identical neighborhoods). Result: the bottom row of the naturality square exists; the parametric Stab cluster connects back to a parametric cocycle structure; slice 4's case lemmas become instances of a parametric form rather than D-special-cased work.

Specifics:
- `V4-Embedding`: introduce `embed-by : (anchor : Axis) → V₄ → Permutation` where V₄ elements parametrically swap (anchor, non-anchor-i) pairs.
- `SemidirectProduct`: replace `Stab-D` with `Stab anchor` (= slice 14's parametric form), generalize `v-of-axis`, `v-for`, `s-for`, factorization.
- `V4-Normality`: anchor-parametric normality proof.
- Downstream: `S4Iso`, `S4GroupIso`, `LiveS4*` instantiate at anchor=D.

## Higher-order findings (deferred)

- **Extend/Restrict parameterization:** both are instances of `transport-perm : (A ↔ B) → Permutation A → Permutation B`. One parametric definition; instantiate twice with bijection going opposite directions.
- **Recursive analysis:** apply the same path-2 + Jaccard analysis to the DEFINITION-level graph for the hot modules. Higher resolution may reveal further unification candidates inside V4-Embedding / SemidirectProduct.
- **Triangle compression:** the (V4-Embedding, SemidirectProduct, V4-Normality) triangle is mutually-defined; def-level analysis may reveal redundant definitions across them.

## Cross-references

- `[[feedback-hough-resolution]]` — module-level "noise" is morphisms at finer resolution.
- `[[feedback-two-path-commutativity]]` — the 2-path structure being detected here.
- `[[feedback-choice-rigidification-in-substrate]]` — translation layers are rigidification residue.
- `[[feedback-expose-generator-not-orbit]]` — anchor-parametric Stab in slice 14 was the 1D form; this is the 2D refinement.
