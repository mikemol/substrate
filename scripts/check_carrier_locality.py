#!/usr/bin/env python3
"""check_carrier_locality.py — canonical operators live in dedicated, carrier-local files.

POLICY (structural; prevents fork-by-reimplementation, e.g. the Q/Z `_+ℤ_` fork):
  A canonical ENDO operator — a mixfix name `_⊕_` whose type is `T → T → T`
  (or `T → T`) over a GLOBALLY-UNIQUE carrier T (a `data`/`record` declared
  exactly once in the tree) — must obey two rules:

    (1) LOCALITY  — it is defined in T's home: the file declaring T, or a file
                    under T's home directory subtree (e.g. an ℤ operator lives
                    under Algebra/Z/, never under Algebra/Q/).

    (2) DEDICATION — a file may host operators over a carrier IT DECLARES (the
                    `data ℕ` + `_+_`/`_*_` home file, named for the carrier).
                    But a file aggregating ≥2 operators over FOREIGN carriers
                    (declared elsewhere) is a generic bucket — the place forks
                    hide, where the file name no longer identifies what is
                    canonical (the old Arithmetic.agda). Those split one-per-file.

  Together these make the home of a canonical operator unambiguous and
  name-identified, so re-declaring it elsewhere is a hard error — the only
  option is to IMPORT it. Bucket files become re-export barrels.

  Uniqueness-gated: carriers whose NAME is reused locally (e.g. several modules
  each declare their own `Word`) are ambiguous and skipped — two
  `_·_ : Word → Word → Word` in different files are usually different `Word`s,
  not a fork. We judge only carriers with a single global declaration.

Blocking gate. Exit 0 = clean, 1 = offenders. Usage: check_carrier_locality.py [--quiet]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "agda", "Substrate")

# Sanctioned exceptions — "<relpath>::<op>", documented in
# scratch/carrier_locality_policy.md. These are pre-existing, cross-subsystem,
# and NOT forks (derived ops in a layered location; identity aliases; ops over
# a local type-synonym carrier). The gate blocks any NEW violation.
ALLOW = {
    # Derived ℕ arithmetic (mod/div) deliberately layered in Algebra/Nat/,
    # not re-implementations of a Foundation/Nat primitive.
    "agda/Substrate/Algebra/Nat/Mod.agda::_mod-suc_",
    "agda/Substrate/Algebra/Nat/DivMod/DivSuc.agda::_div-suc_",
    # `_·_` over a LOCAL `Word` type-synonym (Zn-Word × F-Word), distinct from
    # the Coxeter `Word`; and the canonical Coxeter `_·_` (= normalize ∘ ++),
    # historically in Core/Operations rather than under Word/.
    "agda/Substrate/Groups/Zn-x-FreeCyclic-PhaseProjection.agda::_·_",
    "agda/Substrate/Groups/Coxeter/Core/Operations.agda::_·_",
    # `_ℤ : ℤ → ℤ`, `n ℤ = n` — a local readability identity alias, not arithmetic.
    "agda/Substrate/Algebra/GL3F2/Characters.agda::_ℤ",
    # `_⊗ᴰ_` over DivStr — cross-construction wedge product, sited with the cross.
    "agda/Substrate/Algebra/Wedge/Cross.agda::_⊗ᴰ_",
    # The canonical Klein-four `_·_` over V₄: `data V₄` lives in Groups/V4/Bijection.agda
    # and its operation historically in the sibling Groups/V4/Operations.agda (the
    # substrate's carrier/op/axioms/bundle split for V₄) — NOT under Bijection/. Exactly
    # the grandfathered Coxeter `_·_` pattern above. Surfaced once Ⓒ.v4 unified the
    # scattered local `data V₄` copies onto this one, making V₄ a globally-unique carrier.
    "agda/Substrate/Groups/V4/Operations.agda::_·_",
    # `_+V₄_` over a LOCAL `V₄ = Bool × Bool` type-synonym (the F₂² additive form of the
    # affine V₄ subgroup) — name-conflated with the canonical `data V₄`, not the same
    # carrier and not a fork of its op (the type-synonym-carrier exemption).
    "agda/Substrate/Cocycles/V4Signature/Codeword/ReservedToBivectorAffine/V4.agda::_+V₄_",
}


def strip_comments(s):
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)
    s = re.sub(r"--[^\n]*", " ", s)
    return s


DECL = re.compile(r"^(?:data|record)\s+(\S+)")
SIG = re.compile(r"^(\S+)\s*:\s*(.+?)\s*$")


def agda_files():
    for dp, _, fs in os.walk(SRC):
        for f in sorted(fs):
            if f.endswith(".agda"):
                yield os.path.join(dp, f)


def split_top_arrows(t):
    parts, depth, cur = [], 0, ""
    for c in t:
        if c in "([{":
            depth += 1
            cur += c
        elif c in ")]}":
            depth -= 1
            cur += c
        elif c == "→" and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += c
    parts.append(cur.strip())
    return parts


def carrier_of(t):
    """Carrier T if the type is endo `T → T → T` / `T → T`, else None."""
    prev = None
    while t != prev:                              # strip leading implicit binders
        prev = t
        t = t.strip()
        if t.startswith("∀"):
            t = t[1:].strip()
        m = re.match(r"\{[^}]*\}\s*→(.*)$", t, flags=re.S)
        if m:
            t = m.group(1)
    parts = split_top_arrows(t)
    if len(parts) in (2, 3) and len(set(parts)) == 1 and parts[0]:
        return parts[0].split()[0]
    return None


def main():
    quiet = "--quiet" in sys.argv
    carrier_decls = {}                            # carrier -> set of decl files
    opsigs = []                                   # (op, carrier, file)
    for path in agda_files():
        with open(path, encoding="utf-8") as fh:
            src = strip_comments(fh.read())
        for line in src.splitlines():
            d = DECL.match(line)
            if d:
                carrier_decls.setdefault(d.group(1), set()).add(path)
            s = SIG.match(line)
            if s and "_" in s.group(1):
                T = carrier_of(s.group(2))
                if T is not None:
                    opsigs.append((s.group(1), T, path))

    unique = {c: next(iter(fs)) for c, fs in carrier_decls.items() if len(fs) == 1}

    # canonical endo operators over unique carriers
    canon = [(op, T, path) for op, T, path in opsigs if T in unique]

    locality = []                                 # (op, T, relpath)
    per_file = {}                                 # file -> [(op, T)]
    for op, T, path in canon:
        rel = os.path.relpath(path, ROOT)
        per_file.setdefault(path, []).append((op, T))
        home_file = unique[T]
        home_dir = home_file[:-5]
        ok = (path == home_file) or path.startswith(home_dir + os.sep)
        if not ok and f"{rel}::{op}" not in ALLOW:
            locality.append((op, T, rel))

    bucket = []                                    # (relpath, [ops])
    for path, ops in per_file.items():
        rel = os.path.relpath(path, ROOT)
        # exempt operators over a carrier this very file DECLARES (the carrier's
        # named home), and ALLOW-grandfathered ops.
        foreign = [(op, T) for op, T in ops
                   if path != unique[T] and f"{rel}::{op}" not in ALLOW]
        if len(foreign) >= 2:
            bucket.append((rel, foreign))

    if locality or bucket:
        if locality:
            print("carrier-locality: %d operator(s) defined outside their carrier's home:"
                  % len(locality))
            for op, T, rel in sorted(locality):
                home = os.path.relpath(unique[T], ROOT)[:-5]
                print(f"    {op}  (carrier {T}) in {rel}")
                print(f"                 → belongs under {home}/ ; import it instead.")
        if bucket:
            print("carrier-locality: %d bucket file(s) defining >1 canonical operator "
                  "(split one-per-file):" % len(bucket))
            for rel, ops in sorted(bucket):
                print(f"    {rel}: {', '.join(op for op, _ in ops)}")
        return 1
    if not quiet:
        print("carrier-locality: clean (%d unique carriers, %d canonical operators, "
              "%d grandfathered)." % (len(unique), len(canon), len(ALLOW)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
