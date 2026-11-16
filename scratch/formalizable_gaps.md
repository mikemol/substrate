# Formalizable cotype content NOT yet in Agda — full witness survey (Ⓝ arcs)

The paperkit ships EXECUTABLE WITNESSES (`proofs/`, `checks/`, `witnesses/`) — Python/sympy/numpy
ref-impls that ARE the Agda spec. Surveyed ALL 91 witnesses + 4 proofs (3 Explore passes, verified
against the substrate, 2026-06-25). The user is right: far more is witnessed than is formalized.
Witnesses at `scratch/cotype-ebnf-strictness/cotype-merged-adequate/`.

**Verification correction (the discipline fired):** my first guess "Agda has only c=2 multiplicity"
was WRONG — `PhiMultiplicity.mult2 p n`/`mult2-fibered` are general-c. The CLOSED FORMS are done.

## What IS proven (the foundation — don't rebuild)

- Φ_p multiplicity COUNT: `WitnessTower/PhiMultiplicity` (`mult2`/`nullity2`/`mult2-fibered`, general c) + `FaceCount` (the f-vector, `faces n k`).
- Single-p-cycle spectral dim: `Algebra/F2/Linear/SpectralCycleDim` (`dim ker Φ_p(σ_p)=p−1`), `SpectralTower`, `SpectralCRT`.
- GF(2)ⁿ "three hats": `Groups/F2Cubed` + `Wedge/Sphere` + `Linguistic/Interchange` — PROVEN (gf2_hinge).
- Cayley–Dickson cocycle/coboundary `d²=0`: `CayleyDickson/Cocycle`,`Coboundary`,`Grade` — PROVEN.
- [0,∞] conductance G-value algebra + L-space codec: `Logic/Evidence/GValueAsQ`,`GValueLSpace` — PROVEN (nedge).
- Conjugacy census: `WitnessTower/CycleType` (the partition λ, all classes).

## The ABSENT arcs (witnessed, formalizable, ranked by cleanness)

### Tier 1 — clean, reuse-heavy, small (start here)
- **Ⓝ.rsbpf-involution** — `Inv(F)=GF(2)^|Addr2(F)|` free+transitive torsor on SPPF swap-decorations. Witness `aspf_rsbpf_ref.py`. Generic torsor PROVEN (`Torsor.IsTorsorᴳ`+`F2Cubed`) ⟹ INSTANTIATE. Also a never-discard-residue instance (undecorated forest = lossy canon, σ = residue).
- **Ⓝ.mult-argument-L2** — cross-edge tensor: Φ_p acts as shift⊗shift on the p×p torus, eigenvalue ζ^k has multiplicity p via the bijection i↦k−i on ℤ/p. Witnesses `proofs/f090_2_argument.py` (L2), `probe_inv_construct.py`. ABSENT, a finite-bijection count — self-contained. (L1 degΦ_p=p−1 already = SpectralCycleDim.)
- **Ⓝ.or-semilattice** — OR on 2ⁿ assoc/comm/idem semilattice + pentagon (coherence cell-a). XOR cell DONE; OR side ABSENT (only `Grade.∨-anf` bridges). Witness `gf2_hinge_ref.py`.
- **Ⓝ.rsbpf-functor** — RSBPF binary-path-forest type + rank functor `R:RSBPF→(ℕ,max,0)` strict monoidal. Witness `aspf_rsbpf_ref.py`. Reuse `FreeMonoid`/`SPPF`/`SymmetricMonoidal`.
- **Ⓝ.span-unify** — the ONE span-DP recurrence `T[i,j]=⊕_k T[i,k]⊗T[k,j]` projected to four semirings (Catalan / CYK / APSP / ASPF) as a single theorem; + Catalan (strict-binary bracketings); + the `aspf_segment` single-junction monoid. Witnesses `span_dp_ref.py`,`aspf_segment_ref.py`. `SPPF` fold + `NatInf` tropical exist as scaffolding.

### Tier 2 — new but bounded machinery (foundational, reusable)
- **Ⓝ.homology** ⭐ — the k-FACE CHAIN COMPLEX: boundary `∂_k : C_k→C_{k−1}`, `ker(∂_k)`, the permutation rep projected onto homology, and the ARITY CLIMB (`v_p(disc)` of the projected action climbs with face-dimension: 2 dominates at k=1 edges, 3 at k=2 triangles — f085). Witnesses `probe_arity_homology.py`(⭐), `arity_climb`,`arity_kface`,`arity_baseline`,`simplex_faces`. `FaceCount` has the COUNTS but NO `∂_k`/homology. A reusable foundational win (chain complexes the substrate lacks entirely).
- **Ⓝ.composition** ⭐ — the BLOCK-COMPOSITION law: `charpoly(⊕blocks) = ∏(within-block) × (cross-factors)`; cross-factor = Φ_{mn} on odd-coprime block orders, NON-cyclotomic when a 2-block participates; the Mackey/induced-rep tensor. Witnesses `probe_composition_law.py`(⭐),`interaction_lattice`,`coprime_headtohead`,`inv_construct`. This is the MECHANISM behind general-c multiplicity (how blocks compose), absent though the count is proven.
- **Ⓝ.zerodiv** ⭐ — the ZERO-DIVISOR SPECIES tower: singular cycle-space actions (det=0) = annihilated directions; the orbit-cloud stabilizer/"reroute" (rung-3 degeneracy, clean ≥4); V₂ class splitting; nilpotency grading; 3-torsion (order-3) species; faithfulness-on-generators. Witnesses `probe_zerodiv_span`(⭐),`orbit_cloud`(⭐),`v2_study`,`degeneracy_type`,`sign_link`,`order3`,`faithful_generators`. Beyond `CycleType` census (which IS done). Ties the witness tower ↔ CayleyDickson zero-divisor=residue (Ⓒ.absent-sphere). Needs the cycle-space rep of S_{n+1} + stabilizers.

### Tier 3 — substantial new number theory (the genuinely-foreign frontier)
- **Ⓝ.galois** — cyclotomic-field / Galois / Frobenius / p-adic arithmetic of the NON-cyclotomic factors: ℚ(ζ_p) splitting, Dedekind–Kummer Frobenius cycle-types (factor mod p ⟹ cycle type ⟹ Galois class), `v_p(disc)` ramification, off-circle factors = Φ_m with φ(m)=p−1 (`inversion_clinch`), `T^ord≠I` deformation, tree-relative ramification. Witnesses `probe_inversion_clinch`,`frobenius_inventory`,`galois_generic`,`three_qzeta3`,`three_adic`,`inversion_width`,`tn_deformation`,`tree_deform`. Needs mod-p polynomial factorization + field extensions (mostly absent).
- **Ⓝ.weil** — the GRAPH-WEIL / IHARA–BASS ZETA layer: Bass `det(I−Au+Du²)`, functional equation `u↦1/(qu)`, reciprocal root pairing `λ↦c/λ`. Witnesses `probe_ihara_zeta`,`probe_weil_proxy`. The contrast doc flagged this as genuinely-new (NOT an instance of existing generics) — the deepest arc; needs graph adjacency/determinant machinery.

### Smaller / partial
- **Ⓝ.cocycle-mobius** — the divisor-poset Möbius incidence algebra (`Σ_{d|n}μ(d)=[n=1]`) as the number-theoretic cocycle reading of `aspf_cocycle_ref.py` (the CD-cocycle exists; the Möbius/zeta reading doesn't).
- **Ⓝ.paraconsistent-noexpl** — the no-explosion theorem (series `g_and ≤ min` ⟹ contradiction can't lift Q to truth); algebra is there (`GValueAsQ`), the logical consequence isn't. A `reject-lem-substrate` instance.
- **Ⓝ.nullity-general** — generalize `dim ker Φ_p(σ_p)` from the p-cycle shift to an arbitrary operator T (the nullity technique; PARTIAL — `SpectralCycleDim` is shift-only).

## Recommendation

Two honest framings:
1. **Cheapest wins first** (instantiate/extend what exists): `Ⓝ.rsbpf-involution` → `Ⓝ.mult-argument-L2` → `Ⓝ.or-semilattice`. Each is days, not weeks, and lands a concrete witness.
2. **Highest structural leverage**: `Ⓝ.homology` — the `∂_k` chain complex is foundational machinery the substrate lacks, and it UNLOCKS `Ⓝ.composition` and the arity-climb at once (and feeds `Ⓝ.zerodiv`). If the goal is to absorb the most witnessed math per unit of new foundation, the chain complex is the keystone.

Magnitude note (honest): Tiers 2–3 are a multi-arc research program — the probes encode the full spectral/number-theoretic depth of the f090_2 arc, of which Agda formalizes the count + single-cycle dim. `Ⓝ.weil`/`Ⓝ.galois` are genuinely-new mathematics, not generic-instantiations.
