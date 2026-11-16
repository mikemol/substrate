# Constellation decomposition — external groundings (proper nouns, theorems, citations)
# From the corpus-archaeology deep read. Each atom -> the established structure it instantiates.
# RENDERED as instance-of where solid, as change-of-frame analogy where loose (all-readings).

## ECHO / CONSTELLATION pipeline
- GALAXY (decay-weighted peer sum W_{v,k}=Σ α^{k-1}|N_k(v)|) = KATZ CENTRALITY / von Neumann diffusion /
  walk-proximity series Σ_k α^k A^k = (I-αA)^{-1}1. Katz, Psychometrika 18(1):39-43 (1953). INSTANCE-OF.
  Recursive neighbor-aggregate-then-relabel = 1-WL color refinement (Weisfeiler-Leman 1968).
- 1-WL CEILING = expressiveness bound. Xu-Hu-Leskovec-Jegelka "How Powerful are GNNs?" ICLR 2019
  (arXiv:1810.00826): GIN as powerful as 1-WL. Refinement complexity: Cardon-Crochemore TCS 19(1):85-98
  (1982) O(|A|log^2|V|); Paige-Tarjan SIAM JC 16(6):973-989 (1987). Engine inside nauty/bliss/saucy. INSTANCE-OF.
- ECLIPSE (sort neighbors by weight) = graph CANONIZATION / individualization-refinement (nauty/bliss);
  makes the 1-WL neighbor multiset order-independent. INSTANCE-OF.
- QUANTUM (angular discretization N buckets) = histogram binning of the POLARIS angle. Well-defined only
  relative to the (POLARIS theta, AURORA r) frame. [embedding gap RESOLVED by AURORA correction.]
- WAVE (spreading width sigma) = KDE bandwidth / bias-variance / precision-recall knob. INSTANCE-OF (KDE).
- CONSTELLATION (multi-dim Bloom, 2D slices) = Bloom-family sketch; 2D axes = (AURORA r)x(POLARIS theta);
  similarity regime = LSH/MinHash (Broder 1997). INSTANCE-OF (Bloom); LSH the principled NN index (open).
- NEBULA (BWT+RLE) = core of bzip2 (Burrows-Wheeler 1994). BWT clusters equal-context symbols into runs;
  RLE-run-count = contextual regularity. Mantaci-Restivo-Rosone-Sciortino-Versari (2017): rho(BWT(w))<=2 rho(w),
  clustering ratio in ]0,2]. INSTANCE-OF the transform; NOVEL DOMAIN (BWT on graph-derived sequences).
- AURORA (virtual rotation) = circular registration; r = argmin-rotation magnitude on S^1 = EMD/1-Wasserstein
  on the circle. Rubner-Tomasi-Guibas IJCV 40(2):99-121 (2000). INSTANCE-OF. [AURORA supplies POLARIS's radius.]
- HARMONY (similarity) = metric family: cosine (magnitude-blind), Jaccard/Hamming (set-overlap, LSH), EMD
  (cross-bin, rotation-tolerant, principled). Shares S^1 registration machinery with AURORA.

## GABION / ASPF
- ASPF (prime-product fingerprint F(s)=Π p(t_i)) = GODEL NUMBERING (Godel 1931); multiset-as-monomial.
  Structural arithmetic: dedup=integer-equality, common-substructure=GCD, union=LCM, subtyping=divisibility
  -- the (N, gcd, lcm, |) distributive lattice. INSTANCE-OF. SPPF "packed derivation label" = Tomita 1985 /
  Billot-Lang ACL 1989; interned Forest node = hash-consing (Ershov/Goto).
- Thm 9.1 GALAXY<->ASPF: W_{v,k} <-> log_alpha(F(s)^k), p(t)=alpha^rank(t) = LOGARITHM MONOID ISOMORPHISM
  (multiplicative prime-product -> additive weighted-rank). Exact for EMA decay. STRONGEST bridge. INSTANCE-OF.
- Thm 9.2 CONSTELLATION<->ASPF: bitmask = degenerate Bloom (N=|vocab|,r=1,identity hash = exact membership). SOUND.
- Thm 9.3 Drift=Homotopy: 2-cells in a bicategory; rewriting-as-2-cells. LOOSEST -- render as change-of-frame,
  not proven homotopy equivalence.

## HASH-CONS (the four-sighting invariant)
- (1) ASPF interned Forest node, (2) CONSTELLATION Bloom, (3) APSP segment-dedup by (endpoints,len,childpair),
  (4) paperkit claim-intern. Common = HASH-CONSING / maximal sharing: ATerm (ASF+SDF/Rascal), reduced-ordered
  BDD sharing, SPPF packing (Tomita/Billot-Lang). intern(intern(x))=intern(x) = idempotent normal form. INSTANCE-OF.

## Nedge
- [0,+inf] CLOSED, 1 the IDEAL (self-dual fixed point of G_NOT(G)=1/G). DeMorgan exact: NOT(AND(NOT a,NOT b))
  =OR(a,b). = TORRES DUAL POSITIVE SEMIFIELD under reciprocal involution. Residuated lattice (Galatos-Jipsen-
  Kowalski-Ono). Paraconsistent in spirit (da Costa / Belnap-Dunn FDE / Priest LP) -- [0,inf]-valued not finite.
- NOT TROPICAL: Nedge is SOFT LogSumExp (L_OR=LSE, L_AND=-LSE(-)), explicitly contrasted vs HARD idempotent
  (min,+) tropical. Non-idempotent BY DESIGN (2G, G/2). The APSP-minplus<->Nedge bridge is the tau->0 soft->hard
  LIMIT analogy, NOT instance-of. CHANGE-OF-FRAME, flagged.

## DIR / APSP / OCAL
- DIR = declarative IR: sea-of-nodes (Click), MLIR, e-graphs/equality-saturation (Tate 2009; egg; MLIR eqsat
  arXiv:2505.09363). e-graph = hash-consed congruence-closure DAG = the hash-cons spine again. INSTANCE-OF.
- APSP = ALL-PAIRS SHORTEST PATHS (confirmed; "Adaptive Processing/Search Protocol" = discard). Segment doubling
  = Karp-Miller-Rosenberg prefix-doubling (1972) / Manber-Myers suffix arrays SODA 1990 / min-plus repeated
  squaring (CLRS, ceil(lg(n-1)) rounds). Reverse-index 2-hop = 2-HOP/HUB LABELING, Cohen-Halperin-Kaplan-Zwick
  SIAM JC 32(5):1338-1355 (2003). Hopsets (Cohen 2000), Thorup-Zwick oracles, contraction hierarchies. INSTANCE-OF.
  MERSENNE-PRIME HOP VARIANT = NOT FOUND in corpus (only in unrelated number-theory doc) -- QUARANTINE.
- OCAL = synthesis (DIR=APSP=Nedge, three frames). Curry-Howard (Constraint=Proof) + category-of-pipelines SOUND;
  Langlands-as-compilation / HoTT / "System Pi ToE" = SPECULATION, QUARANTINE.

## chamber/fan/min-plus (already gated f090_2_chamberfan; groundings:)
- braid arrangement of S_n (x_i=x_j) -> n! chambers = Coxeter complex; S_4 = 24 chambers, 6 walls=C(4,2).
  Parametric/tropical shortest-path costs -> normal fan, cells=constant-argmin, walls=ties (Joswig-Schroter). INSTANCE-OF.

## conservation (already gated f090_2_conservation; Cayley-Dickson ladder grounding:)
- R->C->H->O->S releases one property per rung (self-conjugacy/order, commutativity, associativity, alternativity
  +division). Baez "The Octonions". Schematic Noether (symmetry<->conservation analogy), not the literal theorem.
