#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repair a `[NoParseForApplication]` caused by a FIXITY COLLISION.

⟡rename-collision.  A tree-wide `rename_at_source` matches a bare token, and two
operators can share one: `Substrate.Foundation.Nat.Plus._+_` (infixl, BINARY) and
`Substrate.Algebra.Z.Int._+_` (a PREFIX constructor, `+ 0` = the integer zero).
Renaming the first rewrote both, and `0ℤ = + 0` became `0ℤ = ℕ+ 0` — which cannot
parse, because the new operator needs a left operand the site does not have.

THE DIAGNOSIS IS ARITY AT THE USE SITE, and it is decidable rather than heuristic:
agda names the operator, its fixity, and the expression it could not parse.  If the
operator is infix and the reported application supplies no left operand, the site
means the prefix operator the rename displaced.

⚑ WHY THIS IS NOT A REGEX OVER SOURCES, MEASURED TWICE.  Two text heuristics were
tried first and BOTH failed, in opposite directions:
  * enumerate the tokens a prefix use can follow (`^`, `=`, `(`, `,`, `;`, `{`) —
    missed `m ⊖ m ≡ ℕ+ 0`, a prefix use after `≡`, and reported the class closed
    with 22 sites still broken;
  * require no left operand ON THE SAME LINE — flagged `CayleyDickson/Hilbert2D`
    and `Wedge/Compose/Laws`, both of which COMPILE, because a wrapped expression
    puts the operand on the previous line.
The compiler is the oracle: a site agda does not complain about is not damage,
whatever a pattern says.  22 regex candidates reduced to 4 real sites this way.

    fix_noparse.py <build.log | _build-dir> [--apply]

⚑ PREFER the per-module logs (`agda/_build`), for `fix_stale_using`'s reason: a
`make -j` CONSOLE log interleaves jobs and a parse can absorb another job's lines.

⚑ NO LOOP.  One pass, then rebuild.  A repaired line can carry a second error, and
guessing the next one is exactly how the line-local heuristic went wrong.
"""
import os
import re
import sys

AG = "agda"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SNAPPED = []


def _snapshot_once(paths):
    """Arm `edit_snapshot` on the first write of a run; a no-op thereafter."""
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import edit_snapshot
        # ⚑ `intent="apply"` IS ENTAILED BY THE BRANCH, not a guess.  The sole
        # caller is `repair` under `if apply and by_file:` — the write is
        # unconditional past that point, so re-reading argv here could only
        # DISAGREE with the branch that already decided.  It is also what makes the
        # `--selftest` fixture path work: the suite calls `repair(..., apply=True)`
        # directly with a tempfile, and argv there carries `--selftest` and neither
        # mutation flag, so an argv-reading guard REFUSES the one invocation that
        # asks the tool to check itself.  (Measured: `--selftest` exited 2.)
        edit_snapshot.guard("fix_noparse", list(paths), intent="apply")
    except Exception as e:                       # never block the repair on the guard
        print(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


_HDR = re.compile(
    r"^(/\S+\.agda):(\d+)\.(\d+)-(\d+): error: \[NoParseForApplication\]", re.M)
_OP = re.compile(r"^\s*(\S+)\s+\((infix|infixl|infixr)\s+operator", re.M)


def classify(log):
    """[(path, line, col, op, verdict)] for every `[NoParseForApplication]`.

    Verdicts:
      `fixity`  — an INFIX operator applied with no left operand: the site means a
                  PREFIX operator a rename displaced.  Mechanically repairable.
      `other`   — anything else (a genuine precedence or arity error).  Reported,
                  never guessed at: the fix would change what the term MEANS.

    ⚑ THE VERDICT IS READ OFF AGDA'S OWN GRAMMAR REPORT.  The error block lists
    every operator in play with its fixity; a site whose failing application starts
    at the operator itself has nothing to its left.  That is the whole predicate,
    and it needs no knowledge of which rename ran.
    """
    if os.path.isdir(log):
        out = []
        import glob as _g
        for p in sorted(_g.glob(f"{log}/**/*.agdai.log", recursive=True)):
            out += classify(p)
        return out
    try:
        txt = open(log, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    out = []
    for m in _HDR.finditer(txt):
        block = txt[m.end():m.end() + 600]
        ops = _OP.findall(block)
        if not ops:
            continue
        path, ln, col = m.group(1), int(m.group(2)), int(m.group(3))
        # the quoted expression is on the `Could not parse the application` line
        q = re.search(r"Could not parse the application\s+(.+)", block)
        expr = q.group(1).strip() if q else ""
        verdict = "other"
        # ⚑⚑ THE OPERATOR REPORTED MUST BE THE ONE THAT DECIDED THE VERDICT, and my
        # first cut returned `ops[0][0]` — the FIRST operator in agda's grammar list
        # — regardless of which one matched.  MEASURED 2026-08-18 on
        # `Q/JacobianEvalCD.agda:316`: the expression is
        # `powℤ … *ℤ (…) ≡ ℕ+ Dden`, agda lists `*ℤ` first, and the displaced
        # operator is `ℕ+`.  So `classify` said `fixity` (correctly) and handed
        # `repair` the name `*ℤ`, which appears on the line WITH a left operand —
        # so the repair correctly skipped it and the tool reported
        # `1 fixity site, 0 repairable`, refusing its own class.
        #
        # ⚑ A CLASSIFIER THAT NAMES THE WRONG SUBJECT IS WORSE THAN ONE THAT
        # REFUSES: the verdict is right, the remedy is unreachable, and the two
        # disagree silently.  `culprit` carries the decision to the consumer.
        culprit = ops[0][0]
        for name, fixity in ops:
            if not fixity.startswith("infix"):
                continue
            # ⚑ THE PREDICATE IS "THE EXPRESSION BEGINS WITH THE OPERATOR", and my
            # first cut added a second, looser arm that scanned ANYWHERE for the
            # operator preceded by a non-term.  In `a ⊗ b ⊗ c` the SECOND `⊗`
            # follows `b` — a term — but the scan found the first one's context and
            # called a genuine precedence error a fixity collision.  A refusal case
            # caught it; the loose arm is deleted rather than narrowed, because the
            # tight arm is the whole property: an infix operator with nothing to its
            # left is exactly an expression that STARTS with it.
            if re.match(r"^" + re.escape(name) + r"(?![\w'ˡʳ-])", expr):
                verdict, culprit = "fixity", name
                break
            # ⚑⚑ AND THE SAME PROPERTY HOLDS AFTER AN OPERATOR, WHICH THE
            # FIRST-POSITION TEST CANNOT SEE.  MEASURED 2026-08-17, three times by
            # hand in one turn: `(+ 0) *ℤ x ≡ ℕ+ 0` and
            # `cong (λ z → ℕ+ suc z) …` are the SAME displaced prefix operator as
            # `0ℤ = ℕ+ 0`, but the failing expression does not START with it — so
            # `classify` returned `other` and the remedy refused its own class.
            #
            # ⚑ THE PREDICATE IS STILL "NOTHING TO ITS LEFT", not "it appears
            # somewhere".  An infix operator whose left neighbour is ANOTHER
            # operator (`≡`, `→`, `,`) or an opener has no left operand there,
            # which is exactly the prefix reading.  `a ⊗ b ⊗ c` — the case that
            # killed the first loose arm — still classifies as `other`, because
            # the second `⊗`'s left neighbour is the TERM `b`.  That case is
            # pinned in the selftest and must keep passing.
            for m2 in re.finditer(re.escape(name) + r"(?![\w'ˡʳ-])", expr):
                left = expr[:m2.start()].rstrip()
                if not left or not re.search(r"[\w'ˡʳ)\]}]$", left):
                    verdict, culprit = "fixity", name
                    break
            if verdict == "fixity":
                break
        out.append((path, ln, col, culprit, verdict))
    return out


def repair(rows, apply=False):
    """Rewrite each `fixity` site's operator back to its bare (prefix) spelling.

    ⚑ THE PREFIX SPELLING IS THE RENAMED ONE MINUS ITS DOMAIN PREFIX, which is what
    a domain-suffixing rename produced (`+` → `ℕ+`).  Only the reported LINE is
    touched, and only where no left operand precedes the occurrence — the column
    agda reports is the failing application, not always the operator itself.
    """
    by_file = {}
    for path, ln, _col, op, verdict in rows:
        if verdict == "fixity":
            by_file.setdefault(path, []).append((ln, op))
    if apply and by_file:
        _snapshot_once(sorted(by_file))
    n = 0
    for path in sorted(by_file):
        try:
            lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        except OSError:
            continue
        done = []
        for ln, op in sorted(by_file[path], reverse=True):
            i = ln - 1
            if i >= len(lines) or op not in lines[i]:
                continue
            bare = op.lstrip("ℕ")                 # the domain prefix a rename added
            if bare == op or not bare:
                continue
            # ⚑ EVERY OCCURRENCE ON THE LINE IS TESTED, NOT JUST THE FIRST.  This
            # used `partition`, so a line carrying a CORRECT infix use before the
            # displaced prefix one (`(+ 0) *ℤ x ≡ ℕ+ 0`) was judged on the first
            # occurrence and skipped — the repair half of the same blind spot
            # `classify` had.  Right-to-left so earlier offsets stay valid.
            hit = False
            for m2 in reversed(list(re.finditer(
                    re.escape(op) + r"(?![\w'ˡʳ-])", lines[i]))):
                before = lines[i][:m2.start()].rstrip()
                if before and re.search(r"[\w'ˡʳ)\]}]$", before):
                    continue                      # has a left operand: not this one
                lines[i] = lines[i][:m2.start()] + bare + lines[i][m2.end():]
                hit = True
            if not hit:
                continue
            done.append(ln)
        if done:
            print(f"   {'fix ' if apply else 'would'}  "
                  f"{os.path.relpath(path, ROOT)}  lines {sorted(done)}")
            n += len(done)
            if apply:
                open(path, "w", encoding="utf-8").write("\n".join(lines))
    return n


def _selftest():
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # ⚑ THE MEASURED SHAPE, verbatim from `Algebra/Z/ZeroInt.agda` — an infixl
        # operator with nothing to its left.  This is the case the two text
        # heuristics could not decide and the compiler states outright.
        log = os.path.join(td, "a.agdai.log")
        open(log, "w", encoding="utf-8").write(
            "/x/ZeroInt.agda:24.6-10: error: [NoParseForApplication]\n"
            "Could not parse the application ℕ+ 0\n"
            "Operators used in the grammar:\n"
            "  ℕ+ (infixl operator, level 6) [_ℕ+_ (/x/Plus.agda:18.1-5)]\n"
            "when scope checking ℕ+ 0\n")
        rows = classify(log)
        check("a NoParse block is read at all", len(rows), 1)
        check("an infix operator with NO left operand is the FIXITY class",
              rows[0][4], "fixity")
        check("...and the operator is reported", rows[0][3], "ℕ+")

        # ⚑ A GENUINE PRECEDENCE ERROR IS NOT OUR CLASS.  Repairing it would change
        # what the term means, so it is reported and left alone — the same refusal
        # `fix_notinscope` makes on an ambiguous name.
        log2 = os.path.join(td, "b.agdai.log")
        open(log2, "w", encoding="utf-8").write(
            "/x/B.agda:9.1-9: error: [NoParseForApplication]\n"
            "Could not parse the application a ⊗ b ⊗ c\n"
            "Operators used in the grammar:\n"
            "  ⊗ (infix operator, level 5) [_⊗_ (/x/T.agda:3.1-3)]\n")
        check("an operator WITH a left operand is not the fixity class",
              classify(log2)[0][4], "other")

        # ⚑⚑ TRAILING POSITION IS THE SAME DEFECT (Ⓣ22).  MEASURED on
        # `Z/Properties/MulFull.agda:59` — `(+ 0) *ℤ x ≡ ℕ+ 0`, where `--at`
        # proves the source read `≡ + 0` before the `_+_`→`_ℕ+_` rename.  The
        # first-position test returned `other` and the remedy refused its own
        # class, so the site was fixed by hand three times in one turn.
        log3 = os.path.join(td, "c.agdai.log")
        open(log3, "w", encoding="utf-8").write(
            "/x/MulFull.agda:59.22-39: error: [NoParseForApplication]\n"
            "Could not parse the application (+ 0) *ℤ x ≡ ℕ+ 0\n"
            "Operators used in the grammar:\n"
            "  ℕ+ (infixl operator, level 6) [_ℕ+_ (/x/Plus.agda:18.1-5)]\n")
        check("an infix operator with no left operand AFTER an operator is FIXITY",
              classify(log3)[0][4], "fixity")

        # ⚑ AND THE REFUSAL CASE MUST SURVIVE THE WIDENING.  `a ⊗ b ⊗ c` is a
        # genuine precedence error: the second `⊗`'s left neighbour is the TERM
        # `b`, so "nothing to its left" is still false.  This is the case that
        # killed the FIRST loose arm; if widening breaks it, the widening is
        # wrong rather than the case.
        check("a precedence error survives the trailing-position widening",
              classify(log2)[0][4], "other")

        # ⚑⚑ THE REPORTED OPERATOR IS THE ONE THAT DECIDED THE VERDICT, NOT THE
        # FIRST IN AGDA'S GRAMMAR LIST.  MEASURED on `Q/JacobianEvalCD.agda:316`:
        # agda lists `*ℤ` first, the displaced operator is `ℕ+`, and returning
        # `ops[0][0]` handed `repair` a name that appears on the line WITH a left
        # operand — so the tool reported `1 fixity site, 0 repairable`, refusing
        # its own class while the verdict was correct.  A classifier that names
        # the wrong subject is worse than one that refuses: the two halves
        # disagree SILENTLY.
        log4 = os.path.join(td, "d.agdai.log")
        open(log4, "w", encoding="utf-8").write(
            "/x/Eval.agda:316.14-79: error: [NoParseForApplication]\n"
            "Could not parse the application p *ℤ (q) ≡ ℕ+ Dden\n"
            "Operators used in the grammar:\n"
            "  *ℤ (infixl operator, level 7) [_*ℤ_ (/x/Mul.agda:24.1-5)]\n"
            "  ℕ+ (infixl operator, level 6) [_ℕ+_ (/x/Plus.agda:18.1-5)]\n")
        _r4 = classify(log4)[0]
        check("the verdict is fixity when a LATER operator is displaced",
              _r4[4], "fixity")
        check("...and the operator reported is the DISPLACED one, not agda's first",
              _r4[3], "ℕ+")

        # ⚑ A DIRECTORY OF PER-MODULE LOGS IS THE PREFERRED INPUT (interleave-proof).
        check("a directory of logs is walked", len(classify(td)), 4)

        # ⚑ REPAIR TOUCHES ONLY A SITE WITH NO LEFT OPERAND, even on a line that
        # carries the operator twice — the `Hilbert2D` shape, which COMPILES and
        # must not be rewritten.
        src = os.path.join(td, "Z.agda")
        open(src, "w", encoding="utf-8").write(
            "0ℤ = ℕ+ 0\nq = a ℕ+ b\nz : x ≡ ℕ+ 0\nw = cong (λ z → ℕ+ suc z) p\n")
        n = repair([(src, 1, 6, "ℕ+", "fixity"),
                    (src, 2, 7, "ℕ+", "fixity"),
                    (src, 3, 9, "ℕ+", "fixity"),
                    (src, 4, 18, "ℕ+", "fixity")], apply=True)
        body = open(src, encoding="utf-8").read()
        check("the prefix site is restored", "0ℤ = + 0" in body, True)
        check("...and the INFIX site with a left operand is untouched",
              "a ℕ+ b" in body, True)
        # ⚑ THE TWO MEASURED TRAILING SHAPES: after an operator, and inside a
        # lambda body.  Both are the `+_` constructor the rename displaced.
        check("a prefix site AFTER an operator is restored",
              "x ≡ + 0" in body, True)
        check("a prefix site inside a lambda is restored",
              "(λ z → + suc z)" in body, True)
        check("only the repairable sites counted", n, 3)

    ok = sum(1 for _n, g, _got, _w in cases if g)
    for n, g, got, w in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {w!r}")
    print(f"fix_noparse selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    # ⚑ argv[0] IS A LOG, NOT A TARGET.  The files this rewrites are whatever
    # `classify` resolves out of it, so the classification runs first and its
    # paths are what the snapshot must cover; keying on argv would copy the log.
    # ⚑ ONE ACT, and BEFORE the apply/dry decision reaches `repair`.
    # `_snapshot_once` inside `repair` is guarded on `apply and by_file`, so a run
    # that classifies every row as `other` never reaches it.
    rows = classify(args[0])
    import edit_snapshot as _es
    _es.require_at_entry("fix_noparse", paths=sorted({r[0] for r in rows}))
    fixity = [r for r in rows if r[4] == "fixity"]
    other = [r for r in rows if r[4] != "fixity"]
    n = repair(rows, apply="--apply" in sys.argv)
    for path, ln, _c, op, _v in other:
        print(f"   ? {os.path.relpath(path, ROOT)}:{ln}  `{op}` — not a fixity "
              f"collision; a precedence fix would change what the term MEANS")
    print(f"\nfix_noparse: {n} of {len(fixity)} fixity site(s) "
          f"{'repaired' if '--apply' in sys.argv else 'repairable'}, "
          f"{len(other)} other [NoParseForApplication] left alone"
          + ("" if "--apply" in sys.argv else "  (dry run — pass --apply)"))
