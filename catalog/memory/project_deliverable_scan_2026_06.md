---
name: project_deliverable_scan_2026_06
description: "2026-06 repo-wide outstanding-deliverable scan + recursive-collapse triage; 2 fixes landed (Pontryagin ops, Stab-S3 non-anchors generator)"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Repo-wide scan (4 parallel Explore agents) for outstanding deliverables,
triaged with [[feedback_common_substructure_recursively]]. Key insight:
the findings themselves collapse — "skin-deep theorems" (claim, zero
witnesses) and "Cayley tables / reducible chains" (claim, N redundant
witnesses) are ONE substructure: distance between a claim and its single
generic witness. Real debt exists only where the generic primitive is
MISSING; where it exists and leaves are deliberate thin instances
(v4×v4×v4-cover, Coxeter.Cyclic n, cyclic-suc {n}, Zn-Coxeter re-exports,
Cyclen, HigherArity), there is no either/or — flagging them would re-fight
settled gauge decisions (anti-overclaim).

**Genuine untracked debt found:**
- Under-realized ORPHANS (not covered by any arc plan): Pontryagin
  dual-mult/dual-inv identity stubs; HodgeDim4 MetricGauge cardinality `?`
  ([MetricGauge.agda:23]); Hamming [8,4,4] distance ([H-8-4-4.agda:34]);
  Bezout commented-out ([Bezout.agda:111]).
- Over-realized with MISSING generic: Stab-S3 bridge tables (the
  "non-anchor axes" permutation had no name).
- Already-TRACKED under-realized (leave to their arcs): Yoneda reverse
  (B-arc), Conway assoc (S-arc), Interchange (HC-arc), Z30 CRT (QU-arc).

**Landed this session (both standalone-verified, NOT via All.agda):**
1. `Algebra/PontryaginDual/Sites/Zn.agda` — replaced identity stubs with
   real `add-mod`/`neg-mod` (cyclic add / inverse mod suc n) via
   `_mod-suc_` + `mod-suc-bound` + `fromℕ<`. Record has NO law fields so
   stubs weren't vacuous-proof bugs, just wrong data; now correct as data
   (laws still unwitnessed — noted in-file, not overclaimed). Consumer
   `Sites/Manifest` green.
2. `Groups/Stab-S3.agda` — extracted `non-anchors : Axis → Vec Axis 3`
   (the "skip anchor, declaration order" gauge the header documents);
   `fin3-to-non-anchor anchor = lookup (non-anchors anchor)` collapses 12
   clauses to one. `lookup` on concrete vec+Fin reduces definitionally so
   all 7 consumers' `refl` round-trips preserved (verified: Stab-S3-{
   Restrict,Extend,Iso,Hom}, Cocycles/V4Signature/S4Iso-Bridges +
   StabElements all green). Backward map `non-anchor-to-fin3` left
   enumerated (carries ≢-proof + ⊥-elim; forcing it through search would
   ADD complexity — principle says don't).

Inventory of self-declared deferred arcs (11 major, ~190 slices: B/UP+HC/
Q/E/M+Mod/S/C/D/Y/FLQ/QU) lives in scratch/*_arc_plan.md — untouched.
