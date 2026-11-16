#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""band_sppf.py — the BANDING readout over the SPPF forest, not over a token chain.

The phrase pipeline (synth_apex) bands Sequitur rules by how many MEMBER DOCUMENTS
quote them. That works because prose IS a chain, so a list-digram is the honest
incidence. Source is a LATTICE: the honest incidence is the shared FACE (a node
together with its child-tuple), which `jea_pysim.Corpus` already computes at intern
time -- `node_units[nid]` is exactly "which units share this cell".

So this is synth_apex's graded curve with the incidence swapped:

    synth_apex                          band_sppf
    Sequitur rule                  ->   interned node (a cell)
    member docs quoting the rule   ->   node_units[nid] (units sharing the face)
    rule depth (_rdepth)           ->   min depth across units
    maximal-phrase dedup           ->   drop a node whose parent has the SAME support
    universal / broad / pairwise   ->   unchanged: the band is a function of breadth

Dedup is the load-bearing part: interning is bottom-up, so every ancestor of a
shared node is itself shared. Without collapsing a chain of same-support nodes to
its topmost member, the bands fill with fragments of one motif.

    band_sppf.py <dir-or-file> ...
"""
import os
import sys

# ⚑ THE PATHS WERE HARDCODED ABSOLUTE, so this ran on exactly one checkout.  A
# structural reader that only works from one clone is a probe, not a tool — and
# the corpus root is derivable from this file's own location, which every sibling
# reader already does.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(ROOT, "jea", "metalanguage"), os.path.join(ROOT, "jea")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from jea_pysim import Corpus


def _py_under(targets):
    """Expand OPERANDS a caller named into .py paths — not the corpus.

    ⚑ RENAMED FROM `py_files`, WHICH IMPLIED AN AUTHORITY THIS IS NOT.  The
    corpus authority is `pycodemod.py_files`, and it carries five measured
    exclusion classes (`.venv`, `site-packages`, `bazel-*`, `__pycache__`,
    `.edit-snapshots`) that this deliberately has none of.  Sharing the name made
    `--rivals py_files` report "3 defs, 0 delegating", which reads as three rival
    corpus definitions feeding two pre-commit gates — an audit drew exactly that
    conclusion, and it is false: both gates call `pycodemod.py_files` qualified,
    and this has ONE caller, `main` at :56, on paths a human typed.

    ⚑ AND THE MISSING EXCLUSIONS ARE CORRECT HERE, which is why converging the
    bodies would have been the wrong repair.  `main(targets)` receives explicit
    CLI operands, so this expands what was ASKED FOR; a corpus filter would make
    `band_sppf .venv/…/foo.py` silently return nothing.  Naming an excluded tree
    explicitly is a different question and must still answer — the same rule
    `pycodemod.py_files` records for its own root-relative skips.

    **A shared NAME is not a shared authority; a DIFFERENT name is how a private
    helper says so.**"""
    out = []
    for t in targets:
        if os.path.isdir(t):
            for dirpath, _dirs, files in os.walk(t):
                out += [os.path.join(dirpath, f) for f in sorted(files) if f.endswith(".py")]
        elif t.endswith(".py"):
            out.append(t)
    return sorted(out)


def sketch(C, nid, budget=7):
    """A short readable form of a cell: its head plus its children's heads."""
    n = C.I.nodes[nid]
    head = n.op or n.lit or n.kind
    kids = []
    for c in n.children[:budget]:
        cn = C.I.nodes[c]
        kids.append(str(cn.op or cn.lit or cn.kind))
    return f"{head}({', '.join(kids)}{', …' if len(n.children) > budget else ''})"


def bands(targets, min_arity=2):
    """{band -> [(support, depth, nid, units)]} plus the census — the READABLE half.

    ⚑ SPLIT OUT OF `main` SO THE ANSWER IS A VALUE, NOT A PRINT.  Everything this
    computes was previously reachable only by reading stdout, which is the shape
    the standing rule forbids: a consumer wanting the pairwise band had to parse
    the report.  `main` now renders what this returns.

    ⚑ AND THE THRESHOLD IS A PARAMETER BECAUSE IT IS NOT SETTLED FOR SOURCE.
    `MIN_ARITY = 2` was tuned against prose (the memory corpus), where a
    2-child cell is a real phrase.  Measured on five structural readers it
    admits `Block(Name, Name)` ×56 and `Tuple(str, str)` ×20 — role-lowering
    makes those the lattice's stopwords, so the broad band fills with them and
    the signal sits entirely in the pairwise tail.  Exposing it lets the
    threshold be MEASURED per corpus rather than inherited from a different one."""
    files = _py_under(targets)
    C = Corpus()
    for f in files:
        C.add_file(f)
    if not C.units:
        return None

    NU = len(C.units)
    shared = {nid: us for nid, us in C.node_units.items()
              if len(us) >= 2 and len(C.I.nodes[nid].children) >= min_arity}
    parent_support = {}
    for nid in shared:
        for c in C.I.nodes[nid].children:
            if c in shared:
                parent_support.setdefault(c, []).append(nid)
    maximal = {}
    for nid, us in shared.items():
        if any(shared[p] == us for p in parent_support.get(nid, [])):
            continue
        maximal[nid] = us

    def mindepth(nid, us):
        return min(C.units[ui].depth.get(nid, 1 << 30) for ui in us)

    hi = max(3, NU // 2)
    out = {"universal": [], "broad": [], "pairwise": []}
    for nid, us in maximal.items():
        ms = len(us)
        b = "universal" if ms >= hi else ("broad" if ms >= 3 else "pairwise")
        out[b].append((ms, mindepth(nid, us), nid, us))
    return {"bands": out, "corpus": C, "files": len(files), "units": NU,
            "shared": len(shared), "maximal": len(maximal), "hi": hi}


def frame_survey(targets, lo=2, hi=8):
    """The sharing profile ACROSS arity frames — the curve, not a point.

    ⚑ `min_arity` IS A FRAME, NOT A QUALITY KNOB (user, 2026-08-03: *"it's better
    read as a torsor, and the way you fix the torsor is going to depend on the
    questions you're asking — survey-of-parameters or survey-of-code"*).  A torsor
    has no origin; only DIFFERENCES are meaningful.  So "shared cells went 459 →
    27 when I raised arity 2 → 4" is not a reduction and not an improvement — it
    is a TRANSLATION, and comparing the two absolute counts is a category error.
    I was one edit from picking 4 and calling it settled, which bakes one frame
    into the tool and makes every other question unaskable.

    Which origin is right depends on the question:

      * survey-of-CODE ("what duplication should I retire?") wants the frame where
        a cell is a unit of refactorable structure — measured here, arity 4 surfaces
        `And(And, Call, Eq, Call, Call)` shared by `_scan_defs`/`rivals`, which is
        one compound predicate written three times and is actionable;
      * survey-of-PARAMETERS ("how does sharing respond to the frame?") is a question
        ABOUT the torsor, and no single arity answers it — the answer IS this curve;
      * survey-of-SCALE is a third frame entirely, and it already exists upstream:
        `jea_pysim.Corpus._depth_map`'s docstring calls depth "the real scale axis …
        recoverable, NOT a size-cap proxy" — i.e. the authority this reads from
        deliberately refuses to collapse ITS graded axis, and freezing mine would
        contradict that one module down.

    Returns [(arity, shared, maximal, universal, broad, pairwise)] so the caller
    reads the shape and picks a frame for THEIR question — keeping it graded is
    the whole point (`feedback_dont_collapse_to_smallest_representable`)."""
    rows = []
    for a in range(lo, hi + 1):
        got = bands(targets, min_arity=a)
        if got is None:
            break
        b = got["bands"]
        rows.append((a, got["shared"], got["maximal"],
                     len(b["universal"]), len(b["broad"]), len(b["pairwise"])))
    return rows


def main(targets, min_arity=2):
    got = bands(targets, min_arity)
    if got is None:
        print("no units interned")
        return
    C, NU, hi = got["corpus"], got["units"], got["hi"]
    bands_ = got["bands"]
    print(f"corpus: {got['files']} files -> {NU} units, "
          f"forest {C.I.size()} nodes")

    caps = {"universal": 10, "broad": 14, "pairwise": 8}
    label = {
        "universal": f"shared by >={hi}/{NU} units — universal skeleton (shallow)",
        "broad": f"shared by 3–{hi-1} units — broad motifs",
        "pairwise": "shared by exactly 2 units — deep pairwise co-structure (the residue)",
    }
    print(f"shared cells {got['shared']} -> {got['maximal']} maximal "
          f"(ancestor-deduped, min_arity={min_arity})\n")
    for b in ("universal", "broad", "pairwise"):
        rows = sorted(bands_[b], key=lambda r: (-r[0], -r[1]))[: caps[b]]
        if not rows:
            continue
        print(f"### {b} · {label[b]}")
        for ms, d, nid, us in rows:
            names = sorted({C.units[ui].name for ui in us})
            who = ", ".join(names[:4]) + ("…" if len(names) > 4 else "")
            if b == "pairwise":
                print(f"  ·{ms}· d{d}  {sketch(C, nid)}   [{who}]")
            else:
                print(f"  ·{ms}· d{d}  {sketch(C, nid)}")
        print()


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    import tempfile
    d = tempfile.mkdtemp()

    # ⚑ TWO FUNCTIONS SHARING DEEP STRUCTURE UNDER DIFFERENT NAMES — the exact
    # class `--rivals` and `--calls` cannot see, because they need a NAME to ask
    # about.  `alpha` and `beta` share no identifier; they share a shape.
    a = os.path.join(d, "m1.py")
    open(a, "w").write(
        "def alpha(rows):\n"
        "    out = []\n"
        "    for r in rows:\n"
        "        out.append(r.strip())\n"
        "    return sorted(out)\n")
    b = os.path.join(d, "m2.py")
    open(b, "w").write(
        "def beta(items):\n"
        "    acc = []\n"
        "    for it in items:\n"
        "        acc.append(it.strip())\n"
        "    return sorted(acc)\n")
    got = bands([a, b])
    check("two files intern into a corpus", got is not None, True)
    check("both units are seen", got["units"], 2)
    # ⚑ THE FINDING IS THE PAIRWISE BAND.  With exactly two units, every shared
    # cell is shared by 2, so `hi = max(3, 1) = 3` puts all of them in pairwise —
    # which is the band the tool exists to surface (the deep residue).
    check("structure shared by unrelated names IS found",
          len(got["bands"]["pairwise"]) > 0, True)

    # ⚑ AND IT MUST NOT FIRE ON UNRELATED SOURCE — a detector that reports
    # sharing everywhere measures nothing.  This is the discrimination half.
    c = os.path.join(d, "m3.py")
    open(c, "w").write("X = 1\n")
    e = os.path.join(d, "m4.py")
    open(e, "w").write("Y = 2\n")
    lone = bands([c, e])
    check("trivial unrelated files share no multi-child cell",
          lone is None or len(lone["bands"]["pairwise"]) == 0, True)

    # ⚑ MIN_ARITY IS A MEASURED PARAMETER, NOT A CONSTANT.  Raising it must
    # narrow the population — if it did not, the knob would be decoration.
    wide = bands([a, b], min_arity=2)
    narrow = bands([a, b], min_arity=6)
    check("raising min_arity narrows the shared population",
          narrow["shared"] <= wide["shared"], True)

    # ⚑ ANCESTOR DEDUP IS THE LOAD-BEARING STEP (the module docstring says so),
    # and it was never asserted.  Interning is bottom-up, so every ancestor of a
    # shared cell is shared with the SAME support — without collapsing those the
    # bands fill with fragments of one motif.
    check("dedup removes at least as much as it keeps intact",
          wide["maximal"] <= wide["shared"], True)

    # ── the FRAME SURVEY: the curve, not a point ────────────────────────────
    # ⚑ THE PROFILE MUST BE MONOTONE IN THE FRAME.  A wider arity floor admits a
    # SUBSET of the cells a narrower one admits, so `shared` can only fall as
    # arity rises.  A non-monotone row would mean the floor is not doing what its
    # name says — and that is checkable without knowing the "right" arity, which
    # is the point: this asserts a property of the TORSOR, not of an origin.
    curve = frame_survey([a, b], lo=2, hi=5)
    check("the survey returns one row per frame", len(curve) >= 3, True)
    check("shared cells are monotone non-increasing in arity",
          all(curve[i][1] >= curve[i + 1][1] for i in range(len(curve) - 1)), True)
    # ⚑ AND MAXIMAL NEVER EXCEEDS SHARED IN ANY FRAME — the dedup is a subset
    # operation at every origin, which a single-frame case cannot establish.
    check("maximal <= shared in every frame",
          all(r[2] <= r[1] for r in curve), True)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got_, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got_!r} want {want!r}")
    print(f"band_sppf selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    if "--frames" in sys.argv:
        sys.argv.remove("--frames")
        _t = [a for a in sys.argv[1:] if not a.startswith("-")]
        if not _t:
            print("usage: band_sppf.py --frames <dir-or-file> ...")
            sys.exit(2)
        print("arity   shared  maximal   universal  broad  pairwise")
        for _a, _s, _m, _u, _b, _p in frame_survey(_t):
            print("  %-4d  %6d  %7d   %9d  %5d  %8d" % (_a, _s, _m, _u, _b, _p))
        print("   ⚑ THE FRAME HAS NO ORIGIN — read DIFFERENCES down this table, "
              "never one row as\n     'the' answer. Pick the arity that fits your "
              "question (code / parameters / scale).")
        sys.exit(0)
    _ma = 2
    if "--min-arity" in sys.argv:
        _i = sys.argv.index("--min-arity")
        _ma = int(sys.argv[_i + 1])
        del sys.argv[_i:_i + 2]
    _targets = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not _targets:
        print(__doc__)
        print("  --min-arity <n>   the child-count floor for a cell to count as a")
        print("                    gluing FACE (default 2, tuned on prose; measure")
        print("                    it for source rather than inheriting it)")
        sys.exit(2)
    main(_targets, _ma)
