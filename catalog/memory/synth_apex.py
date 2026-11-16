#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_apex.py — graded-S(g) apex synthesis for ONE cluster.

`build_context()` loads the corpus + mesh-derived gauge ONCE; `build_apex(phrase, ctx)`
regenerates one apex against it. `synth_scale.py` calls build_context once and build_apex
per stale cluster IN-PROCESS (no per-cluster corpus reload / gauge rebuild). CLI below.

The apex (`synth/<slug>.md`, type:synthetic, EXCLUDED from the corpus) = the cluster's
shared Sequitur-grammar structure read as a graded curve over sharing-breadth
(universal-shallow → pairwise-deep); every line ≥2-witnessed by construction (gated by
synth_gate.py). Members = bodies CITING the concept ∪ the NAMESAKE memory (cited canonical
source — its name tokenizes to the phrase even if its body phrases it differently).
"""

import os, re, sys, glob
import numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G
from eliza.sequitur import Sequitur, NT

# generic/process stopfilter (not concepts) — kept out of the gauge vocab + apex bands
GENERIC = set(
    "just have thing about make time back name right must own next there into step whole real run case move open order loop kept hold holds itself instead list add base too always says doesn build building check green key fix nothing exactly thing want done here this that them then than only also been being have has had does did will would could".split()
)
# link-prefix / tooling / generic heads dropped from apex bands (family-templates, not concepts)
DROP = set(
    "feedback project reference discipline jea user done all same both every from real "
    "green time here next gates modules session three want this that have does".split()
)


def build_context():
    """Load corpus + mesh-derived gauge (term → dominant SVD content-mode) ONCE."""
    files = sorted(
        f
        for f in glob.glob(HERE + "/**/*.md", recursive=True)
        if os.path.basename(f) not in G.SKIP
        and (os.sep + "index" + os.sep) not in f
        and (os.sep + "synth" + os.sep) not in f
    )
    names = [os.path.basename(f)[:-3] for f in files]
    toks = [G.words(G.full(f)) for f in files]
    text = [" " + " ".join(t) + " " for t in toks]
    df = Counter(w for t in toks for w in set(t))
    vocab = sorted(w for w, n in df.items() if 3 <= n <= 60 and w not in GENERIC)
    vix = {w: j for j, w in enumerate(vocab)}
    N, V = len(files), len(vocab)
    Mx = np.zeros((N, V))
    for i, t in enumerate(toks):
        for w in set(t) & set(vocab):
            Mx[i, vix[w]] = np.log(N / df[w])
    Mx /= np.linalg.norm(Mx, axis=1, keepdims=True) + 1e-9
    _, _, Vt = np.linalg.svd(Mx, full_matrices=False)
    Vk = Vt[1:4]
    gauge = {w: int(np.argmax(np.abs(Vk[:, vix[w]]))) for w in vocab}
    nametok = [" " + " ".join(G.words(names[i].replace("_", " "))) + " " for i in range(N)]
    return dict(names=names, toks=toks, text=text, gauge=gauge, nametok=nametok, N=N)


def members_of(phrase, ctx):
    """citers (body contains phrase) ∪ namesake (name tokenizes to phrase)."""
    text, nametok = ctx["text"], ctx["nametok"]
    p = " " + phrase + " "
    return [i for i in range(ctx["N"]) if p in text[i] or p in nametok[i]]


def build_apex(phrase, ctx):
    """Regenerate one apex against the shared context. Returns its path (or None)."""
    names, toks, text, gauge = ctx["names"], ctx["toks"], ctx["text"], ctx["gauge"]
    members = members_of(phrase, ctx)
    if not members:
        return None
    cdf = Counter(w for i in members for w in set(toks[i]) if w in gauge)
    meet = sorted((w for w in cdf if cdf[w] >= len(members) * 0.4), key=lambda w: -cdf[w])

    # GRADED-Π APEX: the cluster's shared Sequitur grammar as a truncatable curve over
    # sharing-breadth (universal-shallow → pairwise-deep; depth rises as breadth narrows).
    gram = Sequitur()
    for i in members:
        for w in toks[i]:
            gram.observe(w)
        gram.observe("∎")
    rules = gram.all_rules()
    memtext = [text[i] for i in members]
    _dep = {}

    def _rdepth(rid):
        if rid in _dep:
            return _dep[rid]
        _dep[rid] = 1 + max([_rdepth(s.rule_id) for s in rules[rid] if isinstance(s, NT)] + [0])
        return _dep[rid]

    rinfo = []
    for rid in rules:
        if rid == 0:
            continue
        e = tuple(w for w in G.expand(rules[rid], rules) if w != "∎")
        if not (2 <= len(e) <= 14) or not any(w in gauge for w in e) or all(w in DROP for w in e):
            continue
        mset = frozenset(j for j in range(len(memtext)) if (" " + " ".join(e) + " ") in memtext[j])
        if len(mset) >= 2:
            rinfo.append((e, mset, _rdepth(rid)))
    rinfo.sort(key=lambda x: -len(x[0]))  # longest first → maximal-phrase dedup
    maximal = []
    for e, mset, d in rinfo:
        s = " " + " ".join(e) + " "
        if any(s in (" " + " ".join(k[0]) + " ") and mset <= k[1] for k in maximal):
            continue
        maximal.append((e, mset, d))
    hi = max(3, len(members) // 2)
    graded = {"universal": [], "broad": [], "pairwise": []}
    for e, mset, d in maximal:
        ms = len(mset)
        b = "universal" if ms >= hi else ("broad" if ms >= 3 else "pairwise")
        graded[b].append((ms, d, len(e), e, mset))
    graded["universal"].sort(reverse=True)
    graded["broad"].sort(reverse=True)
    graded["pairwise"].sort(key=lambda x: (-x[1], -x[2]))
    caps = {"universal": 8, "broad": 12, "pairwise": 6}
    blab = {
        "universal": f"shared by ≥{hi}/{len(members)} — universal skeleton (shallow)",
        "broad": f"shared by 3–{hi - 1} — broad motifs",
        "pairwise": "shared by exactly 2 — deep pairwise co-quotes (the residue)",
    }
    apex_lines = []
    for b in ("universal", "broad", "pairwise"):
        rows = graded[b][: caps[b]]
        if not rows:
            continue
        apex_lines.append(f"### {b} · {blab[b]}")
        for ms, d, span, e, mset in rows:
            ph = " ".join(e)
            if b == "pairwise":
                apex_lines.append(
                    f"- «{ph}» ·d{d}· " + " ".join(f"[[{names[j]}]]" for j in sorted(mset))
                )
            else:
                apex_lines.append(f"- {ph} ·{ms}·")

    slug = re.sub(r"[^a-z0-9]+", "-", phrase.lower()).strip("-")
    out = [
        "---",
        f"name: synth_{slug.replace('-', '_')}",
        f'description: "SYNTHETIC apex of the «{phrase}» cluster ({len(members)} memories): {", ".join(meet[:8])}."',
        "metadata:",
        "  type: synthetic",
        "  source: synth_apex.py — graded S(g) over sharing-breadth of the Sequitur grammar",
        f"  witnesses: {len(members)}",
        "---",
        "",
        f"_SYNTHETIC apex — derived/regenerable, **proposal-not-truth**. The apex below is the cluster's "
        f"shared Sequitur-grammar structure read as a GRADED CURVE over sharing-breadth (S(g): universal-"
        f"shallow → pairwise-deep), every rule witnessed by ≥2 members (gated by synth_gate.py); no hand-render._",
        "",
        "## apex — graded by sharing-breadth (S(g): truncatable; universal-shallow → pairwise-deep; mechanical, no hand-render)",
        *apex_lines,
        "",
        "## witnesses",
        "  " + ", ".join(f"[[{names[i]}]]" for i in members),
        "",
    ]
    os.makedirs(os.path.join(HERE, "synth"), exist_ok=True)
    path = os.path.join(HERE, "synth", slug + ".md")
    open(path, "w").write("\n".join(out) + "\n")
    return path


if __name__ == "__main__":
    phrase = sys.argv[1] if len(sys.argv) > 1 else "never discard residue"
    ctx = build_context()
    p = build_apex(phrase, ctx)
    print(
        f"wrote {p}  ({len(members_of(phrase, ctx))} members)"
        if p
        else f"no members for «{phrase}»"
    )
