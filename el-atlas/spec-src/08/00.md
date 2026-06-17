## 8. The amplitude reading: norm, phase, curvature, holonomy

The geometric/sheaf-theoretic reading of the carrier, for use as a
coefficient system on graphs and complexes.

**Definition 8.1 (the coefficient object).** The carrier is read as a
**two-component, non-normalized, amplitude-valued coefficient**: the
components are E⁺ and E⁻ (equivalently t, f), kept separate, never
divided into a disposition. The coefficient is *not* a probability — there
is no normalization, ever (Law 3.1). **[W]**

**Definition 8.2 (the dictionary).** On the crossbar of §4:

- **Modal grading / filtration** = total norm **m = t + f**. Not a
  probability: one never divides by it.
- **Connection / phase** = the relative balance of the two unreconciled
  components, carried on the bias axis **b = t − f** — *relative phase
  between two amplitudes that remain uncollapsed*, not a log-odds
  (Law 4.2).
- **Curvature** = contradiction degree, peaking where *both* components
  are large — the interference-dominated region. A collapsed (odds)
  representation must report that region as flat (ratio ≈ 1); the
  amplitude reading reports it as maximally curved. This is the whole
  difference between a geometry that can carry holonomy and one that
  cannot.

**[W]**

**Conjecture 8.3 (holonomy = enclosed contradiction).** On a complex
carrying this coefficient system — connection the net-truth phase,
curvature the contradiction degree, filtration m — the holonomy
accumulated around a loop equals the contradiction it encloses.
**[C]** Proposed test (from the source record, never run): build the
enriched complex with coefficients in the two-term log-semiring and check
"holonomy = enclosed contradiction" under the same d∘d = 0 gate and
vacuity discipline as the existing harness. Obligation OB-3.

**Remark 8.4 (the discipline, stated once).** The same forbidden move
recurs at every level: don't collapse the fiber, don't normalize the
amplitude, don't take the odds. Keep the components live until something
*forces* collapse — and the obstruction to ever being forced is the
holonomy. **[W]**

---

### 8.5 The phase socket — what OB-2/OB-3/OB-9 jointly are (V₄-valued)

OB-2 (phase composition), OB-3 (holonomy = contradiction), and OB-9 (phase
origin) are **one hole, three gradings**, not three obligations. The hole is
characterized here by its boundary conditions (what the rest of the spec forces
about anything filling it), and its value group is then forced. This is the
*characterization*, not the fill; the fill is parked (user-direction pending).

**The socket (six boundary conditions, each from a committed part):**

- **C1 — lives on edges, not nodes.** The carrier at rest is 2-dimensional
  (mass, bias) and §8 fixes the coefficient as the unnormalized *pair*; phase is
  therefore not a third axis on a value at rest but a structure on *comparisons
  between* values — a connection.
- **C2 — typed as a connection.** §8's dictionary already types it: relative
  phase = connection (1-cochain), curvature = contradiction (2-cochain),
  holonomy = enclosed contradiction. The d∘d=0 object of OB-3.
- **C3 — partly occupied.** The OB-3 run witnessed **bias-holonomy** (net bias
  around an unfilled loop, H¹=1). Anything filling the socket must restrict to
  bias-holonomy as its abelian/real shadow on the bias axis.
- **C4 — non-flat (corrected).** The Noether charges (squeeze/dilation) live in
  (ℝ,+)², which is flat; the socket needs *nonzero curvature* for nonzero
  holonomy. (An earlier draft wrote "non-abelian"; that was an error — flat means
  zero *curvature*, not abelian *group*. An abelian group carries nonzero
  holonomy: the Z₂ orientation/Möbius sign is the prototype. The real requirement
  is two **independent involutions**, see the value group.)
- **C5 — not a complexified value.** Caveat 2.4a forbids the field route: phase is
  not arg() of a complexified semiring. It comes from composition structure, not
  from enriching a value at rest.
- **C6 — sourced from overlay non-commutativity.** The overlay (§13.2) is
  composition; transport around a loop composes overlays; **phase is the failure
  of overlays to commute around the loop.** This meets C1 (edges), C2
  (connection), C5 (composition not field), and supplies the curvature C4 needs.

**The value group is forced to be V₄.** The connection must independently record,
around a loop, **two** order-2 bits: (i) the bias-sign flip (the witnessed
bias-holonomy, one Z₂) and (ii) which of the two **distinct** involutions —
negate-a-pin vs pin-swap, kept distinct by Theorem 5.3 — was transported (a
second, independent Z₂). Two required independent order-2 generators is exactly
**Z₂ × Z₂ = V₄**. Smaller groups each fail a named condition: the trivial group
kills holonomy (C2/C3); Z₂ has one bit and conflates De Morgan with bias-flip
(kills Theorem 5.3); Z₃ has no order-2 element and cannot hold even one involution.
V₄ is therefore **forced, not merely minimal** — and it is V₄ (all non-identity
elements order 2), not Z₄. The d∘d=0 gate closes identically with V₄ = (Z₂)²
coefficients, since the cochain complex is then over GF(2) — the *same* ground
field as the Reed–Muller / Walsh structure of §13.1 (the coding substrate and the
phase structure share GF(2); likely not a coincidence). **[W]** for the socket
characterization and the forcing of V₄; **[C]** for any specific fill.

### 8.6 Phase as a dependent type — the V4 interface and its pinnings

The apparent remaining hole ("which loops realize a nonzero class, by evidence")
is an artifact of one framing. It dissolves the same way "unreachable" did: refuse
the either/or, find the common structure. Here the either/or is **carrier vs
action** — does the system *carry* a V4 action (evidence picks each edge's
transport; holonomy is a measurement you survey) or *is* it a V4-torsor (topology
fixes the transport; holonomy = H1(complex; V4), a theorem)? The resolution is
neither: the system is a **dependent type with a fixed V4 interface**, and carrier
and action are two **pinnings** of that interface to a model.

**The interface (fixed; the invariant).**
```
V4Interface:
  transport  : Edge -> V4        -- every edge carries a group element
  holonomy   : Loop -> V4        -- = sum of edge transports
  biasShadow : V4 -> Z2          -- projects to the witnessed bias-holonomy (C3)
Phase : (pin : V4Interface |- Model) -> Type
```
The V4 structure (§5, §8.5) is invariant; what varies per model is the **witness**
supplying `transport` — the pinning.

**The two pinnings (both retained, neither lost).**

- **Carrier pinning (A):** `transport(e) := classify(evidence_at(e))`. Evidence
  picks the V4 element per edge; holonomy *responds to data* — you can ask what the
  evidence does around a loop. Holonomy is a **measurement**.
- **Action pinning (B):** `transport(e) :=` the structural V4 element (torsor);
  topology fixes the elements; holonomy = H1(complex; V4), **determined**, no
  survey. Holonomy is a **theorem**.

**The rich carrier holds both at once.** Because both pinnings implement the *same*
interface, both witnesses can sit on one complex; their **V4-difference is itself a
1-cochain** — the *evidence-relative-to-structure* field. So the carrier holds
three things simultaneously: structural holonomy (what topology forces, B),
evidential holonomy (what the data shows, A), and their difference (where data
departs from structure). The pinning chooses which is read as *primary*; the type
holds all three. Nothing is lost in either direction. **[W]** (worked on a triangle:
B-holonomy and A-holonomy distinct, difference = the data's departure, all three
V4-valued and simultaneously present.)

**C3 holds in both pinnings** because `biasShadow` is in the *interface*, not a
witness — the bias-holonomy is recoverable however you pin.

**Status change.** Phase is therefore **resolved as a type**, not parked: it is a
group-action-carrier with a fixed V4 interface and a pinning-dependent realization.
The pinning is a declared *model parameter* (upstream, like R in OB-1), not a hole
in the logic. The typethy layer is correspondingly re-typed from "open domain-hole"
to **a dependent type, pinning-parametric** — derived once a model supplies its
pinning, exactly as the DAG made the coverage cells derived-by-construction.
OB-2/OB-3/OB-9 consolidate and move from *open* to *resolved-as-type* (the remaining
freedom is the pinning, a modeling choice, not an open obligation of the logic).
**[W]** for the type and the two-pinning structure; the *choice* of pinning per
application is model data, not a spec obligation.

**Addendum (draft 13) — the pinnings are the two representations, and phase
is the extension class.** Theorem 5.4 supplies the consistency check §8.6
predicted. The **action pinning (B)** is the corner/tetrahedron
representation: V₄ exact (the normal double-transpositions), frame
S₃ = Aut(V₄) permuting the three involutions, total symmetry of the
pinning space **S₄ = V₄ ⋊ S₃ = Hol(V₄)** — re-pinnings compose as S₃,
resolving the holomorph candidate (witnessed: image full S₃, kernel V₄).
The **carrier pinning (A)** is the pin-plane representation: only the
antipode-centralizer **D₄** is linearly realizable, i.e. V₄ braided by the
central twist [N,S] = −id; the phase bit of §8.5 is realized internally as
**the extension class of 1 → Z₂ → D₄ → V₄ → 1** — the two De Morgan
generators already fail to commute by exactly one reversible central sign
(Pauli X/Z anticommutation), so phase was never an external add-on: it is
what the carrier pinning *sees* of the structure the action pinning holds
exactly. The §8.6 difference-cochain between the pinnings is this class.
The axis-mixing S₃ frame is linearly invisible to the pin chart
(Theorem 5.4), which is why perspective shifts felt external to the
carrier: they are not in any single chart; they live on the corners. **[W]**

