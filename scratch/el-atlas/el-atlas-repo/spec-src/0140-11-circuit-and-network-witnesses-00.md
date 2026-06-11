## 11. Circuit and network witnesses

The logic has a realized electrical instance. The honest grade (draft 7,
tightened against external review) is **functorial-shape correspondence**,
not literal identity: there is a structure-preserving map between the
logic's connective algebra and the network's combination algebra that
preserves the V₄ and its De Morgan diagonal, witnessed at the level of
*form* (the values are the chart, the form is the invariant). Where this
section formerly said "the same algebraic object," read "the same algebra
*up to the explicit functor named in each item*" — following the
Baez–Fong decorated-cospan template (App. B, S-G), which is how a
network↔semantics correspondence is stated rigorously. Claims of literal
identity beyond the witnessed functor are downgraded to **[C]**. Each
item below is a witness for a section above.

### 11.1 The conductor square (witness for §5–§6)

Series combination adds resistances (R = R₁ + R₂); parallel combination
adds conductances (1/R = 1/R₁ + 1/R₂). Series/parallel are dual under
R ↔ G = 1/R — the same swap as AND ↔ OR under ¬. The square
{series, parallel} × {R, G} is a V₄: series/parallel is the AND/OR axis,
R/G is the negation axis, and their product — the diagonal — is
**De Morgan as the unique law-preserving move** of the square. **[W]**

Precision the algebra forced: De Morgan maps the law-*form*
(X₁ + X₂ ↦ Y₁ + Y₂, same shape, dual quantities), not the value —
series-R-read-as-conductance is not numerically equal to parallel-G; they
are different circuits. De Morgan is a duality of forms, and the square is
its Cayley graph. **[W]**

With this, De Morgan is witnessed from **three independent directions**
landing on the same V₄ diagonal: gate composition ({IDENT, AND, NOT,
XOR}), the differential rail-swap (the pin-swap of §5), and the
conductor-square diagonal. **[W]**

### 11.2 The flat-binding theorem (witness for §5; closes a fork)

Binding De Morgan's V₄ to any other V₄ is choosing one of the 6
isomorphisms (Aut(V₄) = S₃). Of these, **2 preserve the De Morgan
diagonal (flat; they form the C₂ stabilizer of the diagonal) and 4 move
it (twisted)**. Flat-vs-twisted is therefore a property of the *binding*,
not of any circuit or network — decidable, intrinsic, no external data.
Every V₄ in the construction — the gate, the Belnap/crossbar (§4), the
shape-frame, the conductor square (11.1), the constraint plane — was
built with De Morgan as its diagonal, so all these bindings are **flat by
construction**. A twist could only enter by binding to a V₄ that places
De Morgan off-diagonal, or by binding to a non-V₄ and manufacturing the
structure (which smuggles in the placing choice). **[W]**

### 11.3 The Wheatstone bridge: the crossbar as instrument (witness for §4)

The bridge's two sense corners are E⁺ and E⁻. The **galvanometer reads
their difference — bias b**; the **supply reads their sum — mass m**.
The Wheatstone bridge is the physical instrument of the (mass, bias)
basis of §4. **Balance is the null of the difference — the pin-swap
fixpoint**: a balanced bridge is one where swapping the two sense arms
changes nothing, i.e. the De Morgan involution at its fixed point. The
galvanometer reads this null in the *multiplicative chart* (a ratio
E₊/E₋=1), the pin-swap fixes it in the *additive chart* (a difference
b=0), and the two are the same locus across the exp ⊣ log adjunction
(Lemma 2.5b) — the **chart-image** ratio, not the forbidden **collapse**
ratio (Remark 2.5c). The
B/N axis (zero bias) is the balanced condition: one can be balanced at
high supply (B, conflict) or low supply (N, absence) — the mass axis,
orthogonal to what the galvanometer reads. Drive and sense occupy
orthogonal diagonals; the galvanometer reading is the deviation from that
orthogonality. **[W]** (the structural correspondence; see OB-5 for the
strong form.) The corpus consolidation adds the categorical grade of this
object: the bridge is a **higher-order lift — a pair-of-pairs** that
compares two local readings of the carrier (differential/common vs
normalized divider/resource); not merely another gate but a
**comparison-of-comparisons**. **[W]** (corpus-witnessed, App. A D-1.)

### 11.4 The two-readout instrument (witness for Lemma 3.2)

A galvanometer alone is ratio-blind in exactly the sense of Lemma 3.2: at
null it cannot tell B from N. A **differential pair under the bridge**
fixes this: the galvanometer reads bias; the **common-mode output reads
mass**. High common-mode at null = conflict (both arms strongly driven,
opposed); low common-mode = ignorance (both quiet). A two-readout
instrument recovers **both** carrier coordinates that the odds-line
collapse destroys — the full carrier, measured. Lemma 3.2's
impossibility, and its repair, both have hardware. **[W]**

**External grounding (recovered from corpus T1129/T1130, web-verified
there).** The corner-representation half of Theorem 5.4 and this section's
W-axis have published anchors: S₄ = V₄ ⋊ S₃ is standard (the normal
Klein four of double transpositions; quotient S₃); the **tetrahedron
algebra** g_⊠ ≅ sl₂ ⊗ A (arXiv math/0604218, Elduque / Hartwig–Terwilliger)
realizes the S₄ action as exactly *Klein-four automorphisms plus an S₃
action* — published Lie theory for the holomorph structure; and the
dimension-4 **Hodge star** gives Λ¹ ↔ Λ³ (the witness↔triangle duality)
with Λ² (dim 6) splitting 3 + 3 self-dual/anti-self-dual — the W-axis's
form-theoretic home. **[S]** Inherited residue: the binding of the tetrad
(source, sink, witness, apex) to the tetrahedron algebra's four sl₂-points
is cited in the corpus but not yet constructed.

### 11.5 Conflict as stored potential (dynamics for §1's regions)

In a static label system, B is just a label. In the circuit realization,
**conflict is the metastable loaded state**. Minimal witnessed model:
d(bias)/dt = drive·bias − bias³. Above critical drive, bias = 0 is an
**unstable** fixed point — high potential, poised, flipping to a rail
(±) under any perturbation: conflict = stored potential energy waiting to
resolve an either/or, with the flip as its release. Below critical drive,
bias = 0 is **stable** — ignorance, nothing poised. T/F are energy
flowing/dissipating to a rail. **[W]** (minimal model run in the source
record.) With reactive components (C, L), energy is stored rather than
dissipated and the system has a **lattice of fixed points; take the
least** (Knaster–Tarski) — the carrier's dynamics bottom out at the same
fixed-point theorem as the framework's operating principle. **[W]**
The exact reactive network, potential, and critical drive are design
parameters (folds into OB-1's contract). **[W]** as flagged-open.

### 11.6 The square reduces; the triangle doesn't (scope theorem)

Tracing actual resistance *values* (not law-forms) across network
embeddings exposed the boundary of the entire V₄ picture:

- Series/parallel-reducible networks are the V₄ square's territory — the
  **reducible half** of network space.
- The Wheatstone **crossbar R₅** behaves as the sign-object: **at
  balance it vanishes** from the terminal resistance entirely
  (R_terminal = (R₁+R₃)‖(R₂+R₄), R₅ absent — its marginal contribution
  is exactly 0); **off balance it obstructs** — the network becomes
  irreducible by series/parallel and requires the **Y-Δ (star-mesh)
  transform**, which has no series/parallel analog. The irreducible
  3-cycle (the triangle) is structure the square's vocabulary cannot
  represent. **[W]** (sympy-witnessed in the source record.)

The lesson, recorded as method: when a structure comes out *too* clean,
suspect it is the reducible fragment, and go looking for the irreducible
cycle it cannot see (Provenance P-4). The unsigned content of this logic
is a square; the signed content is a triangle. In circuit form:
**affine = bridge balanced = crossbar vanishes = reducible; non-affine =
unbalanced = genuine Y-Δ triangle.** **[W]** for the circuit statement;
the identification with the sign-cocycle computation is OB-5.

### 11.7 Prior electrical formalisms (lineage, classified)

Two earlier constructions in the source record realize this logic's
shape in circuit terms and are recorded as lineage, not as witnesses:

- **CHL-E.** NOT as reciprocal inversion (R = 1/G) — the §2 multiplicative
  negation as a component law; **contradiction as a high-resistance
  state** rather than an explosive one (paraconsistency from circuit
  topology); a **two-rail architecture** (the pins as rails) with
  **harmonic-mean AND and additive OR** — which is exactly the
  parallel/series pair of 11.1. Whether the architecture satisfies the
  paraconsistent axioms (Priest/Belnap literature) was flagged and never
  checked: OB-6. **[W]** as a recorded proposal; unverified as a logic.
- **G-Calculus.** A proposition's state as a six-signal vector:
  (q, r) evidence for/against — the carrier pair; (x₁, x₂)
  capacitive/inductive bias — the reactive predisposition of 11.5;
  (q̇, ṙ) momentum of belief/disbelief — dissonance as velocity. Three
  simultaneous equilibrium laws (op-amp, Wheatstone phase rotator,
  differential tension buffer); the fixed point is the settled state,
  qualified by remaining dissonance. The EL-Atlas carrier is the
  (q, r) plane of this system; the G-Calculus is a candidate *dynamics*
  over the EL-Atlas *statics*. **[W]** as a recorded system; the
  identification of its laws with §§4–6 is **[S]**.

### 11.8 Conservation and equivalence: Kirchhoff, Noether, Thévenin

**Kirchhoff.** The two laws are the dual spine of energy redistribution
over a closed network: KCL — current conservation at nodes; KVL —
voltage sum zero around loops. **[W]** (source record). The corpus
axiomatizes them as named formal axioms (OhmsLawName,
KirchhoffCurrentName, KirchhoffVoltageName in a Level4_Physics module,
App. A D-8), and grounds series composition in global charge
conservation with voltage division as a KVL consequence (D-12). The
atlas identifications, graded:

- **KCL ↔ per-pin bookkeeping.** Conservation at a node is the
  accumulation law of Definition 1.1 read as flow: increments in,
  total maintained, nothing leaks between pins (Law 1.3). **[S]**
- **KVL homogeneous ↔ the d∘d = 0 gate.** "Sum around a loop is zero"
  is exactly the closure condition Conjecture 8.3's harness gates on.
  **[S]**
- **KVL inhomogeneous (Faraday form) ↔ Conjecture 8.3.** A loop sum
  that is *not* zero equals the enclosed source — which is precisely
  "holonomy = enclosed contradiction" in circuit form. The conjecture
  is KVL-with-curl. **[S]** — this gives OB-3 a second, physical
  statement of its test.
- In the purely resistive (dissipative) regime, settlement is the
  unique Thomson minimum; reactive components replace it with the
  least-fixed-point lattice of 11.5. **[W]**

**Noether.** The corpus contains the schema applied to this material's
algebraic spine: D-10 derives a "Law of Conservation of Ontological
Content" from the symmetries of categorical duality, explicitly on the
symmetry → conservation analogy, traced along the Cayley–Dickson
property-degradation ladder (ordering, commutativity, associativity lost
stepwise; content conserved). **[W]** (corpus-witnessed). The
atlas-internal Noether-shaped fact is immediate and checkable:

> **Under the De Morgan involution (pin-swap), mass is conserved and
> bias is negated:** (E⁺, E⁻) ↦ (E⁻, E⁺) gives m ↦ m, b ↦ −b.
> The symmetry of §5 pairs with the invariant of §4 — and the
> galvanometer (11.3) reads exactly the coordinate the symmetry does
> *not* conserve, while the supply reads the one it does. **[S]**
> (one-line computation; stated here, not yet developed.)

Noether proper requires a *continuous* symmetry. The atlas has a
candidate: the exp/log transition makes translation in 𝔸 the same
one-parameter flow as scaling in 𝕄 — a continuous chart symmetry whose
conserved quantity is unidentified. Promoting the discrete pairing above
and the corpus's categorical analogy to an actual Noether statement for
the carrier is **OB-7**.

**Thévenin.** Stated under the charter: **no corpus document names
Thévenin or Norton.** The *move*, however, appears twice, unnamed:
D-1's fourth scalar shadow — "equivalent single-conductor collapse" —
is the Thévenin operation (replace a whole network, seen from a port,
by one equivalent element); and the Sys framework's **Star-Mesh
Transform** (D-13) generalizes it as a reversible level-move,
instantiating conservation across abstraction levels — the n-ary
extension of §11.6's Y-Δ. The atlas reading: **Thévenin equivalence is
a named external projection in the sense of Remark 3.5** — the port
abstraction of an evidence network. It is legal as an instrument
(summarize a subnetwork's contribution at a boundary) and forbidden as
semantics (the equivalent element erases the internal mass/bias
distribution, exactly the ratio-blindness of Lemma 3.2 applied to a
whole subnetwork). Norton/Thévenin source duality
(voltage-source-in-series ↔ current-source-in-parallel) is itself a
De Morgan-shaped swap, unverified here. **[C]** — OB-8.

### 11.9 The simulation stack: verification, tooling, application

The corpus organizes the "what is it for" layer in three tiers, each
with documents in hand (App. A, D-11, D-14–D-16):

- **Verification.** An empirical G-Calculus study implements the
  5D_State vector with G_AND/G_OR composition and an RK4 solver,
  demonstrating existence and uniqueness of equilibrium via the
  contraction property (trajectories from disparate initial conditions
  converge to the same fixed point) and a functorial equivalence to
  Hopfield networks (D-11). This is the empirical counterpart of
  11.5's fixed-point claims: the dynamics over the carrier are not
  only stated but simulated, with convergence witnessed numerically.
  **[W]** as corpus record; binding its 5D_State to this spec's
  carrier+reactive coordinates is unverified.
- **Tooling.** The XSPICE mixed-signal framework analysis (D-14) and
  the LTspice/B2 Spice comparative evaluation (D-15) supply the
  instrument bench. The mixed-signal frame is apt, not incidental: the
  carrier is mixed-signal by construction — continuous accumulation
  (analog pins) punctuated by discrete decisions (external collapses,
  Remark 3.5). A simulated instance of the EL-Atlas is a SPICE-class
  deliverable: pick an ℛ instance (§7), wire the bridge of 11.3–11.4,
  and the two-readout instrument is runnable. **[S]** as a proposed
  application path.
- **Application.** Recorded domains where the carrier-with-dynamics is
  deployed as an interpretation: System Pi — language as a physical
  system under conservation laws, modeled by impedance and circuit
  dynamics (D-16); hyperparameter self-regulation — cognitive-state
  modulation of learning dynamics through a bridge architecture, the
  RLC/optimizer identification (D-17); RCA — computation as
  restoration of equilibrium under conservation laws, "algebraic
  physics of meaning" (D-18); and the Sys framework's conductance
  hierarchy with Star-Mesh as the level-conserving Process (D-13).
  **[W]** as corpus records; each is an interpretation of the atlas,
  none yet a verified model of it.

