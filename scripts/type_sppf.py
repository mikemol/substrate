#!/usr/bin/env python3
"""type_sppf.py — pass types through the wedge to build an SPPF of structure.

Walk the type-dependency graph bottom-up. For each data/record type, extract a
structural skeleton (its field/constructor shapes, with sub-type references
replaced by the structural HASH of the referenced type — recursive
hash-consing). This is the wedge dedup: a sub-structure already in the forest
becomes a shared node (a MOTIF); a type whose whole skeleton-hash already
exists is ISOMORPHIC to the one already there (collapse). Recursion/mutual
reference is the SPPF cycle node (the bastardized-Sequitur "already a path").

Reports: isomorphism classes (≥2 types sharing a skeleton-hash) and the top
recurring field-shape motifs.
"""
import os, re, sys, collections, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
STRUCT = {"→", "×", "Σ", "⊎", "≡", "⊤", "⊥", "Set", "Set₁", "Set₂", "∀", "List", "Vec", "Fin", "ℕ"}

def strip(s):
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)
    return re.sub(r"--[^\n]*", " ", s)

# 1. extract type blocks: decl line + following indented lines.
blocks = {}   # name -> (kind, [type-expr strings])
declre = re.compile(r"^(data|record)\s+(\S+)(.*)$")
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        lines = strip(open(os.path.join(dp, fn), encoding="utf-8").read()).splitlines()
        i = 0
        while i < len(lines):
            m = declre.match(lines[i])
            if m:
                kind, name, rest = m.group(1), m.group(2), m.group(3)
                exprs = [rest]
                j = i + 1
                while j < len(lines) and (lines[j].strip() == "" or lines[j][:1] in " \t"):
                    if " : " in lines[j]:
                        exprs.append(lines[j].split(" : ", 1)[1])
                    elif "→" in lines[j] or "×" in lines[j]:
                        exprs.append(lines[j])
                    j += 1
                blocks.setdefault(name, (kind, exprs))
                i = j; continue
            i += 1

known = set(blocks)

def field_shape(expr, hashes, stack):
    out = []
    for t in re.split(r"[\s()\[\]{};,.]+", expr):
        if t in STRUCT:
            out.append(t)
        elif t in known:
            if t in stack:        # cycle: already a path in the SPPF
                out.append("⟲")
            else:
                out.append("T" + hashes.get(t, "?")[:6])
    return tuple(out)

hashes = {}
def node_hash(name, stack=()):
    if name in hashes: return hashes[name]
    kind, exprs = blocks[name]
    stack = stack + (name,)
    # ensure deps hashed first (bottom-up); ignore cycles via stack
    for e in exprs:
        for t in re.split(r"[\s()\[\]{};,.]+", e):
            if t in known and t not in stack and t not in hashes:
                node_hash(t, stack)
    shapes = sorted(field_shape(e, hashes, stack) for e in exprs if e.strip())
    h = hashlib.sha1((kind + "|" + repr(shapes)).encode()).hexdigest()
    hashes[name] = h
    return h

for n in list(blocks):
    node_hash(n)

# 2. isomorphism classes
byhash = collections.defaultdict(list)
for n, h in hashes.items():
    byhash[h].append(n)
iso = sorted((v for v in byhash.values() if len(v) > 1), key=len, reverse=True)

print(f"== SPPF over {len(blocks)} types: {len(byhash)} distinct structural nodes ==")
print(f"isomorphism classes (≥2 types, identical structure up to sub-iso): {len(iso)}")
for cls in iso[:25]:
    print(f"  [{len(cls)}] " + ", ".join(sorted(cls)[:8]) + (" …" if len(cls) > 8 else ""))

# 3. motifs: recurring field-shapes across types
motif = collections.Counter()
for n in blocks:
    kind, exprs = blocks[n]
    for e in exprs:
        fs = field_shape(e, hashes, (n,))
        if fs: motif[fs] += 1
print(f"\ntop recurring field-shape motifs:")
for fs, c in motif.most_common(15):
    print(f"  {c:4d}  {' '.join(fs)}")
