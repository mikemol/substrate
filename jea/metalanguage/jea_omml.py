#!/usr/bin/env python3
"""jea_omml.py — Σ-OMML: the real OMML (Office Math Markup Language) front-end into the SPPF.

Lowers OMML `<m:oMath>…</m:oMath>` into jea_pyalg IR. The companion to jea_omml_domain (Σ3, the
audience-domain carrier): this PRODUCES the term + any tagged partitions; that CONSUMES them.

Inspiration: the mat260 OMML pipeline (~/github/mat260) — a write-only Agda→OMML renderer (renderOMML
folds a verified `Tm` to OMML). Its vocabulary is the real target here, and its manifest the test corpus.
The decisive observation drawn from it: **function application is EXPLICIT via `<m:func>`** (E(k,p),
Inc(i), …), NOT juxtaposition — so where the OMML uses `m:func` there is NO ambiguity, lower straight to
App; the App/Mul fork (Σ3's partition) arises ONLY for bare juxtaposition (adjacent `<m:r>` with no
`m:func` and no operator between). Well-authored OMML (mat260) therefore lowers to clean App terms with
ZERO partitions; sloppy/implicit OMML surfaces the fork for the audience-carrier to resolve.

THE CLOSED VOCABULARY (measured from mat260's renderOMML; recursive pattern-match, no layout heuristics):
  m:oMath   the equation root
  m:func    EXPLICIT application: m:fName (the op name) + m:e (the arg group)  -> App(Name(op), *args)
            SPECIAL CASE: when m:fName is m:sSub(m:r "ι", sub) -- a subscripted ι, the carrier-injection
            COERCION renderOMML emits for opInject/opFromBlk -- lower to Coercion(sub, arg), NOT App.
  m:fName   the function-name slot (a single m:r; OR an m:sSub for the ι coercion, see m:func)
  Coercion  a carrier-injection coercion ι_{sub}: op=sub (the carrier-pair text, e.g. "𝒮→𝓑"),
            one child = the coerced core. A transparent inclusion (identity on values; see
            project_unified). It is NOT an App(Name "?") -- ι is first-class.
  m:e       a generic element/argument container -> lower its child sequence
  m:d       a delimiter (parens). With several m:e children = an ARGUMENT LIST; with one = grouping.
            m:dPr/begChr/endChr/sepChr are delimiter PROPERTIES (visual) -> ignored for structure.
  m:r       a run: an identifier/literal -> Name(op=text); a lone operator (⊕,+,−,·) -> a BinOp token
  m:sSub    a subscript: m:e (base) + m:sub (subscript content) -> Subscript(base, sub)
  m:sub     the subscript content
  m:brk     a layout line break -> dropped (metadata, not structure; mat260 pins it separately)

Pure stdlib + jea_pyalg. Front-end (sibling of jea_pyalg/jea_cuda in metalanguage/). Returns plain
partition tuples so it stays dependency-light; jea_omml_domain wraps them into Partitions + cross_terms.
"""
from __future__ import annotations
import sys, os
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR

_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
# a lone run that IS one of these is an INFIX OPERATOR token (not an identifier).
_OPS = {"⊕": "Xor", "+": "Add", "−": "Sub", "-": "Sub", "*": "Mult", "·": "Mult", "/": "Div"}


def _tag(el) -> str:
    return el.tag.split("}")[-1]


def _q(name: str) -> str:
    return f"{{{_NS}}}{name}"


class OmmlLowerer:
    """OMML -> IR. Records App/Mul forks (juxtaposition) as partition tuples for the Σ3 carrier."""
    def __init__(self, intern: Intern):
        self.I = intern
        self.partitions: list[tuple] = []        # (tag, strand_a_id, strand_b_id, label_a, label_b)

    def _name(self, txt: str) -> int:
        return self.I.intern(IR(kind="Name", op=txt, children=(), payload=(txt,)))

    def lower(self, el):
        """Return an interned id, or an ('OP', name) marker for a lone operator run, or None (layout)."""
        t = _tag(el)
        if t == "oMath":
            return self._collapse([self.lower(c) for c in el])
        if t == "func":
            fname = el.find(_q("fName"))
            sub = self._coercion_of(fname)
            if sub is not None:
                # ι_{sub}: carrier-injection coercion (renderOMML of opInject/opFromBlk). One argument,
                # the coerced core -> Coercion(sub, core), NOT App(Name "?"). (O1, JeaCoercionAsk §1.)
                args = self._args_of(el.find(_q("e")))
                core = args[0] if len(args) == 1 else self.I.intern(IR(kind="Args", children=tuple(args)))
                return self.I.intern(IR(kind="Coercion", op=sub, children=(core,), payload=(sub,)))
            opname = self._text_of(fname)
            args = self._args_of(el.find(_q("e")))
            fn = self._name(opname)
            return self.I.intern(IR(kind="App", children=(fn,) + tuple(args), payload=(opname,)))
        if t == "d":
            es = [c for c in el if _tag(c) == "e"]                 # skip dPr (visual delimiter props)
            lowered = [self._collapse([self.lower(x) for x in e]) for e in es]
            lowered = [x for x in lowered if x is not None]
            if len(lowered) == 1:
                return lowered[0]                                  # grouping / parenthesised single expr
            return self.I.intern(IR(kind="Args", children=tuple(lowered)))   # an argument list
        if t == "sSub":
            e_el, sub_el = el.find(_q("e")), el.find(_q("sub"))
            base = self._collapse([self.lower(x) for x in e_el]) if e_el is not None else None
            subc = self._collapse([self.lower(x) for x in sub_el]) if sub_el is not None else None
            return self.I.intern(IR(kind="Subscript", children=tuple(c for c in (base, subc) if c is not None)))
        if t == "r":
            txt = (el.text or "").strip()
            if txt in _OPS:
                return ("OP", _OPS[txt])
            return self._name(txt)
        if t == "brk":
            return None                                            # layout break -> dropped
        # fallthrough (e, sub, anything else): lower the child sequence
        return self._collapse([self.lower(c) for c in el])

    def _text_of(self, el) -> str:
        if el is None:
            return "?"
        r = el.find(_q("r"))
        if r is not None and r.text:
            return r.text.strip()
        return (el.text or "").strip() or "?"

    def _coercion_of(self, fname):
        """If m:fName is m:sSub whose base run is "ι" (the carrier-injection coercion), return the
        subscript's carrier-pair text (e.g. "𝒮→𝓑"); else None. A non-ι subscripted fName is left to
        the ordinary _text_of path (unchanged). ι-specific by design: ι is the coercion renderOMML emits."""
        if fname is None:
            return None
        ss = fname.find(_q("sSub"))
        if ss is None:
            return None
        if self._text_of(ss.find(_q("e"))) != "ι":
            return None
        return self._text_of(ss.find(_q("sub")))

    def _args_of(self, e) -> list[int]:
        """A func's m:e holds an m:d whose m:e children are the args (or, no m:d -> the e is one arg)."""
        if e is None:
            return []
        d = e.find(_q("d"))
        if d is None:
            x = self._collapse([self.lower(c) for c in e])
            return [x] if x is not None else []
        args = [self._collapse([self.lower(x) for x in c]) for c in d if _tag(c) == "e"]
        return [a for a in args if a is not None]

    def _collapse(self, items):
        """Fold a lowered child sequence. Operator markers -> BinOp (infix). Bare multi-item adjacency
        with no operator -> the App/Mul JUXTAPOSITION fork (record a partition, default to the App strand)."""
        items = [x for x in items if x is not None]
        if not items:
            return None
        if any(isinstance(x, tuple) and x[0] == "OP" for x in items):
            result = items[0]
            i = 1
            while i < len(items):
                if isinstance(items[i], tuple) and items[i][0] == "OP" and i + 1 < len(items):
                    result = self.I.intern(IR(kind="BinOp", op=items[i][1],
                                              children=(result, items[i + 1])))
                    i += 2
                else:
                    i += 1
            return result
        if len(items) == 1:
            return items[0]
        # JUXTAPOSITION (no operator, no m:func): App-vs-Mul ambiguity -> a Σ3 partition.
        a = self.I.intern(IR(kind="App", children=tuple(items)))                  # application reading
        mul = items[0]
        for x in items[1:]:
            mul = self.I.intern(IR(kind="BinOp", op="Mult", children=(mul, x)))    # product reading
        self.partitions.append(("ADJACENCY", a, mul, "application", "multiplication"))
        return a                                                                   # default strand


def lower_omml(omml_str: str, intern: Intern) -> tuple:
    """Lower one OMML string -> (root_id, partitions). The manifest strings carry the `m:` prefix with
    NO xmlns (as in a docx body fragment), so wrap them in a namespace root before parsing (as mat260's
    verify.py does). partitions is a list of (tag, app_id, mul_id, label_a, label_b) for the Σ3 carrier."""
    wrapped = f'<root xmlns:m="{_NS}">{omml_str}</root>'
    omath = ET.fromstring(wrapped)[0]
    L = OmmlLowerer(intern)
    root = L.lower(omath)
    return root, L.partitions


# a few real mat260 manifest entries, embedded so the demo is self-contained (no cross-repo path dep).
_SAMPLES = {
    "ECB-stUpd":  "<m:oMath><m:r>()</m:r></m:oMath>",
    "ECB-output": ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr>'
                   '<m:e><m:r>k</m:r></m:e><m:e><m:r>p</m:r></m:e></m:d></m:e></m:func></m:oMath>'),
    "CBC-stUpd":  ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr>'
                   '<m:e><m:r>k</m:r></m:e><m:e><m:brk/><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r><m:r>⊕</m:r><m:sSub><m:e>'
                   '<m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e>'
                   '</m:d></m:e></m:func></m:oMath>'),
}


def _render(I: Intern, nid, d=0) -> list:
    if nid is None:
        return ["·(empty)"]
    n = I.nodes[nid]
    head = n.kind + (f"[{n.op}]" if n.op else "")
    out = ["  " * d + head]
    for c in n.children:
        out += _render(I, c, d + 1)
    return out


if __name__ == "__main__":
    print("=== Σ-OMML: lower real OMML (mat260 vocabulary) into the SPPF ===\n")
    for name, omml in _SAMPLES.items():
        I = Intern()
        root, parts = lower_omml(omml, I)
        print(f"--- {name} ---")
        print("\n".join("  " + ln for ln in _render(I, root)))
        print(f"  partitions (App/Mul forks): {len(parts)}  "
              f"{'(clean: explicit m:func, no ambiguity)' if not parts else parts}")
        print()

    # the AMBIGUOUS case mat260 never writes: bare juxtaposition `ab` -> the Σ3 partition fires.
    print("--- juxtaposition  <m:e><m:r>a</m:r><m:r>b</m:r></m:e>  (no m:func) ---")
    I = Intern()
    root, parts = lower_omml("<m:oMath><m:e><m:r>a</m:r><m:r>b</m:r></m:e></m:oMath>", I)
    print("\n".join("  " + ln for ln in _render(I, root)))
    print(f"  partitions: {len(parts)}  -> {[(t, la, lb) for t, _, _, la, lb in parts]}")
    print("  (this tuple feeds jea_omml_domain.Partition; the audience carrier then commits a strand.)")
