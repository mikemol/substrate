#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_gate.py — Ⓜ.synth-gate: enforce that a synthetic apex's RENDER prose is
BOUNDED BY ITS MEET (the witnessed shared vocabulary). Turns the stated "bounded
by the meet" into a CHECK that FAILS on exceeders, mechanically closing the
overclaim surface of the hand/LLM render (the surface that, un-gated, let me
write `lossless / retraction / reify …` — outside-knowledge — into the apex).

A render content-word PASSES iff it:
  · matches a meet term — exact, hyphen-part, or shared ≥5-char stem (so
    `keeping`↔`keep`, `eea-trace`↔`eea`+`trace`, `instantiates`↔`instances`); OR
  · is a connective/meta word (ALLOW); OR
  · is in the file's `metadata.allow` — JUSTIFIED residue the 40%-meet missed
    (each entry is a deliberate, documented exception, not a loophole).
Else it's an EXCEEDER (overclaim) → gate FAILS (exit 1), listing them to cut or justify.

  python3 synth_gate.py synth/<slug>.md     # one      python3 synth_gate.py   # all synth/*.md
"""

import os, re, sys, glob
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G  # full(), words()

# name → real path (memories live in subdirs too; [[name]] resolves anywhere under memory/)
PATHS = {os.path.basename(f)[:-3]: f for f in glob.glob(HERE + "/**/*.md", recursive=True)}
ALLOW = set(
    (
        "the a an of to in is it as be by or and not for on with that this these those we i so its "
        "are was can has had via per no also when then than only into out up down over under most more "
        "less each both new one rather always side apply never either whose carried keep kept keeping "
        "mechanically proposal bounded meet may exceed below above across discipline memories does did "
        "will being been about here want done it their them then a an view"
    ).split()
)


def stem_match(w, meet):
    for part in [w] + w.split("-"):
        if not part:
            continue
        if part in meet:
            return True
        for m in meet:
            if (m.startswith(part) or part.startswith(m)) and min(len(m), len(part)) >= 4:
                return True
            if len(os.path.commonprefix([part, m])) >= 5:
                return True
    return False


def gate(path):
    s = open(path).read()
    # CEILING = words WITNESSED BY ≥2 member memories (hub-robust: a single mega-file
    # like open_threads saying it doesn't license the claim; two members do).
    wsec = s.split("## witnesses", 1)[1] if "## witnesses" in s else ""
    wl = re.findall(r"\[\[([a-z0-9_]+)\]\]", wsec)
    wdf = Counter()
    for nm in wl:
        p = PATHS.get(nm)
        if p:
            wdf.update(set(G.words(G.full(p))))
    ceiling = set(w for w, c in wdf.items() if c >= 2)
    # RENDER = the ## apex section's bullet/quote lines (projection phrases or any prose);
    # drop the header line, strip ·N· support counts and _(annotation)_.
    sec = s.split("## apex", 1)[1].split("## witnesses", 1)[0] if "## apex" in s else ""
    body = "\n".join(l for l in sec.splitlines()[1:] if l.strip().startswith(("-", ">")))
    render = re.sub(
        r"\[\[.*?\]\]|·\d+·|·d\d+·|_\(.*?\)_", "", body, flags=re.S
    )  # links/counts are pointers
    rwords = set(w for w in re.findall(r"[a-z][a-z-]{2,}", render.lower()) if w not in ALLOW)
    exceed = sorted(w for w in rwords if not stem_match(w, ceiling))
    ok = not exceed
    tag = "PASS" if ok else "FAIL"
    print(
        f"{tag}  {os.path.basename(path)}: {len(rwords)} render words, "
        f"ceiling={len(ceiling)} (≥2 of {len(wl)} witnesses), {len(exceed)} EXCEED (no ≥2 support)"
        + (f" → {', '.join(exceed)}" if exceed else "")
    )
    return ok


paths = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "synth", "*.md")))
if not paths:
    print("no synth/*.md to gate")
    sys.exit(0)
results = [gate(p) for p in paths]  # eval ALL (don't short-circuit at first FAIL)
sys.exit(0 if all(results) else 1)
