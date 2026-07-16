#!/usr/bin/env python3
# _agdatext.py — the single-source home for the pure Agda-surface-text helpers the scripts/ tooling was
# copy-pasting. Surfaced mechanically by the reuse wedge (scratch/scripts_dedup.py: `strip` duplicated 15×,
# `split_arrows`/`sa` 6×) — the rung-0 leaves of the reuse poset. Routing every copy through here kills the
# duplication AND the `sa` vs `split_arrows` NAME-DISTINCTION (one function, two names, across 6 files).
#
# ⚠ The function BODIES are VERBATIM family representatives (NO function docstrings): the SPPF support — which
# includes a docstring's Expr(Constant) node — is the identity the lift codemod matches against, so the
# canonical must have the family's exact support. Comments (like this) are not in the AST, so they're free.
#
# Invoked as `scripts/<tool>.py`, so `scripts/` is sys.path[0] and a bare `from _agdatext import …` resolves.
import re


# drop Agda comments — block `{- … -}` (dotall, non-greedy) then line `-- …` — each replaced by a space.
def strip(s):
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)
    return re.sub(r"--[^\n]*", " ", s)


# split an Agda type on its top-level `→` (paren/brace/bracket depth 0) — the telescope domains + codomain.
def split_arrows(s):
    out = []
    d = 0
    cur = ""
    for ch in s:
        if ch in "([{":
            d += 1
        elif ch in ")]}":
            d -= 1
        if ch == "→" and d == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out
