#!/usr/bin/env python3
"""jea_oneforest.py — Σ-FOREST (Δ-Π-oneforest): the verification gate as a CrossMix readout.

Intern source + core + kernel into ONE forest, then the project's REASON falls out as a readout, not
a new mechanism (the recursive law: tiling and the cross-term are two FOLDS of one forest):
  * source↔core↔kernel CROSS-TERM = `CrossMix.cross_term` across the three arms' units = the
    VERIFICATION GATE (`gate`). Where a kernel/source unit and the proof-core unit are ORTHOGONAL
    (degree 0, same canonical node) the kernel REALIZES the proof; where they diverge, the graded
    obstruction + residue say BY HOW MUCH and WHERE -- exactly the "does this artifact faithfully
    realize the proven algorithm" question, answered structurally, not asserted. This is FIDELITY
    (precision): is each matched pair faithful.
  * the COMPLETENESS companion (`coverage`) closes the recall side the bare gate can't see: it walks
    BOTH arms and flags units with NO mirror above a shared-support floor (ORPHANS) on either side --
    a Python algorithm with no proof-core, or an Agda def no arm realizes. With an intended-correspondence
    `manifest` it checks each expected mirror is present AND faithful. Together: complete ∧ faithful.
  * tiling / metalanguage = the cohomology fold on a single arm (jea_pysim) -- a separate readout of
    the same forest (not built here; this module is the cross-arm gate).

ARCHITECTURE (the language-agnostic core, the part that runs ANYWHERE):
  a forest = one `Intern` + a set of named UNITS `(arm, qname, root)` from ANY front-ends that wrote
  into that Intern. The front-ends are environment-bound (libclang here, the Agda shim in the
  integrating session's env); the cross-term READOUT is NOT -- it is pure `CrossMix` over interned
  ids. So this module is verifiable on whichever arms' toolchains are present. In THIS repo that is Python
  (jea_pyalg) AND the AGDA-CORE arm via its REAL landed interface (`jea_agdai.core_intern_agdai`, Φ4):
  both RUN here (ghc+Agda present), no faked output. The CUDA arm (jea_cuda/libclang) is env-bound and
  ABSENT here; it composes by construction where that front-end exists -- NO rework, NO faked Agda output.

WHY no faked Agda arm: inventing shim output would be the invent-attributions error. The Agda arm is
ATTACHED by interface (add_arm consumes the documented {units:[(qname,root)]} shape that
core_intern_agdai returns) and EXERCISED by whoever has the toolchain. Here we prove the gate on the
two arms we can run, and the third composes by construction (same Intern, same unit shape)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, CrossMix, lower_source


class OneForest:
    """One Intern, units from multiple arms, the cross-term readout over them."""
    def __init__(self):
        self.I = Intern()
        self.arms: dict[str, list[tuple[str, int]]] = {}    # arm -> [(qname, interned_root), ...]
        self.cross = CrossMix(self.I)

    # ── front-end arms (each writes into the ONE shared Intern) ──────────────
    def add_python(self, arm: str, src: str, qname: str):
        root = lower_source(src, self.I)[0]
        self.arms.setdefault(arm, []).append((qname, root))
        return root

    def add_cuda(self, arm: str, src: str, qname: str):
        import jea_cuda
        # jea_cuda.lower_cuda interns into ITS own call; rebind it to ours by passing our Intern
        root = jea_cuda.lower_cuda(src, self.I)[0]
        self.arms.setdefault(arm, []).append((qname, root))
        return root

    def add_agda_core(self, arm: str, agdai_path: str, shim_bin: str | None = None):
        """The AGDA-CORE arm via the LANDED shim (jea_agdai.core_intern_agdai). Requires the compiled
        agdai_shim (ghc -package Agda) -- present in the integrating session's env, not necessarily here.
        Consumes the documented {units:[(qname,root)]} shape; drops in unchanged."""
        import jea_agdai
        res = jea_agdai.core_intern_agdai(agdai_path, self.I, shim_bin=shim_bin)
        self.arms.setdefault(arm, []).extend(res["units"])
        return res["units"]

    def add_units(self, arm: str, units: list[tuple[str, int]]):
        """Attach pre-interned units (e.g. a test double for an arm whose toolchain is absent). The
        roots MUST be ids in THIS forest's Intern."""
        self.arms.setdefault(arm, []).extend(units)

    # ── the readout: the cross-arm verification gate ─────────────────────────
    def gate(self, arm_a: str, arm_b: str) -> list[dict]:
        """The VERIFICATION GATE: for each (unit_a, unit_b) pairing across two arms (matched by qname
        when names coincide, else best by shared support), the cross-term. degree 0 = arm_b REALIZES
        arm_a (orthogonal, same canonical structure); degree>0 = graded obstruction (residue = what
        each carries the other doesn't); the shared_fraction = how coherent."""
        ua = {q: r for q, r in self.arms.get(arm_a, [])}
        ub = {q: r for q, r in self.arms.get(arm_b, [])}
        out = []
        for q, ra in ua.items():
            # match by qname if present in b, else take b's best-sharing unit
            if q in ub:
                rb, how = ub[q], "by-name"
            else:
                cand = [(self.cross.shared_fraction(ra, r), r) for r in ub.values()]
                if not cand:
                    continue
                frac, rb = max(cand); how = "by-support"
            ct = self.cross.cross_term(ra, rb)
            out.append({"unit": q, "match": how,
                        "realizes": ct.degree == 0,
                        "degree": ct.degree,
                        "shared_fraction": round(self.cross.shared_fraction(ra, rb), 3),
                        "a_residue": ct.a_residue, "b_residue": ct.b_residue})
        return out

    # ── the COMPLETENESS readout: does every unit have a mirror at all? ───────
    def coverage(self, arm_a: str, arm_b: str, floor: float = 0.5,
                 manifest: dict[str, str] | None = None) -> dict:
        """The completeness/recall companion to `gate`. `gate` answers PRECISION ("is each *matched*
        pair faithful?"); `coverage` answers RECALL ("does every unit have a mirror at all?"). The bare
        gate cannot see recall — it iterates arm_a only and, for an arm_a unit with no real partner,
        still takes arm_b's *best* match, so a MISSING mirror is silently reported as a (low-coherence)
        match and an arm_b unit absent from arm_a is never visited.

        coverage walks BOTH sides: for each unit it finds its best partner across the other arm by
        `shared_fraction`; a unit whose best < `floor` is an ORPHAN (no structural mirror). It returns
        the orphan lists for both arms + per-side coverage fractions. `complete` is True iff neither
        side has an orphan. Coverage is the EXISTENCE question (≥ floor), kept distinct from the gate's
        FIDELITY question (degree 0) — together: complete ∧ faithful.

        With a `manifest` of INTENDED correspondences {arm_a_qname: arm_b_qname}, it also reports each
        intended pair that is missing on either side or present-but-unfaithful (degree > 0) — turning
        best-effort pairing into a checkable spec (`manifest_complete`)."""
        au = self.arms.get(arm_a, [])
        bu = self.arms.get(arm_b, [])

        def best(r, others):
            cand = [(self.cross.shared_fraction(r, ro), qo) for qo, ro in others]
            return max(cand) if cand else (0.0, None)

        a_orphans, b_orphans, a_ok, b_ok = [], [], 0, 0
        for q, r in au:
            frac, partner = best(r, bu)
            if frac >= floor:
                a_ok += 1
            else:
                a_orphans.append({"unit": q, "best": partner, "shared_fraction": round(frac, 3)})
        for q, r in bu:
            frac, partner = best(r, au)
            if frac >= floor:
                b_ok += 1
            else:
                b_orphans.append({"unit": q, "best": partner, "shared_fraction": round(frac, 3)})

        result = {
            "arm_a": arm_a, "arm_b": arm_b, "floor": floor,
            "n_a": len(au), "n_b": len(bu),
            "coverage_a": round(a_ok / len(au), 3) if au else 1.0,
            "coverage_b": round(b_ok / len(bu), 3) if bu else 1.0,
            "a_orphans": a_orphans, "b_orphans": b_orphans,
        }
        if manifest is not None:
            ad, bd, misses = dict(au), dict(bu), []
            for qa, qb in manifest.items():
                if qa not in ad:
                    misses.append({"expected": f"{qa}→{qb}", "reason": f"{arm_a}:{qa} absent"})
                elif qb not in bd:
                    misses.append({"expected": f"{qa}→{qb}", "reason": f"{arm_b}:{qb} absent"})
                else:
                    ct = self.cross.cross_term(ad[qa], bd[qb])
                    if ct.degree != 0:
                        misses.append({"expected": f"{qa}→{qb}",
                                       "reason": f"present but unfaithful (degree {ct.degree})",
                                       "shared_fraction": round(self.cross.shared_fraction(ad[qa], bd[qb]), 3)})
            result["manifest_misses"] = misses
            result["manifest_complete"] = not misses

        result["complete"] = (not a_orphans and not b_orphans
                              and (manifest is None or result["manifest_complete"]))
        return result


if __name__ == "__main__":
    print("=== Σ-FOREST: the cross-arm verification gate (CrossMix over one forest) ===\n")
    F = OneForest()

    # ARM 'spec' = source intent; 'impl' = a faithful realization; 'broken' = a divergent one (same
    # qname, different body). The gate asks, structurally: does the other arm REALIZE spec? (stand-in
    # for source↔core↔kernel; the Agda-core and CUDA arms attach identically below.)
    F.add_python("spec",   "def axpy(x, y):\n    return x + y\n", "axpy")
    F.add_python("impl",   "def axpy(x, y):\n    return x + y\n", "axpy")   # faithful
    F.add_python("broken", "def axpy(x, y):\n    return x * y\n", "axpy")   # same name, divergent body

    def show(a, b):
        print(f"--- gate({a}, {b}): does {b} realize {a}? ---")
        for row in F.gate(a, b):
            verdict = "REALIZES (orthogonal, degree 0)" if row["realizes"] else \
                      f"DIVERGES (degree {row['degree']}, shared {row['shared_fraction']})"
            print(f"  {row['unit']:12} [{row['match']}]  {verdict}")
            if not row["realizes"]:
                print(f"       a_residue={row['a_residue']}  b_residue={row['b_residue']}")

    show("spec", "impl")            # REALIZES (orthogonal)
    print()
    show("spec", "broken")          # DIVERGES -- the gate localizes the obstruction (the residues)
    print()

    # ── COMPLETENESS readout: the gate above is blind to a MISSING mirror. Give 'spec' a 2nd algorithm
    #    with no realization, and 'impl' an extra unit with no spec -> coverage flags both as orphans.
    print("--- coverage(spec, impl): does EVERY unit have a mirror? (recall, not just precision) ---")
    F.add_python("spec", "def dot(u, v):\n    return sum(a * b for a, b in zip(u, v))\n", "dot")   # no impl
    F.add_python("impl", "def scale(x, k):\n    return x * k\n", "scale")                            # no spec
    cov = F.coverage("spec", "impl", floor=0.6)
    print(f"  coverage_a(spec→impl)={cov['coverage_a']}  coverage_b(impl→spec)={cov['coverage_b']}  "
          f"complete={cov['complete']}")
    print(f"  spec orphans (no impl mirror): {[o['unit'] for o in cov['a_orphans']]}")
    print(f"  impl orphans (no spec mirror): {[o['unit'] for o in cov['b_orphans']]}")
    mani = F.coverage("spec", "impl", floor=0.6, manifest={"axpy": "axpy", "dot": "dot"})
    print(f"  manifest {{axpy→axpy, dot→dot}}: complete={mani['manifest_complete']}  "
          f"misses={[m['reason'] for m in mani['manifest_misses']]}  (dot→dot expected but impl:dot absent)")
    print()

    # The other arms compose into the SAME forest+gate with NO new mechanism. They are ENVIRONMENT-BOUND
    # front-ends (the gate READOUT is not); each runs where its toolchain exists, skipping gracefully
    # otherwise -- never faking arm output.
    # AGDA-CORE arm via the LANDED shim (jea_agdai.core_intern_agdai, Φ4): runs where ghc+Agda + a CURRENT
    # .agdai exist (a stale/absent interface -> graceful skip; rebuild with `agda --safe`).
    print("--- agda-core arm (REAL, via the landed Φ4 shim) ---")
    try:
        units = F.add_agda_core("core", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "agda-emit", "Emit.agdai"))
        print(f"  {len(units)} Agda definitions interned into the SAME forest; gate(spec, core) computes the "
              f"cross-term across a real cross-LANGUAGE pair (Python spec ↔ Agda core):")
        for row in F.gate("spec", "core")[:3]:
            print(f"    {row['unit']:20} [{row['match']}]  degree {row['degree']}  shared {row['shared_fraction']}")
    except Exception as e:
        print(f"  skipped (env-bound): {type(e).__name__}: {str(e).splitlines()[0]}")
        print("  (runs where ghc+Agda + a fresh interface exist -- the arm composes by construction)")

    # CUDA kernel arm via libclang: env-bound; composes by construction when the jea_cuda front-end is present.
    print("\n--- cuda kernel arm (env-bound front-end) ---")
    try:
        F.add_cuda("kernel", "__global__ void axpy(float* x, float* y, float* z){ z[0]=x[0]+y[0]; }", "axpy")
        print(f"  kernel arm units: {[q for q,_ in F.arms['kernel']]}; gate(spec, kernel) runs identically.")
    except ModuleNotFoundError:
        print("  jea_cuda front-end not present in this env; the arm composes by construction (same Intern,")
        print("  same {(qname,root)} unit shape) -- no new mechanism, exercised where libclang exists.")
