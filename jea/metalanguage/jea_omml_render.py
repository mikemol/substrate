#!/usr/bin/env python3
"""jea_omml_render.py — Σ-RENDER: OMML-IR → mat260 render-notation (the render leg, ι-aware).

The render oracle (mat260 oracle/run_render_oracle.py) checks that jea's surface notation agrees with
mat260's authored `render` fold (render-manifest.tsv): "E(k, p)", "(p ⊕ s_{i−1})", … This is NOT sympy
LaTeX and NOT the value/Octave projection — it is a STRUCTURAL READOUT over the forest. So it does NOT
go through `project_unified` (which lowers to sympy and ERASES the ι coercion to identity, O2); it walks
the interned IR directly, where the Coercion node is FIRST-CLASS. That is the only place ι can be shown:
the value projection erases it (full-block ⇒ identity), the render projection PRESERVES it.

  render(Name x)          = x                          (op text VERBATIM — "−" U+2212 is kept, not ASCII'd)
  render(Constant v)      = v
  render(App(f, a…))      = render(f) ++ "(" ++ ", "·render(aᵢ) ++ ")"        E(k, p)
  render(BinOp[op](a,b))  = "(" ++ render a ++ " " ++ SYM[op] ++ " " ++ render b ++ ")"   (p ⊕ s_{i−1})
  render(Subscript(b,s))  = render b ++ "_{" ++ render s ++ "}"                s_{i−1}
  render(Coercion(s,x))   = "ι_{" ++ s ++ "}(" ++ render x ++ ")"             ι_{𝒮→𝓑}(…)   (O3)

JeaCoercionAsk §2 (render-ι-CFB / render-ι-ChaCha) pins the exact target strings; the __main__ self-test
reproduces all 12 mat260 manifest entries (10 non-ι + the 2 ι) from their OMML, so mat260 can switch
tools/jea_gen_render.py onto this and retire the 2 PENDING. Pure stdlib + jea_omml.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern
from jea_omml import lower_omml

# BinOp operator -> render symbol. Xor (⊕) is the only operator in the mat260 cipher corpus and is the
# one verified against render-manifest.tsv; the rest are the natural notation, present for totality.
_SYM = {"Xor": "⊕", "Add": "+", "Sub": "−", "Mult": "·", "Div": "/"}


def _txt(n) -> str:
    """A leaf's surface text: the op (kept verbatim, incl. U+2212), else the payload residue."""
    return n.op or (n.payload[0] if n.payload else "?")


def render_notation(I: Intern, nid: int) -> str:
    """Render an interned OMML-IR node to mat260 render-notation. Coercion is first-class (shown);
    contrast project_unified, which erases it (the value projection). The structural read."""
    n = I.nodes[nid]
    k = n.kind
    if k == "Name" or k == "Constant":
        return _txt(n)
    if k == "Coercion":                                   # ι_{sub}(core) — O3, the whole point
        return f"ι_{{{n.op}}}({render_notation(I, n.children[0])})"
    if k == "Subscript":
        base, sub = n.children[0], n.children[1]
        return f"{render_notation(I, base)}_{{{render_notation(I, sub)}}}"
    if k in ("BinOp", "Op"):
        sym = _SYM.get(n.op, n.op)
        acc = render_notation(I, n.children[0])
        for c in n.children[1:]:
            acc = f"({acc} {sym} {render_notation(I, c)})"   # left fold; binary in the corpus
        return acc
    if k == "App":
        head = render_notation(I, n.children[0])
        args = ", ".join(render_notation(I, c) for c in n.children[1:])
        return f"{head}({args})"
    if k == "Args":                                       # bare argument list (no func head): join
        return ", ".join(render_notation(I, c) for c in n.children)
    return _txt(n)                                         # total: unknown leaf -> its text


def render_omml(omml_str: str) -> str:
    """Lower one OMML string and render it to mat260 notation (the render-oracle entry point)."""
    I = Intern()
    root, _ = lower_omml(omml_str, I)
    return render_notation(I, root)


# the full mat260 manifest (omml-manifest.tsv) + its authored render (render-manifest.tsv), embedded so
# the self-test is self-contained (no cross-repo path dep, as the sibling jea modules do). The 2 ι rows
# (CFB-stUpd, ChaCha20-output) are the capability this module adds; the other 10 are the regression.
_MANIFEST = {
    "ECB-stUpd":  ("<m:oMath><m:r>()</m:r></m:oMath>", "()"),
    "ECB-output": ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:r>p</m:r>'
                   '</m:e></m:d></m:e></m:func></m:oMath>', "E(k, p)"),
    "CBC-stUpd":  ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:brk/><m:d>'
                   '<m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r><m:r>⊕</m:r>'
                   '<m:sSub><m:e><m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e>'
                   '</m:d></m:e></m:func></m:oMath>', "E(k, (p ⊕ s_{i−1}))"),
    "CBC-output": ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:brk/><m:d>'
                   '<m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r><m:r>⊕</m:r>'
                   '<m:sSub><m:e><m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e>'
                   '</m:d></m:e></m:func></m:oMath>', "E(k, (p ⊕ s_{i−1}))"),
    "CFB-stUpd":  ('<m:oMath><m:func><m:fName><m:sSub><m:e><m:r>ι</m:r></m:e><m:sub><m:r>𝒮→𝓑</m:r></m:sub>'
                   '</m:sSub></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
                   '<m:e><m:brk/><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e>'
                   '<m:r>p</m:r><m:r>⊕</m:r><m:func><m:fName><m:r>trim</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:brk/><m:func><m:fName>'
                   '<m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/>'
                   '<m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:sSub><m:e><m:r>s</m:r>'
                   '</m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e></m:func></m:e></m:d>'
                   '</m:e></m:func></m:e></m:d></m:e></m:d></m:e></m:func></m:oMath>',
                   "ι_{𝒮→𝓑}((p ⊕ trim(E(k, s_{i−1}))))"),
    "CFB-output": ('<m:oMath><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r>'
                   '<m:r>⊕</m:r><m:brk/><m:func><m:fName><m:r>trim</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:func><m:fName><m:r>E</m:r>'
                   '</m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/>'
                   '</m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:sSub><m:e><m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r>'
                   '</m:sub></m:sSub></m:e></m:d></m:e></m:func></m:e></m:d></m:e></m:func></m:e></m:d>'
                   '</m:oMath>', "(p ⊕ trim(E(k, s_{i−1})))"),
    "OFB-stUpd":  ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r></m:e><m:e><m:sSub>'
                   '<m:e><m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e></m:func>'
                   '</m:oMath>', "E(k, s_{i−1})"),
    "OFB-output": ('<m:oMath><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r>'
                   '<m:r>⊕</m:r><m:brk/><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r>'
                   '</m:e><m:e><m:sSub><m:e><m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e>'
                   '</m:d></m:e></m:func></m:e></m:d></m:oMath>', "(p ⊕ E(k, s_{i−1}))"),
    "CTR-stUpd":  ('<m:oMath><m:func><m:fName><m:r>Inc</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/></m:dPr><m:e><m:r>i</m:r></m:e></m:d></m:e></m:func></m:oMath>',
                   "Inc(i)"),
    "CTR-output": ('<m:oMath><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r>'
                   '<m:r>⊕</m:r><m:brk/><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>k</m:r>'
                   '</m:e><m:e><m:func><m:fName><m:r>Concat</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr><m:e><m:r>v</m:r>'
                   '</m:e><m:e><m:r>i</m:r></m:e></m:d></m:e></m:func></m:e></m:d></m:e></m:func></m:e>'
                   '</m:d></m:oMath>', "(p ⊕ E(k, Concat(v, i)))"),
    "ChaCha20-stUpd": ('<m:oMath><m:func><m:fName><m:r>Inc</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e><m:r>i</m:r></m:e></m:d></m:e>'
                   '</m:func></m:oMath>', "Inc(i)"),
    "ChaCha20-output": ('<m:oMath><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr><m:e>'
                   '<m:brk/><m:func><m:fName><m:sSub><m:e><m:r>ι</m:r></m:e><m:sub><m:r>𝓑→𝔹*</m:r>'
                   '</m:sub></m:sSub></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/>'
                   '</m:dPr><m:e><m:r>p</m:r></m:e></m:d></m:e></m:func><m:r>⊕</m:r><m:brk/><m:func>'
                   '<m:fName><m:r>Permute</m:r></m:fName><m:e><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/></m:dPr><m:e><m:func><m:fName><m:r>Init</m:r></m:fName><m:e>'
                   '<m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr>'
                   '<m:e><m:r>k</m:r></m:e><m:e><m:r>v</m:r></m:e><m:e><m:r>i</m:r></m:e></m:d></m:e>'
                   '</m:func></m:e></m:d></m:e></m:func></m:e></m:d></m:oMath>',
                   "(ι_{𝓑→𝔹*}(p) ⊕ Permute(Init(k, v, i)))"),
}


if __name__ == "__main__":
    print("=== Σ-RENDER: OMML-IR → mat260 render-notation (ι-aware structural readout) ===\n")
    npass = 0
    for label, (omml, expect) in _MANIFEST.items():
        got = render_omml(omml)
        ok = (got == expect)
        npass += ok
        mark = "✓" if ok else "✗"
        tag = "  (ι coercion)" if "ι" in expect else ""
        print(f"  {mark} {label:16} {got}{tag}")
        if not ok:
            print(f"      expected: {expect}")
    print(f"\n  {npass}/{len(_MANIFEST)} render-manifest entries reproduced "
          f"(the 2 ι entries are the new capability; the 10 others the regression).")
    print("  mat260 can point tools/jea_gen_render.py at render_omml() and retire the 2 PENDING.")
    sys.exit(0 if npass == len(_MANIFEST) else 1)
