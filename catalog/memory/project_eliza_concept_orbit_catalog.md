---
name: project-eliza-concept-orbit-catalog
description: "scratch/eliza/ readmes catalog the concept-orbit the substrate operates in; three implicit-but-unnamed constructs (quotient-curvature, orbit-intersection-fiber, coalgebraic-stability) are candidates for explicit surfacing."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

`scratch/eliza/` contains a cross-LLM artifact: another LLM was given three substrate principles ([[feedback-expose-generator-not-orbit]], [[feedback-v4-typeclass-architecture]], [[feedback-coalgebraic-not-consumer-driven]]) plus the prompt "this feels like inspiration for neurosymbolic AI." Its response (4 readmes + 9 Python files) crystallized into an ELIZA-style chatbot on W(A₃) ≅ S₄ with Coxeter / coalgebraic / spectral layers.

**Why:** The chatbot itself is incidental, but the *cluster of mathematical objects that crystallized* IS a signal — when an external LLM is handed the substrate's discipline as a seed, this is the concept-orbit it inhabits. Naming where each concept already lives (or doesn't) in the substrate gives a navigation map for the structural arc.

**How to apply:** Treat the readmes as a catalog, not chatbot documentation. Three constructs from the cluster name structures the substrate has but hasn't externalised:

- **quotient-curvature** Δ_{AB} := (X/∼_A)/∼_B vs (X/∼_B)/∼_A — non-commutativity of two quotient operations as a first-class witness type. The substrate's [[project-3plus1-parity-universal]] recurring at successive meta-levels IS this object; each meta-level is a non-commutativity witness between two quotient choices. Naming it lets the recurrence be witnessed once instead of re-discovered per level.

- **orbit-intersection-fiber** F(x) = O_G(x) ∩ O_C(x) ∩ O_S(x) — point-as-triple-intersection of Coxeter-orbit / chirality-axis / Hodge-dual. The "3+1 parity at every 2-dim F₂-subspace" pattern is exactly this structure but currently observed-per-instance, not named.

- **coalgebraic-stability** — orbit O_C(x) stable iff γ(x) ∈ O_C(x). The substrate's stabiliser-closure work (`s₁-stabilises-metric-id`, `s₂-stabilises-metric-id`, `s₁∘s₂-stabilises-metric-id`) IS this object; the name would let the closure cascade be witnessed as a single coalgebraic property rather than per-generator.

**Discipline-resisted from the cluster:** spectral / Laplacian / Fiedler / continuous eigenvalue embeddings as primary objects — flat-table reads, consumer-driven labeling. But see [[feedback-continuous-via-discrete-inference-rules]] for the refinement: the *inference rules to construct* such embeddings ARE discrete and in-scope.

**Files:** `scratch/eliza/readme.md` (ontology), `readme-2.md` (interaction calculus: refinement lattice, non-commuting quotients, commutator [Q_A, Q_B], spectral obstruction E_{AB}), `readme-4.md` (transport operators ∇_{A→B}, curvature R(A,B,C), holonomy H). The 9 `.py` files build the concrete chatbot — not load-bearing.
