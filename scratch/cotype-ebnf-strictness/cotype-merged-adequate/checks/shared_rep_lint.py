#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""shared_rep_lint.py — [AI-SHARED-REP] made runnable (the standing lens as an instrument).

THE INVARIANT (from the register): a distinction A vs B is real iff the two sides CAN DISAGREE; a shared
representation makes them unable to disagree, so the check is a disguise. This lint mechanically asks, for
every check: under what corruptions does it flip? A check that flips under NEITHER prose- nor code-corruption
shares a representation with what it grades and cannot see past it.

TWO AXES (the grade-honesty finding):
  prose-sensitive : corrupt the warrant PROSE -> does the check flip? (is the warrant text load-bearing?)
  code-coupled    : does the check compute against a reference / independent route? (can wrong CODE be caught?)

HONEST SCOPE (the G8 caveat, respected): this lint SURFACES suspects; it does NOT certify. A self-pass cannot
reliably detect its OWN shared representations -- the thing it would check against is the thing it authored.
So a GREEN here means "no shared-rep detected by THIS corruption set", never "witnessed independent". The
output is a worklist for the external arm (USER/Q/Δ0), not a verdict. New corruption mutators can be added;
absence of a flip is absence of THIS test's evidence, not proof.

USAGE: python3 shared_rep_lint.py [check_name ...]   (no args = all checks)
EXIT: 0 if every check is prose-sensitive AND code-coupled (the genuine floor); 1 if any suspect remains.
"""
import sys, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))   # the paper dir
CHECKS = os.path.join(ROOT, "checks", "claims.py")
WARRANTS = os.path.join(ROOT, "warrants.bib")

def _checknames():
    src = open(CHECKS).read()
    return re.findall(r'\ndef (f090_2_\w+)\(\):', src)

def _passes(chk):
    r = subprocess.run([sys.executable, "checks/claims.py", chk],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0

def _code_coupled(chk):
    """Does the check compute against a reference, an independent route, or a real symbolic derivation?
    (Syntactic signal -- a check with none of these cannot catch a wrong implementation.)"""
    src = open(CHECKS).read()
    body = re.search(r'def ' + chk + r'\(\):(.*?)(?=\ndef |\nCLAIMS)', src, re.S)
    if not body: return False
    b = body.group(1)
    return bool(re.search(r'_probe_ref\(|_probe\(|_mult_computed|_m2_nullity|matrix_rank|_exec_formula', b)) \
        or ('log(' in b and 'simplify' in b) \
        or ('expand(' in b and 'simplify' in b)

def _prose_sensitive(chk):
    """Corrupt this check's WARRANT PROSE to a structureless string; does the check flip pass->fail?
    True = the warrant text is load-bearing. None = no warrant prose found."""
    wb = open(WARRANTS).read()
    m = re.search(r'(@misc\{' + chk + r',.*?claim\s*=\s*\{)(.+?)(\},\s*\n\s*check)', wb, re.S)
    if not m: return None
    if not _passes(chk): return None            # only meaningful if baseline passes
    try:
        open(WARRANTS, "w").write(wb[:m.start(2)] + "CORRUPTED PROSE NO STRUCTURE" + wb[m.end(2):])
        return not _passes(chk)
    finally:
        open(WARRANTS, "w").write(wb)

def grade(ps, cc):
    if ps and cc:            return "2+", "prose-bound AND code-coupled (genuine floor; no shared-rep found by this test)"
    if ps and not cc:        return "1 ", "prose-only (keyword/value on prose; cannot catch wrong code)"
    if (ps is False) and cc: return "C ", "CODE-coupled but prose DECORATIVE (rigorous compute; warrant text unbound)"
    if ps is None:           return "? ", "no warrant prose / baseline not passing"
    return "0!", "NEITHER (corrupting prose does not flip; no reference computation) -- SUSPECT shared-rep"

def main(argv):
    names = argv or _checknames()
    suspects = []
    print(f"# [AI-SHARED-REP] lint — can each check's two sides disagree? ({len(names)} checks)")
    print(f"# axes: prose-sensitive x code-coupled.  '0!' and 'C' and '1' are worklist items, not failures of the math.")
    print(f"# HONEST SCOPE: surfaces suspects for the external arm; a clean result is absence-of-this-evidence, not proof.\n")
    for n in names:
        cc = _code_coupled(n)
        ps = _prose_sensitive(n)
        tag, desc = grade(ps, cc)
        print(f"  {tag}  {n:34} {desc}")
        if tag in ("0!", "1", "C", "? "):
            suspects.append((n, tag))
    print(f"\n# {len(names)-len(suspects)} at genuine floor (2+); {len(suspects)} worklist items.")
    if suspects:
        print("# worklist (specify the fix AI per item):")
        for n, t in suspects:
            fix = {"0!": "[AI-REGEX-TIGHTEN] or [AI-IDENTITY-AUDIT]", "1": "[AI-PROSE-BIND] add code coupling",
                   "C": "[AI-PROSE-REBIND] bind the warrant text", "? ": "inspect manually"}[t]
            print(f"#   {n}: {t} -> {fix}")
    return 0 if not suspects else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
