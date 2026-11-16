---
name: project_split_idempotent_apex
description: "The apex unifying every section-based quotient in the substrate: a retraction (F∘s≡id) gives a split idempotent s∘F that IS a Canonical form for ker F. Built at Algebra.Quotient.split-Canonical."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

`Algebra.Quotient.{KerRel, ker-Quotient, split-Canonical}` (built 2026-06-13). THE
common structure under every section-based quotient in the substrate, found by the
recurring user directive "faced with an either/or, find the common structure recursively."

**The lemma.** For `F : A → B` with a section `s : B → A` and `retract : F∘s ≡ id`:
`ker-Quotient F` is the equivalence `x ≈ y ⟺ F x ≡ F y`, and `split-Canonical F s retract`
is a `Canonical` for it whose canonical form is the **split idempotent** `e = s∘F`
(idempotent because F∘s=id — a Karoubi splitting). All four `Canonical` laws fall out of
`retract` + `cong s`. Level-polymorphic (works for A : Set₁ like UPTerm and A : Set like ℚ).

**Why it matters.** "No quotient types under --safe --without-K" is a NON-ISSUE: a
quotient by `ker(fold)` is realized constructively, with no quotient type, exactly when
the fold SPLITS. A lossless round-trip IS a retraction (the user's "we already have Q,
wedge, lossless Q↔R" — that round-trip is the section). The substrate realizes quotients
by canonical forms = split idempotents, never HITs. Resolves [[feedback_registry_as_pi_not_markdown]]'s
sibling concern at the type level.

**The cluster it's the apex of** (was scattered, no unifying lemma — a textbook
[[discipline/feedback_cluster_means_find_apex]] gap): eval/reify (UPTerm/≈ᵤ), ℚ `reduce`,
the wedge `recon` (a ≡ recon q b r — the LOSSLESS/degenerate case where the idempotent is
identity: [[feedback_never_discard_residue]]), EEA CF-shape, CRT `combine`, Coxeter
`normalize`, GenericHodgeStar `star`/`star-inv`, BeckChevalley section/retraction. Each is
an (F, s, F∘s≡id) triple whose split idempotent is its canonical form.

**UPTerm instance (wired, load-bearing).** `Category.UniversalProperty.Eval`:
`UPTerm-Quotient = ker-Quotient eval`, `UPTerm-Canonical = split-Canonical eval reify
eval-reify`. eval = the fold (the instance of `foldUPTerm`, the free-category universal
extension), reify = the section, `normalize = reify∘eval` = the split idempotent, UP4 =
ker eval. So foldUPTerm / eval / UP4 / det=(−1)ⁿ / routing all collapse to ONE schema:
free syntax + interpretation into a target + kernel; and when the interpretation splits,
the kernel is a Canonical. Ties to [[project_center_free_universal_property]] (Free⊣Forgetful)
and [[project_sppf_eea_unification]].

**Instances wired:** UPTerm/≈ᵤ (`split-Canonical eval reify eval-reify`) and the ℕ wedge
(`Algebra.Nat.GCD.WedgeCanonical`: `split-Canonical recon-pair divide-pair recon-divide`,
the improper→proper quotient). Both load-bearing.

**The detector** (`scripts/law_motif_apex.py`): clusters FUNCTION SIGNATURES by relational
law-motif (the index agda_similarity=token-cosine and type_sppf=data/record-only both miss;
why = the law is a ~3-token type-invariant in disjoint vocabularies, split across an (F,s,
proof) triple). Instance vs apex by BINDING: concrete F,s = instance, bound F,s + law-as-
hypothesis = apex. It confirms split-Canonical IS the retraction apex and quantifies
convergence: **retraction f(g x)≡x — 52 instances, ~5 use-sites → 47 candidates to route
through** (eval∘reify, from∘to, crt-backward∘crt-forward, lambek out∘into, …).

**Apex-candidates → all CLOSED + a BLOCKING GATE wired (a4a4548).** The detector now
gates: `law_motif_apex.py --check` fails if any law-motif (≥3 instances) lacks a parametric
apex — wired into the pre-commit hook AND `make check` (gen_build_makefiles' check-apex
target). NO baseline (no grandfathering), no human triage (the rule decides); remedy =
"build the PARAMETERIZABLE apex, NOT an index" (the PrimitiveInstances lesson: an index
forces concurrent building, an apex is a parameterizable module). The 3 candidates it
surfaced were closed to turn the gate green:
  * idempotent f(f x)≡f x  → `Algebra.Quotient.idem-Canonical` (an idempotent IS a Canonical
    for its own kernel; split-Canonical = the e=s∘F special case).
  * involution f(f x)≡x    → `Algebra.Involution.invol-injective` (an involution is injective;
    k=2 of [[project_torsion_element_universal]]). Hypothesis written INLINE so the motif is
    visible at the binder (the detector doesn't unfold aliases like `IsInvolution`).
  * homomorphism f(x⊕y)≡…  → DROPPED from the detector (bare law has no clean apex; the
    heuristic was unreliable — fixing a buggy classifier, not punting judgment).
Detector coverage = the motifs in `classify()` (retraction/involution/idempotent); add more
law-motifs there as recognized. Retraction still has a 71-instance CONVERGENCE gap (only
~5 route through split-Canonical) — gate checks apex EXISTENCE, not convergence; wiring
ℚ-reduce/EEA/CRT/roundtrips through split-Canonical is the open follow-up (refactor-with-care).
