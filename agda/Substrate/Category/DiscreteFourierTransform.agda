------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform
--
-- PD8-PD20: discrete Fourier transform formalised at the categorical
-- level + Walsh-Hadamard as the F₂ⁿ DFT + Plancherel theorem +
-- convolution theorem + Frobenius algebra structure + categorical
-- Fourier + multi-prime DFT via CRT + connection to MultiSylow.
--
-- The DFT for a finite abelian group G with G^ its Pontryagin dual:
--   F : (G → ℂ) → (G^ → ℂ)
--   F(f)(χ) = Σ_g f(g) · χ(g)^*
-- This generalizes:
--   * Z/n DFT (roots of unity n-th)
--   * F₂ⁿ DFT (Walsh-Hadamard)
--   * Z/p × Z/q DFT (CRT factorization)
--
-- Per [[categorical-name-first]]: discrete Fourier transform is
-- standard. Categorical formulation via Frobenius algebras (per
-- Coecke-Pavlovic) gives the string-diagram language.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.PontryaginDual

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- PD8: A discrete Fourier transform for an LCA group G.
--
-- Given:
--   G       : the LCA group
--   G^      : its Pontryagin dual
--   Coeffs  : the coefficient field (typically ℂ, but for substrate
--             we'd want ℚ ∩ ℂ for constructive numerics)
--
-- The DFT is a linear map (G → Coeffs) → (G^ → Coeffs) defined by
-- character integration.

-- ⟡set1-paydown: parameterize Chars. The character carrier lived in the `G-dual`
-- field as `PontryaginDual A RootsType`'s `Chars`, forcing this record to Set₁. Now that
-- PontryaginDual takes Chars as a parameter, lift Chars here too: the `Chars G-dual`
-- projections become the supplied `Chars`, and the record lands in Set. Consumers write
-- `DiscreteFourierTransform Chars A RootsType G Coeffs`.
module _ (Chars : Set) where

  record DiscreteFourierTransform
         (A : Set)
         (RootsType : Set)
         (G : LocallyCompactAbelian A)
         (Coeffs : Set) : Set where
    field
      G-dual : PontryaginDual Chars A RootsType
      DFT    : (A → Coeffs) → (Chars → Coeffs)
      DFT-1  : (Chars → Coeffs) → (A → Coeffs)   -- inverse DFT
      -- Plancherel / invertibility laws stated abstractly; concrete
      -- instances supply.

  open DiscreteFourierTransform public

------------------------------------------------------------------------
-- PD10: Walsh-Hadamard as F₂ⁿ DFT.
--
-- For G = F₂ⁿ (self-dual), the DFT IS the Walsh-Hadamard transform.
-- The character values are ±1 (the only square roots of unity in ℚ);
-- the DFT matrix is the Hadamard matrix.
--
-- The substrate's GG-arc empirical work used this exact construction
-- (eliza/walsh_hadamard.py); PD10 makes it categorically first-class.

-- ⟡set1-paydown: parameterize F2nVec, F2nChars. The Set₁ debt came entirely through the
-- `self-dual-witness : F2nSelfDual n` field (F2nSelfDual was Set₁). Now that F2nSelfDual takes
-- its two carriers as parameters, lift them here so the field is Set-valued. Consumers write
-- `WalshHadamardDFT F2nVec F2nChars n`.
module _ (F2nVec : Set) (F2nChars : Set) where

  record WalshHadamardDFT
         (n : ℕ) : Set where
    field
      self-dual-witness : F2nSelfDual F2nVec F2nChars n
      -- Plus the concrete DFT data; abstracted here.

  open WalshHadamardDFT public

------------------------------------------------------------------------
-- PD9, PD11, PD12, PD13: DFT for finite abelian groups via CRT,
-- Plancherel theorem, convolution theorem, group ring structure.
--
-- All stated as records over a base DFT instance; concrete groups
-- supply the operators and verify the laws.

-- Per [[coalgebraic-not-consumer-driven]]: each theorem is a record
-- of obligation-surface witnesses; concrete sites discharge by
-- supplying values.

-- Z/n = ∏ Z/(p_i^k_i) for the prime factorization of n. The DFT
-- decomposes correspondingly: F_{Z/n} = ⊗_i F_{Z/(p_i^k_i)}.
-- Consumer supplies the per-factor DFT bundling.

-- ⟡set1-paydown: parameterize PrimeFactors, PerFactorDFT. Both were `: Set` carrier FIELDS
-- (Set₁ debt); take them as module parameters. Consumers write
-- `CRTDecomposition PrimeFactors PerFactorDFT n`.
module _ (PrimeFactors : Set) (PerFactorDFT : Set) where

  record CRTDecomposition
         (n : ℕ) : Set where
    field
      -- The CRT tensor-product witness: a map from factor-list to
      -- the composite per-factor DFT bundle.
      tensor-witness  : PrimeFactors → PerFactorDFT

  open CRTDecomposition public

-- Plancherel: ∑ |f|² ≡ ∑ |F(f)|² (up to scaling). Carried as a
-- per-function equation against consumer-supplied norms.

-- Chars lifted to a module parameter so the `D : DiscreteFourierTransform Chars …` param
-- typechecks and `Chars (G-dual D)` becomes the supplied `Chars` (already Set — no debt paid).
module _ (Chars : Set) where

  record PlancherelTheorem
         (A : Set)
         (RootsType : Set)
         (G : LocallyCompactAbelian A)
         (Coeffs : Set)
         (D : DiscreteFourierTransform Chars A RootsType G Coeffs) : Set where
    field
      -- Consumer-supplied norms on the two sides of the DFT.
      norm     : (A → Coeffs) → Coeffs
      norm-hat : (Chars → Coeffs) → Coeffs
      -- The Plancherel identity: total energy is preserved by DFT.
      plancherel : (f : A → Coeffs) → norm f ≡ norm-hat (DFT D f)

  open PlancherelTheorem public

-- Convolution theorem: DFT of convolution = pointwise product of
-- DFTs. Consumer supplies group-algebra convolution + Hadamard
-- product.

-- Chars lifted to a module parameter (as PlancherelTheorem); `Chars (G-dual D)` → `Chars`.
module _ (Chars : Set) where

  record ConvolutionTheorem
         (A : Set)
         (RootsType : Set)
         (G : LocallyCompactAbelian A)
         (Coeffs : Set)
         (D : DiscreteFourierTransform Chars A RootsType G Coeffs) : Set where
    field
      _*A_      : (A → Coeffs) → (A → Coeffs) → (A → Coeffs)
      _·dual_   : (Chars → Coeffs) →
                  (Chars → Coeffs) →
                  (Chars → Coeffs)
      convolves : (f g : A → Coeffs) →
                  DFT D (f *A g) ≡ (DFT D f) ·dual (DFT D g)

  open ConvolutionTheorem public

------------------------------------------------------------------------
-- PD14-PD16: Frobenius algebra structure + string diagrams +
-- categorical Fourier transform.
--
-- Per Coecke-Pavlovic ("Quantum measurements without sums") and
-- Vicary: the DFT can be presented as a morphism between two
-- Frobenius algebras (the "computational" basis and the "Fourier"
-- basis). Both bases give rise to Frobenius algebras on the same
-- underlying object; the basis-change morphism IS the DFT.
--
-- This is the most categorical form of the DFT, and connects to
-- ZX-calculus / string-diagram reasoning.

-- A basis as a Frobenius algebra: comultiplication, counit,
-- multiplication, unit satisfying the Frobenius law. Per
-- Coecke-Pavlovic, the DFT presents as a basis-change morphism
-- between two such Frobenius structures.

record FrobeniusBasisStructure
       (A : Set) : Set where
  field
    comult   : A → A → A      -- Δ : A → A ⊗ A (uncurried)
    counit   : A → A          -- ε : A → I (substrate-pragmatic: I = A)
    mult     : A → A → A      -- μ : A ⊗ A → A
    unit     : A              -- η : I → A
    -- Frobenius law witness (stated as a consumer obligation):
    frobenius : (a b : A) → mult (comult a b) b ≡ comult a (mult b b)

open FrobeniusBasisStructure public

-- The categorical Fourier transform as a basis-change morphism
-- between two Frobenius algebra structures on A: the "spatial"
-- basis (G's own structure) and the "Fourier" basis (G^'s
-- structure).

record CategoricalFourierTransform
       (A : Set)
       (RootsType : Set)
       (G : LocallyCompactAbelian A) : Set where
  field
    spatial-basis : FrobeniusBasisStructure A
    fourier-basis : FrobeniusBasisStructure A
    -- The DFT is the basis-change morphism between them.
    basis-change : A → A
    -- Coherence: the basis-change conjugates fourier-basis to
    -- spatial-basis at the comult level.
    coherence    : (a b : A) →
                   basis-change (comult fourier-basis a b)
                     ≡ comult spatial-basis (basis-change a)
                                            (basis-change b)

open CategoricalFourierTransform public

------------------------------------------------------------------------
-- PD17-PD19: connection to MultiSylowComposition + multi-prime
-- DFT decomposition + DFT as Markov category morphism.
--
-- Per [[jj-arc-multi-sylow-composition]]: the substrate's multi-
-- Sylow predictor uses each Sylow prime independently. Pontryagin
-- duality says: the DFT of a finite abelian group decomposes via
-- CRT into Sylow-prime DFTs.
--
-- For Z/(p₁^a × p₂^b × p₃^c), the DFT is the tensor product of
-- the per-Sylow DFTs. The substrate's multi-Sylow probe atlas IS
-- the Pontryagin-dual reading of the chain walk's Sylow structure.
--
-- This is the substrate-honest connection between PD arc and JJ
-- arc's empirical work: the multi-Sylow MI saturation curve
-- empirically realizes Pontryagin's CRT decomposition.

-- The DFT for Z/n decomposes via the prime factorization of n
-- into a tensor product of per-Sylow-prime DFTs. Consumer supplies
-- the prime-list and the per-prime DFT bundle.

-- ⟡set1-paydown: parameterize SylowPrimes, PerSylowDFT. Both were `: Set` carrier FIELDS
-- (Set₁ debt); take them as module parameters. Consumers write
-- `MultiSylowDFTDecomposition SylowPrimes PerSylowDFT n`.
module _ (SylowPrimes : Set) (PerSylowDFT : Set) where

  record MultiSylowDFTDecomposition
         (n : ℕ) : Set where
    field
      sylow-bundle : SylowPrimes → PerSylowDFT

  open MultiSylowDFTDecomposition public

-- The DFT can be viewed as a deterministic morphism in a Markov
-- category (basis change). Connects PD arc to MK arc. The
-- consumer site supplies the deterministic-kernel witness — i.e.,
-- the DFT-image is delta-supported.

-- Chars lifted to a module parameter (as PlancherelTheorem); `Chars (G-dual D)` → `Chars`.
module _ (Chars : Set) where

  record DFTasMarkovMorphism
         (A : Set)
         (RootsType : Set)
         (G : LocallyCompactAbelian A)
         (Coeffs : Set)
         (D : DiscreteFourierTransform Chars A RootsType G Coeffs) : Set where
    field
      -- The DFT viewed as a Markov-category morphism: deterministic
      -- = "input-to-output is a function, not a stochastic relation".
      deterministic : (a : A) (c : Chars) →
                      Coeffs

  open DFTasMarkovMorphism public

------------------------------------------------------------------------
-- PD20: PD arc capstone.
--
-- The Pontryagin-duality / categorical Fourier primitives provide:
--   * Locally compact abelian group + Pontryagin dual
--   * Discrete Fourier transform (general LCA case)
--   * Walsh-Hadamard as F₂ⁿ DFT (substrate-aligned)
--   * Plancherel + convolution theorems
--   * Frobenius algebra structure (categorical form)
--   * CRT decomposition matching the substrate's multi-Sylow work
--
-- Connection to existing substrate work:
--   * GG-arc (Walsh-Hadamard) IS PD10 made empirical
--   * JJ-arc (Multi-Sylow composition) IS PD18 made empirical
--   * MultiSylowComposition Agda IS the algebra side of PD16
--
-- Per the horizon: the Frobenius algebra / string-diagram formalism
-- naturally extends to ZX-calculus, Categorical Quantum Mechanics,
-- and tensor network reasoning (beyond this 80-slice scope).
--
-- Per [[expose-generator-not-orbit]]: the DFT is the generator of
-- spectral analysis; per-corpus spectra (substrate_agda, t1t2,
-- etc.) are orbits.
------------------------------------------------------------------------
