# The Commuting Sphere

Re-walk of the argument as a coherent structure: every resolved either/or is a
**commuting cell** (so we don't re-litigate); every open conjecture is a tracked
**boundary cell** (so it is never lost). The precise failure mode this artifact
exists to prevent is **losing track of the conjecture** across context loss.

Durable companions: `memory/project_commuting_sphere.md` (survives flush),
`agda/Substrate/Algebra/Wedge/Sphere.agda` (in-code index next to the proofs),
and `memory/project_wedge_pentagon_sphere.md` (the proven arc, not duplicated).

The end goal this sphere is the spec for: a **VM = the graded semiring-tensor
double category, with the wedge as constructive boundary operator, that provably
maps onto compute-fabric (GPU SM/cache/HBM) boundaries.** "Realize the GF(2)
model" = construct the spec↔impl refinement (Agda structure = spec/value; GF(2)
bit-layout = impl/address; the refinement proof = the seam — the same shape as
the interned register's `value-eq ⟺ index-eq` via `idx-inj`), with GF(2) as the
*carrier/compute* gauge (not "GF(2) everywhere").

---

## A. The arc (proven cells — durable in Agda)

| stage | module | headline |
|---|---|---|
| wedge core | `Algebra/Wedge.agda` | `DivStr`, `Wedge` (q,r,witness), the three reads, `Trace`, `ℕ-div` |
| free term | `Algebra/Nat/GCD/EEATrace.agda` + `Wedge/Shape.agda` | the Euclidean trace; `shape : Trace → List ℕ` (carrier-free spine) |
| double category | `Wedge/Shape/Double.agda` | `Corr` (= shape-equality) groupoid + `square` (the 2-cell) |
| twist | `Wedge/Shape/Twist.agda` | `companion`/`conjoint` = trace/Bézout; `twist` = the involution |
| interned heap | `Wedge/Shape/Register{,/Properties,/FromTrace}.agda` | `idx-inj` (sound), `intern`, `NoDupᴿ`, `idx-cong`, `intern-trace` |
| monoidal sphere | `Wedge/Monoidal.agda` | pentagon, triangle, naturality, braiding σ, hexagon (all `refl`) |
| roots + bridges | `Wedge/Registry.agda` | ℕ/F₂/ℤ/List/⊤ roots; parity, inclusion, modn bridges |
| GF(2) carrier | `F2/Linear/{FromImages,BilinearFromImages}.agda` | `linear-from-images`, `bilinear-from-images` (the genuine GF(2) layer) |

Everything *above* this line in ambition (semiring-VM, graded-GF(2),
Cayley-Dickson, tropical placement) is **conjecture** — see §C.

---

## B. Resolved forks (commuting cells — common substructure, don't re-litigate)

| either / or | common substructure (the filler) |
|---|---|
| build vs name | **the universal property** (a free construction *is* its UP) |
| objects: elements vs DivStr | **the carrier-neutral shape** (`Shape`); both are fills over a shape |
| twist: divisor- vs residue-contravariant | **the braiding σ** (`Monoidal §8`); the two are its directions |
| fibration vs "both fibered over each other" | **the double category** (`Shape/Double`); both fiberings = its two slicings |
| Bool vs GF(2) for the heap | **semiring gauge** (same tensor, different semiring); "GF(2) cancels derivations" is true **only ungraded** — see C2 |
| Morton vs Hilbert | **linearization gauge**; crossover *at the grade boundary* (C3/C8) |
| loose vs certified (`r<b`) wedge | **compose-side vs orbit-side**: loose composes (closed under `wedge-∘`), certified terminates (the `r<b` orbit); the double category indexes over the trace-heap |
| one-way gauge hierarchy vs recursive | **a fixpoint**: gauges form a double category one level up — cost (tropical) measures grade, grade picks curve, curve sets cost |

---

## C. The conjecture ledger (THE PART THAT MUST NOT BE LOST)

Each: **statement** · status · prove-or-correct path · substrate home.

1. **`r<b`-residue = adjoint correction** *(KEYSTONE).* The certified wedge
   residue *is* the precise Free⊣Forgetful adjoint comparison map; so a
   "refutation" (r ≠ 0) hands back exactly the structure to adjoin. ⟹ the
   metaphor→proof engine is **prove-or-correct**, never dead-ends. · *conjecture*
   · prove: `a = recon q b r` is the adjunction triangle (the center); show the
   certified (sharp) residue equals the adjoint comparison. · home: `Algebra/
   Wedge.agda` + `Category/FreeUniversalProperty`. **Build this first.**

2. **graded-GF(2) is non-cancelling.** `x ⊕ x = 0` only bites when distinct
   derivations are summed into one coordinate (ungraded projection-with-collision).
   With the F₂ⁿ-graded topology they live in distinct components → XOR =
   symmetric difference, no cancellation. (Corrects my flat-GF(2) objection.) ·
   *conjecture* · prove: a grading on the carrier such that distinct-degree
   derivations are separated; cancellation ⟺ same-degree collision = the parity
   invariant you want. · home: new graded-GF(2) carrier; relates
   `Category/GradedMonoid.agda`.

3. **Morton ≅ Cayley-Dickson via the cocycle.** A Cayley-Dickson algebra is an
   F₂ⁿ-graded twisted group algebra: `e_i·e_j = ±e_{i⊕j}`, sign = a 2-cocycle.
   Morton = untwisted (trivial cocycle, commutative); Hilbert = twisted
   (rotation = nontrivial cocycle). The CD ladder's graded loss (ℂ comm → ℍ
   non-comm → 𝕆 non-assoc) = the commute-edge grade climbing. · *conjecture* ·
   prove: identify the cocycle of Morton/Hilbert with the CD level. · home:
   **Cayley-Dickson NOT in substrate — must build**; `Substrate/Cocycle.agda`
   partial; `Category/GradedMonoid.agda` exists.

4. **The two gradings coincide (or don't).** ANF/Zhegalkin degree (`OR = XOR ⊕
   AND`, graded by polynomial degree) vs F₂ⁿ-index grading (Morton/CD). Do the
   commute-breaking grade, the ANF degree, and the CD level align? · *conjecture*
   (open: may be three distinct gradings that align, or one) · home: new.

5. **nilpotent-not-annihilating ⟹ no dead-end.** Residues are nilpotent (graded
   correction), never annihilating; so "kill" cannot happen — the negation is a
   *construction* (intuitionistic; deformation tracked, not discarded). Ties to
   C1: the engine has no death branch, only a residue branch, and a residue is a
   repair. · *design principle, partly built* (`CrossMul` coherence = cross-term
   nilpotency degree). · home: `Wedge/CrossMul.agda` + C1.

6. **The semiring VM places itself via tropical.** One tensor (the shape-DAG /
   transition), contracted over a chosen **semiring** = the gauge that picks the
   job: Bool (∨,∧)=routing, GF(2) (⊕,∧)=linear carrier, ℕ=counting, **tropical
   (min,+)=cost/placement**. The *same* double category over (min,+) computes
   the critical path ⟹ the **verified** fabric placement (not a heuristic). The
   square (interchange) = the legal-fusion proof. (GraphBLAS-grounded.) ·
   *conjecture* · home: `Algebra/Semiring.agda` **exists but never instantiated**
   — making it the engine's parameter is the move that *measures* it; **tropical
   NOT built**.

7. **Wedge = constructive boundary operator.** Partial commutativity ⟹ a
   structural partition between "commutes / doesn't" within one domain; the wedge
   *traces its edge*: `a = q·b + r`, q·b = reduces, r = residue. Sharp via `r<b`
   (canonical, unforgeable — vs loose = up-to-gauge), graded by the residue's
   nilpotency degree (distance past the edge), recursive via the orbit (the shape
   = the edge-record at every scale). · *wedge/trace/shape built; the
   "edge = grade = cocycle" identification is the conjecture.* (User's typo fix:
   the partition is **commute**/doesn't, not compute.) · home: `Wedge` + §C3.

8. **Curry-Howard VM.** The bivalent SPPF juggles three DOF — **composition**
   (associative/sequence/time), **grouping** (commutative/parallel/space),
   **growth** (recursion/the orbit) — and = proof = program = execution trace =
   layout. Morton = the binary-tree descent order, valid *while access commutes*;
   Hilbert = the ordered packing decision; the curve crossover is *at the grade
   boundary* (where commutativity breaks), chosen by the tropical/cost instance.
   Recursive fixpoint: top entailed by bottom (the algebra's grades place the
   curves), bottom constrained by top (the fabric's block budget bounds the
   affordable grades). · *framing/conjecture* · home: the VM (downstream).

---

## D. Keystone first brick (the build AFTER this sphere)

Prove **C1: `r<b`-residue = adjoint correction.** Smallest cell that makes the
engine prove-or-correct; gates everything else. Then **C6: make `Semiring` a
real parameter** of the wedge/tensor engine — the single move that measures the
dormant `Semiring` and unifies Bool / GF(2) / tropical as instances rather than
three builds. Curve/Cayley-Dickson (C3) and graded-GF(2) (C2) hang off those.

---

## Completeness check (the sphere catches every point of disagreement)

Every either/or in the arc has a cell in §B; every metaphor/conjecture has a
cell in §C with a prove-or-correct path AND a substrate home (built / partial /
must-build). **Durability test:** a cold read of this file + the memory must
reconstruct the 8 conjectures, the keystone, and the next builds. If a cold read
loses a conjecture, the sphere failed.
