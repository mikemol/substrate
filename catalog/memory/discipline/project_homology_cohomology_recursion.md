---
name: project-homology-cohomology-recursion
description: "The substrate project's deepest structure — observed = homology, cataloged = cohomology, recursive at every level. Local clusters share base; bridge modules materialize cocycles."
metadata: 
  node_type: memory
  type: project
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---
<!-- POLICY: load-bearing discipline; cited heavily across the substrate -->
The substrate project's deepest structural principle (articulated by user 2026-05-16): **everything we observe is homology, and we're attempting to catalog the cohomology. This notion applies recursively.**

**What this means concretely:**
- **Homology** = what's directly observable in the graph/code/structure. Local cycles, local clusters, neighborhood overlaps, what-imports-what.
- **Cohomology** = catalog claims, theorems, gauge-invariant functions on cycles. The cocycle abstractions in `Substrate.Cocycle.agda` (CY-2, CY-4, CY-5).
- **Recursion** = each level's catalog (cohomology) becomes the next level's observed (homology). The patterns ACROSS catalog claims are themselves cocycles at a higher level.

**Why:** during graph analysis, two complementary passes revealed: (a) the V4-Embedding cluster and the Stab-S3-* cluster have NO direct above-base module connecting them; (b) but they share an extensive common base (V4, Axes, S4). The substrate codebase's job is to **materialize the catalog's cocycle claims as actual bridge modules** that explicitly connect above-base. Each catalog claim (e.g., V₄ ⋊ S₃ ≅ S₄) is a cocycle; each substantial slice that proves part of it is a homology-level materialization of that cocycle. Slice 18 (S4Iso-Bridges) was the first such above-base bridge for the V₄/S₃ claim.

**How to apply:**
- When analyzing the codebase, distinguish HOMOLOGY observations (what's directly visible) from COHOMOLOGY catalog claims (what the codebase is PROVING).
- Disconnected local clusters that share a base are NOT structurally disconnected — they're connected through the catalog's cocycle that hasn't been materialized as a bridge module yet. The work is to BUILD those bridges, slice by slice.
- The cocycle abstractions in `Cocycle.agda` are level-1 structures. Disciplines in `Discipline.agda` are level-2 (cohomology of the catalog). Slice planning should track which level a refactor lives at.
- When a graph metric says "disconnected", ask: are they disconnected at this level, or merely awaiting cohomology-materialization at this level?
- Recursive application: the cocycle abstractions in CY-2/4/5 share structure (Invariant, Fiber, Gauge, TotalSpace = Σ Invariant Fiber). Patterns ACROSS those instances are level-2 cocycles. Find them.
- This rule sister-pairs with [[feedback-lem-in-graph-analysis]] (the LEM error of mistaking metric-absence for structural-disconnection) and [[feedback-two-path-commutativity]] (parameterizing one axis vs both — closely related to materializing cocycles vs just observing them).
