---
name: project_wedge_pentagon_sphere
description: "the foundational roots are now wedge-founded (DivStr) and the cross-carrier tensor's full Mac Lane coherence (pentagon + triangle) is proven — the geodesic sphere / foundational quotient algebra"
metadata:
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

The "fluidity" reframe and its landing (2026-06-04). The rank-4 shred
(rank4_shred.py) showed the realizable peak is an OPEN DAG: roots reference
each other one-way, no structural fluidity. My first read ("add ≃ bridges
manually") was WRONG — the user corrected: **the wedge CONSTRUCTS bridges; the
real question is why the bottom of the pyramid isn't built on the wedge
basis.** Answer: the roots (F₂, Fin, ℤ, Word, V₄) predate the wedge and were
never re-founded as `DivStr`; only `ℕ-div` existed (a retrofit). So the wedge's
bridge machinery had no wedge-carriers at the bottom to operate on.

LANDED (commits 0a18e2d, 476a82e on branch session/memory-arch-and-policy):
- `Algebra/F2/Wedge.agda` — `F₂-div` (recon q b r = scale q b + r, z = 𝟘).
- `Algebra/Z/Wedge.agda` — `ℤ-div` (recon q b r = (+ q) ·ℤ b + r), reusing the
  EEA→Bézout ℤ arithmetic. Three genuine roots now: ℕ-div, F₂-div, ℤ-div.
- `Algebra/Wedge/Monoidal.agda` — the cross-carrier tensor `_⊗ᴰ_`'s FULL Mac
  Lane coherence: associator (assoc→/←/assocᴰ), bifunctor on bridges/isos
  (_⊗ᵇ_/_⊗ᵢ_), the **PENTAGON** (§4), and the **TRIANGLE** + unit ⊤-div +
  unitors (§6). Every coherence diagram closes by **refl** because the carrier
  `Σ` and `⊤` are eta-records, so both composite paths reduce to the same
  projection tree. `roots-pentagon` grounds the pentagon at (F₂,ℕ,ℤ,F₂).

THIS IS the "geodesic sphere / foundational quotient algebra" the user named:
roots = vertices, EEA folds (eea-fold/gcd-fold/bezout-ℤ, already landed) =
operations, pentagon+triangle = the coherence that closes the open tree into a
coherent monoidal groupoid. Once the sphere is closed you transport along it —
no retrofits, no re-deriving bridges.

KEY TECHNIQUE: coherence-by-refl. State coherence at the forward bridges'
`translate` (morphism = action), NOT as full WedgeIso equality (which would
need proof-irrelevance of round-trip fields, unavailable --without-K). With
eta carriers, the proof is literally `refl`.

LANDED SINCE (commits 4c2625f, b06f4d6):
- `Algebra/Wedge/ParityBridge.agda` — `parity-bridge : Bridge ℕ-div F₂-div`,
  the FIRST actual cross-root edge (mod-2 ring hom: parity-+ / parity-scale
  assemble respects); `parity-transport-trace` carries gcd/Bézout/mod from ℕ
  onto F₂ via transport-trace. The literal "wedge constructs the bridge" demo.
- `Algebra/List/Wedge.agda` — `List-div A` (recon q b r = (q copies of b)++r,
  z = []): the FREE MONOID as a root, the wedge's NATIVE carrier (recon = the
  wedge's defining phrase, definitionally). Fourth root. parametric in A.

LANDED SINCE (commits 7f3d1d8, 1b23462): naturality of α/λ/ρ (Monoidal §7,
assoc-nat/unitˡ-nat/unitʳ-nat, all refl) → genuine monoidal structure (natural
isos + coherence), not just isos. `Algebra/Wedge/InclusionBridge.agda` —
include-ℕℤ : Bridge ℕ-div ℤ-div (the +_ coercion; respects is refl because
ℤ's pos+pos/pos*pos are definitional); transports ℕ traces into ℤ. Registry
consolidated: 6 objects (roots+unit), morphisms = GROUPOID of WedgeIsos (now
with unitᴸ/unitᴿ/assocᴰ as non-identity isos), bridges = CATEGORY of cross-root
homs (parity, inclusion), forget-iso embeds groupoid→category.

KEY FINDING (the bridge_graph_shred + "identity = everything exchanging via
the root" reframe): the top-down shred's edges are TWO KINDS, and only one is
bridge-realizable — corresponding to the wedge's TWO ℕ-roles:
- ARITHMETIC edges (ℕ as CARRIER/divisor): ℤ→ℕ (inclusion), F₂→ℕ (parity=mod2),
  Fin→ℕ (mod n). The dependency is a quotient/HOMOMORPHISM → realizes as a
  Bridge. Fin is the elegant case: its index n IS its modulus.
- INDEXING edges (ℕ as QUOT/Peano-shadow): Vec n, Linear n m. The dependency is
  a DIMENSION/length — no hom, so NOT bridgeable. These are GRADED/FIBERED over
  ℕ, not bridged through it. (Linear has no add/zero on maps either.)
So "everything exchanging via the root ℕ" splits: arithmetic roots bridge to
ℕ-as-carrier; indexed families are graded by ℕ-as-Quot. Don't try to force
indexing edges into Bridges.

TOOLS: scripts/bridge_graph_shred.py = value-layer companion to rank4_shred;
overlays bridges on the shred (REALIZED/RIGID/UNFOUNDED/EXTRA). Top-down shred
is UNCHANGED by all this (it reads type-defs; wedge fluidity is value-level) —
that's the proof fluidity lives in the bridge layer, not the skeleton.

DOUBLE-CATEGORY + TWIST ARC (commits 0944f43, 2db42fa, 22a8c44; + e4c69ba
bilinear-from-images). The wedge's two categories — Bridge (objects DivStr,
between carriers) and Wedge (objects elements, within a carrier) — are NOT
duals/opposites; they're a DOUBLE CATEGORY (both fiber over each other). KEY
WALL + RESOLUTION: packaging as CategoryOf needs ≡ on Bridge/Wedge RECORDS,
blocked under --without-K by the proof fields (respects/z-pres/wedge-eq) — UIP.
Resolution (the recurring descent-to-shared-structure): build it over the
carrier-neutral SHAPE (List ℕ, DECIDABLE ≡ → no UIP wall). shape-transport
(Shape/Transport.agda): bridges preserve shape (transport copies every quot)
→ both bridges AND correspondences (Corresponds = shape-equality) are
shape-preserving = two arrow-species over the shape base. Shape/Double.agda:
Corr groupoid (vertical) + bridges (horizontal) + square (the genuine 2-cell,
independent top/bottom bridges via the CROSS-carrier correspondence — the
within-carrier wedge is the degenerate single-bridge diagonal). Shape/Twist.agda:
companion (forward=TRACE) / conjoint (backward=BÉZOUT), twist = corr-sym
(companion)≡conjoint (the vertical involution); Bézout IS the conjoint, trace
IS the companion; Möbius seam = iso/identity diagonal. LANDED = data layers
(structure + key cell + twist), all green 0-postulate; coherence layer
(interchange, groupoid laws, equipment triangle identities) inheritable from
trans/sym/cong on List ℕ, NOT yet written (scope marked in docstrings — don't
overclaim "full double category/equipment proven"). DISCIPLINE NOTE: I twice
over-agreed ("double category" / within-carrier setup) before auditing —
caught via the agreement-without-yielding check; the symmetric truth needed the
cross-carrier (shape-level) correspondence.

INTERNED-HEAP CLOSURE (commits 84f7a87, f124f27, 1264cdd). Shape/Register.agda:
the type-theory-native von Neumann heap — Register = List WedgeShape (heap),
_∈ᴿ_/idx (membership = address), idx-inj (SOUNDNESS ⟸: equal address⟹equal
shape), _≟ˢ_ (decidable shape eq = the CMP loop), find/intern (hash-cons:
reuse address or append; dedup whole shapes). Shape/Register/Properties.agda:
NoDupᴿ + idx-cong (⟹: equal shape⟹equal address; proved with DISTINCT params
x,y + equality — same-param double-match is a UIP-shape --without-K refuses,
same trick as idx-inj) + intern-NoDupᴿ (intern preserves faithfulness).
Shape/Double/Interned.agda: THE CLOSURE — corr→addr/addr→corr: a correspondence
IS address-equality (interior shape-eq = exterior idx-eq), idx-inj/idx-cong the
seam. So the double category + twist + SPPF heap are ONE object; correspondence
= "same address," O(1) compare, intern-faithful forever. value-eq=spec,
index-eq=impl, the proof=the refinement. NAMING: _∈ᴿ_/NoDupᴿ register-specific
to avoid manufacturing collisions with WitnessTower's _∈_/NoDup (gates caught
it; the rule is don't fight EXISTING collisions, don't MAKE new ones).
SUFFIX-DAG = THE EEA TRACE (commit 09c4e81). The "well-founded decode measure"
the suffix-DAG seemed to need IS r<b, discharged when compute-trace built the
trace. Trace's `rec` is the tail-pointer, `shape` the structural decode
(terminating free), inductiveness = acyclic free = r<b banked. intern-trace
(Shape/Register/FromTrace.agda) interns every suffix bottom-up via the trace's
structural recursion — no Fin, no flat array, no measure; Agda's termination
checker accepts it silently. TWO-WEDGE SYMMETRY COMPLETE: loose wedge (no r<b)
= COMPOSE side = the double category/twist; wall=UIP, resolved by descending to
shape. Certified wedge (r<b) = ORBIT side = trace/suffix-DAG/interned heap;
wall=termination, resolved by r<b (=inductiveness). Loose composes (closed
under wedge-∘), certified terminates (orbits to z); the double category INDEXES
OVER the trace-heap. r<b — the field distinguishing the two Wedge shapes at the
very start — is the measure that makes the whole heap wall-free. Every
wall-bearing item in the arc is now resolved.
STILL OPEN (no walls, optional): And earlier-parked: ℤ↠F₂ triangle; V₄-div
(arithmetic-vs-indexing first); the coend/bilinear-SPPF over Category/
SymmetricMonoidal.agda instantiated at both F₂-Vect and wedge ⊗ᴰ.
Connects [[project_center_free_universal_property]] (the tensor's
unit/coherence over the Free⊣Forgetful center; List-div = free construction as
root), [[project_type_audit_sppf]] (the shred that diagnosed the open DAG).
