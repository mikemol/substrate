# The Point-Cloud / Hodge-★ / Witness Structure — Formalization

**Status:** SymPy-exact (the rung *below* Agda). Every numbered statement below is discharged by an
exact symbolic or rational assertion that **can fail**, in one of three files in `jea/`:
`jea_strictify_gcalc.py` (G), `jea_strictify_kirchhoff.py` (K), `jea_strictify_rotation.py` (R).
Tallies on disk: G 25/25, K 9/9, R 11/11. **None of this is `--safe` Agda-mechanized** — that is the
standing open edge (§7) and the handoff to AI-Q (Ξ), who holds the checker.

This formalizes one object seen from several ends: the orbit-cloud's density evaporating toward the
∞,∞ corner, the witness as the kernel of an antisymmetric form, the Hodge ★ as the series/parallel
duality, and the mechanism — self-annihilation = rotation into the orthogonal V₂ — that ties them together
and reproduces the measured evaporation law. The whole structure sits **under the navigator relaxation**:
the g-calculus is its conductance model (electronics), confirmed from `el-atlas/tools/kirchhoff_nedge.py`.

---

## 0. The objects

- **Rung n.** The complete graph K_{n+1}. Its **cycle space** = ker(oriented incidence) has dimension
  C(n,2) (rung 2→dim 1, rung 3→dim 3, rung 4→dim 6, rung 5→dim 10).
- **The orbit cloud.** One generic test vector in cycle space, sent through all (n+1)! frames (vertex
  orderings, acting on cycle space by `Cpinv · P_edge · C`), gives (n+1)! images. The cloud's **cardinality
  is the combinatorial count** (verified: rung 4 → 120 distinct; rung 3 → 22-not-24 by a generic-vector
  near-degeneracy; rung 2 → collapses to 2). Generators: `jea_orbit_cloud_gen.py`, `jea_depop_gen.py`.
- **B, the antisymmetric form.** The cycle-space antisymmetric (exterior-algebra / Kirchhoff loop) form.
  In the electrical reading B is the loop-space structure dual to the incidence/Laplacian.
- **The g-calculus pair (n,d).** A G-value is the *class* of a formal-quotient pair (n,d), with class G = n/d.

---

## 1. The g-calculus is the conductance algebra (the engine, not a lens)

The g-calculus is the mathematical model **under the navigator relaxation**, and it is electronics —
confirmed from `kirchhoff_nedge.py`, not inferred: G_OR/G_AND are *derived special cases* of Kirchhoff
nodal analysis, exact only on series-parallel-reducible graphs; the full model is the graph-Laplacian solve;
"the stationary point of the dissipated-power functional (Thomson's principle); KCL is its stationarity condition."

**1.1** [G] `G_OR` = fraction addition: class(G_OR((n₁,d₁),(n₂,d₂))) = n₁/d₁ + n₂/d₂.
**1.2** [G] `G_NOT` = reciprocal/swap: class(G_NOT(n,d)) = d/n.
**1.3** [G] **Non-idempotence (the mass-growth shadow):** (n,d)⊕(n,d) = (2nd, d²), class = 2n/d.
  The pair *remembers the extruded magnitude* that the class G=n/d forgets. (Electrically: two equal
  resistors in parallel halve the resistance.)
**1.4** [G] DeMorgan exactness via the swap: class(G_NOT(G_AND(p,q))) = class(G_OR(G_NOT p, G_NOT q)).
**1.5** [K] **PARALLEL emerges** from the nodal solve: nodal(0=1, two edges) = g₁+g₂ = G_OR.
**1.6** [K] **SERIES emerges**: nodal(0–x–1) = g₁g₂/(g₁+g₂) = G_AND (harmonic).

So the g-calculus is the **series-parallel-reducible shadow** of the Kirchhoff nodal solve; G_OR/G_AND
are reductions of it, not primitives.

---

## 2. The navigator relaxation is Thomson minimization

**2.1** [K] **Thomson:** the dissipated-power functional P(v) = Σ_edges g·(Δv)² is stationary (dP/dv = 0)
  exactly at the nodal potential. (Checked: dP/dvₐ = 0 ⟹ vₐ = g₂V/(g₁+g₂).)
**2.2** [K] **KCL is the stationarity condition:** at that stationary point, net current = 0 at every
  internal node.

The navigator's `argmin over the knob polytope` (a live re-solve, no stored optimum; `jea_navigator.py`)
**is** this minimization. The navigator is therefore not applied-adjacent — it is the **T3 trace** of JEA
(the supervisor decision-WAL = the control-loop SPPF; see `jea_eval`), one of the kernel's three fused traces.

---

## 3. The witness is the kernel; parity forces it

**3.1** [K] The **witness = the loop space (KVL) = ker(incidence) = the cycle space**, orthogonal to the
  node/current directions (KCL): B·loop = 0 for every loop. (Rung 3: loop space is 3-dimensional.)
**3.2** [G] B is **exactly antisymmetric** (Bᵀ = −B) at every rung 2–5.
**3.3** [G] **The rank of B is even** at every rung (a theorem for antisymmetric forms over ℚ).
**3.4** [G] **Parity forces the witness:** odd cycle-dimension ⟹ ker(B) ≥ 1 (an even-rank form cannot fill
  an odd-dimensional space). Rungs 2, 3 (odd cyc-dim 1, 3) carry a 1-dimensional witness kernel; rungs 4, 5
  (even cyc-dim 6, 10) are full-rank, **no kernel**.
**3.5** [G] witness dim = cyc-dim − rank, exactly, at every rung.

This is the structural reason behind "parity V₂ orthogonal to the witness-tower tangent": the witness is
the kernel of the antisymmetric form, orthogonal to the representable (paired) image **by construction**,
and it *exists* precisely when the cycle-dimension is odd. It is a rung-3 (odd-cyc-dim) phenomenon, **not
universal** — the even rungs have no kernel. (rung 3 is "the clearest signature" for exactly this reason.)

---

## 4. The Hodge ★ is the series/parallel duality (forced, not posited)

The earlier abstract strictification (§G) checked ★ as a *constructed* involution (a diagonal in an
orthogonalised basis) — it satisfied ★²=id and fixed the witness axis (statements 4.1–4.2), but it was
*chosen*. The Kirchhoff grounding **forces** ★ from the model:

**4.1** [G] ★ is an involution (★² = id), exact, on the rep⊕witness split.
**4.2** [G] ★ fixes the witness axis.
**4.3** [K] **★ = G_NOT** — the series↔parallel / conductance↔resistance duality — is an involution by the
  swap: swap∘swap = id, **forced from the model, not posited.**
**4.4** [K] ★ swaps series↔parallel: class(G_NOT(parallel)) = the reciprocal/series form.
**4.5** [K] **The Wheatstone bridge-null is the kernel/witness condition:** at balance g₁g₄ = g₂g₃ the
  coupling edge carries no current. The bridge-null is the loop-kernel made electrical; it is precisely the
  condition under which the G_OR/G_AND (series-parallel) algebra is valid — i.e. where the witness/kernel
  is unpopulated.

So ★ is not a convenient matrix: it is the duality already present in the g-calculus (G_NOT), and the
witness-is-the-kernel statement is the bridge-balance condition.

---

## 5. center = ★ : the log-polar center is the witness pole

In the log-polar view of the evaporation (radius = log|image|, angle = direction in the representable
plane), the **center** (|image| → 0) is the locus where the representable component vanishes.

**5.1** [G] **CENTER = the witness line, exactly:** the solution of "representable projection = 0" is the
  1-dimensional kernel direction (rung 3: rep-projection=0 ⟺ {x:z, y:−z}, a multiple of the kernel).
**5.2** [G] The representable image is 2-dimensional and the witness ⟂ it (B·w = 0); rep ⊕ witness spans
  the cycle space (the split is exact, basis invertible).

**Reading.** "Point at the center and that is the ★" is rigorous in this precise sense: the center is the
**witness pole** — where representable magnitude → 0 and only the kernel (= the ★-dual = the open-circuit
G→0 limit) remains. ★ is the **radial fold** exchanging center (witness) and periphery (representable);
the center is **one end** of ★, not ★ itself. This matches the pre-existing Hodge figures
(`scratch/figures/hodge_tetrahedron_3d.py`: ★ as a fold of the tower, fold axis at the centre).

---

## 6. Why the cloud thins where it does: self-annihilation = rotation into V₂

This is the mechanism. The two readings — "density evaporates" and "witness is orthogonal" — are **one
cause**, forced by antisymmetry.

**6.1** [R] **Self-annihilation is the defining property, everywhere:** vᵀBv ≡ 0 for all v (because
  vᵀBv = (vᵀBv)ᵀ = vᵀBᵀv = −vᵀBv). It is not a special corner event — it is antisymmetry itself.
**6.2** [R] **Antisymmetry ⟹ pure rotation:** in the rep⊕witness orthonormal basis B is a clean 2×2
  rotation block (rung 3: [[0, 2√3],[−2√3, 0]]) with the witness axis exactly zeroed; exp(tB) restricted to
  the image is a planar rotation (RᵀR = I).
**6.3** [R] **Kernel fixed, image rotated within itself:** exp(tB)·w = w (witness V₂ fixed); the
  representable plane rotates within itself.
**6.4** [R] **Rotation-out reads as annihilation:** the in-plane (observed) magnitude of a vector tilted by
  angle φ toward the witness axis is cos(φ) → 0 as φ → π/2 (fully rotated into V₂).

**The equivalence:** self-annihilation (vᵀBv≡0) ⟺ B antisymmetric ⟺ B generates pure rotation. A cloud
point "thins out of the observed plane" because the rotation carries its representable component toward the
orthogonal witness V₂; from the observed plane that rotation-out **is** the vanishing. Self-annihilation and
rotation-into-orthogonal are the same fact, not a coincidence.

### The quantitative tie to the measured figures

**6.5** [R] With c = sin(φ) (corner c→1 is φ→π/2, content fully in V₂), the in-plane magnitude per paired
  direction is cos(φ) = √(1−c²), so the **paired-volume over `rank` directions is (√(1−c²))^rank =
  (1−c²)^(rank/2)** — *exactly the measured depopulation law.*
**6.6** [R] Concrete rungs match the measured logspace slopes: rank 2 → (1−c²)¹ (slope 1), rank 6 →
  (1−c²)³ (slope 3), rank 10 → (1−c²)⁵ (slope 5). (Measured slopes in `depopulation_logspace.png`:
  1.0000 / 3.0000 / 5.0000.)

So self-annihilation = rotation-out doesn't only hold structurally — it **reproduces the evaporation curve
quantitatively.** The mechanism and the measured figures are the same object. (Figures:
`depopulation_profile.png`, `depopulation_logspace.png`, `cloud_evaporation{,_logspace,_logpolar}.png`.)

---

## 7. What is open / not yet done (the honest ledger)

1. **center-is-★ is not composed into one check.** §5 gives center = witness-line (5.1) and §4 gives
   ★ = G_NOT (4.3); §6 supplies the *dynamical* reason (rotation completes into V₂ at the corner). But the
   single exact identity — "the G→0 open-circuit corner **is** the G_NOT-fixed witness locus" — tying the
   two halves into one computation is **not yet written.** This is the next strictification.
2. **bridge-null = kernel is shown on the specific Wheatstone bridge** (4.5); the general statement (every
   irreducible coupling's null is the loop-kernel) is the pattern, not yet the theorem.
3. **Everything here is SymPy-exact in AI-Π0's own encoding.** None is `--safe` Agda-checked. The encoding
   itself — the cycle-space form B, the rep⊕witness split, ★ = G_NOT — is the shared assumption no
   strictification pass could question (the retrospective's G8 cross-pass blind spot). **Handoff to AI-Q (Ξ),
   who holds the checker** = the forward path `MECHANIZE-STAR` (P13 in the cotype): mechanize center-is-★
   into Agda over the now-landed linearity carrier (FreeLinearizationR/F2Bridge/multilinear — the algebra-end
   of this same arc). center-is-★ is **proved-but-unmechanized**: proved on the g-calculus/graph side, never
   given a green `--safe` witness, so it *looks* open from inside Agda when it isn't.

---

## 8. Provenance (the dependency arrow, corrected twice this arc)

The g-calculus is **upstream engine**, not downstream lens. The dependency runs:
g-calculus (conductance algebra, from electronics; the navigator-relaxation model)
→ the evaporation graphs are that relaxation's geometry seen
→ the linearity extension (FreeLinearizationR/F2Bridge/multilinear, AI-Q's work) was landed *because* the
  g-calculus reading demanded it.

So the linearity track and the witness/★/evaporation track are **the same arc seen from two ends**, not
adjacent. center-is-★ was proved before on the g-calculus/graph side; the SymPy strictification here is the
rung between that proof and the Agda mechanization. In JEA's three-trace decomposition (T1 eval-SPPF / T2
EEA-residue / T3 decision-WAL) this whole structure is **T3** — the navigator's relaxation geometry — a face
of the device-resident fused intern-eval kernel, not a side-arc.
