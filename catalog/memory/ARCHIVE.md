# Archive — finished / historical arcs (COLD index, not auto-loaded)

These memories' topic files still exist and are readable; they are moved out of the
hot `MEMORY.md` index because the work is COMPLETE or superseded. Read this file only
for historical archaeology. Promote a line back to MEMORY.md if an arc reopens.

## Completed migrations & extractions

- [c-pos migration arc](project_cpos_migration_arc.md) — COMPLETE (9596d2e): all 28 Z_n-Coxeter consumers → c-pos k; legacy ladder deleted; c-pos = sole canonical name for position-k witnesses.
- [Fin.Literals arc](project_fin_literals_arc.md) — subscript synonyms ₀…₃₂ + fin×fin-cover: 1168 substitutions across ~90 files; 110→18 suc-chains remain (legit).
- [Stdlib audit progress](project_stdlib_audit_progress.md) — COMPLETE: all Data.*/Induction.*/Level migrated; GCD closed via native WellFounded/Divides/DivMod; ~250 files; zero stdlib deps.
- [cong-trans extraction](project_cong_trans_extraction.md) — Foundation.Eq trio + KernelPredBridge pair (5 productions / 67 files / 352 sites); saturated the post-Foundation.Eq surface.
- [Generic nth-power identity](project_nth_power_identity_generic.md) — Coxeter.Cyclic.NthPower proves (suc n)-power identity once; Z2/Z3/Z4/Z5/Z7 = one-liners.
- [Generic inv-canonical](project_inv_canonical_generic.md) — Coxeter.Cyclic.InvCanonical proves inv-* arithmetically; per-Zₙ drops 86 lines via renaming.
- [S3-on-V4 file-per-lemma](project_s3_on_v4_file_per_lemma.md) — 7→39 modules; unblocked similarity twin detection (10+ pairs 0.66-0.79).
- [L-arc cover migrations](project_l_arc_cover_migrations.md) — v4-cover/v4×v4/v4×v4×v4 in V4.Operations; V4.Axioms 112→30 lines; ~200 lines saved across 5 modules.
- [Term-algebra extension](project_term_algebra_extension.md) — T1-T30 added a term-algebra layer (typed cons-list) over 80+14 modules; UP-topos uniformly engaged; 124 modules green.
- [Stab-S3-Extend beta-law migration](project_stab_s3_extend_beta_migration.md) — first β-law-over-enumeration refactor: 72 with-clauses → extend-fn-beta; alloc 933→531 MB (−43%); validated the OOM lever.
- [Punctured Fin primitive](project_punctured_fin_primitive.md) — Fin.Punctured + Axes.Punctured (punchIn/punchOut ≅) landed green; Stab-S3 wiring REVERTED (transport breaks refl round-trips); tradeoff per-consumer.
- [Carrier-locality gate + ℚ arc](project_carrier_locality_gate.md) — Q/Z op-fork: ℚ→canonical ℤ ops unify; _≈ℚ_ setoid + 11/14 field laws; blocking gate split Z/Q Arithmetic into per-op files+barrel.

## Prime-factored-gauge / kinematic arc (ALL COMPLETE)

- [Prime-factored gauge arc (T+UVWX+Y+Z)](discipline/project_prime_factored_gauge_arc.md) — ALL 4 ARCS COMPLETE (49 slices); primitive ladder 14→34; Monster: 3 substrate views.
- [Reserved↔SelfDual bijection gauge](project_reserved_selfdual_bijection_gauge.md) — 168 F₂-linear choices; V₄-equivariance via Cayley-Dickson sacrifice ladder; gauge/sacrifice spaces instantiate 3+1.
- [Tetrative metacircularity](project_tetrative_metacircularity.md) — structural reflection reaches tetrative meta-levels; each instantiates 3+1 parity; gauge-honesty at every level.
- [Thompson coupling kinematic realization](project_thompson_coupling_kinematic_realization.md) — F₂³ tower/V₄-gauge/sacrifice-ladder on Reserved-SelfDual maps to a Thompson coupling; CV-joint anatomy.
- [Kinematic gauge-sacrifice catalog](project_kinematic_gauge_sacrifice_catalog.md) — 16+ CV-joint family in 3 discrete Sylows + a continuous-field class; discrete-to-continuous lifts.
- [Continuous-limit lift framework](project_continuous_limit_lift_framework.md) — so(3) Lie-algebra connection; Sylow families reduce the constraint manifold; limit dissolves to SO(3) field.
- [Gauge-sacrifice template universality](project_gauge_sacrifice_template_universality.md) — generalizes beyond CV joints (gimbal, Stewart, wrist); 5th class (Continuum Couplings) formalizes 4+1.
- [168 tower as FanOut](project_168_tower_as_fanout.md) — 168-gauge family is FieldFanOut 3 over Z/168 → (F₂³, F₃, F₇); the sacrifice ladder is gauge-choice.
- [Codec as PFG witness (third leg)](project_codec_as_pfg_witness.md) — scratch/eliza realizes PrimeFactoredGauge at S₄ = V₄⋊S₃; chain-of-charts; per-Sylow agreement breakdown.
- [Q1-Q5 entailment chain](project_q1_q5_entailment_chain.md) — PFG arc via 5 questions (root→Baby Monster→Monster→Galois→Griess→word-algebra); each probes an extreme case.
- [Klein quartic kinematic anatomy](project_klein_quartic_kinematic_anatomy.md) — gauge-classes map to Sylows of GL(3,F₂) ≅ PSL(2,7); CV joints = analog computers; three Sylow-canonical bijections.

## OOM/opacity investigation (done parts; durable findings stay in MEMORY.md)

- [OOM memory profile 2026-06](project_oom_memory_profile_2026_06.md) — MEASURED per-module <100MB FLAT in N; cost = case-COUNT not data size. Superseded by the load-bound finding.
- [CycleN opacity fix](project_cyclen_opacity_fix.md) — Cycle7 OOM = dense matrix-power normalization forced by cyclic-HasOrder {6}; FIXED by `opaque` (OOM→762MB/5s); CycleN dense exports are PoCs.

## Analyses, dossiers, corrections (one-off)

- [Cluster-to-action analysis 2026-05](project_cluster_to_action_analysis_2026_05.md) — 22-cluster SPPF sweep; 8 extractions; 6 verdict retractions.
- [Type audit + SPPF](project_type_audit_sppf.md) — 493 types: 7 dead, 0 postulates, bimodal; correction: reactions primary not enumerators (POSIWID; reaction-SPPF = Forgetful side).
- [Witness-Tower dossier](project_witness_tower_dossier.md) — portable formalization (witnessed-simplex → S₄=V₄⋊S₃ → RM(1,4) → Elduque sl₂⊗A). §8 UPTerm DISCHARGED: "∷ lifts simplicial dimension" NOT in code (lifts chain-position). Reading defensible, not literal.
- [Deliverable scan 2026-06](project_deliverable_scan_2026_06.md) — repo-wide deliverable scan; 2 fixes landed; 11 deferred arcs (now folded into project_open_threads).
- [SESSION HANDOFF 2026-06](project_session_handoff_2026_06.md) — handoff index for the memory-arch/opacity session; superseded by continued work on branch session/memory-arch-and-policy.
- [K-v4-twins-fail-cells false negative](project_k_v4_twins_fail_cells_false_negative.md) — catalog's negative claim is LLM negation-overclaim; the V₄-twin construction is sound.
- [Composite torsion lift via Euler-Fermat](project_composite_torsion_euler_substrate.md) — FLT lifts to Euler-Fermat for composites; Euclid/ExtEuclid backbone.
- [R-arc lambda-VM recognition](project_rarc_lambda_vm_recognition.md) — the machinery IS a lambda-VM in a Cartesian-closed category; R-arc adds 14 control opcodes + OpcodeAlgebra.

## Superseded framings / instance catalogues

- [3+1 parity as graded cocycle](project_3plus1_as_graded_cocycle.md) — SUPERSEDED by "3+1 IS a cone instance" (kept live); 3+1 = degree-1 cocycle in GradedMonoid, Z/2 grading.
- [Cycle generator as 2-cocycle](project_cycle_generator_as_2_cocycle.md) — FreeCyclic's cycle generator in 2-D word algebra is a 2-cocycle; Z/4 vs V₄ are H²(Z/2;Z/2) classes.
- [F₂-grading at substrate sites](project_f2_grading_at_substrate_sites.md) — catalogue of F₂-graded structures (V₄'s three gradings, Bivector weight-parity).
- [FreeLinearization at substrate sites](project_freelinearization_substrate_sites.md) — catalogue of FreeLinearization #6 instances (HodgeStar, Cycle3).
- [Cones at substrate sites](project_cones_at_substrate_sites.md) — catalogue of Cone / Cone.WithMorphisms instances (V₄ 3+1, Hamming 7+1, HodgeStar ★-cone).
- [Eliza concept-orbit catalog](project_eliza_concept_orbit_catalog.md) — scratch/eliza concept-orbit catalog; quotient-curvature / orbit-intersection-fiber candidates.
