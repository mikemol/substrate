#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""chamber_coord_probe.py — PROBE (lead-with-the-instrument): coordinatize the
memory corpus by routing each memory through eliza's REAL Engine (tokens = the
memory's distinctive terms), reading the chamber coordinate (orbit / fiber /
Fiedler / turbulence). NOT a reimplementation of eliza's spectral core — it
CALLS eliza.engine.Engine, the way the user directed.

The recursive common structure (Ⓜ.1): a memory's coordinate = its low-frequency
Laplacian harmonics on a graph. Here the graph is eliza's FIXED S₄ Cayley graph
and the memory is injected as a generator-WALK; the orbit (S₄/V₄ ≅ S₃, 6 values)
is the gauge-invariant cluster label, (Fiedler,turbulence) the continuous dual.

Token freedom (the user's pointer): tokens are whatever we want. Here a token is
a memory's distinctive TERM; the router maps term→generator by a stable hash, so
two memories sharing terms share generator-steps → correlated trajectories →
nearby chambers. route-is-gauge: this gauge is one of many; we lead with it to SEE.
"""

import os, re, glob, sys, hashlib
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.realpath(__file__))
ELIZA = os.path.realpath(os.path.join(HERE, "../../../../github/substrate/scratch/eliza"))
sys.path.insert(0, ELIZA)
from eliza.engine import Engine  # eliza's REAL pipeline
from eliza.router import Router
from eliza.alphabets import Gen

SKIP = {"MEMORY.md", "ARCHIVE.md", "MEMORY.candidate.md"}
STOP = set(
    "the a an of to in is it as be by or and not for on with that this these those we i so its are was can has had via per no also when then than only into out up down over under most more less each both new one".split()
)


def claim(p):
    s = open(p).read()
    m = re.match(r"^---\n(.*?)\n---", s, re.S)
    d = re.search(r"^description:\s*(.+)$", m.group(1), re.M) if m else None
    return d.group(1).strip().strip('"') if d else ""


def terms(t):
    caps = {w.lower() for w in re.findall(r"\b[A-Z][A-Z-]{2,}\b", t)}
    lows = {w for w in re.findall(r"\b[a-z]{5,}\b", t.lower()) if w not in STOP}
    return sorted(caps | lows)


_GENS = (Gen.s1, Gen.s2, Gen.s3)


def term_router(term: str) -> Gen:
    """CONTENT-BLIND gauge: term → generator by stable hash. SAME term → SAME
    gen across memories, but the gen carries no meaning → uniform orbits."""
    h = int(hashlib.blake2b(term.encode(), digest_size=8).hexdigest(), 16)
    return _GENS[h % 3]


def build_content_gauge(files):
    """CONTENT-CARRYING gauge (the wedge: SVD-content FEEDS eliza-geometry).
    Co-cluster terms into 3 generator-classes by their dominant low-frequency
    Laplacian mode on the memory×term graph (the SVD corner), then route each
    term to that generator. Shared MEANING → shared generators → correlated
    walks → orbit clustering. Returns term→Gen."""
    import numpy as np

    T = [set(terms(claim(f))) for f in files]
    df = Counter(w for ts in T for w in ts)
    vocab = sorted(w for w, n in df.items() if 3 <= n <= 60)
    vix = {w: j for j, w in enumerate(vocab)}
    N, V = len(files), len(vocab)
    M = np.zeros((N, V))
    for i, ts in enumerate(T):
        for w in ts & set(vocab):
            M[i, vix[w]] = np.log(N / df[w])
    M /= np.linalg.norm(M, axis=1, keepdims=True) + 1e-9
    U, sv, Vt = np.linalg.svd(M, full_matrices=False)
    Vk = Vt[1:4]  # Fiedler-onward, 3 modes = 3 gens
    gauge = {}
    for w, j in vix.items():
        gauge[w] = _GENS[int(np.argmax(np.abs(Vk[:, j])))]
    return gauge


def make_content_router(gauge):
    def r(term: str) -> Gen:
        return gauge.get(term, _GENS[0])

    return r


def main():
    files = sorted(
        f for f in glob.glob(HERE + "/**/*.md", recursive=True) if os.path.basename(f) not in SKIP
    )
    names = [os.path.basename(f)[:-3] for f in files]
    mode = sys.argv[1] if len(sys.argv) > 1 else "hash"
    if mode == "content":
        gauge = build_content_gauge(files)
        router = make_content_router(gauge)
        print("=== GAUGE: content (SVD term→mode feeds eliza geometry) ===")
    else:
        router = term_router
        print("=== GAUGE: hash (content-blind) ===")
    by_orbit = defaultdict(list)
    coords = {}
    for f, nm in zip(files, names):
        ts = terms(claim(f))
        if not ts:
            continue
        e = Engine(router=router, vocab_size=256)
        # feed the memory's terms as tokens through eliza's real Engine
        traj_orbits = Counter()
        for t in ts:
            r = e.step(t)
            traj_orbits[r.orbit_to] += 1
        final = e.current_chamber
        info = e.cocycle.info(final)
        coords[nm] = (
            info.canonical_word,
            info.fiber_label,
            info.chirality.name,
            round(e.manifold.fiedler_value(final), 3),
            round(e.manifold.turbulence_value(final), 3),
            traj_orbits.most_common(1)[0][0],
        )
        by_orbit[info.canonical_word].append(nm)

    orbits = sorted(by_orbit, key=lambda o: -len(by_orbit[o]))
    print(f"=== {len(coords)} memories routed through eliza's S₄ manifold ===")
    print(f"final-chamber orbit distribution (the 6-way S₄/V₄≅S₃ quotient):")
    for o in orbits:
        print(
            f"  orbit {o:>10}  [{len(by_orbit[o]):3}]  {', '.join(by_orbit[o][:6])}"
            + (" …" if len(by_orbit[o]) > 6 else "")
        )
    # fiber sub-distribution (V₄, the within-orbit coordinate)
    fib = Counter(c[1] for c in coords.values())
    chir = Counter(c[2] for c in coords.values())
    print(f"\nfiber (V₄) distribution: {dict(fib)}   chirality: {dict(chir)}")
    # is the trajectory-dominant orbit more informative than final chamber?
    by_traj = Counter(c[5] for c in coords.values())
    print(f"trajectory-dominant-orbit distribution: {dict(by_traj)}")


if __name__ == "__main__":
    main()
