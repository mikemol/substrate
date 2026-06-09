#!/usr/bin/env python3
"""Render every gallery figure and build an HTML contact sheet.

Runs each figure script non-interactively (so each saves its PNG + SVG to
out/), then writes out/index.html — a thumbnail grid grouped by category, each
thumbnail linking to its SVG.

    python render_all.py            # render all + build index
    python render_all.py --index   # rebuild index.html only (no re-render)
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# (script, title, one-line caption).  Grouped by category for the contact sheet.
# 3D siblings (*_3d) sit right after their 2D figure.
GALLERY = [
    ("3D — PyVista (real lighting, shadows, SSAO, haze)", [
        ("klein_pv", "Klein {7,3} · funnel", "real self-shadowing hyperbolic bowl"),
        ("klein_pv_flower", "Klein {7,3} · flower", "the Minkowski-hyperboloid bloom"),
        ("klein_pv_inverted", "Klein {7,3} · inverted", "centre as peak, hanging skirt"),
        ("permutohedron_pv", "S₄ permutohedron", "breathing Fiedler, soft cast shadows"),
        ("fano_pv", "Fano plane · F₂³ cube", "7 points, 7 lines, Singer cycle"),
        ("idea_pv", "Idea lattice tower", "nine levels, gauge vs invariant"),
        ("hodge_pv", "Hodge ★ fold tower", "grade ladder, 0↔3 / 1↔2"),
        ("surreal_pv", "Surreal tree", "{L|R} unfolded by birthday"),
        ("octonion_pv", "Octonion relief", "sign-coloured bars, floor at 0"),
        ("hadamard_pv", "Walsh–Hadamard terraces", "recursion-grade steppes"),
        ("spectrum_pv", "Permutohedron harmonics", "rectified standing waves"),
        ("similarity_pv", "Similarity clusters", "orbits as 3D clouds"),
        ("import_pv", "Import graph", "packages, node ∝ module count"),
    ]),
    ("Math gems", [
        ("fano_plane", "Fano plane ℙ²(F₂)", "7 points · 7 lines · the Singer 7-cycle"),
        ("fano_plane_3d", "Fano plane · 3D", "the 7 points inside their F₂³ cube"),
        ("octonion_fano", "Octonion multiplication", "Fano mnemonic + the 8×8 Cayley table"),
        ("octonion_fano_3d", "Octonion table · 3D", "signed relief (red/blue → ±height)"),
        ("hodge_tetrahedron", "Hodge duality", "dual-grade ★ on the 3-simplex"),
        ("hodge_tetrahedron_3d", "Hodge ★ · 3D", "the grade ladder as a vertical fold"),
        ("dynkin_diagrams", "Dynkin diagrams", "the finite Cartan types A–G"),
        ("surreal_tree", "Surreal number tree", "{L | R}, stratified by birthday"),
        ("surreal_tree_3d", "Surreal tree · 3D", "birthday lifted, the tree unfolded"),
        ("klein_quartic_tiling", "Klein quartic {7,3}", "the order-3 heptagonal tiling (PSL(2,7))"),
        ("klein_quartic_3d", "Klein quartic · 3D funnel", "the {7,3} hyperbolic tower, lit"),
        ("klein_quartic_flower", "Klein quartic · 3D flower", "Minkowski hyperboloid (z = cosh ρ) bloom"),
        ("klein_quartic_inverted", "Klein quartic · 3D inverted", "the funnel flipped — centre as peak"),
    ]),
    ("Cayley / permutohedron", [
        ("permutohedron_s4", "S₄ permutohedron", "truncated octahedron, Fiedler colouring"),
        ("permutohedron_s4_3d", "S₄ permutohedron · 3D", "breathing along the Fiedler wave"),
        ("s3_hexagon", "S₃ Cayley graph", "the braid relation s₁s₂s₁ = s₂s₁s₂"),
    ]),
    ("Repo meta-structure", [
        ("idea_lattice", "Idea lattice", "nine levels, the five-cocycle tower"),
        ("idea_lattice_3d", "Idea lattice · 3D", "the cocycle tower, rings stacked by level"),
        ("similarity_clusters", "Similarity clusters", "structural orbits among Agda modules"),
        ("similarity_clusters_3d", "Similarity clusters · 3D", "orbits as clouds in a 3D force layout"),
        ("import_dag", "Import graph", "package-level dependency skeleton"),
        ("import_dag_3d", "Import graph · 3D", "packages in a 3D force layout"),
    ]),
    ("Spectral / heatmaps", [
        ("permutohedron_spectrum", "Permutohedron spectrum", "Laplacian eigenvalues + harmonics"),
        ("permutohedron_spectrum_3d", "Permutohedron harmonics · 3D", "standing waves as an amplitude surface"),
        ("hadamard_basis", "Walsh–Hadamard basis", "the Sylvester ±1 fractal"),
        ("hadamard_basis_3d", "Walsh–Hadamard · 3D", "recursion grade → terraced ziggurat"),
        ("totient", "Euler totient", "coprime residues k mod m"),
    ]),
]

ALL_SCRIPTS = [name for _, items in GALLERY for (name, _, _) in items]


# Some gallery keys are variants of one script, driven by flags.
OVERRIDE = {
    "totient": (HERE.parent / "totient_plot.py", []),
    "klein_quartic_flower": (HERE / "klein_quartic_3d.py", ["--model", "hyperboloid"]),
    "klein_quartic_inverted": (HERE / "klein_quartic_3d.py", ["--invert"]),
    "klein_pv_flower": (HERE / "klein_pv.py", ["--model", "hyperboloid"]),
    "klein_pv_inverted": (HERE / "klein_pv.py", ["--invert"]),
}


def render(name):
    script, extra = OVERRIDE.get(name, (HERE / f"{name}.py", []))
    if not script.exists():
        return (name, "missing", f"{script.name} not found")
    proc = subprocess.run([sys.executable, str(script), *extra],
                          capture_output=True, text=True)
    status = "ok" if proc.returncode == 0 and (OUT / f"{name}.png").exists() else "FAIL"
    return (name, status, (proc.stderr or proc.stdout).strip().splitlines()[-1:] or [""])


def build_index():
    rows = []
    for category, items in GALLERY:
        cards = []
        for name, title, caption in items:
            png = f"{name}.png"
            svg = f"{name}.svg"
            have = (OUT / png).exists()
            if not have:
                continue
            cards.append(f"""
        <figure class="card">
          <a href="{svg}"><img src="{png}" alt="{title}"></a>
          <figcaption><b>{title}</b><br><span>{caption}</span>
            <br><code>{name}.py</code></figcaption>
        </figure>""")
        if cards:
            rows.append(f'<h2>{category}</h2>\n<div class="grid">{"".join(cards)}</div>')

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Substrate figure gallery</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; margin: 2rem auto;
         max-width: 1200px; color: #222; background: #fafafa; }}
  h1 {{ font-size: 1.6rem; }}
  h2 {{ margin-top: 2rem; border-bottom: 2px solid #0072B2; padding-bottom: .3rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
           gap: 1.2rem; }}
  .card {{ margin: 0; background: white; border: 1px solid #ddd; border-radius: 8px;
           padding: .6rem; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  .card img {{ width: 100%; height: auto; border-radius: 4px; }}
  figcaption {{ font-size: .85rem; margin-top: .4rem; }}
  figcaption span {{ color: #666; }}
  code {{ color: #0072B2; font-size: .8rem; }}
</style></head><body>
<h1>Substrate figure gallery</h1>
<p>Rendered from <code>scratch/figures/</code>. Click any thumbnail for the SVG.
   Every figure also takes <code>--interactive</code>.</p>
{"".join(rows)}
</body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"  wrote {OUT / 'index.html'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", action="store_true", help="Rebuild index only.")
    a = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    if not a.index:
        for name in ALL_SCRIPTS:
            n, status, _ = render(name)
            print(f"  [{status:>4}] {n}")
    build_index()


if __name__ == "__main__":
    main()
