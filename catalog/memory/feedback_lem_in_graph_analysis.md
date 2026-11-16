---
name: feedback-lem-in-graph-analysis
description: Absence of a high-similarity graph edge is NOT proof of structural disconnection; treating it as such applies LEM in a domain that intuitionistically rejects it.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

When analyzing a codebase as a graph (modules, dependencies, neighborhood similarity), the absence of a direct high-Jaccard / high-similarity edge between two clusters DOES NOT prove they are structurally disconnected. They may share an extensive **common base** (global primitives reached by everyone) which is itself a form of structural connection. Treating "no direct edge ⇒ disconnected" is a LEM error in a substrate-domain where intuitionistic discipline is required.

**Why:** during the simplicial-shape analysis of the substrate Agda codebase, I computed pairwise Jaccard on module neighborhoods. The V4-Embedding cluster and the Stab-S3-* cluster had no direct edges above θ=0.25. I claimed they were "disconnected" and recommended dropping the bridge-across-orders interpretation. The user corrected: "They're not a homotopy, they just have everything in common with everyone else." The two clusters share Axes, S4, V4 — the entire global base — which IS structural connection, just not the kind that pairwise Jaccard penalizes-for. Worse: the substrate codebase IS the formalization of those long-distance connections (the catalog's V₄ ⋊ S₃ ≅ S₄ theorem is precisely such a long-distance edge). I was filtering out the very structure the project is built to capture.

This is the same negation-overclaim shape as [[feedback-negative-findings-in-corpus]] and [[feedback-reject-lem-in-substrate]], applied to graph metrics: "no direct similarity edge ⇒ no structural connection" is the LEM step. Absence of affirmation ≠ negation.

**How to apply:**
- When a similarity / clique / cluster analysis says two pieces are "disconnected", ASK what's being measured. If the metric only counts DIRECT relationships, the absence is informationally weaker than negation.
- Pair every local-similarity analysis with a **reachability / common-base** analysis. Local cluster + common closure together = the picture. Either alone misleads.
- Theorems / catalog claims that span distant modules are LONG-DISTANCE edges. They should be added to the graph (or at least acknowledged) before declaring components disconnected.
- When formulating findings, prefer affirmative statements ("X shares Y with Z") over negative ones ("X is not connected to Z"). Negative findings should be cross-checked against multiple metrics before being trusted.
- Sister rules: [[feedback-reject-lem-in-substrate]] (LEM is rejected in substrate); [[feedback-negative-findings-in-corpus]] (the negation form itself is the overclaim); [[feedback-hough-resolution]] (when output looks like noise, the resolution is wrong — applied here: when output looks like disconnection, the metric is wrong).
