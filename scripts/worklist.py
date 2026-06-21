#!/usr/bin/env python3
"""worklist.py — mechanically-maintained thread status (registry-as-regenerator).

The open-threads worklist kept going STALE: done arcs stayed listed as "open" because their status was
a HAND-EDITED value, and a regrounding then re-dispatched completed work (△, FromImages, def/proof, Ι,
AsNamed all turned up done-but-listed-open in one session). The substrate's own discipline says: don't
store the answer, COMPUTE it from the evidence of the moment (navigator-not-the-answer;
registry-as-Π-not-markdown; judgement-is-demechanization). So status is never written down — it is
DERIVED from the tree every run, and cannot go stale by construction.

The only hand-authored part is the MANIFEST below: each item + a CHECKABLE done-predicate (a commit
subject, a defined lemma, an existing module, a linter that exits 0). Everything else is computed:

    scripts/worklist.py            # the live status table (DONE / OPEN / MANUAL)
    scripts/worklist.py --open     # only the not-done items (what to actually dispatch)
    scripts/worklist.py --md       # a markdown block (paste/generate into a record; never hand-edit)
    scripts/worklist.py --update   # REGENERATE the status block in the open_threads ledger (a command
                                   #   that updates the record — never hand-edit the block)
    scripts/worklist.py --check    # counts (a gate could run this)

Sibling of the `decomposition/` machinery (build_conversation_db / build_cotype_db → DB;
interpret_*_retrospective → REGENERATED markdown): records are produced by commands from durable
artifacts, never hand-maintained. This is the build-status analog over the git tree. The hand-authored
open_threads prose (what each item IS) stays; only its DONE/OPEN STATUS is mechanically regenerated.

Predicate atoms: ("commit", subj) git log has a matching commit · ("defines", relpath, name) an Agda
module defines `name` · ("exists", relpath) · ("grep", pat, relpath) · ("cmd0", shell) exits 0 ·
("manual",) human-judged (audits/sweeps with no machine artifact yet) · ("all"|"any", [atoms]).
A MANUAL item becomes mechanical the moment you give it an artifact predicate (e.g. its report exists).
"""
import os, sys, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AGDA = os.path.join(ROOT, "agda")

# ── the manifest: item + a CHECKABLE done-predicate (the only hand-authored part) ──
WORKLIST = [
    {"sym": "△", "desc": "⊢-arc truth-correction (antisymmetrize sq-zero / phantom postulate / Stab-not-normal)",
     "done": ("all", [("commit", "⊢-△"),
                      ("defines", "Substrate/Groups/StabNotNormal.agda", "StabD-not-normal"),
                      ("grep", "antisymmetrize-square-zero", "agda/Substrate/Category/TensorProduct/Antisymmetric.agda")])},
    {"sym": "Λ", "desc": "mediating-uniqueness via LimitUP.mediate-unique", "done": ("commit", "⊢-Λ")},
    {"sym": "Β", "desc": "bounded-solver via wedge-unique", "done": ("commit", "⊢-Β")},
    {"sym": "Ι", "desc": "NaturalIsomorphism + honest CartanRoot equivalence",
     "done": ("exists", "agda/Substrate/Category/NaturalIsomorphism.agda")},
    {"sym": "Φ", "desc": "coherence/factorization sideways-copy", "done": ("commit", "⊢-Φ")},
    {"sym": "Π", "desc": "prose-disclosure residue", "done": ("commit", "⊢-Π")},
    {"sym": "ŝ", "desc": "concrete-S₄ Stab-not-normal ⊥-witness (△-tail)",
     "done": ("defines", "Substrate/Groups/StabNotNormal.agda", "StabD-not-normal")},
    {"sym": "FromImages.seal", "desc": "seal linear-from-images opaque (fan-in 213 dense-linear family)",
     "done": ("all", [("grep", "opaque", "agda/Substrate/Algebra/F2/Linear/FromImages.agda"),
                      ("commit", "Seal linear-from-images")])},
    {"sym": "def/proof", "desc": "def/proof separation paydown (0 violations)",
     "done": ("cmd0", "bash scripts/check_def_proof_separation.sh --quiet")},
    {"sym": "NatTrans.AsNamed", "desc": "NaturalTransformation.AsNamed sibling",
     "done": ("exists", "agda/Substrate/Category/NaturalTransformation/AsNamed.agda")},
    {"sym": "Ⓤ", "desc": "jea IR→Python unparser: grade ladder + seam + template",
     "done": ("exists", "jea/metalanguage/jea_extrude_ir.py")},
    {"sym": "Ⓤ.split", "desc": "IR retraction as split-Canonical (Agda apex grounding)",
     "done": ("exists", "agda/Substrate/Algebra/Quotient/IRRetraction.agda")},
    {"sym": "Ⓣ", "desc": "trace-intern a Haskell/Core mutate-in-place machine",
     "done": ("exists", "jea/metalanguage/jea_haskell_trace.py")},
    {"sym": "Ⓡ.genlop", "desc": "genlop-style build-time ledger + ETA",
     "done": ("exists", "scripts/buildtime.py")},
    {"sym": "Ⓡ.autobudget", "desc": "size the membudget lease from peak-mem history",
     "done": ("grep", "_auto_mb", "scripts/membudget")},
    {"sym": "Ⓖ★→jea", "desc": "seam-partition synthesis relayed to AI-Π0",
     "done": ("exists", "jea/metalanguage/SEAM_PARTITION.md")},
    # ── genuinely open: audits/sweeps with no machine artifact yet (give them one and they go mechanical) ──
    {"sym": "Ω4", "desc": "reflex-sweep: analytic/transcendental scope-outs (verdict: reflex purged, 3 genuine deferrals)",
     "done": ("exists", "scratch/omega4_reflex_sweep.md")},
    {"sym": "Ε(b)", "desc": "widen the reuse-search trigger (G9 prevention)", "done": ("manual",)},
    {"sym": "Ω3-L-primes.pole1", "desc": "Ⓖ★ invertible-pole cross-coherence, rank-1: gᵏ·(recip g)ᵏ≈1 "
            "(gvalue-power-antipode) — the el-atlas antipode extended to the cyclic subgroup, NO FTA",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "gvalue-power-antipode")},
    {"sym": "Ω3-L-primes.rankN", "desc": "Ⓖ★ invertible-pole, rank-n: ∏gᵢ·∏hᵢ≈1 (prod-cancel) — the "
            "free abelian group on n G-value generators inverted termwise, NO FTA",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "prod-cancel")},
    {"sym": "Ω3-L-primes.zcodec", "desc": "full ℤ-power ExpLogCodec (ZPow.ℤ-power-codec): L=ℤ group via "
            "_+ℤ_, expL z=gᶻ, mixed-sign exp-⊕ — codec-antipode fires non-trivially through the interface, NO FTA",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "gvalue-ℤ-codec")},
    {"sym": "Ω3-L-primes.factor", "desc": "layer-2 foundation: factorization = the div-mod WEDGE iterated "
            "(Algebra.Nat.Prime: mod0→∣ wedge-with-r=0, IsPrime, Factored structure). Next: existence theorem",
     "done": ("defines", "Substrate/Algebra/Nat/Prime.agda", "Factored")},
    {"sym": "Ω3-L-primes.factor-exists", "desc": "factorization EXISTENCE: factorize! (every positive ℕ "
            "= a product of primes) — div-mod wedge iterated by least prime divisor, well-founded. = codec surjectivity onto ℚ₊",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "factorize!")},
    {"sym": "Ω3-L-primes.uniq", "desc": "uniqueness KERNEL: prime-divides-product (Euclid for primes, "
            "lifting the bezout-ℤ/EEA-trace `euclid` via gcd-pos+gcd-divides) + prime∣prime→≡ — the heart of FTA uniqueness",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "prime-divides-product")},
    {"sym": "Ω3-L-primes.u2", "desc": "uniqueness capstone: prime-∈-product (a prime dividing a product "
            "of primes IS one of them) + Foundation.List.Any/_∈_ homed; with existence this forces the prime multiset",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "prime-∈-product")},
    {"sym": "Ω3-L-primes.iso", "desc": "factorisation iso as split-Canonical: factor-Canonical "
            "(ℕ⁺ ≅ canonical prime factorisations, from the factorize! retraction product∘factorize≡id) — the split-idempotent apex, NO quotient type",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "factor-Canonical")},
    {"sym": "Ω3-L-primes.iso2", "desc": "the ⊕ STRUCTURE: product-++ (product is a monoid hom "
            "List/++/[] → ℕ/·/1 — concatenating factor lists multiplies = ADDING exponents). The additive side of the iso, ℕ⁺ level; the engine of LogSumExp",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "product-++")},
    {"sym": "Ω3-L-primes", "desc": "layer (1) FULLY DONE (.pole1/.rankN/.zcodec — rank-1+rank-n invertible poles + the ℤ-power codec interface, GValueLSpace.Primes, NO FTA); layer (2): EXISTENCE done (.factor/.factor-exists — Algebra.Nat.Prime.factorize!, every positive ℕ = ∏ primes, the div-mod wedge iterated = codec surjectivity onto ℚ₊). uniqueness KERNEL+capstone done (.uniq/.u2 — prime-divides-product + prime-∈-product, every prime factor ∈ any factorisation, via euclid; Foundation.List.Any homed). ℕ⁺ iso + ⊕-structure done (.iso/.iso2 — factor-Canonical bijection + product-++ monoid hom). REMAINING (Q-layer home, carrier-locality): ℚ₊-signed exponent-difference (num/den, ℤ exponents — reuses product-++) → L_OR=LogSumExp", "done": ("manual",)},
    {"sym": "Algebra↔Category", "desc": "ground the FLOATING modules on the Category spine (the recurring "
            "categorical-grounding advisory: GValueAsQ / M40Closure / M40Group) — or confirm proxy-noise",
     "done": ("manual",)},
]


def _git_has_commit(subj: str) -> bool:
    r = subprocess.run(["git", "-C", ROOT, "log", "--oneline", "-F", "--grep", subj],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def _defines(relpath: str, name: str) -> bool:
    p = relpath if os.path.isabs(relpath) else os.path.join(AGDA, relpath)
    try:
        with open(p) as f:
            for ln in f:
                s = ln.lstrip()
                if s.startswith(name) and len(s) > len(name) and s[len(name)] in " :":
                    return True
    except OSError:
        return False
    return False


def _grep(pat: str, relpath: str) -> bool:
    p = relpath if os.path.isabs(relpath) else os.path.join(ROOT, relpath)
    try:
        with open(p) as f:
            return pat in f.read()
    except OSError:
        return False


def _cmd0(cmd: str) -> bool:
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True).returncode == 0


def status(pred):
    """True = DONE, False = OPEN, None = MANUAL (human-judged, no machine artifact)."""
    t = pred[0]
    if t == "commit":  return _git_has_commit(pred[1])
    if t == "defines": return _defines(pred[1], pred[2])
    if t == "exists":  return os.path.exists(pred[1] if os.path.isabs(pred[1]) else os.path.join(ROOT, pred[1]))
    if t == "grep":    return _grep(pred[1], pred[2])
    if t == "cmd0":    return _cmd0(pred[1])
    if t == "manual":  return None
    if t == "all":
        rs = [status(p) for p in pred[1]]
        return False if any(r is False for r in rs) else (None if any(r is None for r in rs) else True)
    if t == "any":
        rs = [status(p) for p in pred[1]]
        return True if any(r is True for r in rs) else (None if any(r is None for r in rs) else False)
    return None


def rows():
    for it in WORKLIST:
        yield it["sym"], {True: "DONE", False: "OPEN", None: "MANUAL"}[status(it["done"])], it["desc"]


LEDGER = os.path.expanduser(
    "~/.claude/projects/-home-mikemol-github-substrate/memory/project_open_threads.md")
BEGIN, END = "<!-- worklist:auto BEGIN (regenerated by scripts/worklist.py --update; do not edit) -->", \
             "<!-- worklist:auto END -->"


def _md_block() -> str:
    lines = [BEGIN, "## Live status — DERIVED from the tree (run `scripts/worklist.py`; never hand-edit)",
             "", "| status | sym | item |", "|---|---|---|"]
    for s, st, d in rows():
        lines.append(f"| {'✅' if st=='DONE' else ('🔶' if st=='MANUAL' else '⬜')} {st} | `{s}` | {d} |")
    n = {k: sum(1 for _, st, _ in rows() if st == k) for k in ("DONE", "OPEN", "MANUAL")}
    lines += ["", f"_{n['DONE']} done · {n['OPEN']} open · {n['MANUAL']} manual (audits). "
                  f"Status is computed, not stored — a re-surfaced 'open' that is really done cannot occur._", END]
    return "\n".join(lines)


def _update_ledger(path: str) -> str:
    block = _md_block()
    try:
        with open(path) as f:
            txt = f.read()
    except OSError:
        return f"ledger not found: {path}"
    if BEGIN in txt and END in txt:
        pre, rest = txt.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        txt = pre + block + post
    else:                                              # insert the block right after the H1/intro
        nl = txt.find("\n\n")
        txt = (txt[:nl+2] + block + "\n\n" + txt[nl+2:]) if nl != -1 else (block + "\n\n" + txt)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(txt)
    os.replace(tmp, path)
    return f"regenerated worklist status block in {os.path.basename(path)}"


def main(argv) -> int:
    only_open = "--open" in argv
    as_md = "--md" in argv
    if "--update" in argv:
        i = argv.index("--update")
        path = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("-") else LEDGER
        print(_update_ledger(path))
        return 0
    if "--check" in argv:
        # a gate: every item whose predicate is a concrete artifact should still resolve; report MANUALs.
        bad = [s for s, st, _ in rows() if st == "OPEN" and WORKLIST[[i["sym"] for i in WORKLIST].index(s)]["done"][0] != "manual"]
        # (OPEN with an artifact predicate is legitimately not-done, not a regression — so --check only
        #  reports counts; the value is the DERIVED status itself never going stale.)
        n = {k: sum(1 for _, st, _ in rows() if st == k) for k in ("DONE", "OPEN", "MANUAL")}
        print(f"worklist: {n['DONE']} done, {n['OPEN']} open, {n['MANUAL']} manual (status derived from tree)")
        return 0
    out = [(s, st, d) for s, st, d in rows() if not (only_open and st == "DONE")]
    if as_md:
        print("| status | sym | item |\n|---|---|---|")
        for s, st, d in out:
            print(f"| {'✅' if st=='DONE' else ('🔶' if st=='MANUAL' else '⬜')} {st} | `{s}` | {d} |")
    else:
        for s, st, d in out:
            mark = {"DONE": "✅", "OPEN": "⬜", "MANUAL": "🔶"}[st]
            print(f"  {mark} {st:<6} {s:<16} {d}")
    n = {k: sum(1 for _, st, _ in rows() if st == k) for k in ("DONE", "OPEN", "MANUAL")}
    print(f"\n  {n['DONE']} done · {n['OPEN']} open · {n['MANUAL']} manual  (DERIVED from the tree — never hand-edited)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
