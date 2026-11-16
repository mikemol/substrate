---
name: project_seam_glue_xi_arc
description: The Ξ arc — discharging M2 (realized closure A₄×ℤ₂ vs S₄) in --safe Agda; symbol roster for dispatch
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

The **Ξ arc** = discharge **M2** (`K-M40-aggregator`: the M40 spectral closure is **A₄×ℤ₂**, NOT S₄)
at the substrate's `--safe --without-K` gold standard, from `SEAM_GLUE_SPEC.md` (a PROPOSAL, not a
claim — test it, don't defer to it). Full plan + states: `scratch/seam_glue_discharge_plan.md`;
proof in `scratch/seam/M40Closure.agda` (scratch = out of build tree until the Ξ6 checkpoint).

**v2 SPEC (2026-06-17) — M2 is TWO obligations, two layers (don't conflate):**
- **A. the seam** (gauge∩interface V₄ = a V₂) — ABSTRACT S₄ geometry — **ALREADY BUILT**:
  `WitnessTower.B3Split` (refl over the enumeration: gauge pairs ≡6→1 subgroup, interface ≡18→3; seam
  = gauge∩interface = {id,d} = V₂; NO Sylow/D₈) + `WitnessTower.WhyThreeV2` (`conj-trivial`; three V₂s
  permuted only by external Aut(V₄)=S₃). CITE, don't rebuild.
- **B. centrality** (chirality a central direct factor of the *REALIZED* closure) — the real open work.

**THE TRAP v2 names (it indicts my Ξ1/Ξ2):** proving a tautology by reading the MODEL
(`a4z2_compose`, DEFINED as a direct product) instead of the GENERATORS. My `central-χ`/`no-order-4`
are MODEL-side facts (B2 territory) — true, needed by B2, but NOT the load-bearing claim. **The
load-bearing claim is B1: the REAL generator ACTIONS close to the model.** v2 also reins in my
over-collapse: "direct-factor-central" alone gives only G×ℤ₂; landing A₄×ℤ₂ ALSO needs (ii) V₄⋊ℤ₃=A₄.
Common structure of the two layers = the ISO realized-closure ≅ abstract A₄×ℤ₂; B1 IS that bridge.

**DECISIVE READ DONE (resolved v2's open question):** `verify_architectural_primitives_generate_a4z2()`
closes the REAL actions `architectural_primitives_level_2 = {spectral_translation×3, z3_cycle,
chirality_flip}` via `generate_group_by_action` (composes lambdas on carrier F=[10,20,30,40]) and
checks `set(group.keys()) == {a4z2_act(g,F)}`. SOUND, not circular ⟹ **Agda B1 = faithful PORT.**

**Symbol roster (v2-aligned; dispatch by "Tackle Ξ…"):**
- **Ξ-A** ✅ DONE — the seam = `B3Split`+`WhyThreeV2` (cite). Not my code.
- **ΞB1** ✅ CLOSED (all typecheck --safe --without-K). The explicit iso ⟨real generator actions⟩ ≅ A4Z2
  = conjunction of 4 lemmas: `act-hom` (M40Action: act IS a homomorphism — a4z2_compose computes the
  composition of the REAL actions; rests on rotate-IsHom + rotate³-id, non-tautological) + `T/Z/chi-gen`
  (real spectral_translation/z3_cycle/chirality_flip = act of model gens) + **(a)** `reconstruct`
  (M40Iso: every (s,m,j) = generator-product ⇒ closure = act(A4Z2), not just ⊆) + **(b)** `act-faithful`
  (M40Iso: act injective on probe carrier V₄×Chir, F₀ k=(k,even) — the Python F=[10,20,30,40] analogue
  ⇒ A4Z2 ≅ act(A4Z2)). B1's observable COMPUTED FROM the generators, not read off the model. NOTE: iso
  is the conjunction, not yet bundled as one group-iso record (cosmetic).
- **Ξ6** ✅ DONE (commit 8d21bef) — HOMED into `agda/Substrate/WitnessTower/M40{Closure,Action,Iso}.agda`
  (beside B3Split/WhyThreeV2/SharedMiddle). Typechecks in-tree; makefiles regen'd; all blocking gates
  green; committed by path; scratch dev copies removed. NON-BLOCKING advisory: categorical-grounding
  flags M40Closure FLOATING (group laws, no structure record) → grounded by ΞB2ii (bundle as
  (V₄⋊Z₃)×ℤ₂), NOT papered over.
- **ΞB2i** ✅ = my `central-χ` (typechecks) — the central direct factor (model-side).
- **ΞB2ii** ✅ DONE (commit 202b0be, agda/Substrate/WitnessTower/M40Group.agda). (1) GROUNDING: A4Z2
  bundled as `Algebra.Group` (compose-assoc via σ-hom/σ-add/·-assoc; ι identity; inv (s,m,j)⁻¹=(s,c⁻ʲm,−j))
  — discharges the FLOATING advisory (now GROUNDS-IN-ALGEBRA). (2) SPECIFICALLY A₄: σ z1=rotate is the
  A₄ action — automorphism (rotate-IsHom) + order-3 (rotate³-id) + 3-cycles involutions α→β→γ→α + fixes e;
  the nontrivial 3-cycle ⟹ V₄⋊ℤ₃=A₄ not abelian V₄×ℤ₃ (v3's guard). RESIDUAL advisory = Algebra∥Category
  gap = **Ω2** (deloop bridge), project-level, NOT M2 scope (v3: don't pull adjacent threads).
- **ΞB3** ✅ DONE (commit a4a738c, M40Contrast.agda). S₄ side witnessed: `fc` = 4-cycle e→α→β→γ→e on
  the masks ∈ Sym(V₄)=S₄; `fc-order-4` (HasOrder fc 4) + `fc-not-order-2` (fc² moves e→β≢e ⇒ order
  EXACTLY 4) = `S₄-has-genuine-order-4`. Contrast: `no-order-4` FORBIDS this shape ⇒ the distinguishing
  invariant; tracks chirality (central, ΞB2i → A₄×ℤ₂, no order-4) vs transposition (non-central → S₄,
  order-4). SCOPE: distinguishing invariant, NOT the full machine-checked ¬(A₄×ℤ₂≅S₄) (needs
  order-preserved-under-iso transport — flagged, optional hardening).
- **ΞG** ✅ DONE (commit ace6e5f, M40Gauge.agda). Gauge-invariance via LABEL-UNIFORMITY (not an
  automorphism argument — TEST-THE-WALL: naive even↔odd swap is NOT a group hom, oflip(a*c b)≠oflip a
  *c oflip b, Aut(ℤ₂) trivial). `central-sign` (every pure-sign element central, BOTH labels, central-χ's
  proof generalised over s — odd never privileged) + `gauge-flip-invariant`/`gauge-equivariance`
  (centrality holds at flipped label oflip s ∀s — equivariance, the torsor shape for the sign gauge) +
  `gauge-involution` (oflip²=id). Not a fixed-gauge artifact.

**M2 FULLY DISCHARGED (2026-06-18)** at --safe --without-K: Ξ-A (seam,B3Split) + ΞB1 (closure≅A₄×ℤ₂,
computed from generators) + ΞB2i (central) + ΞB2ii (specifically A₄, A4Z2 grounded as Algebra.Group) +
ΞB3 (S₄ excluded, order-4 contrast) + ΞG (gauge-invariant). The Python catalog [theorem] tag is now a
proof. 6 modules under agda/Substrate/WitnessTower/M40{Closure,Action,Iso,Group,Contrast,Gauge}.agda
(commits 8d21bef, 202b0be, a4a738c, ace6e5f). OPTIONAL hardenings: **Ξ8 ✅ DONE** (commit aa241d2, M40NoIso.agda) — `no-iso : A4Z2≅SymV4 → ⊥`,
the FULL machine-checked ¬(A₄×ℤ₂≅S₄) via order-transport (an iso carries S₄'s fc to an order-4 elt of
A4Z2, forbidden by no-order-4; the A4Z2≅SymV4 record = the iso's order-relevant structure, entailed by
any real iso). REMAINING optionals: Ξ9 (bundle ΞB1's iso as one GroupIso record); Ω2 (M40Closure→Category
bridge, the standing advisory). 7 M40 modules now: +M40NoIso.
- **Ξ7** ✅ DONE (commit 610798d). Mechanically verified the Agda `compose` (M40Closure) ↔ Python
  `a4z2_compose` operator-for-operator (jea_seam_provenance: _*c_↔Mult, _·_↔BitXor, σ↔_apply_cycle,
  _+₃_↔Mod; FAITHFUL). The G8 transcription blind spot is now MECHANICAL + GATED (jea_metalanguage_gate
  17 pass; opportunistic SKIP if M40Closure.agdai unbuilt). **Φ8 NOT needed** — homing (Ξ6) put the
  .agdai in-tree so deps resolve. PROMOTION (Λ8 fix, user chose whole-file): spectral_view.py git-mv'd
  scratch→jea/metalanguage/ (imports only typing ⇒ Λ8-clean); importers re-pointed (applied_grammar.py,
  scratch/verify_spectral.py 98/98, decomposition string). FLAGGED for user: scratch/applied_grammar
  (1).py (identical dupe of root) + applied_grammar_v12_backup.py still ref spectral_view (stale cruft,
  not repointed — delete-or-repoint is user's call). LESSON: Λ8 gate forbids gated-jea→scratch; the fix
  is PROMOTE the dep to its real home, not relocate the check (the "no").

**v3 SPEC (2026-06-17) reconciliation:** v3 = v2 + the witness-as-invariant-fiber property now VERIFIED
(`jea_sppf_torsor.py`), so B1 has a substrate-NATIVE shape (obligation node: op=claim, children=composition
witnesses, empty-children unreachable). KEY: my `act-hom` ALREADY embodies this — a --safe Agda proof
term IS the witness-bundle (postulate/hole = empty children = doesn't typecheck). So --safe = the forest's
"no node completes without its kids." v3 changes no theorems; it reaffirms B1's open observable = my
PENDING (a)+(b). OUT OF SCOPE per v3 (do NOT pull into B): the Hodge ★ Λ²(F₂⁴) n=4 vs apex-duality ★ n=3
bridge (Hodge.agda §3 leaves unidentified) — touches [[project_commuting_sphere]]; respect the fence.

**Status of old labels:** old Ξ1→ΞB2i (kept), Ξ2→model-half of ΞB3, Ξ3/Ξ4/Ξ5 fold into ΞB1/ΞB2ii/ΞG.
`scratch/seam/M40Closure.agda` (Ξ1/Ξ2) typechecks but is the MODEL side; the realized-closure port (ΞB1)
is the new top priority. ONE agent holds jea+AI-Q roles (split RETIRED; by-path + no-`--no-verify` stays).
**G9 recurring:** prose-overclaim ahead of code ([[feedback_comments_dont_overclaim]]).
