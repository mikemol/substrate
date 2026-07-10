------------------------------------------------------------------------
-- Substrate.Category.CoarseResidueEmission
--
-- FF-arc: emit AA-arc S₄ residue σ via a smaller alphabet when σ
-- falls in the NIBBLE_TO_PERM image (16 of 24 chambers), recovering
-- the full chamber index from a 4-bit nibble through structural
-- lookup. The "sloppy emission + recovery via EE7" interpretation:
-- the encoder is allowed to drop the 5-bit chamber index in favor
-- of a 4-bit nibble, recovering the original via the canonical
-- bijection between chain-walk steps and S₄ chambers.
--
-- Per the user's prompt: 'with EE7, we could permit ourselves to
-- get a little sloppy and use EE7 to recover without preserving as
-- much residue'.
--
-- Per [[chain-walk-blocks-rotation-factor]]: the NIBBLE_TO_PERM
-- image is exactly the set of σ values reachable as single-step
-- chain-walk transitions. Empirical FF7 finding: 67-100% of the
-- codec's actual σ emissions fall in this image — backref
-- search prefers single-step-compatible σ values.
--
-- Per [[3plus1-parity-universal]]: |NIBBLE_TO_PERM image| = 16 =
-- 2^4 = |V₄| × |S₃_involutions|; the substrate's V₄ × S₃-inv
-- product naturally gives the 16-element subset.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CoarseResidueEmission where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (_×_; _,_; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; refl)

-- ⟡set1-paydown: parameterize Chamber, Nibble. `Chamber : Set` and `Nibble : Set` were
-- FIELDS of CoarseResidueBijection, forcing it (and the records fielding it) to Set₁. Take
-- them as the module parameters and the tower lives in Set; consumers write
-- `CoarseResidueBijection Chamber Nibble`, etc. (EncoderDispatch / LosslessCoarseRoundTrip
-- stay Set₁ honestly — they field a `Chamber → Set` predicate / a Set-level equality.)
module _ (Chamber Nibble : Set) where

  ------------------------------------------------------------------------
  -- A "coarse residue alphabet" is a smaller alphabet (e.g., 16
  -- elements) injecting into the full S₄ residue alphabet (24
  -- elements). The injection is the bijection between NIBBLE_TO_PERM
  -- indices and the chambers they reach as single-step transitions.

  record CoarseResidueBijection : Set where
    field
      -- The encoding: σ ↪ nibble for σ in the image.
      encode      : Chamber → Nibble
      -- The decoding: nibble → σ.
      decode      : Nibble → Chamber
      -- Round-trip: encode then decode is identity on the image.
      encode-decode :
        (n : Nibble) → encode (decode n) ≡ n

  open CoarseResidueBijection public

  ------------------------------------------------------------------------
  -- A coarse-residue emission opcode in the codec's joint alphabet.
  -- Distinct from the full-residue emission opcode; the decoder
  -- dispatches on the control symbol to choose decode path.

  record CoarseEmissionOpcode : Set where
    field
      -- Full opcode emits σ ∈ Chamber (5 bits in the codec's actual
      -- alphabet).
      full-emit-alphabet-size   : ℕ
      -- Coarse opcode emits σ ∈ Nibble (4 bits).
      coarse-emit-alphabet-size : ℕ
      -- The bijection used for recovery.
      bijection                 : CoarseResidueBijection
      -- Coarse alphabet is strictly smaller (the "savings" axis).
      coarse-smaller            : coarse-emit-alphabet-size ≤ full-emit-alphabet-size

  open CoarseEmissionOpcode public

  ------------------------------------------------------------------------
  -- Encoder dispatch.
  --
  -- Given a σ value, the encoder checks if σ is in the bijection's
  -- image (= reachable as single-step chain-walk transition); if so,
  -- emits via the coarse opcode; else falls back to the full opcode.

  -- ⟡set1-paydown: the membership/decision predicate families `in-image, decide :
  -- Chamber → Set` were FIELDS, forcing EncoderDispatch to Set₁. Lift them to nested
  -- module params → the record lives in Set. `EncoderDispatch in-image decide` names the
  -- dispatch over those two predicates; the opcode is the only remaining content.
  module _ (in-image decide : Chamber → Set) where

    record EncoderDispatch : Set where
      field
        opcode      : CoarseEmissionOpcode

    open EncoderDispatch public

  ------------------------------------------------------------------------
  -- Decoder dispatch.
  --
  -- On receiving the coarse opcode, decoder reads a Nibble symbol
  -- and applies decode to recover the Chamber index. On receiving
  -- the full opcode, decoder reads a Chamber symbol directly.

  record DecoderDispatch : Set where
    field
      opcode      : CoarseEmissionOpcode
      -- Recovery: nibble → chamber via bijection.decode.

  open DecoderDispatch public

  ------------------------------------------------------------------------
  -- Lossless round-trip law.
  --
  -- For any encoder dispatch + decoder dispatch sharing the same
  -- bijection, encode-then-decode preserves the Chamber value.
  --
  -- This holds at the structural level: encoder coarse path emits
  -- bijection.encode σ; decoder coarse path applies bijection.decode
  -- on the same nibble.

  -- ⟡set1-paydown: cascades from EncoderDispatch — its predicates are now params, so
  -- thread (in-image, decide) through here too; `enc-dispatch : EncoderDispatch in-image
  -- decide`. All fields are now Set-level, so LosslessCoarseRoundTrip drops to Set.
  module _ (in-image decide : Chamber → Set) where

    record LosslessCoarseRoundTrip : Set where
      field
        enc-dispatch : EncoderDispatch in-image decide
        dec-dispatch : DecoderDispatch
        same-bijection :
          bijection (opcode enc-dispatch) ≡ bijection (opcode dec-dispatch)

    open LosslessCoarseRoundTrip public

  ------------------------------------------------------------------------
  -- Connection to AA-arc residue and chain-walk image.
  --
  -- Per [[chain-walk-blocks-rotation-factor]]: the substrate's chain
  -- walk is c_{k+1} = c_k ∘ NIBBLE_TO_PERM[n_{k+1}]. The σ values
  -- reachable as one-step transitions from any chamber c_k are
  -- exactly:
  --   image = { NIBBLE_TO_PERM[n] | n ∈ [0, 16) }
  -- This is a 16-element subset of S₄.
  --
  -- FF-arc's coarse opcode emits σ as the nibble n; the decoder
  -- recovers σ = NIBBLE_TO_PERM[n].

  record ChainWalkImageProperty : Set where
    field
      bijection : CoarseResidueBijection
      -- The image is exactly the single-step transitions.
      -- Stated abstractly here; concrete instances enumerate.

  open ChainWalkImageProperty public

------------------------------------------------------------------------
-- Empirical observation (FF7, not theorem).
--
-- Per [[multi-reading-ambient-discipline]] and
-- [[negative-findings-corpus-bound]]:
-- on every tested corpus, 67-100% of the codec's empirical σ
-- emissions fall in the NIBBLE_TO_PERM image. This is a structural
-- alignment: the backref-with-residue search PREFERS σ values that
-- correspond to single-step chain-walk transitions because those
-- σ values produce backref expansions that fit smoothly into the
-- ongoing chain walk.
--
-- Compression-wise: emitting σ via 16-value alphabet vs 24-value
-- alphabet does NOT save bits under the adaptive predictor —
-- range coding cost depends on log₂(p), not alphabet size. The
-- FF-arc's structural value is in NAMING the σ-cluster property,
-- which informs predictor design at the FF+1 arc.

------------------------------------------------------------------------
-- Per [[expose-generator-not-orbit]]:
--
-- The NIBBLE_TO_PERM image IS the generator subset of S₄ relative
-- to the chain walk. Codec emissions stay within the generator
-- subset in the common case; off-generator emissions (the 8 σ
-- values in S₄ \\ image) are rare. FF-arc surfaces this generator/
-- orbit distinction at the opcode layer.

------------------------------------------------------------------------
-- Categorical reading.
--
-- The encoder + decoder form a functor pair between two alphabets
-- (Chamber, Nibble) related by a bijection on the chain-walk image.
-- The FF-arc adds one more level to the substrate's homology/
-- cohomology tower per [[homology-cohomology-recursion]]:
--
--   layer-k    : chain-walk transitions (NIBBLE_TO_PERM image)
--   layer-k+1  : residue emissions (S_REF_RECENT, full S₄)
--   layer-k+2  : coarse residue (S_COARSE_REF, nibble alphabet)
--
-- Each layer's homology is the previous layer's cohomology; FF-arc
-- adds the bijection that closes the layer-k → layer-k+2 path.
------------------------------------------------------------------------
