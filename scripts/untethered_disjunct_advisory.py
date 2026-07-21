#!/usr/bin/env python3
"""untethered_disjunct_advisory.py — UN-TETHERED ⊎-DISJUNCT ADVISORY (post-commit).

THE PATTERN. A `⊎`-valued signature is VACUOUS when one disjunct does not mention
the data being classified — it can then be discharged unconditionally, and the
`⊎` carries no information. Two real instances found in this tree:

  prove-or-correct : {A : Set} (T : TorsorAtom A) → … → (g : A)
                   → (g ≡ e T) ⊎ FixedPointFree A
      right disjunct never mentions `g`; `ℕ-residue-fpf 0` (ResidueAtom.agda:83)
      discharges it for every g. So `prove-or-correct`'s own codomain is vacuous
      at A := ℕ, and anything routed through it INHERITS that.

  seam-cover-spec  : (t : EEATrace a b 1) (x : RealTrace)
                   → (digits-of-EEA t ≡ take (cf-length t) x) ⊎ (x ~ ana out x)
      right disjunct never mentions `t`; `self-unfold x` (Final.agda:116)
      discharges it. Verified by construction before this script was written.

THE RULE IMPLEMENTED (syntactic, deliberately conservative). For the LAST
top-level `→` component, split on top-level `⊎`. Collect the names bound in the
signature's telescope. For each disjunct compute which bound names it mentions.
If the mention-sets are UNEQUAL, flag: the disjunct with the smaller set is not
tethered to everything its sibling classifies.

  P ⊎ ¬ P                    → sets equal      → clean (the tethered dichotomy)
  (g ≡ zero) ⊎ (g ≡ zero → ⊥) → both mention g  → clean (ℕ-zero?)
  (g ≡ e T) ⊎ FixedPointFree A → {g,T} vs {A}   → FLAGGED

HONEST SCOPE — this is a SYNTACTIC approximation of a TYPE-LEVEL property, so it
is ADVISORY (prints, never blocks), matching tautology_advisory.py. It will
over-flag: a disjunct may legitimately depend on fewer inputs. It will also
under-flag: a disjunct can mention every binder and still be provable for all of
them (`x ~ ana out x` mentions x, and is caught here only because it misses `t`).
NEITHER DIRECTION IS COMPLETE. The real check remains a non-vacuity POLE shipped
as a typechecked term — a refutation of each disjunct at a concrete index, the
`Contentful`/`contentful→¬vacuous` idiom (Category/UniversalProperty/Vacuity.agda:
44-59, poles at :74-79). This script only surfaces candidates for that work.

Neither existing gate covers this: tautology_advisory.py tests textual `X ≡ X`
only; check_up_nonvacuity.sh greps only `Witness = λ _ _ → ⊤`.
"""
import re, sys, glob, os

ALLOW = {  # verified-intentional asymmetric disjuncts (name → why)
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

IDENT = re.compile(r"[A-Za-z_][\w'₀-₉ᴬ-ᵿ⟦⟧-]*")

def binders_of(ty):
    """Names bound in the telescope: the `x y` of every `(x y : T)` / `{x y : T}`."""
    names = set()
    for m in re.finditer(r"[({]\s*([^:(){}]*?)\s*:", ty):
        for w in m.group(1).split():
            if IDENT.fullmatch(w):
                names.add(w)
    return names

def mentions(disjunct, names):
    toks = set(IDENT.findall(disjunct))
    return names & toks

def check(ty):
    """Return (disjuncts, mention-sets) if the ⊎-mention-sets are unequal, else None."""
    prop = split_top(ty, "→")[-1].strip()
    parts = [p.strip() for p in split_top(prop, "⊎")]
    if len(parts) < 2 or any(p == "" for p in parts):
        return None
    names = binders_of(ty)
    if not names:
        return None
    sets = [mentions(p, names) for p in parts]
    if all(s == sets[0] for s in sets):
        return None
    return parts, sets

quiet = "--quiet" in sys.argv
paths = [a for a in sys.argv[1:] if not a.startswith("--")] or ["agda/Substrate"]
files = []
for p in paths:
    files += glob.glob(os.path.join(p, "**", "*.agda"), recursive=True) if os.path.isdir(p) else [p]

hits = []
for f in sorted(files):
    try:
        src = strip_comments(open(f, encoding="utf-8").read())
    except OSError:
        continue
    for name, ty in sigs_of(src):
        if name in ALLOW:
            continue
        r = check(ty)
        if r:
            hits.append((f, name, r[0], r[1]))

if not quiet:
    for f, name, parts, sets in hits:
        rel = os.path.relpath(f)
        small = min(range(len(sets)), key=lambda i: len(sets[i]))
        print(f"  UNTETHERED-⊎ {rel}: {name}")
        for i, (p, s) in enumerate(zip(parts, sets)):
            mark = " <-- mentions fewest" if i == small else ""
            print(f"      disjunct {i}: {p.strip()[:88]}")
            print(f"        mentions {sorted(s) if s else '{}'}{mark}")
print(f"untethered-⊎ advisory: {len(hits)} asymmetric ⊎-signature(s) "
      f"({len(ALLOW)} allowlisted). ADVISORY — never blocks; a real non-vacuity "
      f"check is a refutation POLE shipped as a term.")
sys.exit(0)
