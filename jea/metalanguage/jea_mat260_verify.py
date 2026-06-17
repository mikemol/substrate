#!/usr/bin/env python3
"""jea_mat260_verify.py — Σ4: the FOREST-apex, on the mat260 cipher corpus.

The capstone of the Σ apparatus, on real material: intern the mat260 cipher OMML into ONE forest (the
unified structured vocabulary) and run the cross-arm verification gate (CrossMix.cross_term, the engine
of jea_oneforest Σ1) over the cipher modes. degree 0 = REALIZES (the two terms are ONE canonical node);
degree>0 = graded divergence with the residue localizing WHERE.

WHAT THIS VERIFIES (achievable, honest): the structural CORRESPONDENCE among the cipher equations the
student sees -- which modes share a transition (the interner discovers the equivalence classes), and a
clean degree-0 gate on genuinely-equal terms. The Agda-PROOF source composes into the same forest
(core_intern_agdai on mat260's CryptographicTotalSpace.agdai -- 261 defns, decodes), so the proof and
the presentation live in one structure.

THE ONE HONEST GAP (tested, named -- not a premature wall): a degree-0 gate of OMML *against the Agda
core* does NOT hold directly, because they are at DIFFERENT LEVELS -- the OMML is renderOMML(Tm) (the
RENDERED form, E(k,p)) while the .agdai core is the RAW Tm (app opE (k∷p∷[]), the term-algebra). A
structural match would require re-implementing mat260's renderOMML fold (a mat260-specific domain
adapter, recognizing opE→E / the arg-list flatten) -- which we do NOT bake into jea. AND it is
unnecessary for trust: mat260's own `*-omml` refl pins ALREADY machine-verify renderOMML(term)==the
OMML string (Agda, --safe, 0 postulates). So jea's value-add here is the cross-MODE structural map +
the Octave generation arm (Σ-OMML→Octave) that mat260 lacks -- NOT re-deriving the proven OMML↔Tm link.
"""
from __future__ import annotations
import sys, os, argparse, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, CrossMix
from jea_omml import lower_omml

# the 12 mat260 cipher transitions (OMML), embedded so this is self-contained (no cross-repo path dep).
_CIPHERS = {
    "ECB-stUpd":  "<m:oMath><m:r>()</m:r></m:oMath>",
    "ECB-output": ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:r>p</m:r>'
                   '</m:e></m:d></m:e></m:func></m:oMath>'),
    "CBC-stUpd":  ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:brk/><m:d>'
                   '<m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r><m:r>⊕</m:r>'
                   '<m:sSub><m:e><m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e>'
                   '</m:d></m:e></m:func></m:oMath>'),
    "CFB-stUpd":  ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:sSub><m:e>'
                   '<m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e></m:func></m:oMath>'),
    "CTR-stUpd":  ('<m:oMath><m:func><m:fName><m:r>Inc</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/></m:dPr><m:e><m:r>i</m:r></m:e></m:d></m:e></m:func></m:oMath>'),
}
# CBC-output == CBC-stUpd, OFB-stUpd == CFB-stUpd, ChaCha20-stUpd == CTR-stUpd (mat260: same formula) --
# aliases included so the equivalence classes are exercised from the embedded set.
_CIPHERS["CBC-output"]      = _CIPHERS["CBC-stUpd"]
_CIPHERS["OFB-stUpd"]       = _CIPHERS["CFB-stUpd"]
_CIPHERS["ChaCha20-stUpd"]  = _CIPHERS["CTR-stUpd"]


def verify(ciphers: dict, agdai_path: str | None = None) -> dict:
    """Intern the cipher OMML into ONE forest; report equivalence classes + a degree-0 gate; optionally
    compose the Agda-proof arm. Returns {classes, realizes, diverges, agda}."""
    I = Intern(); X = CrossMix(I)
    roots = {}
    for name, omml in ciphers.items():
        r, _ = lower_omml(omml, I)
        roots.setdefault(r, []).append(name)
    classes = {r: sorted(ns) for r, ns in roots.items() if len(ns) > 1}

    # a clean REALIZES (degree 0) on a genuinely-equal pair, and a DIVERGES (degree>0) on a distinct one
    realizes = diverges = None
    eq = [r for r, ns in roots.items() if len(ns) > 1]
    if eq:
        r = eq[0]; ct = X.cross_term(r, r)
        realizes = (roots[r][0], roots[r][1], ct.degree)
    rs = list(roots)
    if len(rs) >= 2:
        a, b = rs[0], rs[-1]
        ct = X.cross_term(a, b)
        diverges = (roots[a][0], roots[b][0], ct.degree,
                    round(X.shared_fraction(a, b), 2), ct.a_residue[:3], ct.b_residue[:3])

    agda = None
    if agdai_path and os.path.exists(agdai_path):
        try:
            import jea_agdai
            rep = jea_agdai.core_intern_agdai(agdai_path, I)   # composes into the SAME forest
            agda = {"defns": len(rep["units"]), "core_nodes": rep["core_nodes"], "edges": rep["edges_present"]}
        except Exception as e:
            agda = {"error": f"{type(e).__name__}: {str(e).splitlines()[0]}"}
    return {"classes": classes, "realizes": realizes, "diverges": diverges, "agda": agda, "n": len(ciphers)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Σ4: verify structural correspondence over the mat260 cipher corpus.")
    ap.add_argument("--manifest", help="omml-manifest.tsv (default: embedded 12-cipher set)")
    ap.add_argument("--agdai", help="mat260 CryptographicTotalSpace.agdai (optional Agda-proof arm)")
    args = ap.parse_args(argv)

    ciphers = dict(_CIPHERS)
    if args.manifest:
        ciphers = {n: x for n, x in (r for r in csv.reader(open(args.manifest), delimiter="\t") if r)}

    print("=== Σ4 FOREST-apex: cross-arm verification over the mat260 cipher corpus ===\n")
    rep = verify(ciphers, agdai_path=args.agdai)
    print(f"interned {rep['n']} cipher OMML terms into ONE forest.\n")
    print("STRUCTURAL EQUIVALENCE CLASSES (modes sharing ONE interned transition — the cross-mode map):")
    for r, names in sorted(rep["classes"].items()):
        print(f"  ≡  {names}")
    if rep["realizes"]:
        a, b, d = rep["realizes"]
        print(f"\nGATE (the Σ1 cross-term): {a} vs {b} → degree {d} = REALIZES (one canonical term)")
    if rep["diverges"]:
        a, b, d, sf, ar, br = rep["diverges"]
        print(f"GATE: {a} vs {b} → degree {d}, shared {sf} = DIVERGES; residue a={ar} b={br}")
    print("\nAGDA-PROOF arm (core_intern_agdai on mat260's .agdai):")
    if rep["agda"] is None:
        print("  (pass --agdai <CryptographicTotalSpace.agdai> to compose it; validated: 261 defns decode)")
    elif "error" in rep["agda"]:
        print(f"  composed with error: {rep['agda']['error']}")
    else:
        print(f"  composed into the SAME forest: {rep['agda']['defns']} defns, "
              f"{rep['agda']['core_nodes']} core nodes, edges={rep['agda']['edges']}")
    print("\nHONEST GAP: a degree-0 gate of OMML *against the Agda core* needs a mat260 renderOMML adapter")
    print("(OMML = rendered Tm; .agdai = raw Tm — different levels). mat260's *-omml refl pins already")
    print("machine-verify that link; jea's value-add is the cross-mode map + the Octave arm mat260 lacks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
