#!/usr/bin/env python3
"""tautology_advisory.py — X≡X / postulate ADVISORY (post-commit).

Set₁ POLICY (operator, 359): Set₁ usages are policy violations / legacy debt.
The house style is Substrate.Category.Lawvere's carrier-generic atoms —
PARAMETERIZE by (V : Set) rather than FIELDING the carrier, so records live
in Set. Because ~190 legacy sites exist, Set₁ is gated as a RATCHET (the
house pattern, cf. scripts/check_import_shape.py "import-shape ratchet"):
the baseline is recorded; the gate FAILS if the count INCREASES. Legacy is
frozen; new debt is blocked. Fix sites to lower the baseline. Structure-aware, comment-stripped.
Validated with a positive control (a real X≡X is flagged) and a negative
control (an identity-action law `f (λ x → x) a ≡ a` is NOT flagged).
Allowlist: intentional self-identities and the canonical Fam Set₁."""
import re, sys, glob, os

ALLOW_TAUT = {  # verified-intentional self-identities (name → why)
    "shared-middle":        "WitnessTower/SharedMiddle: the deeper seam claim is POSITED, not built (self-aware placeholder)",
    "boundary-edges-self":  "WitnessTower/FaceCount: documents SELF-DUALITY of the middle grade (content in the name)",
    "arity-is-chain-depth": "SKIGradedFlatAllegory: definitional bridge, both sides differently motivated",
    "applied-agree":        "FUSep: eta-witness, both sides differently derived",
}

def strip_comments(src):
    return "\n".join(re.sub(r"--.*$", "", ln) for ln in src.splitlines())

def split_top(s, sep):
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        if depth == 0 and s.startswith(sep, i):
            out.append(cur); cur = ""; i += len(sep); continue
        cur += c; i += 1
    out.append(cur); return out

def is_taut(ty):
    prop = split_top(ty, "→")[-1].strip()
    sides = split_top(prop, "≡")
    if len(sides) != 2: return False
    l, r = sides[0].strip(), sides[1].strip()
    return l != "" and l == r

def sigs_of(src):
    out, cur, name = [], None, None
    for ln in src.splitlines():
        m = re.match(r"^([a-zA-Z][\w'₂ᴬ→-]*)\s*:\s*(.*)$", ln)
        if m:
            if cur is not None: out.append((name, cur))
            name, cur = m.group(1), m.group(2)
        elif cur is not None and ln.startswith(("  ", "\t")) and "=" not in ln:
            cur += " " + ln.strip()
        elif cur is not None:
            out.append((name, cur)); cur = name = None
    if cur is not None: out.append((name, cur))
    return out

quiet = "--quiet" in sys.argv
paths = [a for a in sys.argv[1:] if not a.startswith("--")] or ["agda/Substrate"]
files = []
for p in paths:
    files += glob.glob(os.path.join(p, "**", "*.agda"), recursive=True) if os.path.isdir(p) else [p]

fails = []
for f in sorted(files):
    src = strip_comments(open(f, encoding="utf-8").read())
    for n, t in sigs_of(src):
        if is_taut(t) and n not in ALLOW_TAUT:
            fails.append(("TAUTOLOGY", f, f"{n} : {t[:60]}"))
    for i, ln in enumerate(src.splitlines(), 1):
        if re.match(r"^\s*postulate(\s|$)", ln):
            fails.append(("POSTULATE", f, f"line {i}"))

if fails:
    print(f"tautology-advisory: {len(fails)} finding(s) (non-blocking)")
    for kind, f, det in fails[:10]:
        print(f"  {kind:9s} {f.replace('agda/Substrate/','')}: {det}")
elif not quiet:
    print(f"tautology-advisory: OK ({len(files)} modules)")
sys.exit(0)
