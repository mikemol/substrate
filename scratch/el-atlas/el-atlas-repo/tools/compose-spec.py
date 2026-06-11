"""
compose-spec.py — builds el-atlas-spec.md from spec-src/ parts (MANIFEST order).

Discipline (I1): the spec is no longer hand-edited as a monolith. Edits go to
spec-src/ part files (each small enough to confidently rewrite in one pass);
this composer reassembles the deliverable and verifies nothing was shed:
  - every MANIFEST entry must exist; unmanifested *.md parts raise a WARNING
    (they would silently not ship);
  - prints a line-level diffstat vs the prior composed file and previews the
    first shed lines;
  - REFUSES to write a net-smaller composition unless ALLOW_SHRINK=1
    (intentional deletions must be explicit).
New parts: add the file AND its MANIFEST line. Renumber only with care —
filenames are ordering, MANIFEST is authority.
"""
import difflib, hashlib, io, os, sys

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src  = os.path.join(root, 'spec-src')
out  = os.path.join(root, 'el-atlas-spec.md')

names = [l.strip() for l in io.open(os.path.join(src, 'MANIFEST'), encoding='utf-8')
         if l.strip() and not l.startswith('#')]
missing = [n for n in names if not os.path.exists(os.path.join(src, n))]
if missing:
    print("FATAL: manifest entries missing:", missing); sys.exit(1)
extra = [f for f in sorted(os.listdir(src)) if f.endswith('.md') and f not in names]
if extra:
    print("WARNING: unmanifested parts (will NOT be composed):", extra)

new = "".join(io.open(os.path.join(src, n), encoding='utf-8', newline='').read() for n in names)
old = io.open(out, encoding='utf-8', newline='').read() if os.path.exists(out) else ""

if old == new:
    print(f"composition identical to current ({len(new)} bytes); nothing to write."); sys.exit(0)

ol, nl = old.splitlines(), new.splitlines()
sm = difflib.SequenceMatcher(None, ol, nl, autojunk=False)
add = rem = 0
shed_preview = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ('replace', 'delete'):
        rem += i2 - i1
        for l in ol[i1:i2]:
            if len(shed_preview) < 8: shed_preview.append(l)
    if tag in ('replace', 'insert'):
        add += j2 - j1
print(f"diff vs prior composition: +{add} / -{rem} lines; {len(old)} -> {len(new)} bytes")
for l in shed_preview: print("  shed:", l[:110])
if len(new) < len(old) and os.environ.get('ALLOW_SHRINK') != '1':
    print("REFUSED: net shrink. Inspect shed lines above; rerun with ALLOW_SHRINK=1 to accept intentional deletion.")
    sys.exit(1)
io.open(out, 'w', encoding='utf-8', newline='').write(new)
print("written:", out, "sha256[:12] =", hashlib.sha256(new.encode()).hexdigest()[:12])
