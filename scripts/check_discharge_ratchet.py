#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_discharge_ratchet.py — a level-polymorphic carrier must be DISCHARGED.

THE POLICY (user, 2026-07-31):

    "The intent behind the policy is to suppress global proofs like existence. At no
     point is it acceptable to say 'there exists a' without 'and I have handed it to
     you'."

WHY `set1_ratchet_cores` CANNOT ENFORCE THIS.  That gate measures UNIVERSE HEIGHT: it
counts a definition iff its peeled codomain sort is `Type` at a CLOSED level >= 1.  A
level-POLYMORPHIC carrier (`record R {ℓ : Level} … : Set ℓ`) has sort `Max n [ℓ]` — not
closed — so `levelOf` returns `Nothing` and the carrier is invisible to it.  That is
correct for universe height and it is documented (`agdai_shim.hs:52`), and memory
`level-poly-record-is-set1-paydown` records that level-poly-ing a fixed-`Set₁` record IS
a real paydown (`UPCategory` measured -7).

But height and DISCHARGE are different questions.  `Set ℓ` with `ℓ` universally
quantified is a claim over EVERY level; it is honest only when the construction is
uniform AND supplied.  Otherwise it is the same collapse `set1-is-grade-collapse` names
("construct across the grade, never hold the whole family"), relabelled into a shape the
height census cannot see — no closed level, no key, no debt.  This gate asks the second
question: **is the carrier handed over?**

DISCHARGED means either:
  * INHABITED — some term's type is the carrier (`bundle : CartanRoot-Equivalence`, or a
    `record { … }` literal assigned to it); or
  * CONSUMED — a later construction takes it as a hypothesis and discharges it
    (`Σ A (IsEqualised f g)`, `Kernel-At f b = IsEqualised f (const b)`).
A carrier that is neither is a declared existence with nothing handed over.

⚑ THE DETECTOR TOOK FOUR TRIES, AND THE FIRST THREE DISAGREED.  Recorded because the
disagreement is the evidence that a token scan cannot answer this:
  1. strict sort regex               -> 2 carriers   (under-counted: missed multi-line heads)
  2. line-based head parse           -> 112 carriers (right population)
  3. "no top-level signature names it" -> 46 flagged (FALSE POSITIVES: the regex saw only
     `^name :` lines, missing record fields, where-locals and applied positions —
     `IsEqualised` is used as `Σ A (IsEqualised f g)` and was flagged)
  4. "zero token occurrences elsewhere" -> 0 flagged (FALSE NEGATIVES: the tokenizer split
     on `.`, so `module Substrate.Category.RootSystem where` counted the module PATH as a
     use of the record.  `S2-Lift/AsFunctor.agda:41` is worse — a genuine occurrence of a
     DIFFERENT `S2-Lift`, a Functor parameter, not the record.)
A NAME is not a USE, and a module path is not a term.  This gate therefore resolves names
through `agda_defs.def_index` (which knows the definer) and looks only at TERM positions,
never at `module`/`import` lines.

⚑ NO BASELINE IS WRITTEN BY A READ (`ratchet.may_write`), and the census is ORDINAL-free:
keys are `<carrier>::<module>`, invariant under edits that move a declaration.

Usage: check_discharge_ratchet.py [--quiet] [--list]
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scratch"))
import ratchet
import agda_lex
from agda_defs import def_index

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "agda", "Substrate")
BASELINE = os.path.join(HERE, "discharge_baseline.txt")

LEVELVAR = re.compile(r"(?<![\w'-])ℓ[\w₀-₉'-]*(?![\w'-])")
HEAD = re.compile(r"^\s*(record|data)\s+([^\s({]+)")
# a line that is STRUCTURE, not a term: its mention of a name is a module path.
STRUCTURAL = re.compile(r"^\s*(?:module|open|import|--)")


def carriers():
    """{name -> (relpath, sort)} for every level-POLYMORPHIC record/data carrier."""
    out = {}
    for path in agda_lex.agda_files(SRC):
        lines = agda_lex.mask_comments(open(path, encoding="utf-8", errors="replace").read()).split(
            "\n"
        )
        rel = os.path.relpath(path, ROOT)
        for i, l in enumerate(lines):
            m = HEAD.match(l)
            if not m:
                continue
            # ⚑ THE HEADER SPAN IS agda_lex's JOB, and the `j - i < 6` bound here
            # SILENTLY DROPPED declarations: no `where` within 6 lines → `continue`,
            # so the carrier never entered the census.  MEASURED: 401 multi-line
            # headers tree-wide, **136 need more than 6 continuations** (deepest: 40).
            # A discharge census that skips a third of its own multi-line population
            # reports a comfortable number for the wrong reason.
            end = agda_lex.head_span(lines, i)
            decl = " ".join(x.strip() for x in lines[i:end])
            if "where" not in decl:
                continue
            j = end - 1
            sort = decl.rsplit(":", 1)[-1].replace("where", "").strip()
            if sort.startswith("Set") and LEVELVAR.search(sort):
                out[m.group(2)] = (rel, sort)
    return out


def discharged(names):
    """{name} for carriers used in a TERM position anywhere in the tree.

    ⚑ Structural lines are skipped: `module Substrate.Category.RootSystem where` mentions
    the name only as a module-path segment, and counting it made every carrier look used
    (detector try 4).  A name is not a use.
    """
    seen = set()
    if not names:
        return seen
    # ⚑ ONE ALTERNATION, NOT N SEARCHES PER LINE.  This was O(files x lines x
    # carriers): 3457 files, every line, ~117 compiled patterns each `.search()`ed
    # individually -- 26.6s, which was 70% of the whole figure sweep and made the
    # gate the parallel FLOOR of the selftest run.
    #
    # ⚑ AND PARALLELISM WAS THE WRONG LEVER, MEASURED: a thread pool over the
    # eleven gates ran at 0.9x (SLOWER than serial), because one gate dominated
    # -- Amdahl, with a 1.4x ceiling.  `figures.py --times` prints that bound, so
    # the claim is falsifiable rather than asserted.  Fixing the inner loop is
    # what moves it; concurrency over an unbalanced DAG moves nothing.
    #
    # The regex engine scans each line ONCE and reports which alternative hit,
    # so the per-line cost stops scaling with the carrier count.  Longest-first
    # ordering matters: alternation is leftmost-first, so a name that is a
    # prefix of another (`Poly` vs `PolyRing`) must not shadow it.
    ordered = sorted(names, key=len, reverse=True)
    big = re.compile(r"(?<![\w'-])(" + "|".join(re.escape(n) for n in ordered) + r")(?![\w'-])")
    for path in agda_lex.agda_files(SRC):
        src = agda_lex.mask_comments(open(path, encoding="utf-8", errors="replace").read())
        for line in src.split("\n"):
            if STRUCTURAL.match(line):
                continue
            # the declaration itself is not a use of itself
            h = HEAD.match(line)
            decl_name = h.group(2) if h else None
            for m in big.finditer(line):
                n = m.group(1)
                if n != decl_name:
                    seen.add(n)
            if len(seen) == len(names):
                return seen  # every carrier discharged; nothing left to find
    return seen


def census():
    """{`<carrier>::<module>`} for every UNDISCHARGED level-poly carrier."""
    car = carriers()
    ok = discharged(set(car))
    idx = def_index()
    keys = set()
    for n, (rel, _sort) in car.items():
        if n in ok:
            continue
        home = idx.get(n) or [agda_lex.module_path(os.path.join(ROOT, rel), "agda")]
        keys.add(f"{n}::{home[0]}")
    return keys


def main():
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_discharge_ratchet")
    if rc is not None:
        return rc
    # ⚑ LIFTED TO `render=` — and the copy was doing MORE than duplicate a loop: it
    # re-ran `carriers()` and `discharged()` to rebuild the very census `census()`
    # computes one line below, so `--list` and the gate could disagree about the
    # population while claiming to describe the same thing (§6's derived-view class
    # inside one `main()`).  The renderer decorates the AUTHORITY's keys instead.
    # Keys are `<name>::<home>`; the extra fact is the declared sort, looked up by
    # name and falling back to the bare key when absent — total, as paydown needs.
    car = carriers()

    def _render(k):
        n = k.split("::", 1)[0]
        e = car.get(n)
        return f"{k:44} : Set {e[1][3:28]}" if e else k

    return ratchet.set_ratchet(
        census(),
        BASELINE,
        "discharge-ratchet",
        "--quiet" in sys.argv,
        list_keys="--list" in sys.argv,
        render=_render,
        noun="undischarged level-polymorphic carrier(s)",
        refuse_hint=(
            "A level-polymorphic carrier claims something at EVERY level. Hand it over: "
            "inhabit it with a term (`bundle : R`), or consume it in a construction that "
            "discharges it. 'There exists a' without 'and here it is' is the collapse "
            "this policy suppresses — it is merely invisible to the universe-height "
            "census, which measures a different thing."
        ),
    )


if __name__ == "__main__":
    sys.exit(main())
