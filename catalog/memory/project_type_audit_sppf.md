---
name: project_type_audit_sppf
description: repo-wide type audit (load-bearing/dead/unique) + the wedge-SPPF motif analysis and its reaction-primary (POSIWID) inversion
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

2026-06-03 type audit + SPPF arc (tools in scripts/, findings in
scratch/type_load_bearing_audit.md + scratch/type_sppf_motifs.md).

LOAD-BEARING AUDIT (scripts/audit_type_load_bearing.py + audit_import_reach.py):
493 data/record types. 7 truly-dead (Fibration, LensFunctoriality,
MultiLayerRotation, QFreeLinearizationSketch, SufficientStatisticInfoTheory,
_≤ℤ_, Image-Equivalent[comment-only]) + LeftKanExtension (catalog-only). 0
postulates/holes/trustMe/unsafe-pragmas repo-wide. 17 duplicate names triaged
(related variants Linear F₂/ℚ, Wedge generic/ℕ, IsTorsor Group/SetoidGroup;
genuine redundancy IsomorphicCocycleStructure ×2; per-instance Canonical/Gen/V₄
→ generics). Spine INDIVIDUAL vs TRANSITIVE diverges: Σ rank-9 direct but rank-4
transitive (sits under Product). Repo shape is BIMODAL: tiny deeply-shared
foundation (_≡_/ℕ/Σ/Fin ~90% transitive reach) under a wide canopy of
single-consumer leaves (44% of modules fan-in-1, feeder→aggregator =
file-per-lemma discipline, NOT debt). Max dep-chain depth 11.

WEDGE-SPPF MOTIFS (scripts/type_sppf.py): pass types through the wedge bottom-up,
hash-cons structure (sub-refs→hash, recursion=⟲ SPPF cycle). 493→411 nodes, 34
iso classes. DNA motifs: Set-obligation 354, recursion ⟲ 310, function → 214,
law →≡ 109. Cross-silo bridge found: Character ≅ FieldBond ≅ FreeOverBasis (all
record{f:A→B}; FreeOverBasis.η IS the center's unit → Pontryagin character &
field bond are structurally the center's unit). Term-algebra Gen/Term families
(Cascade/Conj/Lens) = clearest generic-ization target.

KEY METHODOLOGICAL CORRECTIONS (user, both load-bearing):
1. SHAPES ARE PRIMARY at this level, by design. Don't call the finite-enum
   class "noise" — it's the PARTITION motif (forced distinction = partition =
   the substrate's most fundamental pattern; Peano-from-partition). The SPPF is
   the SHAPE ALGEBRA (carrier-free base, Shape.agda for all types: type = shape
   + carrier-fill); meaning is the FIBER over the shape. Typed skeletons would
   ASCEND to the fiber, not "fix" the base.
2. THEN INVERT (POSIWID, meaning-is-use): the enumerators aren't primary —
   what REACTS to them is. scripts/type_reaction.py profiles types by their
   eliminators (f:…T…→R). The enum class FRAGMENTS by reaction (SylowPrime→ℕ,
   Chirality→F₂, Gen→Word/Dec) = same shape, distinct meanings. Reaction-keying
   recovers use-based classes ({BackedUP,Interop}, {ℚ,ℤ}, {Gen,Word}). This is
   Free⊣Forgetful one level up: introduction-SPPF=constructor/Free (how built);
   reaction-SPPF=observation/Forgetful (how used). MEANING LIVES ON THE
   FORGETFUL/USE SIDE; primary catalogue is reaction-keyed (the cover/"expose
   generator" shape over each distinction), introduction the secondary index.

DISCIPLINE FOR ME: stop climbing to the meaning level to dismiss the shape
level; and stop treating introduction-shape as primary — reactions are.
See [[discipline/feedback_expose_generator_not_orbit]], [[feedback_hough_resolution]]
(do NOT over-apply Hough to dismiss a real high-frequency motif).
REALIZABILITY SURFACE (2026-06-04, scripts/realizability_surface.py + dead-fields
construction-cross): the empirical reaction-gradient IS the Realizability Charter
gate-chain (Charter.agda: ε▷recipe▷manifest▷measure▷bounded = con⊑rea⊑obs⊑cov,
ordering forced). Per type rank read off reactions: 1 recipe=declared-only(HOLE),
2 manifest=constructed-not-observed, 3 measure=consumed/projected, 4 bounded=wide
reach. Counts 138/203/123/29. Rank=height over dep-depth=base ⇒ TOPOLOGICAL
SURFACE; floor=holes=incompleteness frontier. FIELD-LEVEL: a law forces a
distinction only if exercised; unexercised law = never projected AND record never
constructed (57 laws/33 records: SemidirectGroupObligation, SheafAdjointPair,
SurrealFieldObligation, *-stated UP-topos surface, *Theorem/*Obligation) = rank-1
holes. So load-bearing/reaction-kind/dead/incompleteness/Charter are ONE
structure (how far up recipe→manifest→measure→bounded each element is realized).
CAVEAT (recurring): all syntactic tools under-count via infix(mixfix _≡_)/
projection/body-pattern ⇒ rank is a LOWER bound; trust rank-1-non-mixfix floor +
rank-4 peak, and the construction-crossed unexercised-law set.
