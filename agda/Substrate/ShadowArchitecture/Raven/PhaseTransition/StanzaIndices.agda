------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
--
-- s1 .. s18 : named Fin 18 indices into the 18-stanza Raven vector.
--
-- Each sₖ is built as suc^(k-1) zero — explicit because `sₖ₊₁ = suc sₖ`
-- would make `sₖ₊₁ : Fin 19` rather than `Fin 18`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices where

open import Substrate.Foundation.Fin using (Fin; zero; suc)

s1  : Fin 18 ; s1  = zero
s2  : Fin 18 ; s2  = suc zero
s3  : Fin 18 ; s3  = suc (suc zero)
s4  : Fin 18 ; s4  = suc (suc (suc zero))
s5  : Fin 18 ; s5  = suc (suc (suc (suc zero)))
s6  : Fin 18 ; s6  = suc (suc (suc (suc (suc zero))))
s7  : Fin 18 ; s7  = suc (suc (suc (suc (suc (suc zero)))))
s8  : Fin 18 ; s8  = suc (suc (suc (suc (suc (suc (suc zero))))))
s9  : Fin 18 ; s9  = suc (suc (suc (suc (suc (suc (suc (suc zero)))))))
s10 : Fin 18 ; s10 = suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))
s11 : Fin 18 ; s11 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))
s12 : Fin 18 ; s12 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))
s13 : Fin 18 ; s13 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))))
s14 : Fin 18 ; s14 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))))
s15 : Fin 18 ; s15 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))))))
s16 : Fin 18 ; s16 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))))))
s17 : Fin 18 ; s17 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))))))))
s18 : Fin 18 ; s18 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))))))))
