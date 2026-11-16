#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""pcr_corpus_grammar.py — feed the WHOLE memory corpus through ONE eliza Engine
REPEATEDLY (PCR-style cyclic amplification) until the per-pass surprise stops
dropping. eliza builds transition chains (trigram + Sequitur grammar + grammar-
trigram); cycling amplifies the RECURRING structure until the grammar saturates.

The amplified Sequitur rules ARE the corpus's recurring motifs = the CORE IDEAS
(the common structures the user wants indexed, not the incidents). This is the
real answer to Ⓜ.compact: not a per-memory coordinate read in isolation, but the
grammar eliza LEARNS over the whole corpus.

Tokens (carry whatever we want): each memory's content-word SEQUENCE (order kept
— transition chains need order), memories separated by a ∎ boundary token.
"""

import os, re, glob, sys, hashlib
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
ELIZA = os.path.realpath(os.path.join(HERE, "../../../../github/substrate/scratch/eliza"))
sys.path.insert(0, ELIZA)
from eliza.predictor import TrigramPredictor
from eliza.sequitur import Sequitur, NT

SKIP = {"MEMORY.md", "ARCHIVE.md", "MEMORY.candidate.md"}
STOP = set(
    "the a an of to in is it as be by or and not for on with that this these those we i so its are was can has had via per no also when then than only into out up down over under most more less each both new one are you your they them their".split()
)


def claim(p):
    s = open(p).read()
    m = re.match(r"^---\n(.*?)\n---", s, re.S)
    d = re.search(r"^description:\s*(.+)$", m.group(1), re.M) if m else None
    return d.group(1).strip().strip('"') if d else ""


def words(t):
    """content-word SEQUENCE, order preserved (transition chains need order)."""
    return [w for w in re.findall(r"[a-z][a-z-]{2,}", t.lower()) if w not in STOP]


def expand(seq, rules, max_out=40):
    """Iterative (eliza's recursive walk overflows on the saturated grammar)."""
    out = []
    stack = [(s, ()) for s in reversed(seq)]
    while stack and len(out) < max_out:
        s, seen = stack.pop()
        if isinstance(s, NT):
            if s.rule_id in seen:
                out.append(f"R{s.rule_id}")
            else:
                body = rules.get(s.rule_id, [])
                for sub in reversed(body):
                    stack.append((sub, seen + (s.rule_id,)))
        else:
            out.append(s)
    return out


def main():
    files = sorted(
        f for f in glob.glob(HERE + "/**/*.md", recursive=True) if os.path.basename(f) not in SKIP
    )
    stream = []
    for f in files:
        stream += words(claim(f))
        stream.append("∎")  # memory boundary
    distinct = len(set(stream))
    print(f"corpus: {len(files)} memories → {len(stream)} tokens, {distinct} distinct\n")

    # The transition-chain core: the token-trigram = the transition OPERATOR.
    # PCR-cycling = power-iterating it; "surprise ends" = convergence. (Sequitur
    # explodes on identical-repetition — wrong tool for PCR; the Markov operator
    # is the right one.)
    pred = TrigramPredictor(vocab_size=distinct + 64)
    print(f"{'cyc':>3} {'pass_surprise':>13} {'Δsurp':>9} {'contexts':>9}")
    prev_surp = None
    cycles = 0
    for cyc in range(1, 26):
        cycles = cyc
        tot, n = 0.0, 0
        for tok in stream:
            s = pred.surprise_bits(tok)
            if s is not None:
                tot += s
                n += 1
            pred.update(tok)
        ps = tot / n if n else 0.0
        dsurp = (prev_surp - ps) if prev_surp is not None else float("nan")
        print(f"{cyc:>3} {ps:>13.4f} {dsurp:>9.4f} {pred.n_contexts():>9}")
        # converged when the RELATIVE drop is tiny (the large-vocab Laplace
        # floor makes the absolute surprise asymptote slowly, never 0).
        if prev_surp is not None and dsurp / prev_surp < 0.01:
            print(f"\n*** surprise converged at cycle {cyc} (Δ < 1% of level) ***")
            break
        prev_surp = ps

    # READ OUT the recurring transition chains. PCR multiplies every count by the
    # cycle#, so ABSOLUTE count is meaningless — the genuine cross-memory signal
    # is PER-PASS recurrence (count/cycles ≥ 2). [don't-collapse: per-pass, not raw]
    chains = []
    for (c1, c2), inner in pred.counts.items():
        if c1 == "∎" or c2 == "∎":
            continue
        tot = sum(inner.values())
        for c3, k in inner.items():
            per_pass = k / cycles
            if c3 != "∎" and per_pass >= 2:
                chains.append((per_pass, k / tot, c1, c2, c3))
    chains.sort(reverse=True)
    print(f"\n=== recurring transition chains (per-pass ≥ 2 = genuine cross-memory) ===")
    for pp, p, c1, c2, c3 in chains[:40]:
        print(f"  {pp:>4.0f}/pass p={p:.2f}  {c1} · {c2} → {c3}")


if __name__ == "__main__":
    main()
