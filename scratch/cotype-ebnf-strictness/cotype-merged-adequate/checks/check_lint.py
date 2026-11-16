#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_lint.py — [AI-CHECK-LINT] made runnable. Sibling to shared_rep_lint.py.

THE INVARIANT (from regrounding #2's retro G4-P3): six failure-patterns recur because each is a check or
registration that PASSES under the invocation path the author tested but FAILS under the path the gate uses
(import-time vs script-time; plain vs --without-K; own-claim vs shared-warrant grep). The lessons were banked as
PROSE, not enforced. This lint converts them to detectors so the next occurrence is caught mechanically.

THE SIX PATTERNS (two kinds):
  DETERMINISTIC (definite bugs -> also enforced by the gate meta-check f090_2_check_lint_clean):
    P1 registration-after-__main__ : a `def f090_2_*` or `CLAIMS["f090_2_*"]=` placed AFTER `if __name__`. When
        run as a script the module exits at the guard before reaching it -> the CLI (and thus the gate, which
        shells to the CLI) cannot see the check, while a direct import can. The import/script split is the bug.
    P2 shared-check        : two warrants whose check={claim:X} name the SAME X. Fails --without-K proof-relevance
        (every cited claim needs a DISTINCT check). A warrant sharing another's check is not independently gated.
    P6 litplace-orphan     : a *_litplace warrant whose check points at a DIFFERENT warrant's claim (a subcase of
        P2 specific to narrative/placement warrants, which must carry their OWN non-vacuous check).
  HEURISTIC (suspects, worklist only -- true and false positives, like shared_rep_lint):
    P3 foreign-grep        : a check that calls _claim("Y") for some Y != its own name and does NOT also _claim
        its own key. Prose-weak for any clause in its OWN claim (the aspf_godel bug). May be legitimate when the
        check is genuinely about the foreign warrant -> SURFACE, do not hard-fail.
    P4 flatten-to-yield    : a forest/semiring OTIMES in a *_ref.py that concatenates/flattens to a yield instead
        of pairing trees (the span-DP forest-collapse bug). Heuristic syntactic signal; surface for inspection.
    P5 prose-gut-survivor  : a check that passes when its warrant prose is gutted = shared_rep_lint's
        prose-sensitive axis. SUBSUMED by shared_rep_lint; not re-run here, only cross-referenced.

HONEST SCOPE (the G8 caveat, inherited): P1/P2/P6 are deterministic and certifiable (they are structural facts
of the files). P3/P4 are SUSPECTS -- a clean P3/P4 result is absence-of-this-evidence, not proof of faithfulness;
the external arm ([AI-FAITHFULNESS-AUDIT], USER/Q/Δ0) is the certifier. This lint is the audit's FIRST PASS.

USAGE: python3 check_lint.py            (report all patterns)
EXIT:  0 iff no DETERMINISTIC pattern (P1/P2/P6) fires; 1 otherwise. Heuristic hits (P3/P4) are printed as a
       worklist but do NOT change the exit code (they need human judgement, not a gate-fail).
"""
import sys, os, re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CHECKS = os.path.join(ROOT, "checks", "claims.py")
WARRANTS = os.path.join(ROOT, "warrants.bib")


def _load():
    return open(CHECKS).read(), open(WARRANTS).read()


def p1_registration_after_main(claims):
    """DETERMINISTIC. defs / CLAIMS registrations after the first `if __name__` guard."""
    i = claims.find('if __name__ == "__main__":')
    if i < 0:
        return []
    after = claims[i:]
    defs = re.findall(r'\ndef (f090_2_\w+)\(\):', after)
    regs = re.findall(r'\nCLAIMS\["(f090_2_\w+)"\]', after)
    return [("def", d) for d in defs] + [("reg", r) for r in regs]


def p2_shared_check(bib):
    """DETERMINISTIC. check={claim:X} naming the same X for >1 warrant."""
    used = re.findall(r'check\s*=\s*\{claim:(f090_2_\w+)\}', bib)
    return {k: v for k, v in Counter(used).items() if v > 1}


def p6_litplace_orphan(bib):
    """DETERMINISTIC. a *_litplace warrant whose check points at a foreign claim."""
    out = []
    for lp in re.findall(r'@misc\{(f090_2_\w*litplace\w*),', bib):
        m = re.search(r'@misc\{' + lp + r',.*?check\s*=\s*\{claim:(f090_2_\w+)\}', bib, re.S)
        if m and m.group(1) != lp:
            out.append((lp, m.group(1)))
    return out


def p3_foreign_grep(claims):
    """HEURISTIC. a check that _claim()s a foreign key and not its own."""
    out = []
    for name, body in re.findall(r'\ndef (f090_2_\w+)\(\):(.*?)(?=\ndef |\nCLAIMS\[)', claims, re.S):
        args = re.findall(r'_claim\(\s*["\'](f090_2_\w+)["\']\s*\)', body)
        if args and name not in args:
            out.append((name, args))
    return out


def p4_flatten_to_yield(refdir):
    """HEURISTIC. a forest/semiring OTIMES that concatenates instead of pairing (syntactic signal)."""
    out = []
    for fn in os.listdir(refdir):
        if not fn.endswith("_ref.py"):
            continue
        src = open(os.path.join(refdir, fn)).read()
        # signal: an otimes/pair function whose body uses tuple concatenation (a + b) over comprehension of
        # leaf-spans rather than pairing structured nodes. Heuristic: 'a + b for a in A for b in B' inside a
        # function whose name or context mentions forest/otimes/pair/derivation.
        for m in re.finditer(r'def (\w*(?:otimes|pair|forest|combine)\w*)\([^)]*\):(.*?)(?=\n    def |\ndef |\Z)', src, re.S):
            fname, fbody = m.group(1), m.group(2)
            if re.search(r'\ba\s*\+\s*b\s+for\b', fbody) and 'tree' not in fbody.lower():
                out.append((fn, fname))
    return out



def p8_conformance_mismatch(refdir):
    """DETERMINISTIC. A ref whose docstring declares it CONFORMS TO another ref must produce IDENTICAL outputs to
    that ref for the ops it claims to conform on. Keyed on the DECLARED conformance contract (the phrase
    "Conforms to <other>.<op>"), NOT on shared op-names -- so genuinely-distinct algebras that merely share an
    op name (e.g. gf2_hinge_ref._or Boolean vs nedge_ref.g_or conductance) are NOT flagged. This is the detector
    that would have caught the Nedge [0,1]-vs-[0,inf] mis-model: paraconsistent_ref declares "Conforms to
    nedge_ref.g_not/.g_or/.g_and" and must match nedge_ref on shared inputs."""
    import importlib.util, os
    from fractions import Fraction as Q
    def load(name):
        spec = importlib.util.spec_from_file_location("lint_"+name, os.path.join(refdir, name+".py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    # test inputs valid across the conformance families we have (rationals for the conductance algebra)
    unary = [Q(2), Q(9), Q(1,4), Q(7,3)]
    binary = [(Q(2),Q(3)), (Q(9),Q(1,4)), (Q(5),Q(5)), (Q(1),Q(7))]
    out = []
    for fn in sorted(os.listdir(refdir)):
        if not fn.endswith("_ref.py"):
            continue
        src = open(os.path.join(refdir, fn)).read()
        name = fn[:-3]
        # find per-op conformance declarations: "Conforms to <other_ref>.<op>"
        decls = re.findall(r'[Cc]onforms?\s+to\s+(\w+_ref)\.(\w+)', src)
        if not decls:
            continue
        try:
            me = load(name)
        except Exception as e:
            out.append((name, "?", f"could not load: {e}")); continue
        for other_ref, op in decls:
            try:
                them = load(other_ref)
            except Exception as e:
                out.append((name, other_ref, f"target {other_ref} unloadable: {e}")); continue
            f_me = getattr(me, op, None); f_them = getattr(them, op, None)
            if f_me is None or f_them is None:
                continue   # op not actually present under that name; not a conformance failure
            # try unary then binary signature
            for args_list in (unary, binary):
                for args in args_list:
                    a = args if isinstance(args, tuple) else (args,)
                    try:
                        r_me, r_them = f_me(*a), f_them(*a)
                    except TypeError:
                        break   # wrong arity for this list; try the other
                    except Exception:
                        continue
                    if r_me != r_them:
                        out.append((name, f"{other_ref}.{op}", f"output mismatch on {a}: {r_me} != {r_them}"))
                        break
                else:
                    continue
                break
    return out


def p7_label_source_mismatch(bib):
    """HEURISTIC. A warrant whose AI-CORPUS-WIDER batch-tag names a SOURCE-FAMILY mentioned NOWHERE in its own
    grounding text NOR in any warrant it depends on (`from`) -- the EL-Atlas mislabel (tag 'EL-Atlas', the whole
    cluster grounds 'Nedge'). Checking the from-closure (not just the warrant's own body) avoids false positives
    on derived warrants that inherit the source from an anchor warrant. Only checks tags naming a source (not
    generic 'batch'/'edge'). Proper-noun matching is fuzzy -> worklist, not gate-fail."""
    generic = {"batch", "edge", "edge-a", "edge-b"}
    # index every warrant's body + from-list
    blocks = {}
    for m in re.finditer(r'@misc\{(f090_2_\w+),(.*?)\n\}', bib, re.S):
        name, block = m.group(1), m.group(2)
        claim = re.search(r'claim\s*=\s*\{(.*?)\},\s*\n\s*check', block, re.S)
        body = re.sub(r'AI-CORPUS-WIDER\s+[A-Za-z][A-Za-z0-9-]*', '', claim.group(1) if claim else block).lower()
        fr = re.search(r'\bfrom\s*=\s*\{([^}]*)\}', block)
        froms = [a for a in re.split(r'[,\s]+', fr.group(1)) if a] if fr else []
        tag = re.search(r'AI-CORPUS-WIDER\s+([A-Za-z][A-Za-z0-9-]*)', block)
        blocks[name] = (body, froms, tag.group(1) if tag else None)
    out = []
    for name, (body, froms, batch) in blocks.items():
        if not batch or batch.lower() in generic:
            continue
        token = batch.split("-")[0].lower()
        # search the from-closure: this warrant's body + every ancestor's body (bounded walk). STEM match
        # (left boundary only) so a batch stem like 'crypto' matches 'cryptographic' -- batch tags often name the
        # source by a stem, not the exact word. A genuinely-absent source still fails (the EL-Atlas mislabel: no
        # 'el'-stem word in a Nedge grounding).
        stem = r'\b' + re.escape(token)
        seen, stack, found = set(), list(froms), bool(re.search(stem, body))
        while stack and not found:
            a = stack.pop()
            if a in seen or a not in blocks:
                continue
            seen.add(a)
            abody, afroms, _ = blocks[a]
            if re.search(stem, abody):
                found = True
            stack.extend(afroms)
        if not found:
            out.append((name, batch, f"tag names '{batch}' but neither it nor its from-closure mentions '{token}'"))
    return out


def main(argv):
    claims, bib = _load()
    refdir = os.path.join(ROOT, "witnesses")

    p1 = p1_registration_after_main(claims)
    p2 = p2_shared_check(bib)
    p6 = p6_litplace_orphan(bib)
    p3 = p3_foreign_grep(claims)
    p4 = p4_flatten_to_yield(refdir)
    p7 = p7_label_source_mismatch(bib)
    p8 = p8_conformance_mismatch(refdir)

    print("# [AI-CHECK-LINT] — path-dependent-validity patterns (sibling to shared_rep_lint)")
    print("# DETERMINISTIC P1/P2/P6/P8 set the exit code; HEURISTIC P3/P4/P7 are a worklist for the external arm.\n")

    det_fail = False
    print("## DETERMINISTIC (gate-enforced):")
    if p1:
        det_fail = True
        print(f"  P1 registration-after-__main__: {p1}  <-- BUG (CLI/gate cannot see these)")
    else:
        print("  P1 registration-after-__main__: clean")
    if p2:
        det_fail = True
        print(f"  P2 shared check={{claim:X}}: {p2}  <-- BUG (fails --without-K proof-relevance)")
    else:
        print("  P2 shared check: clean")
    if p6:
        det_fail = True
        print(f"  P6 litplace-orphan (no own check): {p6}  <-- BUG (placement must carry its own check)")
    else:
        print("  P6 litplace-orphan: clean")
    if p8:
        det_fail = True
        print(f"  P8 conformance-mismatch: {p8}  <-- BUG (a ref declares CONFORMS TO another but outputs differ)")
    else:
        print("  P8 conformance-mismatch: clean")

    print("\n## HEURISTIC (worklist; needs judgement, does NOT fail the gate):")
    if p3:
        print(f"  P3 foreign-grep ({len(p3)}): each greps a shared warrant, not its own claim -> prose-weak for")
        print("     any clause in its OWN claim. Legitimate iff the check is genuinely ABOUT the foreign warrant.")
        for n, a in p3:
            print(f"       {n} -> _claim{tuple(a)} (no own _claim)  [inspect: bind own claim or confirm intent]")
    else:
        print("  P3 foreign-grep: clean")
    if p4:
        print(f"  P4 flatten-to-yield ({len(p4)}): an OTIMES/pair that concatenates -- may collapse structure.")
        for fn, fname in p4:
            print(f"       {fn}:{fname}  [inspect: does it pair TREES or flatten to yield?]")
    else:
        print("  P4 flatten-to-yield: clean")
    if p7:
        print(f"  P7 label-source-mismatch ({len(p7)}): batch-tag names a source absent from the grounding text.")
        for n, b, why in p7:
            print(f"       {n}: {why}  [inspect: fix the tag or confirm the source]")
    else:
        print("  P7 label-source-mismatch: clean")
    print("  P5 prose-gut-survivor: delegated to shared_rep_lint.py (the prose-sensitive axis).")

    print(f"\n# DETERMINISTIC result: {'FAIL' if det_fail else 'clean'}; "
          f"HEURISTIC worklist: {len(p3)} foreign-grep, {len(p4)} flatten, {len(p7)} label-mismatch. "
          f"(Heuristic hits are absence-of-evidence when clean, not proof -- the external arm certifies.)")
    return 1 if det_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
