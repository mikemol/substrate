#!/usr/bin/env python3
"""dump_agdai_pyast.py — dump a .agdai as the SHARED jea_pyalg IR (pyast term algebra).
The Agda core is interned (jea_agdai) into the SAME Intern jea_pyalg uses for python, so this
renders the typechecked core AS pyast IR: per-def IR trees + the flat node table."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_agdai as A, jea_pyalg as P

def sh(op): return (op.split(".")[-1] if op and "." in op else (op or "·"))

def dump_tree(I, idx, depth, seen, out, maxdepth):
    n = I.nodes[idx]
    fields = sh(n.op)
    extra = []
    if n.op and "." in n.op: extra.append(f"q={n.op}")
    if n.role: extra.append(f"role={n.role}")
    if n.lit:  extra.append(f"lit={n.lit}")
    if n.payload: extra.append(f"pay={n.payload}")
    tag = f"  ({' '.join(extra)})" if extra else ""
    out.append("  " * depth + f"#{idx} {fields} [{len(n.children)}ch]{tag}")
    if depth >= maxdepth: 
        if n.children: out.append("  "*(depth+1)+"…")
        return
    for c in n.children:
        dump_tree(I, c, depth + 1, seen, out, maxdepth)

def main():
    agdai = sys.argv[1] if len(sys.argv) > 1 else \
        "agda/_build/2.8.0/agda/Substrate/WitnessTower/Wedge/PyAstRig.agdai"
    maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    I = P.Intern(); res = A.core_intern_agdai(agdai, I)
    out = []
    out.append(f"# pyast (jea_pyalg IR) dump of {os.path.relpath(agdai)}")
    out.append(f"# interned forest: {I.size()} IR nodes; {len(res['units'])} def-units")
    out.append("# each node: #id  head  [child-count]  (q=qname role= lit= pay=residue)\n")
    for name, root in sorted(res["units"], key=lambda nr: nr[0]):
        k = res["kinds"].get(name, "?")
        out.append(f"═══ {name}   (Defn-kind: {k}) ═══")
        dump_tree(I, root, 0, set(), out, maxdepth)
        out.append("")
    txt = "\n".join(out)
    sys.stdout.write(txt + "\n")

if __name__ == "__main__":
    main()
