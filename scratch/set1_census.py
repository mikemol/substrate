#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""set1_census.py — ⟡held-family-sweep pass 0: enumerate every remaining Set₁ (level≥1) def
from the .agdai cores (the ratchet's shim data) and group by module — the target-distribution
of held-families to construct-across-the-grade. (The dissolution trichotomy: parameterize /
field→index / carrier-families / ℕ-index.)"""
import os, sys, subprocess, json, glob
from collections import Counter, defaultdict

ROOT = "/home/mikemol/github/substrate"
AGDA = os.path.join(ROOT, "agda")
BUILD = os.path.join(AGDA, "_build", "2.8.0", "agda")
SHIM = os.environ.get("AGDAI_SHIM", os.path.join(ROOT, "jea", "metalanguage", "agdai_shim"))
env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")

cores = sorted(glob.glob(os.path.join(BUILD, "**", "*.agdai"), recursive=True))
bymod, total, sample = Counter(), 0, defaultdict(list)
for c in cores:
    rel = os.path.relpath(c, AGDA)
    try:
        p = subprocess.run([SHIM, rel], cwd=AGDA, env=env, capture_output=True, text=True, timeout=180)
    except Exception:
        continue
    if "decode Nothing" in p.stderr:
        continue
    mod = rel[:-len(".agdai")].replace(os.sep, ".")
    for l in p.stdout.splitlines():
        if not l.startswith('{"unit"'):
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        if isinstance(d.get("level"), int) and d["level"] >= 1:
            total += 1
            bymod[mod] += 1
            if len(sample[mod]) < 3:
                u = d.get("unit", "?")
                sample[mod].append(u.rsplit(".", 1)[-1])

print(f"# Set₁ census: {total} held-family defs across {len(bymod)} modules")
# roll up to top-level silos for the big picture
silo = Counter()
for m, n in bymod.items():
    parts = m.split(".")
    key = ".".join(parts[1:3]) if len(parts) > 2 else m   # Substrate.<A>.<B>
    silo[key] += n
print("\n## by silo (Substrate.<A>.<B>):")
for k, n in silo.most_common(20):
    print(f"  {n:4}  {k}")
print("\n## top modules:")
for m, n in bymod.most_common(30):
    print(f"  {n:4}  {m.replace('Substrate.','')}  ::  {sample[m]}")
