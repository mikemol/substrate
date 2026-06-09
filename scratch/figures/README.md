# Substrate figure gallery

Pretty pictures of the structures that live in this repo. Each script reads
data (or reuses code) that already exists in the substrate and renders a figure.

## Running

Everything uses the repo `.venv` (matplotlib + networkx + numpy):

```sh
# one figure → saves out/<name>.png and out/<name>.svg
.venv/bin/python scratch/figures/fano_plane.py

# the same figure, live window instead of files
.venv/bin/python scratch/figures/fano_plane.py --interactive

# render the whole gallery + build out/index.html (a thumbnail contact sheet)
.venv/bin/python scratch/figures/render_all.py
```

Shared plumbing is in [`_gallery.py`](_gallery.py) (`make_parser` / `set_style`
/ `finish`); the S₄ permutohedron core is in [`_perm.py`](_perm.py).

## Figures

| Figure | What it shows | Reuses |
|---|---|---|
| `fano_plane` | ℙ²(F₂): 7 points, 7 lines, the Singer 7-cycle | `Algebra/F2/FanoPlane.agda` |
| `octonion_fano` | octonion Fano mnemonic + 8×8 Cayley table | `Category/MultiscaleOctonionLoop.agda` |
| `hodge_tetrahedron` | dual-grade ★ on the 3-simplex | `WitnessTower/Hodge.agda` |
| `dynkin_diagrams` | the finite Cartan types A–G | `Category/CartanType.agda` |
| `surreal_tree` | {L\|R} numbers stratified by birthday | `Algebra/Quotient/Surreal.agda` |
| `klein_quartic_tiling` | the {7,3} tiling for GL(3,F₂) ≅ PSL(2,7) | hyperbolic geometry |
| `permutohedron_s4` | S₄ truncated octahedron, Fiedler-coloured | `eliza/13.py` `SpectralManifold` |
| `s3_hexagon` | S₃ Cayley graph, braid relation | `…/MetricGauge/CoxeterRelations.agda` |
| `idea_lattice` | nine levels, the five-cocycle tower | `catalog/idea_lattice.md` |
| `similarity_clusters` | structural orbits among Agda modules | `scripts/agda_similarity.py` |
| `import_dag` | package-level import skeleton | `scripts/audit_import_reach.py` |
| `permutohedron_spectrum` | Laplacian spectrum + harmonics | `_perm.py` |
| `hadamard_basis` | the Sylvester ±1 Walsh fractal | `scratch/hadamard_basis.py` |
| `totient` | coprime residues k mod m | `scratch/totient_plot.py` |

## 3D — PyVista (real lighting & shadows)

The premium 3D path. Matplotlib's 3D is painter's-algorithm (no true occlusion,
no cast shadows), so the headline 3D figures are rendered with **PyVista/VTK**
via the [`_pv.py`](_pv.py) substrate — and reuse all the same data builders
(`_perm` / `_klein` / `_fano` / `_catalog` / `_graphs`) and pure-numpy LiftMaps
(`_lift3d`). Only the draw step differs.

Every `*_pv.py` figure gets, stacked: real **cast shadows** from a *wide* key
light (a disk of jittered samples → soft penumbrae), **SSAO** contact
darkening, **depth-of-field haze** for aerial distance, a **gradient sky**, a
**diegetic box** (floor + walls that occlude and catch the object's real
shadow), **Okabe-Ito** colours on the shapes (so shadows carry depth, not
rainbow encoding), and **rule-of-thirds** framing (opening-up objects seated in
the lower two-thirds). `--edl` adds eye-dome lighting (strong depth edges, but
darkens colours — off by default). Renders headless; PNG only (VTK is raster).

Figures: `permutohedron_pv`, `klein_pv` (+ `--model hyperboloid` flower,
`--invert`), `fano_pv`, `idea_pv`, `hodge_pv`, `surreal_pv`, `octonion_pv`,
`hadamard_pv`, `spectrum_pv`, `similarity_pv`, `import_pv`.

```sh
.venv/bin/python scratch/figures/klein_pv.py                 # → out/klein_pv.png
.venv/bin/python scratch/figures/klein_pv.py --interactive   # rotatable window
```

The matplotlib `*_3d.py` versions are kept alongside (lightweight, SVG-capable,
labeled axes); see below.

## 3D lifts (matplotlib)

Most figures have a `*_3d.py` sibling. They all share one substrate,
[`_lift3d.py`](_lift3d.py): a lift is a *base* (2D layout or grid) + a *scalar
field* + a **LiftMap** `(point, scalar) → (x,y,z)`. The LiftMap is the gauge —
it decides what height *means* — and each carries `.gauge` (chosen convention)
vs canonical (fixed by the mathematics), printed on the figure:

| LiftMap | z is… | example |
|---|---|---|
| `hyperboloid` / `disk_height` | the hyperbolic metric (canonical) | Klein {7,3} tower |
| `radial` | a chosen displacement by the scalar (gauge) | breathing permutohedron |
| `tower` | a discrete level (gauge gap, canonical order) | idea-lattice / Hodge towers |
| `cartesian` | a chosen scalar height (gauge) | surreal unfold, spectra |
| `signed_bars` | signed-value relief (gauge) | octonion table |

Canonical (z fixed by the math): `fano_plane_3d` (the F₂³ cube), `klein_quartic_3d`,
`idea_lattice_3d`, `hodge_tetrahedron_3d`. Gauge lifts label their chosen
encoding (e.g. `octonion_fano_3d --z-mode sign|index`).

Klein has three variants (same tiling, different LiftMap):
`klein_quartic_3d` (funnel), `--model hyperboloid` (the "flower" / Minkowski
bloom), `--invert` (centre as peak).

**Depth cues** (also in `_lift3d`, the "qlight + vis" pass): `style_3d`
(perspective projection + transparent axis panes), `shade_surface` (directional
`LightSource` hillshading), `light_polys` (face-normal lighting for tile
collections), `floor_shadow` / `floor_plane` (drop-shadows and a translucent
z = 0 reference floor). Every 3D figure uses perspective, not isometric.

Shared data/graph shadows so 2D and 3D never duplicate: [`_fano.py`](_fano.py),
[`_klein.py`](_klein.py), [`_catalog.py`](_catalog.py),
[`_graphs.py`](_graphs.py), [`_perm.py`](_perm.py).

Output (PNG + SVG + `index.html`) lands in `out/`.
