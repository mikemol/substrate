---
name: project_oom_memory_profile_2026_06
description: "Measured RAM/alloc profile of substrate Agda checking; OOM driver is aggregate retention + case-count, NOT per-N data size (refuted that hypothesis)"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Measured (Agda 2.8.0, `/usr/bin/time -v` peak RSS + `+RTS -s` total alloc,
each module force-rechecked with deps cached). Method: probe-copy / delete
target .agdai only, so the number isolates the target's checking on top of
cached deps.

**Floors:** trivial module (Empty only) peak RSS ≈ 62 MB, alloc ≈ 28 MB.
Importing the heavy Coxeter framework but defining nothing already allocs
≈ 387 MB ("framework-load floor") — i.e. most of a module's alloc is
loading cached dependencies, not checking its own content.

**Peak RSS (Δ over 62 MB floor):** Zn-Coxeter-Fin ~88.6 MB (+26.6) FLAT
across n=2,3,4,5,7; Stab-S3-Extend 94.6 (+33); V4/Axioms 75.2 (+13);
Pointed (parametric) 66.9 (+5). No single module exceeds ~100 MB.

**Total alloc (normalization-work proxy):** Stab-S3-Extend 933 MB (~546
intrinsic) — the hog; Z2/Z7-Coxeter-Fin 581 MB each (FLAT in n);
V4/Axioms 321 MB; Fin/Punctured 208; Pointed 129 (~0 intrinsic, ≈ floor).

**REFUTED hypothesis** (mine, from .agdai sizes): "concrete finite data is
heavy because normalization scales with the data." The Zn causal series is
FLAT from Z2→Z7 in both RSS and alloc. Bigger N did NOT cost more. .agdai
byte-size is serialized-interface size, a poor proxy for checking RAM.

**CONFIRMED, corrected mechanism:** cost is driven by NUMBER OF PROOF
OBLIGATIONS / case-clauses and per-case proof complexity, NOT data size.
Stab-S3-Extend's 16 enumerated cases + with-captured equation proofs = 933
MB vs the parametric Pointed keystone's 129 MB (~7×) for comparable
content. The β-law approach ([[project_punctured_fin_primitive]]'s
Fin.Punctured.Pointed: `extend` + extend-point/extend-punchIn +
restrict-extend, ZERO carrier case-splits) measurably does the same job at
near-zero intrinsic alloc.

**OOM diagnosis (All.agda, dozens of GiB):** NOT any single module (all
peak <100 MB). It is AGGREGATE LIVE RETENTION — ~1200 modules' interfaces
+ scope + metas co-resident across the full import graph. The 387 MB
framework-load floor per module is the tell: each module drags a large
cached-dependency working set; All.agda forces them all at once.

**Actionable lever:** collapse enumerated obligations into parametric
β-laws (NOT "use smaller N"). Cuts per-module alloc ~7× AND shrinks
serialized .agdai (29 vs 100 KB) that every downstream loader pays —
compounds across the aggregate build. Best single target: Stab-S3-Extend.
Caveat still standing: NEVER build All.agda locally ([[feedback_never_build_all_agda]]).
