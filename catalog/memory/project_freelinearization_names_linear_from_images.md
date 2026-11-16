---
name: project-freelinearization-names-linear-from-images
description: "Substrate.Category.FreeLinearization (#6) names the categorical universal property that substrate's `linear-from-images` + `apply-linear-from-images-basis` + `linear-extensionality` infrastructure has been realizing implicitly. Original roadmap primitive"
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's categorical primitive #6 (FreeLinearization), which
had been deferred since the initial Primitives.DBE.md roadmap, is
now closed:

* **Substrate.Category.FreeLinearization** — record packaging the
  universal property of the free F₂-module on Fin n: any
  f : Fin n → Vector m extends uniquely to a Linear n m.
* **Substrate.Category.FreeLinearization.FromImages** — the
  canonical constructor, built from existing substrate infrastructure:
  * `linear-from-images` (M-3.5) — the extension itself.
  * `apply-linear-from-images-basis` — the on-basis agreement.
  * `linear-extensionality` — the uniqueness.

**What this corrects:**

The substrate's existing infrastructure ALREADY realized this
universal property; it just wasn't named at the categorical level.
Per [[feedback-universal-property-discipline]]: any time the
substrate uses linear-from-images, it's using the
free-linearization universal property. The FreeLinearization
record makes this visible at the type level.

**Original roadmap status:**

The Primitives.DBE.md described #6 as "FreeLinearization — Prong B
/ continuous-side bridge, deferred." At F₂ the discrete version
IS the structural primitive; continuous versions (Laplacian
eigenvectors etc.) would fit via analogous universal properties at
the continuous algebras (out of substrate's current F₂ scope but
the categorical pattern is the same).

**How to apply:**

When the substrate uses `linear-from-images f` for some f, the
categorical reading is: "we are using the FreeLinearization
universal property at f". Downstream code citing
linear-from-images can equivalently cite FreeLinearization +
its extension.

**Connection to other primitives:**

* **#5 BeckChevalley**: the BC squares often involve linear
  extensions (e.g., bilinear-form-of-via-tensor as a BC square cell).
  These are FreeLinearization instances at the cell-providing
  morphism.
* **#4 Adjunction**: linear-from-images ⊣ images-of-linear is
  the adjunction; FreeLinearization is the unit-side of the
  adjunction packaged with its universal property.
* **#9 Cone**: the cone's leg structure often involves linear
  extensions; FreeLinearization provides the universal-property
  framing.

**Status:** named, instantiated, connected. Closes original
roadmap primitive #6.

**Deferred follow-on:**

* **Continuous-side bridge**: at non-F₂ algebras (ℝ-mod, ℂ-mod,
  etc.), the FreeLinearization universal property persists. The
  substrate's coalgebraic discipline (per
  [[feedback-coalgebraic-not-consumer-driven]]) suggests these
  continuous extensions are deferred until a use site demands.
