#!/usr/bin/env python3
"""Compose el-atlas-spec.md from the spec-src/ btree (S43 architecture).
Recursive sorted walk; METADATA files are node frontmatter, never composed;
.md leaves concatenate in lexicographic order ('0' < '00' < ... < '15' < 'A').
Refuses net shrink (the standing guard)."""
import io, os, sys, hashlib
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC, OUT = os.path.join(ROOT,'spec-src'), os.path.join(ROOT,'el-atlas-spec.md')
def walk(d):
    parts=[]
    for e in sorted(os.listdir(d)):
        p=os.path.join(d,e)
        if e=='METADATA': continue
        if os.path.isdir(p): parts+=walk(p)
        elif e.endswith('.md'): parts.append(io.open(p,encoding='utf-8').read())
    return parts
new=''.join(walk(SRC))
old=io.open(OUT,encoding='utf-8').read() if os.path.exists(OUT) else ''
o,n=old.count('\n'),new.count('\n')
if n<o:
    sys.exit(f'REFUSED: net shrink {o}->{n} lines; composition aborted')
io.open(OUT,'w',encoding='utf-8').write(new)
print(f'diff vs prior composition: +{n-o} / -0 lines; {len(old)} -> {len(new)} bytes' if n>=o else '')
print(f'written: {OUT} sha256[:12] = {hashlib.sha256(new.encode()).hexdigest()[:12]}')
