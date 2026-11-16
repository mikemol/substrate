---
name: feedback_categorical_superlative_needs_universal_property
description: "Categorical superlatives (free / complete / initial / terminal / universal / THE) claim a UNIVERSAL PROPERTY — state them only when that property is FORMALIZED. Structure + laws + coherence proven ≠ free/complete. Describe exactly what's proven."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When describing what an Agda development proves, I over-reach into categorical SUPERLATIVES —
"the FREE symmetric rig on one generator," "a COMPLETE rig category," "THE terminal coalgebra,"
"the INITIAL algebra" — when what's actually formalized is the STRUCTURE + LAWS (+ COHERENCE). A
superlative names a UNIVERSAL PROPERTY (an initial/terminal/free object is defined by a unique
mapping property), and that property is a SEPARATE theorem, usually NOT what the structure-proof
establishes.

**Caught 2× in one arc (2026-07-10, the graded-Lehmer-rig arc):**
- "COMPLETE symmetric rig category" — corrected: I'd proven the operations + laws (assoc/unit/comm/
  distrib as isos + naturalities), i.e. the rig STRUCTURE; the coherence DIAGRAMS (pentagon/hexagon/
  Laplaza) were unproven at that point. "Complete" needs the coherence.
- "the FREE symmetric rig on one generator" — even after all coherence was formalized (a coherent
  symmetric rig category, verified), FREENESS is the universal property (initial among symmetric rig
  categories equipped with a chosen object) — NOT formalized. Mathematically true (finite types ARE
  the free symmetric rig), but not an Agda theorem here.

**Why:** the superlative is the satisfying headline, and the structure-proof FEELS like it earns it.
It doesn't — free/complete/initial/terminal/universal are all "there EXISTS a unique …" claims whose
proof is a distinct construction (the universal map + its uniqueness). Claiming the superlative
imports an unproven theorem into the summary, exactly the anti-overclaim failure the retrospective
ritual (G8) exists to catch — the categorical-status flavour of it.

**How to apply:** describe EXACTLY what's formalized. "A symmetric rig category" (structure + laws
+ coherence, proven) is honest; "THE FREE symmetric rig on a generator" adds an unproven universal
property. If you want the superlative, either (a) formalize the universal property (the free/initial
mapping property + uniqueness) and THEN say it, or (b) hedge explicitly: "a coherent symmetric rig
category — which is, mathematically, the free one on a generator, though that universal property is
not formalized here." Sibling of the general anti-overclaim discipline and
[[feedback_reuse_search_before_feasibility_conclusions]] (there: don't assert absence without search;
here: don't assert a universal property without its proof). The tell: any of {free, complete, initial,
terminal, universal, canonical, THE (definite article for an up-to-iso object)} in a summary of what
Agda proved.
