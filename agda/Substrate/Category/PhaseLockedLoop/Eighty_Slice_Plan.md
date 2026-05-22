# 80-Slice Theoretical Extension Plan

User directive 2026-05-21: "rigorize the available substrate theories ...
expanding the costructure will make it a lot easier to jump on ideas
efficiently ... execute the next eighty slices."

Four arcs × 20 slices each, anchored to existing substrate infrastructure
(SymmetricMonoidal, KleisliCategory, TensorProduct, Coalgebra, Monad,
BeckChevalley, CategoryOf).

## MK Arc — Markov Categories (slices MK1–MK20)

Synthesis of CascadedCoalgebra + ConjugateMonad → filtering / estimation.

| Slice | Module / Refinement |
|---|---|
| MK1 | `Substrate.Category.Comonoid` — copy + delete structure |
| MK2 | `Substrate.Category.CommutativeComonoid` |
| MK3 | `Substrate.Probability.MarkovCategory` (record built on SymmetricMonoidal + commutative comonoid each object) |
| MK4 | Terminal object structure (tensor unit = terminal) |
| MK5 | Determinism predicate (morphism preserves copy) |
| MK6 | Almost-sure equality |
| MK7 | Conditional structure |
| MK8 | Marginalisation |
| MK9 | Sufficient statistic (Fritz) |
| MK10 | Bayesian inversion |
| MK11 | `Substrate.Category.StochasticLens` — forward / backward / round-trip |
| MK12 | Identity stochastic lens |
| MK13 | Composition of lenses |
| MK14 | Lens functoriality |
| MK15 | Lens category structure |
| MK16 | Connection: ConjugateMonad → Stochastic Lens |
| MK17 | Connection: CascadedCoalgebra → Stochastic Lens (Kalman shape) |
| MK18 | Filter primitive (state estimation under noise) |
| MK19 | Particle filter sketch (Monte Carlo lens) |
| MK20 | MK arc capstone |

## PF Arc — Polynomial Functors (slices PF1–PF20)

Wiring language for variable-arity / mode-dependent systems.

| Slice | Module / Refinement |
|---|---|
| PF1 | `Substrate.Category.Poly` — polynomial as Σ A. y^B |
| PF2 | Position / direction projections |
| PF3 | Polynomial functor morphism (lens shape) |
| PF4 | Identity polynomial |
| PF5 | Coproduct of polynomials |
| PF6 | Product of polynomials |
| PF7 | Composition `◁` of polynomials |
| PF8 | Tensor `⊗` of polynomials |
| PF9 | `Substrate.Category.PolyLens` — dependent lens |
| PF10 | Lens composition |
| PF11 | Coalgebra over a polynomial functor |
| PF12 | `Substrate.Category.OpenDynamicalSystem` |
| PF13 | Composition of open systems |
| PF14 | Wiring diagram primitive |
| PF15 | FieldFanOut → Poly instance |
| PF16 | StratifiedBundle → Poly-coalgebra |
| PF17 | Mode-dependent IO arity |
| PF18 | Beck-Chevalley for Poly |
| PF19 | Variable-arity PLL bank as Poly-coalgebra |
| PF20 | PF arc capstone |

## IG Arc — Categorical Information Geometry (slices IG1–IG20)

Quantify drift events, posterior surprise, adaptive arity.

| Slice | Module / Refinement |
|---|---|
| IG1 | `Substrate.Probability.Simplex` — finite probability simplex |
| IG2 | `Substrate.Probability.Entropy` — Shannon entropy |
| IG3 | Conditional entropy |
| IG4 | Joint entropy |
| IG5 | Mutual information |
| IG6 | `Substrate.Probability.KLDivergence` |
| IG7 | KL positivity |
| IG8 | KL chain rule |
| IG9 | Cross-entropy |
| IG10 | `Substrate.Probability.FisherInformation` |
| IG11 | Information gain at update step |
| IG12 | Information at strata boundaries |
| IG13 | Baez-Fritz-Leinster entropy functor characterisation |
| IG14 | Convex combination compatibility |
| IG15 | Sufficient statistic via MI (connection to MK9) |
| IG16 | Markov category interpretation |
| IG17 | Adaptive arity via entropy threshold |
| IG18 | Posterior surprise in ConjugateMonad |
| IG19 | BoundaryEvent → information gain |
| IG20 | IG arc capstone |

## PD Arc — Pontryagin Duality / Categorical Fourier (slices PD1–PD20)

Frequency domain at the categorical level.

| Slice | Module / Refinement |
|---|---|
| PD1 | `Substrate.Algebra.TopologicalGroup` |
| PD2 | `Substrate.Algebra.LocallyCompactAbelian` |
| PD3 | `Substrate.Algebra.Character` |
| PD4 | `Substrate.Algebra.PontryaginDual` |
| PD5 | Pontryagin duality theorem (statement) |
| PD6 | F₂ⁿ as self-dual |
| PD7 | Character on Z/n |
| PD8 | `Substrate.Category.DiscreteFourierTransform` |
| PD9 | DFT for finite abelian groups via CRT |
| PD10 | Walsh-Hadamard transform as F₂ⁿ DFT (connection to GG-arc) |
| PD11 | Plancherel theorem (finite case) |
| PD12 | Convolution theorem |
| PD13 | `Substrate.Algebra.GroupRing` |
| PD14 | `Substrate.Category.FrobeniusAlgebra` |
| PD15 | String diagrams for DFT |
| PD16 | `Substrate.Category.CategoricalFourier` |
| PD17 | Connection to MultiSylowComposition |
| PD18 | Multi-prime DFT decomposition |
| PD19 | DFT as Markov category morphism |
| PD20 | PD arc capstone |

## Execution Discipline

Per DBE constructive-completeness criterion (user 2026-05-21):
each record must include all fields needed for someone-handed-these
to construct the whole behavior.

Per [[categorical-name-first]]: use established categorical names;
PLL / signal-processing names are application-layer.

Per [[coalgebraic-not-consumer-driven]] at lowest levels; monadic
structures (ConjugateMonad, KleisliCategory) are honest if their
underlying carriers are coalgebraically built.

All modules typecheck under `--safe --without-K`. No postulates.
Universe-flexible parameters where natural.
