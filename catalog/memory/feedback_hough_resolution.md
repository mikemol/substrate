---
name: feedback-hough-resolution
description: "When Hough/voting analysis on a graph looks like noise, the resolution is too coarse — the \"noise\" is structural signal at a finer grain you haven't resolved yet."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

When applying Hough-style voting to a codebase dependency graph (count of (A→B, A→C, B→D) triples with C→D missing), high-vote "missing edges" between apparently-unrelated primitives are NOT noise. They are categorical morphisms (functors, natural transformations, actions) that EXIST in the codebase but are routed through intermediate modules. The vote count measures how heavily that morphism is assumed.

**Why:** when I called the module-level Hough output "mostly noise" because votes like "S4 → V4 (45 votes)" connect ostensibly-independent primitives, the user replied: "you're not reading enough into it. If it appears mostly noise, that's because you don't have a high enough resolution." Concretely:
- S4 → V4 = the V₄-subgroup-of-S₄ embedding, formalised in `V4-Embedding.embed`. 45 votes = 45 different module-pairs that assume this embedding.
- V4 → Axes = the V₄-acts-on-Axes morphism, formalised in `act-axis`. 43 votes = 43 places assuming the action.
- Axes → S4 = the axis-induced permutations, via `v-of-axis` in `SemidirectProduct`.

Each "missing edge" is the SHADOW of a natural transformation living elsewhere. Module-level analysis FLATTENS these into apparent gaps; definition-level analysis RESOLVES them into the actual morphisms.

**How to apply:**
- When voting/Hough output looks like noise but the user pushes back, the answer is finer resolution, not "ignore it".
- Module-level dependency graphs project natural transformations onto module-pair gaps. Definition-level resolves them.
- Each high-vote missing edge at module level = "find the function/morphism that mediates this; it lives in some intermediate module".
- Sister to [[feedback-two-path-commutativity]]: that rule names the 2D structure; this names the resolution problem when analysing it.
- Sister to [[feedback-negative-findings-in-corpus]]: "looks like noise" is a negative finding; distrust it the same way you distrust "X fails" verdicts. The negation form often hides structural signal.
