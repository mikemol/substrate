------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition
--
-- act-∙: the action's composition law. Per-block dispatch via the
-- structural lemmas (Twist), bridged through act-cong + S₃.∙-cong
-- over normalize-idem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_; _++_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act; act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Axioms using (act-cong)
open import Substrate.Groups.Actions.S3-on-V4.Twist

------------------------------------------------------------------------
-- act-∙-canonical: per-block dispatch via the structural lemmas.
------------------------------------------------------------------------

act-∙-canonical : ∀ {n₁ h₁ n₂ h₂} →
                  Z₃.Canonical n₁ → Z₂.Canonical h₁ →
                  Z₃.Canonical n₂ → Z₂.Canonical h₂ →
                  ∀ v →
                  act ((n₁ , h₁) S₃.∙ (n₂ , h₂)) v ≡
                  act-on-canonical n₁ h₁ (act-on-canonical n₂ h₂ v)
-- Block 00: h₁ = [] forces no swap on n₂; h₂ = [] makes the H-component trivial.
act-∙-canonical {n₁} {.[]} {n₂} {.[]} c-n₁ Z₂.c-ε c-n₂ Z₂.c-ε v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , [])) v ≡ rot-pow n₁ (rot-pow n₂ v)
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.normalize n₂))) Z₂.c-ε v)
      (trans (cong (λ w → rot-pow w v) (Z₃.normalize-idem (n₁ ++ Z₃.normalize n₂)))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.normalize n₂) v))
      (trans (rot-pow-append n₁ (Z₃.normalize n₂) v)
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ v))))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ [] v) ≡ rot-pow n₁ (rot-pow n₂ v)
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-ε (act-on-canonical n₂ [] v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ Z₂.c-ε v))

-- Block 01: h₁ = [], h₂ = [a].
act-∙-canonical {n₁} {.[]} {n₂} {.(Z₂.a ∷ [])} c-n₁ Z₂.c-ε c-n₂ Z₂.c-a v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                 rot-pow n₁ (rot-pow n₂ (swap-αβ v))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.normalize n₂))) Z₂.c-a v)
      (trans (cong (λ w → rot-pow w (swap-αβ v)) (Z₃.normalize-idem (n₁ ++ Z₃.normalize n₂)))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.normalize n₂) (swap-αβ v)))
      (trans (rot-pow-append n₁ (Z₃.normalize n₂) (swap-αβ v))
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ (swap-αβ v)))))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ (Z₂.a ∷ []) v) ≡
                 rot-pow n₁ (rot-pow n₂ (swap-αβ v))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-ε (act-on-canonical n₂ (Z₂.a ∷ []) v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ Z₂.c-a v))

-- Block 10: h₁ = [a], h₂ = []. SP twist inverts n₂.
act-∙-canonical {n₁} {.(Z₂.a ∷ [])} {n₂} {.[]} c-n₁ Z₂.c-a c-n₂ Z₂.c-ε v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ v))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.inv (Z₃.normalize n₂)))) Z₂.c-a v)
      (trans (cong (λ w → rot-pow w (swap-αβ v)) (Z₃.normalize-idem (n₁ ++ Z₃.inv (Z₃.normalize n₂))))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.inv (Z₃.normalize n₂)) (swap-αβ v)))
      (trans (rot-pow-append n₁ (Z₃.inv (Z₃.normalize n₂)) (swap-αβ v))
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃.inv w) (swap-αβ v))) (Z₃.canonical-is-fixed-Z3 c-n₂))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ v)))))))
    RHS-to-pow : act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ [] v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ v))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-a (act-on-canonical n₂ [] v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ Z₂.c-ε v))

-- Block 11: h₁ = [a], h₂ = [a]. SP twist inverts n₂; swaps collapse via swap-αβ²-id.
act-∙-canonical {n₁} {.(Z₂.a ∷ [])} {n₂} {.(Z₂.a ∷ [])} c-n₁ Z₂.c-a c-n₂ Z₂.c-a v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.inv (Z₃.normalize n₂)))) Z₂.c-ε v)
      (trans (cong (λ w → rot-pow w v) (Z₃.normalize-idem (n₁ ++ Z₃.inv (Z₃.normalize n₂))))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.inv (Z₃.normalize n₂)) v))
      (trans (rot-pow-append n₁ (Z₃.inv (Z₃.normalize n₂)) v)
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃.inv w) v)) (Z₃.canonical-is-fixed-Z3 c-n₂))
      (trans (cong (λ x → rot-pow n₁ (rot-pow (Z₃.inv n₂) x)) (sym (swap-αβ²-id v)))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ (swap-αβ v)))))))))
    RHS-to-pow : act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ (Z₂.a ∷ []) v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-a (act-on-canonical n₂ (Z₂.a ∷ []) v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ Z₂.c-a v))

------------------------------------------------------------------------
-- act-∙: full action composition via act-cong + S₃.∙-cong over normalize-idem.
------------------------------------------------------------------------

act-∙ : ∀ s₁ s₂ v → act (s₁ S₃.∙ s₂) v ≡ act s₁ (act s₂ v)
act-∙ (n₁ , h₁) (n₂ , h₂) v =
  trans
    (act-cong {s₁ = (n₁ , h₁) S₃.∙ (n₂ , h₂)}
              {s₂ = (Z₃.normalize n₁ , Z₂.normalize h₁) S₃.∙ (Z₃.normalize n₂ , Z₂.normalize h₂)}
              {v₁ = v} {v₂ = v}
      (S₃.∙-cong {a₁ = n₁ , h₁} {a₂ = Z₃.normalize n₁ , Z₂.normalize h₁}
                  {b₁ = n₂ , h₂} {b₂ = Z₃.normalize n₂ , Z₂.normalize h₂}
                  (sym (Z₃.normalize-idem n₁) , sym (Z₂.normalize-idem h₁))
                  (sym (Z₃.normalize-idem n₂) , sym (Z₂.normalize-idem h₂)))
      refl)
    (act-∙-canonical (Z₃.normalize-canonical n₁) (Z₂.normalize-canonical h₁)
                     (Z₃.normalize-canonical n₂) (Z₂.normalize-canonical h₂) v)
