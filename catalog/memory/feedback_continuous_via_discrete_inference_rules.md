---
name: feedback-continuous-via-discrete-inference-rules
description: "Continuous fields' specific embedding content is out of scope; the inference rules to construct such embeddings ARE discrete and in-scope. Bridging happens via constructors, not enumerations."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Rule:** The substrate is discrete and intuitionistic. Continuous-valued embeddings (Laplacian eigenvectors, Fiedler polarities, character-value vectors over ℂ, heat-kernel evaluations) are out of scope as *specific content*. But the **inference rules that CONSTRUCT such embeddings are discrete**, and those inference rules ARE in-scope.

**Why:** Refinement to [[feedback-expose-generator-not-orbit]] and [[feedback-coalgebraic-not-consumer-driven]]. The earlier framing risked collapsing "no Laplacian eigenvectors as primary objects" into "no continuous-side structure at all." But construction-of-eigenvector is a discrete combinator: Cayley-graph-from-generators → adjacency-matrix → characteristic-polynomial → eigenpair-as-kernel-of (M − λI). Each step is a discrete inference rule. The substrate should formalize the rules; consumers downstream may evaluate them at specific n to obtain specific real-valued vectors, but that evaluation is not the substrate's product.

**How to apply:**

- **In scope as discrete inference rules:** representation theory of S_n via Coxeter character relations; spectral-decomposition-as-construction-recipe; Fourier basis on a Cayley graph as combinator over generators; diffusion / heat kernel as polynomial in adjacency operator; character table as discrete combinator on (conjugacy-classes × irreps).

- **Out of scope as flat-table content:** the specific 24-vector Fiedler embedding of S₄'s Cayley graph; hand-tuned thresholds on continuous values (polarity > 0.15); specific eigenvalue numerics.

- **Bridge pattern:** when a continuous-side concept comes up, ask "what is the *constructor* for this, expressed as discrete inference rules over the substrate's existing carriers?" If the answer is a finite combinator, formalize it. If the answer requires real-analysis machinery, defer (but note the gap explicitly, not via silent omission).

**Diagnostic:** if a slice begins with "let v be the Fiedler vector of M," that's consumer-driven flat-table enumeration. If it begins with "define `fiedler-spec : Graph → (Vector × ℝ) → Set` such that `fiedler-spec G (v, λ)` holds iff v is a normalized eigenvector at the second-smallest eigenvalue of L(G)," that's a discrete inference rule whose evaluations land in the continuous side without the continuous side being primary.

**Connection to existing discipline:** this generalizes [[feedback-expose-generator-not-orbit]] from "expose group generators" to "expose construction generators for any structure whose flat enumeration would be consumer-driven." The eliza/ artifact's spectral side is the test case — see [[project-eliza-concept-orbit-catalog]].
