# f090_2 literature placement — deep-research provenance (two searches, 2026-06-23)

## Search 1 (factored form submitted): cusp delta-invariant
- mult=(c-1)(cp-p-1)/2 = δ(y^c=x^{p(c-1)}), the classical cusp delta-invariant (a-1)(b-1)/2.
  Refs: Greuel–Lossen–Shustin, *Introduction to Singularities and Deformations* (2007);
  arXiv:2311.15922 Ex. 2.7 (δ(y^a=x^b)=(a-1)(b-1)/2, semigroup ⟨a,b⟩).
- Milnor relation μ=2δ-r+1: Buchweitz–Greuel, *Inventiones* 58 (1980) 241–281, DOI 10.1007/BF01390254.
- VERDICT: the collapsed form matches a cusp δ by COINCIDENCE OF QUADRATICS; "c branches" reading REFUTED
  by the Milnor test; the Google-AI value δ(y²=x^p)=⌊(p-1)/2⌋+1 is FALSE (correct: (p-1)/2).
- Kerner–Némethi dual graph (arXiv:0805.4083): δ = Σ edge-weights of K_c — the simplex framing is a
  relabeling of this known construction, NOT novel mathematics.
- Khovanskii "Pascal relation" (Russ. Math. Surveys 52:6 (1997) 1251–1279): UNRELATED false lead (it is a
  Minkowski edge-balancing condition for Newton polygons, not binomial Pascal).

## Search 2 (DECOMPOSED form submitted — the corrected scope): spectral home, packaging novelty
- TRUE HOME is spectral/representation-theoretic, NOT singularity theory. The structured form
  mult = p·faces(c-1,1) − [φ(p)/2 + 1]·(faces(c-1,0)-1) is a cyclotomic-factor multiplicity of a graph
  cycle-space operator.
- Underlying NUMBER is computable by established methods: abelian Artin–Ihara L-function factorization
  (Stark–Terras covering theory; Terras, *Zeta Functions of Graphs*); character-block "equitable"
  decomposition (Barrett–Francis–Webb, LAA 513 (2017), DOI 10.1016/j.laa.2016.10.017; Francis–Smith–Webb,
  arXiv:1809.07186); vertices-minus-orbits redundancy (MacArthur–Sánchez-García, Phys. Rev. E 80, 026117
  (2009), arXiv:0904.3192 — "redundant multiplicity at least n−1", "vertices minus orbits").
- φ(p)/2 = conjugate-pairs of primitive roots = the standard reality involution (BFW Cor. 3.9 block-pairing
  B_j/B_{k-j}); +1 = trivial-character/frame mode. Both individually standard.
- NOVELTY FINDING: the STRUCTURED PACKAGING was NOT FOUND in any of six homes (equitable/isotypic;
  Bass-Hashimoto/Ihara zeta; simplicial f-vector spectral; cyclomatic/cycle-space; voltage/coverings;
  Frobenius-Schur counting). Specifically: (i) f-vector/simplex framing of the orbit pairwise term,
  (ii) the explicit [φ(p)/2+1]-per-spanning-join correction, (iii) the closed quadratic in orbit count c —
  these three do not co-occur anywhere located. The f-vector packaging of a spectral multiplicity is the
  strongest novelty claim (absent everywhere, incl. toric topology / simplicial Hodge).
- VERDICT: number computable (not new); structured PACKAGING plausibly novel as presentation+interpretation,
  NOT as a computability result. Publish around the dictionary + a general proof, not the value.
  Target: LAA or EJC. Pre-empt the cusp-δ coincidence explicitly.

## Caveats (the searches' own G8)
- "not found" is survey-based, not proof of non-existence; adjacent unindexed literatures (coding theory's
  cyclic-code idempotents, condensed-matter symmetric-network spectra) not exhaustively checked.
- Stark–Terras interior partially paywalled — small residual chance the φ(p)/2 packaging appears as a remark.
- gcd(c,p)=1 required for the cusp identification (holds for validated cases); char-0 for the Milnor relation.

## METHOD MECHANISMS (the structural detail, not just the names) — three routes, two compute, one contains

### M1 — Abelian Artin–Ihara L-function factorization (Stark–Terras covering theory)
MECHANISM: the c-fold p-cyclic action makes the operator's zeta/char-poly FACTOR over the p characters
χ of Z/p as a product of one-dimensional L-factors ∏_χ L(u,χ). The trivial character χ_0 gives the base
factor (the "+1 frame/trivial mode"); the (p-1) nontrivial characters pair as L(u,χ)·L(u,χ̄) (conjugates,
the φ(p)/2 reality pairing) into real factors. Φ_p multiplicity = the count carried by the nontrivial
L-factors over the c blocks = p·C(c,2) − [(p-1)/2 + 1]·(c-1). REF: Terras, *Zeta Functions of Graphs: A
Stroll through the Garden* (CUP 2010); Stark–Terras, *Adv. Math.* 1996/2000 covering series.

### M2 — Equitable / character-block decomposition (Barrett–Francis–Webb)
MECHANISM: block-diagonalize T into B_j = Σ_ℓ ω^{jℓ} M_ℓ over j=0..p-1 (ω = p-th root of unity). The
Φ_p-eigenspace lives in the nontrivial blocks j≠0; by BFW Cor. 3.9 the blocks pair B_j ≅ B_{p-j}
(conjugate, the SAME φ(p)/2 reality pairing), so the (p-1) sectors carry EQUAL kernel dim. VERIFIED
numerically: per-character kernel dims are all equal ([1,1], [2,2,2,2], …, exact Galois symmetry).
mult = nullity/(p-1) = the per-sector dim. REF: Barrett–Francis–Webb, *LAA* 513 (2017); Francis–Smith–Webb,
arXiv:1809.07186.

### M1 ≡ M2 (PROVABLE EQUIVALENCE, gated f090_2_methods)
Both equal (c-1)(cp-p-1)/2. They commute because both compute nullity/(p-1) with nullity split equally
over the (p-1) Galois-conjugate characters: M1 counts it via L-factors (p per simplex-edge minus per-join
trivial+reality defect), M2 via block kernels (equal per sector). The equivalence IS the identity
p·C(c,2) − [(p-1)/2+1](c-1) = (c-1)(cp-p-1)/2. The φ(p)/2 appears in BOTH as the conjugate pairing
(L-factor conjugates in M1; block pairing B_j/B_{p-j} in M2) — the reality involution is the SHARED
structure that makes the two routes the same.

### M3 — Orbit redundancy (MacArthur–Sánchez-García) — CONTAINS, does not compute
MECHANISM: count edge-orbits under the cyclic action; the "edges − orbits" redundancy deficit =
c(p-1)(cp-1)/2 (VERIFIED: within-block orbits c(p-1)/2 + cross-block orbits p·C(c,2)). This is the TOTAL
cyclic redundancy of the edge space — it CONTAINS the Φ_p eigenspace [nullity (c-1)(p-1)(cp-p-1)/2] plus
the non-Φ_p modes. gap = deficit − nullity = (p-1)(2cp-p-1)/2 ≥ 0, NOT constant. So M3 is a SUPERSET /
upper structure, not a third computation of mult. REF: MacArthur–Sánchez-García, *Phys. Rev. E* 80, 026117
(2009), arXiv:0904.3192 ("vertices minus orbits", "redundant multiplicity ≥ n−1").

### THE CORRESPONDENCE (corrected from "3 methods"): 2 compute + commute, 1 contains
- M1 (L-function) ≡ M2 (equitable blocks): provably equal, sharing the φ(p)/2 reality pairing as the
  structural reason they commute. This is a genuine COMMUTING DIAGRAM (two routes, one value).
- M3 (orbit redundancy) ⊇ the Φ_p part, with clean closed-form gap (p-1)(2cp-p-1)/2. It is the
  AMBIENT redundancy the Φ_p multiplicity sits inside — a containment, not an equivalence.
- The decomposition mult = p·C(c,2) − [φ(p)/2 + 1](c-1) is M1's native form; the base/fiber WitnessTower
  reading is the same expression's combinatorial skeleton; M2 is the spectral realization; M3 the ambient
  bound. FOUR readings of one object, related by explicit maps (the all-readings law, enacted).

## THE ROSETTA READING — invariant vs idiom across the four renderings (NOT re-narration to discount)
The four computation routes are four LANGUAGES for mult(p,c). The cross-language comparison IS the content
(per the all-readings law): what survives translation is structure; what differs is idiom. Holding them
side by side:
 - M1 (L-function): IDIOM = analytic factorization. SEES UNIQUELY the trivial character as a separate
   factor (the +1) and the conjugate L-pairs (the /2). HIDES the simplex geometry.
 - M2 (equitable blocks): IDIOM = linear-algebraic kernels. SEES UNIQUELY that the (p-1) sectors are EQUAL
   (Galois symmetry as a checkable matrix fact). HIDES why the count is C(c,2)-shaped.
 - WitnessTower base/fiber: IDIOM = simplicial skeleton. SEES UNIQUELY the f-vector geometry + the
   machine-checked base / p-weighted fiber split. HIDES the analytic/spectral content.
 - M3 (orbit redundancy): IDIOM = orbit/group-action counting. SEES UNIQUELY the AMBIENT space (mult as a
   subset of total redundancy with explicit complement). HIDES the Phi_p isolation.
THE TRANSLATION-INVARIANT: the φ(p)/2 reality pairing appears in EVERY rendering (conjugate L-factor pairs
in M1; block pairing B_j/B_{p-j} in M2; the (p-1)/2 weight in the fiber; conjugate eigenvalue pairs in M3's
ambient count). That φ(p)/2 is FORCED in all four is stronger evidence it is fundamental than its presence
in any single one — this is the Rosetta epistemics: the invariant is what no language can avoid expressing.
NOTE (process): "re-narrated in character-theoretic language" was the wrong frame — re-narration across
languages is not redundancy to discount; the comparison surfaces the invariant. Banked as LAW.
